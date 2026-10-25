# ATLAS-002 — Release proposal (A2-T22)

**Date:** 25 October 2026 · **Decision:** **Option A — no ATLAS-002 release tags** (owner, 25 Oct 2026, CP5 decision 1) · **Status:** Decided; the release itself is deferred

## 1. Decision

- No release tag is created for ATLAS-002: no `contract-v*`, no backend `v*`, no frontend `v*`.
- ATLAS-002 is accepted (at G5) against the verified `main` commits recorded below, with their CI runs.
- `info.version` in `contracts/openapi/atlas-api.yaml` stays `0.1.0`. It is not bumped to make tagging possible.
- DEC-039 and `contracts/compatibility.md` are not amended now.
- Release tagging is decided when a **consumer release** is planned, that is, when an API or UI capability first uses the canonical store.

Why: the canonical foundation exposes no deployable API or UI capability (`scope.md`, out of scope: graph-reading APIs, frontend). Nothing is deployed from it yet, so a release tag would add no consumer value.

## 2. Verified `main` commits

| Repository | Commit | `main` CI run | Required checks |
|---|---|---|---|
| atlas-specs | `9ea2b7ed88fafdf483fc495a9fa67be89c1792f1` (G4 evidence, #29); the CP5 documentation merge is recorded in `evidence.md` §12 | [40191059640](https://github.com/Kibana21/atlas-specs/actions/runs/40191059640) | `docs-lint`, `contract`, `tools`, `tokens`, `registry`, `breaking`: all success |
| atlas-specs (contract and rules pinned by the backend) | `3d4002f11f675a4f7520e22abb1b1c4b10e29be1` (#28) | [40189106561](https://github.com/Kibana21/atlas-specs/actions/runs/40189106561) | all six success |
| atlas-backend (code) | `e9737587c4f7e5c25eda62257aba43ea2d9cb7ed` (#11); `specs.lock` → `3d4002f` | [40190186641](https://github.com/Kibana21/atlas-backend/actions/runs/40190186641) | `static`, `unit`, `contract`, `security`, `integration`, `images`: all success (plus `benchmark`) |
| atlas-frontend | `8ed5deb895dced78f98bff13cedd14c28a70f4ac` (unchanged by ATLAS-002 after CP0) | [40095359958](https://github.com/Kibana21/atlas-frontend/actions/runs/40095359958) | all seven success |

The CP5 documentation-only backend merge (`CLAUDE.md`, PR #12) is `0d37b6e0709a4f3603dd4b7373ac330ae7974b69`. Its `main` run [40194599204](https://github.com/Kibana21/atlas-backend/actions/runs/40194599204) is 6/6 success, and its code is identical to `e973758`.

Existing release tags are unchanged and remain the latest releases: `contract-v0.1.0` → `bfe4a09`, backend `v0.1.0` → `585f3f5`, frontend `v0.1.0` → `b9f235e`.

## 3. The release-governance conflict (recorded, not resolved)

| Rule | Text (`contracts/compatibility.md`) | Effect for ATLAS-002 |
|---|---|---|
| §3 | A release build of a consumer (for example backend `v0.2.0`) must pin a specs commit that carries a `contract-v*` tag, and the tag's version must equal `info.version` | The backend pins `3d4002f`, which carries no tag |
| §3 | `contract-vX.Y.Z` requires `info.version == X.Y.Z`; tags are immutable | `contract-v0.1.0` already exists and `info.version` is still `0.1.0`, so no new contract tag is possible without a version change |
| §8 | Taxonomy, canonical schemas and the trust function have their own versions and **do not change** the OpenAPI `info.version` | Taxonomy 1.1.0, schemas v1 and trust-1 cannot raise `info.version` |

Under the current rules, a backend release that contains the canonical store cannot be tagged: §3 needs a new contract tag, and §8 gives the canonical contracts no way to produce one. The owner chose not to resolve this now.

## 4. Options for the future release decision (not decided)

These are recorded for the decision at the first consumer release. None is approved.

| Option | Summary | Needs |
|---|---|---|
| B | Amend DEC-039 / `compatibility.md` so canonical contracts can be released and tagged on their own (for example a canonical-contract tag), and let release builds pin that | Owner approval of a governance change |
| C | Release a new OpenAPI version when the first consumer API lands. That work changes the OpenAPI anyway (MINOR, additive), so a `contract-v0.2.0` tag would follow the existing rules | Nothing new: this is the normal path once an API exists |
| — | Bump `info.version` without an API change | **Rejected** by the owner (CP5 decision 1) |

Note (observation, not a recommendation): the first consumer of the canonical store is expected to be a graph-reading API, which changes the OpenAPI contract. Option C would then apply without a rule change.

## 5. Conditions that apply to any future release containing the canonical store

- **PG-1** must pass before any release with interactive writes or Scale A data (`acceptance.md`; `follow-ups.md` F-01).
- The follow-ups in `follow-ups.md` are open, and are not completed by this decision.
- Every release tag needs the owner's approval (A2-T22; `compatibility.md` §3).
