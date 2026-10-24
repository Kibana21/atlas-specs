# ATLAS-001 — Engineering Foundation: Specification

| Field | Value |
|---|---|
| Work item | ATLAS-001 Engineering Foundation |
| Status | **Draft — awaiting approval** (no implementation may start before the §11 gate is signed) |
| Date | 24 October 2026 |
| Basis | `phase0/Atlas_Phase0_Engineering_Blueprint_v0_1.md` (approved as plan), `decisions/decision-register.md` v0.1, Technical Design v1.1 §6, §8, §16.2, §17 |
| Companion files | `plan.md` (how), `tasks.md` (small verifiable steps), `acceptance.md` (Given/When/Then + verification) |
| Backlog coverage | BL-013 (conventions, partial), BL-021 (bootstrap), BL-103 (API shell), BL-107 (generated client), BL-122 (test harness), BL-126 (diagnostics); **pulls forward a skeleton of BL-201** (durable jobs) to prove Redis/Taskiq + PostgreSQL |

---

## 1. Problem

The three Atlas repositories exist but contain only README and `.gitignore` files. No team can start Phase 1 feature work (canonical graph, projection, canvas) until the repositories share:

- one reproducible local development stack,
- pinned tooling,
- a contract pipeline from `atlas-specs` to backend and frontend,
- a migration discipline,
- a durable background-job path,
- CI gates that block drift.

ATLAS-001 builds that foundation as a **walking skeleton**: the thinnest end-to-end slice that proves every seam works, without any Atlas domain functionality.

## 2. Goals

1. Each repository can be cloned independently and pass its own CI without copying code from another repository (Tech §17.8).
2. A developer can bring up PostgreSQL, Redis, the FastAPI API, a Taskiq worker and the Next.js app locally with documented commands, and can see a live system-status page that renders data fetched through the generated API client.
3. API contracts are authored in `atlas-specs`, pinned by commit SHA in each consumer's `specs.lock`, enforced in backend CI (conformance) and frontend CI (client generation reproducibility).
4. Database schema changes go only through reviewed Alembic migrations, which are tested for upgrade, downgrade and drift.
5. Background work runs through Taskiq on Redis with PostgreSQL as the durable record of job state, plus a transactional outbox.
6. Every repository has an enforced test strategy: lint, types, unit, integration, contract, E2E, accessibility and visual baselines as applicable.

## 3. Non-goals (explicitly out of scope)

| Excluded | Reason / where it goes |
|---|---|
| Canonical graph tables, taxonomy, entities, relationships, projections | Blocked by Open DEC-050, DEC-056, DEC-058 → BL-101/BL-108 (ATLAS-002+) |
| Entra ID authentication, sessions, RBAC/ABAC | Blocked by DEC-026 (Proposed) and DEC-027 (Open) → BL-104/BL-008 |
| Audit event store | BL-118. Retention policy is Open (DEC-074) |
| Product UI (landscape, Passport, search, canvas, design system components) | Phase 1 features. Palette is Proposed (DEC-065) |
| Cloud deployment, environments beyond `local`/CI, image publishing | DEC-030 Proposed. ATLAS-001 only *builds* images |
| Golden MVP fixture and seed graph | BL-016 |
| Any PR-analysis or telemetry-ingestion capability | DEC-002 (Confirmed exclusion). Normal Git pull-request workflow for developing Atlas is not a product feature and is allowed |

## 4. Repository responsibilities

### 4.1 Responsibility matrix

| Concern | `atlas-specs` | `atlas-backend` | `atlas-frontend` |
|---|---|---|---|
| Requirements, UX, technical design, ADRs, decisions | **Owns** | Reads (pinned) | Reads (pinned) |
| OpenAPI contract `contracts/openapi/atlas-api.yaml` | **Owns, reviews, versions** | Implements; proves conformance in CI | Generates typed client from it |
| JSON Schemas and examples `contracts/schemas`, `contracts/examples` | **Owns** | Validates its payloads against them in contract tests | May use them for fixtures |
| Contract conventions (`conventions.md`, `compatibility.md`, error codes) | **Owns** | Implements | Implements client handling |
| `specs.lock` | Defines the format and validator | Holds its own lock | Holds its own lock |
| Specs CI (lint, schema validation, breaking-change detection, requirement registry checks) | **Owns** | – | – |
| Python application, workers, connectors, persistence | Never | **Owns** | Never |
| PostgreSQL schema and Alembic migrations | Never (may document) | **Owns exclusively** | Never connects |
| Redis, Taskiq broker, durable job tables, outbox | Never | **Owns exclusively** | Never connects |
| API process configuration, CORS allowlist, security headers on API | – | **Owns** | Supplies its origin via configuration |
| Next.js application, routes, components, styles, client state | Never | Never | **Owns** |
| Generated TypeScript API client `src/generated/api` | – | – | **Owns; generated only, never hand-edited** |
| Web security headers and CSP | – | – | **Owns** |
| Local infrastructure (PostgreSQL, Redis containers) | – | **Owns** `compose.yaml` | Uses the backend's stack. No own database |
| Backend and worker container images (build only) | – | **Owns** (one Dockerfile, two targets) | – |
| Web container image (build only) | – | – | **Owns** |
| Unit, integration, migration, contract tests | Schema/example validation | **Owns** for backend code | **Owns** for frontend code |
| Browser E2E, accessibility, visual regression | Acceptance scenarios (text) | Provides a runnable backend for E2E | **Owns** the Playwright suite |
| Build provenance (`*_sha`, migration revision, contract version) | Supplies `specs_sha` via lock | Exposes via diagnostics endpoint | Displays on status page; embeds `frontend_sha` |

### 4.2 Hard boundaries (must not)

- `atlas-specs` must not contain executable application code, secrets, runtime data or generated build artifacts. CI tooling scripts for validating specs are allowed under `tools/`. Its tests are fixtures, not application tests.
- `atlas-backend` must not hand-copy DTOs from the frontend or contract into ad-hoc dicts. Pydantic models are the implementation and conformance CI proves them against the pinned contract. It must not depend on `main` of `atlas-specs`; only the SHA in `specs.lock`.
- `atlas-frontend` must not call PostgreSQL, Redis or Azure. It must not hand-edit `src/generated/api`. It must not encode backend business rules. Only form-level UX validation is allowed.
- No repository fetches a mutable branch of another repository at runtime or in a release build (Tech §17.4).

## 5. Functional requirements

IDs are local to this work item (`A001-FR-nn`). Traceability to BRD/UX/Tech requirements is in §9.

### 5.1 Contracts and pinning (`atlas-specs`)

| ID | Requirement |
|---|---|
| A001-FR-01 | `contracts/openapi/atlas-api.yaml` exists at version **0.1.0** (OpenAPI 3.1) and defines only foundation endpoints (§6.2), the error envelope, and the shared headers. |
| A001-FR-02 | `contracts/schemas/error.v1.json`, `contracts/schemas/build-info.v1.json` and `contracts/schemas/job.v1.json` (JSON Schema 2020-12) exist, each with at least one valid and one invalid example under `contracts/examples/`. |
| A001-FR-03 | `contracts/conventions.md` defines: base path `/api/v1`; JSON only; opaque string IDs; cursor pagination shape (`items`, `next_cursor`); `X-Correlation-ID`; `If-Match`/`ETag` revision semantics; `Idempotency-Key`; status-code usage (Tech §6.3); and the initial error-code catalog (§6.4). |
| A001-FR-04 | `contracts/compatibility.md` defines semantic versioning of `atlas-api.yaml`, what counts as breaking, the deprecation process, and the backend-first rollout rule (Tech §17.4(6)). |
| A001-FR-05 | `specs.lock` format is specified (§6.5) with a validator script in `atlas-specs/tools/`. |
| A001-FR-06 | Specs CI runs Markdown lint, OpenAPI lint, JSON Schema validation of examples, a breaking-change check of `atlas-api.yaml` against the previous tagged version, and the requirement-registry check (unique IDs; every RTM row maps to an existing backlog item). |

### 5.2 Backend (`atlas-backend`)

| ID | Requirement |
|---|---|
| A001-FR-10 | The Python project is managed by `uv` with a committed `uv.lock`. The Python version is pinned and reproducible (`requires-python` plus a committed `.python-version`). |
| A001-FR-11 | Source layout follows Tech §17.1 (`src/atlas/{api,core,domain,modules,connectors,workers,persistence}`). Empty packages contain only `__init__.py`. |
| A001-FR-12 | Settings are loaded from environment variables with prefix `ATLAS_` and validated at startup. `.env.example` lists every variable with placeholder values only. |
| A001-FR-13 | FastAPI app factory exposes the §6.2 endpoints under `/api/v1`. Generated OpenAPI is exported by a command, not served as a public contract source of truth. |
| A001-FR-14 | Every response carries `X-Correlation-ID`. An inbound header value is accepted only if it matches the documented format; otherwise a new ID is generated. The ID appears in logs, error envelopes and job records. |
| A001-FR-15 | All errors (HTTP, validation, unhandled) are returned in the Tech §6.3 envelope. Unhandled errors return a generic message with no stack trace, SQL, host name or settings value. |
| A001-FR-16 | Logs are structured JSON with timestamp, level, event, correlation ID and environment. A redaction filter removes values of keys matching secret patterns (`password`, `secret`, `token`, `key`, `authorization`, connection strings). |
| A001-FR-17 | `GET /api/v1/health/live` returns 200 when the process is up. `GET /api/v1/health/ready` returns 200 only when PostgreSQL and Redis are reachable, otherwise 503 with the error envelope. |
| A001-FR-18 | `GET /api/v1/diagnostics/build` returns `backend_sha`, `specs_sha`, `contract_version`, `db_migration_revision` and `environment`. It is enabled only when `ATLAS_DIAGNOSTICS_ENABLED=true`, which defaults to `false` and is allowed only for `local`/`dev`/`test`. When disabled it returns 404. *(Tech §17.4(7) requires authentication; until BL-104 this endpoint is restricted by environment, not by identity.)* |
| A001-FR-19 | PostgreSQL access uses SQLAlchemy 2 (async engine) with the psycopg 3 driver. Alembic uses the same metadata and a naming convention for constraints and indexes. |
| A001-FR-20 | The first migration creates only infrastructure tables: `job`, `job_attempt`, `outbox_event` (§6.6). No domain tables. |
| A001-FR-21 | Every migration is reversible. CI proves `upgrade head → downgrade base → upgrade head` on an empty database and that autogenerate detects no drift between models and migrations. |
| A001-FR-22 | A Taskiq broker on Redis and a worker entry point exist. Worker and API are built from the same source and image family. |
| A001-FR-23 | Job lifecycle: creating a job inserts a `job` row (status `queued`, unique `idempotency_key`) and an `outbox_event` in **one transaction**. A relay dispatches outbox events to Taskiq. The worker records each attempt in `job_attempt` and transitions `job.status` (`queued → running → succeeded \| failed \| retrying`). A duplicate `idempotency_key` returns the existing job instead of creating a new one. |
| A001-FR-24 | Transient failures retry with exponential backoff and jitter up to a configured maximum. Exhausted jobs end in `failed` with `last_error` set (sanitized). |
| A001-FR-25 | A diagnostic task `diagnostics.ping` exercises the pipeline. `POST /api/v1/diagnostics/jobs/ping` creates one and `GET /api/v1/jobs/{job_id}` reads its state. Both exist only when diagnostics are enabled (FR-18 rule). |
| A001-FR-26 | Losing Redis state (flush or restart) never deletes or corrupts `job` / `job_attempt` rows. Undispatched outbox events are re-dispatched by the relay. |
| A001-FR-27 | Backend CI verifies `specs.lock`, fetches the contract at the pinned SHA, and fails if the FastAPI-generated OpenAPI differs from the pinned contract in paths, operations, parameters, request bodies, responses or schemas (descriptions and examples excluded). |
| A001-FR-28 | One multi-stage `Dockerfile` builds `api` and `worker` targets. CI builds both and does not push. Containers run as a non-root user. |
| A001-FR-29 | A `Makefile` provides the documented developer commands (§7). Each target is a thin wrapper over `uv`/`docker compose`/`alembic`. |
| A001-FR-30 | CORS allows only origins listed in `ATLAS_CORS_ORIGINS` (default `http://localhost:3000` for `local`). The API sets baseline security headers (`X-Content-Type-Options: nosniff`, `Referrer-Policy: no-referrer`, `Cache-Control: no-store` on API responses). |

### 5.3 Frontend (`atlas-frontend`)

| ID | Requirement |
|---|---|
| A001-FR-40 | A Next.js App Router project in TypeScript `strict` mode, managed by **pnpm** with a committed lockfile. Node version pinned (`.nvmrc`, `engines`, `packageManager`). |
| A001-FR-41 | Source layout follows Tech §17.2 (`src/app`, `src/components/{ui,canvas,shell}`, `src/features/{studio,explore,intelligence}`, `src/generated/api`, `src/lib`, `src/styles`). Empty folders hold a `.gitkeep`. |
| A001-FR-42 | `pnpm gen:api` generates TypeScript types from the OpenAPI file at the SHA in `specs.lock` into `src/generated/api/`. Output is committed and carries a "generated — do not edit" header. CI fails if regeneration produces a diff. |
| A001-FR-43 | A thin transport module (`src/lib/api/`) wraps the generated client. It is the only place that knows the API base URL, adds `X-Correlation-ID`, and maps the error envelope to a typed error. The base URL comes from validated environment configuration. |
| A001-FR-44 | The `/status` route shows backend liveness, readiness and build provenance (backend, specs, frontend SHAs; contract version; migration revision), fetched through the transport module. It shows explicit loading, success, unavailable and error states with the correlation ID. |
| A001-FR-45 | The `/` route is a minimal branded landing page in the bright theme with one working link to `/status`. **No dead controls**: nothing is shown that does not work (DEC-012). |
| A001-FR-46 | Proposed design tokens (Tech §5.3, UX §2.1) are defined once as CSS custom properties in `src/styles/tokens.css` and wired into Tailwind. They are marked *proposed (DEC-065)*. |
| A001-FR-47 | Production builds send security headers including a Content-Security-Policy without `unsafe-eval` in production, `frame-ancestors 'none'`, `X-Content-Type-Options` and `Referrer-Policy`. |
| A001-FR-48 | `pnpm check:specs-lock` validates the lock file. In E2E mode it also asserts the running backend reports the same `specs_sha`. |
| A001-FR-49 | One `Dockerfile` builds the web image (`output: "standalone"`). CI builds it and does not push. |

## 6. Interfaces

### 6.1 Ports and local URLs

| Service | Local address | Owner |
|---|---|---|
| PostgreSQL 16 | `localhost:5432` (db `atlas`, user `atlas`, local-only password from `.env`) | backend `compose.yaml` |
| Redis 7 | `localhost:6379` | backend `compose.yaml` |
| FastAPI | `http://localhost:8000` | backend |
| Taskiq worker | no port | backend |
| Next.js | `http://localhost:3000` | frontend |

All ports are overridable by environment variables documented in each `.env.example`.

### 6.2 Foundation API (contract 0.1.0)

| Method and path | Auth | Purpose | Responses |
|---|---|---|---|
| `GET /api/v1/health/live` | none | Process liveness | 200 `{status:"ok"}` |
| `GET /api/v1/health/ready` | none | Dependency readiness (PostgreSQL, Redis) | 200 `{status:"ok", checks:{database:"ok", redis:"ok"}}` · 503 error envelope `DEPENDENCY_UNAVAILABLE` |
| `GET /api/v1/diagnostics/build` | env-restricted (FR-18) | Build provenance | 200 `BuildInfo` · 404 `NOT_FOUND` when disabled |
| `POST /api/v1/diagnostics/jobs/ping` | env-restricted | Enqueue diagnostic job; header `Idempotency-Key` required | 202 `Job` · 200 `Job` (duplicate key) · 422 · 404 when disabled |
| `GET /api/v1/jobs/{job_id}` | env-restricted in ATLAS-001; owner/scope check arrives with BL-104 | Job state | 200 `Job` · 404 |

`BuildInfo`: `backend_sha` (40-hex or `"unknown"` locally), `specs_sha` (40-hex), `contract_version` (semver), `db_migration_revision` (string or null), `environment` (`local|dev|test|uat|prod`).
`Job`: `id`, `type`, `status` (`queued|running|retrying|succeeded|failed`), `attempts`, `created_at`, `updated_at`, `correlation_id`, `last_error` (sanitized string or null).

### 6.3 Error envelope (Tech §6.3)

```json
{"error": {"code": "STRING_CODE", "message": "Human readable, no internals", "correlation_id": "…", "details": {}, "recoverable": false}}
```

### 6.4 Initial error-code catalog

`VALIDATION_FAILED` (422) · `NOT_FOUND` (404) · `DEPENDENCY_UNAVAILABLE` (503, recoverable) · `IDEMPOTENCY_KEY_REQUIRED` (422) · `REVISION_CONFLICT` (409/412, reserved for Phase 1) · `RATE_LIMITED` (429, reserved) · `INTERNAL_ERROR` (500). Codes are append-only.

### 6.5 `specs.lock` (in `atlas-backend` and `atlas-frontend` roots)

```yaml
specs_repo: atlas-specs
specs_commit: "<40-hex SHA reachable in atlas-specs>"
api_contract: contracts/openapi/atlas-api.yaml
schemas_dir: contracts/schemas
contract_version: "0.1.0"
```

Rules: `specs_commit` must be a full SHA (no branch or tag names). `contract_version` must equal `info.version` of the contract at that SHA. Tools read contract files with `git show <sha>:<path>` from a local `atlas-specs` clone (default `../atlas-specs`, overridable with `ATLAS_SPECS_DIR`) or from a CI checkout at that SHA.

### 6.6 Infrastructure tables (first migration)

| Table | Columns (indicative) | Constraints |
|---|---|---|
| `job` | `id uuid pk`, `type text`, `status text`, `idempotency_key text`, `payload jsonb`, `attempts int`, `max_attempts int`, `correlation_id text`, `last_error text null`, `created_at`, `updated_at` | unique `(type, idempotency_key)`; status check constraint |
| `job_attempt` | `id uuid pk`, `job_id fk`, `attempt int`, `started_at`, `finished_at null`, `outcome text`, `error text null` | unique `(job_id, attempt)` |
| `outbox_event` | `id uuid pk`, `topic text`, `payload jsonb`, `created_at`, `dispatched_at null`, `dispatch_attempts int` | index on `dispatched_at` where null |

IDs come from one application-side ID factory. UUIDv7 per DEC-037 (Proposed); swapping to UUIDv4 changes one function.

## 7. Local development experience

Documented in each repo README. The developer-facing commands:

| Repo | Command | Effect |
|---|---|---|
| backend | `make setup` | `uv sync`, copy `.env.example` → `.env` if absent |
| backend | `make up` / `make down` | Start/stop PostgreSQL + Redis via `docker compose` (named volumes) |
| backend | `make migrate` | `alembic upgrade head` |
| backend | `make api` | Run FastAPI with reload on :8000 |
| backend | `make worker` | Run Taskiq worker (and outbox relay) |
| backend | `make check` | Lint + format check + types + unit tests |
| backend | `make test-integration` | Integration + migration tests against the compose services |
| backend | `make contract` | Verify `specs.lock` and OpenAPI conformance |
| frontend | `pnpm install` | Install pinned dependencies |
| frontend | `pnpm dev` | Next.js dev server on :3000 |
| frontend | `pnpm gen:api` | Regenerate the client from the pinned contract |
| frontend | `pnpm check` | Typecheck + lint + unit tests + lock check |
| frontend | `pnpm e2e` | Playwright against a running backend (`ATLAS_E2E_API_URL`) |
| specs | `make check` (or documented `npx`/`uvx` commands) | Lint docs, lint OpenAPI, validate schemas/examples, registry check |

**Smoke journey (local):** `make up && make migrate && make api` plus `make worker` in the backend → `pnpm dev` in the frontend → open `/status` → all checks green, SHAs shown → `curl` the ping job → `GET /jobs/{id}` reaches `succeeded`.

## 8. Non-functional requirements

| ID | Requirement |
|---|---|
| A001-NFR-01 | **Reproducibility:** clean clone → green local checks using only the README, on macOS and Linux. Lockfiles enforced in CI (`uv sync --locked`, `pnpm install --frozen-lockfile`). |
| A001-NFR-02 | **Speed:** backend `make check` ≤ 60 s and frontend `pnpm check` ≤ 90 s on a reference developer laptop for the foundation codebase. Each repo's CI pipeline ≤ 15 min. |
| A001-NFR-03 | **Quality gates:** Ruff (lint + format), mypy `--strict` with the Pydantic plugin, TypeScript `strict`, ESLint with zero warnings in CI. |
| A001-NFR-04 | **Coverage:** backend foundation code ≥ 85% line coverage (unit + integration). Frontend transport and status logic ≥ 80%. Thresholds enforced in CI and raised later, never lowered. |
| A001-NFR-05 | **Security baseline:** no secrets in repos (secret scanning in CI); dependency vulnerability audit (`pip-audit`, `pnpm audit --prod`) fails on high/critical; Ruff security rules (`S`) enabled; containers non-root; errors and logs leak no internals (FR-15/16). |
| A001-NFR-06 | **Accessibility:** `/` and `/status` pass axe-core with zero serious/critical violations and are fully keyboard operable. |
| A001-NFR-07 | **Browsers:** E2E runs in Chromium and WebKit (proposed reading of DEC-055: Chromium mandatory + Safari engine as the "one additional"). |
| A001-NFR-08 | **Visual baseline:** golden screenshots of `/` and `/status` at 1440×900 and 1280×720, generated and compared only in the CI Linux container to avoid OS font drift. |
| A001-NFR-09 | **Observability of Atlas only:** structured logs and job state. No external telemetry SDKs, no enterprise telemetry ingestion (DEC-002/003). |

## 9. Traceability

| ATLAS-001 item | Satisfies / enables |
|---|---|
| FR-01…06, FR-27, FR-42, FR-48 | Tech §17.4 contract-first workflow; §17.7 drift safeguards; DEC-039; BL-013, BL-021 |
| FR-10, FR-11, FR-40, FR-41 | Tech §17.1, §17.2 layouts; DEC-020, DEC-024, DEC-038 |
| FR-13…FR-18, FR-30 | Tech §6, §6.3, §15, §17.4(7); BL-103, BL-126; NFR-06, NFR-12 (BRD §8, proposed IDs) |
| FR-19…FR-21 | Tech §3.5 hardening, §17.7 expand/migrate/contract; DEC-021 |
| FR-22…FR-26 | Tech §8 worker reliability; DEC-028; BL-201 (skeleton) |
| FR-28, FR-49 | Tech §17.5 release outputs; §17.7 one-commit images |
| FR-43…FR-47 | Tech §5.1, §9.3 (CSP); UX §1.2(5), DEC-011, DEC-012 |
| NFR-03…08 | Tech §17.5, §20.3; UX-NFR-008/011/012; BRD EXP-02, NFR-13 (proposed ID); BL-122 |
| Tech §17.8 acceptance bullets 1–6 | `acceptance.md` A001-AC-01…AC-06 |

## 10. Assumptions and decisions used

Decisions are taken from the register. **None become Confirmed by this spec.** Approving this spec confirms the rows marked "confirm at gate" for the scope of ATLAS-001, and the register is updated afterwards.

| Ref | Decision | Register status | Used as | Gate action |
|---|---|---|---|---|
| DEC-001 | Three independent repositories | Confirmed | Basis | – |
| DEC-002/003 | Scope exclusions; Atlas self-diagnostics allowed | Confirmed | Basis | – |
| DEC-012 | Real-browser acceptance; no dead controls | Confirmed | Basis | – |
| DEC-020 | Python 3.12+, FastAPI, Pydantic v2, SQLAlchemy 2, Alembic | Proposed | Working assumption | **Confirm at gate** |
| DEC-021 | PostgreSQL 16+ | Proposed | Working assumption | **Confirm at gate** |
| DEC-024 | Next.js App Router, TS strict, Tailwind (shadcn/ui deferred to Phase 1) | Proposed | Working assumption | **Confirm at gate** |
| DEC-028 | Taskiq + Redis + PostgreSQL durable jobs/outbox | Proposed | Working assumption | **Confirm at gate** |
| DEC-037 | UUIDv7 | Proposed | Isolated in ID factory | Confirm or choose v4 |
| DEC-038 | uv, Ruff, mypy *or* pyright, pytest, Hypothesis; pnpm, ESLint, Vitest, Playwright | Proposed | Working assumption | **Confirm at gate**, including FD-01/FD-02 |
| DEC-039 | Contract-first, `specs.lock` SHA pinning | Proposed | Core of ATLAS-001 | **Confirm at gate** |
| DEC-040 | Keep current `atlas-specs` folder layout; add `contracts/examples`, `tools/`, `features/` | Proposed | Working assumption | **Confirm at gate** |
| DEC-042 | Frontend develops against contract mocks; acceptance against real backend | Proposed | Working assumption | Confirm at gate |
| DEC-055 | Browser matrix | **Open** | Proposed reading (NFR-07) | Confirm Chromium + WebKit for foundation |
| DEC-065 | Palette | **Open** | Tokens marked proposed | No action (not blocking) |
| DEC-026/027 | Auth and session model | Proposed / **Open** | **Not used**; diagnostics env-restricted | None; out of scope |

**Foundation-local decisions (new; become ADRs on approval):**

| ID | Decision | Recommendation | Alternatives |
|---|---|---|---|
| FD-01 | Python type checker | **mypy `--strict`** + Pydantic plugin (mature SQLAlchemy 2/Pydantic support) | pyright (faster) |
| FD-02 | OpenAPI → TypeScript generator | **openapi-typescript** (types) + **openapi-fetch** (tiny typed runtime) | orval, @hey-api/openapi-ts |
| FD-03 | PostgreSQL driver | **psycopg 3** for both async app and sync Alembic (one driver) | asyncpg + psycopg2 |
| FD-04 | Structured logging | **structlog** JSON renderer over stdlib logging | python-json-logger |
| FD-05 | Local infrastructure runtime | **Docker Compose** (`compose.yaml` in backend) with Docker Desktop, Colima or Podman | Natively installed services |
| FD-06 | CI platform | **GitHub Actions** (repos are on GitHub; Tech §17 names `.github/workflows`) | Azure DevOps Pipelines |
| FD-07 | Cross-repo CI access to `atlas-specs` (and backend for frontend E2E) | Read-only fine-grained token or GitHub App installation stored as a repository secret | Public repos (no secret) |
| FD-08 | Contract conformance method | **oasdiff** structural diff (both directions) between FastAPI output and the pinned contract, ignoring descriptions/examples | Byte-equality of normalized JSON |
| FD-09 | Specs lint tooling | markdownlint-cli2, Redocly CLI (OpenAPI lint), check-jsonschema (examples), oasdiff (breaking), Python `tools/check_registry.py` | Spectral; ajv-cli |
| FD-10 | Frontend → API call path during ATLAS-001 | Browser calls the API directly with a CORS allowlist, isolated in `src/lib/api/transport.ts` so a BFF (DEC-027) can replace it without touching features | Next.js route-handler proxy now |
| FD-11 | Version pinning policy | Pin the latest stable release of each tool at implementation time in lockfiles. Minimums: Python 3.12, PostgreSQL 16, Redis 7, Node.js Active LTS, Next.js current stable major. Renovate/Dependabot proposals reviewed weekly | Floating ranges (rejected) |
| FD-12 | Backend `.gitignore` ignores `.python-version` | Remove that line so the uv Python pin is committed (FR-10) | Rely on `requires-python` only |

## 11. Approval gate (stop point)

Implementation of `tasks.md` starts only after all of these are recorded:

1. Approval of this spec, `plan.md`, `tasks.md` and `acceptance.md`.
2. Confirmation of DEC-020, 021, 024, 028, 038, 039, 040 (and 037, 042) for ATLAS-001 scope. Register rows are updated and ADR-0006 (repo/contract governance) is written.
3. Choices on FD-01…FD-12 (accept the recommendations or override them).
4. DEC-055 foundation reading (Chromium + WebKit) accepted.
5. FD-07 credential approach agreed, plus who creates the secrets.
6. Named code owners for each repository (CODEOWNERS) and a release coordinator. This is part of DEC-081, which can be partial for ATLAS-001.

## 12. Revision record

| Version | Date | Change |
|---|---|---|
| 0.1 | 2026-10-24 | Initial draft for approval. |
