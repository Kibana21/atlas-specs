# ADR-0001 — Canonical store: PostgreSQL schema and scale design

| Field | Value |
|---|---|
| Status | **Proposed** (CP1 of ATLAS-002, 24 Oct 2026) |
| Register | DEC-021 (Proposed); bounded traversal per DEC-022 (Proposed, benchmark pending) |
| Owner (proposed) | Architecture + DBA; approval: Atlas owner |
| Related | INV-01…07, MOD-01, MOD-03, MOD-04, HIST-01/02; tech §3.5, §4; ADR-0003, ADR-0008, ADR-0015…0018 |

## Problem

The canonical graph needs a storage design that:

- serves **thousands of entities and tens of thousands of relationships** now (pilot: 10k / 40k), and stays sound at Scale A (100k / 500k);
- is organization-scoped (ADR-0016), revision-aware (ADR-0008) and evidence-backed (ADR-0018);
- runs on the approved **PostgreSQL 15**, with no graph database and **no PostgreSQL extensions**. Extensions such as `pg_trgm`, `ltree` and `btree_gist` would need a superuser change on the owner's shared server, which is excluded.

## Options

| Option | Verdict |
|---|---|
| **A. Typed relational graph: identity tables + revision-ranged version tables + JSONB for type-specific attributes, plain B-tree indexes** | **Recommended** (tech ADR-001, DEC-021) |
| B. Single generic `node`/`edge` tables with all attributes in JSONB | Simpler DDL, but no FK-level type integrity, weak indexing of required attributes, harder validation |
| C. Graph database (Neo4j etc.) as primary | Excluded by the owner without a separate decision; tech §4.3 allows it only as a rebuildable read projection after a failed benchmark (DEC-022) |
| D. Materialized-path (`ltree`) containment | Fast subtree queries, but needs the `ltree` extension (shared-server change). A bounded recursive CTE plus a denormalized parent column covers v1 depths (≤ 8) |

## Recommended schema (all in schema `atlas`; columns abbreviated)

Conventions:

- `org_id uuid NOT NULL` leads every key and index;
- all IDs UUIDv7 (ADR-0015);
- composite FKs `(org_id, …)`;
- `CHECK` constraints for enumerations;
- no `ON DELETE CASCADE` (nothing is deleted).

| Table | Key columns | Constraints and indexes |
|---|---|---|
| `organization` | `id`, `key` | `UNIQUE (key)` |
| `org_revision` | `org_id`, `last bigint` | PK `org_id`; row-locked to allocate revisions |
| `change_set` | `(org_id, revision)`, `kind`, `actor`, `source_ref`, `input_hash`, `created_at` | PK `(org_id, revision)`; index `(org_id, input_hash)` for idempotent loads |
| `entity_type`, `relationship_type`, `relationship_rule`, `attribute_rule` | `type_key` / `rel_type`, `taxonomy_version` | Seeded from the pinned taxonomy (ADR-0017); FK targets |
| `entity` (identity) | `id`, `org_id`, `type_key`, `created_revision`, `merged_into` | PK `id`; `UNIQUE (org_id, id)`; FK `(org_id, merged_into) → entity`; FK `type_key → entity_type` |
| `entity_version` | `(org_id, entity_id, revision_from)`, `revision_to`, `display_name`, `lifecycle`, `environment_id`, `container_id`, `attributes jsonb`, `trust_state`, `verification_state`, `verified_by/at`, `expires_at`, `taxonomy_version` | PK `(org_id, entity_id, revision_from)`; FK `(org_id, entity_id) → entity`; `CHECK (revision_to IS NULL OR revision_to > revision_from)`; **partial unique** `(org_id, entity_id) WHERE revision_to IS NULL` (one current version); partial indexes on current rows: `(org_id, type_key*)`, `(org_id, container_id)`, `(org_id, environment_id)`, `(org_id, lower(display_name))` |
| `relationship` (identity) | `id`, `org_id`, `rel_type`, `from_id`, `to_id`, `created_revision` | PK `id`; `UNIQUE (org_id, id)`; FKs `(org_id, from_id)`, `(org_id, to_id) → entity`; `CHECK (from_id <> to_id)`; indexes `(org_id, from_id, rel_type)`, `(org_id, to_id, rel_type)` |
| `relationship_version` | `(org_id, relationship_id, revision_from)`, `revision_to`, `lifecycle`, `environment_id`, `cross_environment`, `attributes jsonb`, `trust_state`, `verification…`, `taxonomy_version` | Partial unique current version; partial index `(org_id, relationship_id) WHERE revision_to IS NULL` |
| `external_identity` | `id`, `org_id`, `entity_id`, `namespace`, `normalized_key`, `match_method`, `status`, `created_revision`, `superseded_revision` | **Partial unique** `(org_id, namespace, normalized_key) WHERE status = 'active'`; index `(org_id, entity_id)` |
| `entity_alias` | `id`, `org_id`, `entity_id`, `alias_normalized`, `scope_type`, `scope_environment_id`, `status`, `approved_by` | **Partial unique** `(org_id, scope_type, scope_environment_id, alias_normalized) NULLS NOT DISTINCT WHERE status = 'approved'` (PostgreSQL 15 feature: an environment-neutral alias is unique too) |
| `evidence` (append-only) | `id`, `org_id`, `kind`, `source_ref`, `artifact_ref`, `artifact_hash`, `method`, `confidence`, `observed_at`, `valid_from`, `valid_to`, `change_revision` | Index `(org_id, change_revision)` |
| `fact_assertion` (append-only) | `id`, `org_id`, `fact_kind`, `fact_id`, `field_path`, `asserted_value jsonb`, `evidence_id`, `status`, `change_revision` | Index `(org_id, fact_id, field_path)` |
| `match_candidate`, `reconciliation_case` | shells for ADR-0003 (Phase 2 workflow) | Org-scoped FKs |
| `graph_snapshot` | `id`, `org_id`, `revision`, `label`, `status`, `graph_hash` | `UNIQUE (org_id, label)`; FK `(org_id, revision) → change_set` |

\* `type_key` is copied from `entity` into the current-version index (or the query joins `entity`); the CP3 benchmark decides which.

**Containment:**

- `CONTAINS` is a relationship like any other (with evidence).
- The current primary parent is **also** denormalized as `entity_version.container_id`, maintained in the same change set (one parent rule, ADR-0017). Children listing is then an index lookup.
- Ancestor and subtree queries use a bounded recursive CTE over `container_id` (depth ≤ 8).
- A consistency test asserts that `container_id` equals the current `CONTAINS` relationship.

**Environments:** `environment_id` references a `core.environment` entity. Cross-environment relationships set `cross_environment` (ADR-0017).

## Scale assessment (per owner §8)

| Concern | Design answer | Expected at pilot (10k / 40k) and Scale A (100k / 500k) |
|---|---|---|
| Organization-scoped uniqueness | Partial unique indexes leading with `org_id` | Index-only checks; no global locks |
| Source/target lookup | `(org_id, from_id, rel_type)` and `(org_id, to_id, rel_type)` on identity rows, joined to current versions by partial index | Neighbors of one entity: 2 index scans plus a PK join; expected to stay in single-digit milliseconds at Scale A (an estimate, to be measured in CP4) |
| Hierarchical containment | `container_id` + partial index; bounded recursive CTE | Children: one index range; ancestors: ≤ 8 PK lookups |
| Identity lookup | Unique `(org_id, namespace, normalized_key)` | O(log n) |
| Alias resolution | Partial unique index on approved aliases | O(log n); unapproved aliases never resolve |
| Revision-aware access | Current reads use `revision_to IS NULL` partial indexes; history uses PK `(org_id, id, revision_from)` | Current reads are unaffected by history size |
| Referential integrity | Composite FKs everywhere; immutable relationship endpoints, so FKs never change | FK checks during bulk load are index lookups; one transaction |
| Bulk ingestion | Validate in the application against the taxonomy, then `COPY … FROM STDIN` (psycopg) **directly into target tables** inside one change-set transaction; no temp tables (the runtime role has no `TEMP`, ATLAS-001); batches of 5–10k rows | 10k/40k fixture: seconds. Scale A: minutes, measured in CP4 |
| Query performance | All read paths are repository functions with bounded depth, limits and explicit columns; `EXPLAIN` checks in tests for the core queries | Projection performance is ATLAS-003+ (BL-108); CP4 benchmarks core lookups |
| Migration performance | Additive migrations; indexes created with the tables (empty). Later large-table indexes use `CREATE INDEX CONCURRENTLY` in non-transactional Alembic steps | — |
| Graph analytics / deep traversal | Out of scope; bounded recursive CTEs (DEC-022). A graph engine only as a rebuildable projection after a failed benchmark (tech §4.3) | — |
| Partitioning | **Not** in v1. Candidates later: `*_version`, `evidence`, `fact_assertion` by organization or revision range, after measurement at Scale A | — |

**Storage estimate (pilot):**

- about 50k identity rows, about 100k version rows after a few revisions, and 0.5–1 M assertion rows;
- roughly 0.5–1.5 GB including indexes.

That's acceptable for local `atlas_db`/`atlas_test`. Scale A fixtures run only in CI or disposable environments, never on the shared server, unless the owner approves.

## Privileges (extends the ATLAS-001 FR-28 rule)

- The runtime role gets **explicit per-table grants** in the migration that creates each table:
  - `INSERT` on identity, version, evidence, assertion, change-set and snapshot tables;
  - `UPDATE (revision_to)` on version tables and `UPDATE (merged_into)` on `entity`;
  - `UPDATE (last)` on `org_revision`;
  - **no `DELETE`, no `TRUNCATE`**, and `SELECT` as today.
- Evidence and assertions are insert-only.
- The migration role keeps DDL.
- Tests extend the ATLAS-001 privilege suite: for example, an UPDATE of `display_name` in place is denied; only `revision_to` may change.

## Trade-offs and risks

- **The two-table identity/version pattern** costs a join on reads. Compensated by partial indexes; measured in CP4.
- **JSONB for type-specific attributes:** required attributes are validated in the service layer (ADR-0017). Hot attributes can become columns in MINOR migrations if queries need them.
- **No extensions:** fuzzy search (`pg_trgm`) is unavailable in ATLAS-002. Search (BL-111) will need an owner decision on enabling `pg_trgm` in `atlas_db`, or another approach.

## Impact on APIs and authorization (future)

- Read APIs map one-to-one onto repository functions taking `OrgScope` and an optional revision.
- Authorization filters run **before** traversal (invariant 4), using type, environment and classification attributes.
- Classification (DEC-073, Open) arrives as an additive column in ATLAS-003.

## Migration and compatibility

- One Alembic migration per checkpoint (CP3), reversible on empty tables, with expand-migrate-contract for later changes.
- Taxonomy seeds are versioned (ADR-0017).

## Requires owner approval

1. Option A: typed relational graph, identity/version tables, JSONB attributes, PostgreSQL 15 only, **no extensions** and no graph database.
2. The table set, keys and indexes above as the CP3 baseline (refinable without re-approval if keys, uniqueness and privilege rules stay intact).
3. Runtime-role write privileges: INSERT plus column-limited UPDATE, no DELETE (extends FR-28).
4. Bulk loading by validated `COPY` into target tables within one change set.
5. Scale A data never on the shared server without approval.
