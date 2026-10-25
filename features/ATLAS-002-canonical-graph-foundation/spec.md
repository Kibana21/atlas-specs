# ATLAS-002 — Canonical Graph Foundation: Specification (CP3–CP5)

**Version:** 0.1 · **Date:** 25 October 2026 · **Status:** **Proposed** (CP2 deliverable). CP3–CP5 are **not authorized**: each needs the owner's explicit authorization. Built on the Accepted ADR-0001, 0003, 0008, 0015–0019 and the CP2 contracts.

## 1. Scope

Backend implementation of the canonical store, with no graph-reading API, UI, connector, worker or authentication:

| CP | Repository | Content |
|---|---|---|
| CP3 | atlas-backend (+ the owner-run role bootstrap) | Migration `0002`, constraints, two triggers, grants, taxonomy seed, normalizers, repository layer with `OrgScope`, domain validator, privilege tests |
| CP4 | atlas-backend | Deterministic fixture loader and import planner (ingestion role), integrity suite at every revision, revert, pilot-size benchmark |
| CP5 | all | Evidence, releases, owner acceptance |

Out of scope: graph-reading APIs (invariant 4: authorization first, ATLAS-003), frontend changes, connectors and discovery syncs, reconciliation workflow and UI, drafts and branches, search and `pg_trgm`, partitioning, PostgreSQL extensions, any graph database.

## 2. Inputs (pinned)

- `atlas-specs` at the CP2 merge commit, through `specs.lock`: `contracts/taxonomy/atlas-taxonomy.v1.json`, `contracts/schemas/canonical/`, `contracts/canonical-validation-rules.md`, `acceptance/test-data/canonical-golden-v1/`.
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
| DP-1 | Ingestion roles exist locally (`atlas_ingest`, `atlas_test_ingest`) before migration `0002` runs locally | **G3-R** (owner-controlled, below) |
| DP-2 | Backend `specs.lock` pins the CP2 merge commit | CP3 |
| DP-3 | Backend CI bootstraps the ingestion roles from a verbatim copy of the approved script | CP3 |
| DP-4 | Frontend CI's e2e job runs the same bootstrap once `e2e/backend.ref` moves past migration `0002` | When the frontend next moves its backend pin |

## 6. Gate G3-R: database-role bootstrap (separate, owner-controlled)

1. Claude writes `features/ATLAS-002-canonical-graph-foundation/proposals/postgres-ingest-roles.sql` exactly as designed in `proposals/dec-044-amendment.md` §7 (guards, two roles, `CONNECT`, `USAGE`, settings, rollback). This is a specs PR, reviewed.
2. The owner reviews it, creates the two passwords, and runs it as the local superuser. Claude never creates credentials and never runs it.
3. Claude verifies with read-only catalog queries (`atlas doctor`) and records the evidence.
4. Only then is migration `0002` run against the local `atlas_test` (and `atlas_db` only with separate approval). CI uses its own ephemeral server throughout.

## 7. Open items (not decided in CP2; owner decision or confirmation needed)

| # | Item | Effect | Proposed handling |
|---|---|---|---|
| U-1 | `CONTAINS` and `DEPLOYED_AS` don't accept `contract` evidence (ADR-0017 §4.1), so OpenAPI files can't evidence API → operation containment, and IaC can't evidence containment or deployments | The fixture uses documentation evidence for those facts | Owner decision: keep, or a MINOR taxonomy change adding `contract` to those two types |
| U-2 | ADR-0019 §3 says `native_type` is required on every physical entity; ADR-0017 §2.2 exempts `azure.tenant` | CP2 follows the explicit exemption | One-line correction to ADR-0019 §3: "every physical entity except `azure.tenant`" |
| U-3 | ADR-0018 doesn't define the trust-function precedence for mixed evidence (for example provider configuration plus a human assertion) | CP2 checks only compatibility (D-12); the fixture avoids mixed cases | Owner decision before CP3 implements the trust function |
| U-4 | Relationship `environment_id` for a cross-environment relationship | CP2 uses `null` (interpretation I-1) | Owner confirmation |
| U-5 | Persisting rejected import items (report only, or a `reconciliation_case`) | CP2/CP4 report them; nothing is stored | Decide with the reconciliation work (Phase 2) |
| U-6 | Provider `scope_kind` vocabularies for non-Azure providers are "intended shape" | Used by the fixture; marked `intended_shape` | Confirm per provider at onboarding |
| U-7 | Fixture size 617 relationships against the ~700 target | No padding | Accept, or extend with further evidenced facts later |

## 8. Acceptance

See `acceptance.md`. ATLAS-002 is Accepted only at Gate G5.
