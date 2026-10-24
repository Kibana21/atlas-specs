# ATLAS-001 — v0.2 Change Summary, D-07 Briefing and Remaining Blockers

**Date:** 24 October 2026 · **Applies to:** `spec.md`, `plan.md`, `tasks.md`, `acceptance.md` (v0.1 → v0.2), plus new `ci-access.md`, `proposals/postgres-local-setup.sql` and `decisions/decision-register.md` v0.2 · **Status:** for owner review. ATLAS-001 is **not Accepted**, and nothing in `atlas-backend`, `atlas-frontend` or the shared services was changed.

---

## 1. What changed and why

| # | Change | Driven by |
|---|---|---|
| 1 | **PostgreSQL 15** for local and CI everywhere; production major split into Open DEC-086 | D-01 → DEC-043; review C-01 |
| 2 | Local development uses the **existing** PostgreSQL and Redis. `compose.yaml` removed from the local path; CI uses isolated service containers | Owner direction; D-02/D-03 |
| 3 | `atlas_db` **verified empty** (read-only). Exact SQL proposed: six least-privilege roles, separate runtime/migration/test credentials, schema `atlas`, `PUBLIC` revoked, guarded, with rollback. **Dry-run tested in a disposable container; not applied** | D-02 → DEC-044 |
| 4 | Redis: DB 10 local, 11 test, Atlas prefixes. No `FLUSHALL`/`FLUSHDB`. Exact-key cleanup with a session guard. Static ban on dangerous commands. Shared services never stopped | D-03 → DEC-045; review C-02 |
| 5 | Outbox, durable job tables, retries and job endpoints removed. Taskiq seam = broker + worker + ping round-trip test. Migrations = reviewed empty `0001_baseline`. The contract shrinks to 3 operations | D-04 → DEC-046; review M-01 |
| 6 | GitHub Actions access model documented: Mode A (public repos; no credentials) and Mode B (GitHub App installation tokens). No PATs. Nothing created | D-05 → DEC-047; review M-06 |
| 7 | Node.js **24 LTS** pinned (`.nvmrc`, `engines`, `engine-strict`, CI from `.nvmrc`) | D-06 → DEC-048; review M-05 |
| 8 | Conformance rewritten: lint → **operation inventory** (explicit `MISSING_OPERATION` / `UNEXPECTED_OPERATION` / `OPERATION_ID_MISMATCH`) → normalization → `oasdiff diff --fail-on-diff` → breaking check in specs. The tool lives in `atlas-specs/tools` and is versioned with the contract. FastAPI-side rules specified | Requirement 5; review C-03 |
| 9 | Complete bright design foundation: full token set, text-safe entity variants and a 3:1 border, computed contrast, accessibility rules AR-01…AR-10, reduced motion, light-only, tokens generated from `atlas-specs` | Requirement 3; review M-03 |
| 10 | Chromium-only E2E; screenshot baselines and WebKit deferred | Requirement 4; review M-04 |
| 11 | Every task is single-repository and self-verifying; 7 checkpoints with gates; owner actions moved to preconditions | Requirements 1–2; review M-02 |
| 12 | Markdownlint excludes `brd/`, `ux/`, `technical/`; baselines are never edited for lint | Requirement 6 |
| 13 | Decision status split into **Approved / Pending (D-07) / Provisional / Unresolved** throughout | Requirement 8 |
| 14 | Tasks reduced from 108 to 53 (§4) | Requirement 9 |
| 15 | New AC-07 (credential separation and least privilege). v0.1 AC-12 (outbox) and AC-17 (visual) deferred with their features | Consequence of 3, 5, 10 |

Product exclusions are unchanged (requirement 7): no PR analysis, telemetry, tracing, provisioning or AI. AC-17 guards them, and the four documents contain no such capability.

## 2. ID mapping v0.1 → v0.2

| v0.1 | v0.2 |
|---|---|
| FR-01…06 (specs) | FR-01…09 (adds style guide, conformance tool, tokens, registry tool) |
| FR-10…30 (backend) | FR-20…38. Removed: job/outbox FRs (old 20, 23–26) |
| FR-40…49 (frontend) | FR-50…59 (adds generated tokens, accessibility shell, Chromium E2E) |
| AC-01…11, 13…16, 18 | AC-01…06, 08…17 (renumbered; see `acceptance.md` table) |
| AC-12 outbox, AC-17 visual | Deferred (BL-201; first real screen) |
| — | **AC-07 new** (least privilege) |
| Tasks `A001-T-<M>-<nn>` | Tasks `S-nn`, `B-nn`, `F-nn` (repo letter = the only repo touched) |

## 3. D-07 — exact current wording and implications (approval requested; not approved)

The quoted text is the current register row. **Requested scope** is what ATLAS-001 needs approved; anything outside it stays *Proposed*.

### DEC-020 — Backend language and framework
> *"Python 3.12+ (pinned patch), FastAPI, Pydantic v2, SQLAlchemy 2, Alembic (tech §0; specs README; backend `.gitignore`)"* · Owner (proposed): Backend lead + Security · Needed by: P0 · Blocks: all backend work

- **Requested scope:** approve as written. ATLAS-001 uses Python **3.12** (patch locked by uv; 3.12.12 already available locally), FastAPI, Pydantic v2, SQLAlchemy 2 (async, psycopg 3) and Alembic.
- **Implications if approved:**
  - Fixes the backend language and framework for Atlas, not only ATLAS-001.
  - Python 3.12 receives upstream security fixes until October 2028, so a later minor upgrade is expected within the product's life.
  - The register lists Security as co-owner. Approving now means you approve in place of not-yet-named owners (DEC-081).
- **If not approved:** CP2–CP5 cannot start, and the Tech Design §0, §17.1 backend design would need to be redone.

### DEC-024 — Frontend framework and libraries
> *"Next.js App Router, TypeScript strict, Tailwind, shadcn/ui, TanStack Query, Zustand (tech §5.1)"* · Alternative noted: enterprise-approved component kit instead of shadcn/ui · Needed by: P0 · Blocks: BL-105

- **Requested scope (narrower than the wording):** approve **Next.js App Router, TypeScript strict, Tailwind and TanStack Query**. Leave **shadcn/ui and Zustand Proposed** until Phase 1 (BL-105/BL-109) needs them.
- **Implications if approved:**
  - Commits the App Router conventions (server/client components).
  - Tailwind's theme is generated from `design/tokens.json`, so token changes flow through `atlas-specs`.
  - TanStack Query becomes the server-state standard.
  - The component-kit decision stays open, which avoids premature product UI.
- **If not approved:** CP6–CP7 cannot start.

### DEC-028 — Background jobs
> *"Taskiq + Redis dispatch, PostgreSQL durable job records + outbox (tech ADR-005, §8)"* · Alternatives noted: Celery, Arq, Dramatiq · Needed by: P1 (needed P2 at scale) · Blocks: BL-201

- **Requested scope (narrowed by DEC-046):** approve **Taskiq + Redis as the dispatch mechanism** only. "PostgreSQL durable job records + outbox" stays Proposed until BL-201.
- **Implications if approved:**
  - Taskiq is async-native and fits FastAPI, but its ecosystem is smaller than Celery's. If BL-201 finds gaps in acknowledgement or retry semantics, a switch is cheaper now, since ATLAS-001 ships one diagnostic task.
  - Production would use Azure Managed Redis (DEC-030 Proposed).
  - Redis server licensing changed from 7.4 onwards. Atlas only *consumes* Redis as a service (local container now, managed service later); this is flagged for the platform team's awareness, not as a blocker.
- **If not approved:** CP4 cannot start. The migration mechanism (CP3) is unaffected.

### DEC-038 — Tooling
> *"Backend: `uv`, Ruff, mypy or pyright (strict), pytest, Hypothesis. Frontend: pnpm, ESLint, Vitest, Playwright. Typed client generator TBD (tech §17.1, §17.5)"* · Alternatives noted: Poetry; pyright vs mypy; npm/yarn; client generators · Needed by: P0

- **Requested scope:** approve **uv, Ruff, pytest, pnpm, ESLint, Vitest and Playwright**. The two open choices inside the wording are taken as **Provisional**: DEC-091 = mypy, DEC-092 = openapi-typescript + openapi-fetch. You may override them without blocking. Hypothesis is not used in ATLAS-001 (no property-based targets remain once retries are deferred) and stays in the approved set for later.
- **Implications if approved:**
  - Locks the developer toolchain. Lint and test tools can be swapped cheaply later; package managers (uv, pnpm) can't.
  - pnpm's version is pinned via `packageManager`; 11.5.2 is installed locally.
- **If not approved:** no repository bootstrap (B-01, F-01).

### DEC-039 — Contract-first workflow
> *"OpenAPI + JSON Schema in `atlas-specs`, consumers pin a commit SHA in `specs.lock`, frontend client generated from the pinned contract, CI compares emitted OpenAPI (tech §17.4)"* · Owner (proposed): Architecture + release coordinator · Needed by: P0

- **Requested scope:** approve as written. "CI compares emitted OpenAPI" is made concrete by Provisional DEC-095 (inventory + normalized exact diff).
- **Implications if approved:**
  - Every API change starts as a reviewed `atlas-specs` PR and tag before backend or frontend changes. That's a small per-change overhead in exchange for drift protection.
  - Backend ships first for additive changes.
  - Breaking changes need a new major version or parallel paths.
  - A release coordinator role is implied. You hold it until DEC-081 names someone.
- **If not approved:** the alternative is code-first (backend exports the schema into specs). That contradicts Tech §17.4 and weakens AC-02/AC-03. Large rework of CP1/CP5.

### DEC-040 — `atlas-specs` folder layout
> *"Align to tech §17.3 or update §17.3 to match the repo. **Recommendation:** keep the current `contracts/openapi`, `contracts/schemas`, `acceptance/scenarios`, `acceptance/test-data`, `decisions/` and add `contracts/examples/`, `contracts/compatibility.md`, `design/tokens.md`, `phase0/`; amend tech §17.3 at its next revision"* · Needed by: P0

- **Requested scope:** approve the layout. ATLAS-001 adds:
  - `contracts/examples/`, `contracts/conventions.md`, `contracts/style-guide.md`, `contracts/compatibility.md`;
  - `design/tokens.json` + `design/tokens.md`;
  - `tools/`, `features/`.
  **No Technical Design edit now** (requirement 6). The §17.3 amendment waits for the next Tech revision, approved separately.
- **Implications if approved:**
  - Tech §17.3 and the repo diverge until that revision. This is documented, not hidden.
  - `tools/` is CI tooling in a specs repo. It is allowed by the spec §4 boundary, and it is not product code.
- **If not approved:** CP1 file locations change. Low rework.

## 4. Task count: 108 → 53

| Category | Effect | Why quality is not weakened |
|---|---|---|
| Owner actions (approval, register, ADR, credentials, CODEOWNERS/protection) | 6 tasks → 7 **preconditions** (P-01…P-07) | Still tracked and evidenced, but not counted as engineering work |
| Deferred scope (outbox, job tables, relay, retries, job endpoints, Redis-loss test, job schema, compose, visual baselines) | ≈ 11 removed | Owner-approved deferrals (DEC-046, M-04). BL-201 is a hard prerequisite of the first business job |
| Configuration steps sharing one verification (Ruff/mypy/pytest; scaffold/TS/ESLint; lint configs; schemas+examples; contract operations; CI jobs) | ≈ 48 merged into ≈ 20 | Each merged task still has one decisive command (e.g. `make check`), and failure isolation is preserved inside CI by separate jobs |
| Drills (breaking-change, parity, coverage, fake secret) | Moved from tasks into acceptance verification | Drills are now mandatory evidence in the AC they prove |
| **New** in v0.2 | +11: tokens (S-05), token checker (S-08), doctor (B-08), least-privilege tests (B-12), key-hygiene round trip (B-15), Redis safety ban (B-16), worker smoke (B-17), CI bootstrap SQL (B-22), generated tokens (F-04), per-repo release tags (B-26, F-14) | Covers v0.2 requirements: isolation, least privilege, design foundation, single-repo release steps |

Every v0.1 acceptance criterion that is still in scope maps to a v0.2 criterion (§2), and one criterion was added.

## 5. Evidence gathered for v0.2 (read-only, or a disposable sandbox)

| Check | Result |
|---|---|
| PostgreSQL | 15.12 Homebrew, locale `C`, `scram-sha-256` password encryption, `pg_hba.conf` `trust`; current role is a superuser; no `atlas_*` roles; no `atlas_test` |
| `atlas_db` | Empty: schema `public` only, 0 relations/functions/types, `plpgsql` only, 0 large objects, no role settings, `tup_inserted 0`; one idle pgAdmin 4 session (owner) |
| Redis | 7.4.9 in container `redis`, 16 DBs, DB 1 holds 3 keys from another user, no auth, AOF off |
| GitHub | All three repos public (unauthenticated API 200); no workflows |
| SQL dry run | Disposable `postgres:15-alpine` container (existing image, no host port, removed after). Found and fixed a guard bug: psql `\quit` ignores exit codes, so guards now raise exceptions. Then all guards, privileges, `SET ROLE` ownership, timeouts and rollback were verified |
| Contrast | All token pairs computed (spec §7.1). Entity base colours below 4.5:1 on canvas/subtle surfaces received text-safe variants; `border-strong` was darkened to reach ≥ 3:1 |
| Toolchain | uv 0.10.0; Python 3.12.12 available via uv; Node v25.2.1 (needs 24 LTS, P-04); pnpm 11.5.2; Docker 27.4; no `redis-cli` on host (verification uses a project script instead) |

## 6. Remaining blockers

### Genuine blockers (owner action required)

| # | Blocker | Blocks | Owner action |
|---|---|---|---|
| 1 | **D-07 approval** (§3) | All implementation | Approve the requested scopes or override |
| 2 | **Approval of v0.2 documents** (P-01) | All implementation | Review spec/plan/tasks/acceptance v0.2 |
| 3 | **PostgreSQL setup SQL** reviewed and applied (P-03) | CP3 → CP5, CP7 | Review `proposals/postgres-local-setup.sql`; run it yourself, or authorize Claude to run it |
| 4 | **Node.js 24 LTS** available locally (P-04) | CP6, CP7 | Install it, or authorize a method (e.g. `pnpm env use --global 24`, or a version manager) |
| 5 | **Pinned oasdiff container image** may be pulled for local runs (P-05) | Local S-07/B-19 runs (CI unaffected) | Permit or refuse. If refused, local conformance runs only in CI |

### Conditional

| # | Item | When it blocks |
|---|---|---|
| 6 | Repo visibility intent (DEC-085). If any repo becomes private, create the GitHub App (`ci-access.md` §4) | Before the first cross-repo CI job (B-24, F-11, F-12) |
| 7 | Apply the `main` ruleset with required checks (P-07) | G7 sign-off only |

### Unresolved but not blocking ATLAS-001

DEC-055 (second browser) · DEC-065 (palette approval; tokens stay *proposed*) · DEC-083 (DB locale/collation, before BL-101/BL-111) · DEC-084 (local `trust` auth; your server) · DEC-086 (production PostgreSQL major, before the first deployed environment) · DEC-081 (named owners; CODEOWNERS = `@Kibana21` meanwhile).

## 7. Files in this revision

| File | Change |
|---|---|
| `spec.md`, `plan.md`, `tasks.md`, `acceptance.md` | Rewritten to v0.2 |
| `changes-v0.2.md` | New (this file) |
| `ci-access.md` | New |
| `proposals/postgres-local-setup.sql` | New. **Proposal only, not applied** |
| `review-01.md` | Unchanged (history) |
| `../../decisions/decision-register.md` | v0.2: DEC-043…048 approved; DEC-021/028 narrowed; DEC-083…086 Open; DEC-090…099 Provisional; status "Provisional" defined |

---

## 8. v0.2.1 addendum (final candidate)

| # | Change | Driven by |
|---|---|---|
| 1 | D-07 applied: DEC-020 (Python 3.12 + dependency pinning policy FR-20a), DEC-024, DEC-028, DEC-038 (mypy, openapi-typescript), DEC-039 (immutable-SHA pinning; tags only for approved releases; release builds pin a tagged commit), DEC-040 (layout; deviation TD-DEV-001) | Owner D-07 |
| 2 | PostgreSQL roles **6 → 4**; runtime role read-only by default with per-table write grants in migrations; Alembic no longer uses `SET ROLE`; `ATLAS_DB_OWNER_ROLE` replaced by `ATLAS_DB_APP_ROLE`. SQL re-dry-run | Owner request 1 |
| 3 | Local `trust` limitation documented; `make doctor` auth probe; CI `scram-sha-256` + random masked passwords + `ci_auth` test (FR-39); cross-database `PUBLIC` `CONNECT` finding; optional Atlas-only `proposals/pg_hba-atlas.conf`, validated | Owner request 2 |
| 4 | Repository visibility is a security decision (DEC-085) with recommendation **private** and plan consequences (spec §6.8). No change made | Owner request 3 |
| 5 | CP1 needs no Node: markdownlint, Redocly and oasdiff run via digest-pinned containers (FR-07, S-10, P-05) | Owner request 4 |
| 6 | New preconditions P-08 (branch/PR workflow) and P-09 (contract release approval); tasks still 53 in 7 checkpoints | Owner requests 4–6 |
| 7 | New `decisions/baseline-deviations.md` (TD-DEV-001…007) and `readiness.md` (approval request) | DEC-040 modification; owner request 6 |
| 8 | Register v0.3: D-07 rows moved to Confirmed; DEC-084/085 updated; DEC-091/092 narrowed | Requirement 8 (status separation) |
