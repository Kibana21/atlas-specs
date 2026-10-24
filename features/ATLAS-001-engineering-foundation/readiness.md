# ATLAS-001 — Implementation Readiness Summary and Final Approval Request

**Date:** 24 October 2026 · **Specification set:** `spec.md` v0.2.1, `plan.md` v0.2.1, `tasks.md` v0.2.1, `acceptance.md` v0.2.1 · **Register:** `decisions/decision-register.md` v0.3
**Status:** **Approved for Implementation** (owner, 24 Oct 2026). **Checkpoint 1 authorized**; CP2–CP7 not authorized. ATLAS-001 **not Accepted** until G7.

## Owner decisions recorded on 24 Oct 2026

| Item | Decision |
|---|---|
| A — specification set v0.2.1 | **Approved for Implementation** (implementation baseline; not feature acceptance) |
| B — four-role PostgreSQL model | **Approved as design.** SQL **not authorized for execution**; no PostgreSQL change during CP1 |
| C — P-05 / P-08 | **Confirmed**, with the controls listed in the approval: no global installs, no mutable `latest` tags, temporary containers removed, no shared-service access, no new dependencies without approval; feature branches only, never `main`, never self-merge, no force-push to shared branches, no credential exposure |
| D — DEC-085 visibility | **PUBLIC** for all three repositories (explicit owner decision). Mode A CI; public-repository safety rules mandatory (spec §6.8) |
| E — DEC-084 `pg_hba` hardening | **Approved in principle, not applied.** Before CP3: verify rule precedence and rollback, effective `CONNECT`/`PUBLIC` grants, and that other projects are unaffected; then request explicit authorization |
| P-09 | **Pending.** No `contract-v0.1.0` tag until explicitly approved |

The sections below are the pre-approval readiness analysis, kept for the record.

Nothing in this round changed PostgreSQL, Redis, GitHub settings, repository visibility or the local Node installation. No production code was written, and nothing was committed. Verification used read-only queries and disposable containers from images already on the machine.

---

## 1. Requested checks — results

| # | Check | Result | Where |
|---|---|---|---|
| 1 | Review the PostgreSQL roles; explain purpose and minimum privileges; simplify if safe | **Simplified 6 → 4 roles** (`atlas_migrator`, `atlas_app`, `atlas_test_migrator`, `atlas_test_app`). The NOLOGIN owner roles were removed: their only benefit, credential rotation without ownership transfer, is irrelevant for local/CI, and they forced an error-prone `SET ROLE` in Alembic. **Runtime default narrowed to read-only**: writes are granted per table in reviewed migrations. Re-tested in a disposable container: every guard, privilege, denial and the rollback behave as specified | spec §6.2; `proposals/postgres-local-setup.sql` |
| 2 | Document local trust-auth limitation; ensure stronger CI auth | Documented. Locally, `trust` means passwords aren't verified. **New finding:** the default `PUBLIC` `CONNECT` lets Atlas roles connect to other projects' databases. Mitigations: `make doctor` warns; CI enforces **`scram-sha-256`** for every connection with random per-run passwords and a `ci_auth` test (FR-39), verified in a CI-like container (wrong and missing passwords rejected). Optional Atlas-only `pg_hba` hardening validated: Atlas roles must use passwords and are rejected on non-Atlas databases, other users unaffected | spec §6.2, FR-35, FR-39; `proposals/pg_hba-atlas.conf`; DEC-084 |
| 3 | Treat repository visibility as an explicit security decision; recommend private | DEC-085 reframed as a security decision. **Recommendation: private by default.** Consequences listed, including that private repos on a personal GitHub Free account generally lose rulesets/branch protection without GitHub Pro, plus Actions-minute quotas and the need for a GitHub App for cross-repo CI. **Visibility not changed** | spec §6.8; `ci-access.md` §1, §6 |
| 4 | Precise list of external services, credentials and permissions for checkpoint 1 | §2 below | — |
| 5 | Confirm 53 tasks in seven checkpoints with independently verifiable gates | Confirmed. v0.2.1 changed task content, not structure (§4) | `tasks.md` |
| 6 | Readiness summary with genuine blockers to checkpoint 1 | §3 below | — |

D-07 decisions are applied as approved, with their modifications (register §A2):

- DEC-020: Python 3.12 with a pinning policy (FR-20a).
- DEC-024 and DEC-028: as approved.
- DEC-038: includes mypy and openapi-typescript.
- DEC-039: immutable-SHA pinning, with tags only for approved releases (spec §6.4).
- DEC-040: the Tech §17.3 difference recorded as TD-DEV-001 in the new `decisions/baseline-deviations.md`, to be reconciled through a controlled Technical Design revision.

## 2. Checkpoint 1 (`atlas-specs` only): external services, credentials and permissions

**Needed:**

| # | Item | Kind | Status today | Permission / scope required | Who provides |
|---|---|---|---|---|---|
| 1 | GitHub repository `Kibana21/atlas-specs` | Service | Exists; public; `main` only; no tags; no workflows | **Write** (push feature branches; later push tag `contract-v0.1.0`) | Owner's account |
| 2 | Local git credential | Credential (existing) | HTTPS remote with `osxkeychain` helper already configured | Used **as is** for pushes. **No new credential.** Claude never reads or prints it | Owner (P-08 confirms use) |
| 3 | GitHub web UI for PRs | Service | `gh` CLI not installed | Owner opens, reviews and merges PRs | Owner |
| 4 | GitHub Actions on `atlas-specs` | Service | Enabled by default for public repos (confirmed at first PR run) | Workflow token = built-in `GITHUB_TOKEN` with **`contents: read` only**. No secrets, variables or Apps | GitHub (default) |
| 5 | GitHub-hosted runner `ubuntu-latest` | Service | n/a | Runs Docker for the pinned images | GitHub (default) |
| 6 | Actions marketplace: `actions/checkout`, `astral-sh/setup-uv` | Dependency | n/a | Pinned by full commit SHA; read-only | Public |
| 7 | Docker Hub images `tufin/oasdiff`, `redocly/cli`, `davidanson/markdownlint-cli2` | Dependency | Docker 27.4 installed; `tufin/oasdiff:latest` present from the review probe (to be replaced by a pinned digest) | **Anonymous pull** of three digest-pinned public images, locally and in CI. No Docker Hub login | Owner permits local pulls (P-05) |
| 8 | PyPI | Dependency | uv 0.10.0 present; Python 3.12.12 available via uv | Anonymous download of the pinned `tools/` dependencies (PyYAML, jsonschema, check-jsonschema, pytest) into a **project-local** environment. No global install | Public |

**Not needed for checkpoint 1:**

- PostgreSQL and Redis (CP3/CP4);
- Node.js (no Node tooling in `atlas-specs`);
- GitHub App, PATs, deploy keys, repository secrets or variables;
- branch-protection rulesets (P-07, before G7);
- Azure, Entra ID, Key Vault;
- any container registry push;
- npm registry.

## 3. Readiness: blockers to checkpoint 1

| # | Item | Genuine blocker? | Needed for | Your action |
|---|---|---|---|---|
| 1 | **Explicit approval of the final specification set** (P-01) | **Yes**, it blocks every task | All | Approve (see §5) |
| 2 | **P-05** permission to pull three digest-pinned images locally | **Yes** for S-07/S-10 local verification. CI pulls on GitHub's runners regardless | S-07, S-10 | Permit, or refuse; then local runs skip those steps and rely on CI |
| 3 | **P-08** change workflow: Claude pushes feature branches with the existing credential; you open and merge PRs | **Yes**, the first push in S-01 | All of CP1 | Confirm, or specify another workflow |
| 4 | **P-09** approval of contract release `0.1.0` before tagging | Blocks only **S-12**, the CP1 exit | S-12 / G1 | Approve the release when S-01…S-11 are merged |
| 5 | **P-06 / DEC-085** repository visibility | **No** (CP1 works either way), but **recommended before CP1 merges** so new contracts and tokens aren't published | Security posture | Decide: private (recommended) or keep public for now |
| — | P-03 PostgreSQL SQL (and optional `pg_hba` hardening) | No, CP3 | CP3 | Later |
| — | P-04 Node.js 24 LTS install | No, CP6 | CP6 | Later |
| — | P-07 `main` ruleset | No, G7 | G7 | Later (plan-dependent if private) |

**Conclusion:** once you approve the specification set and confirm P-05 and P-08, checkpoint 1 has **no other blockers**. P-09 is needed only at the end of CP1, and DEC-085 is strongly recommended first but not required.

## 4. Structure confirmation: 53 tasks, 7 checkpoints, 7 gates

| CP | Repo | Tasks | Gate | ACs first proven at the gate | Preconditions |
|---|---|---|---|---|---|
| CP1 | atlas-specs | S-01…S-12 (12) | G1 | AC-01 (specs), AC-03 (self-tests, breaking), AC-14 (token contrast), AC-02 (release tag) | P-01, P-05, P-08, P-09 (S-12) |
| CP2 | atlas-backend | B-01…B-08 (8) | G2 | AC-08, AC-10, AC-12, AC-13 (backend unit), AC-04 (doctor), AC-07 (guards) | P-01 |
| CP3 | atlas-backend | B-09…B-12 (4) | G3 | AC-05 (DB), AC-06, AC-07 (privileges), AC-09 (revision) | **P-03** |
| CP4 | atlas-backend | B-13…B-17 (5) | G4 | AC-05 (Redis), AC-10 (worker), AC-11 | — |
| CP5 | atlas-backend | B-18…B-25 (8) | G5 | AC-01, AC-02, AC-03, AC-05 (images), AC-07 (CI auth), AC-12, AC-13 | G1; P-06 if private |
| CP6 | atlas-frontend | F-01…F-09 (9) | G6 | AC-08, AC-10, AC-12 (CSP), AC-14, AC-15 | G1, **P-04** |
| CP7 | frontend (F-10…F-14) + backend B-26 + specs S-13 (7) | — | G7 | AC-02 (parity, release tags), AC-04, AC-16, AC-17, sign-off | G5, G6, P-07 |
| **Total** | | **53** (specs 13 · backend 26 · frontend 14) | **7** | **17 ACs** | **9 preconditions** |

Every task changes exactly one repository and names its own verification command. Cross-repo flow is only through pinned SHAs, so each gate is verifiable with its checkpoint's repository alone, plus pinned read-only inputs.

## 5. Final approval request

Please reply with your decision on each item:

| # | Request | Recommendation |
|---|---|---|
| A | **Approve the ATLAS-001 specification set v0.2.1** (spec, plan, tasks, acceptance) as the implementation baseline. *This authorizes implementation starting at CP1. ATLAS-001 still becomes Accepted only at the G7 sign-off* | Approve |
| B | **Approve the simplified PostgreSQL role model** (4 roles, runtime read-only by default) as the design behind `proposals/postgres-local-setup.sql`. *The SQL is still applied only later, by you or with your explicit go-ahead (P-03)* | Approve |
| C | **Confirm P-05** (pull three digest-pinned images locally) and **P-08** (push feature branches with the existing credential; you open and merge PRs) | Confirm both |
| D | **Decide DEC-085**: make the repositories private (you change it; I make no visibility change), or keep public for now | Private, before CP1 merges |
| E | *(Optional, not blocking)* Decide DEC-084: apply `proposals/pg_hba-atlas.conf` before CP3 | Apply before CP3; it affects only Atlas roles |

On approval of A–C I will start CP1 with S-01 and stop at each gate for your review. **I will not mark ATLAS-001 Accepted** until you explicitly approve the final sign-off.
