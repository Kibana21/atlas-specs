# ATLAS-001 — Independent Engineering Review #1

**Date:** 24 October 2026 · **Reviewed:** `spec.md` v0.1, `plan.md`, `tasks.md` (108 tasks), `acceptance.md` (18 ACs) · **Status of reviewed docs:** Draft, unchanged by this review. Nothing has been approved or marked Accepted.

**Owner direction received during review:** *"use the existing postgres and redis"* for local development. It is applied below as an input. The resulting spec changes still need approval (decision table §4).

## 1. Evidence gathered (read-only)

| Check | Result |
|---|---|
| Local PostgreSQL | **Homebrew PostgreSQL 15.12** (aarch64, macOS 26.3) running as a brew service on `localhost:5432`. Shared: it hosts several other projects' databases (names withheld from this public repository). An empty `atlas_db` (owned by the local superuser, no tables) already exists. The connecting role is a **superuser**. `pg_trgm`, `pgcrypto`, `uuid-ossp`, `btree_gist` available. |
| Local Redis | Docker container `redis` (image `redis:7`, **server 7.4.9**) on `*:6379`. Not part of any compose project. 16 logical DBs, **db1 already holds keys (another project)**, no password, AOF off, restart policy `no`. |
| CI environment | **None exists.** No `.github/` in any repo and no `gh` CLI locally. Repo visibility, Actions availability and runner policy are unverifiable from here. The CI PostgreSQL/Redis version is whatever we pin in service containers. |
| Toolchain | uv 0.10.0; Python 3.14.7 default, **3.12.12 available via uv**; **Node v25.2.1** (odd-numbered "Current" line, past end of life by this date); no Node version manager; pnpm 11.5.2; Docker 27.4. |
| FastAPI conformance probe | Scratch app using FastAPI 0.162.0 / Pydantic 2.14.1 with the foundation shapes, compared with oasdiff (container image, version `6e25854`). Findings in C-03. |

## 2. Findings

### Critical

**C-01 · PostgreSQL 16 is assumed everywhere but is neither decided nor present.**
The spec hard-codes PostgreSQL 16 in §6.1, FD-11, B1-06, B6-02, AC-04 and AC-06. DEC-021 ("16+") is only *Proposed*. The actual local server is 15.12, and you've directed local development to use it. With 15 locally and 16 in CI, the tests would run on a different major than development. *Fix:* make the major an explicit decision (D-01). Pin CI to the **same major as local**. Forbid features newer than that major in ATLAS-001. Keep the production/target major (Azure Flexible Server) as a separate DEC-021 decision, due before the first deployed environment. PostgreSQL 15 is supported upstream until November 2027.

**C-02 · Test designs are destructive on shared services.**
Using the existing PostgreSQL and Redis makes these planned steps unsafe:
- B4-10 `FLUSHALL` wipes every project's Redis data, including db1.
- B4-02, AC-05 and AC-15 "stop redis" stop the shared container.
- Plan §5.2 per-session `atlas_test_<worker>` databases require CREATE DATABASE on a shared superuser role.
- Running the app as the local superuser is not production-quality.

*Fix:*
- Dedicated non-superuser role and dedicated dev and test databases (D-02).
- A dedicated Redis DB index per environment plus an `atlas:` key/queue prefix (D-03).
- A guard that refuses destructive test operations unless `ATLAS_ENV=test` **and** the target is the Atlas test DB/index.
- `FLUSHDB` on the Atlas test index only.
- Simulate dependency failures with an unreachable URL or port, never by stopping shared services.
- Remove `compose.yaml` from the local path; CI keeps service containers.

**C-03 · The contract-conformance method in FR-27/FD-08 is not feasible as written; a corrected method is.**

What the probe showed:

| Behaviour | Consequence for the spec |
|---|---|
| FastAPI emits OpenAPI **3.1.0** ✔, and oasdiff parses it ✔ | No blocker here |
| `oasdiff breaking --fail-on ERR` caught a removed required response field ✔ | Breaking detection works |
| Pydantic adds `title` to every schema and property. A contract without titles makes `oasdiff diff --fail-on-diff` **fail on cosmetic differences**, and oasdiff has no ignore-title option | Exact structural diff is noisy |
| An endpoint present in code but absent from the contract is **not** reported by `breaking` (exit 0) | The spec's "breaking in both directions" leaks undocumented additions, e.g. new optional fields |
| FastAPI auto-injects `HTTPValidationError` / `ValidationError` 422 responses on any route with parameters, unless 422 is declared on that route | Conflicts with the error envelope |
| Generated `operationId`s are verbose (`get_job_api_v1_jobs__job_id__get`) | Won't match hand-authored IDs |
| `X-Correlation-ID` response headers are not emitted | Contract declares them; code output omits them |
| Optional fields come out as `anyOf: [{type}, {type: null}]` | Hand-authored `type: [string, "null"]` would differ structurally |

*Corrected method (verified feasible):*
1. Explicit `operation_id` on every route.
2. Declare the envelope for 422/4xx/5xx on every route, via router-level `responses` or explicitly per route. In the probe, a route that declared 422 no longer got the automatic `HTTPValidationError`; the router-level variant is confirmed in the first B5 task.
3. A small `app.openapi()` hook that adds the shared `X-Correlation-ID` header reference to every response.
4. A deterministic normalizer applied to **both** documents that strips `title`/`description`/`summary`/`examples`, sorts keys, and canonicalizes nullable forms.
5. `oasdiff diff --fail-on-diff` on the normalized pair for **exact equivalence**, plus `oasdiff breaking` in specs CI for versioning.
6. A contract style guide saying contracts are written in the Pydantic-compatible 3.1 dialect.
7. Pin the oasdiff image by version or digest.

### Major

**M-01 · Scope: durable jobs and the transactional outbox should be deferred.**
B4 (11 tasks, ≈2.5 days) pulls BL-201 forward from Phase 2: the job/attempt tables, outbox, relay, retry/backoff, Redis-loss recovery and two job endpoints. ATLAS-001 contains **no job with business value**, so none of that durability protects anything yet. It also adds two endpoints to contract 0.1.0 that would need deprecating. "Minimal but production-quality" here means proving the **seams**:
- Taskiq broker configuration with an Atlas-isolated queue;
- a worker built from the same codebase and image;
- one diagnostic task's round trip;
- Redis readiness.

*Recommendation (D-04):*
- Defer the outbox, durable job state, retries and the job endpoints to BL-201. Make that a hard prerequisite of the first real background job (exports, connectors).
- Keep a `diagnostics.ping` round-trip integration test and a `make worker-smoke` command, using Taskiq's Redis result backend with a short TTL on the Atlas Redis index. Redis is acceptable here because nothing durable is stored.
- Migrations still need proving. Use a reviewed **empty baseline revision** `0001_baseline` so the upgrade/downgrade, drift and single-head checks run with zero domain tables. The first real tables arrive with BL-101.

**M-02 · Some tasks span several repositories or can't be verified on their own.**
- **Multi-repo:** M0-05 (backend + frontend), M0-06 (all three), X2-01 (all), X2-02 (all). *Fix:* split into one task per repo. Sign-off evidence lives in specs; tags are separate backend and frontend tasks.
- **Forward verification:** F1-05 is verified in F4-02, F1-06 and F2-04 in F4-01. A task can't prove itself before the test harness exists. *Fix:* move Vitest setup into F1 (new F1-0x) and have each task ship its own tests.
- **Vague checks:**
  - B1-05 says "0 tests… exit 0 or 5". *Fix:* include one sanity test.
  - B6-05 says "lowering tests below fails". *Fix:* make it a deterministic `--cov-fail-under` drill.
  - S2-04 says "fix or exempt current violations". *Fix:* exclude the baseline folders from linting.
- **Implicit baseline edits:** S2-04 would push edits into the BRD, UX and Tech baselines, which are under approval control. Lint only non-baseline documents in ATLAS-001.

**M-03 · Frontend design language is too thin.**
FR-46 defines only Tech §5.3 colours and omits:
- Compute violet `#8C58D8` (UX §2.1, CF-14);
- typography scale and font strategy (self-hosted, so the security policy needs no exception);
- spacing, radii, elevation;
- a focus ring of at least 2 px;
- motion tokens (120–220 ms) with `prefers-reduced-motion`;
- semantic status tokens with non-colour cues;
- an explicit `color-scheme: light`, since UX says never dark by default.

*Fix:*
- Complete the token set and mark it "proposed — DEC-065".
- Add an automated **WCAG contrast unit test** for every declared text/background pair, so palette validation starts now.
- Keep no navigation rail, no product components and no shadcn/ui primitives until Phase 1.
- Add the missing "diagnostics disabled" state to `/status`. With diagnostics off, `/diagnostics/build` returns 404, and the page must say so instead of showing an error.

**M-04 · Visual regression and a second browser engine exceed a minimal skeleton.**
Golden screenshots of a one-link page (AC-17, F4-05) add container-pinning work and flakiness for almost no protection. WebKit E2E also depends on DEC-055, which is still Open.
*Fix:*
- Defer visual baselines to the first real screen (BL-105/BL-109).
- Run E2E in **Chromium only** for ATLAS-001, with Playwright projects structured so a second engine is a one-line addition once DEC-055 closes.
- Keep axe accessibility checks; they're cheap.
- Update spec §9: UX-NFR-012 is no longer claimed.

**M-05 · Local Node runtime doesn't match the pinning policy.**
The local Node 25.2.1 is an odd-numbered, end-of-life line, and no version manager is installed. A pin to the current LTS in `.nvmrc`/`engines` would not hold locally.
*Fix:* pin the Node 24 LTS line, add `engine-strict`, and document installing it (e.g. `pnpm env use --global 24`, or a version manager). The install changes your machine, so it appears as D-06.

**M-06 · The CI environment can't be verified.**
No workflows exist yet, and repo visibility and Actions availability are unknown. The cross-repo jobs (B6-03, F5-03, X1-02) depend on read-only tokens. *Fix:* add one CI preflight task per repo that proves Actions run and the token can read the other repo, before any CI-dependent task. Keep credentials as an approval item (D-05).

### Minor

| ID | Finding | Fix |
|---|---|---|
| m-01 | Spec §6.1 assumes db/user `atlas`; `atlas_db` already exists | Settle in D-02 |
| m-02 | Python 3.12 stdlib has no `uuid7` | Add a small dependency (e.g. `uuid-utils`) inside the single ID factory; keep DEC-037 swappable |
| m-03 | Redis 7.4 in CI should match local 7.4.9 | Pin `redis:7.4`. Redis 7.4 is under the RSAL/SSPL licence, acceptable for local/test; production uses Azure Managed Redis (DEC-030) |
| m-04 | AC-04 timing gates (≤60 s/≤90 s) depend on an undefined reference laptop (DEC-054 Open) | Make them informational in ATLAS-001 |
| m-05 | Plan §5.2 per-xdist-worker databases | Use a single `atlas` test DB with serial integration tests (small suite); no CREATE DATABASE needed |
| m-06 | FD-01…FD-12 are all listed as approval items, though most are reversible implementation details | Reclassify as Claude-resolved, recorded in an ADR and reviewable (§4 note) |
| m-07 | `/` will later become the UX Home route (UX §3) | Label the landing as a placeholder to be replaced by BL-105, not a product page |
| m-08 | The scratch probe used `oasdiff:latest` | Pin it (C-03 step 7) |
| m-09 | RTM and backlog untouched by ATLAS-001 | After approval, map ATLAS-001 tasks to BL-013/021/103/107/122/126 in the backlog. No RTM row changes needed once M-01 is accepted |

### Traceability and exclusion check (requested item 7)

- **No excluded capability introduced.** The four documents contain no OpenTelemetry, tracing, telemetry SDK, provisioning or AI. Every "PR" mention is the normal Git workflow for developing Atlas, which spec §3 explicitly distinguishes from the excluded PR-analysis feature. AC-18 adds a scope guard.
- **Traceability intact:** spec §9 maps FR/NFR to Tech §6, §8, §15, §17 and to BL-013/021/103/107/122/126. Two corrections:
  1. With M-01, the BL-201 "skeleton" mapping becomes "seam only".
  2. With M-04, drop the UX-NFR-012 claim and keep UX-NFR-008 (accessibility) and UX-NFR-011 (Chromium E2E, partial until DEC-055).

## 3. Proposed change list

| # | Change | Rationale | Affects |
|---|---|---|---|
| 1 | Replace "PostgreSQL 16" with the D-01 major in spec §6.1, FD-11, AC-04/06, CI tasks. Add a rule: no features above the pinned major | C-01 | spec, plan, tasks B6-02/X1-02, AC-04/06 |
| 2 | Local services = existing PostgreSQL and Redis. Remove `compose.yaml`/`make up`/`make down` from the local path. Add a `make doctor` preflight that checks versions, role, database, Redis index and isolation | Owner direction; C-02 | spec §4.1, §6.1, §7, FR-29, FD-05; tasks B1-06/07 |
| 3 | Isolation contract: dedicated role (no superuser), dev and test databases, Redis DB index per env plus `atlas:` prefix, destructive-operation guard, no `FLUSHALL`, no stopping shared services | C-02 | spec (new FR), plan §5.2, tasks B3/B4, AC-05/12/15 |
| 4 | Rewrite FR-27/FD-08 to the 7-step normalized-equivalence method. Add a contract style guide task in S1 and a normalizer task in B5 | C-03 | spec, plan §4.1, tasks S1/B5/B6-03, AC-03 |
| 5 | Defer outbox, durable job tables, relay, retries and the job endpoints to BL-201. Keep the Taskiq seam (broker, worker, ping round trip, readiness, worker image). Migration `0001_baseline` (empty, reviewed) | M-01 | spec FR-20, 23–26, §6.2, §6.6; contract 0.1.0 shrinks to health + build; tasks B3-04/05, B4 (11 → ≈5); AC-06/11/12 |
| 6 | Split M0-05, M0-06, X2-01, X2-02 into single-repo tasks. Move Vitest setup into F1. Each task ships its own tests. Tighten B1-05, B6-05 and S2-04 checks; markdownlint excludes baseline folders | M-02 | tasks, AC-01 |
| 7 | Complete the bright token set (colours incl. compute violet, type, spacing, radii, elevation, focus, motion, status semantics, `color-scheme: light`). Add a contrast unit test. Self-hosted font. Add a `/status` "diagnostics disabled" state. Label `/` a placeholder | M-03, m-07 | FR-44–46, tasks F1-05/F3, AC-14/15 |
| 8 | Defer visual regression; Chromium-only E2E (second engine after DEC-055) | M-04 | NFR-07/08, tasks F4-02/F4-05, AC-16/17, spec §9 |
| 9 | Pin Node 24 LTS with `engine-strict`; document the install | M-05 | FR-40, F1-01, frontend README |
| 10 | Add a CI preflight task per repo (Actions runs; cross-repo token works) before CI-dependent tasks | M-06 | tasks S2/B6/F5 |
| 11 | Minor fixes m-02…m-05, m-08, m-09 | Minor | various |
| 12 | Reduce the approval gate (spec §11) to the decision table below. FD items not listed there become Claude-resolved and recorded in an ADR | m-06 | spec §10–11 |

Expected effect: about 95–100 tasks (B4 shrinks; splits and preflights add some). Calendar estimate drops to about 2–2.5 weeks with two engineers. The contract shrinks to four operations, which reduces the later deprecation burden.

## 4. Decisions requiring your approval

Only genuine blockers are listed. Everything else (Python 3.12 via uv, mypy, openapi-typescript/openapi-fetch, psycopg 3, structlog, normalizer design, ports, lint tools, correlation-ID format, committing `.python-version`) I resolve. Each choice is recorded in ADR-0006 or a successor so you can review and override it.

| ID | Decision | Options | Recommendation | Blocks |
|---|---|---|---|---|
| D-01 | PostgreSQL major for ATLAS-001 (local + CI) | (a) **15**: matches the existing server; CI pins `postgres:15` · (b) upgrade the local server to 16/17 · (c) local 15, CI 16 (rejected: version skew) | **(a) 15**, with "no features newer than 15". The production major stays DEC-021, due before the first deployed environment | B3, B6, all migration ACs |
| D-02 | Atlas footprint on the shared PostgreSQL | Role name, and reuse `atlas_db` vs create new databases | Create non-superuser role `atlas_app`. Reuse the empty `atlas_db` for dev and create `atlas_test` for tests, both owned by `atlas_app`. I'd give you the exact SQL to run (or run it with your go-ahead) | B3 |
| D-03 | Atlas footprint on the shared Redis | Which DB indexes; destructive-test policy | DB **10** (dev) and **11** (test), `atlas:` prefix, `FLUSHDB` only on 11 under `ATLAS_ENV=test`. db1 is in use by another project | B4 |
| D-04 | Defer outbox and durable job persistence to BL-201 | (a) defer: seam only plus empty baseline migration · (b) keep as specified · (c) keep the `job` table only, defer outbox/relay | **(a)**. Nothing durable is needed until the first business job; becomes a hard prerequisite of BL-201 | Spec FR-20…26, contract scope |
| D-05 | CI platform access | GitHub Actions + read-only cross-repo credential type (fine-grained token vs GitHub App), who creates it, and named code owners for branch protection | GitHub Actions. A read-only fine-grained token per consumer repo, created by you. Code owners: you, until DEC-081 names others | Cross-repo CI jobs, M0 tasks |
| D-06 | Local Node runtime | Install Node 24 LTS on your machine (pnpm-managed or version manager) vs keep Node 25 | Install **Node 24 LTS**; Node 25 is end-of-life | Frontend tasks F1+ |
| D-07 | Stack confirmations carried from spec §11 | Confirm DEC-020, DEC-024, DEC-028, DEC-038, DEC-039, DEC-040 for ATLAS-001 scope (DEC-021 is replaced by D-01) | Confirm | All implementation |

**Next step after your answers:** I revise spec/plan/tasks/acceptance to v0.2 with the approved changes, and you review that version before anything is marked Accepted or any implementation starts.

---
*Probe artefacts (throwaway, not in any repo): scratchpad `fastapi-probe/` with `probe.py`, the generated `openapi.json` and the oasdiff test variants.*
