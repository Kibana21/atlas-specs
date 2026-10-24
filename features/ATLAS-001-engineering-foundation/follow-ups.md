# ATLAS-001 — Follow-ups after acceptance

**Date:** 24 October 2026 · **Context:** recorded at the owner's acceptance of ATLAS-001 v0.1.0 (`evidence.md` §13.11). ATLAS-001 is Accepted *subject to* these items and the deviations in `evidence.md`. Scheduling any item needs owner approval; none is part of ATLAS-001.

| ID | Kind | Source | Summary | State |
|---|---|---|---|---|
| A001-DEF-01 | Backend defect | E-48 | First readiness check after a Redis outage falsely reports Redis failed in an API process that was idle during the outage | **Closed 2026-10-24** by ATLAS-002 CP0 (backend `2987262`, frontend `8ed5deb`; `features/ATLAS-002-canonical-graph-foundation/evidence.md` §1) |
| A001-OBS-01 | Tracked observation | E-62 | One unreproduced axe violation in a fresh-clone E2E run | **Open** — monitoring |
| DEC-084 | Open owner decision | E-35 | Local `pg_hba` hardening approved in principle, not applied | **Open** (unchanged; no infrastructure change) |
| E-07 | Optional owner action | §8.3 | Rotation of the existing git OAuth credential | **Open** (unchanged; no credential change) |

## A001-DEF-01 — Redis readiness after an outage (E-48)

**Closed 2026-10-24 (ATLAS-002 CP0).** Fix: one reconnect on a connection error within the 1 s budget, as proposed below. The required integration and E2E regression tests were written first and fail on `585f3f5`. Backend [atlas-backend#8](https://github.com/Kibana21/atlas-backend/pull/8) → `2987262`; frontend [atlas-frontend#9](https://github.com/Kibana21/atlas-frontend/pull/9) → `8ed5deb` (`e2e/backend.ref` moved). The ATLAS-001 release tags are unchanged. The original record follows.

**Severity:** low–medium. A transient false "degraded" status: the API reports `redis` failed although Redis is reachable again. It self-corrects on the next check. No data is affected, but it violates FR-56 / AC-15 "never shows a false state" for one check, and invariant 3 (unknown stays unknown, failures are not invented).

**Observed (2026-10-24, CP7):** in the E2E stack, two API processes shared one Redis fault proxy. The proxy was taken down and brought back while the diagnostics-disabled API sent no Redis command. That process's next `GET /api/v1/health/ready` returned 503 `DEPENDENCY_UNAVAILABLE`, `failed_check: redis`, and logged `redis_command_failed` with `exc_type: ConnectionError`, `operation: ping`. The following check returned 200. The API that *was* used during the outage recovered on its first check. PostgreSQL does not show this (`pool_pre_ping=True`).

**Probable cause (hypothesis, not yet proven by a test):** the redis-py connection pool keeps an idle connection whose socket the outage closed. The first command after recovery uses it, fails with `ConnectionError`, and the probe reports failure instead of reconnecting.

**Reproduction (manual):**

1. Start the API with `ATLAS_REDIS_URL` pointing at a TCP pass-through proxy in front of Redis (for example the frontend E2E harness `e2e/support/fault-proxy.ts`, or a pytest fixture).
2. `GET /health/ready` → 200 (a pooled Redis connection now exists).
3. Without sending any request to this API, stop the proxy (dropping its connections), then start it again.
4. `GET /health/ready` → **actual:** 503 `failed_check: redis`; **expected:** 200.

**Required regression test (before the fix is merged):**

- A backend integration test (`tests/integration/`, Redis DB 11, run prefix, exact-key hygiene unchanged) with an in-process TCP proxy fixture: warm readiness 200 → drop all proxy connections and restart the proxy with no app traffic in between → the **first** readiness call returns 200 with `{database: ok, redis: ok}`.
- The test must fail on the current code (`585f3f5`) and pass with the fix.
- A second assertion keeps the outage behaviour: with the proxy down, readiness returns 503 `failed_check: redis` within the existing 1 s probe budget, with no host or URL in the body.
- Frontend follow-up: re-enable the shared-proxy case in the E2E suite (an idle API process across a Redis outage recovers on its first check).

**Proposed remediation (for review, not implemented):**

- In `atlas.persistence.redis`, let the probe reconnect **once** on a connection-level error within the same 1 s budget, for example redis-py `Retry(NoBackoff(), 1)` with `retry_on_error=[ConnectionError, TimeoutError]`, or `health_check_interval` on the pool so stale connections are checked before use.
- This is connection-level resilience for a health probe. It is not a task-level retry, so DEC-046 / BL-201 are unaffected.
- Apply the same client settings to the worker's broker connection if the test shows the same effect there (the listener already reconnects, E-22).
- Release path: backend PR with the test, `make check`, `make integration`, CI 6/6; then bump frontend `e2e/backend.ref` in a reviewed PR so the E2E suite runs against the fixed backend.

## A001-OBS-01 — Intermittent accessibility result (E-62)

- **What happened:** the first E2E run in a fresh clone reported an axe violation in the first `/status` scan. The details were cut off in the terminal output. It did not reproduce in 24 further runs (local and CI).
- **Mitigation in place:** each axe scan waits until `document.getAnimations()` is empty (a running opacity transition was the most plausible cause). No axe rule is disabled.
- **Monitoring:** every `e2e` CI run attaches the full axe JSON per scan to the `e2e-report` artifact. If a scan fails again, record the rule, node and run link here and open a defect.
- **Close criterion (proposal):** no recurrence in the next 20 `e2e` runs on `main` and pull requests, or a root cause found and fixed.
