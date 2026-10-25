# ATLAS-002 — Canonical Graph Foundation: Specification (CP3–CP5)

**Version:** 0.1 · **Date:** 25 October 2026 · **Status:** **Proposed** (CP2 deliverable; updated at Gate G2, 25 Oct 2026, for owner decisions U-1…U-7). CP3–CP5 are **not authorized**: each needs the owner's explicit authorization. Built on the Accepted ADR-0001, 0003, 0008, 0015–0019 and the CP2 contracts.

## 1. Scope

Backend implementation of the canonical store, with no graph-reading API, UI, connector, worker or authentication:

| CP | Repository | Content |
|---|---|---|
| CP3 | atlas-backend (+ the owner-run role bootstrap) | Migration `0002`, constraints, two triggers, grants, taxonomy seed, normalizers, repository layer with `OrgScope`, domain validator, privilege tests |
| CP4 | atlas-backend | Deterministic fixture loader and import planner (ingestion role), integrity suite at every revision, revert, pilot-size benchmark |
| CP5 | all | Evidence, releases, owner acceptance |

Out of scope: graph-reading APIs (invariant 4: authorization first, ATLAS-003), frontend changes, connectors and discovery syncs, reconciliation workflow and UI, drafts and branches, search and `pg_trgm`, partitioning, PostgreSQL extensions, any graph database.

## 2. Inputs (pinned)

- `atlas-specs` at the CP2 merge commit, through `specs.lock`: `contracts/taxonomy/atlas-taxonomy.v1.json`, `contracts/schemas/canonical/`, `contracts/canonical-validation-rules.md`, `contracts/trust-function.md`, `acceptance/test-data/canonical-golden-v1/`, `acceptance/test-data/trust-function-v1/cases.json`. Taxonomy **1.1.0**.
- The OpenAPI contract is unchanged; the released `contract-v0.1.0` stays the API baseline.

## 3. Functional requirements

| ID | Requirement | Source |
|---|---|---|
| A002-FR-01 | Migration `0002` creates the canonical tables of ADR-0001 (as amended by ADR-0003, 0008 §10, 0019) in schema `atlas`, with organization-leading keys, composite FKs, partial unique indexes and `CHECK` constraints. No extension. Downgrade works on empty databases | ADR-0001, ADR-0016 |
| A002-FR-02 | Exactly two triggers (plain PL/pgSQL): set-once `revision_to` on every versioned table; server-set `created_at` and `db_role` on `change_set` | ADR-0008 §2, §10 |
| A002-FR-03 | Grants per the DEC-044 amendment matrix; `atlas_app` gets no canonical write privilege; the migration fails if the ingestion role is missing | DEC-044 (amended) |
| A002-FR-04 | Reference tables (`provider`, `category`, `identity_namespace`, `native_type_mapping`, `actor_namespace`, `entity_type`, `relationship_type`, `relationship_rule`, `attribute_rule`) seeded from the pinned taxonomy; a CI check compares the seed with the artifact | ADR-0017 §1 |
| A002-FR-05 | Identity normalizers for the approved rules only, passing the same golden examples as `tools/canonical_model.py`; planned and reserved namespaces rejected | ADR-0003 |
| A002-FR-06 | Repository layer: every read and write takes an `OrgScope`; a query without it does not type-check; cross-organization access returns "not found" | ADR-0016 |
| A002-FR-07 | Domain validator implementing the DOMAIN rules (D-01…D-18) in the publishing transaction, with readable reasons; ADVISORY findings reported, never blocking | Rules v1 |
| A002-FR-08 | Publishing procedure of ADR-0008 §3: counter lock, diff, validate, write, integrity checks (H-10, H-14, D-09), commit; no change set for an unchanged input | ADR-0008 |
| A002-FR-09 | Fixture loader CLI (CP4) running as the ingestion role: loads the golden fixture's stored rows for tests, and applies import batches through the planner; actor from the execution context only | ADR-0008 §8, §10 |
| A002-FR-10 | Revert as a new change set, refused on conflict | ADR-0008 §7 |
| A002-FR-11 | As-of reconstruction and graph hash identical to the reference definitions (`expected-as-of.json`) | ADR-0008 §4, §6 |
| A002-FR-13 | Trust function v1 (`trust-1`) as a pure, versioned function in the publishing transaction: stored trust states and verification follow `contracts/trust-function.md` (D-12, D-19, D-20); the backend passes every case of `trust-function-v1/cases.json` and reproduces every stored trust state of the golden fixture | ADR-0018, owner decision U-3 |
| A002-FR-12 | Pilot-size benchmark (10k entities / 40k relationships) generated synthetically, run in CI or a disposable environment only, never on the shared server | ADR-0001 |

## 4. Non-functional requirements

| ID | Requirement |
|---|---|
| A002-NFR-01 | PostgreSQL 15 only; no extension; no server setting change |
| A002-NFR-02 | All test data synthetic; Scale A data never on the shared server |
| A002-NFR-03 | Coverage and quality gates of ATLAS-001 (lint, type checks, tests) stay green |
| A002-NFR-04 | No Redis use for the canonical store |

## 5. Dependencies

| # | Dependency | Owner gate |
|---|---|---|
| DP-1 | ~~Ingestion roles exist locally before migration `0002` runs locally~~ **Superseded locally (owner decision, 25 Oct 2026):** the single-user model (`atlas_db_user`; ADR-0001 §Privileges, DEC-044, TD-DEV-010) | G3-R not required locally |
| DP-2 | Backend `specs.lock` pins the CP2 merge commit | CP3 |
| DP-3 | Backend CI bootstraps the ingestion roles from a verbatim copy of the approved script | CP3 |
| DP-4 | Frontend CI's e2e job runs the same bootstrap once `e2e/backend.ref` moves past migration `0002` | When the frontend next moves its backend pin |

## 6. Gate G3-R: database-role bootstrap (separate, owner-controlled)

**Not required locally (owner decision, 25 Oct 2026).** Local development uses the single-user model. The steps below and the scripts stay as the production-hardening procedure; CI runs the scripts on every change.

1. Claude writes `features/ATLAS-002-canonical-graph-foundation/proposals/postgres-ingest-roles.sql` exactly as designed in `proposals/dec-044-amendment.md` §7 (guards, two roles, `CONNECT`, `USAGE`, settings), with `postgres-ingest-roles-verify.sql` (read-only), `postgres-ingest-roles-rollback.sql` and the owner runbook `g3r-runbook.md`. This is a specs PR, reviewed. **Done in CP3.**
2. The owner reviews it, creates the two passwords, and runs it as the local superuser. Claude never creates credentials and never runs it.
3. Claude verifies with read-only catalog queries (`atlas doctor`) and records the evidence.
4. Only then is migration `0002` run against the local `atlas_test` (and `atlas_db` only with separate approval). CI uses its own ephemeral server throughout.

## 7. Items raised in CP2 and the owner's G2 decisions (25 Oct 2026)

| # | Item | Owner decision | Applied |
|---|---|---|---|
| U-1 | `CONTAINS` and `DEPLOYED_AS` didn't accept `contract` evidence | Narrow taxonomy clarification. Provider configuration evidences observed containment and deployment. IaC evidences declared ones, never live deployment. OpenAPI evidences documented API structure, never infrastructure deployment. The semantics stay; no relationship is invented | Taxonomy **1.1.0** (MINOR): `contract` allowed for both types; ADR-0017 §4.1 amended. Contract-only facts are `documented` and can't alone support verifying a physical claim (TF-6, TF-V). The fixture now uses IaC and OpenAPI evidence where 1.0.0 forced documents |
| U-2 | `native_type` wording for `azure.tenant` | Retain the exemption; minimum documentation correction | ADR-0017 §2.1 and §2.2 and ADR-0019 §3 state the exemption. Correction to the CP2 report: the exemption had been explicit only in the taxonomy artifact and the validator; both ADRs used the general wording |
| U-3 | Trust for mixed evidence | Conservative, claim-aware, deterministic. VERIFIED needs applicable, sufficiently authoritative evidence and no unresolved contradiction. No universal source ranking, no verification from evidence count, no silent promotion where authority or freshness is undefined | `contracts/trust-function.md` (approved for CP3 at G2 closure); truth table of 36 cases; validator D-12 (equality), D-19, D-20. C-1 (IaC is declared evidence) and C-2 (claim-specific `discovered`) **approved at G2 closure**; ADR-0018 amended |
| U-4 | Relationship `environment_id` when cross-environment | Accepted: nullable, classification from endpoint memberships | Interpretation I-1 marked accepted |
| U-5 | Rejected import items | Preserve them with reasons in the approved import-report mechanism | Unchanged: the import report (`expected-report.json`) records rule and reasons; nothing is stored as a graph fact |
| U-6 | Non-Azure `scope_kind` vocabularies; unconfirmed provider ID formats | Record the limitations | §7.1 |
| U-7 | 617 relationships against ~700 | Accepted | — |

New from G2 work, **approved at G2 closure**: **I-6**. A required attribute whose sources disagree, with no prior approved value, is left absent on a `conflicted` fact. It is never filled with one source's value (ADR-0018 conflict procedure; invariant 3).

### 7.1 Recorded limitations

- **Provider ID formats:**
  - AWS, Google Cloud, Alibaba Cloud and OCI identities are `validation_only`: the approved format is checked and case is preserved, but no normalization rule exists;
  - Huawei Cloud, Tencent Cloud and IBM Cloud namespaces are `planned` and rejected;
  - `apim.operation` is `reserved`.

  Each needs an approved rule before its identities can match across sources (ADR-0003, ADR-0019 onboarding).
- **Non-Azure hierarchies:** `provider_scope_rules` for providers other than Azure are marked `intended_shape`. They are confirmed per provider at onboarding (ADR-0019 §4). Until then, D-16 checks fixtures against the intended shape only.
- **Freshness and precedence:**
  - no per-source freshness policy (DEC-072, Open) and no field precedence (DEC-034, Proposed) is approved;
  - the trust function therefore never makes a fact stale by age outside the fixture's synthetic policy;
  - it never resolves a disagreement automatically.
- **Publication performance (release limitation, owner instruction at G4, 25 Oct 2026):** the publishing procedure loads and validates the organization's whole current state on every publish (CP3-D7). Measured cost grows linearly with organization size (`evidence.md` §9.3: at 10k entities / 40k relationships, a one-entity change takes 4.8 s and a no-op 3.6 s). This is acceptable for the initial fixture load and batch imports; it is **not** approved as the interactive-editing implementation. Narrowing the load to the touched facts and their neighbours, and passing the future performance gate PG-1 (`acceptance.md`), are required before any release with interactive writes or Scale A data. No publishing-engine redesign is part of G4 closure.

## 8. Acceptance

See `acceptance.md`. ATLAS-002 is Accepted only at Gate G5.
