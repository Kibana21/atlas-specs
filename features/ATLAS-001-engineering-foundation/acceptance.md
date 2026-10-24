# ATLAS-001 — Engineering Foundation: Acceptance Criteria

**Version:** 0.2.1 (final candidate) · **Date:** 24 October 2026 · **Status:** Approved for Implementation (owner, 24 Oct 2026); CP1 authorized; ATLAS-001 not Accepted until G7 · **Spec:** `spec.md` v0.2.1 · **Tasks:** `tasks.md` v0.2.1

## Rules

- Each criterion states Given/When/Then, **Verify** (command, CI job or drill), **Evidence** to record in `evidence.md`, the **Gate** where it must first pass, and the delivering tasks.
- Final acceptance runs on clean clones at the SHA triple recorded in `evidence.md` (S-13). Drills are throwaway branches that are closed, never merged.
- Evidence is mandatory. A criterion with no recorded evidence is failed (DEC-012).
- **No acceptance step may modify shared services** beyond the owner-approved Atlas objects (spec NFR-06).

| AC | Title | First gate |
|---|---|---|
| AC-01 | Each repository passes its own checks independently | G1 / G5 / G7 |
| AC-02 | One immutable specs revision, with parity enforced | G1 / G5 / G7 |
| AC-03 | Contract conformance detects missing, unexpected and changed operations | G1 / G5 / G6 |
| AC-04 | Local development on existing services is reproducible and safe | G2 / G4 / G7 |
| AC-05 | Health, readiness and buildable images | G3 / G4 / G5 / G6 |
| AC-06 | Migration mechanism | G3 |
| AC-07 | Credential separation, least privilege and authentication strength | G2 / G3 / G5 |
| AC-08 | Uniform error envelope | G2 / G5 / G6 |
| AC-09 | Build provenance, environment-restricted | G3 / G6 |
| AC-10 | Correlation IDs end to end | G2 / G4 / G6 |
| AC-11 | Taskiq/Redis seam with key hygiene | G4 |
| AC-12 | Security baseline | G2 / G5 / G6 |
| AC-13 | Quality gates and coverage | G2 / G5 / G7 |
| AC-14 | Bright design foundation and accessibility | G1 / G6 / G7 |
| AC-15 | Status page tells the truth in every state | G6 |
| AC-16 | Chromium E2E against a persisted backend | G7 |
| AC-17 | Scope guard, exclusions and sign-off | G7 |

---

### AC-01 — Each repository passes its own checks independently

*Tech §17.8 #1 · FR-07, FR-20, FR-50 · NFR-01, NFR-03*

- **Given** a clean clone of one repository and its README only,
- **When** its check command runs (`make check` for specs/backend, `pnpm check` for frontend) and its CI workflow runs on a PR,
- **Then** everything passes without copying files from another repository. The only cross-repo inputs are read-only checkouts at pinned SHAs. `atlas-specs` checks need only Docker (digest-pinned lint images) and uv, not Node.

**Verify:** local commands exit 0, and the three workflows are green. Drill: a PR with one lint error and one type error fails `static` (backend and frontend).
**Evidence:** run links plus terminal logs. **Tasks:** S-09, S-10, S-11, B-01, B-28, B-23, B-24, F-01, F-11.

### AC-02 — One immutable specs revision, with parity enforced

*Tech §17.8 #2 · FR-05, FR-36, FR-51, FR-59 · DEC-039 (pending D-07)*

- **Given** `specs.lock` in backend and frontend,
- **When** lock validation runs, and the frontend E2E compares its lock with the backend's `/diagnostics/build.specs_sha`,
- **Then** both locks hold the same immutable 40-hex SHA (for ATLAS-001, the `contract-v0.1.0` release commit), `contract_version` equals `info.version`, and parity passes. Branch names, tag names, short SHAs, unknown SHAs and version mismatches are rejected with distinct messages.
- **And** the release tags `v0.1.0` (backend, frontend) are created only on commits whose lock points at a commit carrying a `contract-v*` release tag, which the owner approved (P-09).

**Verify:** `check_specs_lock.py` tests (S-06); `make specs` (B-18); `pnpm specs` (F-03); E2E parity test (F-10). Drill: point the frontend lock at another SHA, and E2E parity fails.
**Evidence:** validator output for the valid case and five invalid cases; drill run link; release-tag check output; owner's release approval. **Tasks:** S-02, S-06, S-12, B-18, F-03, F-10, B-26, F-14.

### AC-03 — Contract conformance detects missing, unexpected and changed operations

*Tech §17.8 #3 (client part), #5 · FR-06, FR-36, FR-51 · DEC-095*

- **Given** contract 0.1.0 and the conformance tool at the pinned SHA,
- **When** these cases are exercised:

| Case | Where | Expected |
|---|---|---|
| (a) Pydantic titles/descriptions only differ | tool self-test | **pass** |
| (b) Contract operation not implemented | self-test + backend drill (remove the route for `getHealthLive`) | fail `MISSING_OPERATION getHealthLive` |
| (c) Route implemented but not in contract | self-test + backend drill (add `GET /api/v1/diagnostics/extra`) | fail `UNEXPECTED_OPERATION GET /api/v1/diagnostics/extra` |
| (d) operationId differs | self-test | fail `OPERATION_ID_MISMATCH` |
| (e) Extra optional response property in code | self-test + backend drill | fail (normalized structural diff) |
| (f) Required property removed / status code changed | self-test | fail |
| (g) Contract PR removes a response field without a major bump | specs drill | `breaking` job fails |
| (h) Hand-edit of `src/generated/api` | frontend drill | `generated` job fails |

- **Then** every case gives the expected outcome, and reverting each drill turns its job green.

**Verify:** `tools/tests/test_conformance.py` (S-07); `make contract` (B-19); CI jobs `contract` (B-24), `breaking` (S-11), `generated` (F-11).
**Evidence:** test report plus 5 drill run links. **Tasks:** S-02, S-04, S-07, S-11, B-27, B-28, B-18, B-19, F-03, F-11.
*Note:* the "does not bypass authorization" half of Tech §17.8 #3 is deferred to BL-104.

### AC-04 — Local development on existing services is reproducible and safe

*FR-21, FR-35, spec §8 · NFR-01, NFR-06 · DEC-043/044/045/048*

- **Given** the owner's existing PostgreSQL 15 and Redis, P-03 applied, Node 24 and uv,
- **When** a second engineer follows only the READMEs through the spec §8 smoke journey,
- **Then** `make doctor` is green, migrations apply to `atlas_db`, the API and worker run, `make worker-smoke` is OK, and `/status` is green with SHAs.
- **Before and after** the journey, these are unchanged:
  - the list of non-Atlas databases and roles on the server;
  - the key count of every Redis DB other than 10/11;
  - the Redis container state.

**Verify:** B-25/F-13 dry runs. Snapshot via `make doctor SNAPSHOT=…` (read-only, B-08) before and after, with diff empty outside Atlas objects.
**Evidence:** timed log and the snapshot diff. **Tasks:** B-08, B-17, B-25, F-02, F-13.

### AC-05 — Health, readiness and buildable images

*Tech §17.8 #4 · FR-26, FR-31, FR-37, FR-58*

- **Given** the API running,
- **When** `/health/live` and `/health/ready` are called with dependencies healthy, with the database URL pointed at a closed port, and with the Redis URL pointed at a closed port,
- **Then** `live` is always 200. `ready` is 200 with `{database:ok, redis:ok}`, or 503 `DEPENDENCY_UNAVAILABLE` naming the failed check, with no host or credential in the body. Shared services are never stopped to test this.
- The `api`, `worker` and web images build from single commits and run as non-root.

**Verify:** B-09, B-13 integration tests; B-21, F-09 builds; CI `images`/`image` jobs.
**Evidence:** test reports, `curl -i` transcripts, `id -u` outputs. **Tasks:** B-06, B-09, B-13, B-21, F-09.

### AC-06 — Migration mechanism

*FR-28, FR-29 · DEC-046*

- **Given** `atlas_test` and `atlas_test_migrator`,
- **When** `upgrade head → downgrade base → upgrade head` and `alembic check` run,
- **Then** all succeed with a single head. `alembic_version` lives in schema `atlas`, owned by the migration role. The schema contains **no** tables other than `alembic_version`.

**Verify:** `tests/integration/test_migrations.py` (B-11); `make migrate` on `atlas_db` (B-10).
**Evidence:** CI integration log; `\dt atlas.*` output. **Tasks:** B-10, B-11.

### AC-07 — Credential separation, least privilege and authentication strength

*FR-21, FR-28, FR-30, FR-35, FR-39 · DEC-044, DEC-084*

- **Given** the approved four roles (`atlas_migrator`, `atlas_app`, `atlas_test_migrator`, `atlas_test_app`),
- **When** the privilege tests, settings guards, `make doctor` and the CI `ci_auth` test run,
- **Then**:
  - the API and worker use only the runtime credential, and Alembic only the migration credential;
  - test runs use only `atlas_test_*` credentials, and settings refuse mixed configurations;
  - the runtime role has `SELECT` by default and no `CREATE` or `TEMP`; it cannot write to a table without an explicit per-table grant;
  - neither environment's roles can connect to the other environment's database;
  - no Atlas role is superuser, or can create roles or databases, replicate or bypass RLS;
  - **in CI**, a wrong or missing password is rejected for every Atlas role;
  - **locally**, `make doctor` reports the authentication method read-only from `pg_hba_file_rules` (or *deferred*), so the `trust` limitation is documented, not hidden. No active authentication probe is run (A4).

**Verify:** `tests/integration/test_privileges.py` (B-12); `tests/unit/test_settings.py` (B-03); `ci_auth` test in CI (B-23); doctor output (B-08).
**Evidence:** test reports; read-only role listing; CI `ci_auth` log; doctor warning output. **Tasks:** B-03, B-08, B-12, B-22, B-23.

### AC-08 — Uniform error envelope

*FR-01, FR-03, FR-24, FR-52 · Tech §6.3*

- **Given** the API,
- **When** requests produce 404 (unknown route), 404 (diagnostics disabled), 503 (dependency) and 500 (test-only failing route),
- **Then** each body validates against `error.v1.json`, carries the documented code, and has `correlation_id` equal to the response header. The 500 body has no traceback, SQL, path, host or settings value. The frontend maps envelope, non-JSON and network failures to typed errors.

**Verify:** B-05 unit tests; B-20 contract tests; F-05 unit tests.
**Evidence:** test reports. **Tasks:** S-01, S-03, B-05, B-20, F-05.

### AC-09 — Build provenance, environment-restricted

*FR-27, FR-56 · Tech §17.4(7)*

- **Given** diagnostics enabled under `ATLAS_ENV=test`,
- **When** `/diagnostics/build` is called and `/status` is opened,
- **Then**:
  - the response validates against `build-info.v1.json` and reports the real backend SHA, the lock `specs_sha`, `0.1.0` and `0001_baseline`;
  - `/status` also shows `frontend_sha`;
  - with diagnostics disabled, the endpoint returns 404 and `/status` shows "Diagnostics disabled";
  - startup with diagnostics enabled under `uat`/`prod` fails.

**Verify:** B-07, B-12 tests; B-03 guard test; F-07 tests.
**Evidence:** JSON vs `git rev-parse`; startup failure log. **Tasks:** B-07, B-12, F-07.

### AC-10 — Correlation IDs end to end

*FR-23, FR-32, FR-52*

- **Given** the frontend sends `X-Correlation-ID: req_test123456`,
- **When** it calls the API, and a ping task is enqueued with that ID,
- **Then** the response header, API log line and worker log line all carry `req_test123456`. Invalid inbound values (`<script>`, 200 characters) are replaced, never echoed.

**Verify:** B-04, B-14 tests; worker log captured in B-15; F-05 tests.
**Evidence:** test reports plus one captured log pair. **Tasks:** B-04, B-14, F-05.

### AC-11 — Taskiq/Redis seam with key hygiene

*FR-31…FR-34 · DEC-045, DEC-046*

- **Given** Redis DB 11 and run prefix `atlas:test:<run_id>:`,
- **When** the worker round-trip test runs (real worker process, enqueue, marker observed),
- **Then**:
  - the test passes;
  - it deletes **only** keys it created;
  - afterwards no `atlas:test:<run_id>:*` key exists, and the set of other keys in DB 11 is unchanged;
  - no Atlas code uses `FLUSHALL`, `FLUSHDB`, pattern deletion, `CONFIG SET`, `SWAPDB` or `SELECT`;
  - the client factory refuses any other DB index;
  - the local smoke uses DB 10, leaves no keys, and leaves DB 1's key count unchanged.

**Verify:** B-15, B-16, B-17; CI integration job uses an isolated `redis:7.4` service.
**Evidence:** test report; `scripts/redis_keys.py` before/after outputs. **Tasks:** B-13, B-14, B-15, B-16, B-17.

### AC-12 — Security baseline

*FR-24, FR-25, FR-38, FR-57 · NFR-05*

- **Given** backend and frontend builds,
- **When** security tests and CI security jobs run,
- **Then**:
  - secrets and DSNs in logs are redacted;
  - unlisted CORS origins get no allow header;
  - API responses carry `nosniff`, `no-referrer`, `no-store`;
  - `next start` serves a CSP without `unsafe-eval`, `frame-ancestors 'none'`, nosniff and referrer policy;
  - audits show no high/critical findings, and secret scanning fails a branch containing a fake credential;
  - containers are non-root;
  - workflows have read-only permissions, SHA-pinned actions and no `pull_request_target`.

**Verify:** B-04, B-05, B-06, F-08 tests; CI `security` jobs; fake-secret drill; workflow review.
**Evidence:** reports, header transcripts, drill link. **Tasks:** B-04, B-05, B-06, B-24, F-08, F-11.

### AC-13 — Quality gates and coverage

*NFR-03, NFR-04*

- **Given** backend and frontend CI,
- **When** a drill PR lowers coverage (backend < 85%, frontend `src/lib` + status < 80%) or adds a Ruff/mypy/tsc/ESLint error,
- **Then** the relevant job fails. On the release SHAs the thresholds are met.

**Verify:** coverage reports; one failing drill per repo.
**Evidence:** coverage summaries, drill links. **Tasks:** B-02, B-28, B-23, F-01, F-11.

### AC-14 — Bright design foundation and accessibility

*FR-08, FR-54, FR-55 · spec §7 · UX §1.2, §2.1–2.2, §12 · DEC-011, DEC-065 (values proposed)*

- **Given** `design/tokens.json` and the production frontend build,
- **When** the token checker, unit tests and E2E run,
- **Then**:
  - every declared pair meets its WCAG ratio;
  - the generated CSS equals the pinned tokens;
  - pages use `color-scheme: light`;
  - every interactive element shows the 2 px focus ring;
  - `/` has exactly one interactive element (a working link) and a skip link;
  - status uses icon + text;
  - under reduced-motion emulation, computed transition and animation durations are ≤ 0.01 ms;
  - axe reports 0 serious/critical issues on `/` and `/status`;
  - a keyboard-only user reaches and operates every control.
- **And** no product UI, navigation, icons or component library is present.

**Verify:** S-08; F-04, F-06 tests; F-10 E2E (keyboard, reduced motion, axe).
**Evidence:** checker output, Playwright report. **Tasks:** S-05, S-08, F-04, F-06, F-10.

### AC-15 — Status page tells the truth in every state

*FR-56*

- **Given** `/status`,
- **When** the backend is (a) healthy, (b) ready = 503, (c) unreachable, (d) diagnostics disabled, (e) returning an error, and (f) the user presses Retry after recovery,
- **Then** the page shows, respectively:
  - (a) green checks and provenance;
  - (b) degraded, naming the failed dependency with its correlation ID;
  - (c) unreachable, with no fabricated values;
  - (d) health shown plus "Diagnostics disabled";
  - (e) an error with its correlation ID;
  - (f) a refetch that returns to healthy.
- Changes are announced through the live region. It never shows "ok" when the backend says otherwise.

**Verify:** F-07 component tests (all states); F-10 E2E covers (a), (c) and (d) against the real backend.
**Evidence:** test report plus Playwright traces. **Tasks:** F-07, F-10.

### AC-16 — Chromium E2E against a persisted backend

*Tech §17.8 #6 · FR-59 · DEC-012 · UX-NFR-011 (Chromium; second engine pending DEC-055)*

- **Given** the frontend `e2e` CI job,
- **When** it starts isolated `postgres:15` and `redis:7.4` services, bootstraps roles, migrates, runs the backend at `e2e/backend.ref` (API + worker) and the production frontend build,
- **Then** the status, keyboard, reduced-motion, accessibility and parity suites pass in Chromium with no route interception or mocks.

**Verify:** CI `e2e` job (F-12); `grep -r "page.route(" e2e/` returns nothing.
**Evidence:** run link plus HTML report artifact. **Tasks:** F-10, F-12.

### AC-17 — Scope guard, exclusions and sign-off

*spec §2 · DEC-002 · DEC-046*

- **Given** the release SHAs,
- **When** reviewers inspect the diff since ATLAS-001 started,
- **Then** there are:
  - no domain, job or outbox tables (only `0001_baseline`);
  - no auth code beyond the diagnostics guard;
  - no UI beyond `/` and `/status`;
  - no screenshot baselines or WebKit project enabled;
  - no telemetry SDKs, tracing, PR-analysis, provisioning or AI functionality;
  - no change to `brd/`, `ux/` or `technical/`;
  - no shared-service change outside approved Atlas objects.
- `evidence.md` lists every AC with evidence and is signed by the owner.

**Verify:** reviewer checklist; `grep -riE "opentelemetry|applicationinsights|langchain|openai" atlas-backend atlas-frontend` returns nothing; `alembic history` shows only `0001_baseline`; `git log --stat -- brd ux technical` shows no ATLAS-001 commits.
**Evidence:** signed checklist in `evidence.md`. **Tasks:** B-26, F-14, S-13.

---

## Sign-off

ATLAS-001 is **Accepted** only when every AC above has evidence recorded in `evidence.md` and the owner signs it (G7). Tags: `atlas-specs` `contract-v0.1.0`, `atlas-backend` `v0.1.0`, `atlas-frontend` `v0.1.0`.
