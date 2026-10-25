# ADR-0008 — Revisions, history and snapshots

| Field | Value |
|---|---|
| Status | **Accepted** (owner, 25 Oct 2026: ATLAS-002 CP1 final approval of D1–D19). Drafting history: Revision 3 (25 Oct 2026): change attribution (§10). Revision 2 (25 Oct 2026) after the owner's CP1 review (D15 amended: define atomic publication, immutable fact versions, snapshot consistency, historical reconstruction, relationship endpoint validity and rollback, proportionate to the MVP); revision 1 was 24 Oct 2026 |
| Register | DEC-031 (**Confirmed** 25 Oct 2026); compatible with, but does not decide, DEC-057 (Open) |
| Owner (proposed) | Data architect; approval: Atlas owner |
| Related | INV-06, HIST-01, HIST-02, MOD-05, GOV-04; tech §3.5 ("MVCC/revision manifests"), §10; ADR-0001, ADR-0016, ADR-0017, ADR-0018 |

## Problem

The canonical graph needs:

- **auditability:** who changed what, when, from which input;
- **historical reconstruction:** the graph as of any past revision;
- **deterministic fixture loading:** the same input gives the same IDs, rows and hash, and a re-load changes nothing;
- **consistent graph snapshots:** a reader never sees half of a change;
- **future incremental imports:** only differences are written, idempotently.

**Owner direction:** avoid unnecessary event-sourcing infrastructure, explain the trade-offs between append-only revisions, temporal tables and snapshots, and keep the implementation proportionate to the MVP.

## Options

| Option | How it works | For | Against |
|---|---|---|---|
| **A. Append-only versioned rows on a per-organization revision counter** (recommended) | Every write belongs to a **change set** with a monotonically increasing `revision` per organization. Facts have immutable identity rows plus **version rows** valid for `[revision_from, revision_to)`. A **snapshot** is a named, immutable pointer to a revision | Plain SQL on PostgreSQL 15, no extension. Point-in-time and diff queries are range predicates. Snapshots cost O(1). Small edits write few rows | History grows (only changed rows). Queries need a revision predicate (wrapped in repository functions). One serialization point per organization |
| B. System-versioned temporal tables (time ranges) | Each row has a `tstzrange` of validity, maintained by triggers or an extension | Familiar SQL:2011 idea | PostgreSQL has **no native** system versioning: it needs triggers or the `temporal_tables` extension (excluded). Time is a poor snapshot key: clock skew, and all rows of one transaction share `now()`. Exclusion constraints need `btree_gist` (extension) |
| C. Snapshot copies | Each publication copies the graph or a full manifest | Trivial snapshot reads | O(N) per snapshot; rejected by tech §3.5 for cost; no history between snapshots |
| D. Event sourcing | An event log is the source of truth; tables are projections | Complete audit, replay | Event schema versioning, projection rebuilds, eventual consistency: a whole infrastructure (owner: avoid) |

## Recommendation: Option A

### 1. Vocabulary

| Term | Definition |
|---|---|
| **Fact** | An entity, relationship, external-identity binding, alias, or evidence assertion (ADR-0018) |
| **Identity row** | Immutable: the fact's ID, organization, the revision that created it and, for relationships, the type and endpoints. Never updated |
| **Version row** | One state of a fact, valid for `[revision_from, revision_to)`. Its content is immutable. Its only mutable cell is `revision_to`, set **once** from `NULL` to the revision that supersedes it |
| **Change set** | The set of version rows written by one transaction, numbered by one revision. The unit of audit (GOV-04), consistency and rollback |
| **Revision** | `bigint`, per organization, gap-free, increasing in commit order |
| **Current** | `revision_to IS NULL` |
| **Snapshot** | An immutable, named pointer `(org_id, revision)` plus a graph hash (HIST-01) |
| **`record_state`** | Per version: `present`, `removed` (tombstone) or `merged`. Separate from business `lifecycle` (ADR-0017 §2.1) |

### 2. Immutable fact versions

- Identity rows: INSERT only.
- Version rows: INSERT, plus closing `revision_to` once. A plain PL/pgSQL `BEFORE UPDATE` trigger (no extension) rejects any update that changes another column, or that changes `revision_to` when it is already set. Column privileges restrict UPDATE to `revision_to` as well (ADR-0001 §Privileges). There is no DELETE privilege.
- Evidence rows: INSERT only. An assertion's end of validity is its own `revision_to`.
- `type_key`, `merged_into` and `record_state` live on version rows, so re-typing (ADR-0017 §2.4), merging and removal are new versions, not edits.
- A fact that doesn't change gets no new row.

### 3. Atomic publication

One change set is published in one transaction:

| Step | Action |
|---|---|
| 1 | `BEGIN` (READ COMMITTED). Read the input; compute its `input_hash` |
| 2 | **Lock the organization's counter:** `SELECT last FROM org_revision WHERE org_id = $1 FOR UPDATE`. Let `R = last + 1`. All other writers for this organization wait here |
| 3 | Load the affected current versions (now stable, because writers are serialized). Compute the difference. **If there is none: `ROLLBACK`.** No revision is consumed and nothing is written (idempotent) |
| 4 | Validate the result: taxonomy (ADR-0017), identity (ADR-0003), endpoint validity (§5), containment rules, allowed evidence kinds |
| 5 | `INSERT change_set (org_id, R, kind, channel, actor_kind, actor_namespace, actor_key, actor_label, source_ref, input_hash, reason, change_reference)`; a trigger sets `created_at` and `db_role` (§10) |
| 6 | For every changed fact: close the current version (`revision_to = R`), insert the new version (`revision_from = R`). New facts: identity row plus first version. Evidence and assertions: insert with `R` |
| 7 | In-transaction integrity checks on the touched rows: one current version per fact, one current `CONTAINS` parent, `container_id` agrees with `CONTAINS`, no dangling relationship |
| 8 | `UPDATE org_revision SET last = R`; `COMMIT` |

- **All or nothing:** a failure at any step rolls everything back. Readers never see part of a change set, because PostgreSQL makes the whole transaction visible at commit.
- **Commit order = revision order:** the counter row stays locked until commit, so revision `R + 1` can't be allocated before `R` commits or aborts. A reader that sees revision `R` has also seen every revision below it. Without this property, "as of R" could miss an earlier change set still in flight.
- **Gap-free:** an aborted transaction releases the lock without advancing `last`, so the next writer re-uses the number.
- **Scope:** in ATLAS-002 every committed change set is published (there are no drafts). Approval-based publication (tech §10, DEC-057) later adds a policy over `change_set.kind` and snapshot status, not new tables.

### 4. Snapshot consistency

- **Reading "current":** a single SQL statement sees one consistent MVCC snapshot. A read that needs several statements runs in `REPEATABLE READ READ ONLY`, or pins the revision: it reads `last` once and then queries "as of" that revision.
- **Reading a named snapshot:** the same as-of query at the snapshot's revision. Version rows are immutable and revisions are committed in order, so the result never changes over time.
- **`graph_hash`:** SHA-256 over a canonical serialization of every `present` entity and relationship version and its current assertions valid at the revision, sorted by ID. Revision numbers and timestamps are excluded, so the same facts give the same hash whatever their history. It verifies fixture loads (CP4) and lets two snapshots be compared cheaply.
- Snapshots never copy data. `graph_snapshot` rows are INSERT only; a label never moves to another revision.

### 5. Relationship endpoint validity

1. A relationship version may be current at revision R only if **both** endpoints have a version valid at R with `record_state = present`.
2. Removing or merging an entity at R requires, **in the same change set**, closing every current relationship that touches it (or, for a merge, re-pointing it as a new relationship to the survivor: ADR-0003). Otherwise publication fails at step 7.
3. Endpoints are immutable. "Changing" an endpoint means retiring the relationship and creating a new one.
4. Re-typing an endpoint (ADR-0017 §2.4) re-validates its relationships against the taxonomy in the same change set. A relationship the new type does not allow blocks the re-type until a steward resolves it.
5. Because of 1–2, an as-of query at any revision never returns a relationship whose endpoint is missing at that revision. The CP4 integrity suite checks this for **every** revision of the fixture history, not only the current one.

### 6. Historical reconstruction

| Question | Query shape |
|---|---|
| The graph as of revision R | Versions with `revision_from <= R AND (revision_to IS NULL OR revision_to > R)` and `record_state = present`, for entities, relationships, identities, aliases and assertions |
| What changed in `(R1, R2]` (HIST-02) | Versions with `revision_from` or `revision_to` in that interval, grouped by change set |
| Who changed a fact and why | Its versions joined to `change_set` (actor, channel, kind, reason, reference, server time; §10) and its assertions to `evidence` |
| Which taxonomy validated a version | `taxonomy_version` on the row |

History is complete for the canonical store: nothing is deleted, and every change has a change set.

### 7. Rollback semantics

| Kind of rollback | Meaning |
|---|---|
| **Before commit** | A failed or abandoned transaction leaves nothing behind. No revision is consumed |
| **Revert of a committed change set** | A **new** change set (`kind = revert`, `reverts_revision = R`). For each fact changed by R, it writes a new version equal to the version valid at `R − 1`, and closes assertions that R added (the evidence rows stay in history). History is never rewritten or deleted |
| Revert conflict | If a later change set also changed one of those facts, the revert is refused with the conflicting facts listed. A steward resolves it in a new change set. A revert never silently overwrites later work |
| Snapshot | A snapshot is never moved or deleted. "Going back to snapshot S" means reading S, or reverting to it with a new change set and a new snapshot |
| Schema | Alembic downgrades are supported for empty tables (dev, CI). A downgrade that would destroy data in `atlas_db` is not run without owner approval |

### 8. Deterministic fixture load and incremental import

- Fixtures carry explicit IDs (ADR-0015) and a canonical ordering. The loader computes `input_hash`.
- Same facts → no difference → no change set (§3 step 3). Different facts → one `fixture_load` change set with exactly the differences.
- Incremental imports (future) use the same diff-and-apply path, keyed by `(source, scope, input_hash)` (CON-06).
- Optimistic concurrency (future APIs): a fact version's `revision_from` is its ETag; `If-Match` compares it (412 on mismatch).

### 9. Proportionate to the MVP: what ATLAS-002 builds, and what it doesn't

| Built in ATLAS-002 | Not built (later, without reshaping these tables) |
|---|---|
| `org_revision`, `change_set`, version tables, `graph_snapshot` | Drafts and branches (tech §10, BL-116) |
| The publication procedure (§3) and integrity checks (§5) | Approval workflow for publication (DEC-057 Open) |
| As-of and diff repository functions, used by tests | Graph-reading APIs (none before authorization) |
| Graph hash | Partitioning, archiving or history compaction |
| The set-once trigger | Revert tooling for stewards (the semantics are fixed now; a CP4 test covers one revert) |
| — | Audit store (BL-118), event streams, temporal extensions |

### 10. Change attribution (revision 3)

Owner check (25 Oct 2026): every committed change set must say who or what made it, through which channel, what it did, when, and why, immutably and per organization. Revision 2's `change_set.actor` was a single untyped text and `created_at` could be supplied by the writer. That was the gap. The amendment below is columns and one trigger on `change_set`; no new table and no change to identity, version or evidence semantics.

| Requirement | Column or rule |
|---|---|
| Who or what initiated it | `actor_kind` ∈ {human, service, system} |
| Stable, namespace-qualified actor ID | `actor_namespace` + `actor_key`, never a display name. v1 namespaces (reference data, each fixed to one kind): `oidc` (human: `{issuer}\|{subject}` from a validated token, later), `atlas.service` (service: for example `fixture-loader`, `import-worker`, `connector.<name>`), `atlas.system` (system: for example `migration`, `revert`). A `CHECK` ties namespace to kind, so a service can't be recorded as a human |
| Display at the time | `actor_label`: optional snapshot for readability; never used to identify |
| Source or ingestion channel | `channel` ∈ {fixture_cli, import, api, connector, migration, system_job}; plus the existing `source_ref` and `input_hash` |
| Action and affected IDs | `kind` is the action. The affected entities and relationships are exactly the version and assertion rows with `revision_from = R` or `revision_to = R` (§6); nothing is stored twice |
| Server timestamp and revision | `revision` from the locked counter (§3). A `BEFORE INSERT` trigger **overwrites** `created_at` with the server's `now()` and `db_role` with `session_user`, whatever the writer sent |
| Reason or reference | `reason` (text) and optional `change_reference` (for example a ticket key) |
| Initiator vs approver | The change set records the **initiator**. Approvals (maker-checker, later) are a separate append-only table referencing `(org_id, revision)` or a draft, with their own actor columns and server time. An approval never edits the change set |
| Immutable across reclassification, rollback, history | `change_set` is insert-only (no UPDATE grant; ADR-0001). Re-typing, merges and reverts are new change sets with their own attribution; `reverts_revision` links a revert to the original |

**Spoofing.** The actor comes from the **execution context**, never from the payload:

- the fixture loader and importers use their configured service identity;
- a value such as "author" inside a fixture or import file is evidence (`source_ref`, or a human assertion), not the actor;
- later APIs take the actor from the validated token.

The database can't know which human is behind a session. What it can do is record which credential wrote (`db_role`), stop any role but the ingestion role from writing (ADR-0001), and keep the timestamp server-side.

**Renamed or deactivated users:** the key is the identity provider's subject (or the service name), which doesn't change on rename. A future, organization-scoped directory can join on `(actor_namespace, actor_key)`. Deactivation never deletes or rewrites history.

**Organization scope:** the change set's key is `(org_id, revision)`. There is no global actor table, and attribution is read only through organization-scoped queries (ADR-0016).

**Out of scope here:** login, RBAC, maker-checker, user directories, audit UI and connectors. These attach later to the columns above without changing canonical identity semantics.

## Worked example (synthetic)

One organization. Entities: E1 = `core.service` "Quote Service"; E2 = `azure.sql_database` "sqldb-quotes" (UAT); E3 = `k8s.workload` "quote-service" (UAT).

| Revision | Change set | What it does |
|---|---|---|
| R1 | `fixture_load` | Creates E1, E2 and E3. Creates relationship L1 = E1 `READS_FROM` E2, with a `documentation` assertion (design document A) |
| — | Snapshot `pilot-baseline` | Points to R1 with its graph hash H1 |
| R2 | `import` | Renames E1 to "Quotation Service". Adds L2 = E3 `WRITES_TO` E2 with a `provider_configuration` assertion. L1 untouched |
| R3 | `steward_edit` | A steward records that the service no longer reads the database: L1 gets a `removed` version (`human_assertion`) |
| — | Snapshot `after-cleanup` | Points to R3 |
| R4 | `revert` of R3 | The steward's change was wrong. L1 gets a new `present` version equal to its R1 state; the R3 assertion is closed but stays in history |

**`entity_version` (E1 only; E2 and E3 never change):**

| Row | `revision_from` | `revision_to` | `display_name` | `record_state` |
|---|---|---|---|---|
| E1·v1 | 1 | 2 | Quote Service | present |
| E1·v2 | 2 | NULL | Quotation Service | present |

**`relationship_version`:**

| Row | `revision_from` | `revision_to` | `record_state` | Assertions valid in this interval |
|---|---|---|---|---|
| L1·v1 | 1 | 3 | present | documentation (design doc A) |
| L1·v2 | 3 | 4 | removed | human_assertion "removed" (R3). The documentation assertion was closed at 3 as superseded by the steward's decision; its evidence row is unchanged |
| L1·v3 | 4 | NULL | present | documentation: a **new** assertion row at 4 on the same evidence row (closed rows are never re-opened); the R3 human assertion closed at 4 |
| L2·v1 | 2 | NULL | present | provider_configuration |

Only `revision_to` cells were ever updated, each once: E1·v1 (`NULL` → 2), L1·v1 (→ 3), L1·v2 (→ 4), and the two closed assertions. Every other cell is as first written.

**As-of reads:**

| As of | Entities | Relationships |
|---|---|---|
| R1 (`pilot-baseline`) | Quote Service, sqldb-quotes, quote-service | L1 (reads) |
| R2 | Quotation Service, sqldb-quotes, quote-service | L1 (reads), L2 (writes) |
| R3 (`after-cleanup`) | as R2 | L2 only |
| R4 (current) | as R2 | L1, L2 |

**Diff (R1, R3]:** E1 renamed (R2); L2 added (R2); L1 removed (R3). The trust of L1 and L2 is independent throughout: L1 is `documented`, L2 `discovered` (ADR-0018), which a single `access_mode` edge could not express (ADR-0017 §5).

**Reloading the R1 fixture at R4:** its facts differ from the current graph (rename, L2), so the loader would write a new change set (R5) setting the fixture's facts. Reloading it straight after R1 would have produced no change set at all.

## Trade-offs and risks

| Risk | Mitigation |
|---|---|
| History tables grow with churn | Only changed rows are versioned. Measured at the pilot size in CP4. Partitioning only when measured (Scale A+) |
| Forgetting the revision predicate | Repository functions are the only read path; tests cover as-of reads at every revision |
| The per-organization lock limits concurrent writers | Writers batch into one change set. Measured in CP4. Later: allocate revision ranges |
| A trigger is extra database logic | It is ten lines of PL/pgSQL, tested directly, and makes immutability hold even for a bug in the application |

## Impact on the database schema

Tables `org_revision`, `change_set` (with `reverts_revision`), `entity`/`entity_version`, `relationship`/`relationship_version`, `external_identity`, `entity_alias`, `evidence`, `fact_assertion` and `graph_snapshot`; one set-once trigger function. See ADR-0001.

## Impact on APIs and authorization (future)

- Read APIs take `snapshot_id` or `revision`; a missing value means "current".
- Writes return the new revision.
- History access is authorized like current access: a hidden entity's history is hidden too.

## Migration and compatibility

- Additive tables.
- Branches, discovery syncs and the audit store attach to `change_set` later without reshaping version tables.

## Approved by the owner (25 Oct 2026)

1. Option A, not temporal tables, snapshot copies or event sourcing.
2. Immutable versions with set-once `revision_to` (trigger plus column privilege); no physical deletion.
3. Atomic publication (§3), including commit-ordered, gap-free revisions and no change set for an unchanged input.
4. Snapshot consistency and the graph hash (§4).
5. Endpoint validity (§5) and historical reconstruction (§6).
6. Rollback semantics: revert as a new change set, refused on conflict (§7).
7. The ATLAS-002 scope limits in §9.
