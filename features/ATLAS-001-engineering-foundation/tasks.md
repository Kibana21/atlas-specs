# ATLAS-001 — Engineering Foundation: Tasks

**Version:** 0.2.1 (final candidate) · **Date:** 24 October 2026 · **Status:** Approved for Implementation (owner, 24 Oct 2026); CP1 authorized; ATLAS-001 not Accepted until G7 · **Spec:** `spec.md` v0.2.1 · **Acceptance:** `acceptance.md` v0.2.1 · **Readiness:** `readiness.md`

## Rules

1. **One repository per task.** The checkpoint header names the repository and every task in it changes only that repository. Cross-repo dependencies flow only through a merged and tagged `atlas-specs` SHA, or a recorded backend SHA.
2. **Independently verifiable.** Each task ships its own tests (where it has code) and names **one** verification command or observable check that a reviewer re-runs. Nothing is verified "later by another task".
3. **Size:** about 1–4 hours, one reviewable change. PR title starts with the task ID.
4. **Definition of done** (every task):
   - its verification passes locally and in CI (once CI exists for that repo);
   - static checks and coverage thresholds hold;
   - no new warnings;
   - README/docs updated if a command or variable changed;
   - nothing outside the task's repository is modified;
   - no shared-service state is changed (spec NFR-06).
5. **Never in ATLAS-001:** domain or job tables, auth code, outbox, UI beyond `/` and `/status`, screenshot baselines, WebKit, product exclusions (spec §2).

**Totals:** 53 implementation tasks in 7 checkpoints (specs 13 · backend 26 · frontend 14), plus 9 owner preconditions (P-01…P-09). v0.1 had 108; the reduction is explained in `changes-v0.2.md` §4. v0.2.1 changes task content, not task count.

---

## P — Owner preconditions (not implementation tasks)

| ID | Precondition | Needed before | How it is evidenced |
|---|---|---|---|
| P-01 | Owner approves `spec.md`, `plan.md`, `tasks.md`, `acceptance.md` — **done: v0.2.1 Approved for Implementation, 24 Oct 2026** | Any task | Approval recorded in spec §13 |
| P-02 | Owner approves or overrides D-07 (DEC-020, 024, 028, 038, 039, 040) — **done: approved, register v0.3** | Any task | Register rows updated by owner instruction |
| P-03 | Owner reviews and applies (or explicitly authorizes applying) `proposals/postgres-local-setup.sql` (4 roles). **Design approved 24 Oct 2026; execution not authorized yet.** `proposals/pg_hba-atlas.conf` approved in principle (DEC-084); before CP3: re-verify rule precedence and rollback, effective `CONNECT`/`PUBLIC` grants, and that other projects are unaffected; then request explicit authorization | CP3 | `make doctor` (B-08) reports roles and databases present |
| P-04 | Node.js 24 LTS available locally (owner installs or authorizes the method) | CP6 | `node --version` reports v24.x |
| P-05 | **Confirmed 24 Oct 2026.** Owner permits pulling three **digest-pinned** container images for local runs: `tufin/oasdiff`, `redocly/cli`, `davidanson/markdownlint-cli2`. No host install. (`tufin/oasdiff:latest` is already present from the review-01 probe and will be replaced by the pinned digest) | **CP1** (S-07, S-10); B-19 local | Digests recorded in `tools/images.lock` |
| P-06 | **Decided 24 Oct 2026: repositories remain PUBLIC (DEC-085).** CI uses Mode A (no App, no PATs, no secrets). Public-repository safety rules apply (spec §6.8) | Every push | Staged-diff review recorded in `evidence.md` |
| P-07 | Owner applies the `main` ruleset with required checks (`ci-access.md` §6) | G7 sign-off | Ruleset visible in repo settings |
| P-08 | **Confirmed 24 Oct 2026.** Owner confirms the change workflow (never push to `main`, never merge own changes, never force-push shared branches, never print credentials): Claude creates feature branches locally and pushes them with the machine's **existing** git credential (HTTPS + osxkeychain; no new credential); the owner opens, reviews and merges PRs (no `gh` CLI installed) | **CP1** (first push) | Owner confirmation recorded in `evidence.md` |
| P-09 | Owner approves each **contract release** before its tag is created (DEC-039): for ATLAS-001, release `contract-v0.1.0` | S-12 | Approval recorded in `evidence.md` |

---

## CP1 — Specs: contract, tokens and tooling · repository **atlas-specs**

| ID | Task | Depends | Verify | AC |
|---|---|---|---|---|
| S-01 | `contracts/conventions.md` (headers, IDs, status codes, error-code catalog) and `contracts/style-guide.md` (operationId naming, components, nullable `anyOf` form, mandatory error responses) | P-01, P-02 | `npx markdownlint-cli2 contracts/*.md` exit 0. Reviewer checklist = spec §6.6 + FR-03 items all present | AC-08 |
| S-02 | `contracts/compatibility.md`: semver; breaking rules; deprecation; backend-first rollout; **pinning and release rules** (pin immutable `main` SHAs; `contract-v*` tags only for approved releases; release builds must pin a tagged release commit; pre-release `info.version` form `X.Y.Z-dev.N` between releases) | S-01 | markdownlint (pinned container) exit 0. Checklist = spec FR-04 + §6.4 rules | AC-02, AC-03 |
| S-03 | JSON Schemas `error.v1`, `health-live.v1`, `health-ready.v1`, `build-info.v1` + valid/invalid examples (amendment A1) | S-01 | `check-jsonschema` passes all `valid-*` and fails every `invalid-*` (scripted loop exits 0) | AC-08 |
| S-04 | `contracts/openapi/atlas-api.yaml` 0.1.0 with `getHealthLive`, `getHealthReady`, `getDiagnosticsBuild`, envelope and `X-Correlation-ID` on every response | S-03 | `npx @redocly/cli lint contracts/openapi/atlas-api.yaml` exit 0 | AC-03, AC-08 |
| S-05 | `design/tokens.json` (spec §7.1, each value tagged `proposed`) and `design/tokens.md` (AR-01…AR-10, motion rules) | P-01 | `python -m json.tool design/tokens.json` exit 0. Checklist = every §7.1 group + AR rule present | AC-14 |
| S-06 | `tools/` project (pinned deps, `uv run --project tools`) and `check_specs_lock.py` with tests (valid, branch name, short SHA, unknown SHA, version mismatch) | S-04 | `uv run --project tools pytest tools/tests/test_specs_lock.py` passes | AC-02 |
| S-07 | `tools/contract_conformance.py` (spec §6.7: inventory, normalizer, oasdiff `--fail-on-diff`, pinned image digest) with 7 fixture cases | S-06, P-05 | `uv run --project tools pytest tools/tests/test_conformance.py`. Cosmetic-only passes; missing op, unexpected op, operationId mismatch, added optional property, removed required property, changed status code each fail with their specific code | AC-03 |
| S-08 | `tools/check_tokens.py` validates every declared pair in `tokens.json` against its WCAG threshold, with tests | S-05, S-06 | `uv run --project tools python tools/check_tokens.py design/tokens.json` exit 0. Test with a failing pair exits non-zero | AC-14 |
| S-09 | `tools/check_registry.py` (unique requirement IDs; `BL-`/`DEC-` references resolve), with tests | S-06 | `uv run --project tools python tools/check_registry.py` exit 0 on repo. Duplicate-ID fixture fails | AC-01 |
| S-10 | Lint configs: `.markdownlint-cli2.yaml` **excluding `brd/`, `ux/`, `technical/`** (baselines never edited for lint) and `redocly.yaml`; `tools/images.lock` with the three pinned image digests; `Makefile` target `check` running S-03…S-09 with markdownlint, Redocly and oasdiff **via the pinned containers** | S-04, S-07, S-08, S-09, P-05 | `make check` exit 0 on a clean clone with only Docker and uv present (no Node). `git diff --stat brd ux technical` empty | AC-01 |
| S-11 | `.github/workflows/specs-ci.yml` (jobs `docs-lint`, `contract`, `tools`, `tokens`, `registry`, `breaking` vs the **latest `contract-v*` release tag**, skipping with notice if none), using the same pinned images; `permissions: {}` + per-job `contents: read`; actions pinned by SHA; `CODEOWNERS` (`* @Kibana21`) | S-10 | PR run shows all 6 jobs green | AC-01, AC-03 |
| S-12 | Tag `contract-v0.1.0` (first approved contract release) on the merged `main` commit; create `features/ATLAS-001-engineering-foundation/evidence.md` recording the SHA and the owner's release approval | S-11, P-09 | `git rev-parse contract-v0.1.0^{commit}` equals the SHA in `evidence.md` | AC-02 |

**Gate G1 (CP1 exit):** `make check` and specs CI green on the tagged SHA; conformance self-tests prove missing **and** unexpected operations are detected; token contrast check passes; baselines unchanged. ACs: AC-01 (specs), AC-03 (specs part), AC-14 (token values).

---

## CP2 — Backend skeleton and quality gates · repository **atlas-backend**

| ID | Task | Depends | Verify | AC |
|---|---|---|---|---|
| B-01 | uv project (`requires-python = "==3.12.*"`), `uv.lock`, `.python-version` (remove its `.gitignore` line), `src/atlas` layout per FR-20, one sanity unit test | P-01, P-02 | `uv sync --locked && uv run pytest -m unit` → 1 passed | AC-01 |
| B-02 | Ruff (lint+format, rules incl. `S`,`B`,`UP`,`I`), mypy `--strict` + Pydantic plugin, pytest markers, coverage `fail_under = 85`; `Makefile` `setup`, `check` | B-01 | `make check` exit 0 (ruff, format check, mypy, unit tests + coverage) | AC-13 |
| B-03 | `core/settings.py` with environment guards (FR-21), `.env.example`, `.env.test.example` (placeholders only) | B-02 | `uv run pytest tests/unit/test_settings.py`: guard matrix (test↔`atlas_test`/DB 11/prefix; local forbids test DB/index; DB ≠ 10/11 rejected; diagnostics refused in uat/prod) | AC-07, AC-11 |
| B-04 | `core/logging.py` (structlog JSON + redaction) and `core/correlation.py` middleware | B-03 | `uv run pytest tests/unit/test_logging.py tests/unit/test_correlation.py`: secrets redacted; valid ID echoed; invalid replaced; header always present | AC-10, AC-12 |
| B-05 | `core/errors.py`: `AtlasError` + handlers (Atlas, validation, HTTP, unhandled) → envelope | B-04 | `uv run pytest tests/unit/test_errors.py`: codes, statuses, `correlation_id` = header; 500 body contains no traceback/SQL/path text | AC-08, AC-12 |
| B-06 | `main.py` app factory with router conventions (explicit `operation_id`, router-level envelope responses, `X-Correlation-ID` header hook, schema identical across envs, docs only in `local`); `GET /health/live`; CORS + security headers; `make api` | B-05 | `uv run pytest tests/unit/test_app.py`: live 200 + headers; unlisted origin gets no ACAO; `app.openapi()` byte-identical under `local` and `test`; no `HTTPValidationError` component | AC-05, AC-12 |
| B-07 | `GET /diagnostics/build` (guarded, 404 when disabled) + `version.py` (backend SHA from `ATLAS_BUILD_SHA` → git → `"unknown"`; specs SHA/version from `specs.lock` when present; `db_migration_revision` `null` until B-12) | B-06 | `uv run pytest tests/unit/test_diagnostics.py`: enabled 200, disabled 404 envelope, each SHA fallback | AC-09 |
| B-08 | `make doctor`: read-only preflight (spec FR-35) with remediation messages, **including local-auth detection** (one deliberate wrong-password attempt; warns if trust). `make doctor SNAPSHOT=file` writes a read-only inventory (database names, role names, Redis key count per DB) for before/after diffs | B-03 | Run against the existing services. Before P-03 it reports server 15.x and "Atlas roles missing → proposals/…". After P-03 it reports the trust warning. A test asserts only `SELECT`/`PING`/`INFO`/`SCAN`/`DBSIZE` and the auth probe are issued | AC-04, AC-07 |

**Gate G2:** `make check` green with coverage ≥ 85%; live endpoint returns envelope-conformant errors and correlation headers; doctor runs read-only against shared services. ACs: AC-08/10/12/13 (backend unit level).

---

## CP3 — Backend persistence and migrations · repository **atlas-backend** · requires P-03

| ID | Task | Depends | Verify | AC |
|---|---|---|---|---|
| B-09 | `persistence/db.py` async engine (psycopg 3) on the **runtime** URL; `/health/ready` database check (1 s timeout) | B-07, P-03 | `uv run pytest -m integration tests/integration/test_ready_db.py` (`.env.test`): 200 with DB; 503 `DEPENDENCY_UNAVAILABLE` when URL points to a closed port (no host in body) | AC-05 |
| B-10 | Alembic on the **migration** URL (the migrator owns schema `atlas`), `version_table_schema="atlas"`, naming convention, `ATLAS_DB_APP_ROLE` available for per-table grants; reviewed empty `0001_baseline`; `make migrate`; README migration policy (expand/migrate/contract, reviewed, reversible, explicit per-table write grants) | B-09 | `make migrate` then `alembic current` → `0001_baseline (head)` on `atlas_db`; `alembic_version` owned by `atlas_migrator` | AC-06 |
| B-11 | Migration tests on `atlas_test` as `atlas_test_migrator`: `upgrade head → downgrade base → upgrade head`, `alembic check`, single head | B-10 | `uv run pytest -m integration tests/integration/test_migrations.py` passes | AC-06 |
| B-12 | Least-privilege tests (FR-30) and build info `db_migration_revision` read by the runtime role | B-11 | `uv run pytest -m "integration and security" tests/integration/test_privileges.py`: runtime `CREATE`/`TEMP`/ungranted write denied; cross-env `CONNECT` denied for both roles; no elevated role flags; `/diagnostics/build` reports `0001_baseline` | AC-07, AC-09 |

**Gate G3:** migrations round-trip as the test migrator; runtime role cannot run DDL; no Atlas test touched any non-Atlas database. ACs: AC-05 (DB), AC-06, AC-07, AC-09 (revision).

---

## CP4 — Backend Taskiq/Redis seam · repository **atlas-backend**

| ID | Task | Depends | Verify | AC |
|---|---|---|---|---|
| B-13 | Redis client factory (refuses DB index ≠ configured; applies prefix), `workers/broker.py` (`ListQueueBroker`, queue `<prefix>taskiq:queue`); `/health/ready` Redis check | B-09 | `uv run pytest -m integration tests/integration/test_ready_redis.py`: ready 200; 503 with closed port; factory rejects DB 1 | AC-05, AC-11 |
| B-14 | `diagnostics.ping(marker_id, correlation_id)` task (marker key under prefix, TTL ≤ 60 s, logs correlation ID); `make worker` | B-13 | `uv run pytest tests/unit/test_ping_task.py` (task body against a fake client: key name, TTL, log field) | AC-10, AC-11 |
| B-15 | Worker round-trip integration test: real worker subprocess, enqueue, observe marker, key-tracker cleanup of exact keys; session guard (no `atlas:test:<run_id>:*` keys left; non-run keys in DB 11 unchanged); read-only `scripts/redis_keys.py` (SCAN/DBSIZE only) for evidence | B-14 | `uv run pytest -m integration tests/integration/test_worker_roundtrip.py` passes **and** `uv run python scripts/redis_keys.py --db 11 --pattern 'atlas:test:*'` reports 0 keys afterwards | AC-11 |
| B-16 | Redis safety static check (FR-34): no forbidden command strings in `src/` or `tests/` | B-13 | `uv run pytest tests/unit/test_redis_safety.py` passes; a fixture file containing `FLUSHDB` makes it fail | AC-11 |
| B-17 | `make worker-smoke` on DB 10: enqueue ping, await marker, delete its own keys | B-14 | With `make worker` running: `make worker-smoke` prints OK; `uv run python scripts/redis_keys.py --db 10 --pattern 'atlas:local:ping:*'` reports 0; `--db 1 --dbsize` unchanged before/after | AC-04, AC-11 |

**Gate G4:** worker round trip proven; no keys remain outside expectations; no forbidden commands; other Redis DBs unchanged. ACs: AC-05 (Redis), AC-10 (worker), AC-11.

---

## CP5 — Backend contract conformance, CI and images · repository **atlas-backend**

| ID | Task | Depends | Verify | AC |
|---|---|---|---|---|
| B-18 | `specs.lock` → the immutable commit of release `contract-v0.1.0`; `make specs` extracts `contracts/` and `tools/` at the SHA via `git archive` into `build/specs/` and validates the lock | S-12, B-07 | `make specs` exit 0; `build/specs/tools/check_specs_lock.py` comes from the pinned SHA (checksum matches `git show <sha>:tools/check_specs_lock.py`) | AC-02 |
| B-19 | Transport models aligned to the contract; deterministic `scripts/export_openapi.py`; `make contract` runs the pinned conformance tool | B-18, B-12, B-13 | `make contract` exit 0. Two exports byte-identical | AC-03 |
| B-20 | Response contract tests: bodies of all 3 operations (incl. 404/503 envelopes) validate against JSON Schemas at the pinned SHA | B-18 | `uv run pytest -m contract` passes | AC-08 |
| B-21 | Multi-stage `Dockerfile` (`api`, `worker` targets, non-root, `ATLAS_BUILD_SHA`) | B-14 | `docker build --target api .` and `--target worker .` succeed; `docker run --rm <img> id -u` ≠ 0 | AC-05 |
| B-22 | `scripts/db/bootstrap.sql`: CI copy of the **approved** 4-role proposal (adds `CREATE DATABASE atlas_db` for empty CI servers); header cites the proposal SHA | P-03, B-12 | `diff` against the proposal shows only the documented CI difference; used successfully by B-23 | AC-07 |
| B-23 | `.github/workflows/backend-ci.yml` part 1: jobs `static`, `unit`, `integration`. Services `postgres:15` with `scram-sha-256` (FR-39) and `redis:7.4`. Random per-run role passwords (masked) passed to the B-22 bootstrap; `ci_auth` test enabled (`ATLAS_EXPECT_PASSWORD_AUTH=true`) | B-02, B-22, B-15 | PR run: 3 jobs green; integration log shows migration round trip, worker round trip, and `ci_auth` (wrong/missing password rejected) passing | AC-01, AC-07, AC-13 |
| B-24 | Workflow part 2: jobs `contract` (checkout `atlas-specs` at lock SHA, Mode A, with optional Mode B branch per `ci-access.md`), `security` (pip-audit, secret scan), `images` (build both targets); `CODEOWNERS` | B-23, B-19, B-21 | PR run: all 6 jobs green; `permissions` read-only; no secrets referenced unless `vars.ATLAS_CI_APP_ID` is set | AC-01, AC-03, AC-12 |
| B-25 | README "Local development": prerequisites (existing PostgreSQL 15 + Redis, P-03 SQL, uv), env files, every `make` target, smoke journey, shared-service safety rules | B-17, B-19 | A second engineer follows the README on a clean clone up to `make worker-smoke` OK (evidence log) | AC-04 |

**Gate G5:** backend CI fully green; conformance proven (incl. the AC-03 drills); images build; README reproducible. ACs: AC-01, AC-02 (backend), AC-03, AC-05, AC-12, AC-13.

---

## CP6 — Frontend foundation · repository **atlas-frontend** · requires G1 and P-04 (can run in parallel with CP2–CP5)

| ID | Task | Depends | Verify | AC |
|---|---|---|---|---|
| F-01 | Next.js App Router scaffold (no demo content), pnpm lockfile, Node 24 pins (`.nvmrc`, `engines`, `engine-strict`), TS strict, ESLint flat `--max-warnings 0`, Vitest with one sanity test, folder skeleton (FR-50) | P-01, P-02, P-04 | `pnpm install --frozen-lockfile && pnpm check` exit 0 (tsc, eslint, vitest) | AC-01, AC-13 |
| F-02 | `src/lib/env.ts` with tests | F-01 | `pnpm vitest run src/lib/env.test.ts`. `NEXT_PUBLIC_ATLAS_API_BASE_URL=notaurl pnpm build` fails with a clear message | AC-04 |
| F-03 | `specs.lock` → the same immutable `contract-v0.1.0` commit as the backend; `pnpm specs` (extract at SHA); `pnpm gen:api` → `src/generated/api/schema.d.ts`; `pnpm check:generated` | F-01, S-12 | `pnpm gen:api && pnpm check:generated` exit 0 (second run no diff); generated header present | AC-02, AC-03 |
| F-04 | `pnpm gen:tokens` → `src/styles/tokens.generated.css` + Tailwind theme mapping; global base styles (`color-scheme: light`, focus ring, reduced-motion block, typography); tests asserting the generated CSS contains every token and the reduced-motion rule | F-03 | `pnpm gen:tokens && pnpm check:generated && pnpm vitest run src/styles` pass | AC-14 |
| F-05 | `src/lib/api/transport.ts` + `errors.ts` (envelope / non-JSON / network → `AtlasApiError`, correlation header) with tests | F-03, F-02 | `pnpm vitest run src/lib/api` passes (header attached, base URL, 3 error mappings, coverage ≥ 80%) | AC-08, AC-10 |
| F-06 | Root layout (lang, skip link, landmarks) and `/` placeholder (one link) with component tests | F-04 | `pnpm vitest run src/app/page.test.tsx`: exactly one interactive element; skip link targets `main`; single `h1` | AC-14 |
| F-07 | `/status` with TanStack Query: states loading / ready / degraded / unreachable / diagnostics-disabled / error; `aria-live`; icon + text; retry | F-05, F-06 | `pnpm vitest run src/app/status` covers all 6 states. Manual run against local backend matches `curl` values | AC-09, AC-15 |
| F-08 | Production security headers + CSP in `next.config.ts` | F-06 | `pnpm build && pnpm start` then `curl -sI localhost:3000/`: CSP without `unsafe-eval`, `frame-ancestors 'none'`, nosniff, referrer policy (scripted assertion) | AC-12 |
| F-09 | `Dockerfile` (standalone, non-root) | F-08 | `docker build .` succeeds; `docker run --rm <img> id -u` ≠ 0 | AC-05 |

**Gate G6:** `pnpm check` green; generated client and tokens reproducible; status page shows true state in all 6 states; CSP present. ACs: AC-08/10 (frontend), AC-12 (CSP), AC-14, AC-15.

---

## CP7 — Frontend CI, Chromium E2E and release · tasks each in **one** repository as marked

| ID | Repo | Task | Depends | Verify | AC |
|---|---|---|---|---|---|
| F-10 | frontend | Playwright (**Chromium only**; projects array ready for WebKit), against `next start` + real backend: status journey, keyboard-only, reduced-motion emulation, axe on `/` and `/status`, lock parity | F-07, F-08, G5 | `pnpm e2e` green locally against `make api`/`make worker` | AC-02, AC-14, AC-16 |
| F-11 | frontend | `.github/workflows/frontend-ci.yml`: `static`, `unit`, `generated` (checkout specs at lock SHA), `build`, `security` (pnpm audit, secret scan), `image`; Node from `.nvmrc`; `CODEOWNERS` | F-09, F-04 | PR run: 6 jobs green; read-only permissions | AC-01, AC-03, AC-12, AC-13 |
| F-12 | frontend | `e2e/backend.ref` (backend SHA from G5) and CI job `e2e`: checkout backend at ref, `postgres:15` + `redis:7.4` services, backend `scripts/db/bootstrap.sql`, migrate, start API + worker, Playwright Chromium, upload report | F-11, F-10 | PR run: `e2e` green; report artifact present; no `page.route(` in acceptance specs | AC-16 |
| F-13 | frontend | README "Local development" (Node 24, pnpm, env, `gen`, `e2e` against local backend) | F-10 | Second engineer reproduces `pnpm dev` + `/status` green from README (evidence log) | AC-04 |
| B-26 | backend | Tag `v0.1.0` at the SHA recorded in `e2e/backend.ref` once G7 evidence is complete; its `specs.lock` must point at a commit carrying a `contract-v*` release tag | F-12 | `git rev-parse v0.1.0` equals that SHA; `git -C ../atlas-specs tag --points-at <lock sha>` lists `contract-v0.1.0` | AC-02, AC-17 |
| F-14 | frontend | Tag `v0.1.0` at the SHA that passed F-12; its `specs.lock` must point at a `contract-v*` release commit | F-12 | `git rev-parse v0.1.0` equals the CI-green SHA; lock SHA carries `contract-v0.1.0` | AC-02, AC-17 |
| S-13 | specs | Complete `evidence.md`: every AC with evidence links, the SHA triple (specs/backend/frontend), the open-decision snapshot | B-26, F-14, P-07 | Every AC row in `acceptance.md` has a linked evidence entry. The owner signs | AC-17 |

**Gate G7 (ATLAS-001 sign-off):** all ACs evidenced; the owner signs `evidence.md`; register updated by owner instruction. ATLAS-001 becomes **Accepted** only when the owner signs.

---

## Dependency overview

```text
P-01,P-02 ─┬─ CP1 (specs) ── G1 ──┬───────────────────────────── CP6 (frontend, needs P-04) ── G6 ─┐
           │                      │                                                                 │
           └─ CP2 (backend) ─ G2 ─┴─ CP3 (needs P-03) ─ G3 ─ CP4 ─ G4 ─ CP5 (needs G1) ─ G5 ────────┴─ CP7 ─ G7
```
