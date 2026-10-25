# ATLAS-002 — Acceptance criteria

**Status:** **Proposed**. CP2 criteria are met by this delivery (evidence §3, §4); CP3 and CP4 criteria are met (G3, G4); every criterion is traced to tests, runs and SHAs in `evidence.md` §12.3; AC-CP5-01 awaits the owner's G5 sign-off.

## CP2 — Contracts and golden fixture (this delivery)

| ID | Given / When / Then |
|---|---|
| AC-CP2-01 | Given the taxonomy artifact, when CI runs, then it validates against its schema and every self-check T-01…T-10 passes, with 38 types and 8 provider-neutral types |
| AC-CP2-02 | Given every canonical schema, when CI runs, then each is a valid 2020-12 schema, every valid example is accepted and every invalid example is rejected |
| AC-CP2-03 | Given the golden fixture, when the validator runs, then HARD = 0, DOMAIN = 0 and the ADVISORY findings equal `expected-findings.json` |
| AC-CP2-04 | Given the fixture is regenerated, then every file is byte-identical to the committed one |
| AC-CP2-05 | Given the import batch, when it is planned against revision 1, then it yields exactly revision 2's facts and the expected rejection; against revision 2 and head it yields no change |
| AC-CP2-06 | Given each negative mutation of the fixture in `tools/tests/test_canonical.py`, then the validator reports the expected rule |
| AC-CP2-07 | Given an import payload containing an actor, revision, server timestamp or database role, then the schema rejects it |
| AC-CP2-08 | Given taxonomy 1.1.0, when contract evidence supports `CONTAINS` or `DEPLOYED_AS`, then it is accepted, the fact is `documented`, and a verification resting on it alone for a physical claim is rejected (U-1) |
| AC-CP2-09 | Given `trust-function-v1/cases.json`, when the reference trust function runs, then every case gives its expected trust state, rule, verification state and selected values. Given the golden fixture, every stored trust state equals the function at every revision (U-3) |

## CP3

| ID | Given / When / Then |
|---|---|
| AC-CP3-01 | Given the migration on `atlas_test`, when it is upgraded, downgraded and upgraded again, then it succeeds with no drift and creates no extension |
| AC-CP3-02 | Given the runtime role, when it inserts, updates or deletes any canonical row, then it is denied |
| AC-CP3-03 | Given the ingestion role, when it updates any column other than `revision_to` (or `org_revision.last`), deletes, truncates, creates a temporary table or connects to the other environment's database, then it is denied; a second change of `revision_to` is rejected by the trigger |
| AC-CP3-04 | Given a change set inserted with a client-supplied `created_at` or `db_role`, then the stored values are the server's |
| AC-CP3-05 | Given the golden rows, when loaded into `atlas_test`, then the database accepts them and the HARD checks pass as SQL |
| AC-CP3-06 | Given each negative case of the fixture tests, when written through the publishing procedure, then it is rejected with its rule's reason |
| AC-CP3-07 | Given the taxonomy seed, then CI shows it equals the pinned artifact |
| AC-CP3-09 | Given the local single-user model (`ATLAS_DB_ROLE_MODEL=single`, superuser `atlas_db_user`), when the integration suite runs on `atlas_test`, then every test passes except those that need separated roles, which are skipped with the stated reason; CI runs the separated-roles suite (AC-CP3-02/03) and the single-user suite on every change |
| AC-CP3-08 | Given the backend trust function, when it runs the pinned truth table and the golden rows, then every case and every stored trust state match, and the publishing procedure rejects versions failing D-12, D-19 or D-20 |

## CP4

| ID | Given / When / Then |
|---|---|
| AC-CP4-01 | Given an empty organization, when the loader applies the fixture's inputs, then revision 2 equals the fixture's and every as-of graph hash matches `expected-as-of.json` |
| AC-CP4-02 | Given the same batch again, then no change set is written |
| AC-CP4-03 | Given a revert of revision 4, then the result equals the fixture's revision 5; a revert of a later-modified fact is refused |
| AC-CP4-04 | Given the integrity suite, then H-10, H-14 and D-09 hold at every revision |
| AC-CP4-05 | Given the pilot-size benchmark, then its results are recorded (no thresholds before the owner sets them), including the publishing procedure's state load (A2-T25) |
| AC-CP4-06 | Given evidence that is added, closed or expires, when the affected facts are republished or recomputed, then their stored trust states equal trust function v1 and untouched facts are unchanged (A2-T27) |
| AC-CP4-07 | Given a revision that re-typed an entity (the steward reclassification r6, the taxonomy migration r7), when it is reverted, then a new attributed `revert` change set restores the earlier version exactly, **including the taxonomy version it recorded**; the reverted revision still reconstructs. Given a revert that conflicts (a fact changed again later, or a relationship the restored type does not allow), then it is refused with its rule and nothing is written (owner instruction at G4, 25 Oct 2026; A2-T28) |

## Future performance acceptance gate (PG-1; owner instruction at G4, 25 Oct 2026)

Not part of G4 or ATLAS-002 acceptance. The publishing procedure currently loads and validates the organization's whole current state on every publish (CP3-D7; benchmark in `evidence.md` §9.3). That is approved for fixture loads and batch imports only, **not** as the implementation for interactive editing (`spec.md` §7.1). Before any release with interactive writes or Scale A data, a performance gate PG-1 must pass. Its thresholds are set by the owner before the work starts; the measurements run in CI or a disposable environment only, never on the shared server (A002-FR-12).

| ID | Given / When / Then |
|---|---|
| PG-1.1 | **Single-entity update:** given organizations of increasing size, when one entity changes, then publication time is within the owner's threshold and does not grow linearly with the organization's size |
| PG-1.2 | **No-op publishing:** given an unchanged input, when it is published, then nothing is written and the time is within the threshold |
| PG-1.3 | **Concurrent writers:** given several writers on one organization (and on different organizations), then revisions stay gap-free and in commit order, no write is lost, and wait times are recorded against the threshold |
| PG-1.4 | **Increasing graph sizes:** given the pilot size (10k/40k) and at least one larger step towards Scale A, then initial load, update, no-op and state-load times are recorded per size, and the growth curve is reported |
| PG-1.5 | **Historical reconstruction:** given a long history, when the graph is reconstructed as of an early, middle and recent revision, then the result equals the recorded graph hash and the time is within the threshold |

## CP5

| ID | Given / When / Then |
|---|---|
| AC-CP5-01 | Given the evidence record, then every criterion above links to runs, counts and SHAs, and the owner signs off |
