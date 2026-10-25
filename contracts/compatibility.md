# Atlas Contract Compatibility, Pinning and Release Rules

**Applies to:** `contracts/openapi/atlas-api.yaml`, `contracts/schemas/*`, `design/tokens.json` · **Status:** Approved for ATLAS-001 (spec v0.2.1 FR-04, §6.4; DEC-039 as approved with modification)

## 1. Versioning

The contract version is `info.version` in `atlas-api.yaml`, using semantic versioning:

| Change | Version bump | Examples |
|---|---|---|
| **Breaking** | MAJOR (and a new `/api/vN` prefix once 1.0.0 is released) | Remove or rename an operation, path, parameter, response field, enum value or status code; make an optional request field required; tighten a type or pattern; change the meaning of a field |
| **Additive** | MINOR | New operation; new optional request field; new response field; new enum value *in a request*; new error code in the catalog |
| **Clarifying** | PATCH | Descriptions, examples, typo fixes; no schema or behaviour change |

Before 1.0.0, breaking changes bump MINOR, but **are still treated as breaking** for rollout and release approval (§4).

**Pre-release versions:** between approved releases, `info.version` carries the *next* version with a development suffix: `X.Y.Z-dev.N`, where `N` increases with each merged change. Example: after release `0.1.0`, the first additive change becomes `0.2.0-dev.1`.

## 2. Pinning (development and CI)

- Consumers (`atlas-backend`, `atlas-frontend`) record a `specs.lock`:

  ```yaml
  specs_repo: atlas-specs
  specs_commit: "<40-hex SHA>"
  api_contract: contracts/openapi/atlas-api.yaml
  schemas_dir: contracts/schemas
  tokens: design/tokens.json
  contract_version: "0.1.0"
  ```

- `specs_commit` is a **full 40-character SHA** of a commit that is reachable from `atlas-specs` `main`. Branch names, tag names and short SHAs are rejected.
- `contract_version` must equal `info.version` at that commit.
- Development and CI may pin **any** such commit. They never track a moving branch, and never fetch `atlas-specs` at runtime.
- `tools/check_specs_lock.py` enforces these rules.

## 3. Releases and tags

- A **contract release** is an owner-approved version of the contract. Only releases receive a tag: `contract-vX.Y.Z` on the merged `main` commit, with `info.version` equal to `X.Y.Z` (no pre-release suffix). **Tags are not created for every change.**
- The owner approves a release after reviewing the contract diff since the previous release, plus the breaking-change report (`make breaking`).
- **Release builds** of consumers, i.e. version tags such as `atlas-backend v0.1.0`, must pin a commit that carries a `contract-v*` tag. Check with `tools/check_specs_lock.py --release`.
- Tags are immutable: never moved or deleted. A wrong release is superseded by a new one.

## 4. Breaking-change control

- Specs CI compares the contract on every change against the **latest release tag** using oasdiff's breaking-change detection, and fails on errors unless the MAJOR version (MINOR before 1.0.0) was bumped.
- A breaking change requires:
  - an explicit note in the change description;
  - owner approval at release time;
  - a coordinated rollout (§5).

## 5. Rollout order

| Change type | Order |
|---|---|
| Additive | 1. specs merged → 2. backend implements and pins it, deploys → 3. frontend pins it and uses it |
| Breaking | Parallel version: the old and new operations or prefixes coexist until all consumers have moved. Never deploy an incompatible frontend/backend pair. Backend removes the old version only after the frontend no longer uses it |

## 6. Deprecation

A deprecated operation or field is marked `deprecated: true` in the contract. It keeps working for at least one release. Its removal is a breaking change (§1).

## 7. Design tokens

`design/tokens.json` follows the same pinning rules (it is read at the `specs.lock` commit). Token value changes are reviewed as additive; removing or renaming a token is breaking for the frontend.

## 8. Canonical graph contracts (ATLAS-002)

- `contracts/taxonomy/atlas-taxonomy.v1.json` carries its own semantic version (`taxonomy_version`, 1.0.0). MINOR adds; MAJOR removes, renames, narrows or makes an attribute required, and needs a data migration plan and owner approval (ADR-0017 §1).
- `contracts/schemas/canonical/*.v1.json` are versioned by the `vN` in their `$id`. A breaking change creates `v2` beside `v1`.
- None of these change the OpenAPI contract or `info.version`; `contract-v0.1.0` remains the API baseline. Consumers pin them through the same `specs.lock` commit SHA.
