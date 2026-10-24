# ATLAS-001 — Engineering Foundation: Specification

| Field | Value |
|---|---|
| Work item | ATLAS-001 Engineering Foundation |
| Version | **0.2.3** (controlled amendments of 0.2.1; see §13) — final candidate of v0.2: owner decisions D-01…D-07 applied, PostgreSQL roles simplified, authentication and repository-visibility analysis added (24 Oct 2026) |
| Status | **Accepted** (owner, 24 Oct 2026, Gate G7; `evidence.md` §13.11), subject to the recorded deviations and `follow-ups.md`. Implemented from baseline v0.2.1 with amendments v0.2.2/v0.2.3 |
| Basis | Phase 0 Blueprint (approved as plan); `decisions/decision-register.md` v0.3; Technical Design v1.1 §6, §8, §16.2, §17 (deviations recorded in `decisions/baseline-deviations.md`) |
| Companions | `plan.md`, `tasks.md`, `acceptance.md`, `readiness.md` (approval request), `changes-v0.2.md`, `ci-access.md`, `proposals/postgres-local-setup.sql` and `proposals/pg_hba-atlas.conf` (review only, **not applied**) |
| Backlog coverage | BL-013 (conventions, partial), BL-021 (bootstrap), BL-103 (API shell), BL-107 (generated client), BL-122 (test harness, Chromium only), BL-126 (diagnostics), BL-024 (tokens, as proposed values). BL-201 (durable jobs/outbox) is **deferred** (DEC-046) |

---

## 1. Purpose

ATLAS-001 delivers a **minimal, production-quality walking skeleton**. It proves every engineering seam between `atlas-specs`, `atlas-backend` and `atlas-frontend` without implementing any Atlas product capability:

- Reproducible local development on the owner's **existing PostgreSQL 15 and Redis**, isolated from their other users.
- Pinned tooling and quality gates in each repository.
- Contract-first API: authored in `atlas-specs`, pinned by SHA, enforced by **exact conformance**. The check detects missing and unexpected operations as well as any shape difference.
- Alembic migration mechanism with **separated runtime, migration and test credentials** and least privilege.
- A Taskiq/Redis integration seam proven by a worker round-trip test that cleans up only its own keys.
- The bright Atlas design foundation: tokens, accessibility rules and reduced motion, with no product UI.
- GitHub Actions CI per repository, with real-browser (Chromium) E2E against a persisted backend.

## 2. Non-goals

| Excluded or deferred | Reason / destination |
|---|---|
| Canonical graph, taxonomy, entities, projections, any domain table | Open DEC-050/056/058 → BL-101+ |
| Authentication, sessions, RBAC/ABAC | DEC-026 Proposed, DEC-027 Open → BL-104/BL-008 |
| Transactional outbox, durable job tables, retries/backoff, job endpoints | **Deferred by DEC-046** → BL-201, a hard prerequisite of the first business background job |
| Audit store | BL-118 (DEC-074 Open) |
| Product UI: navigation rail, Home, landscape, Passport, search, canvas, component library (shadcn/ui), Azure icons | Phase 1. DEC-061 (icon licence) Open |
| Screenshot/visual baselines, WebKit/second browser engine | Deferred (review M-04). DEC-055 Open |
| Local container orchestration for PostgreSQL/Redis (`compose.yaml`) | Replaced by existing services (DEC-043/044/045). CI uses isolated service containers |
| Cloud deployment, image publishing | DEC-030 Proposed. ATLAS-001 only builds images |
| Changes to the BRD, UX or Technical Design baselines | Not required. Documentation lint excludes them (FR-07) |
| PR analysis, telemetry ingestion, tracing, provisioning, AI | **Product exclusions (DEC-002) unchanged.** The Git pull-request workflow used to develop Atlas is not a product feature |

## 3. Decision status used by this spec

### 3.1 Approved (owner, 24 Oct 2026)

| Ref | Decision |
|---|---|
| DEC-043 (D-01) | PostgreSQL **15** for local development and CI. Production major remains separate (DEC-086 Open) |
| DEC-044 (D-02) | Dedicated Atlas databases and least-privilege roles. **Runtime, migration and test credentials are separate.** `atlas_db` verified empty before any proposal (§6.2). **No server, role, database or permission change until the SQL in `proposals/` is reviewed and applied by the owner** |
| DEC-045 (D-03) | Redis logical DB **10** for local, **11** for tests, Atlas key prefixes. **No `FLUSHALL`/`FLUSHDB`.** Tests delete only keys they created. Other Redis users undisturbed. CI uses isolated Redis services |
| DEC-046 (D-04) | Outbox and durable job persistence deferred to BL-201. ATLAS-001 = minimal Taskiq/Redis integration test + migration mechanism |
| DEC-047 (D-05) | GitHub Actions. Cross-repo read via built-in `GITHUB_TOKEN` (repos are currently public) or GitHub App installation tokens if private. **No long-lived PATs.** No credentials created or changed yet (`ci-access.md`) |
| DEC-048 (D-06) | Node.js **24 LTS**, pinned consistently in local tooling and CI |
| DEC-020 (D-07) | Python **3.12** baseline; FastAPI, Pydantic v2, SQLAlchemy 2, Alembic. **Modification:** dependencies pinned to supported, mutually compatible versions (FR-20a); later Python upgrades only through a new controlled decision |
| DEC-024 (D-07) | Next.js App Router, TypeScript strict, Tailwind, TanStack Query. shadcn/ui and Zustand stay provisional until needed |
| DEC-028 (D-07) | Taskiq + Redis for initial background task dispatch. Outbox and durable job tables deferred to BL-201 (DEC-046) |
| DEC-038 (D-07) | uv, Ruff, pytest, pnpm, ESLint, Vitest, Playwright, **mypy**, **openapi-typescript** |
| DEC-039 (D-07) | Contract-first is **mandatory**. **Modification:** development and CI pin immutable `atlas-specs` commits; version tags are created only for **approved contract releases**, not for every API change (§6.4) |
| DEC-040 (D-07) | Proposed specs layout adopted. **Modification:** the difference from Technical Design §17.3 is recorded (`decisions/baseline-deviations.md`, TD-DEV-001) and reconciled through a controlled Technical Design revision |
| DEC-001/002/003/012 | Three repos; product exclusions; Atlas self-diagnostics allowed; real-browser acceptance, no dead controls |

### 3.2 Pending owner approval

None. The specification set was approved on 24 Oct 2026, and DEC-085 was decided: **repositories stay public** (§6.8).

### 3.3 Provisional implementation assumptions (Claude-resolved, reversible, recorded in register §F)

| Ref | Assumption |
|---|---|
| DEC-090 | Python **3.12** (`requires-python = "==3.12.*"`, committed `.python-version`). Available locally via uv; no install |
| DEC-091 | mypy in `--strict` mode with the Pydantic plugin (*mypy itself now approved under DEC-038; the strictness configuration is the provisional part*) |
| DEC-092 | **openapi-fetch** as the typed runtime over openapi-typescript output (*openapi-typescript approved under DEC-038; openapi-fetch remains provisional*) |
| DEC-093 | PostgreSQL driver: **psycopg 3** (async app + sync Alembic) |
| DEC-094 | Logging: **structlog** JSON over stdlib logging |
| DEC-095 | Contract conformance: inventory check + normalized exact diff (**oasdiff**, pinned container image) implemented once in `atlas-specs/tools` (§6.7) |
| DEC-096 | Specs lint: markdownlint-cli2 (scoped), Redocly CLI, check-jsonschema |
| DEC-097 | Browser calls API directly with CORS allowlist, isolated in `src/lib/api/transport.ts` (replaceable by BFF, DEC-027) |
| DEC-098 | Taskiq `ListQueueBroker` (taskiq-redis) for the seam. Queue name derived from the Atlas prefix. At-least-once/durability is BL-201's job |
| DEC-099 | Design tokens authored in `atlas-specs/design/tokens.json` and **generated** into frontend CSS (same pattern as the API client) |

### 3.4 Unresolved (not blocking ATLAS-001 unless stated)

DEC-055 browser matrix (Chromium-only now) · DEC-065 palette approval (tokens remain *proposed*) · DEC-083 database locale/collation (`C` locally; CI matches; real choice before BL-101/BL-111) · DEC-084 local `pg_hba.conf` `trust` authentication (owner's server; optional Atlas-only hardening proposed, §6.2) · DEC-084 Atlas-specific `pg_hba` hardening (**approved in principle, not applied**; pre-CP3 checks in §6.2) · DEC-086 production PostgreSQL major.

## 4. Repository responsibilities

| Concern | `atlas-specs` | `atlas-backend` | `atlas-frontend` |
|---|---|---|---|
| Requirements, UX, technical design, ADRs, decision register, work-item specs | **Owns** | Reads at pinned SHA | Reads at pinned SHA |
| OpenAPI `contracts/openapi/atlas-api.yaml`, JSON Schemas, examples, conventions, compatibility policy, contract style guide | **Owns, versions, tags** | Implements; proves conformance | Generates typed client |
| Design tokens `design/tokens.json` + rules `design/tokens.md` (incl. accessibility rules) | **Owns**; CI validates contrast | – | Generates CSS from them; enforces rules in UI tests |
| Specs tooling `tools/` (lock validator, conformance checker, token checker, registry checker) | **Owns** (CI tooling, not product code) | Runs conformance tool at pinned SHA | Runs lock validator at pinned SHA |
| `specs.lock` | Defines format + validator | Holds own lock | Holds own lock |
| Python API, worker, persistence, Alembic migrations, Redis/Taskiq | Never | **Owns exclusively** | Never connects |
| Database role/permission bootstrap SQL (local + CI) | Reviews the proposal (`proposals/`) | **Owns** the executable copy after approval (`scripts/db/`) | – |
| API CORS allowlist, API security headers | – | **Owns** | Supplies its origin via config |
| Next.js app, routes, styles, client state, CSP/web security headers | Never | Never | **Owns** |
| Generated code (`src/generated/api`, `src/styles/tokens.generated.css`) | – | – | **Owns; never hand-edited**, reproducibility checked in CI |
| Backend images (`api`, `worker`) / web image (build only) | – | **Owns** | **Owns** |
| Browser E2E (Chromium), accessibility checks | Acceptance text | Provides runnable backend at a pinned ref | **Owns** suite |
| Build provenance | `specs_sha` via lock | Exposes via diagnostics | Displays; embeds `frontend_sha` |

**Must not:**

- `atlas-specs`: no executable product code, secrets, runtime data or build artifacts.
- `atlas-backend`: never tracks `atlas-specs` `main`, and never hand-copies frontend types.
- `atlas-frontend`: never touches PostgreSQL, Redis or Azure, never hand-edits generated files, never encodes backend business rules.
- No repository fetches a mutable branch of another at build or runtime.

## 5. Functional requirements

IDs are renumbered for v0.2 (mapping from v0.1 in `changes-v0.2.md` §2).

### 5.1 `atlas-specs`

| ID | Requirement |
|---|---|
| A001-FR-01 | `contracts/openapi/atlas-api.yaml` **0.1.0**, OpenAPI 3.1, written in the **Pydantic-compatible dialect** of `contracts/style-guide.md`. It defines exactly three operations (§6.5), shared components (error envelope, `X-Correlation-ID` header) and per-operation error responses. |
| A001-FR-02 | JSON Schemas (2020-12) `error.v1`, `build-info.v1`, `health-live.v1` and `health-ready.v1` in `contracts/schemas/`, **one schema per response body**, each with ≥1 valid and ≥1 invalid example in `contracts/examples/<schema>/`. *(Amendment A1, v0.2.2: originally a single `health.v1`; split because a union schema accepted an invalid readiness body that also matched the liveness shape. Owner-approved E-01.)* |
| A001-FR-03 | `contracts/conventions.md`: base path, IDs, cursor pagination shape (reserved), headers (`X-Correlation-ID`; `If-Match`, `Idempotency-Key` reserved), status-code usage, error-code catalog (§6.6). `contracts/style-guide.md`: operationId naming, component naming, nullable form (`anyOf` with `null`), no inline shared schemas, error responses on every operation. |
| A001-FR-04 | `contracts/compatibility.md`: semver for `atlas-api.yaml`, breaking-change definitions, deprecation, backend-first rollout (Tech §17.4(6)). |
| A001-FR-05 | `tools/check_specs_lock.py` validates a consumer's `specs.lock` (§6.4) with self-tests. |
| A001-FR-06 | `tools/contract_conformance.py` implements §6.7, with self-tests on fixture pairs covering at least: cosmetic-only difference (pass), missing operation, unexpected operation, operationId mismatch, added optional response property, removed required property, changed status code (all fail with specific messages). |
| A001-FR-07 | Specs CI (GitHub Actions) runs: markdownlint on **non-baseline documents only** (`brd/`, `ux/`, `technical/` excluded; baselines are never edited to satisfy lint); Redocly lint of the contract; schema/example validation; tools self-tests; token contrast check; registry check; breaking-change check against the latest **approved release tag** (`contract-v*`). markdownlint, Redocly and oasdiff run from **container images pinned by digest**, identically in CI and locally (no Node required for `atlas-specs`). |
| A001-FR-08 | `design/tokens.json` (machine-readable, normative values of §7.1) and `design/tokens.md` (rules of §7.2–7.3). `tools/check_tokens.py` fails if any declared foreground/background pair misses its required WCAG ratio. Every value is marked *proposed — DEC-065*. |
| A001-FR-09 | `tools/check_registry.py`: unique requirement IDs in `phase0/requirements-registry.csv`; every `BL-`/`DEC-` reference resolves. |

### 5.2 `atlas-backend`

| ID | Requirement |
|---|---|
| A001-FR-20 | uv-managed project with committed `uv.lock` and `.python-version` (the existing `.gitignore` line for `.python-version` is removed). Layout per Tech §17.1 (`src/atlas/{api,core,domain,modules,connectors,workers,persistence}`; empty packages contain only `__init__.py`). |
| A001-FR-20a | **Dependency pinning (DEC-020 modification):**<br>• Python is fixed at 3.12 (`requires-python = "==3.12.*"`).<br>• Every direct dependency in `pyproject.toml` declares a lower bound equal to the version verified at implementation, plus an upper bound below the next major (below the next **minor** for 0.x packages such as FastAPI). Each version must officially support Python 3.12.<br>• `uv.lock` pins exact versions and hashes; CI installs with `uv sync --locked`.<br>• Upgrades arrive as reviewed changes that pass all gates.<br>• A Python minor upgrade requires a new decision-register entry. |
| A001-FR-21 | Settings from `ATLAS_*` environment variables, validated at startup (§6.3), including **environment guards**:<br>• `ATLAS_ENV=test` requires database `atlas_test`, Redis DB 11 and prefix `atlas:test:`;<br>• `local`/`dev` forbid `atlas_test` and Redis DB 11;<br>• Redis DB ≠ 10/11 is rejected in local/test;<br>• diagnostics are refused when `ATLAS_ENV ∈ {uat, prod}`. |
| A001-FR-22 | App factory `create_app(settings)`. All routes under `/api/v1` with **explicit `operation_id`**, error-envelope responses declared for 4xx/5xx on every route, and an OpenAPI hook adding the `X-Correlation-ID` response header to every response. The **schema is identical in every environment**: diagnostics routes are always registered and disabled by a guard. `/docs` and `/openapi.json` are served only in `local`. |
| A001-FR-23 | Correlation ID: an inbound `X-Correlation-ID` matching `^[A-Za-z0-9_-]{8,64}$` is reused, otherwise `req_<uuid7>` is generated. It is echoed on every response and bound to logs, error envelopes and worker task logs. |
| A001-FR-24 | Every error (Atlas, validation, HTTP, unhandled) returns the Tech §6.3 envelope. Unhandled errors return `INTERNAL_ERROR` without traceback, SQL, path, host or settings values. |
| A001-FR-25 | structlog JSON logs (timestamp, level, event, correlation_id, environment) with a redaction processor for secret-like keys and DSNs. |
| A001-FR-26 | `GET /api/v1/health/live` → 200. `GET /api/v1/health/ready` → 200 if PostgreSQL (runtime role) and Redis (configured DB) respond within 1 s each, else 503 `DEPENDENCY_UNAVAILABLE` naming the failed check (no host or credentials). |
| A001-FR-27 | `GET /api/v1/diagnostics/build` → `BuildInfo` (§6.5) when `ATLAS_DIAGNOSTICS_ENABLED=true` (default `false`), else 404 `NOT_FOUND`. Environment-restricted until BL-104 adds identity. |
| A001-FR-28 | SQLAlchemy 2 async engine (psycopg 3) using the **runtime** URL only. Alembic uses the **migration** URL only; the migration role **owns** schema `atlas` and every object it creates. `alembic_version` is kept in schema `atlas`, and a constraint naming convention is applied. **Rule for all future migrations:** the runtime role receives read access by default only. Any write privilege is granted per table, explicitly, inside the migration that creates the table, using `ATLAS_DB_APP_ROLE` (reviewed in code review). ATLAS-001's baseline needs none. |
| A001-FR-29 | Migration mechanism: reviewed **empty baseline revision `0001_baseline`**. Tests prove `upgrade head → downgrade base → upgrade head` on `atlas_test` with the test migration role, `alembic check` (no drift), and a single head. No domain or job tables. |
| A001-FR-30 | Least-privilege proof (integration tests on `atlas_test`):<br>• the runtime role cannot `CREATE` in schema `atlas`, cannot create temporary tables, and cannot write to a table without an explicit grant;<br>• neither role can connect to the other environment's database;<br>• no Atlas role is superuser, or can create roles or databases, replicate or bypass RLS;<br>• the runtime role can read `alembic_version`, so build info reports `db_migration_revision`. |
| A001-FR-31 | Taskiq broker (`ListQueueBroker`) on the configured Redis DB with queue name `<prefix>taskiq:queue`. Worker entry point (`make worker`) built from the same source and image family as the API. |
| A001-FR-32 | Task `diagnostics.ping(marker_id, correlation_id)` writes `<prefix>ping:<marker_id>` with TTL ≤ 60 s and logs the correlation ID. |
| A001-FR-33 | Worker round-trip integration test:<br>• starts a real worker process;<br>• enqueues `diagnostics.ping`;<br>• observes the marker key;<br>• deletes **only the exact keys it created** (marker and queue key), via a key-tracker fixture.<br>A session guard asserts no key remains under the run prefix `atlas:test:<run_id>:`, and that the set of keys outside that prefix in DB 11 is unchanged. |
| A001-FR-34 | Redis safety: no source or test file contains `FLUSHALL`, `FLUSHDB`, `KEYS` pattern deletion, `CONFIG SET`, `SWAPDB` or `SELECT` (static check test). Clients refuse a DB index other than the configured one. |
| A001-FR-35 | `make doctor`: **read-only** preflight. It reports:<br>• PostgreSQL server major (=15);<br>• presence of Atlas roles, databases and the `atlas` schema;<br>• Redis reachability on DBs 10/11 and prefix configuration;<br>• the **local authentication method**, read from `pg_hba_file_rules` when the metadata session may read it, otherwise reported as *deferred*.<br>All PostgreSQL work runs in a read-only session (`SELECT`/`SHOW` only). Redis commands are limited to `PING`, `INFO`, `DBSIZE` and bounded `SCAN`. **No active authentication probe** (no wrong-password attempts; amendment A4). It never writes, and fails with remediation text (e.g. "roles not yet created — see proposals/postgres-local-setup.sql"). |
| A001-FR-36 | `specs.lock` pins an **immutable `atlas-specs` commit** (DEC-039); for ATLAS-001 the `contract-v0.1.0` release commit `bfe4a09`. `make specs` extracts `contracts/` and `tools/` **at the pinned SHA** (`git archive`) into `build/specs/`. `make contract` exports the FastAPI OpenAPI deterministically and runs the specs conformance tool. **From CP2 (amendment A5):** it runs in backend CI; operations whose implementation task has not landed are listed explicitly in `contract-pending.yaml` (CP2: only `getHealthReady`, lands in B-09) and removed from the compared contract. Every other difference fails. The list must be empty by Gate G5 (B-18). Response-body contract tests validate against the JSON Schemas at the pinned SHA. |
| A001-FR-37 | Multi-stage `Dockerfile` with `api` and `worker` targets, non-root user, `ATLAS_BUILD_SHA` build argument. CI builds both; nothing is pushed. |
| A001-FR-38 | CORS allowlist from `ATLAS_CORS_ORIGINS`. API responses carry `X-Content-Type-Options: nosniff`, `Referrer-Policy: no-referrer`, `Cache-Control: no-store`. |
| A001-FR-39 | **CI database authentication is stronger than local:**<br>• the `postgres:15` service is initialised with `POSTGRES_HOST_AUTH_METHOD=scram-sha-256` and `POSTGRES_INITDB_ARGS="--auth-local=scram-sha-256 --auth-host=scram-sha-256 --locale=C --encoding=UTF8"`;<br>• Atlas role passwords are random per run (masked in logs, never stored);<br>• an integration test marked `ci_auth` asserts that a wrong or missing password is rejected for each Atlas role. It runs when `ATLAS_EXPECT_PASSWORD_AUTH=true`, i.e. in CI. |

### 5.3 `atlas-frontend`

| ID | Requirement |
|---|---|
| A001-FR-50 | Next.js App Router, TypeScript `strict` (+ `noUncheckedIndexedAccess`), pnpm with committed lockfile. **Node 24 LTS** pinned in `.nvmrc`, `package.json` `engines` and `engine-strict`. CI uses the same version via `.nvmrc`. Layout per Tech §17.2 with `.gitkeep` in empty folders. |
| A001-FR-51 | `specs.lock` pins the same immutable commit as the backend (for ATLAS-001, the `contract-v0.1.0` release commit). `pnpm specs` extracts `contracts/` and `design/` at the pinned SHA. `pnpm gen` generates `src/generated/api/schema.d.ts` (openapi-typescript) and `src/styles/tokens.generated.css` + Tailwind theme mapping (from `tokens.json`), each with a do-not-edit header. `pnpm check:generated` fails if regeneration changes anything. |
| A001-FR-52 | `src/lib/api/transport.ts` (openapi-fetch) is the only module that knows the API base URL. It adds `X-Correlation-ID` and maps the error envelope, non-JSON responses and network failure (`NETWORK_UNAVAILABLE`, client-side code) to a typed `AtlasApiError`. |
| A001-FR-53 | `src/lib/env.ts` validates `NEXT_PUBLIC_ATLAS_API_BASE_URL` and `NEXT_PUBLIC_ATLAS_FRONTEND_SHA`, failing fast in dev and build. |
| A001-FR-54 | Root layout: `lang="en"`, skip link, `header`/`main` landmarks, global base styles from tokens (`color-scheme: light`, focus ring, reduced-motion rules, typography). |
| A001-FR-55 | `/` is an **explicit placeholder** (replaced by Home in BL-105): Atlas wordmark in text, one sentence, and exactly one interactive element, a link to `/status`. No icons, navigation or product features. |
| A001-FR-56 | `/status` (TanStack Query) shows liveness, readiness per dependency and build provenance (backend/specs/frontend SHAs, contract version, migration revision). Distinct states: **loading, ready, degraded (503), unreachable (network), diagnostics disabled (404 on build info), error (with correlation ID)**. Updates are announced through an `aria-live="polite"` region. Retry refetches. Status is conveyed by icon **and** text, never colour alone. |
| A001-FR-57 | Production build sends a CSP without `unsafe-eval`, `frame-ancestors 'none'`, `X-Content-Type-Options`, `Referrer-Policy`. No external font or asset origins (system font stack). |
| A001-FR-58 | `Dockerfile` (standalone output, non-root). CI builds it; nothing is pushed. |
| A001-FR-59 | Playwright E2E, **Chromium only**, against `next build && next start` and a real backend:<br>• status journey;<br>• keyboard-only journey;<br>• reduced-motion emulation (computed transition durations ≈ 0);<br>• axe on `/` and `/status` (0 serious/critical);<br>• `specs.lock` parity with the backend's `specs_sha`.<br>No route interception in acceptance tests. Projects are structured so adding WebKit is a one-entry change. |

## 6. Interfaces

### 6.1 Local services (existing; verified 24 Oct 2026, read-only)

| Service | Fact | Atlas use |
|---|---|---|
| PostgreSQL | Homebrew **15.12**, `localhost:5432`, server locale `C`/`C`, `password_encryption=scram-sha-256`, `pg_hba.conf` = `trust` for local/loopback | Databases `atlas_db` (local) and `atlas_test` (tests) with Atlas roles (§6.2). Shared with other projects: never modify anything outside Atlas objects |
| Redis | Container `redis` (`redis:7`, server **7.4.9**), `*:6379`, 16 DBs, no auth, DB 1 used by another project | DB **10** local, DB **11** tests, prefixes `atlas:local:` / `atlas:test:<run_id>:` |
| CI | GitHub Actions service containers `postgres:15` (`scram-sha-256` for all connections, `C` locale, FR-39) and `redis:7.4`, per job | Same role/database names and DB indexes as local, plus password authentication |

### 6.2 PostgreSQL isolation and credentials (DEC-044)

**Verification of `atlas_db` (read-only, 24 Oct 2026):**

- only schema `public`;
- 0 relations, 0 functions, 0 user types;
- only extension `plpgsql`;
- 0 large objects, 0 publications;
- no database-level role settings;
- owner: the local superuser, encoding UTF8, locale `C`;
- `tup_inserted = 0` since stats creation (never written);
- the only session was the owner's idle pgAdmin 4 connection.

**Conclusion: empty and safe to reuse.** Reuse requires only ownership and permission changes, with no drop or recreate.

#### Role model (simplified in v0.2.1: six roles → four)

| Role | Purpose | Minimum privileges (and nothing else) | Limits |
|---|---|---|---|
| `atlas_migrator` | Runs Alembic against `atlas_db`. **Owns** `atlas_db`, schema `atlas` and every migration-created object | Ownership of `atlas_db` and schema `atlas`. No `SUPERUSER`, `CREATEDB`, `CREATEROLE`, `REPLICATION`, `BYPASSRLS`. Cannot connect to `atlas_test` | 3 connections; `lock_timeout 10s` |
| `atlas_app` | Runtime identity of API and worker | `CONNECT` on `atlas_db`; `USAGE` on schema `atlas`; `SELECT` on tables by default. Write privileges only where a migration grants them per table. No `CREATE`, no `TEMP`, no other database | 10 connections; `statement_timeout 30s`; `idle_in_transaction_session_timeout 60s` |
| `atlas_test_migrator` | As `atlas_migrator`, for `atlas_test` only | As above, scoped to `atlas_test`; cannot connect to `atlas_db` | 3 connections |
| `atlas_test_app` | Runtime identity used by tests | As `atlas_app`, scoped to `atlas_test`; cannot connect to `atlas_db` | 10 connections |

The three required separations hold: runtime vs migration, and local vs test. That gives four credentials, one per role.

**Why the v0.2 owner roles were removed:** the separate `NOLOGIN` owner roles (`atlas_owner`, `atlas_test_owner`) added one benefit, rotating a migration login without transferring object ownership. That is irrelevant for local and CI databases, which can be recreated at will. The cost was a `SET ROLE` step inside Alembic, an easy place for mistakes. Both models give the runtime role exactly the same privileges, so the simplification removes no protection. A production role model is decided separately, with DEC-086 and DEC-030.

**Defaults tightened:** v0.2 granted the runtime role DML on every future table by default. v0.2.1 grants **read-only by default**; writes are granted per table in reviewed migrations. This keeps later append-only tables (e.g. the audit store, BL-118) from receiving `UPDATE`/`DELETE` by accident.

`PUBLIC` loses `CONNECT`/`TEMP` on both Atlas databases and all privileges on schema `public` in them. Passwords use SCRAM and come from environment variables at execution time, never committed. The exact SQL, its verification queries and a rollback are in `proposals/postgres-local-setup.sql` (**not applied**).

**Dry-run evidence (24 Oct 2026, disposable `postgres:15-alpine` containers; no host port; removed afterwards; the Homebrew server untouched):**

- Guards: missing password, non-empty `atlas_db` and a re-run each exit 3 with zero changes.
- Roles: 4 created, all elevated flags false.
- Migrator owns `alembic_version` and test tables; it cannot create databases or roles.
- Runtime role: reads `alembic_version`; `INSERT` denied without a grant and allowed with an explicit per-table grant; `UPDATE` denied when not granted; DDL denied; `TEMP` denied; cross-environment connection denied.
- Rollback restores the prior state. The database ACL becomes the explicit equivalent of the default.

#### Authentication: local limitation vs CI (DEC-084)

| | Local (owner's Homebrew server) | CI (`postgres:15` service) |
|---|---|---|
| Method | `trust` for local socket and loopback (all users) | `scram-sha-256` for socket and host (FR-39) |
| Effect | Passwords are **not verified**. Anyone with local access can connect as any role, including Atlas roles | Wrong or missing passwords are rejected (verified in dry run) |
| What still protects | Role privileges (what each role may do); settings guards (FR-21) | Authentication **and** privileges |
| Visibility | `make doctor` warns when trust is detected | `ci_auth` test fails if passwords are not enforced |

**Shared-server finding:** PostgreSQL's default `CONNECT` grant to `PUBLIC` on other databases means Atlas roles *can connect to other projects' databases* on this server (verified: `atlas_app` → `postgres`). They gain only what those databases grant to `PUBLIC`. Atlas will not modify other databases to fix this.

**Optional, owner-decided hardening:** `proposals/pg_hba-atlas.conf` adds six lines that apply **only to the four Atlas roles**:

- passwords are enforced (`scram-sha-256`);
- Atlas roles are **rejected on every non-Atlas database**;
- every other user's behaviour is unchanged.

Validated in a disposable container. Not applied.

### 6.3 Configuration (backend)

| Variable | Local example (`.env`) | Test example (`.env.test`) |
|---|---|---|
| `ATLAS_ENV` | `local` | `test` |
| `ATLAS_DATABASE_URL` (runtime) | `postgresql+psycopg://atlas_app@localhost:5432/atlas_db` | `…atlas_test_app@localhost:5432/atlas_test` |
| `ATLAS_MIGRATION_DATABASE_URL` | `…atlas_migrator@…/atlas_db` | `…atlas_test_migrator@…/atlas_test` |
| `ATLAS_DB_APP_ROLE` (grantee for per-table grants in migrations) | `atlas_app` | `atlas_test_app` |
| `ATLAS_REDIS_URL` | `redis://localhost:6379/10` | `redis://localhost:6379/11` |
| `ATLAS_REDIS_KEY_PREFIX` | `atlas:local:` | `atlas:test:` (+ `<run_id>:` appended per test session) |
| `ATLAS_CORS_ORIGINS` | `http://localhost:3000` | `http://localhost:3000` |
| `ATLAS_DIAGNOSTICS_ENABLED` | `true` | `true` |
| `ATLAS_BUILD_SHA`, `ATLAS_LOG_LEVEL` | optional | optional |

Ports: API 8000, web 3000. The env files are git-ignored; only `.env.example`/`.env.test.example` with placeholders are committed.

### 6.4 `specs.lock`

```yaml
specs_repo: atlas-specs
specs_commit: "<40-hex SHA>"
api_contract: contracts/openapi/atlas-api.yaml
schemas_dir: contracts/schemas
tokens: design/tokens.json
contract_version: "0.1.0"
```

Rules (DEC-039 as approved):

- `specs_commit` is a **full 40-hex SHA of a reviewed commit on `atlas-specs` `main`**. Never a branch or tag name. Development and CI may pin any such commit.
- **Release tags `contract-vX.Y.Z` are created only for approved contract releases**, not for each API change. An approved release requires owner approval of the contract diff since the previous release.
- **Release builds** (backend/frontend version tags such as `v0.1.0`) must pin a commit that carries a `contract-v*` release tag. The G7 gate checks this.
- Between releases, `info.version` carries the next version with a pre-release suffix (e.g. `0.2.0-dev.3`), defined in `contracts/compatibility.md`. `contract_version` in the lock must equal `info.version` at the pinned SHA.
- The breaking-change check compares against the **latest release tag**.
- Files are read at the pinned SHA via `git archive`/`git show` from a sibling clone (`ATLAS_SPECS_DIR`, default `../atlas-specs`) or a CI checkout at that SHA.

### 6.5 Contract 0.1.0 operations

| operationId | Method and path | Responses |
|---|---|---|
| `getHealthLive` | `GET /api/v1/health/live` | 200 `HealthLive` · 500 `ErrorEnvelope` |
| `getHealthReady` | `GET /api/v1/health/ready` | 200 `HealthReady` · 503 `ErrorEnvelope` · 500 |
| `getDiagnosticsBuild` | `GET /api/v1/diagnostics/build` | 200 `BuildInfo` · 404 `ErrorEnvelope` · 500 |

- `HealthReady` = `{status, checks:{database, redis}}`.
- `BuildInfo` = `{backend_sha, specs_sha, contract_version, db_migration_revision|null, environment}`.
- Every response declares the `X-Correlation-ID` header.

### 6.6 Error envelope and codes

Envelope per Tech §6.3. Codes in 0.1.0:

- **In use:** `NOT_FOUND`, `VALIDATION_FAILED`, `DEPENDENCY_UNAVAILABLE`, `INTERNAL_ERROR`.
- **Reserved:** `REVISION_CONFLICT`, `IDEMPOTENCY_KEY_REQUIRED`, `RATE_LIMITED`.

The catalog is append-only.

### 6.7 Contract conformance method (DEC-095)

Input **C** is the contract at the pinned SHA. Input **A** is FastAPI's `app.openapi()`, exported deterministically under `ATLAS_ENV=test`. Since the schema is identical in all environments (FR-22), the export environment does not change the result.

| Step | What it does | Detects |
|---|---|---|
| 1. Validity | Redocly lint of C (specs CI) and A (backend CI) as OpenAPI 3.1 | Malformed documents |
| 2. **Operation inventory** | Compares sets of `(METHOD, path-template)` and the `operationId` per operation | **Missing operations** (in C, not A) → `MISSING_OPERATION`; **unexpected operations** (in A, not C) → `UNEXPECTED_OPERATION`; `OPERATION_ID_MISMATCH`. Each is listed explicitly by name |
| 3. Normalize C and A identically | Strip `title`, `description`, `summary`, `example(s)`, `externalDocs`, `tags`, `servers`, `info` except `version`. Canonicalize nullable to `anyOf[...,{type:null}]`. Sort keys, `required`, `enum`, and parameters by `(in, name)` | Removes the cosmetic noise observed in review-01 (Pydantic titles) |
| 4. **Exact structural diff** | `oasdiff diff --fail-on-diff` on normalized C vs A | Any remaining difference in either direction: parameters, request bodies, status codes, response headers, schemas, components (e.g. an injected `HTTPValidationError`), added optional properties |
| 5. Versioning (specs CI only) | `oasdiff breaking <previous tag> <current> --fail-on ERR` unless the major version is bumped | Unannounced breaking changes in the contract itself |

Why not `oasdiff breaking` in both directions (v0.1 FD-08): the review-01 probe showed it does not report an operation present in code but absent from the contract. Step 2 makes both missing and unexpected operations explicit. Step 4 catches every other difference.

The tool lives in `atlas-specs/tools/` and is versioned with the contract, so the checker and the contract come from the same pinned SHA. oasdiff runs from a container image pinned by digest; there is no host install.

### 6.8 Repository visibility — security decision (DEC-085, decided: PUBLIC)

**Owner decision (24 Oct 2026):** `Kibana21/atlas-specs`, `Kibana21/atlas-backend` and `Kibana21/atlas-frontend` **remain public**. This is the approved configuration. The earlier recommendation (private) is superseded. Engineering never changes visibility.

**Consequences adopted:**

- CI uses **Mode A** (`ci-access.md` §3): public cross-repository checkout, read-only, pinned to immutable SHAs, minimal `GITHUB_TOKEN` permissions. No GitHub App, no personal access tokens, no repository secrets for cross-repository reads.
- Rulesets/branch protection remain available on public repositories (P-07, before G7).

**Public-repository safety rules (mandatory for every change):**

| Rule | Applies to |
|---|---|
| No secrets, credentials, tokens, keys or connection strings with passwords | Files, fixtures, logs, commit messages, Git history |
| No confidential enterprise architecture information: no real system inventories, internal network topology, hostnames or IP ranges, customer information or proprietary company documents | All content; fixtures are synthetic |
| No unnecessary personal or local-environment details (local usernames, other projects' names, home-directory paths) | Documentation and evidence |
| Every push is preceded by a staged-diff review: secret patterns, local identifiers, IPs/hostnames, credential-like strings. The result is recorded in `evidence.md` | Every push |
| CI never prints secrets (none exist in Mode A). Generated CI passwords (from CP5) are masked | Workflows |

## 7. Design foundation (bright Atlas language, no product UI)

All values are **proposed (DEC-065)**. They extend Tech §5.3 and UX §2.1 with text-safe variants. Contrast ratios below were computed on 24 Oct 2026.

### 7.1 Tokens (`design/tokens.json`)

| Group | Tokens |
|---|---|
| Surfaces | `surface-app #FFFFFF`, `surface-canvas #F8FAFE`, `surface-subtle #F0F5FC`, `surface-raised #FFFFFF` (with elevation) |
| Ink | `ink-primary #15283F` (≥13.6:1 on all surfaces), `ink-secondary #4A5B70` (≥6.3), `ink-muted #5F6E82` (≥4.75), `ink-inverse #FFFFFF` |
| Lines | `border-subtle #C9D4E3` (decorative only; never the sole boundary of a control), `border-strong #7A8AA0` (≥3.2:1, for component boundaries) |
| Brand / focus | `brand-primary #1769E0` (≥4.64 on all surfaces; white on it 5.08), `brand-primary-hover #1257BE` (≥6.1), `focus-ring #1769E0` |
| Entity accents (fills, borders, icons only; ≥3:1) | application `#5A54D6`, api `#1674E8`, compute `#8C58D8`, messaging `#C47B13`, data `#087F8C`, security `#BD4D76`, capability `#22865E` |
| Entity text (≥4.5:1 on all surfaces and on their own 10% tint) | application `#5A54D6`, api `#146BD5`, compute `#8453CB`, messaging `#9D620F`, data `#087784`, security `#B2486F`, capability `#1F7B56` |
| Entity tints (10% over white) | application `#EEEEFB`, api `#E8F1FD`, compute `#F4EEFB`, messaging `#F9F2E7`, data `#E6F2F4`, security `#F8EDF1`, capability `#E9F3EF` |
| Status (with icon + text) | success `#1B7A4E`, warning `#8F5A0E`, danger `#B42318`, info `#1257BE` (each ≥4.6:1 on surfaces and own tint) |
| Typography | system sans stack (`ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif`), mono stack. Sizes 12 / 14 / 16 / 20 / 24 / 32 px. Weights 400 / 500 / 600. Line-height 1.25 headings, 1.4 UI, 1.5 body |
| Relationships *(Amendment A2)* | `relationship-default #5F6E82` (neutral slate), `relationship-selected #1769E0`, `relationship-muted #7A8AA0`; all ≥ 3:1 on every surface; line widths 1.5 px default / 2.5 px selected. Category accents reuse entity accents |
| Spacing | 4-px scale: 0, 4, 8, 12, 16, 24, 32, 48, 64 |
| Sizing *(Amendment A2)* | controls 24 / 32 / 40 px (24 px = minimum target, AR-07); icons 16 / 20 / 24 px; border widths 1 / 2 px; focus ring 2 px width, 2 px offset |
| Radius | 4, 8, 12, full |
| Elevation | three subtle ink-tinted shadows (`rgba(21,40,63,.08/.10/.14)`) |
| Motion | `duration-fast 120ms`, `duration-base 160ms`, `duration-slow 220ms`; `easing-standard cubic-bezier(0.2,0,0,1)`, `easing-exit cubic-bezier(0.4,0,1,1)` |

Trust/evidence state tokens are **not** defined, because they depend on DEC-056 (Open).

**Known limitation (E-04, accepted provisionally):** `api` text on its own 10% tint (`#146BD5` on `#E8F1FD`) is exactly **4.50:1**, meeting AA with zero margin. The value is retained and recorded under DEC-065 for reassessment at final palette approval. `tools/check_tokens.py` keeps enforcing ≥ 4.5:1, so any drift fails CI.

### 7.2 Accessibility rules (`design/tokens.md`, enforced in UI tests)

| ID | Rule (WCAG 2.2 AA target) |
|---|---|
| AR-01 | Text contrast ≥ 4.5:1; large text (≥ 24 px, or ≥ 18.66 px bold) ≥ 3:1 (1.4.3) |
| AR-02 | Non-text contrast ≥ 3:1 for control boundaries, focus indicators and meaningful icons (1.4.11) |
| AR-03 | Entity accent colours never colour text. Text in an entity hue uses its `-text` token |
| AR-04 | Colour is never the only carrier of meaning. Status = icon + text (1.4.1) |
| AR-05 | Visible focus on every interactive element (2.4.7). House rule: 2 px solid `focus-ring` with 2 px offset, ≥ 3:1 against adjacent colours. Never `outline: none` without a replacement. Focus never obscured (2.4.11) |
| AR-06 | All functionality keyboard operable, logical order, no traps, skip link to `main` (2.1.1, 2.1.2, 2.4.1) |
| AR-07 | Target size ≥ 24 × 24 CSS px (2.5.8) |
| AR-08 | Semantics: `lang`, one `h1` per page, landmarks, native `<button>`/`<a>`, live region for asynchronous status (4.1.3) |
| AR-09 | Text sizing: minimum 12 px (captions/metadata), 14 px default UI, 16 px long-form. Layout survives 200% zoom and text-spacing overrides; simple pages reflow to 320 CSS px (1.4.4, 1.4.10, 1.4.12) |
| AR-10 | **Light only:** `color-scheme: light`; no dark-mode media rules until a dark theme is approved. Under `forced-colors: active`, focus and status icons stay visible |

### 7.3 Motion and reduced motion

- Transitions use the motion tokens only, on opacity, colour and shadow. No layout-shifting animation in ATLAS-001.
- Under `prefers-reduced-motion: reduce`, all transition and animation durations become `0.01ms`, transforms are removed, and smooth scrolling is disabled.
- No auto-playing animation longer than 5 s (2.2.2), and nothing flashes (2.3.1).
- Verified by E2E reduced-motion emulation (FR-59).

## 8. Local development commands

| Repo | Command | Effect |
|---|---|---|
| specs | `make check` | Every specs CI step locally. markdownlint, Redocly and oasdiff run via digest-pinned containers; Python tools via uv |
| backend | `make setup` | `uv sync --locked`; copy env examples if absent |
| backend | `make doctor` | Read-only preflight of existing PostgreSQL/Redis and Atlas isolation |
| backend | `make migrate` | Alembic upgrade on `atlas_db` as `atlas_migrator` |
| backend | `make api` / `make worker` | API on :8000 / Taskiq worker |
| backend | `make worker-smoke` | Enqueue ping on DB 10, await marker, delete its own keys |
| backend | `make check` / `make test-integration` / `make contract` | Static + unit / integration (uses `.env.test`) / conformance |
| frontend | `pnpm install` · `pnpm dev` · `pnpm gen` · `pnpm check` · `pnpm e2e` | Install / dev on :3000 / regenerate / static + unit + generated check / Chromium E2E against a running backend |

**Smoke journey:**

1. `make doctor` green.
2. `make migrate`, then `make api` and `make worker`.
3. `make worker-smoke` OK.
4. `pnpm dev`, then open `/status`: all checks green and SHAs shown.

## 9. Non-functional requirements

| ID | Requirement |
|---|---|
| A001-NFR-01 | Reproducible from READMEs on a clean clone. Lockfiles enforced (`uv sync --locked`, `pnpm install --frozen-lockfile`) |
| A001-NFR-02 | Each CI pipeline ≤ 15 min. Local check timings recorded, informational (DEC-054 Open) |
| A001-NFR-03 | Ruff (lint + format), mypy strict, TypeScript strict, ESLint `--max-warnings 0` |
| A001-NFR-04 | Coverage: backend ≥ 85% (unit + integration); frontend `src/lib` + status ≥ 80%. Enforced from the first code task |
| A001-NFR-05 | Security baseline: secret scanning; `pip-audit`/`pnpm audit --prod` fail on high/critical; Ruff `S`; non-root containers; no internals in errors or logs; workflow `permissions: contents: read`; third-party actions pinned by commit SHA; no `pull_request_target` |
| A001-NFR-06 | Shared-service safety: no Atlas test or command changes any PostgreSQL object outside Atlas databases/roles, or any Redis key outside its own prefix, and never stops or reconfigures shared services |
| A001-NFR-07 | Accessibility per §7.2; axe 0 serious/critical on `/` and `/status` |
| A001-NFR-08 | Atlas-only observability (logs). No telemetry SDKs or enterprise telemetry ingestion |

## 10. Traceability

| ATLAS-001 | Satisfies / enables |
|---|---|
| FR-01…07, FR-36, FR-51 | Tech §17.4 contract-first, §17.7 drift safeguards; DEC-039, DEC-095; BL-013, BL-021 |
| FR-08, FR-54…57, §7 | UX §1.2(3,10), §2.1–2.2, §12, UX-GLB-007, UX-NFR-008; Tech §5.3; DEC-011, DEC-065 (proposed values); BL-024 |
| FR-20…27, FR-38 | Tech §6, §6.3, §9.3, §15, §17.1, §17.4(7); BL-103, BL-126; NFR-06/12 (BRD §8, proposed IDs) |
| FR-28…30, FR-39 | Tech §3.5 hardening, §9.3 least privilege, §17.7 expand/migrate/contract; DEC-043, DEC-044, DEC-084 |
| FR-31…35 | Tech §8 (seam only); DEC-028 (narrowed), DEC-045, DEC-046 |
| FR-37, FR-58 | Tech §17.5 release outputs, §17.7 one-commit images |
| FR-59, NFR-03/04 | Tech §17.5, §20.3; BRD EXP-02, US-08 (foundation part); UX-NFR-011 (Chromium; second engine pending DEC-055); BL-122 |
| Tech §17.8 #1–#6 | AC-01, AC-02, AC-03, AC-05, AC-03, AC-15 (see `acceptance.md`). #3's authorization half is deferred to BL-104 |

## 11. Remaining risks (summary; details in `plan.md` §6)

- The Taskiq library may write Redis keys that cannot be fully prefixed. Mitigation: the round-trip test tracks and deletes exact keys, the session guard fails if anything else appears (FR-33), and the stop-and-escalate rule applies (`plan.md` §2.5).
- Local `trust` authentication means credentials are not verified locally, and Atlas roles can reach other projects' databases that grant `CONNECT` to `PUBLIC` (§6.2). Mitigations: role privileges, settings guards, a `make doctor` warning, CI password enforcement, and the optional Atlas-only `pg_hba` hardening (owner decision DEC-084).
- Repositories are public until you decide otherwise (DEC-085, recommendation private).
- Locale `C` locally; CI matches. Search behaviour is decided later (DEC-083).

## 12. Approval gate (stop point)

Implementation of CP1 starts only when **all** of these hold:

1. You explicitly approve this final specification set (spec v0.2.1, `plan.md`, `tasks.md`, `acceptance.md`).
2. The CP1 preconditions in `readiness.md` §3 are confirmed: P-05 pinned container images, P-08 branch/PR workflow, and P-06 the visibility decision, or an explicit "keep public for now".

Later checkpoints have their own preconditions (P-03 SQL before CP3, P-04 Node 24 before CP6, P-07 ruleset before G7).

ATLAS-001 is **not Accepted** by this document. It becomes Accepted only through the signed sign-off in `acceptance.md` / `evidence.md` (G7). *Update 24 Oct 2026: the owner accepted ATLAS-001 at G7 (`evidence.md` §13.11).*

## 13. Revision record

| Version | Date | Change |
|---|---|---|
| 0.2.3 | 2026-10-24 | **Status only: Accepted** by the owner at Gate G7 (`evidence.md` §13.11), subject to the recorded deviations and `follow-ups.md`. No content change |
| 0.1 | 2026-10-24 | Initial draft |
| 0.2 | 2026-10-24 | Revised per review-01 and owner decisions D-01…D-06; see `changes-v0.2.md` |
| 0.2.3 | 2026-10-24 | **Controlled amendment (owner-approved CP2 authorization):**<br>• **A4** doctor performs no active authentication probe; auth method read-only from `pg_hba_file_rules` or deferred (FR-35);<br>• **A5** backend `static`/`unit`/`contract`/`security` CI moved from CP5 into CP2 (new tasks B-27, B-28; FR-36 explicit pending-operation list);<br>• **A6** CI triggers `pull_request` + `push` to `main` in all repos, so required checks are never satisfied by skipped jobs (E-08) |
| 0.2.2 | 2026-10-24 | **Controlled amendment** (owner-approved E-01, E-03, E-04; no change to BRD, UX or Technical Design baselines):<br>• **A1** FR-02 health schemas split into `health-live.v1` and `health-ready.v1`;<br>• **A2** relationship-colour and sizing tokens added to §7.1;<br>• **A3** `api` text-on-tint 4.50:1 limitation recorded (DEC-065).<br>Approval status of v0.2.1 carries over to v0.2.2 for these amendments only |
| 0.2.1 | 2026-10-24 | **Approved for Implementation** by the owner (CP1 authorized; repositories remain public by owner decision DEC-085). Final candidate content: D-07 applied; roles simplified (6 → 4) and runtime default narrowed to read-only; local-trust limitation and CI scram enforcement specified; shared-server cross-database finding and optional `pg_hba` hardening; contract pinning/release-tag rules; repository-visibility security analysis; CP1 tooling via pinned containers; see `changes-v0.2.md` §8 |
