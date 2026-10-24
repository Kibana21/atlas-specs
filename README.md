# Atlas Specifications

This repository is the source of truth for Atlas requirements, UX, technical architecture and shared contracts.

## Current baselines
- `brd/Atlas_Enterprise_Architecture_BRD_v2_2.md`
- `ux/Atlas_Bright_UX_Interaction_Requirements_v1_1.md`
- `technical/Atlas_Technical_Architecture_System_Design_v1_1.md`

## Intended companion repositories
- `atlas-backend` — Python/FastAPI services, connectors, persistence and workers
- `atlas-frontend` — Next.js/React application and diagramming UX

Keep versioned API contracts under `contracts/openapi/` and schemas under `contracts/schemas/`. Backend and frontend CI should pin a reviewed `atlas-specs` commit.
