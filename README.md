# Atlas Specifications

This repository is the source of truth for Atlas requirements, UX, technical architecture and shared contracts.

## Current baselines

- `brd/Atlas_Enterprise_Architecture_BRD_v2_2.md`
- `ux/Atlas_Bright_UX_Interaction_Requirements_v1_1.md`
- `technical/Atlas_Technical_Architecture_System_Design_v1_1.md`

## Phase 0 engineering blueprint (proposed, v0.1)

- `phase0/Atlas_Phase0_Engineering_Blueprint_v0_1.md` — readiness assessment, conflicts, dependencies, contract gaps, risks, implementation order
- `phase0/requirement-traceability-matrix.md` and `phase0/requirements-registry.csv` — requirement traceability (393 requirements)
- `phase0/prioritized-backlog.md` — ranked backlog, Phase 0–5
- `decisions/decision-register.md` — Confirmed / Proposed / Open decisions

## Work items

- `features/ATLAS-001-engineering-foundation/` — engineering foundation: spec, plan, tasks, acceptance, evidence, follow-ups. **Accepted** (owner, 24 Oct 2026; release `contract-v0.1.0` / `v0.1.0`)

## Intended companion repositories

- `atlas-backend` — Python/FastAPI services, connectors, persistence and workers
- `atlas-frontend` — Next.js/React application and diagramming UX

Keep versioned API contracts under `contracts/openapi/` and schemas under `contracts/schemas/`. Backend and frontend CI should pin a reviewed `atlas-specs` commit.
