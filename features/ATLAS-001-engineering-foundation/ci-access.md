# ATLAS-001 — CI Access, Permissions and Setup (GitHub Actions)

**Version:** 0.2 · **Date:** 24 October 2026 · **Decision:** DEC-047 (owner D-05, approved with modifications) · **Status:** Documentation only. **No GitHub credential, App, secret, variable, ruleset or setting has been created or changed.**

## 1. Facts (verified 24 Oct 2026)

- `Kibana21/atlas-specs`, `Kibana21/atlas-backend` and `Kibana21/atlas-frontend` return HTTP 200 from the unauthenticated GitHub API, so they are **public**.
- None of the repos has a `.github/` directory, so no workflows exist yet.
- The repos are owned by a personal account (`Kibana21`), not an organization.

**Owner decision DEC-085 (24 Oct 2026): all three repositories remain PUBLIC.** **Mode A is the approved configuration.** Mode B is kept only as documented contingency, in case visibility is ever changed by a separate owner decision. Engineering never changes visibility. Public-repository safety rules (spec §6.8) apply to every change.

## 2. Cross-repository needs

| Consumer workflow | Reads | At | Why |
|---|---|---|---|
| backend `contract` job | `atlas-specs` (`contracts/`, `tools/`) | SHA in backend `specs.lock` | Conformance check (spec §6.7) and schema contract tests |
| frontend `generated` job | `atlas-specs` (`contracts/`, `design/`) | SHA in frontend `specs.lock` | Client and tokens reproducibility |
| frontend `e2e` job | `atlas-backend` (whole repo) | SHA in frontend `e2e/backend.ref` | Run the real backend for browser E2E |
| frontend `e2e` job | `atlas-specs` | lock SHA | Lock parity, generated assets |

Every access is **read-only** at an **immutable SHA**.

## 3. Mode A — public repositories (**approved configuration**; no credentials)

- `actions/checkout` with `repository: Kibana21/<repo>`, `ref: <sha>`, `path: .deps/<repo>`, `persist-credentials: false`. The built-in `GITHUB_TOKEN` (or no token) can read public repositories.
- Workflow-level `permissions: {}`, with per-job `permissions: { contents: read }`.
- **No secrets, variables or Apps required.** No personal access tokens.

## 4. Mode B — contingency only, if visibility is ever changed by a separate owner decision (GitHub App installation tokens)

The built-in `GITHUB_TOKEN` is scoped to the repository running the workflow, so it **cannot** read another private repository. Use a GitHub App:

| Item | Setting |
|---|---|
| App name | `atlas-ci-reader` (owned by `Kibana21`) |
| Repository permissions | **Contents: Read-only**; **Metadata: Read-only** (always required by GitHub). Nothing else |
| Organization/account permissions | None |
| Webhook | Disabled (inactive) |
| Installation | "Only select repositories": `atlas-specs` and `atlas-backend` (the repos being *read*) |
| Consumer repo configuration | Actions **variable** `ATLAS_CI_APP_ID`; Actions **secret** `ATLAS_CI_APP_PRIVATE_KEY`, in `atlas-backend` and `atlas-frontend` only |
| Token minting | `actions/create-github-app-token` (pinned by commit SHA) with `owner: Kibana21` and `repositories: atlas-specs` (and `atlas-backend` in frontend E2E). Installation tokens are short-lived (about 1 hour) and limited to the installed repositories and permissions |
| Use | Pass the minted token to `actions/checkout` `token:` with `persist-credentials: false` |
| Rotation | Rotate the private key at least annually and on any suspected exposure. Delete old keys in App settings |
| Prohibited | Classic or fine-grained personal access tokens; deploy keys with write access; storing tokens in repository files |

The App private key is a stored secret, but the credential used by jobs is minted per run, read-only and expires quickly. This satisfies "avoid long-lived personal access tokens".

## 5. Workflow hardening (both modes)

- Trigger on `pull_request` and `push` to `main`. **Never** use `pull_request_target` to check out PR code.
- Pin third-party actions by full commit SHA. Dependabot (actions ecosystem) proposes updates. Enabling it is a later owner choice.
- `permissions: {}` at workflow level; jobs request `contents: read` only. No job needs write.
- Service containers: `postgres:15` with `POSTGRES_HOST_AUTH_METHOD=scram-sha-256` and `POSTGRES_INITDB_ARGS="--auth-local=scram-sha-256 --auth-host=scram-sha-256 --locale=C --encoding=UTF8"`, bootstrapped with the same four roles; and `redis:7.4`. They are created per job and isolated from every other user (DEC-045).
- Role passwords are generated per run (`openssl rand`), masked with `::add-mask::`, and never stored as secrets. The `ci_auth` test proves wrong or missing passwords are rejected (FR-39).
- Fork PRs:
  - Mode A: all jobs run without secrets.
  - Mode B: cross-repo jobs are skipped for forks with an explicit notice. Enable "Require approval for first-time contributors" in repo Actions settings (owner action).

## 6. Rulesets (E-08) — applied 2026-10-24 to atlas-specs and atlas-backend (owner-authorized; evidence §9.4)

**Enforceability (checked read-only 2026-10-24):** account `Kibana21` is on **GitHub Free** (personal); all three repositories are **public**; none has a ruleset or classic branch protection. Rulesets are available for public repositories on GitHub Free, so the settings below are enforceable as written. No bypass actors are configured, so they also bind the owner's account and Claude's merges through it.

**Prerequisite (amendment A6):** workflows run every required job on `pull_request` and on `push` to `main`. A required check can therefore never be satisfied by a skipped job.

### 6.1 Ruleset `protect-main` (one per repository; Settings → Rules → Rulesets → New branch ruleset, or `POST /repos/Kibana21/<repo>/rulesets`)

```json
{
  "name": "protect-main",
  "target": "branch",
  "enforcement": "active",
  "bypass_actors": [],
  "conditions": {"ref_name": {"include": ["~DEFAULT_BRANCH"], "exclude": []}},
  "rules": [
    {"type": "deletion"},
    {"type": "non_fast_forward"},
    {"type": "pull_request", "parameters": {
      "required_approving_review_count": 0,
      "dismiss_stale_reviews_on_push": false,
      "require_code_owner_review": false,
      "require_last_push_approval": false,
      "required_review_thread_resolution": false,
      "allowed_merge_methods": ["merge"]}},
    {"type": "required_status_checks", "parameters": {
      "strict_required_status_checks_policy": true,
      "do_not_enforce_on_create": false,
      "required_status_checks": "<per repository, below>"}}
  ]
}
```

| Repository | `required_status_checks` (context names; GitHub Actions app `integration_id` 15368) | Grows with |
|---|---|---|
| `atlas-specs` | `docs-lint`, `contract`, `tools`, `tokens`, `registry`, `breaking` | — |
| `atlas-backend` | `static`, `unit`, `contract`, `security` (from CP2), `integration` (from CP3), `images` (from CP5) | — |
| `atlas-frontend` | `static`, `unit`, `generated`, `build`, `security`, `image` (applied CP6) | `e2e` (CP7) |

**Why these values:**

- **Zero required approvals:** with a single maintainer, authors cannot approve their own PRs, so any required approval would block every merge. Raise it once a second maintainer exists (DEC-081).
- **Strict up-to-date checks:** a PR must pass against the current `main`.
- **Merge commits only:** this keeps release trees and task-commit traceability (PR #1).

### 6.2 Ruleset `immutable-release-tags` (`atlas-specs`; later also `v*` in the other repos)

```json
{
  "name": "immutable-release-tags",
  "target": "tag",
  "enforcement": "active",
  "bypass_actors": [],
  "conditions": {"ref_name": {"include": ["refs/tags/contract-v*"], "exclude": []}},
  "rules": [{"type": "update"}, {"type": "deletion"}]
}
```

Tag *creation* stays allowed, so approved releases can still be published. Moving or deleting a release tag becomes impossible.

### 6.3 Other settings

- **CODEOWNERS:** `* @Kibana21`, committed by tasks S-11, B-28 and F-11.
- **Actions:** allow GitHub-owned and SHA-pinned actions. The default workflow token permission is **read**.
- **Branch hygiene:** "Automatically delete head branches" may be enabled. Merged feature branches are not needed after merge, because commits remain on `main`.

## 7. Owner checklist (only when needed)

1. Mode A: nothing to create.
2. Before making any repo private: create the `atlas-ci-reader` App (§4), install it on `atlas-specs` and `atlas-backend`, and add the variable and secret to `atlas-backend` and `atlas-frontend`. Workflows already contain the Mode B branch (if `vars.ATLAS_CI_APP_ID` is set, mint a token; otherwise use Mode A).
3. Now that every required check has run at least once on `main`, apply §6.1 to each repository with CI and §6.2 to `atlas-specs`. Claude verifies them read-only afterwards.
