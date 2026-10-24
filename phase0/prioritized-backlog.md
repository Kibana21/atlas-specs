# Atlas — Prioritized Feature Backlog (Phase 0 baseline)

**Version:** 0.1 · **Date:** 24 October 2026 · **Status:** Proposed. Sequencing and estimates are directional (tech §18) and not staffing commitments.  
**Companions:** `Atlas_Phase0_Engineering_Blueprint_v0_1.md` (rationale and order), `requirement-traceability-matrix.md` / `requirements-registry.csv` (requirement → backlog mapping), `../decisions/decision-register.md` (DEC IDs).

## Conventions

- **ID ranges:** `BL-0xx` Phase 0 (decisions, contracts, fixtures, spikes; **no production code**), `BL-1xx` Phase 1 (Explore + Studio foundation), `BL-2xx` Phase 2 (trustworthy discovery), `BL-3xx` Phase 3 (design productivity), `BL-4xx` Phase 4 (intelligence), `BL-5xx` Phase 5 (enterprise expansion). BL-507 is scheduled in Phase 4.
- **Rank** = execution priority within the phase (1 = first). Cross-phase priority is strictly by phase: no item from phase N+1 starts before phase N's exit gate, except long-lead items marked ⏩ (start early, finish later).
- **Type:** `DEC` decision closure · `CON` contract/spec artifact · `FIX` fixture/test data · `SPK` throwaway spike (never merged to `main` of backend/frontend) · `FEAT` feature · `NFR` quality/non-functional · `OPS` delivery/CI.
- **Repo:** `S` atlas-specs · `B` atlas-backend · `F` atlas-frontend.
- **Reqs** = number of RTM requirements where the item is primary / total mapped. Enablers with 0 have no direct requirement but unblock others.
- Tech-design epics are referred to as **TE01–TE09** (tech §19) to avoid confusion with BRD experience sections E01–E20 (DEC-082).

---

## Phase 0 — Decisions, contracts and spikes (2–4 weeks; atlas-specs + throwaway spikes only)

Exit gate is in blueprint §9 ("Definition of Ready for production code").

| Rank | ID | Item | Type | Repo | Depends on | Closes / uses decisions | Reqs | Done when |
|---:|---|---|---|---|---|---|---:|---|
| 1 | BL-001 | Nominate sponsor, decision owners and sign-off RACI | DEC | S | – | DEC-081 | 0 | Named owner for every register row; App D sign-off roles filled |
| 2 | BL-002 | Canonical type taxonomy v1 + relationship-type matrix (allowed from/to, required attributes, parentage, multi-deployment) | DEC/CON | S | BL-001 | DEC-050, DEC-070 | 0/2 | `contracts/schemas/taxonomy.v1.json` + human-readable matrix approved by EA; BRD INV-02 alias mapping recorded |
| 3 | BL-003 | Unified trust / evidence / verification / completeness model + visual legend spec | DEC/CON | S | BL-002 | DEC-056, DEC-066 | 0/5 | One enum schema used by API, UI legend, export and AI; mock legend reviewed by UX |
| 4 | BL-004 | Role model, RBAC/ABAC matrix v1 and data-classification scheme | DEC | S | BL-001 | DEC-051, DEC-073, DEC-035, DEC-063 (draft) | 1/2 | Security-approved action × role × scope matrix incl. search, export, AI, connectors; classification levels defined |
| 5 | BL-006 | ADR: snapshot / revision / branch model + discovery publication semantics | DEC | S | BL-002 | DEC-031, DEC-057 | 0/1 | ADR-0008 accepted; worked example: sync update while a branch is open |
| 6 | BL-007 | ADRs: canonical identity (UUID format, provider keys, aliases) and source-precedence principles | DEC | S | BL-002 | DEC-025, DEC-034, DEC-037, DEC-058 | 0/2 | ADR-0001 + ADR-0003 accepted; tenancy decision recorded |
| 7 | BL-008 | ADR: authentication and session architecture (BFF vs SPA tokens) | DEC | S | BL-004 | DEC-026, DEC-027 | 0 | ADR-0005 accepted by Security; Entra app-registration requirements listed |
| 8 | BL-009 | Stack ADRs: backend, frontend, storage, jobs, search, hosting, tooling | DEC | S | BL-001 | DEC-020–024, DEC-028–030, DEC-038, DEC-041 | 0 | Each row in register §B moved to Confirmed or explicitly kept Proposed with owner |
| 9 | BL-005 | Adopt engineering phase scheme and priority semantics; re-baseline release mapping | DEC | S | BL-001 | DEC-052, DEC-053 | 0 | Blueprint §8 phase map approved by Product |
| 10 | BL-013 | Contract conventions: `contracts/compatibility.md`, versioning, pagination, error-code catalog, ID format, idempotency, `If-Match` | CON | S | BL-007 | DEC-039, DEC-071 | 0 | Conventions doc reviewed by both leads |
| 11 | BL-015 | JSON Schemas v0.1: entity, relationship, provenance/evidence, projection request/response, view state + deep-link encoding, layout, draft command union, error envelope, capability set | CON | S | BL-002, BL-003, BL-013 | DEC-050, DEC-056 | 0 | Schemas + valid/invalid examples in `contracts/schemas` and `contracts/examples`; lint passes |
| 12 | BL-014 | OpenAPI v0.1 for the Phase 1 vertical slice (see blueprint §6.3 list C-01…C-14) | CON | S | BL-015, BL-004 | DEC-039 | 0 | `contracts/openapi/atlas-api.yaml` reviewed; every Phase 1 FE screen has its endpoints |
| 13 | BL-016 | Golden fixture: MVP vertical slice (Digital Channels → APIM → New Business → Policy Administration → Claims), 250 entities / 700 relationships, with ACL personas, trust-state mix, conflicts, cycles; spec for 10k/100k generator | FIX | S | BL-002, BL-003, BL-004 | DEC-054, DEC-068 | 0/1 | Fixture in `acceptance/test-data`, sanitized, deterministic; generator spec written |
| 14 | BL-017 | Phase 1 acceptance journeys (Given/When/Then): owner lookup, X-Ray, 6-node draft save/reload/412, deep-link share, restricted-user negative paths, keyboard-only | CON | S | BL-016 | – | 0 | `acceptance/scenarios/*.md` linked to requirement IDs |
| 15 | BL-018 | Canvas spike: XYFlow + ELK worker, nested Azure groups, orthogonal routes, edge bundles, 100 / 1,000 / 2,000-node projections, real-browser timing | SPK | F (spike branch) | BL-015 draft | DEC-023, DEC-060 | 0 | Benchmark report in `phase0/spikes/`; go/no-go for DEC-023 |
| 16 | BL-019 | Persistence spike: PostgreSQL recursive-CTE projection + access filter at 100k / 500k with skewed hubs | SPK | B (spike branch) | BL-002 | DEC-021, DEC-022 | 0 | p95 numbers vs NFR targets; go/no-go for DEC-022 |
| 17 | BL-010 | NFR baseline: reference device/network, browser matrix, dataset tiers, consolidated targets | DEC | S | BL-001 | DEC-054, DEC-055 | 0/1 | One NFR table replaces the conflicting ones (blueprint §3) |
| 18 | BL-020 ⏩ | Azure icon licence review and pinned icon registry spec (`iconKey` ↔ taxonomy type) | DEC | S | BL-002 | DEC-061 | 0/1 | Legal sign-off; registry key list in taxonomy contract |
| 19 | BL-022 | Threat model (graph enumeration, counts, imports, SVG/XML, AI injection, connectors, exports, local draft storage) | NFR | S | BL-004, BL-008 | DEC-035 | 0/2 | Threat model doc with mitigations mapped to backlog items |
| 20 | BL-024 | Design tokens validated (contrast, CVD, Azure icon samples) → `design/tokens.md` | CON | S | – | DEC-065, DEC-011 | 0 | Token table with contrast evidence approved by UX |
| 21 | BL-025 | Clickable prototype + moderated usability round (BRD E19 Release 0, UX R0) | NFR | F (prototype) | BL-018, BL-024 | DEC-012 | 1/1 | Findings recorded; architect + developer journeys walked |
| 22 | BL-011 | Requirements registry adopted as ID authority; CI check for ID uniqueness and RTM coverage | OPS | S | – | DEC-082 | 0 | CI fails on duplicate IDs or unmapped requirements |
| 23 | BL-012 | Baseline document corrections (stale cross-references, swapped columns, duplicate §5.23, missing E15 note, tech §17.3 layout, INV-02 alias note) | CON | S | BL-002, BL-005 | DEC-040, DEC-082 | 0 | BRD v2.3 / UX v1.2 / Tech v1.2 with revision records (**requires owner approval to edit baselines**) |
| 24 | BL-021 | Repository bootstrap plan: `specs.lock`, CI skeletons, PR templates, CODEOWNERS (executed **after** blueprint approval, first Phase 1 task) | OPS | S → B, F | BL-009, BL-013 | DEC-038, DEC-039 | 0 | Bootstrap checklist approved; no backend/frontend changes in Phase 0 |
| 25 | BL-023 ⏩ | Pilot sources: subscriptions, APIM/AKS instances, read-only scopes and permissions requested | DEC | S | BL-001 | DEC-068, DEC-069, DEC-070 | 0 | Access requests raised (long lead for Phase 2) |

---

## Phase 1 — Explore + Studio foundation (6–10 weeks; tech §18 Phase 1, sprints A–D)

Exit gate: developer finds owner and dependency; architect creates a 6-node Azure design and saves/reloads it; permission negative tests pass; all primary controls functional in real browser (tech §18, BRD E19 Release 1).

| Rank | ID | Item | Sprint | Repo | Depends on | Key requirements | Reqs | Decisions |
|---:|---|---|---|---|---|---|---:|---|
| 1 | BL-103 | API shell: error envelope, correlation IDs, cursor pagination, OpenAPI-conformance CI against `specs.lock` | A | B | BL-014, BL-021 | INV-07 | 1/1 | DEC-039 |
| 2 | BL-101 | Canonical graph schema, taxonomy validation, aliases, provenance, migrations (TE01) | A | B | BL-002, BL-007 | INV-01–06, MOD-01, MOD-03/04, DEP-01, UX-NFR-014 | 11/11 | DEC-050, DEC-037, DEC-058 |
| 3 | BL-104 | Entra auth, policy engine (RBAC+ABAC), field redaction, negative tests (TE08) | A→D | B (+F guards) | BL-004, BL-008 | GOV-01, SEC-05, SELF-04, UX-GLB-003, UX-NFR-009 | 7/13 | DEC-051, DEC-073, DEC-027 |
| 4 | BL-102 | Synthetic graph generator + golden fixture loader | A | B | BL-016 | (enabler for E2E/perf) | 0 | DEC-054 |
| 5 | BL-105 | Bright app shell, navigation, inspector frame, routes, home dashboard | A | F | BL-024, BL-021 | CMD-05, UX-GLB-012 | 2/2 | DEC-041, DEC-065 |
| 6 | BL-106 | Azure icon registry + labelled neutral fallback | A | F | BL-020 | CAN-01 | 1/1 | DEC-061 |
| 7 | BL-107 | Generated typed API client, auth transport, error handling, contract mocks for dev | A | F | BL-014 | (enabler) | 0 | DEC-042 |
| 8 | BL-118 | Append-only audit event store | A | B | BL-101 | GOV-04 | 1/2 | DEC-074 |
| 9 | BL-108 | Scoped projection API: budgets, grouping, bundles, access-aware counts, projection token, C4-style levels (TE02) | B | B | BL-101, BL-104 | MOD-02, MOD-06, CAN-08, UX-CAN-020, UX-MOD-01, J-MOD-01 | 10/14 | DEC-060, DEC-035 |
| 10 | BL-109 | Landscape canvas: select, pan/zoom, fit, minimap, bundles, trust indicators, context menu, relationship inspector (TE02) | B | F | BL-108, BL-018, BL-106 | CAN-02/04/07, UX-CAN-001–006/008/009/023/024, E01 | 18/22 | DEC-023, DEC-056 |
| 11 | BL-110 | Passport API + page: owner, purpose, provenance, environment switch, links, completeness (TE03) | B | B+F | BL-101, BL-003 | PASS-01–05/07, UX-PASS-*, DEV-03/05, KNOW-01, SELF-01, J01 | 26/26 | DEC-062, DEC-056 |
| 12 | BL-111 | Search API (FTS/trigram/aliases, ACL before ranking) + Cmd/Ctrl+K palette (TE06) | B | B+F | BL-101, BL-104 | DEV-01/02/07, CMD-01/03/04, UX-GLB-001/002, US-01 | 15/16 | DEC-029 |
| 13 | BL-112 | Deep links and URL view-state contract; share links re-check authorization | B | F (+B) | BL-015 | DEV-04, PASS-08, UX-GLB-008, UX-PASS-001 | 4/8 | DEC-067 |
| 14 | BL-113 | X-Ray: in-place expand/collapse, abstraction levels, breadcrumbs, large-child grouping (TE04) | C | B+F | BL-108, BL-109 | XRAY-01–04/06/07, UX-XR-*, US-02, E05 | 16/20 | DEC-060 |
| 15 | BL-114 | Personal/curated views; layout save/reload with `If-Match`; layout reconciliation on graph change | C | B+F | BL-108, BL-109 | CAN-06, MOD-05, XRAY-05, UX-CAN-010, CMD-02, US-03 | 10/14 | DEC-059, DEC-067 |
| 16 | BL-115 | Accessible node list and keyboard parity for canvas tasks | C | F | BL-109 | CAN-10, XRAY-06, UX-CAN-019, UX-GLB-007, UX-NFR-008 | 6/6 | DEC-055 |
| 17 | BL-121 | Shared state library: loading / empty / stale / denied / error / partial / conflict states; toasts | C | F | BL-105 | UX-GLB-004/006, UX §4.4 | 2/3 | – |
| 18 | BL-116 | Draft branch from pinned baseline; typed draft commands; undo/redo; save states; 412 conflict UI (TE05) | D | B+F | BL-114, BL-006 | BRN-01, GOV-07, UX-CAN-011/016/017, UX-NFR-006 | 9/12 | DEC-031, DEC-063 |
| 19 | BL-117 | Edit mode: Azure palette, typed ports, connection validation, ELK orthogonal routing, waypoints, align/distribute (TE05) | D | F (+B validation) | BL-116 | CAN-03/05/11, UX-CAN-012–015 | 7/8 | DEC-023 |
| 20 | BL-119 | Feedback / correction / ownership-claim workflow with review and audit (TE07) | D | B+F | BL-118, BL-104 | PASS-06, FBK-01–04, DEV-06, UX-GLB-011, J-FBK-01 | 14/14 | DEC-063 |
| 21 | BL-123 | Business capability map sample (Claims Settlement) | D | B+F | BL-108 | BCM-01/02, J-BCM-01 (sample scope) | 4/4 | DEC-052 |
| 22 | BL-120 | Export SVG/PNG/PDF with legend, snapshot, classification marker; audited | D | F+B | BL-109, BL-104 | CAN-09, UX-CAN-018, UX-NFR-007 | 3/4 | DEC-064 |
| 23 | BL-124 | Staged manual/CSV inventory import (preview → steward commit) | D | B+F | BL-101, BL-203 schema | CON-08 (CSV part), BRD E19 R1 | 1/1 | DEC-050 |
| 24 | BL-122 | Playwright E2E (Chromium + 1), visual regression 1440×900 / 1280×720, a11y gates in CI (TE09) | A→D | F | BL-021 | EXP-02, US-08, UX-NFR-011/012, E18 | 7/14 | DEC-055 |
| 25 | BL-125 | Performance harness (k6/Locust + browser profiling) against 10k fixture | C→D | B+F | BL-102 | UX-NFR-001–005, NFR-01/02/05 | 2/8 | DEC-054 |
| 26 | BL-126 | Atlas self-diagnostics: structured logs, authenticated build-provenance endpoint (`frontend_sha`, `backend_sha`, `specs_sha`, migration rev) | A | B+F | BL-103 | NFR-06, NFR-12, tech §17.4(7) | 2/2 | DEC-003, DEC-076 |

---

## Phase 2 — Trustworthy discovery (6–10 weeks)

Exit gate: idempotent re-sync, no duplicate canonical entities in golden fixtures, stale-source warnings, field-level evidence (tech §18). **Do not start BL-204+ until the reconciliation semantics (BL-006/BL-007) are approved.**

| Rank | ID | Item | Repo | Depends on | Key requirements | Reqs | Decisions |
|---:|---|---|---|---|---|---|---|
| 1 | BL-201 | Durable job framework, retries, idempotency keys, outbox | B | BL-103 | CON-06 | 1/1 | DEC-028 |
| 2 | BL-202 | Source observation store + raw artifacts in Blob with checksums | B | BL-201 | REC-04/05, INV-03/06 (observation side) | 2/5 | DEC-057 |
| 3 | BL-203 | Deterministic reconciliation engine + steward inbox, reversible merge/split | B+F | BL-202 | REC-01–03/07, INV-04, UX-REC-01, J-REC-01, E03 | 7/9 | DEC-025, DEC-034, DEC-057 |
| 4 | BL-210 | Connector SDK baseline: observation/relationship contracts, conformance suite, dry-run | B (+S contract) | BL-202 | SDK-01–04/06, CON-10, UX-SDK-01 | 7/8 | DEC-072 |
| 5 | BL-204 | Azure Resource Graph connector | B | BL-210, BL-023 | CON-01, J06, E04 | 3/3 | DEC-069, DEC-070 |
| 6 | BL-205 | APIM management connector (secrets redacted) | B | BL-210 | CON-02 | 1/1 | DEC-069 |
| 7 | BL-206 | AKS read-only connector | B | BL-210 | CON-03 | 1/1 | DEC-069 |
| 8 | BL-207 | Messaging configuration discovery (Service Bus / Event Hubs) via ARM | B | BL-204 | CON-05, US-04, J03 | 3/3 | DEC-079 |
| 9 | BL-208 | Source coverage, freshness and backlog dashboard | B+F | BL-203 | CON-07, REC-06, GOV-03, UX-NFR-010 | 4/6 | DEC-072 |
| 10 | BL-209 | Contract Registry baseline: OpenAPI/AsyncAPI import, quarantine, versions, deterministic diff, field redaction | B+F | BL-202 | ICR-01–09, UX-ICR-*, DEP-02, E07 | 17/19 | DEC-071, DEC-073 |
| 11 | BL-211 | Bounded traversal, impact paths, snapshot compare | B+F | BL-108 | DEP-03/06/07, HIST-01/02, GOV-05, UX-CAN-022, J02 | 9/11 | DEC-031 |
| 12 | BL-212 | Approved source-control metadata ingestion (default branch, allow-listed files, no PR data) | B | BL-210 | CON-04 | 1/1 | DEC-078 |

---

## Phase 3 — Design productivity (6–10 weeks)

Exit gate: sandbox → validation → review → promotion without cloud mutation; import never marks lines verified.

| Rank | ID | Item | Repo | Depends on | Key requirements | Reqs | Decisions |
|---:|---|---|---|---|---|---|---|
| 1 | BL-303 | Branch diff (topology vs layout), three-way merge, promotion with rule gate, discard/archive | B+F | BL-116 | BRN-02–06, SAN-05, GOV-02, UX-BRN-01, US-05, J04 | 9/13 | DEC-031, DEC-063 |
| 2 | BL-305 | Rule engine baseline: allowlisted rules, 5 statuses, test harness, exceptions with expiry, reports | B+F | BL-211 | RULE-01–10, UX-RULE-*, DEP-09, PAT-06, E09 | 20/21 | DEC-036, DEC-063 |
| 3 | BL-304 | Pattern library + sandbox instantiation and parameter validation | B+F | BL-303, BL-305 | PAT-*, SAN-01–04, UX-PAT-*, E08 | 17/17 | DEC-036 |
| 4 | BL-301 | Architecture-as-code YAML/JSON schema, dry-run diff, deterministic export | S+B+F | BL-015, BL-303 | AAC-01–06, UX-AAC-01, J-AAC-01 | 8/8 | DEC-050 |
| 5 | BL-302 | draw.io import (Visio interchange later): staged preview, icon/shape mapping, no verified edges | B+F | BL-301 | IMP-01–06, CON-08, UX-IMP-01, J-IMP-01 | 8/9 | DEC-032 |
| 6 | BL-306 | ADR / document linking, decision status, permission-aware previews | B+F | BL-110 | ADR-01–05, GOV-06, KNOW-03, UX-ADR-01 | 7/9 | DEC-082 |
| 7 | BL-307 | Storytelling scenes, presentation mode, design-time playback | F+B | BL-114 | STORY-*, FLOW-*, CAN-12, UX-CAN-021, J-STORY-01 | 14/14 | DEC-064 |
| 8 | BL-308 | Threaded comments and review assignments on entities/revisions | B+F | BL-303 | COL-01/02/05, EXP-04, UX-COL-01 | 5/6 | DEC-077 |

## Phase 4 — Intelligence and data context (8–12 weeks)

| Rank | ID | Item | Repo | Depends on | Key requirements | Reqs | Decisions |
|---:|---|---|---|---|---|---|---|
| 1 | BL-407 | Scale hardening and 100k-entity benchmark (Scale A) | B+F | BL-125 | NFR-01 | 0/1 | DEC-022, DEC-054 |
| 2 | BL-401 | Documented system/dataset lineage | B+F | BL-211 | LIN-*, DEP-05, UX-LIN-01, J-LIN-01 | 10/10 | DEC-073 |
| 3 | BL-403 | Drift and time machine | B+F | BL-211, BL-303 | HIST-03–06, E10 | 4/5 | DEC-057, DEC-059 |
| 4 | BL-406 | Security / data-flow lens | B+F | BL-305 | SEC-01–04, DEP-08, US-06, J05 | 8/8 | DEC-073 |
| 5 | BL-402 | Advanced capability maps (heatmaps, curated approval, gaps/redundancy) | B+F | BL-123 | BCM-03–06 | 4/6 | DEC-050 |
| 6 | BL-405 | Quality scorecards (completeness vs conformance) | B+F | BL-305 | SCORE-*, FBK-05 | 6/6 | DEC-036 |
| 7 | BL-404 | Grounded AI assistant with citations, guarded actions, golden-set evaluation | B+F | BL-111, BL-211, BL-306 | AI-*, AIX-*, UX-XR-010, US-10, E11 | 16/16 | DEC-033, DEC-075, DEC-076 |
| 8 | BL-507 | Guided onboarding journeys and new-joiner orientation | F+B | BL-110, BL-307 | KNOW-02/05, DEV-08 | 3/3 | – |

## Phase 5 — Enterprise collaboration and expansion (BRD §12 Phase 5)

| Rank | ID | Item | Key requirements | Reqs | Decisions |
|---:|---|---|---|---:|---|
| 1 | BL-501 | Subscriptions and change notices (approved changes only) | NTF-*, UX-NTF-01 | 6/6 | – |
| 2 | BL-505 | CMDB / ITSM / directory / data-catalog connectors | CON-09 | 1/1 | DEC-079 |
| 3 | BL-503 | Governed self-service requests and links | SELF-02/03 | 1/2 | DEC-051 |
| 4 | BL-506 | Extension framework (connectors, entity types, widgets), connector package sandbox | EXP-03, SDK-05 | 2/2 | – |
| 5 | BL-502 | Cost showback (**needs tech design addendum first**) | COST-*, CON-09 (billing), E12 | 5/7 | DEC-080 |
| 6 | BL-504 | Real-time presence / co-editing (only if justified) | COL-03/04 | 2/2 | DEC-077 |

---

## Critical path (summary)

`BL-001 → BL-002 → BL-003/BL-004/BL-006/BL-007 → BL-013 → BL-015 → BL-014 → BL-021 → BL-103/BL-101/BL-104 → BL-108 → BL-109/BL-110/BL-111 → BL-113/BL-114 → BL-116/BL-117`

Long-lead items started in Phase 0: BL-020 (icon licence), BL-023 (source permissions).
