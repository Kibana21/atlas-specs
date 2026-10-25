# ATLAS-002 — Acceptance criteria

**Status:** **Proposed**. CP2 criteria are met by this delivery (evidence §3); CP3–CP5 criteria apply when those checkpoints are authorized.

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

## CP4

| ID | Given / When / Then |
|---|---|
| AC-CP4-01 | Given an empty organization, when the loader applies the fixture's inputs, then revision 2 equals the fixture's and every as-of graph hash matches `expected-as-of.json` |
| AC-CP4-02 | Given the same batch again, then no change set is written |
| AC-CP4-03 | Given a revert of revision 4, then the result equals the fixture's revision 5; a revert of a later-modified fact is refused |
| AC-CP4-04 | Given the integrity suite, then H-10, H-14 and D-09 hold at every revision |
| AC-CP4-05 | Given the pilot-size benchmark, then its results are recorded (no thresholds before the owner sets them) |

## CP5

| ID | Given / When / Then |
|---|---|
| AC-CP5-01 | Given the evidence record, then every criterion above links to runs, counts and SHAs, and the owner signs off |
