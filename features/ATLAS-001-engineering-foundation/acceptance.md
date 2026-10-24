# ATLAS-001 — Engineering Foundation: Acceptance Criteria

**Status:** Draft — awaiting approval · **Date:** 24 October 2026 · **Spec:** `spec.md` · **Tasks:** `tasks.md`

## How acceptance works

- Each criterion has Given/When/Then, the exact **verification** (command or CI job), the **evidence** to attach at sign-off, and the tasks that deliver it.
- Acceptance runs on **clean clones** of all three repositories at the tagged release candidate SHAs. CI evidence must come from those SHAs.
- A criterion passes only with evidence. "Works on my machine" is not evidence (DEC-012).
- Requirement links: `FR`/`NFR` = `spec.md` §5/§8. "Tech §17.8 #n" = the repository acceptance bullets in the technical design.

---

## A. Repository independence and contract governance

### A001-AC-01 — Each repository passes its own checks independently
*Tech §17.8 #1 · FR-06, FR-10, FR-11, FR-40, FR-41, NFR-01, NFR-03*

- **Given** a clean clone of exactly one repository and only its README,
- **When** the developer runs its documented check command (`make check` in specs/backend, `pnpm check` in frontend) and its CI workflow runs on a PR,
- **Then** all steps pass without copying files from another repository. The only cross-repo input is the read-only fetch of `atlas-specs` at the pinned SHA.

**Verify:** `make check` / `pnpm check` exit 0. CI runs `specs-ci`, `backend-ci`, `frontend-ci` green. A test PR with one lint error and one type error fails `static`.
**Evidence:** three CI run links plus terminal logs. **Tasks:** S2-03…S2-07, B1-01…B1-04, B6-01, F1-01…F1-04, F5-01, F5-02.

### A001-AC-02 — Backend and frontend identify the same immutable specs revision
*Tech §17.8 #2 · FR-05, FR-48 · ADR-0006*

- **Given** `specs.lock` in backend and frontend,
- **When** lock validation runs and the frontend E2E queries the running backend's build info,
- **Then** both locks contain the same 40-hex SHA equal to tag `contract-v0.1.0`, `contract_version` matches the contract `info.version`, and the parity assertion passes. A branch name, short SHA, unknown SHA or mismatched version fails validation with a specific message.

**Verify:** `tools/check_specs_lock.py` on both locks. Frontend `e2e` parity test. Negative drill X1-03 fails as expected.
**Evidence:** validator output for valid and four invalid samples; link to the failed parity drill run. **Tasks:** M0-04, M0-05, S1-02, S2-02, S2-09, B5-01, B6-03, F2-01, F4-06, X1-03.

### A001-AC-03 — Incompatible API changes are blocked before merge
*Tech §17.8 #3 (client generation part), #5 · FR-06, FR-27, FR-42*

- **Given** the pinned 0.1.0 contract,
- **When**
  - (a) a specs PR removes a response field without a major version bump,
  - (b) a backend PR renames a response field in a Pydantic model,
  - (c) a frontend PR hand-edits `src/generated/api`,
- **Then**
  - (a) `breaking-change` fails in specs CI,
  - (b) `contract` fails in backend CI with the oasdiff difference,
  - (c) `client-repro` fails in frontend CI.
  - Reverting each change turns the job green.

**Verify:** three deliberate test PRs (closed afterwards).
**Evidence:** three failed and three passing run links. **Tasks:** S2-08, B5-03, B5-04, B6-03, F2-02, F2-03, F5-03.
*Note:* the "does not bypass FastAPI authorization" half of Tech §17.8 #3 is deferred to BL-104 (authentication is out of scope, spec §3).

### A001-AC-04 — Local development is reproducible from the READMEs
*FR-12, FR-29, spec §7, NFR-01, NFR-02*

- **Given** a macOS or Linux machine with the documented prerequisites (Docker-compatible runtime or native PostgreSQL 16/Redis 7, uv, Node via `.nvmrc`, pnpm),
- **When** an engineer who did not write the setup follows only the READMEs through the spec §7 smoke journey,
- **Then** PostgreSQL and Redis are healthy, migrations apply, the API answers on :8000, the worker processes a ping job to `succeeded`, and `/status` on :3000 shows all checks green with SHAs. `make check` finishes in ≤ 60 s and `pnpm check` in ≤ 90 s on the reference laptop.

**Verify:** X2-01 dry run by a second engineer on a clean clone.
**Evidence:** timed log of commands and outputs, plus a screenshot of `/status`. **Tasks:** B1-06, B1-07, B2-10, B4-11, F1-06, X1-04, X1-05, X2-01.

---

## B. Backend runtime

### A001-AC-05 — Health endpoints and buildable images
*Tech §17.8 #4 · FR-17, FR-22, FR-28*

- **Given** the API running against compose services,
- **When** `GET /api/v1/health/live` and `GET /api/v1/health/ready` are called with both dependencies up, then with Redis stopped, then with PostgreSQL unreachable,
- **Then** `live` is always 200. `ready` is 200 with both checks `ok` when healthy, and 503 with an error envelope `DEPENDENCY_UNAVAILABLE` naming the failed check (no host or credentials) otherwise. The `api` and `worker` images build from the same commit and run as non-root.

**Verify:** integration tests B3-07, B4-02. `docker build --target api|worker`. `docker run … id -u`.
**Evidence:** test report; `curl -i` transcripts for the three cases; image build log. **Tasks:** B2-06, B3-07, B4-02, B6-06, B6-07, F5-05.

### A001-AC-06 — Migrations are reviewed, reversible and drift-free
*FR-19, FR-20, FR-21*

- **Given** an empty PostgreSQL 16 database,
- **When** CI runs `upgrade head → downgrade base → upgrade head` and `alembic check`,
- **Then** every step succeeds, there is exactly one head, autogenerate reports no differences, and the schema has only `job`, `job_attempt`, `outbox_event` (plus `alembic_version`) with the spec §6.6 constraints.

**Verify:** `pytest tests/integration/test_migrations.py`; `\dt` and `\d job` output.
**Evidence:** CI integration job log; schema dump. **Tasks:** B3-02…B3-05, B3-08, B3-09, B6-02.

### A001-AC-07 — Uniform error envelope and conventions
*FR-01, FR-03, FR-13, FR-15 · Tech §6.3*

- **Given** the API,
- **When** a request triggers validation failure (422), an unknown route (404), a missing `Idempotency-Key` (422), a dependency failure (503) and an unhandled exception (500, test-only route),
- **Then** every body validates against `contracts/schemas/error.v1.json`, carries the documented `code`, and has a `correlation_id` equal to the response header. The 500 body contains no traceback, SQL, file path, host name or settings value. The frontend maps each case and a network failure to a typed `AtlasApiError`.

**Verify:** backend `pytest -m "unit or contract"` (B2-04, B5-05); frontend unit tests (F2-05).
**Evidence:** test reports. **Tasks:** S1-01, S1-03, S1-06, B2-04, B2-05, B5-02, B5-05, F2-05.

### A001-AC-08 — Build provenance is complete and environment-restricted
*FR-18, FR-44 · Tech §17.4(7)*

- **Given** a build from known commits with `ATLAS_DIAGNOSTICS_ENABLED=true` and `ATLAS_ENV=test`,
- **When** `GET /api/v1/diagnostics/build` is called and `/status` is opened,
- **Then** the response validates against `build-info.v1.json` and reports the real `backend_sha`, the lock `specs_sha`, `contract_version` `0.1.0` and `db_migration_revision` `0001…`. `/status` additionally shows the `frontend_sha` of the build. With diagnostics disabled the endpoint returns 404. Starting the API with diagnostics enabled and `ATLAS_ENV=uat|prod` fails at startup.

**Verify:** B2-08 and B3-06 tests; B6-08 security test; E2E F4-03.
**Evidence:** JSON response vs `git rev-parse` of each repo; startup failure log. **Tasks:** S1-04, B2-01, B2-07, B2-08, B3-06, F3-03, F3-05.

### A001-AC-09 — Correlation IDs flow end to end
*FR-14, FR-43*

- **Given** the frontend sends `X-Correlation-ID: req_test123456`,
- **When** it calls `POST /diagnostics/jobs/ping` and the worker processes the job,
- **Then** the response header, the `job.correlation_id` column and the API and worker log lines all contain `req_test123456`. An invalid inbound value (e.g. `<script>` or 200 characters) is replaced, never echoed.

**Verify:** B2-03 unit tests; B4-09 integration test; F2-04 unit test.
**Evidence:** test reports plus one captured log pair. **Tasks:** B2-03, B4-09, F2-04.

### A001-AC-10 — Security baseline holds
*FR-15, FR-16, FR-30, FR-47 · NFR-05*

- **Given** the backend and frontend builds,
- **When** security tests and CI security jobs run,
- **Then** all of the following hold:
  - log records with secret-like keys or DSNs show `[REDACTED]`;
  - CORS returns no allow-origin header for unlisted origins;
  - API responses include `nosniff`, `no-referrer`, `no-store`;
  - `next start` responses include a CSP without `unsafe-eval`, `frame-ancestors 'none'`, nosniff and referrer policy;
  - dependency audits report no high/critical findings;
  - secret scanning fails a branch containing a fake credential;
  - containers run as non-root.

**Verify:** `pytest -m security`; B2-02/B2-09 tests; `curl -sI` against `next start`; CI `security` jobs; fake-secret drill.
**Evidence:** reports, header transcripts, drill run link. **Tasks:** B2-02, B2-09, B6-04, B6-08, F3-06, F5-04.

### A001-AC-11 — Jobs are idempotent, durable and retried correctly
*FR-23, FR-24, FR-25*

- **Given** API, relay and worker running,
- **When**
  - (a) `POST /diagnostics/jobs/ping` is sent twice with the same `Idempotency-Key`,
  - (b) a ping job is configured to fail twice,
  - (c) a ping job always fails,
  - (d) a succeeded job's message is redelivered,
- **Then**
  - (a) the first call returns 202 and the second returns 200 with the same job ID, and one job row exists;
  - (b) the job ends `succeeded` with 3 `job_attempt` rows and increasing delays within the backoff cap;
  - (c) it ends `failed` at `max_attempts` with a sanitized `last_error`;
  - (d) it stays `succeeded` with no extra side effects.
  - All responses validate against `job.v1.json`.

**Verify:** B4-03, B4-06, B4-07, B4-08 integration tests; Hypothesis backoff test.
**Evidence:** test report; one `GET /jobs/{id}` transcript per scenario. **Tasks:** S1-05, B4-01, B4-03, B4-06, B4-07, B4-08.

### A001-AC-12 — Outbox atomicity and Redis-loss resilience
*FR-23, FR-26 · Tech §8*

- **Given** the job service and relay,
- **When**
  - (a) an exception occurs after inserting a job inside its transaction,
  - (b) two relays run concurrently over the same pending events,
  - (c) Redis is flushed after the job is committed but before dispatch,
- **Then**
  - (a) neither the job nor the outbox row persists;
  - (b) each event is dispatched exactly once by the relays;
  - (c) the relay re-dispatches, the job reaches `succeeded`, and no `job` or `job_attempt` row is lost.

**Verify:** B4-04, B4-05, B4-10 integration tests in CI with real PostgreSQL/Redis.
**Evidence:** CI integration job log. **Tasks:** B4-04, B4-05, B4-10, B6-02.

### A001-AC-13 — Quality gates and coverage are enforced
*NFR-03, NFR-04*

- **Given** CI on both application repositories,
- **When** a PR lowers backend coverage below 85% or frontend `src/lib` + status coverage below 80%, or introduces a mypy/tsc/ESLint/Ruff error,
- **Then** the corresponding job fails. On the release candidate the thresholds are met.

**Verify:** CI runs plus coverage reports.
**Evidence:** coverage summaries; one failing drill. **Tasks:** B1-05, B6-05, F4-01.

---

## C. Frontend experience and browser verification

### A001-AC-14 — Bright landing with no dead controls, accessible
*FR-45, FR-46 · NFR-06 · DEC-011, DEC-012*

- **Given** the production build (`next build && next start`),
- **When** a user opens `/`,
- **Then** the page uses the proposed bright tokens (canvas `#F8FAFE`, primary `#1769E0`) and contains exactly one interactive element, a link to `/status`, which works with mouse and keyboard. A skip-link is present. axe-core reports zero serious/critical violations on `/` and `/status`.

**Verify:** F4-03 (keyboard path), F4-04 (axe), DOM assertion that only one interactive element exists.
**Evidence:** Playwright report. **Tasks:** F1-05, F3-01, F4-03, F4-04.

### A001-AC-15 — Status page shows true state in every condition
*FR-44*

- **Given** `/status` against a running backend,
- **When**
  - (a) all dependencies are healthy,
  - (b) Redis is stopped,
  - (c) the API is unreachable,
  - (d) the user presses Retry after recovery,
- **Then**
  - (a) it shows green checks and all provenance values;
  - (b) it shows a degraded state naming Redis, with the correlation ID;
  - (c) it shows an unreachable state with no fabricated values;
  - (d) it refetches and returns to the healthy state.
  - It never shows "ok" when the backend says otherwise.

**Verify:** component tests (F3-04) and E2E (F4-03).
**Evidence:** Playwright report with screenshots of each state. **Tasks:** F3-02, F3-03, F3-04, F4-03.

### A001-AC-16 — Full-stack browser E2E against persisted backend in two engines
*Tech §17.8 #6 · NFR-07 · DEC-012*

- **Given** the frontend `e2e` CI job,
- **When** it starts PostgreSQL, Redis, the backend at `e2e/backend.ref` (migrated, API + worker) and the production frontend build,
- **Then** the status, keyboard, accessibility, visual and parity suites pass in Chromium and WebKit against the real backend. No route interception or mocks are used in acceptance tests.

**Verify:** frontend CI `e2e` job; grep confirms no `page.route(` in the acceptance specs.
**Evidence:** run link plus Playwright HTML report artifact. **Tasks:** F4-02, F4-03, X1-01, X1-02.

### A001-AC-17 — Visual baselines exist and detect regressions
*NFR-08 · UX-NFR-012*

- **Given** golden screenshots of `/` and `/status` at 1440×900 and 1280×720 generated in the pinned Playwright container,
- **When** a test PR changes `--brand-primary`,
- **Then** the visual comparison fails. Reverting passes.

**Verify:** F4-05 drill.
**Evidence:** diff image from the failed run. **Tasks:** F4-05, X1-02.

---

## D. Scope guard

### A001-AC-18 — Foundation stays a foundation
*spec §3 · DEC-002*

- **Given** the release candidate of all three repositories,
- **When** reviewers inspect the diff since the ATLAS-001 start,
- **Then** there are:
  - no domain tables or models (entity, relationship, taxonomy, views);
  - no authentication or authorization code beyond the diagnostics environment guard;
  - no UI beyond `/` and `/status`;
  - no telemetry SDKs or enterprise telemetry ingestion;
  - no PR-analysis functionality.
  - The smoke journey meets A001-NFR-02 timings.

**Verify:** reviewer checklist; `grep -ri "opentelemetry\|applicationinsights" atlas-backend atlas-frontend` returns nothing; migration list = `0001` only.
**Evidence:** signed checklist. **Tasks:** X2-01, X2-02.

---

## Sign-off

| AC | Result | Evidence link | Verified by | Date |
|---|---|---|---|---|
| A001-AC-01 … A001-AC-18 | ☐ per row at sign-off | | | |

ATLAS-001 is accepted when all 18 rows are ticked with evidence, and tags `contract-v0.1.0` (specs), `v0.1.0` (backend) and `v0.1.0` (frontend) are recorded together in each repository's release notes.
