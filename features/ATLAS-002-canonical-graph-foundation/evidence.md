# ATLAS-002 — Evidence Record

**Status:** **CP0 complete** (G0 passed, 2026-10-24; accepted by the owner 2026-10-25). **CP1 revision 2:** owner review of revision 1 recorded, amended decisions redrafted; every register row still Proposed, awaiting owner confirmation (G1). CP2–CP5 not authorized. ATLAS-002 not Accepted.

## 1. CP0 — A001-DEF-01 / E-48: Redis readiness after an outage

**Authorization:** owner, 2026-10-24 (ATLAS-002 approved in principle; CP0 first, including the frontend `e2e/backend.ref` update).

### 1.1 Backend

| Item | Evidence |
|---|---|
| Defect reproduced first | New `tests/integration/test_ready_redis_recovery.py` on unfixed `585f3f5` (backend `v0.1.0`): the first readiness check after the outage gave **503 `failed_check: redis`**, logged `redis_command_failed` with `exc_type: ConnectionError`, `operation: ping`. The outage test passed (as designed) |
| Fix | `atlas.persistence.redis.AtlasRedis`: `Retry(NoBackoff(), 1, supported_errors=(ConnectionError,))`. One reconnect for a stale pooled connection, inside the existing 1 s wall-clock budget. Timeouts are not retried. Connection-level only, not a task retry (DEC-046 unaffected) |
| Regression tests | Integration (test-owned TCP fault proxy in front of the test Redis, DB 11, no keys written): (1) first readiness after an outage = 200 with `{database: ok, redis: ok}`; (2) during the outage 503 `failed_check: redis` in < 1.5 s with no host or port in the body, then recovery. Unit test pins the reconnect configuration. **Mutation check:** removing the fix makes (1) fail again |
| First CI run found a test defect | On Linux, `close()` from another thread does not interrupt a blocked `accept()`. The proxy kept accepting after "stop", so the restart hit "Address already in use". Fixed with a polled stop flag (50 ms accept timeout) and joining before close. Verified in the digest-pinned `python:3.12.15-slim-trixie` image without network (refuse, drop, same-port restart) before re-pushing |
| Pull request | [atlas-backend#8](https://github.com/Kibana21/atlas-backend/pull/8): 2 commits, 4 files (+179/−3), file list equal to the local diff |
| Merge commit | **`2987262db765586b7b3e99011074ff6bc2380ee5`** |
| CI | PR head `a3ad4a9` and `main` ([run 40094805311](https://github.com/Kibana21/atlas-backend/actions/runs/40094805311)): `static`, `unit`, `contract`, `security`, `integration`, `images` **6/6 success**. `integration` (job 120874710306): `test_ready_redis_recovery.py ..`, **37 passed** (35 before), `db 11: 0 keys match 'atlas:test:*'` |
| Local (fresh clone) | `make check` 164 passed, coverage 94.50 %; `make contract` conforms (28 passed); `make security` clean; `make integration` 29 passed, 8 `ci_auth` skipped by design |

### 1.2 Frontend

| Item | Evidence |
|---|---|
| `e2e/backend.ref` | `585f3f5…` → **`2987262db765586b7b3e99011074ff6bc2380ee5`** |
| New E2E test | "an API idle during a Redis outage reports Ready on its first check afterwards (A001-DEF-01)": open `/status` (Ready), Redis proxy down then up with no browser traffic, Check again → **Ready**, Redis Operational, response 200, no `redis_command_failed` log event for that correlation ID |
| Verified both ways | Against backend `v0.1.0` (temporary worktree): **1 failed** (`Expected "Ready"`, `Received "Degraded"`), 24 passed. Against `2987262`: 25/25 |
| Test-harness defect found and fixed | CP7 changed "Check again" from `disabled` to `aria-disabled` (focus fix, E-53). After that, the helper's `toBeEnabled()` returned immediately, so a test that expects the **same** state after "Check again" could pass on the previous screen. Tests expecting a state change still synchronized on the new label. `checkAgainAndWait` now waits for the readiness request to finish or fail and for `aria-disabled="false"`; the keyboard test likewise. No `toBeEnabled` remains in `e2e/` |
| Pull request | [atlas-frontend#9](https://github.com/Kibana21/atlas-frontend/pull/9): 1 commit, 6 files (+61/−11) |
| Merge commit | **`8ed5deb895dced78f98bff13cedd14c28a70f4ac`** |
| CI | PR head `5212682` and `main` ([run 40095359958](https://github.com/Kibana21/atlas-frontend/actions/runs/40095359958)): **7/7 success**. `e2e` (job 120876327973) checked out backend `2987262…`: **25 passed**, including the A001-DEF-01 test; `db 11: 0 keys match` |
| Local (fresh clone) | `pnpm check` 65 passed, 98.17 %; full audit clean; specs and generated OK; `pnpm e2e` 25/25 |

### 1.3 Gate G0

| Criterion | Result |
|---|---|
| Defect closed with a regression test that fails on the old code | ✔ backend integration and frontend E2E, both verified both ways |
| Required checks green on PR and `main` | ✔ backend 6/6, frontend 7/7 |
| ATLAS-001 tags and contract pins unchanged | ✔ `contract-v0.1.0` → `bfe4a09`, backend `v0.1.0` → `585f3f5`, frontend `v0.1.0` → `b9f235e`; both `specs.lock` = `bfe4a09` |
| Shared services | ✔ Redis DB 1 = 3 keys, DB 10 = 0, DB 11 = 0; no configuration change. PostgreSQL untouched (CP0 issues only `SELECT 1` through the runtime role) |

**Verdict: Gate G0 — PASS.**

### 1.4 Notes

| ID | Item | Status |
|---|---|---|
| N-01 | The harness weakness above went unnoticed in CP7 because every CP7 status test expected a *change* of state; it surfaced only when CP0 added a same-state test. Reviewed against the CP7 suite: every status, contract and accessibility test synchronized on a state change. The one weak spot was the keyboard test's **Enter** step, which did not prove that Enter triggered a refetch (its Space step did, through "Last checked"). It now waits for the readiness request. The G7 conclusions stand; this precision is recorded here | Fixed |
| N-02 | Stopping the preview worker by signalling its **child** process made taskiq's supervisor restart it and wait. A read-only check showed Ctrl+C (SIGINT to the process group), group SIGTERM and top-process SIGTERM all stop `make worker` cleanly in about 1 s, so there is no defect. Operate the worker through its top process or process group | Operations note |

## 2. CP1 — decision drafting (no product code)

| Deliverable | Location |
|---|---|
| Decision matrix (exact choices awaiting approval) | `decision-matrix.md` |
| Proposed ADRs | `adr/ADR-0001` (canonical store and scale), `ADR-0003` (identity matching), `ADR-0008` (revisions), `ADR-0015` (IDs), `ADR-0016` (tenancy), `ADR-0017` (taxonomy), `ADR-0018` (trust and evidence) |
| Register | DEC-050, DEC-056, DEC-058, DEC-070: Open → **Proposed**; DEC-021, DEC-025, DEC-031, DEC-034, DEC-037 stay Proposed with ADR links (register v0.6) |
| RTM | `requirements-registry.csv` and the matrix regenerated (68 requirements no longer list DEC-050/056/058/070 as Open; R0 177 → 124). R1/R2 mean "no Open decision", not approval |
| Baselines | Unchanged. The INV-02 deviation is recorded only after approval |

CP2 starts only after the owner approves the decisions.

### 2.1 Owner review and revision 2 (2026-10-25)

- **Owner review (written, in the conversation, 25 Oct 2026):** overall direction approved; CP0 accepted as complete. Approved: D1, D2, D3, D5, D9, D10, D13, D14, D16, D18 (subject to consistency with the authoritative specifications). Approved with clarification: D4, D11, D12. Amend: D6, D7, D8, D15, D17. Instruction: keep unapproved decisions Proposed; no CP2, graph tables, migrations or role changes until the revised decisions are approved.
- **Revision 2:** ADR-0017 (catalog, matrix, coverage, gaps, `READS_FROM`/`WRITES_TO`, `CONTAINS` vs `MEMBER_OF`), ADR-0003 (ARM original and normalized keys), ADR-0008 (revision lifecycle and example), ADR-0001 (schema alignment, ingestion role and privilege matrix), ADR-0018 (alignment); ADR-0015/0016 status notes only. `decision-matrix.md` revision 2 with the baseline-consistency review (C-01…C-12) and the confirmation table.
- **Register:** v0.7 annotations only; **no status changes** (totals unchanged). The approved rows are not moved to Confirmed individually: G1 confirms them together, after the consistency review in `decision-matrix.md` §3.
- **Not done:** no role, credential, grant, table, migration or product code. Baselines unchanged.
