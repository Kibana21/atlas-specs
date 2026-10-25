# ATLAS-002 — Tasks (CP3–CP5)

**Status:** **Proposed**; not authorized. IDs are stable.

## CP3 — Canonical store schema and validation (atlas-backend; specs for the role script)

| ID | Task | Depends on | Requirement |
|---|---|---|---|
| A2-T01 | Write `proposals/postgres-ingest-roles.sql` from the DEC-044 amendment §7 (guards, roles, settings, rollback) | — | A002-FR-03 |
| A2-T02 | **Owner** runs A2-T01 with owner-created passwords (gate G3-R) | A2-T01 | DEC-044 |
| A2-T03 | Read-only verification (`atlas doctor`), evidence recorded | A2-T02 | DEC-044 |
| A2-T04 | Pin specs; add ingest settings; API never reads them (test) | — | A002-FR-09 |
| A2-T05 | CI: verbatim bootstrap copy, checker, masked passwords; images check | A2-T01 | DP-3 |
| A2-T06 | Migration `0002`: tables, keys, FKs, `CHECK`, partial unique indexes | A2-T04 | A002-FR-01 |
| A2-T07 | Triggers: set-once `revision_to`; change-set server fields | A2-T06 | A002-FR-02 |
| A2-T08 | Grants per the matrix; fail when the role is missing | A2-T06 | A002-FR-03 |
| A2-T09 | Taxonomy seed from the pinned artifact + CI seed check | A2-T06 | A002-FR-04 |
| A2-T10 | Normalizers + golden tests | A2-T04 | A002-FR-05 |
| A2-T11 | `OrgScope` repository layer (mypy-enforced) | A2-T06 | A002-FR-06 |
| A2-T12 | Domain validator D-01…D-18 with readable reasons | A2-T09 | A002-FR-07 |
| A2-T13 | Publishing procedure with integrity checks | A2-T11, A2-T12 | A002-FR-08 |
| A2-T14 | Privilege tests (FR-30 extended): app read-only; ingest insert + set-once close; no delete, truncate, DDL, TEMP; no cross-environment connect | A2-T08 | DEC-044 |
| A2-T15 | Load the golden rows into `atlas_test`; HARD rules as SQL checks | A2-T13 | A002-FR-11 |

## CP4 — Loader, integrity and benchmark (atlas-backend)

| ID | Task | Depends on | Requirement |
|---|---|---|---|
| A2-T16 | Loader CLI as the ingestion role; actor from configuration | CP3 | A002-FR-09 |
| A2-T17 | Import planner; R2 reproduction; replay no-op; rejection report | A2-T16 | A002-FR-09 |
| A2-T18 | Revert command; conflict refusal | A2-T13 | A002-FR-10 |
| A2-T19 | As-of and graph hash equal to `expected-as-of.json` at every revision | A2-T16 | A002-FR-11 |
| A2-T20 | Pilot-size benchmark in CI (synthetic 10k/40k) | A2-T16 | A002-FR-12 |

## CP5 — Evidence and acceptance (all)

| ID | Task |
|---|---|
| A2-T21 | Evidence, traceability to acceptance criteria |
| A2-T22 | Release proposal (versions and tags only with owner approval) |
| A2-T23 | Owner acceptance (G5) |
