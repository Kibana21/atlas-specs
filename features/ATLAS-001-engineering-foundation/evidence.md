# ATLAS-001 — Evidence Record

**Status:** **Gate G1 PASSED**, **Gate G2 PASSED**, **Gate G3 PASSED**, **Gate G4 PASSED**, **Gate G5 PASSED** (2026-10-24). CP1 (S-01…S-12) and backend CP2–CP5 (B-01…B-25, B-27, B-28) complete; CP6 **not started** (awaiting owner authorization). ATLAS-001 **not Accepted** (G7).
**Baseline:** spec v0.2.2 (controlled amendment of v0.2.1) with plan/tasks/acceptance v0.2.1 — Approved for Implementation (owner, 2026-10-24); CP1 authorized.

## 1. Approvals and decisions in force

| Item | State (2026-10-24) |
|---|---|
| P-01 specification set v0.2.1 | Approved for Implementation |
| P-02 D-07 stack decisions | Approved (register v0.3/v0.4) |
| P-03 PostgreSQL four-role SQL | **Applied 2026-10-24** under the owner's conditional CP3 authorization, after a passing read-only preflight (§9.1) |
| P-05 pinned images / PyPI / local venvs / temporary containers | Confirmed |
| P-06 / DEC-085 repository visibility | **PUBLIC** (owner decision); CI Mode A |
| P-08 change workflow | Confirmed, then **superseded by the owner's standard workflow (2026-10-24):** Claude creates the feature branch and PR, waits for required checks, reviews the diff, merges when all gates pass, and confirms `main` CI. Never force-push shared branches, bypass protection, or merge failing checks |
| P-09 contract release `0.1.0` | **Approved conditionally** (owner, 2026-10-24); all conditions verified (§6) → tag created |
| Amendments A1/A2/A3 (E-01/E-03/E-04) | Approved (A1, A2) / accepted provisionally (A3); spec v0.2.2 |
| DEC-084 `pg_hba` hardening | Approved in principle; **not applied** (CP3 authorization excluded `pg_hba.conf` changes) |
| P-07 rulesets (`ci-access.md` §6) | **Applied 2026-10-24** to `atlas-specs` and `atlas-backend` (§9.4); backend required checks extended with `images` after its first green `main` run (§11.4); `atlas-frontend` waits for its CI (CP6/CP7) |
| G2 / CP3 | G2 accepted and CP3 authorized by the owner (2026-10-24) |
| G3 / CP4 | G3 accepted and CP4 authorized by the owner (2026-10-24), including completion of `getHealthReady` and emptying the pending list |
| G4 / CP5 | G4 accepted and CP5 authorized by the owner (2026-10-24) |

## 2. Branch, commits and CI

- **Branch:** `atlas-001/cp1-specs-foundation` (pushed; not merged; `main` unchanged at `ba67ce2`).
- **CI run (S-01…S-11 head):** [specs-ci run 40065369863](https://github.com/Kibana21/atlas-specs/actions/runs/40065369863) — event `push`, commit `be72947aea7b2e73d90dd76e0c6723b8ab74ee40`, run 1 attempt 1, **conclusion: success**.

| Job | Conclusion (GitHub API) | Steps |
|---|---|---|
| `docs-lint` | success | checkout → `make docs-lint` |
| `contract` | success | checkout → setup-uv → `make contract` → `make schemas` |
| `tools` | success | checkout → setup-uv → `make tools` |
| `tokens` | success | checkout → setup-uv → `make tokens` |
| `registry` | success | checkout → setup-uv → `make registry` |
| `breaking` | success (**skip notice: no `contract-v*` release tag yet**) | checkout (full history + tags) → setup-uv → `make breaking` |

Job logs require GitHub authentication to download; job and step conclusions above come from the public Actions API. Every step is a `make` target with `-e -o pipefail`, so any failing command fails the step (pytest also fails when no tests are collected).

| Commit | Task |
|---|---|
| `ff3a5ae` | Approved baseline v0.2.1 recorded (docs, register v0.4, deviations, proposals; local identifiers redacted) |
| `c600f16` | S-01 conventions + style guide |
| `c648ba3` | S-02 compatibility, pinning and release rules |
| `44e702a` | S-03 JSON Schemas + examples |
| `f8d237c` | S-04 OpenAPI contract 0.1.0 |
| `baf38b7` | S-05 design tokens + accessibility rules |
| `3aa7ea3` | S-06 tools project + `specs.lock` validator |
| `48c0820` | S-07 conformance tool + regression tests |
| `749ae5e` | S-08 token/WCAG validation |
| `dee94c2` | S-09 registry validation |
| `808df14` | S-10 lint config, pinned images, `make check` |
| `be72947` | S-11 CI workflow + CODEOWNERS |

## 3. Verification results (local, macOS arm64; and CI, ubuntu-24.04)

| Task | Verification | Result |
|---|---|---|
| S-01 | markdownlint (pinned) `contracts/*.md` | 0 issues |
| S-02 | markdownlint; checklist FR-04 + spec §6.4 | 0 issues; all rules present |
| S-03 | check-jsonschema 0.38.2: valid accepted / invalid rejected; 2020-12 metaschema | 6/6 valid accepted, 13/13 invalid rejected, 4/4 schemas valid |
| S-04 | Redocly 2.58.2 lint; structural check | valid, 0 errors; 3 operations, 2xx + envelope errors, `X-Correlation-ID` on all 8 responses |
| S-05 | `json.tool`; completeness checklist | valid; 95 tokens all `proposed`; all groups and AR-01…AR-10 |
| S-06 | `pytest tools/tests/test_specs_lock.py` | 16 passed |
| S-07 | `pytest test_conformance.py test_schema_consistency.py` (real oasdiff v1.33.0) | 29 passed |
| S-08 | `check_tokens.py`; `pytest test_tokens.py` | 95 tokens, 111 pairs pass; 13 passed |
| S-09 | `check_registry.py`; `pytest test_registry.py` | 393 requirements unique/mapped, refs resolve; 12 passed |
| S-10 | `make check` (repo); `make check` in a **fresh clone with no Node on PATH** | all 7 gates pass (both) |
| S-10 drill | `make breaking` in a disposable clone with a throwaway local tag (never pushed) | unchanged → pass; removed required field at same version → **fail** (`BREAKING_CHANGE`); same with 0.x minor bump → pass (`BREAKING_CHANGE_ACKNOWLEDGED`) |
| S-11 | static workflow checks; GitHub run | triggers push/pull_request only; permissions `{}` + `contents: read`; actions SHA-pinned; no secrets; run 40065369863 success |

Totals: **70 tool tests**, 19 schema examples, 111 contrast pairs, 393 requirements.

## 4. Public-repository safety (P-06)

Before the push, the full branch diff against `main` (2,996 added lines) and all commit messages were reviewed for secret/credential patterns, private keys, credential-like assignments, local paths and usernames, other projects' names, non-loopback IP addresses, internal hostnames and e-mail addresses. **No sensitive content found.** The only e-mail address is the synthetic `test@example.invalid` (reserved domain); the only IP is `127.0.0.1`. Local identifiers present in earlier drafts (local username, other projects' database names) were redacted in `ff3a5ae`. No `.venv`, caches, `.env`, keys or certificates are tracked.

## 5. Shared services and other repositories (read-only checks, 2026-10-24)

| Resource | Result |
|---|---|
| PostgreSQL 15 (shared) | 0 `atlas_*` roles; `atlas_db` owner and ACL unchanged (default), 0 tables; `atlas_test` absent |
| Redis (shared container) | Running (unchanged); DB 1 = 3 keys (other user, unchanged); DB 10 = 0; DB 11 = 0 |
| `atlas-backend` | HEAD `daa077e`, no local changes, remote unchanged |
| `atlas-frontend` | HEAD `b102612`, no local changes, remote unchanged |
| Node.js | not modified (still the pre-existing local version) |
| Temporary containers | none remaining; only the three digest-pinned validation images are kept |

## 6. Contract release (S-12) — completed

| Step | Evidence |
|---|---|
| Release candidate | branch `atlas-001/cp1-specs-foundation` head `5a5b555e01d155d68101395abc66a700cda3e234`, tree `97800c469d91ffa72f672e657d0782d4ea71f10c`; specs-ci [run 40066176722](https://github.com/Kibana21/atlas-specs/actions/runs/40066176722) green (6/6) |
| Pull request | [PR #1](https://github.com/Kibana21/atlas-specs/pull/1) — mergeable `clean`, 14 commits, 71 files (+6116/−819), file list identical to the local diff, no `brd/`/`ux/`/`technical/` files, only removals the two `.gitkeep` placeholders |
| Merge | merge commit **`bfe4a09e5d7d260afe15576b4fb9fd7530949370`** (parents `ba67ce2`, `5a5b555`), merged by Claude per the owner's workflow with a SHA guard on the head |
| Tree verification | merged `main` tree = `97800c469d91ffa72f672e657d0782d4ea71f10c` = approved candidate ✔ |
| `make check` on `bfe4a09` | all 7 gates pass (70 tool tests; 111 contrast pairs; 393 requirements) |
| `main` CI | [run 40066501022](https://github.com/Kibana21/atlas-specs/actions/runs/40066501022) — 6/6 success; `tools` log: `collected 70 items … 70 passed` |
| **Release tag** | **`contract-v0.1.0`**: annotated tag object `c70743d9dfa49cea6e68c84e05aa887aa6da0ec8` → commit **`bfe4a09e5d7d260afe15576b4fb9fd7530949370`**; `info.version` 0.1.0; on GitHub (`refs/tags/contract-v0.1.0^{}` = `bfe4a09`). No pre-existing tag; never moved |
| Release-mode `specs.lock` | in a fresh clone from GitHub: pin `bfe4a09` + `--release` → OK; untagged `5a5b555` + `--release` → `LOCK_NOT_RELEASE`; tag name as pin → `LOCK_TAG_NAME`; wrong version → `LOCK_VERSION_MISMATCH` |
| Tagged breaking comparison in CI | tag-triggered [run 40066596786](https://github.com/Kibana21/atlas-specs/actions/runs/40066596786) 6/6 success; `breaking` job log: `breaking: comparing against contract-v0.1.0` → `OK: no unacknowledged breaking changes` (the pre-tag `main` run logged the skip notice, confirming the switch) |

Process note: during tagging, a shell variable-expansion error made one pre-tag check (`info.version`) fail to run while the tag was already created **locally**; nothing was pushed. All pre-tag checks were then re-run and passed before the push.

## 6a. Gate G1 evaluation

| G1 criterion (tasks.md) | Result |
|---|---|
| `make check` and specs CI green on the tagged SHA | ✔ `make check` on `bfe4a09`; CI runs 40066501022 and 40066596786 green |
| Conformance self-tests prove missing **and** unexpected operations are detected | ✔ `test_missing_operation_detected`, `test_unexpected_operation_detected`, `test_unexpected_method_on_existing_path_detected` pass locally and in CI |
| Token contrast check passes | ✔ 111/111 pairs (tightest text 4.50:1, E-04 accepted provisionally; tightest non-text 3.05:1) |
| Baselines unchanged | ✔ no `brd/`, `ux/`, `technical/` changes in PR #1 |
| AC-01 (specs part) | ✔ independent `make check` incl. fresh clone without Node; specs-ci green |
| AC-02 (specs part) | ✔ release tag on an approved `main` commit; release-mode lock validation |
| AC-03 (specs part) | ✔ 23 conformance cases + 6 schema-consistency cases; breaking job fails unannounced breaking changes (local drill) and compares against the release tag in CI |
| AC-14 (token values) | ✔ 95 proposed tokens, AR-01…AR-10, reduced motion, light-only |

**Verdict: Gate G1 — PASS.**

## 7. Deviations and open items for G1

| ID | Item | Status |
|---|---|---|
| E-01 | FR-02 named one `health.v1` schema; delivered `health-live.v1` + `health-ready.v1` because a union schema accepted an invalid readiness body | **Approved** (owner, 2026-10-24); spec amendment A1 (v0.2.2) |
| E-02 | Config files introduced earlier than their task for verification (`.markdownlint-cli2.yaml` in S-01, `redocly.yaml` in S-04, `tools/images.lock` in S-07), finalized in S-10 | Sequencing only |
| E-03 | Relationship colour and sizing tokens added per the owner's CP1 instruction §10 (spec §7.1 did not list them) | **Approved** (owner, 2026-10-24); spec amendment A2 (v0.2.2) |
| E-04 | `api` text on its own tint passes at exactly 4.50:1 (zero margin) | **Accepted provisionally** (owner, 2026-10-24); recorded under DEC-065 and spec §7.1 (A3); reassess at final palette approval |
| E-05 | Whitespace-only lint fixes in non-baseline documents (incl. approved ATLAS-001 docs); `git diff -w --ignore-blank-lines` shows only a code-fence language, one heading level and backticks around a literal | Formatting only |
| E-06 | `breaking` tagged path | **Closed** — verified in CI run 40066596786 |
| E-07 | While reading CI logs, a helper script's default redirect handling forwarded the existing GitHub OAuth credential (unprinted) to GitHub's Actions log-storage host over HTTPS on three requests, which rejected it (401). Fixed: logs are now fetched via the signed URL without credentials | Disclosed; owner may rotate the credential |
| E-08 | `main` has no branch protection/ruleset (P-07 pending); merges rely on the documented workflow rules | Risk until P-07 |

---

## 8. Checkpoint 2 — backend foundation (atlas-backend)

**Authorization:** owner, 2026-10-24 — B-01…B-08, read-only diagnostics against the shared services (no active auth probe), backend static/unit/contract/security CI moved into CP2 (spec v0.2.3, amendments A4–A6; PR [atlas-specs#3](https://github.com/Kibana21/atlas-specs/pull/3), merge `74503e9`).

| Item | Evidence |
|---|---|
| Pull request | [atlas-backend#1](https://github.com/Kibana21/atlas-backend/pull/1): 11 commits, 66 files, file list equal to the reviewed local diff, mergeable `clean` |
| Merge commit | **`a040129607068e1e32ba47530f3774dcdba11443`** (merge commit, head-SHA guard) |
| CI on PR head `3543492` | `static`, `unit`, `contract`, `security`: all success |
| CI on `main` | [backend-ci run 40068675645](https://github.com/Kibana21/atlas-backend/actions/runs/40068675645): 4/4 success. Logs: Ruff "All checks passed", mypy "no issues found in 53 source files", **106 passed, coverage 95.68 %**, contract "conforms" with the single declared pending operation, pip-audit "No known vulnerabilities found" |
| Local (clean clone of the committed branch) | `make check` 106 passed, 95.68 %; `make security` clean; `make contract` conforms |
| Contract conformance | Pinned `contract-v0.1.0` (`bfe4a09`) minus `getHealthReady` (→ B-09). Drills: removed route → `MISSING_OPERATION`; undeclared route → `UNEXPECTED_OPERATION`; bogus pending entry → `PENDING_LIST_INVALID` |
| `make api` smoke | 127.0.0.1:8100 → `200 {"status":"ok"}`, echoed `X-Correlation-ID`, security headers; `/docs` only in local. Port 8000 is used by another local project (left untouched); `API_PORT` is configurable |
| `make doctor` (read-only, live) | PG major 15 PASS; Atlas roles, `atlas_test`, schema `atlas` missing → FAIL with P-03 remediation; loopback auth `trust` → WARN (read from `pg_hba_file_rules`, no probe); runtime-role login not attempted; Redis 7.4.9 DBs 10/11 reachable, 0 keys |
| Shared services after CP2 | PG: 0 Atlas roles, `atlas_db` ACL default, no extra schemas, no `atlas_test`; Redis DB1 = 3 keys (unchanged), DB10/11 = 0 |

### 8.1 Gate G2 evaluation

| G2 criterion | Result |
|---|---|
| `make check` green with coverage ≥ 85 % | ✔ 106 tests, 95.68 % (local and CI) |
| Backend CI `static`/`unit`/`contract`/`security` green on PR and `main` | ✔ |
| `make contract` exact except the declared pending `getHealthReady` | ✔ incl. drills |
| Live endpoint: envelope errors and correlation headers | ✔ unit tests + live smoke |
| Doctor runs read-only against shared services | ✔ allowlist enforced in code and tests; live run changed nothing |
| AC-08/10/12/13 (backend unit level), AC-07 guards, AC-04 doctor | ✔ |

**Verdict: Gate G2 — PASS.**

### 8.2 CP2 deviations and findings

| ID | Item | Status |
|---|---|---|
| E-09 | Dev dependency `httpx` replaced by `httpx2` (Starlette 1.7's test client imports it; declared in `starlette[full]`; same author, `pydantic` org) | Implementation detail; no runtime dependency |
| E-10 | Unknown routes **and unsupported methods** return 404 `NOT_FOUND` (anti-enumeration) instead of inventing a 405 code outside the append-only catalog | Implementation detail; a `METHOD_NOT_ALLOWED` code would be a future contract change |
| E-11 | Logging redaction also masks secret-like `key=value` pairs inside text (tracebacks stay useful) | Strengthening of FR-25 |
| E-12 | Unhandled-error middleware placed inside the correlation/security middleware so 500s keep the request's correlation ID and headers (found by a failing test) | Design detail |
| E-13 | CI found two defects hidden locally by the untracked working tree (`.env.test.example` ignored by `.env.*`; scanner matching its own source); fixed and verified from a clean clone | Process: clean-clone verification now precedes every push |
| E-14 | Local port 8000 is occupied by another project; Atlas API port configurable (`make api API_PORT=8100`) | Environment note; frontend base URL must follow (CP6) |
| E-15 | `pending` operation `getHealthReady` | Must be implemented in B-09 and the list emptied by G5 (B-18) |

### 8.3 E-07 credential rotation — recommended owner procedure (not performed)

The credential is an **OAuth token** (`gho_…`) held by the macOS keychain for git over HTTPS, with scopes `repo`, `workflow`, `read:user`, `user:email`.

1. GitHub → Settings → **Applications → Authorized OAuth Apps**. Identify the app that issued the git credential (typically "Git Credential Manager" or "GitHub CLI"), then **Revoke**. This invalidates its tokens.
2. Remove the cached entry locally: Keychain Access → search `github.com` → delete the internet password used by git. Equivalent: `printf "protocol=https\nhost=github.com\n\n" | git credential-osxkeychain erase`.
3. Run `git fetch` in any Atlas repository and complete the browser sign-in that git's helper opens. A new token is stored.
4. Verify: `git ls-remote origin` works. CI is unaffected (Mode A uses no secrets).

Optionally review GitHub → Settings → **Security log** for unexpected `oauth_access` events.

## 9. Checkpoint 3 — backend persistence and migrations (atlas-backend)

**Authorization:** owner, 2026-10-24.

- G2 accepted; CP3 (B-09…B-12) authorized.
- P-03 SQL execution conditionally authorized, subject to a read-only preflight.
- Rulesets to be applied only if they preserve the automated PR workflow.
- Excluded: `pg_hba.conf`, server settings, unrelated databases, `atlas-frontend`, CP4.

### 9.1 P-03 preflight (read-only) and execution

| Preflight item | Result |
|---|---|
| Server | Homebrew PostgreSQL **15.12** on port 5432 (`server_version_num` 150012). Executor: the local bootstrap superuser |
| `atlas_db` empty | Only schema `public`. 0 relations, functions, types, large objects, publications and default ACLs. Only `plpgsql`. `tup_inserted = 0`. Default ACL. The only session was the owner's idle pgAdmin connection |
| `atlas_test` / Atlas roles | Absent / 0 `atlas_*` roles |
| Change list | Exactly the proposal: 4 login roles and their role settings; `atlas_db` owner + ACL; new `atlas_test`; in both Atlas databases, `public`-schema `PUBLIC` privileges revoked; schema `atlas` + default `SELECT` privileges + per-database `search_path` |
| Non-Atlas objects | None modified. No other database, role, schema, ownership, privilege, `pg_hba.conf` or server setting is touched |
| Rerun safety | The guards abort with zero changes on a rerun (verified again in the CI rehearsal: `ABORT: atlas_* roles already exist`) |
| Rollback | Documented in the proposal. Original `atlas_db` owner = the local bootstrap superuser (name not recorded in this public repo). Original ACL = default (`PUBLIC` CONNECT/TEMP; `public` schema `U` for `PUBLIC`) |
| Least privilege | Matches spec §6.2 (verified after apply, below) |
| Credentials | Generated in memory and passed to `psql` through environment variables. Written only to the git-ignored `.env`/`.env.test` (mode 0600). psql output redacted. Never on a command line, in shell history, logs or Git. `log_statement = none` (no statement logging) |
| Version check | File unchanged since the approved v0.2.1 baseline (`ff3a5ae`) and identical at the pinned `bfe4a09` |

**Execution:** `psql` exit 0; every step committed.

**Verification:**

- 4 login roles. All elevated flags false; connection limits 3/10.
- Owners `atlas_migrator` / `atlas_test_migrator`. No `PUBLIC` entry in either database ACL.
- `atlas_app`: no `CREATE` on `atlas`, no `TEMP`.
- All four cross-environment `CONNECT` privileges false.
- Database count 18 → 19 (`atlas_test`). 0 non-Atlas ACL or role-setting changes.
- `make doctor`: PASS for version, roles, databases, schema and the runtime-role session. WARN for `trust` (DEC-084, expected).

### 9.2 Implementation and CI

| Item | Evidence |
|---|---|
| Pull request | [atlas-backend#3](https://github.com/Kibana21/atlas-backend/pull/3): 5 commits, 33 files (+1391/−37), file list equal to the reviewed local diff, mergeable `clean` |
| Merge commit | **`7826f640d1522c0febb5880d8cec93254a321fd2`** (merge commit, head-SHA guard) |
| CI on PR head `9f3992a` and on `main` | [backend-ci run 40071857701](https://github.com/Kibana21/atlas-backend/actions/runs/40071857701) (`main`): `static`, `unit`, `contract`, `security`, `integration`: **5/5 success** (also 5/5 on the PR head) |
| `integration` job log (`main`) | `OK: bootstrap.sql = approved proposal + documented CI-ONLY block`; setup complete; `Running upgrade -> 0001_baseline`; `0001_baseline (head)` on `atlas_db`; **26 passed, 0 skipped** (incl. 8 `ci_auth` wrong/missing-password rejections under scram-sha-256). Role passwords masked; no unmasked password-length value in the log |
| Local (clean clone of the committed branch) | `make check`: 122 passed, **coverage 95.10 %**. `make contract`: conforms. `make security`: pip-audit clean + 7 tests. `make integration`: **18 passed**, 8 `ci_auth` skipped by design (local `trust`, no wrong-password probes) |
| B-09 live smoke (127.0.0.1:8100) | `GET /health/ready` → `200 {"status":"ok","checks":{"database":"ok"}}` with `X-Correlation-ID`. `/diagnostics/build` → `db_migration_revision: "0001_baseline"`. Only the Atlas process started for the smoke run was stopped |
| B-10 | `make migrate` on `atlas_db`, then `alembic current` → `0001_baseline (head)`. `atlas.alembic_version` owned by `atlas_migrator`. `atlas_app` has `SELECT` and no `INSERT`. `alembic check`: no drift |
| CI rehearsal (before push) | Disposable `postgres:15.19` container (loopback-only random port, removed afterwards): bootstrap OK, rerun aborts, migrate OK, 26/26 integration tests |
| Shared services after CP3 | PG: 19 databases. No non-Atlas ACL or role-setting change. `atlas_db` and `atlas_test` each hold only `atlas.alembic_version`. Redis: DB1 = 3 keys (unchanged), DB10/DB11 = 0. CP3 issues no Redis commands |

### 9.3 Gate G3 evaluation

| G3 criterion | Result |
|---|---|
| Migrations round-trip as the test migrator | ✔ `upgrade head → downgrade base → upgrade head`, `alembic check`, single head: local (trust) and CI (scram) |
| Runtime role cannot run DDL | ✔ `CREATE` in `atlas`/`public` and `TEMP` denied. Writes denied without a grant, allowed only after an explicit per-table grant. `UPDATE`/`DELETE` still denied |
| No Atlas test touched any non-Atlas database | ✔ Integration connections are restricted in code to `atlas_test` (plus the expected-denied `atlas_db` attempts). The session guard (non-Atlas databases, ACLs, roles, role settings) was unchanged in every run. Before/after inventory unchanged |
| AC-05 (database part) | ✔ 200 with the database; 503 `DEPENDENCY_UNAVAILABLE` naming `database` for a closed port, with no host, port, role or credential in the body. The Redis part follows in G4 |
| AC-06 | ✔ |
| AC-07 (CP3 part) | ✔ Privilege tests; cross-environment `CONNECT` denied (connection attempts for the test roles; catalog checks for all four pairs); no elevated flags; `ci_auth` in CI |
| AC-09 (revision) | ✔ `db_migration_revision = 0001_baseline`, read by the runtime role (integration test, CI and live smoke) |

**Verdict: Gate G3 — PASS.**

### 9.4 Rulesets (P-07), applied

The §6 settings preserve the automated workflow:

- **0 required approvals:** a single maintainer can still merge.
- **Merge commits only:** the method the PR helper already uses.
- **Strict required checks:** a PR that is behind `main` stops; it is never merged around the rule.

Configured with the existing credential (repository admin). No bypass actors. The owner can still edit or remove the rulesets.

| Repository | Ruleset (id) | Effective rules on `main` (read back) |
|---|---|---|
| `atlas-specs` | `protect-main` (25773158), `immutable-release-tags` (25773159) | `deletion`, `non_fast_forward`, `pull_request` (merge only, 0 approvals), strict checks `docs-lint, contract, tools, tokens, registry, breaking`. Tags `contract-v*`: no update or deletion |
| `atlas-backend` | `protect-main` (25773160) | Same rules; strict checks `static, unit, contract, security, integration` |
| `atlas-frontend` | not applied | Has no CI yet, so required checks could never report. Apply with F-11/F-12 (`ci-access.md` §6.1) |

### 9.5 CP3 deviations and findings

| ID | Item | Status |
|---|---|---|
| E-16 | The contract's `ReadinessChecks` requires `database` **and** `redis`, but the Redis check is B-13 (CP4). `getHealthReady` therefore stays in `contract-pending.yaml` (now `lands_in: B-09 + B-13`, removed by B-18), and the route is excluded from the generated schema until it is complete. Conformance stays exact; the route never claims `redis: ok` | Implementation sequencing, consistent with B-18; reversible |
| E-17 | Database parts of B-22 (`scripts/db/bootstrap.sql`, drift-checked against the pinned proposal) and B-23 (`integration` job, scram service, masked random passwords, `ci_auth`) brought forward from CP5, as "appropriate CI verification" for CP3. Redis service, worker round trip and `images` stay in CP4/CP5 | Scope moved earlier within ATLAS-001; no new scope |
| E-18 | The CP2 hygiene rule "no `services:` / `localhost:5432` in workflows" is narrowed, not removed. A job may reach `localhost:5432` only if it declares its own digest-pinned scram `postgres:15` service. `localhost:6379` is still forbidden | Strengthened check |
| E-19 | Clean-clone verification caught a scanner hit (`…:secret@…` in a new unit-test URL). Replaced with the approved placeholder before pushing | Process working as intended (E-13) |
| E-20 | The CI bootstrap superuser password is a fixed value scoped to the ephemeral, job-local container. The four Atlas role passwords are random per run and masked (FR-39) | Accepted CI detail |
| E-15 | Updated: `getHealthReady` partly implemented (database). Completes in B-13; list emptied by G5 (B-18) | **Closed in CP4** (§10.4, E-21) |

## 10. Checkpoint 4 — Redis and Taskiq worker foundation (atlas-backend)

**Authorization:** owner, 2026-10-24.

- G3 accepted; CP4 (B-13…B-17) authorized.
- Also authorized: completing `getHealthReady` and removing it from the pending list once exact conformance is verified.
- Excluded: outbox, durable jobs, advanced orchestration, CP5, `atlas-frontend`, PostgreSQL changes, DEC-084.

### 10.1 Architecture as built

| Part | Design |
|---|---|
| Redis client (`atlas.persistence.redis`) | **Allocation:** `AtlasRedis` is bound to the URL's DB (10 local, 11 test); any other DB is refused before connecting.<br>**Keys and commands:** keys must start with the `atlas:` prefix. Allowed: `PING`, `SET` with TTL, `GET`, `TTL`, exact-key `DEL`, bounded prefix `SCAN`, `DBSIZE`.<br>**Failures:** 1 s timeouts; errors carry no connection details |
| Broker (`atlas.workers.broker`) | **Queue:** `AtlasListQueueBroker` (taskiq-redis `ListQueueBroker`) on the single queue `<prefix>taskiq:queue`; no result backend.<br>**Registration:** explicit (`configure`).<br>**Listening:** bounded `BRPOP` (1 s, below the 5 s socket timeout); transient Redis errors are logged and retried by the listener, not the task |
| Middleware | Task allowlist; any `queue_name` override is refused; producer stamps a `correlation_id` label, the worker binds it to logs; one `task_failed` report (exception type only); **no automatic task retries** (DEC-046 → BL-201) |
| Task | `atlas.diagnostics.ping(marker_id, correlation_id)`. Typed `PingPayload`, validated by the producer and again by the worker. Writes `<prefix>ping:<marker_id>` = correlation ID with a 60 s TTL. Idempotent. Invalid input raises `InvalidTaskPayload` (field names only) |
| Processes | **Producer** (API, scripts, tests) only enqueues.<br>**Worker:** `make worker` = `taskiq worker atlas.workers.entrypoint:broker --workers 1 --shutdown-timeout 10 --wait-tasks-timeout 10`.<br>**Startup:** configures logging and stdlib redaction, then checks Redis is reachable.<br>**Shutdown:** SIGTERM / Ctrl+C is graceful (exit 0).<br>Only the entry-point module builds a broker at import; building connects nothing and runs nothing |
| Readiness | `/health/ready`: PostgreSQL and Redis concurrently, 1 s each. 503 `DEPENDENCY_UNAVAILABLE` with `failed_check` (first failing, in order). No host, port, URL or credential in the body |

### 10.2 Results

| Item | Evidence |
|---|---|
| Pull request | [atlas-backend#4](https://github.com/Kibana21/atlas-backend/pull/4): 5 commits, 34 files (+1846/−74), file list equal to the reviewed local diff, mergeable `clean`. Merged under the `protect-main` ruleset |
| Merge commit | **`450eb47b0919e9f75acaeabda3c19b524c51ad96`** |
| CI on PR head `529030f` and on `main` | [backend-ci run 40076619731](https://github.com/Kibana21/atlas-backend/actions/runs/40076619731): `static`, `unit`, `contract`, `security`, `integration`: **5/5 success** on both |
| `integration` log (`main`) | Isolated `postgres:15.19` + `redis:7.4.9` services. Bootstrap drift check OK. `0001_baseline (head)`. **35 passed, 0 skipped** (incl. 8 `ci_auth` and the worker round trip). `db 11: 0 keys match 'atlas:test:*'`. Passwords masked |
| Local (fresh clone) | `make check`: **156 passed, coverage 94.56 %**. `make contract`: `pending: none - full contract compared`, conforms. `make security`: pip-audit clean, 21 tests. `make integration`: **27 passed**, 8 `ci_auth` skipped by design |
| CI rehearsal | Disposable `postgres:15.19` + `redis:7.4.9` (loopback-only random ports, removed afterwards): 35/35; 0 keys left in DB 10/11 |
| B-17 smoke (local, DB 10) | `make worker` + `make worker-smoke` twice, after 8 s and 7 s idle: `OK … marker TTL 60 s`. `redis_keys.py --db 10 --pattern 'atlas:local:*'` → 0. DB 1 `dbsize` 3 before and after. Worker log: 0 restarts; graceful `worker_stopped` on SIGTERM |
| Shared services after CP4 | **PG:** 19 databases; 0 non-Atlas ACL or role-setting changes; Atlas DBs hold only `atlas.alembic_version`; no Atlas sessions.<br>**Redis:** DB 1 = 3 keys (unchanged), DB 10 = 0, DB 11 = 0; uptime ≈ 55 days (no restart); no configuration change, flush or foreign-key access.<br>No Atlas processes left running |

### 10.3 Gate G4 evaluation

| G4 criterion | Result |
|---|---|
| Worker round trip proven | ✔ A real worker subprocess consumed the run queue. The marker carried the producer's correlation ID (TTL ≤ 60 s). Local, CI, and the live DB 10 smoke |
| No keys remain outside expectations | ✔ Exact-key tracker and session guard: no run-prefix keys left. `DBSIZE` of DB 1, DB 10 and DB 11 unchanged in every run. The CI job checks 0 Atlas test keys |
| No forbidden commands | ✔ `test_redis_safety.py` over `src/`, `tests/`, `scripts/`, with fixture files proving each pattern is detected |
| Other Redis DBs unchanged | ✔ DB 1 = 3 keys before and after every local run. Its keys are never listed or read |
| AC-05 (Redis part) | ✔ 200 `{database: ok, redis: ok}`. 503 naming `redis` for a closed port (no host, port or URL in the body) |
| AC-10 (worker part) | ✔ Correlation ID in `task_enqueued`, `task_started`, `diagnostics_ping`, `task_succeeded` |
| AC-11 | ✔ DB/prefix isolation, factory rejects DB 1, queue override refused, exact-key cleanup |
| Contract conformance | ✔ Full `contract-v0.1.0` (pinned `bfe4a09`) with an empty pending list. The re-add drill fails with `UNEXPECTED_OPERATION` |

**Verdict: Gate G4 — PASS.**

### 10.4 CP4 deviations and findings

| ID | Item | Status |
|---|---|---|
| E-21 | The B-18 step "empty `contract-pending.yaml`" was done in CP4, as authorized. The remaining B-18 parts (re-add test in CI, drills B-19, response contract tests B-20) stay in CP5. A unit test asserts the list stays empty | Sequencing, owner-authorized |
| E-22 | **Upstream defect:** taskiq-redis `ListQueueBroker.listen()` blocks in `BRPOP` forever and handles only connection errors. With redis-py 8's default 5 s socket read timeout, an idle worker crashed and was restarted every ~5 s (found in the B-17 smoke). Fixed by `AtlasListQueueBroker` (1 s bounded `BRPOP`, transient errors logged and retried by the listener) | Fixed; unit and integration regression tests |
| E-23 | **Log leak found and fixed:** taskiq's receiver logs tracebacks through stdlib logging, bypassing structlog redaction. A pydantic validation traceback echoed task arguments. Fixed in two places: stdlib records get the same redaction (`RedactingFilter`), and task payload errors name fields only, with no chained cause | Fixed; tests assert argument values never reach the worker log |
| E-24 | FR-33's "keys outside the run prefix in DB 11 unchanged" is checked by key **count** (`DBSIZE`), not by listing key names. This follows the CP4 instruction not to scan unrelated keys; DB 1 and DB 10 are guarded the same way | Safer method; equivalent for the test's purposes |
| E-25 | "Safe retries" means idempotent tasks plus a listener that reconnects after transient Redis errors. Task-level retries/backoff stay deferred (DEC-046 → BL-201); a failed task is reported once and not re-executed | Within approved scope |
| E-26 | `make worker` runs one worker process (`--workers 1`) to stay within the shared server's footprint; scaling options are later work | Implementation detail |

## 11. Checkpoint 5 — conformance drills, response contract tests, images, README (atlas-backend)

**Authorization:** owner, 2026-10-24.

- G4 accepted; CP5 (B-18…B-25) authorized.
- Source of truth: the released `contract-v0.1.0`. It was not modified.
- Excluded: Docker-based PostgreSQL for local development, shared-service changes, DEC-084, `atlas-frontend`, CP6.

### 11.1 Tasks

| Task | Delivered |
|---|---|
| B-18 | Pending list stays empty (since CP4). The re-add drill fails `UNEXPECTED_OPERATION getHealthReady`. Release-mode lock check kept |
| B-19 | Drills run in `make contract` (CI `contract`) against the pinned conformance tool. Removed route → `MISSING_OPERATION getHealthLive`. Undeclared `GET /api/v1/diagnostics/extra` → `UNEXPECTED_OPERATION`. Extra optional property, renamed field, removed required field, changed status code and changed operationId each fail. The unchanged app conforms. Exports byte-identical |
| B-20 | Every released operation and declared status is exercised on the real app: live 200; ready 200, 503 database, 503 Redis; build 200, 404 disabled; 422, 500 and unknown-route 404 envelopes through the shared error path. Each response is checked against the pinned contract: status declared, `application/json`, `X-Correlation-ID` pattern (equal to `error.correlation_id`), schema with no undeclared fields, and the matching JSON Schema file. Meta-tests prove the validator rejects six body mutations and wrong status, header and media type |
| B-21 | `Dockerfile`, targets `api` and `worker`:<br>• digest-pinned `python:3.12.15-slim-trixie` and `uv:0.10.0`;<br>• locked runtime dependencies only; Debian `libpq5`;<br>• uid 10001, read-only `/app`;<br>• no env files, credentials, tests, caches or VCS data;<br>• health checks: api `/health/live`, worker Redis `PING`;<br>• graceful SIGTERM; `ATLAS_BUILD_SHA` |
| B-22/B-23 | Done earlier (CP3/CP4; §9, §10) |
| B-24 | CI `images` job (`scripts/images_check.sh`) and a dedicated Trivy secret scan in `security` (`make secret-scan`) |
| B-25 | Backend README: prerequisites; environment setup; local PostgreSQL 15 and Redis; API on a configurable port; worker; migrations; tests and contract checks; Docker images; troubleshooting; security restrictions |

### 11.2 Results

| Item | Evidence |
|---|---|
| Pull request | [atlas-backend#5](https://github.com/Kibana21/atlas-backend/pull/5): 6 commits, 17 files (+1122/−38), file list equal to the reviewed diff, mergeable `clean`, merged under `protect-main` |
| Merge commit | **`585f3f52e477b051cc33b15fdb549c8af6e6f44a`** |
| CI on PR head `5637eb4` and on `main` | [backend-ci run 40079105731](https://github.com/Kibana21/atlas-backend/actions/runs/40079105731): `static`, `unit`, `contract`, `security`, `integration`, `images`: **6/6 success**. Every job ≤ 1 min (NFR-02 ≤ 15 min) |
| `unit` | **163 passed, coverage 94.48 %** |
| `contract` | Lock valid (release). `pending: none - full contract compared`. Conforms. **28 pinned-contract tests passed** (drills + response validation) |
| `integration` | Bootstrap drift check OK. **35 passed, 0 skipped** (incl. `ci_auth` and the worker round trip) |
| `security` | pip-audit "No known vulnerabilities found". 26 security tests passed. Trivy secret scan: 0 secrets |
| `images` | See §11.3 |
| Local (fresh clone, README walkthrough) | `make setup` created `.env`/`.env.test` with placeholders; credentials entered. `make doctor`: all PASS, `trust` WARN. `make migrate` → `0001_baseline (head)`. `make check`: 163 passed, 94.48 %. `make integration`: 27 passed (8 `ci_auth` CI-only). `make contract`: 28 passed. `make security`, `make secret-scan` clean. `make api API_PORT=8101` → ready `{database: ok, redis: ok}`. `make worker` + `make worker-smoke` → OK. `make images` → OK |

### 11.3 Docker build, runtime and security findings

| Check | Result (local and CI `main`) |
|---|---|
| Build | Both targets build from one commit with `ATLAS_BUILD_SHA` |
| hadolint v2.14.0 | No findings |
| Trivy 0.67.2: image vulnerabilities (HIGH/CRITICAL) | api and worker: **0 fixable**, **0 in Python packages**. 44 OS findings in the base image with no upstream fix yet: reported, not gating |
| Trivy: secrets in images; Dockerfile misconfiguration | 0; 0 HIGH/CRITICAL |
| Static image checks | uid 10001 (non-root); health check present; no `.env`, `.git`, tests, build output or tool caches in `/app`; no secret-named variables in the image environment |
| Hardened runtime (isolated Docker network; own `postgres:15.19` + `redis:7.4.9`; `--read-only --cap-drop=ALL --security-opt=no-new-privileges`) | Bootstrap and `alembic upgrade head` from the api image. **api** and **worker** reach Docker `healthy`. `live` 200 (correlation ID echoed, `nosniff`, no `server` header). `ready` 200 `{database: ok, redis: ok}`. Build info: commit SHA and `0001_baseline`. Unknown route: 404 envelope |
| Worker in container | Round trip on DB 10: marker = producer's correlation ID; correlation ID in worker logs |
| Graceful shutdown | `docker stop`: api exit 0 (≈1 s, "Application shutdown complete"); worker exit 0 (≈1 s, `worker_stopped`). No credential in either log |

### 11.4 Drills (real PRs, closed unmerged, branches deleted)

| Drill | PR / run | Result |
|---|---|---|
| Quality gates: one Ruff error + one mypy error; untested module; fake credential (AC-01, AC-12, AC-13) | [#6](https://github.com/Kibana21/atlas-backend/pull/6), [run 40079303853](https://github.com/Kibana21/atlas-backend/actions/runs/40079303853) | `static` **failure** (`F401 os imported but unused`; the same commit fails mypy locally: `Incompatible return value type`). `unit` **failure** (`Required test coverage of 85.0% not reached. Total coverage: 70.27%`). `security` **failure** (`drill-fake-credential.txt: password in url`). `contract`, `integration`, `images` success. PR `blocked` by the ruleset |
| Contract: undeclared `GET /api/v1/diagnostics/extra` (AC-03 c) | [#7](https://github.com/Kibana21/atlas-backend/pull/7), [run 40079379070](https://github.com/Kibana21/atlas-backend/actions/runs/40079379070) | `contract` **failure** (`UNEXPECTED_OPERATION: GET /api/v1/diagnostics/extra (getDiagnosticsExtra) is implemented but not in the contract`). `unit` also fails (the export test lists the released operations). Others success. PR `blocked` |
| Revert | `main` (no drill commits) | 6/6 green (run 40079105731) |

The `protect-main` ruleset on `atlas-backend` now requires `static, unit, contract, security, integration, images` (strict). Verified read-only after the change.

### 11.5 Gate G5 evaluation

| G5 criterion | Result |
|---|---|
| Backend CI fully green | ✔ 6/6 required jobs on the PR and `main` |
| Conformance proven, incl. the AC-03 drills | ✔ Structural conformance with an empty pending list. Automated drills b, c, e, f, operationId and pending re-add. Real drill PR (c) fails `contract`. Response bodies validated against the released contract and JSON Schemas |
| Images build | ✔ Both targets; non-root; scanned; hardened runtime verified |
| README reproducible | ✔ Followed step by step on a clean clone (deviation E-28) |
| AC-01 (backend) | ✔ `make check` exit 0 on a clean clone; CI green; lint/type drill fails `static` |
| AC-02 (backend) | ✔ `make specs` release-mode lock validation (`contract-v0.1.0` commit). The frontend parity part is CP7 |
| AC-03 (backend) | ✔ |
| AC-05 | ✔ Readiness (G3/G4) plus images non-root (`id -u` = 10001) and healthy |
| AC-08 (backend) | ✔ 404 (unknown route and diagnostics disabled), 422, 500 and 503 bodies validate against `error.v1.json`, with `correlation_id` equal to the header. The 500 body carries no traceback, SQL, host, path or settings value |
| AC-12 (backend) | ✔ Redaction, CORS and headers (G2). Audit clean. Fake-secret drill fails `security`. Containers non-root. Workflows read-only, SHA-pinned, no `pull_request_target` |
| AC-13 (backend) | ✔ Coverage drill fails `unit` (70.27 % < 85 %). Lint/type drill fails `static`. Release SHA 94.48 % |

**Verdict: Gate G5 — PASS.**

### 11.6 CP5 deviations, findings and risks

| ID | Item | Status |
|---|---|---|
| E-27 | **Security finding fixed:** the `psycopg[binary]` wheel bundles C libraries built on EL8, including `libpcre2` 10.32 (8 HIGH/CRITICAL findings) and OpenSSL 1.1.1k, which OS updates never patch. Runtime now uses pure `psycopg` with Debian's `libpq5` (pinned `17.11-0+deb13u1`). `psycopg-binary` is dev-only (local and CI tests) | Fixed. Images verified. Local/CI tests still use the binary build (accepted: not shipped) |
| E-28 | B-25 asks a **second engineer** to follow the README. There is one maintainer, so Claude followed the README step by step on a clean clone (§11.2) | Owner may repeat it; otherwise accepted |
| E-29 | Base image `python:3.12.15-slim-trixie` (published 2026-10-21) is newer than the two-week supply-chain lag applied to PyPI. The 3.12.12 base had 83 fixable HIGH/CRITICAL OS findings; the current one has 0. Local Python is 3.12.12; images use 3.12.15 (same minor, `requires-python ==3.12.*`) | Security over lag for OS images; recorded |
| E-30 | Trivy gate fails on **fixable** HIGH/CRITICAL findings, any Python-package finding, secrets and Dockerfile misconfiguration. 44 unfixed Debian findings are reported, not gating, so CI does not depend on upstream fix timing | Risk accepted; revisit when releasing to an environment |
| E-31 | `libpq5` is pinned to an exact Debian version. A future Debian point release removes it from the mirror, so builds will fail until the pin is bumped in a reviewed PR | Deliberate (reproducible, reviewed updates) |
| E-32 | CI `images` initially failed after **all checks had passed**: root-owned Trivy cache files made the cleanup trap fail on Linux. Trivy now runs as the invoking user, and cleanup never overrides the result. Also found before push: the URL-password rule flagged `${VAR}` placeholders; it now allows exactly `${NAME}` references, and literals are still flagged (tests) | Fixed |
| E-33 | `opentelemetry-api` is a transitive dependency of taskiq. Atlas never imports or configures it (no tracing or telemetry; scope exclusion unaffected) | Noted |
| E-34 | In the drill, `static` stops at the first failing step (Ruff), so mypy's failure was shown locally on the same commit. In the fake-secret drill, `make security` fails before the dedicated Trivy step | Behaviour as designed |
| E-35 | `pg_hba` hardening (DEC-084) is still not applied. Locally, passwords are not enforced; CI and the image check enforce scram | Open owner decision |
