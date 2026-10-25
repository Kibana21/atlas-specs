# ATLAS-002 — Canonical Graph Foundation: Scope

**Version:** 0.1 · **Date:** 24 October 2026 · **Status:** **Approved in principle** by the owner (24 Oct 2026). CP0 authorized and complete. CP1 authorized for **decision drafting only**; the owner reviewed revision 1 on 25 Oct 2026 and revision 2 awaits confirmation. CP2–CP5 **not authorized**: the foundational decisions need owner approval first. ATLAS-002 is not Accepted until its final gate.

## Goal

A canonical, evidence-backed graph store that every later feature reads from. It is organization-scoped, revision-aware and validated against a versioned taxonomy, and it is loaded from a synthetic golden fixture. Nothing in ATLAS-002 serves graph data to users.

## In scope

- **Decision closure (CP1):** tenancy (DEC-058), identifiers (DEC-037), identity matching (DEC-025), taxonomy (DEC-050, DEC-070), trust and evidence (DEC-056), revisions (DEC-031) and the PostgreSQL design (DEC-021). Backlog BL-002, BL-003, BL-007 and parts of BL-006.
- **Contracts and fixture (CP2):** taxonomy artifact, JSON Schemas for entity, relationship and provenance with valid/invalid examples, a synthetic golden fixture subset (BL-015, BL-016), and a validator.
- **Backend (CP3–CP4):** canonical tables and migration `0002`, taxonomy validation, deterministic fixture loader, integrity checks, pilot-size benchmark (BL-101, BL-102).

## Out of scope (owner, 24 Oct 2026)

- Graph-reading APIs: none before an authorization model exists (invariant 4; BL-104 belongs to a later item).
- Frontend graph UI, canvas, projections or search; ATLAS-003 or anything beyond this scope.
- Connectors, discovery syncs, fuzzy matching, the reconciliation workflow, jobs and outbox.
- Changes to shared PostgreSQL or Redis configuration; PostgreSQL extensions; any graph database.
- Product exclusions: PR impact analysis, live monitoring, distributed tracing, inferred runtime traffic.

## Checkpoints and gates

| CP | Repository | Content | Gate | State |
|---|---|---|---|---|
| CP0 | backend + frontend | Fix A001-DEF-01 (E-48) with a regression test; move frontend `e2e/backend.ref` | G0: defect closed, CI green, E2E green | **Done** (`evidence.md` §1) |
| CP1 | specs | Decision proposals as ADRs (Proposed), register rows set to Proposed, decision matrix | G1: owner approves the decisions; register rows become Confirmed | **Revision 2 (25 Oct 2026), awaiting owner confirmation** (`decision-matrix.md`) |
| CP2 | specs | Taxonomy artifact, schemas, examples, golden fixture, validator; spec/plan/tasks/acceptance for CP3–CP5 | G2: CI validates schemas and fixture; owner approves the plan | Not authorized |
| CP3 | backend | Migration `0002` per ADR-0001; taxonomy validation; privilege tests | G3: migrations round-trip; privileges; matrix rejects invalid input | Not authorized |
| CP4 | backend | Deterministic fixture loader; integrity suite; pilot-size benchmark | G4: idempotent load with an equal graph hash; integrity green; benchmark recorded | Not authorized |
| CP5 | all | Evidence, release tags, owner sign-off | G5: acceptance | Not authorized |

## Restrictions carried forward

- ATLAS-001 release tags (`contract-v0.1.0`, backend and frontend `v0.1.0`) and contract pins are preserved.
- Synthetic fixtures only.
- Repositories stay public.
- BRD, UX and Technical baselines are not edited. Deviations go to `decisions/baseline-deviations.md` once approved.
- Protected-branch PR workflow; every required check must pass; fresh-clone verification before every push.
- No product code before the relevant P0 decisions are Confirmed.
