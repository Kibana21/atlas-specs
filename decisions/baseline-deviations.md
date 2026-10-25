# Atlas — Baseline Deviation Record

**Version:** 0.2 · **Date:** 25 October 2026 · **Owner:** project owner (until DEC-081 names others)

## Purpose

The approved baselines (`brd/…BRD_v2_2.md`, `ux/…UX_Interaction_Requirements_v1_1.md`, `technical/…System_Design_v1_1.md`) are **not edited ad hoc** (DEC-040 modification, ATLAS-001 requirement 6). When an approved decision or work item knowingly differs from a baseline, the difference is recorded here. It is later reconciled through a **controlled revision** of that baseline: a version bump, revision record and owner approval.

| Field | Meaning |
|---|---|
| Type | **Permanent**: the baseline should change. **Temporary**: a work item defers a baseline requirement; the baseline stays as is |
| Reconcile via | The controlled revision that will absorb a permanent deviation, or the work item that ends a temporary one |

## Deviations

| ID | Baseline and section | Baseline says (summary) | Approved position | Type | Decision / source | Reconcile via | Status |
|---|---|---|---|---|---|---|---|
| TD-DEV-001 | Technical Design v1.1 §17.3 | `atlas-specs` tree: `contracts/openapi/atlas-api.yaml`, `contracts/jsonschema/`, `contracts/examples/`, `contracts/compatibility.md`, `acceptance/journeys/`, `acceptance/golden-datasets/`, `design/tokens.md` | Adopted layout: `contracts/{openapi,schemas,examples}`, `contracts/{conventions,style-guide,compatibility}.md`, `acceptance/{scenarios,test-data}`, `design/tokens.json` + `tokens.md`, plus `decisions/`, `phase0/`, `features/`, `tools/` | Permanent | DEC-040 (owner-approved with modification) | Technical Design v1.2, §17.3 | Open |
| TD-DEV-002 | Technical Design v1.1 §17.3 boundary text | `atlas-specs` stores specifications and portable test fixtures, not executable source | `tools/` holds CI validation scripts (lock, conformance, tokens, registry). This is not product code and is never deployed | Permanent (clarification) | DEC-040; ATLAS-001 spec §4 | Technical Design v1.2, §17.3 boundary | Open |
| TD-DEV-003 | Technical Design v1.1 §0 (canonical persistence) | "PostgreSQL 16+ managed in Azure" (proposal) | Local and CI use **PostgreSQL 15**; production major undecided | Permanent | DEC-043 (approved), DEC-086 (Open), DEC-021 (narrowed) | Technical Design v1.2, §0 and §16, once DEC-086 closes | Open |
| TD-DEV-004 | Technical Design v1.1 §5.3; UX v1.1 §2.1 | Candidate colour tokens (Tech omits compute violet; no text-safe variants) | Token set extended: compute violet, entity **text** variants, tints, `border-strong #7A8AA0`, status colours, **relationship-line colours and widths**, typography/spacing/**sizing**/motion tokens (ATLAS-001 amendment A2, E-03). All remain *proposed* (DEC-065) | Permanent (pending DEC-065) | ATLAS-001 spec §7; DEC-099 | Technical Design v1.2 §5.3 and UX v1.2 §2.1, after DEC-065 approval | Open |
| TD-DEV-005 | Technical Design v1.1 §8 | Taskiq + Redis dispatch with PostgreSQL durable job state and outbox | ATLAS-001 ships dispatch only; durable state and outbox deferred | Temporary | DEC-028 (approved), DEC-046 (approved) | BL-201 (hard prerequisite of the first business background job) | Open |
| TD-DEV-006 | UX v1.1 UX-NFR-011 | Browser E2E in real Chromium **and one additional** supported browser | ATLAS-001 runs Chromium only; WebKit project prepared but disabled | Temporary | ATLAS-001 owner requirement 4; DEC-055 (Open) | DEC-055 closure; first work item after ATLAS-001 that adds UI screens | Open |
| TD-DEV-007 | UX v1.1 UX-NFR-012; Technical Design v1.1 §5.6 | Golden screenshots at 1440×900 and 1280×720 for core screens | Deferred: no core screens exist in ATLAS-001 | Temporary | ATLAS-001 owner requirement 4 | First work item delivering a core screen (BL-105/BL-109) | Open |
| TD-DEV-008 | BRD v2.2 §5.1 INV-02 | Relationship types `CALLS_API, PUBLISHES, CONSUMES, READS, WRITES, DEPLOYED_ON, HOSTED_IN, OWNS, DEPENDS_ON, PROTECTS` | Canonical vocabulary per ADR-0017 §8 with documented aliases: `CALLS_API` → `CONSUMES_API`; `PUBLISHES` → `PUBLISHES_TO`; `CONSUMES` → `SUBSCRIBES_TO` or `CONSUMES_API` by target; `READS` → `READS_FROM`; `WRITES` → `WRITES_TO`; `DEPLOYED_ON` → `DEPLOYED_AS`; `HOSTED_IN` → `CONTAINS` (**inverse direction**); `OWNS`, `DEPENDS_ON` (curated only) unchanged; `PROTECTS` defined but reserved until security-control types exist | Permanent | DEC-050 (owner-approved 25 Oct 2026, ATLAS-002 D6, D8–D10) | BRD v2.3, §5.1 INV-02 | Open |
| TD-DEV-009 | Technical Design v1.1 §3.1, §3.3 | Relationship catalog `CONTAINS, SUPPORTS_CAPABILITY, EXPOSES_API, CONSUMES_API, PUBLISHES_TO, SUBSCRIBES_TO, STORES_IN, DEPLOYED_AS, CONNECTS_TO, OWNS, PRODUCES_DATA/CONSUMES_DATA, DECIDED_BY`; modeling layers without provider categories | Adds `READS_FROM`, `WRITES_TO`, `MEMBER_OF`, `DEPENDS_ON`, `PROTECTS` (reserved); narrows `CONTAINS` to hierarchical containment within one provider and `STORES_IN` to "direction not established"; `REFERENCES_SELF` dropped; adds `core.system`, `core.component`, provider-neutral categories and eight `infra.*` types (ADR-0017, ADR-0019) | Permanent | DEC-050, DEC-004 (owner-approved 25 Oct 2026, ATLAS-002 D6–D12, D19) | Technical Design v1.2, §3.1 and §3.3 | Open |

## Procedure

1. A new deviation is added here in the same change that introduces it, citing the approving decision.
2. Permanent deviations are batched into the next controlled baseline revision. That revision cites the TD-DEV IDs it closes, and each closed row is set to *Closed (vX.Y)*.
3. Temporary deviations close when the named work item delivers the baseline requirement.
4. IDs are never reused.
