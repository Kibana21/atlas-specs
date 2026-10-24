# ATLAS-001 — Evidence Record

**Status:** **Gate G1 PASSED**, **Gate G2 PASSED** (2026-10-24). CP1 (S-01…S-12) and CP2 (B-01…B-08, B-27, B-28) complete; CP3 **not started** (awaiting owner authorization). ATLAS-001 **not Accepted** (G7).
**Baseline:** spec v0.2.2 (controlled amendment of v0.2.1) with plan/tasks/acceptance v0.2.1 — Approved for Implementation (owner, 2026-10-24); CP1 authorized.

## 1. Approvals and decisions in force

| Item | State (2026-10-24) |
|---|---|
| P-01 specification set v0.2.1 | Approved for Implementation |
| P-02 D-07 stack decisions | Approved (register v0.3/v0.4) |
| P-03 PostgreSQL four-role SQL | Approved as design; **execution not authorized** |
| P-05 pinned images / PyPI / local venvs / temporary containers | Confirmed |
| P-06 / DEC-085 repository visibility | **PUBLIC** (owner decision); CI Mode A |
| P-08 change workflow | Confirmed, then **superseded by the owner's standard workflow (2026-10-24):** Claude creates the feature branch and PR, waits for required checks, reviews the diff, merges when all gates pass, and confirms `main` CI. Never force-push shared branches, bypass protection, or merge failing checks |
| P-09 contract release `0.1.0` | **Approved conditionally** (owner, 2026-10-24); all conditions verified (§6) → tag created |
| Amendments A1/A2/A3 (E-01/E-03/E-04) | Approved (A1, A2) / accepted provisionally (A3); spec v0.2.2 |
| DEC-084 `pg_hba` hardening | Approved in principle; not applied (re-verify before CP3) |

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
