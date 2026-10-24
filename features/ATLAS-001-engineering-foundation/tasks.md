# ATLAS-001 — Engineering Foundation: Tasks

**Status:** Draft — awaiting approval · **Date:** 24 October 2026 · **Spec:** `spec.md` · **Plan:** `plan.md` · **Acceptance:** `acceptance.md`

## Rules

- **Size:** each task is one reviewable change (≈ 1–4 h) in **one repository**.
- **Verify:** each task names a single command or observable check, which a reviewer re-runs to accept it. "CI green" alone never counts. The task's own check must be named.
- **Order:** follow `Depends`. Tasks in different repositories connect only through a merged, pinned `atlas-specs` SHA.
- **IDs:** `A001-T-<milestone>-<nn>` (e.g. `A001-T-B3-02`). PR titles start with the task ID.
- **Gate:** no task except M0 starts before the spec §11 approval gate is signed.
- **Never in ATLAS-001:** domain tables, auth code, product UI beyond `/` and `/status` (spec §3).

Legend: **Repo** `S` atlas-specs, `B` atlas-backend, `F` atlas-frontend. **AC** = acceptance criterion advanced (see `acceptance.md`).

---

## M0 — Approval gate (no code)

| ID | Task | Repo | Depends | Verify | AC |
|---|---|---|---|---|---|
| A001-T-M0-01 | Record approval of spec, plan, tasks, acceptance (approver, date) in spec §12 | S | – | Revision row present with approver name | – |
| A001-T-M0-02 | Update decision register: DEC-020/021/024/028/038/039/040 (and 037/042) to Confirmed for ATLAS-001 scope, or record overrides | S | M0-01 | Register rows show new status + date + approver | – |
| A001-T-M0-03 | Record FD-01…FD-12 outcomes as register rows (`DEC-043…`) | S | M0-01 | Each FD has a DEC row with status | – |
| A001-T-M0-04 | Write `adr/ADR-0006-three-repository-contract-governance.md` (repos, `specs.lock`, conformance, rollout rule) | S | M0-02 | ADR file exists with Status: Accepted and links to DEC-001/039 | AC-02 |
| A001-T-M0-05 | Create read-only CI credentials per FD-07 and store as repo secrets `ATLAS_SPECS_READ_TOKEN` (backend, frontend), `ATLAS_BACKEND_READ_TOKEN` (frontend) | B, F | M0-03 | Secrets visible (names only) in repo settings; owner confirms scope is read-only | AC-02 |
| A001-T-M0-06 | Add `CODEOWNERS` and branch protection (required reviews, required status checks) in all three repos | S, B, F | M0-01 | `CODEOWNERS` merged; protection rule visible | – |

## S1 — Specs: conventions and contract 0.1.0

| ID | Task | Repo | Depends | Verify | AC |
|---|---|---|---|---|---|
| A001-T-S1-01 | Write `contracts/conventions.md` (base path, IDs, pagination, headers, status codes, error catalog from spec §6.4) | S | M0-02 | Reviewer checklist: every spec §6.3–6.4 item present | AC-07 |
| A001-T-S1-02 | Write `contracts/compatibility.md` (semver, breaking definitions, deprecation, rollout order) | S | M0-02 | Reviewer checklist against spec FR-04 | AC-02 |
| A001-T-S1-03 | Add `contracts/schemas/error.v1.json` + `examples/error/valid-*.json`, `invalid-*.json` | S | S1-01 | `check-jsonschema --schemafile contracts/schemas/error.v1.json contracts/examples/error/valid-*.json` passes; invalid files fail | AC-07 |
| A001-T-S1-04 | Add `build-info.v1.json` + examples | S | S1-01 | Same as S1-03 for build-info | AC-08 |
| A001-T-S1-05 | Add `job.v1.json` + examples (status enum per spec §6.2) | S | S1-01 | Same as S1-03 for job | AC-11 |
| A001-T-S1-06 | Author `contracts/openapi/atlas-api.yaml` 0.1.0: `info`, servers, shared components (error envelope, headers `X-Correlation-ID`, `Idempotency-Key`), `health/live`, `health/ready` | S | S1-03 | `npx @redocly/cli lint contracts/openapi/atlas-api.yaml` passes | AC-07 |
| A001-T-S1-07 | Add `diagnostics/build`, `diagnostics/jobs/ping`, `jobs/{job_id}` operations referencing the schemas | S | S1-04, S1-05, S1-06 | Redocly lint passes; every operation has 2xx + error responses with envelope | AC-08, AC-11 |
| A001-T-S1-08 | Update `contracts/` folder `.gitkeep`s → remove where now non-empty; add `contracts/README.md` index | S | S1-07 | `ls contracts/*` shows no orphan `.gitkeep` in non-empty folders | – |

## S2 — Specs: tools and CI

| ID | Task | Repo | Depends | Verify | AC |
|---|---|---|---|---|---|
| A001-T-S2-01 | Add pinned tooling manifest for `tools/` (Python, run via `uvx`/`uv run`) and `README` section "specs tooling is not product code" | S | M0-03 | `uv run --project tools python -c "import yaml, jsonschema"` succeeds | – |
| A001-T-S2-02 | `tools/check_specs_lock.py <lockfile> [--specs-dir]`: validates schema of lock, 40-hex SHA, SHA reachable, `contract_version == info.version` at SHA | S | S2-01, S1-07 | Unit-style self-test: valid sample lock passes; branch name / short SHA / version mismatch each fail with distinct exit message | AC-02 |
| A001-T-S2-03 | `tools/check_registry.py`: unique requirement IDs in `phase0/requirements-registry.csv`; every `BL-`/`DEC-` reference exists in backlog/register | S | S2-01 | Runs green on current repo; injecting a duplicate ID in a temp copy fails | AC-01 |
| A001-T-S2-04 | Add `.markdownlint-cli2.yaml` tuned for existing baselines (long tables allowed) and fix or explicitly exempt current violations without changing requirement text | S | – | `npx markdownlint-cli2 "**/*.md"` exits 0 | AC-01 |
| A001-T-S2-05 | Add `redocly.yaml` ruleset (recommended + require operationId, error responses, no inline schemas for shared types) | S | S1-07 | `npx @redocly/cli lint` exits 0 using config | AC-07 |
| A001-T-S2-06 | `Makefile` target `check` running S2-02…S2-05 + schema example validation locally | S | S2-02…05 | `make check` exits 0 on clean clone | AC-01 |
| A001-T-S2-07 | `.github/workflows/specs-ci.yml` with jobs docs-lint, contract-lint, schema-examples, registry-check | S | S2-06 | Workflow run on PR shows all four jobs green | AC-01 |
| A001-T-S2-08 | Add `breaking-change` job: oasdiff `breaking` vs latest `contract-v*` tag (skip with notice when no tag exists) | S | S2-07 | Test PR that removes a response field fails the job; revert passes | AC-03 |
| A001-T-S2-09 | Tag `contract-v0.1.0` on merged `main`; record SHA in the ATLAS-001 spec revision table | S | S2-08 | `git tag -l contract-v0.1.0` shows tag; SHA recorded | AC-02 |

## B1 — Backend: tooling

| ID | Task | Repo | Depends | Verify | AC |
|---|---|---|---|---|---|
| A001-T-B1-01 | Remove `.python-version` from `.gitignore` (FD-12); add `.python-version` and `pyproject.toml` (`requires-python`, project metadata, src layout) via `uv init --package` equivalent; commit `uv.lock` | B | M0-02 | `uv sync --locked` succeeds on clean clone | AC-01 |
| A001-T-B1-02 | Create package skeleton per spec FR-11 (`api/routers`, `api/dependencies`, `api/schemas`, `core`, `domain`, `modules/<10>`, `connectors`, `workers`, `persistence`) with `__init__.py` only | B | B1-01 | `uv run python -c "import atlas.modules.catalog, atlas.workers"` succeeds | AC-01 |
| A001-T-B1-03 | Configure Ruff (lint rules incl. `S`,`B`,`UP`,`I`; format) in `pyproject.toml` | B | B1-01 | `uv run ruff check . && uv run ruff format --check .` exit 0 | AC-01 |
| A001-T-B1-04 | Configure mypy `--strict` + Pydantic plugin (FD-01) | B | B1-01 | `uv run mypy src` exits 0 | AC-01 |
| A001-T-B1-05 | Configure pytest (+ pytest-asyncio, pytest-cov, Hypothesis), markers `unit`/`integration`/`contract`/`security`, coverage config with `fail_under = 85` (enforced from B6) | B | B1-01 | `uv run pytest -m unit` runs (0 tests OK, exit 0 or 5 handled by config) | AC-13 |
| A001-T-B1-06 | `compose.yaml` with `postgres:16` and `redis:7`, named volumes, healthchecks, env from `.env` | B | – | `docker compose up -d --wait` → both services `healthy` | AC-04 |
| A001-T-B1-07 | `.env.example` with every `ATLAS_*` variable (placeholders only) and `Makefile` targets `setup`, `up`, `down`, `check` | B | B1-03…06 | `make setup && make up && make check` exit 0 on clean clone | AC-04 |

## B2 — Backend: API shell

| ID | Task | Repo | Depends | Verify | AC |
|---|---|---|---|---|---|
| A001-T-B2-01 | `core/settings.py` (pydantic-settings, `ATLAS_` prefix, env enum, URLs, CORS list, diagnostics flag, job tuning); startup refusal rule for diagnostics in uat/prod | B | B1-07 | Unit tests: missing required var fails; `ATLAS_ENV=prod` + diagnostics true raises | AC-08 |
| A001-T-B2-02 | `core/logging.py` structlog JSON (FD-04) + redaction processor | B | B2-01 | Unit test: log call with `password=`/`token=`/DSN emits `[REDACTED]`; output is valid JSON | AC-10 |
| A001-T-B2-03 | `core/correlation.py` middleware: accept valid inbound `X-Correlation-ID`, else generate; set response header; bind to log context | B | B2-02 | Unit tests: valid echoed; invalid (`<script>`, 200 chars) replaced; header always present | AC-09 |
| A001-T-B2-04 | `core/errors.py`: `AtlasError` hierarchy + handlers for AtlasError, validation, HTTP, unhandled → envelope | B | B2-03 | Unit tests per handler: status, `code`, `correlation_id` match; unhandled body has no traceback text | AC-07, AC-10 |
| A001-T-B2-05 | `main.py` app factory `create_app(settings)`; mount `/api/v1`; docs/openapi only in local/dev | B | B2-04 | `uv run python -c "from atlas.main import create_app"`; test: `/docs` 404 when `ATLAS_ENV=test` | AC-07 |
| A001-T-B2-06 | `api/routers/health.py` `live` endpoint + schema | B | B2-05 | `curl -s localhost:8000/api/v1/health/live` → `{"status":"ok"}` with `X-Correlation-ID` | AC-05 |
| A001-T-B2-07 | `version.py` build info: `backend_sha` from `ATLAS_BUILD_SHA` (else `git rev-parse` locally, else `"unknown"`), `specs_sha`/`contract_version` read from `specs.lock` | B | B2-01 | Unit tests for each source fallback | AC-08 |
| A001-T-B2-08 | `api/routers/diagnostics.py` `GET /diagnostics/build` guarded by settings (404 when disabled); `db_migration_revision` stubbed `null` until B3-06 | B | B2-07 | Tests: enabled → 200 schema-valid; disabled → 404 envelope | AC-08 |
| A001-T-B2-09 | CORS (allowlist from settings) + security headers middleware | B | B2-05 | Tests: allowed origin gets ACAO; unlisted origin gets none; `nosniff`, `no-referrer`, `no-store` present | AC-10 |
| A001-T-B2-10 | `make api` target (uvicorn reload, :8000) | B | B2-06 | `make api` then `curl …/health/live` → 200 | AC-04 |

## B3 — Backend: PostgreSQL and Alembic

| ID | Task | Repo | Depends | Verify | AC |
|---|---|---|---|---|---|
| A001-T-B3-01 | `persistence/db.py`: async engine (SQLAlchemy 2 + psycopg 3, FD-03), session factory, dispose on shutdown | B | B2-05 | Integration test: session executes `SELECT 1` against compose PostgreSQL | AC-05 |
| A001-T-B3-02 | `persistence/base.py`: `DeclarativeBase` with naming convention; `core/ids.py` ID factory (UUIDv7 per DEC-037 outcome) | B | B3-01 | Unit: 1,000 IDs unique and (v7) time-ordered; naming convention keys present | AC-06 |
| A001-T-B3-03 | Initialize Alembic (`alembic.ini`, `env.py` using settings URL + `Base.metadata`, sync psycopg URL) | B | B3-02 | `uv run alembic current` connects (no revision) | AC-06 |
| A001-T-B3-04 | Models for `job`, `job_attempt`, `outbox_event` (spec §6.6) | B | B3-02 | `uv run mypy src` passes; models import | AC-06 |
| A001-T-B3-05 | Migration `0001_infrastructure` (hand-reviewed, reversible) | B | B3-03, B3-04 | `make migrate` → `alembic current` = `0001`; `\d job` shows unique + check constraints | AC-06 |
| A001-T-B3-06 | Wire `db_migration_revision` into build info (read `alembic_version`) | B | B3-05, B2-08 | `GET /diagnostics/build` returns `"0001…"` after migrate | AC-08 |
| A001-T-B3-07 | Readiness: `GET /health/ready` checks DB (`SELECT 1`, timeout) — Redis check added in B4-02 | B | B3-01 | Test: DB up → 200; DB URL pointed at closed port → 503 `DEPENDENCY_UNAVAILABLE` | AC-05 |
| A001-T-B3-08 | Migration tests: upgrade head → downgrade base → upgrade head on fresh DB; `alembic check` no drift; single head | B | B3-05 | `uv run pytest tests/integration/test_migrations.py` passes | AC-06 |
| A001-T-B3-09 | Document migration policy (expand/migrate/contract, review, downgrade required) in backend README | B | B3-08 | README section present; reviewer checklist | AC-06 |

## B4 — Backend: Redis, Taskiq, jobs, outbox

| ID | Task | Repo | Depends | Verify | AC |
|---|---|---|---|---|---|
| A001-T-B4-01 | `workers/broker.py`: Taskiq broker on Redis from settings; result backend not required (state in PostgreSQL) | B | B1-07 | Integration: kiq a trivial task and receive it in an in-process worker | AC-11 |
| A001-T-B4-02 | Add Redis `PING` to readiness | B | B4-01, B3-07 | Test: `docker compose stop redis` → `/health/ready` 503; start → 200 | AC-05 |
| A001-T-B4-03 | `persistence/repositories/jobs.py`: create-idempotent, get, transition status, record attempt | B | B3-05 | Integration: duplicate `(type,key)` returns same id; illegal transition rejected | AC-11 |
| A001-T-B4-04 | `persistence/outbox.py`: `enqueue(session, topic, payload)` used inside the job-create transaction | B | B4-03 | Integration: exception after insert → neither job nor outbox row persists | AC-12 |
| A001-T-B4-05 | `workers/relay.py`: poll undispatched (`FOR UPDATE SKIP LOCKED`), dispatch to Taskiq, mark dispatched; bounded batch + interval | B | B4-01, B4-04 | Integration: 3 events → dispatched_at set; two relays concurrently never dispatch same event twice | AC-12 |
| A001-T-B4-06 | `workers/tasks.py` `diagnostics.ping` task: running → succeeded; idempotent on redelivery; optional `fail_times` payload for tests | B | B4-03 | Integration: job reaches `succeeded`, 1 attempt row; redelivery leaves 1 succeeded state | AC-11 |
| A001-T-B4-07 | `workers/retry.py`: exponential backoff + full jitter, max attempts; exhausted → `failed` with sanitized `last_error` | B | B4-06 | Unit (Hypothesis): delay ∈ [0, cap]; Integration: `fail_times=2` → succeeded after 3 attempts; `fail_times=99` → failed at max | AC-11 |
| A001-T-B4-08 | Endpoints `POST /diagnostics/jobs/ping` (requires `Idempotency-Key`) and `GET /jobs/{id}`, guarded by diagnostics flag | B | B4-06, B2-08 | Tests: 202 then 200 on same key; missing key → 422 `IDEMPOTENCY_KEY_REQUIRED`; disabled → 404 | AC-11 |
| A001-T-B4-09 | Correlation ID propagation API → job row → worker logs | B | B4-08, B2-03 | Integration: job.correlation_id equals request header; worker log line contains it | AC-09 |
| A001-T-B4-10 | Redis-loss resilience test: create job, `FLUSHALL` before dispatch, relay re-dispatches, job succeeds; job rows intact | B | B4-05, B4-06 | `uv run pytest -k redis_loss` passes | AC-12 |
| A001-T-B4-11 | `make worker` (Taskiq worker + relay as two processes) | B | B4-05 | Manual: `make worker`, POST ping, GET job → `succeeded` within 5 s | AC-04 |

## B5 — Backend: contract conformance

| ID | Task | Repo | Depends | Verify | AC |
|---|---|---|---|---|---|
| A001-T-B5-01 | Add `specs.lock` pinned to `contract-v0.1.0` SHA | B | S2-09 | `python ../atlas-specs/tools/check_specs_lock.py specs.lock` exits 0 | AC-02 |
| A001-T-B5-02 | Pydantic transport models in `api/schemas` aligned to contract components (names, required fields, enums) | B | B5-01, B4-08 | `uv run mypy src` passes; endpoints return these models | AC-07 |
| A001-T-B5-03 | `scripts/export_openapi.py` writes FastAPI OpenAPI (3.1) to `build/openapi.json` deterministically | B | B5-02 | Two runs produce byte-identical files | AC-03 |
| A001-T-B5-04 | `scripts/check_contract.sh`: extract pinned contract via `git show <sha>:<path>`; run oasdiff diff both directions ignoring descriptions/examples; fail on any difference; `make contract` | B | B5-03 | `make contract` exits 0; deliberately renaming a response field makes it fail | AC-03 |
| A001-T-B5-05 | Schema-level contract tests: responses of each endpoint validate against `contracts/schemas/*.json` at the pinned SHA | B | B5-01 | `uv run pytest -m contract` passes | AC-07 |

## B6 — Backend: CI and images

| ID | Task | Repo | Depends | Verify | AC |
|---|---|---|---|---|---|
| A001-T-B6-01 | `.github/workflows/backend-ci.yml`: lock-and-sync, static, unit jobs with uv cache | B | B1-05 | PR run shows jobs green; a lint error in a test PR fails `static` | AC-01 |
| A001-T-B6-02 | Add `integration` job with postgres:16 + redis:7 services (migrations + B4 tests) | B | B6-01, B4-10 | PR run green; job log shows migration round-trip test executed | AC-06, AC-12 |
| A001-T-B6-03 | Add `contract` job: checkout atlas-specs at lock SHA with `ATLAS_SPECS_READ_TOKEN`; run `make contract` + contract tests | B | B6-01, B5-04, M0-05 | PR run green; job fails when lock SHA is unknown | AC-02, AC-03 |
| A001-T-B6-04 | Add `security` job: pip-audit (fail high/critical), secret scan (e.g. gitleaks), Ruff `S` already in static | B | B6-01 | PR run green; committing a fake AWS-style key in a test branch fails | AC-10 |
| A001-T-B6-05 | Enforce coverage `fail_under = 85` across unit + integration | B | B6-02 | CI coverage report ≥ 85%; lowering tests below fails | AC-13 |
| A001-T-B6-06 | Multi-stage `Dockerfile` with `api` and `worker` targets, non-root user, `ATLAS_BUILD_SHA` build arg | B | B4-11 | `docker build --target api .` and `--target worker .` succeed; `docker run --rm <img> id -u` ≠ 0 | AC-05 |
| A001-T-B6-07 | Add `images` CI job building both targets (no push) | B | B6-06 | PR run green | AC-05 |
| A001-T-B6-08 | Security tests: 500 body has no traceback/SQL/hostnames; diagnostics refused in prod; startup fails on unsafe config | B | B2-04, B2-01 | `uv run pytest -m security` passes | AC-10 |

## F1 — Frontend: tooling

| ID | Task | Repo | Depends | Verify | AC |
|---|---|---|---|---|---|
| A001-T-F1-01 | Scaffold Next.js App Router + TypeScript (no example content), pnpm, commit `pnpm-lock.yaml`; `.nvmrc`, `engines`, `packageManager` | F | M0-02 | `pnpm install --frozen-lockfile && pnpm build` succeed | AC-01 |
| A001-T-F1-02 | `tsconfig.json` strict (+ `noUncheckedIndexedAccess`), path alias `@/*` | F | F1-01 | `pnpm tsc --noEmit` exits 0 | AC-01 |
| A001-T-F1-03 | ESLint flat config (next + typescript-eslint strict), `--max-warnings 0`; Prettier or ESLint-stylistic (pick one) | F | F1-01 | `pnpm lint` exits 0 | AC-01 |
| A001-T-F1-04 | Folder skeleton per spec FR-41 with `.gitkeep`; remove scaffold demo assets | F | F1-01 | `tree src` matches FR-41; `pnpm build` passes | AC-01 |
| A001-T-F1-05 | Tailwind setup + `src/styles/tokens.css` (proposed tokens, header comment "proposed — DEC-065") mapped into theme | F | F1-04 | Build passes; a test page class using `bg-surface-canvas` renders `#F8FAFE` (verified in F4-02) | AC-14 |
| A001-T-F1-06 | `.env.example`, `src/lib/env.ts` validation (fails fast on missing/invalid `NEXT_PUBLIC_ATLAS_API_BASE_URL`) | F | F1-02 | Unit test (F4-01) + `NEXT_PUBLIC_ATLAS_API_BASE_URL=notaurl pnpm build` fails with clear message | AC-04 |

## F2 — Frontend: contract, generated client, transport

| ID | Task | Repo | Depends | Verify | AC |
|---|---|---|---|---|---|
| A001-T-F2-01 | Add `specs.lock` pinned to `contract-v0.1.0` SHA; `scripts/check-specs-lock.mjs` (or call specs tool) + `pnpm check:specs-lock` | F | S2-09 | `pnpm check:specs-lock` exits 0; corrupt SHA fails | AC-02 |
| A001-T-F2-02 | `scripts/gen-api.mjs`: read contract via `git show <sha>:<path>` from `ATLAS_SPECS_DIR` (default `../atlas-specs`); run openapi-typescript (FD-02) → `src/generated/api/schema.d.ts` with do-not-edit header; `pnpm gen:api` | F | F2-01 | Running twice yields no diff; file header present | AC-03 |
| A001-T-F2-03 | ESLint rule / CI check forbidding edits: generated folder excluded from lint and protected by CODEOWNERS; reproducibility enforced in F5-03 | F | F2-02 | Lint ignores generated path; CODEOWNERS entry present | AC-03 |
| A001-T-F2-04 | `src/lib/api/transport.ts` with openapi-fetch client, base URL from env, `X-Correlation-ID` per request | F | F2-02, F1-06 | Unit test (F4-01): header attached; base URL used | AC-09 |
| A001-T-F2-05 | `src/lib/api/errors.ts`: map envelope / non-JSON / network failure to `AtlasApiError` | F | F2-04 | Unit tests for the three cases incl. `correlationId` propagation | AC-07 |

## F3 — Frontend: shell and status page

| ID | Task | Repo | Depends | Verify | AC |
|---|---|---|---|---|---|
| A001-T-F3-01 | Root `layout.tsx` (lang, metadata, tokens, skip-link) and `/` landing with single working link to `/status` | F | F1-05 | Manual + E2E (F4-03): link navigates; no other interactive elements | AC-14 |
| A001-T-F3-02 | Add TanStack Query provider (client boundary) | F | F3-01 | Build passes; provider renders once | AC-15 |
| A001-T-F3-03 | `/status` page: live, ready (per dependency), build provenance (backend/specs/frontend SHAs, contract version, migration revision) | F | F3-02, F2-05 | Manual against local backend: values match `curl` output | AC-15 |
| A001-T-F3-04 | Status states: loading, ready, degraded (503), unreachable (network), error with correlation ID; retry button refetches | F | F3-03 | Unit/component tests for each state; E2E degraded (F4-03) | AC-15 |
| A001-T-F3-05 | `NEXT_PUBLIC_ATLAS_FRONTEND_SHA` injected at build (CI SHA; local `git rev-parse`) and shown | F | F3-03 | `pnpm build && pnpm start` shows SHA equal to `git rev-parse HEAD` | AC-08 |
| A001-T-F3-06 | Production security headers + CSP in `next.config.ts` (no `unsafe-eval` in prod) | F | F3-01 | `curl -sI localhost:3000/` after `next start` shows CSP, `frame-ancestors 'none'`, nosniff, referrer policy | AC-10 |

## F4 — Frontend: tests

| ID | Task | Repo | Depends | Verify | AC |
|---|---|---|---|---|---|
| A001-T-F4-01 | Vitest + Testing Library config; unit tests for env, transport, errors, status states; coverage ≥ 80% for `src/lib` + status | F | F2-05, F3-04 | `pnpm test --coverage` passes thresholds | AC-13 |
| A001-T-F4-02 | Playwright config: projects Chromium + WebKit, `baseURL` from env, runs against `next start`, `ATLAS_E2E_API_URL` | F | F3-03 | `pnpm e2e --list` lists both projects | AC-16 |
| A001-T-F4-03 | E2E `status.spec.ts`: landing → link → status green with SHAs; keyboard-only path (Tab/Enter); degraded state via API test hook or stopped Redis in CI | F | F4-02 | `pnpm e2e` green locally against running backend | AC-15, AC-16 |
| A001-T-F4-04 | E2E `a11y.spec.ts` with @axe-core/playwright on `/` and `/status` (fail on serious/critical) | F | F4-02 | `pnpm e2e a11y` green | AC-14 |
| A001-T-F4-05 | E2E `visual.spec.ts`: screenshots at 1440×900 and 1280×720; baselines generated in the pinned Playwright container | F | F4-02 | Container run green; changing a token colour fails the comparison | AC-17 |
| A001-T-F4-06 | E2E lock parity: assert `/diagnostics/build.specs_sha` == frontend `specs.lock` | F | F4-02, F2-01 | Test passes; editing lock SHA locally makes it fail | AC-02 |

## F5 — Frontend: CI and image

| ID | Task | Repo | Depends | Verify | AC |
|---|---|---|---|---|---|
| A001-T-F5-01 | `.github/workflows/frontend-ci.yml`: install (frozen) → static (tsc, eslint) → unit; pnpm store cache | F | F4-01 | PR run green; a type error in a test PR fails `static` | AC-01 |
| A001-T-F5-02 | Add `build` job (`next build` with CI SHA) | F | F5-01 | PR run green | AC-01 |
| A001-T-F5-03 | Add `client-repro` job: checkout atlas-specs at lock SHA (`ATLAS_SPECS_READ_TOKEN`), `pnpm gen:api`, `git diff --exit-code` | F | F5-01, F2-02, M0-05 | Green; hand-editing generated file in a test PR fails | AC-03 |
| A001-T-F5-04 | Add `security` job: `pnpm audit --prod` (fail high/critical), secret scan | F | F5-01 | Green on clean tree | AC-10 |
| A001-T-F5-05 | `Dockerfile` (standalone output, non-root) + `image` job (no push) | F | F5-02 | `docker build .` succeeds; container user ≠ root | AC-05 |

## X — Cross-repository integration and sign-off

| ID | Task | Repo | Depends | Verify | AC |
|---|---|---|---|---|---|
| A001-T-X1-01 | Add `e2e/backend.ref` (backend commit SHA) to frontend; document bump procedure | F | B6-07 | File contains 40-hex SHA that exists in atlas-backend | AC-16 |
| A001-T-X1-02 | Add `e2e` CI job: checkout backend@ref (`ATLAS_BACKEND_READ_TOKEN`), start postgres/redis services, `uv sync --locked`, migrate, run api + worker with diagnostics enabled (`ATLAS_ENV=test`), then Playwright (Chromium + WebKit, a11y, visual, parity) | F | X1-01, F4-03…06 | PR run green; artifacts include Playwright report | AC-16 |
| A001-T-X1-03 | Negative parity drill: temporarily point frontend `specs.lock` at a different SHA in a test PR → `e2e` fails on parity; revert | F | X1-02 | Failed run linked in PR conversation | AC-02 |
| A001-T-X1-04 | Backend README "Local development" (macOS/Linux, Docker and native options, every Makefile target) | B | B4-11 | Fresh-machine dry run by a second engineer succeeds (AC-04 evidence) | AC-04 |
| A001-T-X1-05 | Frontend README "Local development" (Node via `.nvmrc`, pnpm, env, `gen:api`, e2e) | F | F4-03 | Same dry-run evidence | AC-04 |
| A001-T-X2-01 | Run full smoke journey (spec §7) on a clean clone of all three repos; record timings vs A001-NFR-02 | all | X1-02, X1-04, X1-05 | Evidence log attached to acceptance sign-off | AC-04, AC-18 |
| A001-T-X2-02 | Acceptance sign-off: tick every AC in `acceptance.md` with evidence links; tag `v0.1.0` (backend, frontend); update register FD/DEC rows | all | X2-01 | `acceptance.md` sign-off table complete; tags exist | all |

---

**Task count:** 108 tasks (M0 6 · S1 8 · S2 9 · B1 7 · B2 10 · B3 9 · B4 11 · B5 5 · B6 8 · F1 6 · F2 5 · F3 6 · F4 6 · F5 5 · X 7). Every task has one owner repo, explicit dependencies and its own verification step.
