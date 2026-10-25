# Atlas — Requirement Traceability Matrix (Phase 0)

**Status:** Proposed working baseline · **Date:** 24 October 2026 (readiness regenerated 24 Oct 2026 after register v0.6, and again 25 Oct 2026 after register v0.9: ATLAS-002 CP1 decisions Confirmed; no readiness change) · **Generated from:** `brd/Atlas_Enterprise_Architecture_BRD_v2_2.md`, `ux/Atlas_Bright_UX_Interaction_Requirements_v1_1.md`; mapping per `phase0/Atlas_Phase0_Engineering_Blueprint_v0_1.md` and `phase0/prioritized-backlog.md`.  
**Machine-readable source:** `phase0/requirements-registry.csv` (same rows, full text, extra columns). Edit the CSV and this file together, or regenerate both.

> Engineering phase, backlog mapping, module mapping, readiness and gaps are **blueprint proposals**, not approved scope. Requirement text is quoted from the baselines (truncated here; full text in CSV). UX-OD-01–12 are decisions and live in `decisions/decision-register.md`.

## Legend

| Column | Meaning |
|---|---|
| Pri | Strength from source (Must/Should/Could), with BRD P0/P1/P2 where given; `Gate` = UX quality gate; `-` = none in source |
| Phase | Recommended engineering phase (tech design §18): P0 decisions/spikes, P1 Explore+Studio foundation, P2 trustworthy discovery, P3 design productivity, P4 intelligence, P5 enterprise expansion |
| Backlog | `phase0/prioritized-backlog.md` items; first item is primary |
| Gaps | `AC` acceptance column is the BRD generic boilerplate and no UX counterpart gives a testable criterion · `API` endpoint not in tech §6.1 · `DATA` no table in tech §3.5 |
| Ready | `R0 Blocked` by ≥1 Open decision · `R1 Gaps` no open decision but gaps listed · `R2 Contract-ready` can go straight to contract drafting. No requirement is R3 (contract approved) because `contracts/` is empty |

## Summary

- **Requirements traced:** 393 (288 BRD, 105 UX). All map to at least one backlog item (script-checked).

- **By engineering phase:** P0 = 2, P1 = 179, P2 = 56, P3 = 88, P4 = 51, P5 = 17

- **By readiness:** R0 Blocked = 124, R1 Gaps = 180, R2 Contract-ready = 89

- **Gaps:** generic acceptance criteria = 79, missing API = 250, missing data model = 34

- **Most-blocking open decisions (requirement count):** DEC-051 (16), DEC-063 (14), DEC-057 (14), DEC-054 (11), DEC-073 (10), DEC-072 (9), DEC-075 (8), DEC-064 (6), DEC-055 (6), DEC-062 (6), DEC-059 (5), DEC-069 (5)

## Coverage by family

| Family | Area | Count | Phases | R0 | R1 | R2 | Primary backlog |
|---|---|---:|---|---:|---:|---:|---|
| INV | Canonical graph | 7 | P1 P2 | 0 | 7 | 0 | BL-101 BL-103 BL-203 |
| CAN | Canvas | 12 | P1 P3 | 5 | 7 | 0 | BL-106 BL-108 BL-109 BL-114 BL-115 BL-117 BL-120 BL-307 |
| DEV | Search & developer portal | 8 | P1 P4 | 2 | 6 | 0 | BL-110 BL-111 BL-112 BL-119 BL-507 |
| DEP | Dependency intelligence | 9 | P1 P2 P3 P4 | 0 | 9 | 0 | BL-101 BL-109 BL-110 BL-211 BL-305 BL-401 BL-406 |
| CON | Discovery connectors | 10 | P1 P2 P5 | 8 | 2 | 0 | BL-124 BL-201 BL-204 BL-205 BL-206 BL-207 BL-208 BL-210 BL-212 BL-505 |
| GOV | Governance & lifecycle | 7 | P1 P2 P3 | 7 | 0 | 0 | BL-104 BL-110 BL-116 BL-118 BL-211 BL-306 |
| AI | AI assistant | 8 | P4 | 8 | 0 | 0 | BL-404 |
| KNOW | Knowledge hub & onboarding | 5 | P1 P4 | 0 | 5 | 0 | BL-110 BL-112 BL-119 BL-507 |
| FLOW | Design-time playback | 5 | P3 | 0 | 5 | 0 | BL-307 |
| HIST | Time machine & drift | 6 | P2 P4 | 6 | 0 | 0 | BL-211 BL-403 |
| SAN | Sandbox | 5 | P3 | 0 | 5 | 0 | BL-303 BL-304 |
| SEC | Security & data-flow lens | 5 | P1 P4 | 5 | 0 | 0 | BL-104 BL-406 |
| COST | Cost showback | 5 | P5 | 5 | 0 | 0 | BL-502 |
| SELF | Governed self-service | 4 | P1 P5 | 2 | 2 | 0 | BL-104 BL-110 BL-119 BL-503 |
| SCORE | Quality scorecards | 5 | P4 | 0 | 5 | 0 | BL-405 |
| AIX | AI design intelligence | 5 | P4 | 0 | 5 | 0 | BL-404 |
| EXP | Product experience | 5 | P1 P3 P5 | 1 | 1 | 3 | BL-109 BL-111 BL-122 BL-308 BL-506 |
| XRAY | Architecture X-Ray | 7 | P1 | 2 | 0 | 5 | BL-113 BL-114 BL-115 |
| PASS | Architecture Passport | 8 | P1 | 4 | 4 | 0 | BL-110 BL-112 BL-119 |
| ICR | Contract registry | 9 | P2 | 2 | 7 | 0 | BL-209 |
| PAT | Pattern library | 8 | P3 | 1 | 7 | 0 | BL-304 BL-305 |
| RULE | Rule engine | 10 | P3 | 1 | 9 | 0 | BL-305 |
| MOD | Multi-level modeling | 6 | P1 | 1 | 5 | 0 | BL-101 BL-108 BL-114 |
| BCM | Capability mapping | 6 | P1 P4 | 2 | 0 | 4 | BL-123 BL-402 |
| REC | Reconciliation | 7 | P2 | 7 | 0 | 0 | BL-202 BL-203 BL-208 |
| AAC | Architecture-as-code | 6 | P3 | 0 | 6 | 0 | BL-301 |
| BRN | Branching & merging | 6 | P1 P3 | 1 | 5 | 0 | BL-116 BL-303 |
| ADR | Decisions & knowledge (req family) | 5 | P3 | 0 | 5 | 0 | BL-306 |
| LIN | Data lineage | 7 | P4 | 1 | 0 | 6 | BL-401 |
| SDK | Connector SDK | 6 | P2 P5 | 2 | 4 | 0 | BL-210 BL-506 |
| NTF | Notifications | 5 | P5 | 1 | 4 | 0 | BL-501 |
| COL | Collaboration | 5 | P3 P5 | 2 | 3 | 0 | BL-308 BL-504 |
| CMD | Command palette & workspace | 5 | P1 | 1 | 4 | 0 | BL-105 BL-111 BL-114 |
| STORY | Storytelling | 5 | P3 | 2 | 3 | 0 | BL-307 |
| IMP | Legacy diagram import | 6 | P3 | 0 | 0 | 6 | BL-302 |
| FBK | Feedback & correction | 5 | P1 P4 | 2 | 3 | 0 | BL-119 BL-405 |
| J | Acceptance journeys | 15 | P1 P2 P3 P4 | 1 | 0 | 14 | BL-108 BL-110 BL-116 BL-119 BL-123 BL-203 BL-204 BL-207 BL-211 BL-301 BL-302 BL-303 BL-307 BL-401 BL-406 |
| US | User stories | 10 | P1 P2 P3 P4 | 1 | 0 | 9 | BL-110 BL-111 BL-113 BL-114 BL-119 BL-122 BL-207 BL-303 BL-404 BL-406 |
| UX-CAN | Canvas | 24 | P1 P2 P3 | 5 | 19 | 0 | BL-108 BL-109 BL-111 BL-113 BL-114 BL-115 BL-116 BL-117 BL-120 BL-211 BL-307 |
| UX-XR | Architecture X-Ray | 10 | P1 P4 | 2 | 0 | 8 | BL-113 BL-114 BL-404 |
| UX-PASS | Architecture Passport | 12 | P1 | 3 | 9 | 0 | BL-110 BL-114 BL-119 |
| UX-ICR | Contract registry | 7 | P2 | 2 | 5 | 0 | BL-209 |
| UX-PAT | Pattern library | 6 | P3 | 1 | 5 | 0 | BL-304 BL-305 |
| UX-RULE | Rule engine | 6 | P3 | 1 | 5 | 0 | BL-305 |
| UX-GLB | Product experience | 12 | P1 | 2 | 0 | 10 | BL-104 BL-105 BL-109 BL-111 BL-112 BL-114 BL-115 BL-116 BL-119 BL-121 |
| UX-NFR | Non-functional (BRD §8, proposed IDs) | 14 | P0 P1 P2 | 9 | 0 | 5 | BL-025 BL-101 BL-104 BL-108 BL-109 BL-110 BL-111 BL-114 BL-115 BL-120 BL-122 BL-208 |
| UX-MOD | Multi-level modeling | 1 | P1 | 0 | 1 | 0 | BL-108 |
| UX-BCM | Capability mapping | 1 | P1 | 1 | 0 | 0 | BL-123 |
| UX-REC | Reconciliation | 1 | P2 | 1 | 0 | 0 | BL-203 |
| UX-AAC | Architecture-as-code | 1 | P3 | 0 | 1 | 0 | BL-301 |
| UX-BRN | Branching & merging | 1 | P3 | 0 | 1 | 0 | BL-303 |
| UX-ADR | Decisions & knowledge (req family) | 1 | P3 | 0 | 1 | 0 | BL-306 |
| UX-LIN | Data lineage | 1 | P4 | 0 | 0 | 1 | BL-401 |
| UX-SDK | Connector SDK | 1 | P2 | 0 | 1 | 0 | BL-210 |
| UX-NTF | Notifications | 1 | P5 | 0 | 1 | 0 | BL-501 |
| UX-COL | Collaboration | 1 | P3 | 1 | 0 | 0 | BL-308 |
| UX-CMD | Command palette & workspace | 1 | P1 | 0 | 1 | 0 | BL-111 |
| UX-STORY | Storytelling | 1 | P3 | 0 | 1 | 0 | BL-307 |
| UX-IMP | Legacy diagram import | 1 | P3 | 0 | 0 | 1 | BL-302 |
| UX-FBK | Feedback & correction | 1 | P1 | 0 | 1 | 0 | BL-119 |
| E | BRD experience sections | 17 | P0 P1 P2 P3 P4 | 4 | 0 | 13 | BL-004 BL-101 BL-109 BL-110 BL-111 BL-113 BL-116 BL-122 BL-125 BL-204 BL-209 BL-211 BL-304 BL-305 BL-404 BL-406 |
| NFR | Non-functional (BRD §8, proposed IDs) | 13 | P1 P2 | 9 | 0 | 4 | BL-104 BL-108 BL-109 BL-111 BL-115 BL-122 BL-125 BL-126 BL-208 |

## Matrix

### INV — Canonical graph

Backend: `catalog, domain, persistence` · Frontend: `-` · API: GET /entities/{id}; GET /entities/{id}/relationships; entity write API MISSING · Data: entity, entity_alias, relationship, fact_provenance, entity_type

| ID | Src § | Pri | Requirement | Phase | Backlog | Open decisions | Gaps | Ready | Notes |
|---|---|---|---|---|---|---|---|---|---|
| INV-01 | BRD 5.1 Enterprise inventory an… | Must | Maintain canonical IDs for business capabilities, domains, systems, applications, services, deployments, cloud resource… | P1 | BL-101 |  | AC API | R1 |  |
| INV-02 | BRD 5.1 Enterprise inventory an… | Must | Support directed typed relationships: CALLS_API, PUBLISHES, CONSUMES, READS, WRITES, DEPLOYED_ON, HOSTED_IN, OWNS, DEPE… | P1 | BL-101 BL-002 |  | AC API | R1 |  |
| INV-03 | BRD 5.1 Enterprise inventory an… | Must | Record source system, evidence pointer, discovery method, confidence, first/last seen, validity period and verification… | P1 | BL-101 BL-202 |  | AC API | R1 |  |
| INV-04 | BRD 5.1 Enterprise inventory an… | Must | Support deduplication, alias matching, merge review and conflict resolution across multiple discovery sources. | P2 | BL-203 |  | AC API | R1 |  |
| INV-05 | BRD 5.1 Enterprise inventory an… | Must | Represent environment and regional separation, shared infrastructure and many-to-many ownership. | P1 | BL-101 |  | AC API | R1 |  |
| INV-06 | BRD 5.1 Enterprise inventory an… | Must | Retain history and soft deletion/tombstones for removed resources; distinguish missing data from verified removal. | P1 | BL-101 BL-202 |  | AC API | R1 |  |
| INV-07 | BRD 5.1 Enterprise inventory an… | Must | Provide graph and catalog APIs with pagination, filters and access-aware responses. | P1 | BL-103 BL-108 |  | AC API | R1 |  |

### CAN — Canvas

Backend: `layouts, projections` · Frontend: `components/canvas, features/explore, features/studio` · API: GET /views/{id}/projection; POST /views/{id}/expand; PUT /views/{id}/layout; GET layout MISSING · Data: view_definition, view_layout

| ID | Src § | Pri | Requirement | Phase | Backlog | Open decisions | Gaps | Ready | Notes |
|---|---|---|---|---|---|---|---|---|---|
| CAN-01 | BRD 5.2 Premium diagramming can… | Must | Render official licensed Microsoft Azure Architecture Icons using a centrally maintained asset library; preserve labels… | P1 | BL-106 BL-020 | DEC-061 | API | R0 | AC via UX-CAN-012 |
| CAN-02 | BRD 5.2 Premium diagramming can… | Must | Support nested containers: tenant, subscription, resource group, VNet, subnet, AKS cluster, namespace, workload and app… | P1 | BL-109 BL-113 |  | API | R1 | AC via UX-CAN-007 |
| CAN-03 | BRD 5.2 Premium diagramming can… | Must | Provide orthogonal routing with port anchors, arrowheads, waypoints, edge labels, obstacle avoidance and visual distinc… | P1 | BL-117 |  | API | R1 | AC via UX-CAN-015 |
| CAN-04 | BRD 5.2 Premium diagramming can… | Must | Support expand/collapse and semantic zoom with configurable visibility rules by scale and user intent. | P1 | BL-109 BL-113 | DEC-060 | API | R0 | AC via UX-CAN-020 |
| CAN-05 | BRD 5.2 Premium diagramming can… | Must | Allow free positioning, resize, multi-select, alignment, distribution, grid snapping, copy/paste, undo/redo and connect… | P1 | BL-117 BL-116 |  | API | R1 | AC via UX-CAN-014 UX-CAN-016 |
| CAN-06 | BRD 5.2 Premium diagramming can… | Must | Persist manual layouts separately from topology and support named, shared, versioned curated diagrams. | P1 | BL-114 | DEC-059 DEC-067 | API | R0 | AC via UX-CAN-010 |
| CAN-07 | BRD 5.2 Premium diagramming can… | Must | Provide pan/zoom, fit-to-view, mini-map, breadcrumb navigation, focus mode and performant selection/hover states. | P1 | BL-109 |  | API | R1 | AC via UX-CAN-004 |
| CAN-08 | BRD 5.2 Premium diagramming can… | Must | Bundle related edges with counts and expansion; offer path highlighting and crossing reduction. | P1 | BL-108 BL-109 |  | API | R1 | AC via UX-CAN-009 |
| CAN-09 | BRD 5.2 Premium diagramming can… | Must | Export high-resolution SVG, PNG and PDF with labels, boundaries, legends and optional provenance. | P1 | BL-120 | DEC-064 | API | R0 | AC via UX-CAN-018 |
| CAN-10 | BRD 5.2 Premium diagramming can… | Must | Support keyboard shortcuts, accessible selection, readable contrast, tooltips and screen-reader alternatives. | P1 | BL-115 | DEC-055 | API | R0 | AC via UX-CAN-019 |
| CAN-11 | BRD 5.2 Premium diagramming can… | Should | Offer auto-layout presets for landscape, layered flow, deployment hierarchy and integration sequence. | P1 | BL-117 |  | AC API | R1 |  |
| CAN-12 | BRD 5.2 Premium diagramming can… | Should | Enable diagram comments, annotations, review status, templates and presentation mode. | P3 | BL-307 BL-308 |  | API | R1 | AC via UX-CAN-021 UX-STORY-01; build with STORY-* + COL-01 |

### DEV — Search & developer portal

Backend: `search, passports` · Frontend: `shell (search, palette), features/explore` · API: GET /search; GET /entities/{id}/passport; favorites/recent MISSING · Data: entity, entity_alias, document

| ID | Src § | Pri | Requirement | Phase | Backlog | Open decisions | Gaps | Ready | Notes |
|---|---|---|---|---|---|---|---|---|---|
| DEV-01 | BRD 5.3 Search, navigation and… | Must | Provide global search over names, aliases, resource IDs, APIs, routes, repositories, owners, tags and business capabili… | P1 | BL-111 |  | API | R1 | AC via UX-GLB-001 |
| DEV-02 | BRD 5.3 Search, navigation and… | Must | Return relevant results with type, environment, owner, last-seen and deep link to focused diagram. | P1 | BL-111 |  | API | R1 | AC via UX-GLB-002 |
| DEV-03 | BRD 5.3 Search, navigation and… | Must | Provide a service home page showing purpose, owner/team, contacts, repositories, deployments, APIs, dependencies, runbo… | P1 | BL-110 |  | API | R1 | AC via UX-PASS-002; build with PASS-01..04 (Passport) |
| DEV-04 | BRD 5.3 Search, navigation and… | Must | Support saved views, recently viewed items, favorites and shareable deep links with access control. | P1 | BL-112 BL-114 | DEC-067 | API | R0 | AC via UX-GLB-008; build with CMD-02 + UX-GLB-008 |
| DEV-05 | BRD 5.3 Search, navigation and… | Must | Offer one-click copy for resource IDs, API endpoints, repository URLs and documentation references. | P1 | BL-110 |  | AC API | R1 |  |
| DEV-06 | BRD 5.3 Search, navigation and… | Must | Provide ownership claim, correction and verification workflows with approval and audit. | P1 | BL-119 | DEC-051 DEC-063 | API | R0 | AC via UX-PASS-006; build with PASS-06 + FBK-* |
| DEV-07 | BRD 5.3 Search, navigation and… | Should | Support keyboard-first command palette and fast navigation. | P1 | BL-111 |  | API | R1 | AC via UX-CMD-01; build with CMD-01 |
| DEV-08 | BRD 5.3 Search, navigation and… | Should | Provide onboarding journeys: start from a business process, trace to code and deployment. | P4 | BL-507 |  | AC API | R1 |  |

### DEP — Dependency intelligence

Backend: `projections, contracts` · Frontend: `features/explore (path focus, impact)` · API: neighbors/paths/impact endpoints MISSING · Data: relationship, fact_provenance, contract

| ID | Src § | Pri | Requirement | Phase | Backlog | Open decisions | Gaps | Ready | Notes |
|---|---|---|---|---|---|---|---|---|---|
| DEP-01 | BRD 5.4 Integration and depende… | Must | Model APIs and event contracts as first-class entities, not only labels on edges. | P1 | BL-101 |  | AC API | R1 |  |
| DEP-02 | BRD 5.4 Integration and depende… | Must | Inspect endpoint/method, contract/version, configured producer/consumer, authentication, data classification and eviden… | P1 | BL-110 BL-209 |  | API | R1 | AC via UX-CAN-008 |
| DEP-03 | BRD 5.4 Integration and depende… | Must | Trace upstream/downstream dependencies with direction, hop limits, environment filters and cycle-safe traversal. | P2 | BL-211 |  | API | R1 | AC via UX-CAN-022 |
| DEP-04 | BRD 5.4 Integration and depende… | Must | Distinguish configuration-derived, contract-derived, manually verified and inferred links in UI and export; do not impl… | P1 | BL-109 BL-003 |  | API | R1 | AC via UX-GLB-010 |
| DEP-05 | BRD 5.4 Integration and depende… | Must | Offer business process and data lineage overlays where supporting sources exist. | P4 | BL-401 |  | AC API | R1 |  |
| DEP-06 | BRD 5.4 Integration and depende… | Must | Provide explainable impact reports listing candidate affected systems, paths, owners, criticality, confidence and unkno… | P2 | BL-211 |  | AC API | R1 |  |
| DEP-07 | BRD 5.4 Integration and depende… | Must | Avoid presenting potential blast radius as guaranteed failure impact; expose assumptions and missing evidence. | P2 | BL-211 |  | AC API | R1 |  |
| DEP-08 | BRD 5.4 Integration and depende… | Should | Provide design-time dependency and business-criticality overlays without live health or telemetry integration. | P4 | BL-406 |  | AC API | R1 |  |
| DEP-09 | BRD 5.4 Integration and depende… | Should | Detect stale contracts, unowned interfaces, unsupported API versions and dangling dependencies. | P3 | BL-305 |  | AC API | R1 |  |

### CON — Discovery connectors

Backend: `connectors, sources, workers, jobs` · Frontend: `admin (sources)` · API: connector admin/sync endpoints MISSING; GET /jobs/{id} · Data: source_system, source_observation, job, job_attempt

| ID | Src § | Pri | Requirement | Phase | Backlog | Open decisions | Gaps | Ready | Notes |
|---|---|---|---|---|---|---|---|---|---|
| CON-01 | BRD 5.5 Discovery, connectors a… | Must | Read Azure Resource Graph and approved Azure APIs for resource inventory and hierarchy. | P2 | BL-204 | DEC-069 DEC-072 | AC API | R0 |  |
| CON-02 | BRD 5.5 Discovery, connectors a… | Must | Ingest APIM APIs, operations and policy metadata where permitted. | P2 | BL-205 | DEC-069 DEC-072 | AC API | R0 |  |
| CON-03 | BRD 5.5 Discovery, connectors a… | Must | Discover AKS namespaces, services, ingress, workloads and deployment metadata with least-privilege access. | P2 | BL-206 | DEC-069 DEC-072 | AC API | R0 |  |
| CON-04 | BRD 5.5 Discovery, connectors a… | Must | Ingest repositories, IaC manifests, OpenAPI/AsyncAPI, deployment metadata and documentation from approved source contro… | P2 | BL-212 | DEC-069 DEC-072 DEC-078 | AC API | R0 |  |
| CON-05 | BRD 5.5 Discovery, connectors a… | Must | Ingest messaging topology and configuration metadata (queues, topics, subscriptions, routing rules) without message pay… | P2 | BL-207 | DEC-069 DEC-072 | AC API | R0 |  |
| CON-06 | BRD 5.5 Discovery, connectors a… | Must | Support scheduled incremental sync, manual refresh, connector health, rate limiting, retries and idempotency. | P2 | BL-201 BL-210 | DEC-072 | AC API | R0 |  |
| CON-07 | BRD 5.5 Discovery, connectors a… | Must | Expose connector coverage, sync lag, permissions, errors and provenance at record level. | P2 | BL-208 | DEC-072 | AC API | R0 |  |
| CON-08 | BRD 5.5 Discovery, connectors a… | Must | Provide an import path for curated Visio/draw.io/CSV architecture inventory with validation. | P1 | BL-124 BL-302 |  | AC API | R1 | build with IMP-* (draw.io/Visio) + CSV import |
| CON-09 | BRD 5.5 Discovery, connectors a… | Should | Add CMDB, ITSM, identity directory, cloud billing exports and data catalog integrations; exclude production-application… | P5 | BL-505 BL-502 | DEC-079 | AC API | R0 |  |
| CON-10 | BRD 5.5 Discovery, connectors a… | Should | Allow extensible connector SDK and event-driven synchronization. | P2 | BL-210 |  | AC API | R1 | build with SDK-* |

### GOV — Governance & lifecycle

Backend: `identity, designs, audit` · Frontend: `features/studio (review), admin` · API: POST /branches/{id}/submit\|approve; audit history GET MISSING · Data: architecture_branch, review, audit_event, graph_snapshot

| ID | Src § | Pri | Requirement | Phase | Backlog | Open decisions | Gaps | Ready | Notes |
|---|---|---|---|---|---|---|---|---|---|
| GOV-01 | BRD 5.6 Architecture collaborat… | Must | Define roles: viewer, developer, editor, domain owner, architect reviewer, administrator and connector operator. | P1 | BL-104 BL-004 | DEC-051 | AC API | R0 |  |
| GOV-02 | BRD 5.6 Architecture collaborat… | Must | Provide draft/published diagram lifecycle, review/approval, version history and comparison. | P1 | BL-116 BL-303 | DEC-051 DEC-063 | API | R0 | AC via UX-BRN-01 |
| GOV-03 | BRD 5.6 Architecture collaborat… | Must | Show ownership, verification status, exceptions, policy violations and freshness indicators. | P1 | BL-110 BL-208 | DEC-051 | AC API | R0 |  |
| GOV-04 | BRD 5.6 Architecture collaborat… | Must | Maintain immutable audit events for access-sensitive edits, publication, approvals, imports and permission changes. | P1 | BL-118 | DEC-051 | AC API | R0 |  |
| GOV-05 | BRD 5.6 Architecture collaborat… | Must | Support architecture snapshots and diff of resources, relationships, ownership and deployment changes. | P2 | BL-211 | DEC-051 | AC API | R0 | build with HIST-01/02 |
| GOV-06 | BRD 5.6 Architecture collaborat… | Should | Attach diagrams and impact dossiers to ADRs, change tickets and release reviews. | P3 | BL-306 | DEC-051 | AC API | R0 |  |
| GOV-07 | BRD 5.6 Architecture collaborat… | Should | Support design proposals versus discovered current state, with clear visual differentiation. | P1 | BL-116 | DEC-051 | API | R0 | AC via UX-GLB-005 |

### AI — AI assistant

Backend: `ai, search, knowledge` · Frontend: `Ask Atlas panel` · API: POST /ai/query (response schema MISSING) · Data: document, audit_event

| ID | Src § | Pri | Requirement | Phase | Backlog | Open decisions | Gaps | Ready | Notes |
|---|---|---|---|---|---|---|---|---|---|
| AI-01 | BRD 5.7 AI architecture assista… | Must | Answer natural-language questions using authorized graph, catalog and documentation evidence. | P4 | BL-404 | DEC-075 | AC API | R0 |  |
| AI-02 | BRD 5.7 AI architecture assista… | Must | Return cited paths, source timestamps and confidence; never fabricate nodes, edges, owners or production states. | P4 | BL-404 | DEC-075 | API | R0 | AC via UX-XR-010 |
| AI-03 | BRD 5.7 AI architecture assista… | Must | Offer user-approved canvas actions: focus, expand, filter, highlight path and create draft view. | P4 | BL-404 | DEC-075 | AC API | R0 |  |
| AI-04 | BRD 5.7 AI architecture assista… | Must | Respect RBAC in retrieval, reasoning, response text and generated diagrams. | P4 | BL-404 | DEC-075 | AC API | R0 |  |
| AI-05 | BRD 5.7 AI architecture assista… | Must | Request clarification for ambiguous application names or environments and disclose coverage gaps. | P4 | BL-404 | DEC-075 | AC API | R0 |  |
| AI-06 | BRD 5.7 AI architecture assista… | Must | Log prompts, retrieved references and actions under enterprise privacy controls. | P4 | BL-404 | DEC-075 DEC-076 | AC API | R0 |  |
| AI-07 | BRD 5.7 AI architecture assista… | Should | Generate draft diagrams and architecture summaries from grounded data. | P4 | BL-404 | DEC-075 | AC API | R0 |  |
| AI-08 | BRD 5.7 AI architecture assista… | Should | Suggest ownership gaps, likely stale diagrams and candidate architecture review questions. | P4 | BL-404 | DEC-075 | AC API | R0 |  |

### KNOW — Knowledge hub & onboarding

Backend: `passports, knowledge` · Frontend: `features/explore (Passport, journeys)` · API: journeys/collections endpoints MISSING · Data: document, decision

| ID | Src § | Pri | Requirement | Phase | Backlog | Open decisions | Gaps | Ready | Notes |
|---|---|---|---|---|---|---|---|---|---|
| KNOW-01 | BRD 5.8 Developer knowledge hub… | Must | Provide a unified developer homepage for each application/service with purpose, business capability, owner, support con… | P1 | BL-110 |  | API | R1 | AC via UX-PASS-004; build with PASS-01..04 (Passport) |
| KNOW-02 | BRD 5.8 Developer knowledge hub… | Should | Offer guided learning journeys (for example, “Understand Policy Issuance”) combining diagrams, relevant docs and key in… | P4 | BL-507 |  | AC API | R1 |  |
| KNOW-03 | BRD 5.8 Developer knowledge hub… | Should | Identify missing, stale or conflicting documentation and provide a review workflow. | P1 | BL-119 BL-306 |  | AC API | R1 | build with FBK-* |
| KNOW-04 | BRD 5.8 Developer knowledge hub… | Should | Support deep links, bookmarks, recently visited systems, saved collections and role-aware recommendations. | P1 | BL-112 BL-114 |  | AC API | R1 |  |
| KNOW-05 | BRD 5.8 Developer knowledge hub… | Should | Enable a “new joiner” orientation experience with curated reading order, glossary and system map. | P4 | BL-507 |  | AC API | R1 |  |

### FLOW — Design-time playback

Backend: `knowledge, layouts` · Frontend: `features/studio (story/playback)` · API: process journey endpoints MISSING · Data: story/scene tables MISSING from tech §3.5

| ID | Src § | Pri | Requirement | Phase | Backlog | Open decisions | Gaps | Ready | Notes |
|---|---|---|---|---|---|---|---|---|---|
| FLOW-01 | BRD 5.9 Design-time architectur… | Should | Model a business/technical journey as an ordered graph of steps, applications, APIs, queues, databases and human approv… | P3 | BL-307 |  | AC API DATA | R1 | build with STORY-01 |
| FLOW-02 | BRD 5.9 Design-time architectur… | Should | Animate the journey on the architecture canvas with play/pause, step, speed and jump-to-component controls. | P3 | BL-307 |  | AC API DATA | R1 |  |
| FLOW-03 | BRD 5.9 Design-time architectur… | Should | Label each step with protocol, input/output contract, sync/async behavior, error paths and source evidence where docume… | P3 | BL-307 |  | AC API DATA | R1 |  |
| FLOW-04 | BRD 5.9 Design-time architectur… | Could | Support alternate paths and failure branches, explicitly marked as design scenarios rather than observed executions. | P3 | BL-307 |  | AC API DATA | R1 |  |
| FLOW-05 | BRD 5.9 Design-time architectur… | Should | Export a static sequence diagram or shareable process walkthrough. | P3 | BL-307 |  | AC API DATA | R1 |  |

### HIST — Time machine & drift

Backend: `designs, catalog` · Frontend: `/history/:viewId` · API: compare_snapshots endpoint MISSING · Data: graph_snapshot

| ID | Src § | Pri | Requirement | Phase | Backlog | Open decisions | Gaps | Ready | Notes |
|---|---|---|---|---|---|---|---|---|---|
| HIST-01 | BRD 5.10 Architecture time mach… | Must | Retain immutable, timestamped architecture snapshots with source and publication status. | P2 | BL-211 BL-006 | DEC-057 | AC API | R0 |  |
| HIST-02 | BRD 5.10 Architecture time mach… | Must | Compare any two snapshots for added/removed resources, connections, owners, contracts and deployment configuration. | P2 | BL-211 | DEC-057 | API | R0 | AC via UX-BRN-01 |
| HIST-03 | BRD 5.10 Architecture time mach… | Should | Visually highlight changes on the same canvas and generate an explainable diff report. | P4 | BL-403 | DEC-057 | AC API | R0 |  |
| HIST-04 | BRD 5.10 Architecture time mach… | Should | Compare an approved target-state design with imported/discovered configuration to identify drift and unapproved additio… | P4 | BL-403 | DEC-057 DEC-059 | AC API | R0 |  |
| HIST-05 | BRD 5.10 Architecture time mach… | Must | Distinguish confirmed drift from incomplete discovery, permission gaps and connector lag. | P4 | BL-403 | DEC-057 | AC API | R0 |  |
| HIST-06 | BRD 5.10 Architecture time mach… | Should | Support time-based browsing without overwriting curated historical diagrams. | P4 | BL-403 | DEC-057 | AC API | R0 |  |

### SAN — Sandbox

Backend: `designs, patterns` · Frontend: `/sandbox/:id` · API: POST /branches; PATCH /branches/{id}; compare MISSING · Data: architecture_branch, branch_change

| ID | Src § | Pri | Requirement | Phase | Backlog | Open decisions | Gaps | Ready | Notes |
|---|---|---|---|---|---|---|---|---|---|
| SAN-01 | BRD 5.11 Architecture sandbox a… | Should | Fork an existing architecture into an isolated proposal workspace without changing the published baseline. | P3 | BL-304 BL-116 |  | API | R1 | AC via UX-PAT-004; build with BRN-01 |
| SAN-02 | BRD 5.11 Architecture sandbox a… | Should | Add/remove components and dependencies; compare as-is versus to-be architecture side by side. | P3 | BL-304 BL-303 |  | AC API | R1 | build with BRN-02 |
| SAN-03 | BRD 5.11 Architecture sandbox a… | Should | Recalculate candidate downstream dependencies and governance checks for proposed changes, showing assumptions. | P3 | BL-304 |  | AC API | R1 |  |
| SAN-04 | BRD 5.11 Architecture sandbox a… | Should | Attach rationale, ADRs, estimated cost assumptions and review comments to proposals. | P3 | BL-304 BL-306 |  | AC API | R1 |  |
| SAN-05 | BRD 5.11 Architecture sandbox a… | Must | Publish approved changes through an explicit review workflow; no direct Azure provisioning required. | P3 | BL-303 |  | AC API | R1 | build with BRN-04 |

### SEC — Security & data-flow lens

Backend: `projections, rules, identity` · Frontend: `lens: security` · API: lens parameter on projection; no dedicated contract · Data: relationship, dataset

| ID | Src § | Pri | Requirement | Phase | Backlog | Open decisions | Gaps | Ready | Notes |
|---|---|---|---|---|---|---|---|---|---|
| SEC-01 | BRD 5.12 Security and data-flow… | Should | Visualize trust zones, VNets/subnets, ingress/egress, public endpoints, identity boundaries and sensitive data classifi… | P4 | BL-406 | DEC-073 | AC | R0 |  |
| SEC-02 | BRD 5.12 Security and data-flow… | Should | Map documented data flows across applications, stores, APIs and messaging endpoints. | P4 | BL-406 | DEC-073 | AC | R0 |  |
| SEC-03 | BRD 5.12 Security and data-flow… | Should | Flag configuration-derived risks such as undocumented exposure, missing ownership or violations of approved architectur… | P4 | BL-406 BL-305 | DEC-073 | AC | R0 |  |
| SEC-04 | BRD 5.12 Security and data-flow… | Could | Generate a draft threat-model inventory (assets, trust boundaries, entry points, data flows) for human review. | P4 | BL-406 | DEC-073 | AC | R0 |  |
| SEC-05 | BRD 5.12 Security and data-flow… | Must | Apply RBAC to security-sensitive metadata and exported diagrams. | P1 | BL-104 BL-120 | DEC-064 DEC-073 |  | R0 | AC via UX-PASS-010 |

### COST — Cost showback

Backend: `NOT IN TECH DESIGN` · Frontend: `lens: cost` · API: MISSING (no module) · Data: MISSING

| ID | Src § | Pri | Requirement | Phase | Backlog | Open decisions | Gaps | Ready | Notes |
|---|---|---|---|---|---|---|---|---|---|
| COST-01 | BRD 5.13 Cloud cost, ownership… | Should | Import approved cloud billing/cost export data and map costs to resource, application, platform and business domain. | P5 | BL-502 | DEC-080 | AC API DATA | R0 |  |
| COST-02 | BRD 5.13 Cloud cost, ownership… | Should | Support cost showback with transparent allocation rules for shared services. | P5 | BL-502 | DEC-080 | AC API DATA | R0 |  |
| COST-03 | BRD 5.13 Cloud cost, ownership… | Could | Show month-over-month cost trends and budget variance without requiring operational telemetry. | P5 | BL-502 | DEC-080 | AC API DATA | R0 |  |
| COST-04 | BRD 5.13 Cloud cost, ownership… | Should | Identify orphaned/unowned resources and candidates for cost review; avoid declaring resources unused without adequate e… | P5 | BL-502 | DEC-080 | AC API DATA | R0 |  |
| COST-05 | BRD 5.13 Cloud cost, ownership… | Could | Provide scenario-based estimates for proposed architectures with explicit assumptions and uncertainty. | P5 | BL-502 | DEC-080 | AC API DATA | R0 |  |

### SELF — Governed self-service

Backend: `passports, feedback` · Frontend: `Passport links` · API: POST /feedback; request endpoints MISSING · Data: feedback_request

| ID | Src § | Pri | Requirement | Phase | Backlog | Open decisions | Gaps | Ready | Notes |
|---|---|---|---|---|---|---|---|---|---|
| SELF-01 | BRD 5.14 Governed developer sel… | Must | Offer one-click links to approved repositories, API specifications, CI/CD systems, runbooks and architecture records. | P1 | BL-110 |  | API | R1 | AC via UX-PASS-004 |
| SELF-02 | BRD 5.14 Governed developer sel… | Should | Support governed requests for API access, ownership updates, documentation corrections and architecture reviews. | P1 | BL-119 BL-503 | DEC-051 DEC-063 | AC API | R0 |  |
| SELF-03 | BRD 5.14 Governed developer sel… | Could | Allow approved service templates or scaffolding requests only through explicit authorization and audit. | P5 | BL-503 |  | AC API | R1 |  |
| SELF-04 | BRD 5.14 Governed developer sel… | Must | Make all actions permission-aware, auditable and reversible where applicable; no unapproved production mutations. | P1 | BL-104 BL-118 | DEC-051 | AC API | R0 |  |

### SCORE — Quality scorecards

Backend: `rules` · Frontend: `features/intelligence` · API: scorecard endpoints MISSING · Data: rule_evaluation, rule_finding

| ID | Src § | Pri | Requirement | Phase | Backlog | Open decisions | Gaps | Ready | Notes |
|---|---|---|---|---|---|---|---|---|---|
| SCORE-01 | BRD 5.15 Architecture quality s… | Should | Define transparent, versioned standards for ownership, documentation, API lifecycle, architecture freshness, security b… | P4 | BL-405 |  | AC API | R1 |  |
| SCORE-02 | BRD 5.15 Architecture quality s… | Should | Score applications/domains using documented rules and linked evidence. | P4 | BL-405 |  | AC API | R1 |  |
| SCORE-03 | BRD 5.15 Architecture quality s… | Must | Show “unknown/not assessed” separately from “failed” to avoid penalizing missing source coverage as a verified defect. | P4 | BL-405 BL-003 |  | AC API | R1 | build with RULE-04 |
| SCORE-04 | BRD 5.15 Architecture quality s… | Should | Assign remediation owners, exceptions, due dates and review status. | P4 | BL-405 |  | AC API | R1 |  |
| SCORE-05 | BRD 5.15 Architecture quality s… | Could | Provide domain/team trends and exportable scorecards, with configurable visibility. | P4 | BL-405 |  | AC API | R1 |  |

### AIX — AI design intelligence

Backend: `ai, designs` · Frontend: `Ask Atlas panel` · API: POST /ai/query · Data: architecture_branch

| ID | Src § | Pri | Requirement | Phase | Backlog | Open decisions | Gaps | Ready | Notes |
|---|---|---|---|---|---|---|---|---|---|
| AIX-01 | BRD 5.16 Architecture assistant | Should | Convert a natural-language architecture question into a focused, evidence-backed canvas view. | P4 | BL-404 |  | AC | R1 |  |
| AIX-02 | BRD 5.16 Architecture assistant | Should | Draft ADRs, architecture summaries, design review checklists and impact dossiers from authorized graph/document evidenc… | P4 | BL-404 |  | AC | R1 |  |
| AIX-03 | BRD 5.16 Architecture assistant | Could | Propose future-state design options and trade-offs in a sandbox without automatically publishing changes. | P4 | BL-404 |  | AC | R1 |  |
| AIX-04 | BRD 5.16 Architecture assistant | Must | Provide source links, confidence and explicit unknowns for every generated architectural assertion. | P4 | BL-404 |  | AC | R1 | build with AI-02 |
| AIX-05 | BRD 5.16 Architecture assistant | Must | Never perform PR analysis, ingest telemetry or claim observed transaction behavior. | P4 | BL-404 |  | AC | R1 |  |

### EXP — Product experience

Backend: `-` · Frontend: `shell` · API: n/a · Data: -

| ID | Src § | Pri | Requirement | Phase | Backlog | Open decisions | Gaps | Ready | Notes |
|---|---|---|---|---|---|---|---|---|---|
| EXP-01 | BRD 5.17 Product experience and… | Must | Offer search-first command palette, keyboard shortcuts, recent history, pinned views and shareable deep links. | P1 | BL-111 BL-112 |  |  | R2 | AC via UX-CMD-01; build with CMD-01/CMD-02 |
| EXP-02 | BRD 5.17 Product experience and… | Must | Provide responsive, accessible, high-performance diagram interactions with browser-based end-to-end tests. | P1 | BL-122 | DEC-055 |  | R0 | AC via UX-NFR-011 |
| EXP-03 | BRD 5.17 Product experience and… | Should | Allow extensions for approved connectors, entity types, policies and developer portal widgets without compromising the… | P5 | BL-506 |  | AC | R1 |  |
| EXP-04 | BRD 5.17 Product experience and… | Should | Support collaborative annotations, comments, diagram ownership and publication review. | P3 | BL-308 |  |  | R2 | AC via UX-COL-01; build with COL-01/02 |
| EXP-05 | BRD 5.17 Product experience and… | Must | Expose a clear distinction between curated, discovered, inferred and proposed architecture states. | P1 | BL-109 BL-003 |  |  | R2 | AC via UX-GLB-010; build with DEC-056 trust model |

### XRAY — Architecture X-Ray

Backend: `projections, layouts` · Frontend: `features/explore (X-Ray)` · API: POST /views/{id}/expand · Data: view_layout, relationship

| ID | Src § | Pri | Requirement | Phase | Backlog | Open decisions | Gaps | Ready | Notes |
|---|---|---|---|---|---|---|---|---|---|
| XRAY-01 | BRD 5.18 Architecture X-Ray | Must | Expand an application in place to show logical services, APIs, data stores, messaging endpoints and infrastructure chil… | P1 | BL-113 |  |  | R2 |  |
| XRAY-02 | BRD 5.18 Architecture X-Ray | Must | Provide selectable abstraction levels: business application, logical services, integration and Azure deployment. | P1 | BL-113 BL-108 | DEC-060 |  | R0 |  |
| XRAY-03 | BRD 5.18 Architecture X-Ray | Must | Support Azure hierarchy traversal through subscription, resource group, VNet/subnet, AKS cluster, namespace and service… | P1 | BL-113 |  |  | R2 |  |
| XRAY-04 | BRD 5.18 Architecture X-Ray | Should | Reveal and collapse cross-boundary dependencies with grouped connector counts and on-demand expansion. | P1 | BL-113 BL-108 |  |  | R2 |  |
| XRAY-05 | BRD 5.18 Architecture X-Ray | Should | Preserve per-user and curated X-Ray layout state independently of topology data. | P1 | BL-114 | DEC-059 |  | R0 |  |
| XRAY-06 | BRD 5.18 Architecture X-Ray | Must | Provide keyboard navigation, accessible node list, and controlled rendering budgets for large nested systems. | P1 | BL-115 BL-113 |  |  | R2 |  |
| XRAY-07 | BRD 5.18 Architecture X-Ray | Must | Label discovered, curated, inferred and proposed elements distinctly at every level. | P1 | BL-113 BL-003 |  |  | R2 |  |

### PASS — Architecture Passport

Backend: `passports` · Frontend: `/applications/:id, inspector` · API: GET /entities/{id}/passport (section schema MISSING) · Data: entity, fact_provenance, document

| ID | Src § | Pri | Requirement | Phase | Backlog | Open decisions | Gaps | Ready | Notes |
|---|---|---|---|---|---|---|---|---|---|
| PASS-01 | BRD 5.19 Architecture Passport | Must | Generate a canonical Passport page for every supported entity type with stable identifier, name, type, purpose, lifecyc… | P1 | BL-110 | DEC-062 | API | R0 |  |
| PASS-02 | BRD 5.19 Architecture Passport | Must | Display business owner, technical owner, support group, contact method and stewardship status. | P1 | BL-110 | DEC-062 | API | R0 |  |
| PASS-03 | BRD 5.19 Architecture Passport | Must | Show direct dependencies and integrations with typed direction, related contract and supporting evidence. | P1 | BL-110 |  | API | R1 |  |
| PASS-04 | BRD 5.19 Architecture Passport | Must | Link to approved repositories, ADRs, API specifications, deployment diagrams, runbooks, onboarding material and service… | P1 | BL-110 |  | API | R1 |  |
| PASS-05 | BRD 5.19 Architecture Passport | Should | Display environment-specific deployment locations, Azure resource references and last successful source synchronization… | P1 | BL-110 |  | API | R1 |  |
| PASS-06 | BRD 5.19 Architecture Passport | Must | Support proposed corrections, owner attestation, audit history and approval before publishing authoritative changes. | P1 | BL-119 | DEC-063 | API | R0 |  |
| PASS-07 | BRD 5.19 Architecture Passport | Should | Provide a completeness checklist with unknown, missing, verified and stale states. | P1 | BL-110 | DEC-062 | API | R0 |  |
| PASS-08 | BRD 5.19 Architecture Passport | Should | Offer shareable links and embeddable references without bypassing authentication or leaking restricted metadata. | P1 | BL-112 |  | API | R1 |  |

### ICR — Contract registry

Backend: `contracts` · Frontend: `/contracts` · API: GET /contracts; GET /contracts/{id}/diff; import MISSING · Data: contract, contract_version

| ID | Src § | Pri | Requirement | Phase | Backlog | Open decisions | Gaps | Ready | Notes |
|---|---|---|---|---|---|---|---|---|---|
| ICR-01 | BRD 5.20 Integration Contract R… | Must | Ingest and catalog approved OpenAPI specifications, AsyncAPI specifications and explicitly documented file/data exchang… | P2 | BL-209 |  | API | R1 |  |
| ICR-02 | BRD 5.20 Integration Contract R… | Must | Model producers, consumers, operations/topics, endpoints, payload schemas, protocol, authentication and environment as… | P2 | BL-209 |  | API | R1 |  |
| ICR-03 | BRD 5.20 Integration Contract R… | Must | Support contract version history, lifecycle state, deprecation notices and effective dates. | P2 | BL-209 |  | API | R1 |  |
| ICR-04 | BRD 5.20 Integration Contract R… | Should | Provide semantic contract comparison, including additive and potentially breaking schema changes, based on published co… | P2 | BL-209 | DEC-071 | API | R0 |  |
| ICR-05 | BRD 5.20 Integration Contract R… | Must | Search by API path, operation ID, event name, topic, schema field, owning system and consumer. | P2 | BL-209 |  | API | R1 |  |
| ICR-06 | BRD 5.20 Integration Contract R… | Should | Reconcile contracts imported from APIM and approved documentation sources, flagging duplicates and mismatches. | P2 | BL-209 |  | API | R1 |  |
| ICR-07 | BRD 5.20 Integration Contract R… | Must | Record data classification and sensitive fields at the contract level, with field-level visibility controls where requi… | P2 | BL-209 | DEC-073 | API | R0 |  |
| ICR-08 | BRD 5.20 Integration Contract R… | Should | Support ownership, review status, contract stewardship and subscriptions to lifecycle notices. | P2 | BL-209 |  | API | R1 |  |
| ICR-09 | BRD 5.20 Integration Contract R… | Should | Export an authorized contract inventory and integration map for design reviews. | P2 | BL-209 |  | API | R1 |  |

### PAT — Pattern library

Backend: `patterns` · Frontend: `/patterns` · API: pattern endpoints MISSING · Data: pattern, pattern_version

| ID | Src § | Pri | Requirement | Phase | Backlog | Open decisions | Gaps | Ready | Notes |
|---|---|---|---|---|---|---|---|---|---|
| PAT-01 | BRD 5.21 Architecture Pattern L… | Must | Maintain a searchable library of versioned architecture patterns with title, intent, context, constraints, owner, statu… | P3 | BL-304 |  | API | R1 |  |
| PAT-02 | BRD 5.21 Architecture Pattern L… | Must | Include reusable graph templates with Azure service roles, boundaries, required interfaces and configurable placeholder… | P3 | BL-304 |  | API | R1 |  |
| PAT-03 | BRD 5.21 Architecture Pattern L… | Must | Attach reference diagrams, ADRs, security controls, operational considerations and known trade-offs to each pattern. | P3 | BL-304 |  | API | R1 |  |
| PAT-04 | BRD 5.21 Architecture Pattern L… | Should | Support configuration of pattern parameters, including environment, network boundary, identity approach and data classi… | P3 | BL-304 |  | API | R1 |  |
| PAT-05 | BRD 5.21 Architecture Pattern L… | Must | Support draft, reviewed, approved, deprecated and retired lifecycle states with versioned approvals. | P3 | BL-304 | DEC-063 | API | R0 |  |
| PAT-06 | BRD 5.21 Architecture Pattern L… | Should | Validate a proposed pattern instance against applicable architecture rules before review. | P3 | BL-305 |  | API | R1 |  |
| PAT-07 | BRD 5.21 Architecture Pattern L… | Could | Track adoption through documented pattern references in published architecture models. | P3 | BL-304 |  | API | R1 |  |
| PAT-08 | BRD 5.21 Architecture Pattern L… | Should | Allow curated organization-specific and reusable general patterns without hard-coding a single Azure topology. | P3 | BL-304 |  | API | R1 |  |

### RULE — Rule engine

Backend: `rules` · Frontend: `/rules, /evaluations/:id` · API: POST /rules/evaluations; catalog/exception endpoints MISSING · Data: rule_definition, rule_evaluation, rule_finding, exception

| ID | Src § | Pri | Requirement | Phase | Backlog | Open decisions | Gaps | Ready | Notes |
|---|---|---|---|---|---|---|---|---|---|
| RULE-01 | BRD 5.22 Architecture Rule Engi… | Must | Define versioned, machine-evaluable rules with ID, title, scope, severity, owner, rationale and required evidence. | P3 | BL-305 |  | API | R1 |  |
| RULE-02 | BRD 5.22 Architecture Rule Engi… | Must | Evaluate published, imported and proposed architectures against applicable rules without modifying the underlying resou… | P3 | BL-305 |  | API | R1 |  |
| RULE-03 | BRD 5.22 Architecture Rule Engi… | Must | Support initial rule categories for ownership, public exposure, approved authentication, network boundaries, data class… | P3 | BL-305 |  | API | R1 |  |
| RULE-04 | BRD 5.22 Architecture Rule Engi… | Must | Distinguish PASS, FAIL, UNKNOWN, NOT_APPLICABLE and EXEMPT with evidence and confidence. | P3 | BL-305 |  | API | R1 |  |
| RULE-05 | BRD 5.22 Architecture Rule Engi… | Must | Link each finding to affected graph entities, relevant rule text, evidence sources and recommended remediation. | P3 | BL-305 |  | API | R1 |  |
| RULE-06 | BRD 5.22 Architecture Rule Engi… | Must | Support governed exceptions with justification, approver, scope, expiry and audit trail. | P3 | BL-305 | DEC-063 | API | R0 |  |
| RULE-07 | BRD 5.22 Architecture Rule Engi… | Should | Run rule checks on demand and after approved architecture snapshot or connector-sync events, with bounded workloads. | P3 | BL-305 |  | API | R1 |  |
| RULE-08 | BRD 5.22 Architecture Rule Engi… | Should | Produce review-ready reports grouped by domain, application, severity and rule, with access-controlled export. | P3 | BL-305 |  | API | R1 |  |
| RULE-09 | BRD 5.22 Architecture Rule Engi… | Must | Offer a safe rule test harness with synthetic fixtures and expected outcomes before publication. | P3 | BL-305 |  | API | R1 |  |
| RULE-10 | BRD 5.22 Architecture Rule Engi… | Must | Keep the rule engine deterministic for authoritative pass/fail judgments; AI may draft explanations but not override ev… | P3 | BL-305 |  | API | R1 |  |

### MOD — Multi-level modeling

Backend: `catalog, projections` · Frontend: `canvas (lens/level selector)` · API: GET /views/{id}/projection; GET /taxonomy MISSING · Data: entity_type, relationship, view_definition

| ID | Src § | Pri | Requirement | Phase | Backlog | Open decisions | Gaps | Ready | Notes |
|---|---|---|---|---|---|---|---|---|---|
| MOD-01 | BRD 5.23 Canonical multi-level… | Must/P0 | Define a versioned type taxonomy for capability, domain, application, system, container, component, API, data asset, de… | P1 | BL-101 BL-002 | DEC-062 | API | R0 |  |
| MOD-02 | BRD 5.23 Canonical multi-level… | Must/P0 | Support context, system, container/component and deployment projections over the same canonical graph. | P1 | BL-108 |  | API | R1 |  |
| MOD-03 | BRD 5.23 Canonical multi-level… | Must/P0 | Validate parent-child and relationship-type rules, including multi-deployment logical services. | P1 | BL-101 |  | API | R1 |  |
| MOD-04 | BRD 5.23 Canonical multi-level… | Must/P0 | Support aliases, environment-qualified identities and lifecycle states. | P1 | BL-101 |  | API | R1 |  |
| MOD-05 | BRD 5.23 Canonical multi-level… | Must/P0 | Maintain explicit view provenance, authorship and revision independent of graph facts. | P1 | BL-114 |  | API | R1 |  |
| MOD-06 | BRD 5.23 Canonical multi-level… | Must/P0 | Support cross-view navigation and scoped access control. | P1 | BL-108 BL-104 |  | API | R1 |  |

### BCM — Capability mapping

Backend: `catalog, projections` · Frontend: `features/intelligence (capability map)` · API: GET /capabilities/{id}/map · Data: entity (capability), relationship

| ID | Src § | Pri | Requirement | Phase | Backlog | Open decisions | Gaps | Ready | Notes |
|---|---|---|---|---|---|---|---|---|---|
| BCM-01 | BRD 5.24 Business capability ma… | Must/P0 | Model capability hierarchy, business owner, criticality, lifecycle and supporting applications. | P1 | BL-123 | DEC-052 |  | R0 |  |
| BCM-02 | BRD 5.24 Business capability ma… | Must/P0 | Provide business-first heatmaps and capability-to-technology drill-down. | P1 | BL-123 | DEC-052 |  | R0 |  |
| BCM-03 | BRD 5.24 Business capability ma… | Must/P0 | Distinguish direct support, enabling dependency and inferred associations. | P4 | BL-402 |  |  | R2 |  |
| BCM-04 | BRD 5.24 Business capability ma… | Must/P0 | Allow curated capability maps with ownership and approval. | P4 | BL-402 |  |  | R2 |  |
| BCM-05 | BRD 5.24 Business capability ma… | Should/P0 | Filter by business domain, region, environment, criticality and ownership. | P4 | BL-402 |  |  | R2 |  |
| BCM-06 | BRD 5.24 Business capability ma… | Should/P0 | Support capability gap and redundancy review without automatic recommendations being treated as facts. | P4 | BL-402 |  |  | R2 |  |

### REC — Reconciliation

Backend: `reconciliation, sources` · Frontend: `features/intelligence (inbox)` · API: GET /reconciliation/cases; POST .../resolve · Data: reconciliation_case, source_identity, source_observation

| ID | Src § | Pri | Requirement | Phase | Backlog | Open decisions | Gaps | Ready | Notes |
|---|---|---|---|---|---|---|---|---|---|
| REC-01 | BRD 5.25 Intelligent source rec… | Must/P0 | Implement source-specific stable identifiers, alias matching and scoped identity rules. | P2 | BL-203 BL-007 | DEC-057 |  | R0 |  |
| REC-02 | BRD 5.25 Intelligent source rec… | Must/P0 | Provide deterministic matching precedence and configurable conflict policy. | P2 | BL-203 BL-007 | DEC-057 |  | R0 |  |
| REC-03 | BRD 5.25 Intelligent source rec… | Must/P0 | Create a reconciliation inbox for ambiguous matches, conflicting fields and orphaned relationships. | P2 | BL-203 | DEC-057 |  | R0 |  |
| REC-04 | BRD 5.25 Intelligent source rec… | Must/P0 | Retain source observations, timestamps, field-level provenance and audit history. | P2 | BL-202 | DEC-057 |  | R0 |  |
| REC-05 | BRD 5.25 Intelligent source rec… | Must/P0 | Support idempotent incremental sync, deletions/tombstones and reappearance. | P2 | BL-202 BL-203 | DEC-057 |  | R0 |  |
| REC-06 | BRD 5.25 Intelligent source rec… | Must/P0 | Expose connector coverage, unknowns and reconciliation backlog. | P2 | BL-208 | DEC-057 |  | R0 |  |
| REC-07 | BRD 5.25 Intelligent source rec… | Should/P0 | Allow reversible merge decisions and protected manual overrides. | P2 | BL-203 | DEC-057 |  | R0 |  |

### AAC — Architecture-as-code

Backend: `designs, sources` · Frontend: `features/studio (import preview)` · API: POST /imports/preview\|commit; export MISSING · Data: branch_change, source_observation

| ID | Src § | Pri | Requirement | Phase | Backlog | Open decisions | Gaps | Ready | Notes |
|---|---|---|---|---|---|---|---|---|---|
| AAC-01 | BRD 5.26 Architecture-as-Code | Must/P1 | Publish versioned schemas for entities, relationships, environment scope and metadata. | P3 | BL-301 |  | API | R1 |  |
| AAC-02 | BRD 5.26 Architecture-as-Code | Must/P1 | Support dry-run import with preview of additions, updates, removals and conflicts. | P3 | BL-301 |  | API | R1 |  |
| AAC-03 | BRD 5.26 Architecture-as-Code | Must/P1 | Provide schema validation and precise line/path errors. | P3 | BL-301 |  | API | R1 |  |
| AAC-04 | BRD 5.26 Architecture-as-Code | Must/P1 | Export authorized architecture snapshots to stable, deterministic YAML/JSON. | P3 | BL-301 |  | API | R1 |  |
| AAC-05 | BRD 5.26 Architecture-as-Code | Must/P1 | Support explicit merge rules between declarative, discovered and curated sources. | P3 | BL-301 |  | API | R1 |  |
| AAC-06 | BRD 5.26 Architecture-as-Code | Should/P1 | Document local CLI/API import workflow without requiring repository hooks or PR integration. | P3 | BL-301 |  | API | R1 |  |

### BRN — Branching & merging

Backend: `designs` · Frontend: `features/studio (diff)` · API: POST /branches...; diff/merge/discard MISSING · Data: architecture_branch, branch_change

| ID | Src § | Pri | Requirement | Phase | Backlog | Open decisions | Gaps | Ready | Notes |
|---|---|---|---|---|---|---|---|---|---|
| BRN-01 | BRD 5.27 Architecture alternati… | Must/P1 | Create a named draft branch from a pinned published architecture snapshot. | P1 | BL-116 |  | API | R1 |  |
| BRN-02 | BRD 5.27 Architecture alternati… | Must/P1 | Compare two branches or a branch against baseline at entity, relationship and layout levels. | P3 | BL-303 |  | API | R1 |  |
| BRN-03 | BRD 5.27 Architecture alternati… | Must/P1 | Detect concurrent changes and show merge conflicts with source details. | P3 | BL-303 |  | API | R1 |  |
| BRN-04 | BRD 5.27 Architecture alternati… | Must/P1 | Require authorization and rule checks before promoting an approved design. | P3 | BL-303 | DEC-063 | API | R0 |  |
| BRN-05 | BRD 5.27 Architecture alternati… | Should/P1 | Allow discard, archive and restore of draft branches. | P3 | BL-303 |  | API | R1 |  |
| BRN-06 | BRD 5.27 Architecture alternati… | Should/P1 | Provide a readable side-by-side comparison and rationale log. | P3 | BL-303 |  | API | R1 |  |

### ADR — Decisions & knowledge (req family)

Backend: `knowledge` · Frontend: `Passport Documents tab` · API: document/decision endpoints MISSING · Data: document, decision

| ID | Src § | Pri | Requirement | Phase | Backlog | Open decisions | Gaps | Ready | Notes |
|---|---|---|---|---|---|---|---|---|---|
| ADR-01 | BRD 5.28 Contextual decisions a… | Must/P1 | Attach versioned ADRs, rationale, trade-offs, review notes and approved documents to entities and relationships. | P3 | BL-306 |  | API | R1 |  |
| ADR-02 | BRD 5.28 Contextual decisions a… | Must/P1 | Support searchable decision status: proposed, accepted, superseded and retired. | P3 | BL-306 |  | API | R1 |  |
| ADR-03 | BRD 5.28 Contextual decisions a… | Must/P1 | Allow comments and suggested corrections without changing approved source records. | P3 | BL-306 |  | API | R1 |  |
| ADR-04 | BRD 5.28 Contextual decisions a… | Should/P1 | Show context-specific knowledge when inspecting a component or dependency. | P3 | BL-306 |  | API | R1 |  |
| ADR-05 | BRD 5.28 Contextual decisions a… | Must/P1 | Enforce document-level permissions in search, summaries and exports. | P3 | BL-306 |  | API | R1 |  |

### LIN — Data lineage

Backend: `lineage` · Frontend: `features/intelligence (lineage)` · API: GET /lineage/{dataset_id} · Data: dataset, relationship

| ID | Src § | Pri | Requirement | Phase | Backlog | Open decisions | Gaps | Ready | Notes |
|---|---|---|---|---|---|---|---|---|---|
| LIN-01 | BRD 5.29 Documented data lineag… | Must/P1 | Model dataset, data domain, classification, producer, transformation and consumer relationships. | P4 | BL-401 |  |  | R2 |  |
| LIN-02 | BRD 5.29 Documented data lineag… | Must/P1 | Support system-level and dataset-level lineage as initial scope. | P4 | BL-401 |  |  | R2 |  |
| LIN-03 | BRD 5.29 Documented data lineag… | Should/P1 | Represent transformations, data residency, retention classification and cross-boundary movement where known. | P4 | BL-401 |  |  | R2 |  |
| LIN-04 | BRD 5.29 Documented data lineag… | Must/P1 | Provide lineage impact exploration with bounded traversal and cycle handling. | P4 | BL-401 |  |  | R2 |  |
| LIN-05 | BRD 5.29 Documented data lineag… | Must/P1 | Link lineage edges to approved schemas, interface contracts or curated documentation. | P4 | BL-401 |  |  | R2 |  |
| LIN-06 | BRD 5.29 Documented data lineag… | Must/P1 | Protect sensitive datasets and field names in all views and exports. | P4 | BL-401 | DEC-073 |  | R0 |  |
| LIN-07 | BRD 5.29 Documented data lineag… | Could/P1 | Defer column-level lineage unless reliable metadata sources are available. | P4 | BL-401 |  |  | R2 |  |

### SDK — Connector SDK

Backend: `connectors, sources` · Frontend: `admin` · API: connector package/admin endpoints MISSING · Data: source_system

| ID | Src § | Pri | Requirement | Phase | Backlog | Open decisions | Gaps | Ready | Notes |
|---|---|---|---|---|---|---|---|---|---|
| SDK-01 | BRD 5.30 Connector SDK and exte… | Must/P1 | Publish connector contracts for entities, relationships, identity keys, provenance, sync cursors and errors. | P2 | BL-210 |  | API | R1 |  |
| SDK-02 | BRD 5.30 Connector SDK and exte… | Must/P1 | Support least-privilege connector credentials, secret rotation and scoped source permissions. | P2 | BL-210 |  | API | R1 |  |
| SDK-03 | BRD 5.30 Connector SDK and exte… | Must/P1 | Provide dry-run preview, schema mapping, incremental sync and retry semantics. | P2 | BL-210 | DEC-072 | API | R0 |  |
| SDK-04 | BRD 5.30 Connector SDK and exte… | Must/P1 | Expose source health, sync freshness, field coverage and reconciliation outcomes. | P2 | BL-210 BL-208 | DEC-072 | API | R0 |  |
| SDK-05 | BRD 5.30 Connector SDK and exte… | Should/P1 | Provide sandboxed validation and version compatibility for connector packages. | P5 | BL-506 |  | API | R1 |  |
| SDK-06 | BRD 5.30 Connector SDK and exte… | Must/P1 | Support curated legacy-system connectors without requiring cloud resource IDs. | P2 | BL-210 |  | API | R1 |  |

### NTF — Notifications

Backend: `NOT IN TECH MODULE LIST` · Frontend: `shell (notices)` · API: MISSING · Data: subscription tables MISSING

| ID | Src § | Pri | Requirement | Phase | Backlog | Open decisions | Gaps | Ready | Notes |
|---|---|---|---|---|---|---|---|---|---|
| NTF-01 | BRD 5.31 Architecture subscript… | Should/P2 | Subscribe to applications, contracts, patterns, domains and owner changes. | P5 | BL-501 |  | API DATA | R1 |  |
| NTF-02 | BRD 5.31 Architecture subscript… | Should/P2 | Generate notices for approved revision, deprecation, ownership or contract changes. | P5 | BL-501 |  | API DATA | R1 |  |
| NTF-03 | BRD 5.31 Architecture subscript… | Should/P2 | Provide digest, mute and notification preferences. | P5 | BL-501 |  | API DATA | R1 |  |
| NTF-04 | BRD 5.31 Architecture subscript… | Must/P2 | Deduplicate repeated connector observations and respect permissions. | P5 | BL-501 | DEC-051 | API DATA | R0 |  |
| NTF-05 | BRD 5.31 Architecture subscript… | Must/P2 | Exclude PR activity, runtime telemetry and production incident alerts. | P5 | BL-501 |  | API DATA | R1 |  |

### COL — Collaboration

Backend: `designs` · Frontend: `features/studio (comments)` · API: comment endpoints MISSING · Data: review (comments MISSING)

| ID | Src § | Pri | Requirement | Phase | Backlog | Open decisions | Gaps | Ready | Notes |
|---|---|---|---|---|---|---|---|---|---|
| COL-01 | BRD 5.32 Collaborative architec… | Should/P2 | Attach threaded comments and mentions to graph entities, connectors and draft revisions. | P3 | BL-308 |  | API DATA | R1 |  |
| COL-02 | BRD 5.32 Collaborative architec… | Should/P2 | Provide reviewer assignments, resolution status and audit trail. | P3 | BL-308 |  | API DATA | R1 |  |
| COL-03 | BRD 5.32 Collaborative architec… | Could/P2 | Show presence and editing ownership in shared drafts. | P5 | BL-504 | DEC-077 | API DATA | R0 |  |
| COL-04 | BRD 5.32 Collaborative architec… | Could/P2 | Support simultaneous editing only with explicit conflict-safe concurrency semantics. | P5 | BL-504 | DEC-077 | API DATA | R0 |  |
| COL-05 | BRD 5.32 Collaborative architec… | Must/P2 | Keep architecture reviews independent from source-code PR workflows. | P3 | BL-308 |  | API DATA | R1 |  |

### CMD — Command palette & workspace

Backend: `search, identity` · Frontend: `shell (Cmd+K)` · API: GET /search; preferences/favorites MISSING · Data: user preference tables MISSING

| ID | Src § | Pri | Requirement | Phase | Backlog | Open decisions | Gaps | Ready | Notes |
|---|---|---|---|---|---|---|---|---|---|
| CMD-01 | BRD 5.33 Command palette and pe… | Must/P1 | Provide Cmd/Ctrl+K command palette for search, navigation and permitted actions. | P1 | BL-111 |  | API DATA | R1 |  |
| CMD-02 | BRD 5.33 Command palette and pe… | Must/P1 | Offer recent, favorite, pinned views and user-specific saved filters. | P1 | BL-114 |  | API DATA | R1 |  |
| CMD-03 | BRD 5.33 Command palette and pe… | Must/P1 | Use context-aware actions for selected entities and current role. | P1 | BL-111 BL-104 | DEC-051 | API DATA | R0 |  |
| CMD-04 | BRD 5.33 Command palette and pe… | Should/P1 | Provide command aliases and fuzzy matching with accessible result announcements. | P1 | BL-111 |  | API DATA | R1 |  |
| CMD-05 | BRD 5.33 Command palette and pe… | Should/P1 | Show useful home dashboard with assigned stewardship tasks and recently viewed objects. | P1 | BL-105 |  | API DATA | R1 |  |

### STORY — Storytelling

Backend: `layouts` · Frontend: `features/studio (presentation)` · API: story endpoints MISSING · Data: story/scene tables MISSING

| ID | Src § | Pri | Requirement | Phase | Backlog | Open decisions | Gaps | Ready | Notes |
|---|---|---|---|---|---|---|---|---|---|
| STORY-01 | BRD 5.34 Architecture storytell… | Must/P1 | Create a story as ordered scenes referencing saved graph view state. | P3 | BL-307 |  | API DATA | R1 |  |
| STORY-02 | BRD 5.34 Architecture storytell… | Must/P1 | Step through scenes with keyboard controls and reduced-motion support. | P3 | BL-307 |  | API DATA | R1 |  |
| STORY-03 | BRD 5.34 Architecture storytell… | Must/P1 | Support shareable presentation links and access-controlled export. | P3 | BL-307 | DEC-064 | API DATA | R0 |  |
| STORY-04 | BRD 5.34 Architecture storytell… | Should/P1 | Provide annotation, callout and speaker-note support. | P3 | BL-307 |  | API DATA | R1 |  |
| STORY-05 | BRD 5.34 Architecture storytell… | Must/P1 | Preserve version and evidence context in exported story. | P3 | BL-307 | DEC-064 | API DATA | R0 |  |

### IMP — Legacy diagram import

Backend: `sources, designs` · Frontend: `features/studio (import)` · API: POST /imports/preview\|commit · Data: source_observation, branch_change

| ID | Src § | Pri | Requirement | Phase | Backlog | Open decisions | Gaps | Ready | Notes |
|---|---|---|---|---|---|---|---|---|---|
| IMP-01 | BRD 5.35 Legacy diagram import… | Must/P1 | Accept supported draw.io XML and documented Visio interchange/export formats through staged import. | P3 | BL-302 |  |  | R2 |  |
| IMP-02 | BRD 5.35 Legacy diagram import… | Must/P1 | Preview shapes, connectors, group boundaries and icon mappings before applying. | P3 | BL-302 |  |  | R2 |  |
| IMP-03 | BRD 5.35 Legacy diagram import… | Must/P1 | Separate visual-only import from canonical graph reconciliation. | P3 | BL-302 |  |  | R2 |  |
| IMP-04 | BRD 5.35 Legacy diagram import… | Must/P1 | Detect duplicates against existing graph and route ambiguous matches to steward review. | P3 | BL-302 |  |  | R2 |  |
| IMP-05 | BRD 5.35 Legacy diagram import… | Must/P1 | Preserve original file, import report and traceable source references. | P3 | BL-302 |  |  | R2 |  |
| IMP-06 | BRD 5.35 Legacy diagram import… | Should/P1 | Allow partial import, rollback and clear error recovery. | P3 | BL-302 |  |  | R2 |  |

### FBK — Feedback & correction

Backend: `knowledge, audit` · Frontend: `global feedback entry` · API: POST /feedback; list/review MISSING · Data: feedback_request, review, audit_event

| ID | Src § | Pri | Requirement | Phase | Backlog | Open decisions | Gaps | Ready | Notes |
|---|---|---|---|---|---|---|---|---|---|
| FBK-01 | BRD 5.36 Architecture feedback… | Must/P1 | Provide Report issue / Suggest correction on Passport, canvas node, edge and contract. | P1 | BL-119 |  | API | R1 |  |
| FBK-02 | BRD 5.36 Architecture feedback… | Must/P1 | Route requests to owner or steward with status, severity and comment history. | P1 | BL-119 | DEC-063 | API | R0 |  |
| FBK-03 | BRD 5.36 Architecture feedback… | Should/P1 | Support evidence attachments and proposed replacement values. | P1 | BL-119 |  | API | R1 |  |
| FBK-04 | BRD 5.36 Architecture feedback… | Must/P1 | Require approval before authoritative metadata or relationships change. | P1 | BL-119 | DEC-063 | API | R0 |  |
| FBK-05 | BRD 5.36 Architecture feedback… | Should/P1 | Provide correction backlog and quality trends by domain. | P4 | BL-405 |  | API | R1 |  |

### J — Acceptance journeys

Backend: `various` · Frontend: `various` · API: see backlog · Data: -

| ID | Src § | Pri | Requirement | Phase | Backlog | Open decisions | Gaps | Ready | Notes |
|---|---|---|---|---|---|---|---|---|---|
| J-BCM-01 | BRD 5.38 New cross-persona acce… | - | [Business leader] Search “Claims Settlement” → open capability map → inspect supporting apps and integration paths → sh… | P1 | BL-123 BL-402 |  |  | R2 |  |
| J-MOD-01 | BRD 5.38 New cross-persona acce… | - | [Enterprise architect] Open enterprise context → switch to application/container/deployment views → select same logical… | P1 | BL-108 |  |  | R2 |  |
| J-REC-01 | BRD 5.38 New cross-persona acce… | - | [Platform steward] Import overlapping APIM/Azure data → inspect candidate duplicate → review source evidence → merge →… | P2 | BL-203 |  |  | R2 |  |
| J-AAC-01 | BRD 5.38 New cross-persona acce… | - | [Developer] Upload valid YAML design → preview diff → resolve ambiguous mappings → save draft → export same design. Pub… | P3 | BL-301 |  |  | R2 |  |
| J-BRN-01 | BRD 5.38 New cross-persona acce… | - | [Solution architect] Branch published baseline → model alternative → compare topology/layout diffs → request approval →… | P3 | BL-303 |  |  | R2 |  |
| J-LIN-01 | BRD 5.38 New cross-persona acce… | - | [Data architect] Search Customer Profile dataset → follow documented onboarding-to-policy lineage → inspect schema evid… | P4 | BL-401 |  |  | R2 |  |
| J-IMP-01 | BRD 5.38 New cross-persona acce… | - | [Architect] Import draw.io diagram → map Azure icons and edges → reject unsupported connections → publish approved view… | P3 | BL-302 |  |  | R2 |  |
| J-FBK-01 | BRD 5.38 New cross-persona acce… | - | [Developer] Flag wrong API owner → attach documentation → owner reviews and approves → Passport updates with audit and… | P1 | BL-119 |  |  | R2 |  |
| J-STORY-01 | BRD 5.38 New cross-persona acce… | - | [Architect] Build four architecture scenes → present by keyboard → export. Scene transitions are readable, preserve sou… | P3 | BL-307 |  |  | R2 |  |
| J01 | BRD §6 J01 | - | Developer onboarding: search 'Policy Issuance' → service home → API contracts → dependency path to APIM/AKS/DB → repo/r… | P1 | BL-110 BL-111 BL-114 |  |  | R2 |  |
| J02 | BRD §6 J02 | - | APIM change impact: select operation → environment → verified consumers and transitive candidates → owners/confidence/u… | P2 | BL-211 BL-209 |  |  | R2 |  |
| J03 | BRD §6 J03 | - | Production incident: select Service Bus namespace → documented producers/consumers/subscriptions → owners, processes, r… | P2 | BL-207 BL-211 | DEC-079 |  | R0 |  |
| J04 | BRD §6 J04 | - | Architecture design review: published state → proposal branch → edit → compare → comment → approve → publish; layout su… | P1 | BL-116 BL-303 |  |  | R2 |  |
| J05 | BRD §6 J05 | - | Security review: filter customer-data flows → inspect auth, private endpoints, routes, stores → flag evidence gaps; ver… | P4 | BL-406 |  |  | R2 |  |
| J06 | BRD §6 J06 | - | Cloud platform discovery: subscription → RG → VNet → AKS → namespace → service; search resource ID and focus in hierarc… | P2 | BL-204 BL-113 |  |  | R2 |  |

### US — User stories

Backend: `various` · Frontend: `various` · API: see backlog · Data: -

| ID | Src § | Pri | Requirement | Phase | Backlog | Open decisions | Gaps | Ready | Notes |
|---|---|---|---|---|---|---|---|---|---|
| US-01 | BRD 14. User stories and accept… | - | As a developer, I can search for an API or resource and open its architecture context. | P1 | BL-111 |  |  | R2 |  |
| US-02 | BRD 14. User stories and accept… | - | As an architect, I can expand AKS cluster → namespace → service. | P1 | BL-113 |  |  | R2 |  |
| US-03 | BRD 14. User stories and accept… | - | As an architect, I can manually route a connector and save a named view. | P1 | BL-114 BL-117 |  |  | R2 |  |
| US-04 | BRD 14. User stories and accept… | - | As an SRE, I can trace a Service Bus dependency. | P2 | BL-207 BL-211 |  |  | R2 |  |
| US-05 | BRD 14. User stories and accept… | - | As a reviewer, I can compare current and proposed architectures. | P3 | BL-303 |  |  | R2 |  |
| US-06 | BRD 14. User stories and accept… | - | As a security analyst, I can inspect data classification and trust boundaries. | P4 | BL-406 BL-104 | DEC-073 |  | R0 |  |
| US-07 | BRD 14. User stories and accept… | - | As a developer, I can inspect service code and runbook links. | P1 | BL-110 |  |  | R2 |  |
| US-08 | BRD 14. User stories and accept… | - | As an engineer, I can use all canvas controls in a real browser. | P1 | BL-122 |  |  | R2 |  |
| US-09 | BRD 14. User stories and accept… | - | As an owner, I can correct an inaccurate dependency. | P1 | BL-119 |  |  | R2 |  |
| US-10 | BRD 14. User stories and accept… | - | As a user, I can ask Atlas which systems depend on an API. | P4 | BL-404 |  |  | R2 |  |

### UX-CAN — Canvas

Backend: `layouts, projections` · Frontend: `components/canvas, features/explore, features/studio` · API: GET /views/{id}/projection; POST /views/{id}/expand; PUT /views/{id}/layout; GET layout MISSING · Data: view_definition, view_layout

| ID | Src § | Pri | Requirement | Phase | Backlog | Open decisions | Gaps | Ready | Notes |
|---|---|---|---|---|---|---|---|---|---|
| UX-CAN-001 | UX 4.2 Canvas interaction requ… | Must | Single-click node selects and opens inspector. | P1 | BL-109 |  | API | R1 |  |
| UX-CAN-002 | UX 4.2 Canvas interaction requ… | Must | Double-click application enters X-Ray or opens a clear drill-down affordance. | P1 | BL-109 |  | API | R1 |  |
| UX-CAN-003 | UX 4.2 Canvas interaction requ… | Must | Hover reveals contextual affordances without hiding key labels. | P1 | BL-109 |  | API | R1 |  |
| UX-CAN-004 | UX 4.2 Canvas interaction requ… | Must | Drag empty canvas to pan; scroll/pinch to zoom around pointer. | P1 | BL-109 |  | API | R1 |  |
| UX-CAN-005 | UX 4.2 Canvas interaction requ… | Must | Search and highlight matching nodes; optionally center selected result. | P1 | BL-111 BL-109 |  | API | R1 |  |
| UX-CAN-006 | UX 4.2 Canvas interaction requ… | Must | Toggle lens and environment with clear data boundaries. | P1 | BL-109 |  | API | R1 |  |
| UX-CAN-007 | UX 4.2 Canvas interaction requ… | Must | Expand group, collapse group, and expand one level only. | P1 | BL-113 |  | API | R1 |  |
| UX-CAN-008 | UX 4.2 Canvas interaction requ… | Must | Select a connector to see direction, protocol, evidence, confidence and linked contract. | P1 | BL-109 BL-108 |  | API | R1 |  |
| UX-CAN-009 | UX 4.2 Canvas interaction requ… | Must | Group edges and reveal exact members on request. | P1 | BL-108 BL-109 |  | API | R1 |  |
| UX-CAN-010 | UX 4.2 Canvas interaction requ… | Must | Save a personal view of filters, lens, viewport, expanded groups and visible labels. | P1 | BL-114 | DEC-059 DEC-067 | API | R0 |  |
| UX-CAN-011 | UX 4.2 Canvas interaction requ… | Must | Edit mode is explicitly entered with appropriate permissions. | P1 | BL-116 |  | API | R1 |  |
| UX-CAN-012 | UX 4.2 Canvas interaction requ… | Must | In edit mode, add node from searchable Azure/component palette. | P1 | BL-117 | DEC-061 | API | R0 |  |
| UX-CAN-013 | UX 4.2 Canvas interaction requ… | Must | Create directed edge by connecting visible ports; choose relationship type. | P1 | BL-117 |  | API | R1 |  |
| UX-CAN-014 | UX 4.2 Canvas interaction requ… | Must | Drag, align, distribute and resize editable nodes/containers. | P1 | BL-117 |  | API | R1 |  |
| UX-CAN-015 | UX 4.2 Canvas interaction requ… | Must | Support orthogonal routing and manual waypoints in edit mode. | P1 | BL-117 |  | API | R1 |  |
| UX-CAN-016 | UX 4.2 Canvas interaction requ… | Must | Undo/redo reversible draft edits with keyboard shortcuts. | P1 | BL-116 |  | API | R1 |  |
| UX-CAN-017 | UX 4.2 Canvas interaction requ… | Must | Show dirty, saving, saved, conflict and failed-save states. | P1 | BL-116 BL-114 |  | API | R1 |  |
| UX-CAN-018 | UX 4.2 Canvas interaction requ… | Must | Export visible view to PNG/SVG/PDF and architecture metadata when permitted. | P1 | BL-120 | DEC-064 | API | R0 |  |
| UX-CAN-019 | UX 4.2 Canvas interaction requ… | Must | Provide accessible keyboard node list and inspector navigation. | P1 | BL-115 |  | API | R1 |  |
| UX-CAN-020 | UX 4.2 Canvas interaction requ… | Must | Handle thousands of total entities via semantic zoom and progressive rendering. | P1 | BL-108 BL-109 | DEC-060 | API | R0 |  |
| UX-CAN-021 | UX 4.2 Canvas interaction requ… | Should | Support pinned labels, bookmarks, annotation callouts and curated view layouts. | P3 | BL-307 |  | API | R1 |  |
| UX-CAN-022 | UX 4.2 Canvas interaction requ… | Should | Show edge-path focus: upstream, downstream, one-hop, N-hop. | P2 | BL-211 |  | API | R1 |  |
| UX-CAN-023 | UX 4.2 Canvas interaction requ… | Must | Show source freshness and uncertainty on visible entities. | P1 | BL-109 |  | API | R1 |  |
| UX-CAN-024 | UX 4.2 Canvas interaction requ… | Must | Context menu offers only permitted actions. | P1 | BL-109 BL-104 | DEC-051 | API | R0 |  |

### UX-XR — Architecture X-Ray

Backend: `projections, layouts` · Frontend: `features/explore (X-Ray)` · API: POST /views/{id}/expand · Data: view_layout, relationship

| ID | Src § | Pri | Requirement | Phase | Backlog | Open decisions | Gaps | Ready | Notes |
|---|---|---|---|---|---|---|---|---|---|
| UX-XR-001 | UX 5.1 Interaction model | Must | In-place expansion and collapse. | P1 | BL-113 |  |  | R2 |  |
| UX-XR-002 | UX 5.1 Interaction model | Must | Multi-level nested navigation with breadcrumbs. | P1 | BL-113 |  |  | R2 |  |
| UX-XR-003 | UX 5.1 Interaction model | Must | Abstraction level selector. | P1 | BL-113 | DEC-060 |  | R0 |  |
| UX-XR-004 | UX 5.1 Interaction model | Must | Cross-boundary edge bundling. | P1 | BL-113 |  |  | R2 |  |
| UX-XR-005 | UX 5.1 Interaction model | Must | Evidence and uncertainty display. | P1 | BL-113 |  |  | R2 |  |
| UX-XR-006 | UX 5.1 Interaction model | Must | Per-view expansion state persistence. | P1 | BL-114 | DEC-059 |  | R0 |  |
| UX-XR-007 | UX 5.1 Interaction model | Must | Large-child-set handling. | P1 | BL-113 |  |  | R2 |  |
| UX-XR-008 | UX 5.1 Interaction model | Should | Side-by-side logical and physical mapping. | P1 | BL-113 |  |  | R2 |  |
| UX-XR-009 | UX 5.1 Interaction model | Must | Permission-aware hierarchy. | P1 | BL-113 BL-104 |  |  | R2 |  |
| UX-XR-010 | UX 5.1 Interaction model | Should | “Explain this layer” helper. | P4 | BL-404 |  |  | R2 |  |

### UX-PASS — Architecture Passport

Backend: `passports` · Frontend: `/applications/:id, inspector` · API: GET /entities/{id}/passport (section schema MISSING) · Data: entity, fact_provenance, document

| ID | Src § | Pri | Requirement | Phase | Backlog | Open decisions | Gaps | Ready | Notes |
|---|---|---|---|---|---|---|---|---|---|
| UX-PASS-001 | UX 6.3 Passport interaction re… | Must | Stable deep link and canonical identity. | P1 | BL-110 BL-112 |  | API | R1 |  |
| UX-PASS-002 | UX 6.3 Passport interaction re… | Must | Clear overview with owner, purpose, lifecycle and evidence freshness above the fold. | P1 | BL-110 | DEC-062 | API | R0 |  |
| UX-PASS-003 | UX 6.3 Passport interaction re… | Must | Dependency mini-map with upstream/downstream tabs. | P1 | BL-110 |  | API | R1 |  |
| UX-PASS-004 | UX 6.3 Passport interaction re… | Must | Links to contracts, diagrams, ADRs, runbooks and repositories. | P1 | BL-110 |  | API | R1 |  |
| UX-PASS-005 | UX 6.3 Passport interaction re… | Must | Environment switcher with explicit environment scoping. | P1 | BL-110 |  | API | R1 |  |
| UX-PASS-006 | UX 6.3 Passport interaction re… | Must | Proposed correction workflow. | P1 | BL-119 | DEC-063 | API | R0 |  |
| UX-PASS-007 | UX 6.3 Passport interaction re… | Must | Provenance per important field. | P1 | BL-110 |  | API | R1 |  |
| UX-PASS-008 | UX 6.3 Passport interaction re… | Must | Explicit missing, stale and conflicting information states. | P1 | BL-110 |  | API | R1 |  |
| UX-PASS-009 | UX 6.3 Passport interaction re… | Should | Follow/bookmark and share exact Passport section. | P1 | BL-114 |  | API | R1 |  |
| UX-PASS-010 | UX 6.3 Passport interaction re… | Must | Restricted metadata redaction. | P1 | BL-110 BL-104 |  | API | R1 |  |
| UX-PASS-011 | UX 6.3 Passport interaction re… | Should | Completeness checklist and stewardship action. | P1 | BL-119 | DEC-063 | API | R0 |  |
| UX-PASS-012 | UX 6.3 Passport interaction re… | Must | One-click “Explore on canvas” and “Open X-Ray.” | P1 | BL-110 BL-112 |  | API | R1 |  |

### UX-ICR — Contract registry

Backend: `contracts` · Frontend: `/contracts` · API: GET /contracts; GET /contracts/{id}/diff; import MISSING · Data: contract, contract_version

| ID | Src § | Pri | Requirement | Phase | Backlog | Open decisions | Gaps | Ready | Notes |
|---|---|---|---|---|---|---|---|---|---|
| UX-ICR-001 | UX 7. Screen D | Must | Unified searchable inventory of OpenAPI, AsyncAPI and approved documented interfaces. | P2 | BL-209 |  | API | R1 |  |
| UX-ICR-002 | UX 7. Screen D | Must | Contract detail with version, owner, status, endpoints/topics and source. | P2 | BL-209 |  | API | R1 |  |
| UX-ICR-003 | UX 7. Screen D | Must | Producer/consumer map with Passport deep links. | P2 | BL-209 |  | API | R1 |  |
| UX-ICR-004 | UX 7. Screen D | Must | Side-by-side version comparison. | P2 | BL-209 | DEC-071 | API | R0 |  |
| UX-ICR-005 | UX 7. Screen D | Must | Access-aware schema display. | P2 | BL-209 | DEC-073 | API | R0 |  |
| UX-ICR-006 | UX 7. Screen D | Should | Deprecation notice and owner subscription. | P2 | BL-209 |  | API | R1 |  |
| UX-ICR-007 | UX 7. Screen D | Must | Conflicting imported contract resolution. | P2 | BL-209 |  | API | R1 |  |

### UX-PAT — Pattern library

Backend: `patterns` · Frontend: `/patterns` · API: pattern endpoints MISSING · Data: pattern, pattern_version

| ID | Src § | Pri | Requirement | Phase | Backlog | Open decisions | Gaps | Ready | Notes |
|---|---|---|---|---|---|---|---|---|---|
| UX-PAT-001 | UX 8. Screen E | Must | Bright, visual pattern gallery with categories and approved badges. | P3 | BL-304 |  | API | R1 |  |
| UX-PAT-002 | UX 8. Screen E | Must | Pattern detail with preview diagram, constraints, trade-offs and references. | P3 | BL-304 |  | API | R1 |  |
| UX-PAT-003 | UX 8. Screen E | Must | “Use in sandbox” wizard-free parameter panel. | P3 | BL-304 |  | API | R1 |  |
| UX-PAT-004 | UX 8. Screen E | Must | Draft isolation and versioned pattern lineage. | P3 | BL-304 |  | API | R1 |  |
| UX-PAT-005 | UX 8. Screen E | Should | Rule evaluation before review submission. | P3 | BL-305 |  | API | R1 |  |
| UX-PAT-006 | UX 8. Screen E | Must | Approval/deprecation clarity. | P3 | BL-304 | DEC-063 | API | R0 |  |

### UX-RULE — Rule engine

Backend: `rules` · Frontend: `/rules, /evaluations/:id` · API: POST /rules/evaluations; catalog/exception endpoints MISSING · Data: rule_definition, rule_evaluation, rule_finding, exception

| ID | Src § | Pri | Requirement | Phase | Backlog | Open decisions | Gaps | Ready | Notes |
|---|---|---|---|---|---|---|---|---|---|
| UX-RULE-001 | UX 9. Screen F | Must | Rule catalog with category, owner, severity, version and applicability. | P3 | BL-305 |  | API | R1 |  |
| UX-RULE-002 | UX 9. Screen F | Must | Evaluation report with PASS, FAIL, UNKNOWN, N/A, EXEMPT. | P3 | BL-305 |  | API | R1 |  |
| UX-RULE-003 | UX 9. Screen F | Must | Click finding to focus exact node/edge on canvas. | P3 | BL-305 |  | API | R1 |  |
| UX-RULE-004 | UX 9. Screen F | Must | Exception request and approval flow. | P3 | BL-305 | DEC-063 | API | R0 |  |
| UX-RULE-005 | UX 9. Screen F | Must | Deterministic evaluation and safe testing. | P3 | BL-305 |  | API | R1 |  |
| UX-RULE-006 | UX 9. Screen F | Should | Report export and saved filters. | P3 | BL-305 |  | API | R1 |  |

### UX-GLB — Product experience

Backend: `-` · Frontend: `shell` · API: n/a · Data: -

| ID | Src § | Pri | Requirement | Phase | Backlog | Open decisions | Gaps | Ready | Notes |
|---|---|---|---|---|---|---|---|---|---|
| UX-GLB-001 | UX 10. Cross-screen interactio… | Must | Global search supports aliases, synonyms and fuzzy matches. | P1 | BL-111 |  |  | R2 |  |
| UX-GLB-002 | UX 10. Cross-screen interactio… | Must | Search result opens exact entity or relevant graph view. | P1 | BL-111 BL-112 |  |  | R2 |  |
| UX-GLB-003 | UX 10. Cross-screen interactio… | Must | Role-aware actions and navigation. | P1 | BL-104 | DEC-027 DEC-051 |  | R0 |  |
| UX-GLB-004 | UX 10. Cross-screen interactio… | Must | Contextual onboarding and empty states. | P1 | BL-121 |  |  | R2 |  |
| UX-GLB-005 | UX 10. Cross-screen interactio… | Must | Consistent save, draft, review and publish language. | P1 | BL-116 BL-121 |  |  | R2 |  |
| UX-GLB-006 | UX 10. Cross-screen interactio… | Must | Toasts and errors identify action, outcome and recovery. | P1 | BL-121 |  |  | R2 |  |
| UX-GLB-007 | UX 10. Cross-screen interactio… | Must | Accessibility: keyboard, focus, labels, contrast, reduced motion. | P1 | BL-115 BL-122 |  |  | R2 |  |
| UX-GLB-008 | UX 10. Cross-screen interactio… | Must | Share links preserve entity, view, lens, filters and focus where authorized. | P1 | BL-112 | DEC-067 |  | R0 |  |
| UX-GLB-009 | UX 10. Cross-screen interactio… | Should | User preferences for density, label size and panel width. | P1 | BL-114 |  |  | R2 |  |
| UX-GLB-010 | UX 10. Cross-screen interactio… | Must | Trust indicators show source, sync time, verified status and scope. | P1 | BL-109 BL-003 |  |  | R2 |  |
| UX-GLB-011 | UX 10. Cross-screen interactio… | Must | Global feedback entry for incorrect architecture data. | P1 | BL-119 |  |  | R2 |  |
| UX-GLB-012 | UX 10. Cross-screen interactio… | Must | No PR or telemetry affordances. | P1 | BL-105 BL-122 |  |  | R2 |  |

### UX-NFR — Non-functional (BRD §8, proposed IDs)

Backend: `cross-cutting` · Frontend: `cross-cutting` · API: n/a · Data: -

| ID | Src § | Pri | Requirement | Phase | Backlog | Open decisions | Gaps | Ready | Notes |
|---|---|---|---|---|---|---|---|---|---|
| UX-NFR-001 | UX 11. Scale, speed and qualit… | Gate | Search responsiveness: p95 indexed query response ≤ 1.5 s in pilot dataset, excluding cold startup | P1 | BL-111 BL-125 | DEC-054 |  | R0 |  |
| UX-NFR-002 | UX 11. Scale, speed and qualit… | Gate | Passport navigation: p95 interactive page ≤ 2.5 s on agreed corporate laptop/network profile | P1 | BL-110 BL-125 | DEC-054 |  | R0 |  |
| UX-NFR-003 | UX 11. Scale, speed and qualit… | Gate | Canvas initial view: p95 interactive curated view ≤ 3 s with default bounded visible objects | P1 | BL-108 BL-125 | DEC-054 |  | R0 |  |
| UX-NFR-004 | UX 11. Scale, speed and qualit… | Gate | Large enterprise graph: 10,000+ total entities indexed; default rendering uses semantic grouping rather than displaying… | P1 | BL-108 BL-016 | DEC-054 |  | R0 |  |
| UX-NFR-005 | UX 11. Scale, speed and qualit… | Gate | Canvas interaction: Pan/zoom aims for perceptually smooth interaction on reference hardware; profile with agreed browse… | P1 | BL-109 BL-125 | DEC-054 |  | R0 |  |
| UX-NFR-006 | UX 11. Scale, speed and qualit… | Gate | Data integrity: Save/reload retains layout, hierarchy, route waypoints and draft revision without silent loss | P1 | BL-114 BL-116 |  |  | R2 |  |
| UX-NFR-007 | UX 11. Scale, speed and qualit… | Gate | Export quality: SVG and PDF vector output where supported; PNG crisp at selected output scale; official icons remain re… | P1 | BL-120 | DEC-064 |  | R0 |  |
| UX-NFR-008 | UX 11. Scale, speed and qualit… | Gate | Accessibility: WCAG 2.2 AA for application chrome and equivalent keyboard access for essential graph exploration | P1 | BL-115 BL-122 |  |  | R2 |  |
| UX-NFR-009 | UX 11. Scale, speed and qualit… | Gate | Security: No unauthorized entity/field disclosure through UI, search, URL, exports, snapshots or AI | P1 | BL-104 BL-122 |  |  | R2 |  |
| UX-NFR-010 | UX 11. Scale, speed and qualit… | Gate | Reliability: Connector failure does not block exploration of last-known published graph; freshness warning shown | P2 | BL-208 |  |  | R2 |  |
| UX-NFR-011 | UX 11. Scale, speed and qualit… | Gate | Browser E2E: All flagship flows tested in real Chromium and one additional supported browser | P1 | BL-122 | DEC-055 |  | R0 |  |
| UX-NFR-012 | UX 11. Scale, speed and qualit… | Gate | Visual regression: Golden screenshots at 1440×900 and 1280×720 for core screens; meaningful review of changes | P1 | BL-122 | DEC-055 |  | R0 |  |
| UX-NFR-013 | UX 11. Scale, speed and qualit… | Gate | Pilot usability: 5+ representatives per key persona group in moderated testing; track task completion, time and satisfa… | P0 | BL-025 | DEC-054 |  | R0 |  |
| UX-NFR-014 | UX 11. Scale, speed and qualit… | Gate | Data trust: Every imported fact carries source and timestamp; conflicts visible; no fabricated default ownership | P1 | BL-101 BL-202 |  |  | R2 |  |

### UX-MOD — Multi-level modeling

Backend: `catalog, projections` · Frontend: `canvas (lens/level selector)` · API: GET /views/{id}/projection; GET /taxonomy MISSING · Data: entity_type, relationship, view_definition

| ID | Src § | Pri | Requirement | Phase | Backlog | Open decisions | Gaps | Ready | Notes |
|---|---|---|---|---|---|---|---|---|---|
| UX-MOD-01 | UX 18. V2.2 additional bright… | - | [All] Switch context, application, component and deployment projection from view selector | P1 | BL-108 |  | API | R1 |  |

### UX-BCM — Capability mapping

Backend: `catalog, projections` · Frontend: `features/intelligence (capability map)` · API: GET /capabilities/{id}/map · Data: entity (capability), relationship

| ID | Src § | Pri | Requirement | Phase | Backlog | Open decisions | Gaps | Ready | Notes |
|---|---|---|---|---|---|---|---|---|---|
| UX-BCM-01 | UX 18. V2.2 additional bright… | - | [Intelligence] Browse color-coded capability map and expand Claims into supporting systems | P1 | BL-123 BL-402 | DEC-052 |  | R0 |  |

### UX-REC — Reconciliation

Backend: `reconciliation, sources` · Frontend: `features/intelligence (inbox)` · API: GET /reconciliation/cases; POST .../resolve · Data: reconciliation_case, source_identity, source_observation

| ID | Src § | Pri | Requirement | Phase | Backlog | Open decisions | Gaps | Ready | Notes |
|---|---|---|---|---|---|---|---|---|---|
| UX-REC-01 | UX 18. V2.2 additional bright… | - | [Intelligence] Steward opens conflict inbox and compares field-level source evidence | P2 | BL-203 | DEC-057 |  | R0 |  |

### UX-AAC — Architecture-as-code

Backend: `designs, sources` · Frontend: `features/studio (import preview)` · API: POST /imports/preview\|commit; export MISSING · Data: branch_change, source_observation

| ID | Src § | Pri | Requirement | Phase | Backlog | Open decisions | Gaps | Ready | Notes |
|---|---|---|---|---|---|---|---|---|---|
| UX-AAC-01 | UX 18. V2.2 additional bright… | - | [Studio] Import YAML/JSON and inspect staged graph diff | P3 | BL-301 |  | API | R1 |  |

### UX-BRN — Branching & merging

Backend: `designs` · Frontend: `features/studio (diff)` · API: POST /branches...; diff/merge/discard MISSING · Data: architecture_branch, branch_change

| ID | Src § | Pri | Requirement | Phase | Backlog | Open decisions | Gaps | Ready | Notes |
|---|---|---|---|---|---|---|---|---|---|
| UX-BRN-01 | UX 18. V2.2 additional bright… | - | [Studio] Compare baseline and alternative in split-screen | P3 | BL-303 |  | API | R1 |  |

### UX-ADR — Decisions & knowledge (req family)

Backend: `knowledge` · Frontend: `Passport Documents tab` · API: document/decision endpoints MISSING · Data: document, decision

| ID | Src § | Pri | Requirement | Phase | Backlog | Open decisions | Gaps | Ready | Notes |
|---|---|---|---|---|---|---|---|---|---|
| UX-ADR-01 | UX 18. V2.2 additional bright… | - | [Explore] Open contextual decision from node, edge or Passport | P3 | BL-306 |  | API | R1 |  |

### UX-LIN — Data lineage

Backend: `lineage` · Frontend: `features/intelligence (lineage)` · API: GET /lineage/{dataset_id} · Data: dataset, relationship

| ID | Src § | Pri | Requirement | Phase | Backlog | Open decisions | Gaps | Ready | Notes |
|---|---|---|---|---|---|---|---|---|---|
| UX-LIN-01 | UX 18. V2.2 additional bright… | - | [Explore / Intelligence] Follow documented dataset lineage with scope controls | P4 | BL-401 |  |  | R2 |  |

### UX-SDK — Connector SDK

Backend: `connectors, sources` · Frontend: `admin` · API: connector package/admin endpoints MISSING · Data: source_system

| ID | Src § | Pri | Requirement | Phase | Backlog | Open decisions | Gaps | Ready | Notes |
|---|---|---|---|---|---|---|---|---|---|
| UX-SDK-01 | UX 18. V2.2 additional bright… | - | [Admin] Configure connector and preview mapped entities | P2 | BL-210 |  | API | R1 |  |

### UX-NTF — Notifications

Backend: `NOT IN TECH MODULE LIST` · Frontend: `shell (notices)` · API: MISSING · Data: subscription tables MISSING

| ID | Src § | Pri | Requirement | Phase | Backlog | Open decisions | Gaps | Ready | Notes |
|---|---|---|---|---|---|---|---|---|---|
| UX-NTF-01 | UX 18. V2.2 additional bright… | - | [Explore] Follow component and manage digest/mute settings | P5 | BL-501 |  | API DATA | R1 |  |

### UX-COL — Collaboration

Backend: `designs` · Frontend: `features/studio (comments)` · API: comment endpoints MISSING · Data: review (comments MISSING)

| ID | Src § | Pri | Requirement | Phase | Backlog | Open decisions | Gaps | Ready | Notes |
|---|---|---|---|---|---|---|---|---|---|
| UX-COL-01 | UX 18. V2.2 additional bright… | - | [Studio] Comment on a draft node and resolve review thread | P3 | BL-308 | DEC-077 | API DATA | R0 |  |

### UX-CMD — Command palette & workspace

Backend: `search, identity` · Frontend: `shell (Cmd+K)` · API: GET /search; preferences/favorites MISSING · Data: user preference tables MISSING

| ID | Src § | Pri | Requirement | Phase | Backlog | Open decisions | Gaps | Ready | Notes |
|---|---|---|---|---|---|---|---|---|---|
| UX-CMD-01 | UX 18. V2.2 additional bright… | - | [All] Cmd/Ctrl+K to search or invoke permitted action | P1 | BL-111 |  | API DATA | R1 |  |

### UX-STORY — Storytelling

Backend: `layouts` · Frontend: `features/studio (presentation)` · API: story endpoints MISSING · Data: story/scene tables MISSING

| ID | Src § | Pri | Requirement | Phase | Backlog | Open decisions | Gaps | Ready | Notes |
|---|---|---|---|---|---|---|---|---|---|
| UX-STORY-01 | UX 18. V2.2 additional bright… | - | [Studio] Author and present stepwise architecture scenes | P3 | BL-307 |  | API DATA | R1 |  |

### UX-IMP — Legacy diagram import

Backend: `sources, designs` · Frontend: `features/studio (import)` · API: POST /imports/preview\|commit · Data: source_observation, branch_change

| ID | Src § | Pri | Requirement | Phase | Backlog | Open decisions | Gaps | Ready | Notes |
|---|---|---|---|---|---|---|---|---|---|
| UX-IMP-01 | UX 18. V2.2 additional bright… | - | [Studio] Upload draw.io/Visio interchange file and map shapes in preview | P3 | BL-302 |  |  | R2 |  |

### UX-FBK — Feedback & correction

Backend: `knowledge, audit` · Frontend: `global feedback entry` · API: POST /feedback; list/review MISSING · Data: feedback_request, review, audit_event

| ID | Src § | Pri | Requirement | Phase | Backlog | Open decisions | Gaps | Ready | Notes |
|---|---|---|---|---|---|---|---|---|---|
| UX-FBK-01 | UX 18. V2.2 additional bright… | - | [All] Report incorrect owner or relationship from current context | P1 | BL-119 |  | API | R1 |  |

### E — BRD experience sections

Backend: `various` · Frontend: `various` · API: see backlog · Data: -

| ID | Src § | Pri | Requirement | Phase | Backlog | Open decisions | Gaps | Ready | Notes |
|---|---|---|---|---|---|---|---|---|---|
| E01 | BRD V2.0 E01 | - | Enterprise landscape and visual canvas (experience contract, business rules, failure handling, 4 Given/When/Then). | P1 | BL-109 |  |  | R2 |  |
| E02 | BRD V2.0 E02 | - | Search, navigation and developer workspace (3 Given/When/Then). | P1 | BL-111 |  |  | R2 |  |
| E03 | BRD V2.0 E03 | - | Canonical graph, evidence and reconciliation (3 Given/When/Then). | P1 | BL-101 BL-203 |  |  | R2 |  |
| E04 | BRD V2.0 E04 | - | Azure and enterprise connector discovery (3 Given/When/Then). | P2 | BL-204 |  |  | R2 |  |
| E05 | BRD V2.0 E05 | - | Architecture X-Ray (2 Given/When/Then). | P1 | BL-113 |  |  | R2 |  |
| E06 | BRD V2.0 E06 | - | Architecture Passport and knowledge hub (2 Given/When/Then). | P1 | BL-110 |  |  | R2 |  |
| E07 | BRD V2.0 E07 | - | Integration Contract Registry (2 Given/When/Then). | P2 | BL-209 |  |  | R2 |  |
| E08 | BRD V2.0 E08 | - | Pattern Library and future-state sandbox (2 Given/When/Then). | P3 | BL-304 |  |  | R2 |  |
| E09 | BRD V2.0 E09 | - | Rule Engine and scorecards (3 Given/When/Then). | P3 | BL-305 |  |  | R2 |  |
| E10 | BRD V2.0 E10 | - | Dependency analysis, time machine and design-time playback (3 Given/When/Then). | P2 | BL-211 BL-403 |  |  | R2 |  |
| E11 | BRD V2.0 E11 | - | AI-assisted architecture intelligence (3 Given/When/Then). | P4 | BL-404 |  |  | R2 |  |
| E12 | BRD V2.0 E12 | - | Security, data flows, cost and self-service (2 Given/When/Then). | P4 | BL-406 BL-502 |  |  | R2 |  |
| E13 | BRD V2.0 E13 | - | Governance, collaboration and enterprise trust (3 Given/When/Then). | P1 | BL-116 BL-303 |  |  | R2 |  |
| E14 | BRD V2.0 E14 | - | Performance, accessibility and resilience (3 Given/When/Then). | P1 | BL-125 BL-122 | DEC-054 |  | R0 |  |
| E16 | BRD V2.0 E16 | - | Core entity Passport field contract (mandatory/recommended/unknown handling per entity class). | P1 | BL-110 | DEC-062 |  | R0 |  |
| E17 | BRD V2.0 E17 | - | Lifecycle and permission expectations (draft/review/published/superseded per object; minimum role separation). | P0 | BL-004 | DEC-051 DEC-063 |  | R0 |  |
| E18 | BRD V2.0 E18 | - | Quality and design acceptance matrix (10 release-blocking quality gates). | P1 | BL-122 | DEC-055 |  | R0 |  |

### NFR — Non-functional (BRD §8, proposed IDs)

Backend: `cross-cutting` · Frontend: `cross-cutting` · API: n/a · Data: -

| ID | Src § | Pri | Requirement | Phase | Backlog | Open decisions | Gaps | Ready | Notes |
|---|---|---|---|---|---|---|---|---|---|
| NFR-01 | BRD §8 (ID proposed by blueprin… | - | Scale: pilot 10k resources / 100k relationships; design for 100k+ / 1m+ via progressive loading. | P1 | BL-125 BL-407 | DEC-054 |  | R0 |  |
| NFR-02 | BRD §8 (ID proposed by blueprin… | - | Rendering: first meaningful render ≤2 s p75; pan/zoom 45–60 FPS for curated views. | P1 | BL-109 BL-125 | DEC-054 |  | R0 |  |
| NFR-03 | BRD §8 (ID proposed by blueprin… | - | Interaction: no blocking main-thread layout; click/drill/inspector covered by browser E2E. | P1 | BL-109 BL-122 |  |  | R2 |  |
| NFR-04 | BRD §8 (ID proposed by blueprin… | - | Search: p95 <1.5 s for indexed common queries under pilot load. | P1 | BL-111 | DEC-054 |  | R0 |  |
| NFR-05 | BRD §8 (ID proposed by blueprin… | - | Graph queries: p95 <3 s for bounded 1–3 hop traces; deeper traversals async/progressive. | P1 | BL-108 BL-125 | DEC-054 |  | R0 |  |
| NFR-06 | BRD §8 (ID proposed by blueprin… | - | Availability: pilot SLO 99.5% proposed; production target and DR to be approved. | P1 | BL-126 | DEC-074 |  | R0 |  |
| NFR-07 | BRD §8 (ID proposed by blueprin… | - | Security: SSO, RBAC/ABAC, least-privilege connectors, encryption, audit, secrets management. | P1 | BL-104 BL-022 | DEC-027 DEC-051 |  | R0 |  |
| NFR-08 | BRD §8 (ID proposed by blueprin… | - | Privacy: data minimization, redaction of secrets/PII, classification-aware search and AI grounding. | P1 | BL-104 BL-022 | DEC-073 |  | R0 |  |
| NFR-09 | BRD §8 (ID proposed by blueprin… | - | Resilience: connector failures never blank the canvas; last-known-good snapshot + freshness warning. | P2 | BL-208 |  |  | R2 |  |
| NFR-10 | BRD §8 (ID proposed by blueprin… | - | Accessibility: keyboard-operable core functions, visible focus, canvas alternatives, WCAG 2.2 AA. | P1 | BL-115 BL-122 |  |  | R2 |  |
| NFR-11 | BRD §8 (ID proposed by blueprin… | - | Portability: Chrome/Edge/Safari; browser-tested deployment URL. | P1 | BL-122 BL-010 | DEC-055 |  | R0 |  |
| NFR-12 | BRD §8 (ID proposed by blueprin… | - | Observability (Atlas itself): client errors, render time, query latency, sync lag, connector failures, feature adoption. | P1 | BL-126 | DEC-076 |  | R0 |  |
| NFR-13 | BRD §8 (ID proposed by blueprin… | - | Quality: unit, integration, contract, accessibility, performance, security and E2E release gates. | P1 | BL-122 |  |  | R2 |  |
