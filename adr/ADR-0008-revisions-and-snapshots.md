# ADR-0008 — Revisions, history and snapshots

| Field | Value |
|---|---|
| Status | **Proposed** (CP1 of ATLAS-002, 24 Oct 2026) |
| Register | DEC-031 (Proposed); compatible with, but does not decide, DEC-057 (Open) |
| Owner (proposed) | Data architect; approval: Atlas owner |
| Related | INV-06, HIST-01, HIST-02, MOD-05, GOV-04; tech §3.5 ("MVCC/revision manifests"), §10; ADR-0001, ADR-0016, ADR-0018 |

## Problem

The canonical graph needs:

- **auditability:** who changed what, when, from which input;
- **historical reconstruction:** the graph as of any past revision;
- **deterministic fixture loading:** the same input gives the same IDs, rows and hash, and a re-load changes nothing;
- **consistent graph snapshots:** a reader never sees half of a change;
- **future incremental imports:** only differences are written, idempotently.

**Owner direction:** avoid unnecessary event-sourcing infrastructure, and explain the trade-offs between append-only revisions, temporal tables and snapshots.

## Options

| Option | How it works | For | Against |
|---|---|---|---|
| **A. Append-only versioned rows on a per-organization revision counter** (recommended) | Every write belongs to a **change set** with a monotonically increasing `revision` per organization. Each entity and relationship has immutable identity rows plus **version rows** valid for `[revision_from, revision_to)`. "Current" means `revision_to IS NULL`. A **snapshot** is a named, immutable pointer to a revision | Plain SQL on PostgreSQL 15, no extension. Point-in-time and diff queries are range predicates. Snapshots cost O(1). Small edits write few rows. Consistent: a revision becomes visible atomically with its transaction | History grows (mitigated: only changed rows). Queries need a revision predicate (wrapped in views and repository functions). One serialization point per organization for allocating revisions |
| B. System-versioned temporal tables (time ranges) | Each row has a `tstzrange` of validity, maintained by triggers or an extension | Familiar SQL:2011 idea | PostgreSQL has **no native** system versioning: it needs triggers or the third-party `temporal_tables` extension (not available to Atlas without a server change, and not on every managed PostgreSQL). Time is a poor snapshot key: clock skew, and all rows of one transaction share `now()`, so ordering is ambiguous. Exclusion constraints would need the `btree_gist` extension |
| C. Snapshot copies (full materialization per published version) | Each publication copies the whole graph (or a manifest listing every member version) | Trivial reads of a snapshot | O(N) storage and time per snapshot: at 100k entities and 500k relationships every small publish copies everything (rejected by tech §3.5 for cost). It also doesn't give history between snapshots |
| D. Event sourcing | An append-only event log is the source of truth; tables are projections rebuilt from events | Complete audit, replay | Event schema versioning, projection rebuilds and eventual consistency are a whole infrastructure (owner: avoid). Deterministic replay of years of events is costly |

## Recommendation

**Option A**, with named snapshots as pointers:

1. **Change set:** `change_set (org_id, revision, kind, actor, source_ref, input_hash, created_at, description)`, PK `(org_id, revision)`.
   - `kind` ∈ {`fixture_load`, `import`, `steward_edit`, `merge`, `split`, `discovery_sync` (Phase 2), `migration`}.
   - Exactly one change set per transaction; it is the unit of audit (GOV-04) and of consistency.
2. **Revision allocation:**
   - `UPDATE org_revision SET last = last + 1 WHERE org_id = $1 RETURNING last` inside the writing transaction;
   - this serializes writers **per organization**, which is acceptable at curation and import rates;
   - bulk loads use one change set, not one per row;
   - revisions are gap-free per organization (a rolled-back transaction releases its row lock and the number is re-used).
3. **Identity and version rows:**
   - `entity (org_id, id, type_key, created_revision, merged_into)`: identity only, never updated except `merged_into`;
   - `entity_version (org_id, entity_id, revision_from, revision_to, display_name, lifecycle, environment_id, attributes jsonb, trust_state, verification…, taxonomy_version)`;
   - same for `relationship` / `relationship_version`. Endpoints are immutable: changing an endpoint means a new relationship plus retiring the old one.
   - A change **closes** the current version (`revision_to = R`) and inserts the new one (`revision_from = R`). Unchanged rows are untouched.
4. **Reads:**
   - **current:** `revision_to IS NULL` (partial indexes);
   - **as of revision R:** `revision_from <= R AND (revision_to IS NULL OR revision_to > R)`;
   - **diff (R1, R2]:** versions with `revision_from` or `revision_to` in that interval (HIST-02).
5. **Snapshot:** `graph_snapshot (org_id, id, revision, label, status, graph_hash, created_by, created_at)`, immutable (HIST-01).
   - `graph_hash` is a deterministic hash over the current versions at that revision, which lets a fixture load be verified.
   - Snapshots never copy data.
6. **Deletion:**
   - nothing is physically deleted;
   - removal is a version with `lifecycle = removed` (tombstone) and provenance (INV-06, ADR-0018);
   - the runtime role gets INSERT and UPDATE (only to close `revision_to`) on version tables, **no DELETE** (ADR-0001).
7. **Deterministic fixture load:**
   - fixtures carry explicit IDs (ADR-0015) and canonical ordering;
   - the loader computes `input_hash`;
   - if the current graph already equals the fixture (hash match), no change set is written (idempotent);
   - otherwise one `fixture_load` change set writes exactly the differences.
8. **Incremental import (future):** the same diff-and-apply path, keyed by `(source, scope, input_hash)` for idempotency (CON-06).
9. **Optimistic concurrency (future APIs):** an entity version's `revision_from` is its ETag; `If-Match` compares it (412 on mismatch).
10. **Branches and drafts** (tech §10, BL-116) are **not** in ATLAS-002. They fit as typed patches against a pinned `revision`, without changing these tables.

**Discovery publication (DEC-057, still Open):** whether non-conflicting discovered facts auto-apply as system revisions, or wait for approval, is a policy over `change_set.kind` and snapshot status. This ADR does not decide it.

## Trade-offs and risks

| Risk | Mitigation |
|---|---|
| History tables grow with churn | Only changed rows are versioned. Measure at the pilot size in CP4. Partition `*_version` by organization or revision range only when measured (Scale A+) |
| Forgetting the revision predicate | Repository functions and views (`entity_current`) are the only read path. Tests cover as-of reads |
| Per-organization revision lock limits write concurrency | Writers batch into one change set. Measure with the CP4 benchmark. If needed later, allocate revision ranges |
| Closing versions needs UPDATE on version tables | UPDATE limited to `revision_to` through the repository (column privileges `GRANT UPDATE (revision_to)`), no DELETE |

## Impact on the database schema

Tables `org_revision`, `change_set`, `entity`/`entity_version`, `relationship`/`relationship_version` and `graph_snapshot`. Evidence is append-only and tied to change sets (ADR-0018). See ADR-0001.

## Impact on APIs and authorization (future)

- Read APIs take `snapshot_id` or `revision`; a missing value means "current".
- Writes return the new revision.
- History access is authorized like current access: a hidden entity's history is hidden too.

## Migration and compatibility

- Additive tables.
- Branches, discovery syncs and the audit store (BL-118) attach to `change_set` later without reshaping version tables.

## Requires owner approval

1. Option A (append-only versions with per-organization revisions and change sets), not temporal tables, snapshot copies or event sourcing.
2. Snapshots as immutable pointers with a deterministic graph hash.
3. No physical deletion; tombstones; runtime role INSERT plus `UPDATE (revision_to)` only on version tables.
4. Deterministic, idempotent fixture loading by input hash.
