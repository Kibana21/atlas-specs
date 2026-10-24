# ATLAS-001 — Evidence Record

**Status:** Interim — **Gate G1 not complete.** CP1 tasks S-01…S-11 done and verified; S-12 (release tag `contract-v0.1.0`) **awaiting owner approval P-09**. ATLAS-001 **not Accepted**.
**Baseline:** spec/plan/tasks/acceptance v0.2.1 — Approved for Implementation (owner, 2026-10-24), CP1 authorized only.

## 1. Approvals and decisions in force

| Item | State (2026-10-24) |
|---|---|
| P-01 specification set v0.2.1 | Approved for Implementation |
| P-02 D-07 stack decisions | Approved (register v0.3/v0.4) |
| P-03 PostgreSQL four-role SQL | Approved as design; **execution not authorized** |
| P-05 pinned images / PyPI / local venvs / temporary containers | Confirmed |
| P-06 / DEC-085 repository visibility | **PUBLIC** (owner decision); CI Mode A |
| P-08 change workflow | Confirmed — feature branches only; owner opens and merges PRs |
| P-09 contract release `0.1.0` | **Pending** |
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

## 6. Proposed contract release (S-12) — not created

- **Release:** `contract-v0.1.0` (contract `info.version` 0.1.0).
- **Release commit:** the `main` commit produced when the owner merges this branch. Its SHA is known only after the merge. The content fingerprint to verify is the **git tree hash** of the branch head (recorded in the G1 report); the merged commit must have the identical tree before tagging.
- **Pre-tag checks (after merge, before tag):** `make check` on the merged `main` commit; specs-ci green on that commit; tree hash equal to the reviewed branch head.
- **Not done:** no tag created or pushed. Requires explicit P-09 approval.

## 7. Deviations and open items for G1

| ID | Item | Status |
|---|---|---|
| E-01 | FR-02 named one `health.v1` schema; delivered `health-live.v1` + `health-ready.v1` because a union schema accepted an invalid readiness body | Refinement — owner acknowledgement requested |
| E-02 | Config files introduced earlier than their task for verification (`.markdownlint-cli2.yaml` in S-01, `redocly.yaml` in S-04, `tools/images.lock` in S-07), finalized in S-10 | Sequencing only |
| E-03 | Relationship colour and sizing tokens added per the owner's CP1 instruction §10 (spec §7.1 did not list them) | Owner instruction — spec §7.1 amendment pending in a later revision |
| E-04 | `api` text on its own tint passes at exactly 4.50:1 (zero margin) | Palette decision for DEC-065; value unchanged |
| E-05 | Whitespace-only lint fixes in non-baseline documents (incl. approved ATLAS-001 docs); `git diff -w --ignore-blank-lines` shows only a code-fence language, one heading level and backticks around a literal | Formatting only |
| E-06 | `breaking` tagged path proven only locally (no release tag exists on GitHub yet) | Re-verified in CI after `contract-v0.1.0` exists |
