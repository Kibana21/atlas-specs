# ATLAS-002 — Implementation plan (CP3–CP5)

**Version:** 0.1 · **Date:** 25 October 2026 · **Status:** **Proposed**. Nothing here is authorized until the owner authorizes each checkpoint.

## Sequence

| Step | CP | Repository | Work | Gate |
|---|---|---|---|---|
| 1 | CP3 | atlas-specs | Ingestion-role bootstrap script (from the DEC-044 amendment) | PR, owner review |
| 2 | CP3 | local server | **Owner runs the script**; Claude verifies read-only | **G3-R** |
| 3 | CP3 | atlas-backend | Pin specs (`specs.lock`); settings `ATLAS_INGEST_DATABASE_URL`, `ATLAS_DB_INGEST_ROLE`; CI bootstrap copy and checker | CI green |
| 4 | CP3 | atlas-backend | Migration `0002` (tables, constraints, two triggers, grants), taxonomy seed and seed check | Round-trip on `atlas_test`; CI green |
| 5 | CP3 | atlas-backend | Normalizers, `OrgScope` repository, domain validator, publishing procedure; load the golden fixture's rows in tests | **G3**: privileges, constraints, rejection of invalid input |
| 6 | CP4 | atlas-backend | Loader CLI (ingestion role) and import planner; replay no-op; revert | Fixture reproduces revision 2 and every as-of hash |
| 7 | CP4 | atlas-backend | Integrity suite at every revision; pilot-size benchmark in CI | **G4** |
| 8 | CP5 | all | Evidence, release proposal, owner acceptance | **G5** |

## Approach

- **Reuse the contracts:** backend tests read the pinned schemas, taxonomy and fixture directly. The golden examples for normalizers and rules are the same files; no DTO is copied by hand.
- **Database does structure and security only:** keys, FKs, `CHECK`, partial unique indexes, column privileges, the two triggers. Matrix and architecture rules live in the domain validator (DOMAIN) and reports (ADVISORY).
- **One write path:** the publishing procedure (ADR-0008 §3). The fixture loader and future importers use it, as the ingestion role.
- **Evidence:** every checkpoint records commands, counts, run URLs and SHAs in `evidence.md`.

## Risks

| Risk | Mitigation |
|---|---|
| Behaviour drift between the reference model and the backend | Backend tests assert the same expected as-of hashes, plans and findings as the fixture |
| Per-organization write lock limits throughput | Benchmark in CP4; batching |
| Local `trust` authentication (DEC-084) | Ingestion-role separation is enforced in CI; locally it prevents mistakes only |
| Open items U-1…U-7 | Raised before the code that depends on them (U-3 before the trust function) |
