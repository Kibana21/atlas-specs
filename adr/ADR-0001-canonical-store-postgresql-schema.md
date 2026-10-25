# ADR-0001 — Canonical store: PostgreSQL schema and scale design

| Field | Value |
|---|---|
| Status | **Accepted** (owner, 25 Oct 2026: ATLAS-002 CP1 final approval of D1–D19). Drafting history: Revision 2 (25 Oct 2026) after the owner's CP1 review: D16 and D18 approved; D17 amended (a dedicated least-privilege ingestion role instead of widening the runtime role); schema adjusted for the revised ADR-0003, ADR-0008 and ADR-0017. Revision 3 (25 Oct 2026): provider-neutral columns and reference tables (ADR-0019); the exact DEC-044 amendment is in `features/ATLAS-002-canonical-graph-foundation/proposals/dec-044-amendment.md`. Revision 1 was 24 Oct 2026 |
| Register | DEC-021 (**Confirmed** 25 Oct 2026); bounded traversal per DEC-022 (still Proposed, benchmark pending); DEC-044 amended to six roles (**Confirmed** 25 Oct 2026, design only; nothing created) |
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
| `change_set` | `(org_id, revision)`, `kind`, `channel`, `actor_kind`, `actor_namespace`, `actor_key`, `actor_label`, `source_ref`, `input_hash`, `reverts_revision`, `reason`, `change_reference`, `created_at`, `db_role` | PK `(org_id, revision)`; index `(org_id, input_hash)` for idempotent loads; index `(org_id, actor_namespace, actor_key)`; FK `(org_id, reverts_revision)`; FK `actor_namespace` → `actor_namespace` (reference data, one kind each) with a kind `CHECK`; `BEFORE INSERT` trigger sets `created_at = now()` and `db_role = session_user` (ADR-0008 §10) |
| `entity_type`, `relationship_type`, `relationship_rule`, `attribute_rule` | `type_key` / `rel_type`, `category`, `taxonomy_version` | Seeded from the pinned taxonomy (ADR-0017); FK targets. Rules reference categories (ADR-0019) |
| `provider`, `category`, `identity_namespace`, `native_type_mapping`, `actor_namespace` | provider key; category key; namespace (provider, normalizer and version, case rule, scope); `(provider, native_type) → category` | Reference data seeded from the pinned taxonomy; adding a provider adds rows here only |
| `entity` (identity) | `id`, `org_id`, `created_revision` | PK `id`; `UNIQUE (org_id, id)`. Insert-only: type, merge and removal are on versions |
| `entity_version` | `(org_id, entity_id, revision_from)`, `revision_to`, `type_key`, `category`, `provider`, `native_type`, `record_state`, `merged_into`, `display_name`, `lifecycle`, `environment_scope`, `environment_id`, `container_id`, `attributes jsonb`, `trust_state`, `verification_state`, `verified_by/at`, `expires_at`, `taxonomy_version` | PK `(org_id, entity_id, revision_from)`; FKs `(org_id, entity_id)`, `(org_id, merged_into)`, `(org_id, environment_id)`, `(org_id, container_id) → entity`; FK `type_key → entity_type`; `CHECK (revision_to IS NULL OR revision_to > revision_from)`; `CHECK ((record_state = 'merged') = (merged_into IS NOT NULL))`; `CHECK` environment scope vs `environment_id`; **partial unique** `(org_id, entity_id) WHERE revision_to IS NULL` (one current version); `CHECK` physical types have `provider` and `native_type`; partial indexes on current rows: `(org_id, type_key)`, `(org_id, provider, category)`, `(org_id, container_id)`, `(org_id, environment_id)`, `(org_id, lower(display_name))` |
| `relationship` (identity) | `id`, `org_id`, `rel_type`, `from_id`, `to_id`, `discriminator`, `created_revision` | PK `id`; `UNIQUE (org_id, id)`; **`UNIQUE (org_id, rel_type, from_id, to_id, discriminator)`** (one record per fact, ADR-0017 §4; a retired relationship that returns gets a new version, not a new identity); FKs `(org_id, from_id)`, `(org_id, to_id) → entity`; `CHECK (from_id <> to_id)`; indexes `(org_id, from_id, rel_type)`, `(org_id, to_id, rel_type)` |
| `relationship_version` | `(org_id, relationship_id, revision_from)`, `revision_to`, `record_state`, `lifecycle`, `environment_id`, `cross_environment`, `shared_endpoint`, `cross_provider`, `attributes jsonb`, `trust_state`, `verification…`, `taxonomy_version` | Partial unique current version; partial index `(org_id, relationship_id) WHERE revision_to IS NULL` |
| `external_identity` | `id`, `org_id`, `entity_id`, `namespace` (FK → `identity_namespace`), `original_key`, `normalized_key`, `normalization_version`, `key_parts jsonb`, `match_method`, `revision_from`, `revision_to` | **Partial unique** `(org_id, namespace, normalized_key) WHERE revision_to IS NULL`; index `(org_id, entity_id)` |
| `entity_alias` | `id`, `org_id`, `entity_id`, `alias_original`, `alias_normalized`, `scope_type`, `scope_environment_id`, `status`, `approved_by`, `revision_from`, `revision_to` | **Partial unique** `(org_id, scope_type, scope_environment_id, alias_normalized) NULLS NOT DISTINCT WHERE status = 'approved' AND revision_to IS NULL` (PostgreSQL 15 feature: an environment-neutral alias is unique too). A status change is a new row |
| `evidence` (append-only) | `id`, `org_id`, `kind`, `source_ref`, `artifact_ref`, `artifact_hash`, `method`, `confidence`, `observed_at`, `valid_from`, `valid_to`, `change_revision` | Index `(org_id, change_revision)` |
| `fact_assertion` | `id`, `org_id`, `fact_kind`, `fact_id`, `field_path`, `asserted_value jsonb`, `evidence_id`, `evidence_kind`, `revision_from`, `revision_to` | Index `(org_id, fact_id, field_path) WHERE revision_to IS NULL`; check that `evidence_kind` is allowed for the relationship type (ADR-0017 §4) |
| `match_candidate`, `reconciliation_case` | shells for ADR-0003 (Phase 2 workflow) | Org-scoped FKs |
| `graph_snapshot` | `id`, `org_id`, `revision`, `label`, `status`, `graph_hash` | `UNIQUE (org_id, label)`; FK `(org_id, revision) → change_set` |

**Set-once trigger:** every table with `revision_to` has a `BEFORE UPDATE` trigger (plain PL/pgSQL) that rejects the update unless `OLD.revision_to IS NULL`, `NEW.revision_to IS NOT NULL` and no other column changed (ADR-0008 §2).

**Containment:**

- `CONTAINS` is a relationship like any other (with evidence).
- The current primary parent is **also** denormalized as `entity_version.container_id`, maintained in the same change set (one parent rule, ADR-0017). Children listing is then an index lookup.
- Ancestor and subtree queries use a bounded recursive CTE over `container_id` (depth ≤ 8).
- A consistency test asserts that `container_id` equals the current `CONTAINS` relationship.

**Environments:** `environment_id` references a `core.environment` entity. Cross-environment relationships set `cross_environment` (ADR-0017).

**Provider neutrality:** no table, column or constraint names a provider. Provider-specific detail is reference data (`provider`, `identity_namespace`, `native_type_mapping`), `native_type`, and `attributes`/`provider_attributes` JSON validated per type or profile. A new provider adds reference rows and a normalizer; it never changes these tables (ADR-0019).

**Facts vs presentation:** these tables hold architecture facts only. No positions, colours, icons, provider logos, collapsed state or diagram grouping. Those belong to the separate, later view and layout tables (DEC-005, MOD-05, invariant 1); icons are derived from category in the frontend.

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
| Bulk ingestion | Validate in the application against the taxonomy, then `COPY … FROM STDIN` (psycopg) **directly into target tables** inside one change-set transaction; no temp tables (neither the runtime nor the ingestion role has `TEMP`), using the ingestion role; batches of 5–10k rows | 10k/40k fixture: seconds. Scale A: minutes, measured in CP4 |
| Query performance | All read paths are repository functions with bounded depth, limits and explicit columns; `EXPLAIN` checks in tests for the core queries | Projection performance is ATLAS-003+ (BL-108); CP4 benchmarks core lookups |
| Migration performance | Additive migrations; indexes created with the tables (empty). Later large-table indexes use `CREATE INDEX CONCURRENTLY` in non-transactional Alembic steps | — |
| Graph analytics / deep traversal | Out of scope; bounded recursive CTEs (DEC-022). A graph engine only as a rebuildable projection after a failed benchmark (tech §4.3) | — |
| Partitioning | **Not** in v1. Candidates later: `*_version`, `evidence`, `fact_assertion` by organization or revision range, after measurement at Scale A | — |

**Storage estimate (pilot):**

- about 50k identity rows, about 100k version rows after a few revisions, and 0.5–1 M assertion rows;
- roughly 0.5–1.5 GB including indexes.

That's acceptable for local `atlas_db`/`atlas_test`. Scale A fixtures run only in CI or disposable environments, never on the shared server, unless the owner approves.

## Privileges: a dedicated ingestion role (D17, revised)

**Owner review (25 Oct 2026):** do not broaden `atlas_app` into a general-purpose writer; propose a dedicated least-privilege ingestion role or an equivalent isolated write boundary; explain the exact role, grant, migration, local setup and CI changes; **do not create roles or change privileges yet**.

Nothing in this section has been executed. No role exists, no grant was made, and no credential was created.

### Role options

| Option | How | Verdict |
|---|---|---|
| **A. Separate login role per environment: `atlas_ingest` and `atlas_test_ingest`** | Its own credential. Used only by the ingestion entry points (the CP4 fixture loader CLI; later the import and sync workers). The API process never receives its URL. Per-table grants from the migration that creates each table | **Recommended**: the API stays read-only at the database level; a bug or injection in the API can't write canonical facts; easy to test and to audit (`pg_stat_activity.usename`) |
| B. `SECURITY DEFINER` functions owned by a `NOLOGIN` writer role; `atlas_app` gets `EXECUTE` only | One isolated write boundary in PL/pgSQL | Rejected for now: puts validation and diff logic in the database, can't use `COPY` (D18), and is harder to test and review than Python |
| C. A `NOLOGIN` group role `atlas_writer` granted to `atlas_app` (`SET ROLE`) | One login | Rejected: `atlas_app` can switch to the writer at will, so it is effectively a writer |
| D. Revision 1: `atlas_app` gets INSERT and column UPDATE | No new role | Rejected by the owner |

**Later API writes** (steward edits, BL-119; ATLAS-003+) are not decided here. The options then are an API that submits commands executed by the ingestion boundary, or a separately reviewed grant. Either needs its own approval.

### Role attributes (proposal)

| Attribute | `atlas_ingest` / `atlas_test_ingest` |
|---|---|
| Login | Yes; `CONNECTION LIMIT 2` |
| Superuser, CREATEDB, CREATEROLE, REPLICATION, BYPASSRLS | No (defaults) |
| Membership in other roles | None |
| Database | `CONNECT` on its own environment's database only (`atlas_db` or `atlas_test`). `PUBLIC` already has no `CONNECT` or `TEMP` there (ATLAS-001), so it can't create temporary tables |
| Schema `atlas` | `USAGE` only (no `CREATE`) |
| Session limits | `statement_timeout = '120s'` (bulk loads), `idle_in_transaction_session_timeout = '60s'`, `lock_timeout = '10s'` |
| `search_path` | `atlas` |
| Default privileges | **None.** Everything is granted per table by migrations |

### Privilege matrix (canonical tables, per environment)

`atlas_migrator` owns the schema and every table (DDL, ATLAS-001), and is not listed per row. "S" = `SELECT`, "I" = `INSERT`, "U(c)" = `UPDATE` of column c only.

| Table | `atlas_app` (API runtime) | `atlas_ingest` (new) |
|---|---|---|
| `alembic_version` | S (ATLAS-001) | — |
| `organization`, `provider`, `category`, `identity_namespace`, `native_type_mapping`, `actor_namespace`, `entity_type`, `relationship_type`, `relationship_rule`, `attribute_rule` (seeded by migrations only) | S | S |
| `org_revision` | S | S, U(`last`) |
| `change_set`, `graph_snapshot`, `evidence` | S | S, I |
| `entity`, `relationship` (identity rows) | S | S, I |
| `entity_version`, `relationship_version`, `external_identity`, `entity_alias`, `fact_assertion` | S | S, I, U(`revision_to`) |
| `match_candidate`, `reconciliation_case` (shells) | S | S, I |
| Any table | no I/U/D, no `TRUNCATE`, `REFERENCES` or `TRIGGER` | no D, no `TRUNCATE`, `REFERENCES` or `TRIGGER` |

- `atlas_app` keeps exactly its ATLAS-001 rights: `SELECT` through the schema's default privileges. Graph-reading APIs still need authorization first (invariant 4).
- No sequences are needed: IDs come from the application (UUIDv7) and revisions from `org_revision`.
- `COPY … FROM STDIN` needs only `INSERT` (D18).
- The set-once trigger (above) also binds the owner, so a migration can't rewrite history by accident.

### Exact changes, by place (all after approval; none made now)

| Where | Change |
|---|---|
| **atlas-specs** | A new proposal script `features/ATLAS-002-canonical-graph-foundation/proposals/postgres-ingest-roles.sql` (CP3), reviewed like the ATLAS-001 one. Guards: server major 15; the four ATLAS-001 roles exist and are unchanged; neither ingest role exists; both databases exist and are owned by their migrators. It creates only the two roles and their `CONNECT`, `USAGE`, settings and `search_path`; it touches no other role, database, extension, server setting or `pg_hba.conf`. It has a rollback section (`REVOKE`, `DROP ROLE`). The DEC-044 row is amended (four → six roles) |
| **Shared local server** | Only the server owner runs that script, as the local superuser, with two new passwords in environment variables (`ATLAS_INGEST_PASSWORD`, `ATLAS_TEST_INGEST_PASSWORD`). Claude does not create the credentials, and they are never committed or printed. Claude then verifies with read-only catalog queries (`atlas doctor`) |
| **Local `.env`** (git-ignored) | The owner adds `ATLAS_INGEST_DATABASE_URL` (and the test equivalent). The API configuration does not read it |
| **atlas-backend settings** | New `ATLAS_INGEST_DATABASE_URL` and `ATLAS_DB_INGEST_ROLE`, read only by the ingestion entry points. `create_app()` never builds an engine for it; a test asserts that the API connects as the runtime role |
| **atlas-backend migration `0002`** | Creates the tables, the trigger and the grants in the matrix, naming `ATLAS_DB_INGEST_ROLE` (passed to Alembic like `ATLAS_DB_APP_ROLE` today). It **fails** if the role doesn't exist, rather than skipping the grants. The downgrade revokes the grants and drops the tables (empty databases only) |
| **atlas-backend CI** | After `bootstrap.sql`, also runs `scripts/db/bootstrap-ingest.sql`: a verbatim copy of the specs proposal at the pinned commit, which `check_bootstrap.py` verifies the same way. Two more random passwords are generated and masked per job. Integration tests get the ingest URL and role |
| **atlas-backend `images_check.sh`** | Same extra bootstrap step for the image check |
| **atlas-backend `doctor`** | Reports whether the ingest role exists and can connect (read-only), and fails if it has any privilege beyond the matrix |
| **atlas-frontend CI (e2e job)** | Once `e2e/backend.ref` moves to a backend commit with migration `0002`, the e2e job must also run the ingest bootstrap, or `alembic upgrade head` fails. Nothing changes in the frontend before then |
| **Privilege tests** (extend the ATLAS-001 suite) | `atlas_app` can't insert, update or delete any canonical table. `atlas_ingest` can insert; can update only `revision_to`, and only once (trigger); can't delete or truncate; can't run DDL, create temporary tables, or connect to the other environment's database; can't write reference tables. Neither role is superuser or can create roles or databases, replicate or bypass RLS |
| **Workspace rules** | The local workspace note "Atlas uses its four roles" becomes six once applied |

## PostgreSQL 15 remains sufficient (revision 3)

| Need | PostgreSQL 15 feature used | Extension needed? |
|---|---|---|
| Organization-scoped uniqueness, composite FKs | B-tree unique indexes, composite foreign keys | No |
| Current-version lookups | Partial indexes (`WHERE revision_to IS NULL`) | No |
| Environment-neutral alias uniqueness | `NULLS NOT DISTINCT` (new in 15) | No |
| Provider- and type-specific attributes | `jsonb` with application-side validation | No |
| Containment and bounded traversal | Recursive CTEs with depth limits | No |
| Immutability | PL/pgSQL triggers, column privileges | No (`plpgsql` is built in) |
| Bulk load | `COPY … FROM STDIN` | No |
| Multi-provider support | Reference rows plus columns above | No |

No feature from PostgreSQL 16 or later and no extension is required. Fuzzy search (`pg_trgm`) remains a later, separate decision (BL-111).

**No additional infrastructure:** no graph database, search engine, message broker, object store, cache, new Redis usage or new service. The only server-level change ATLAS-002 proposes is the two ingestion roles, which the owner runs (DEC-044 amendment).

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

## Approved by the owner (25 Oct 2026)

1. Option A: typed relational graph, identity/version tables, JSONB attributes, PostgreSQL 15 only, **no extensions** and no graph database.
2. The table set, keys and indexes above as the CP3 baseline (refinable without re-approval if keys, uniqueness and privilege rules stay intact).
3. D17: a dedicated ingestion role per environment (§Privileges), the runtime role staying read-only; the privilege matrix; the role SQL as a proposal for the server owner to run after approval.
4. Bulk loading by validated `COPY` into target tables within one change set.
5. Scale A data never on the shared server without approval.
