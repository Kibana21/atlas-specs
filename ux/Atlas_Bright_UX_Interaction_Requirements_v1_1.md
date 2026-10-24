# ATLAS — Bright Application UX & Interaction Requirements

**Companion to Atlas Enterprise Architecture BRD V2.0**  
**Version:** UX 1.1 · **Date:** 24 October 2026 · **Status:** Proposed for design and stakeholder validation  
**Audience:** Enterprise architects, solution architects, developers, platform engineers, security, operations, product, design and QA.

> **Product mandate:** Atlas must feel like a world-class, bright, joyful and highly capable engineering workspace—not a CMDB form, a static Visio export, or a tangled network graph. Every interaction must make complex architecture easier to understand and act upon.

**Authority:** This document specifies experience and interaction behavior for the V2.0 BRD; it does not replace its graph, security, connector, or governance requirements. Where a conflict arises, the stricter evidence/security requirement applies and the discrepancy must be resolved before implementation. All performance thresholds and design tokens are **proposed acceptance baselines**, not approved commitments.

## 1. North-star experience

A user lands on a crisp, bright Atlas workspace with a useful enterprise overview, not a blank canvas. Within 30–60 seconds, they can search for a system, inspect its Passport, expand its internal architecture, follow a documented dependency, and share the exact view with a colleague. An architect can open a governed draft, drag an approved Azure component onto a canvas, route a connection, save the diagram, compare with a baseline, and present it without switching tools.

**Personality:** Confident, clear, vibrant, precise, fast, trustworthy, welcoming. **Never:** dark-by-default, neon-on-neon, visually noisy, dense walls of metadata, mysterious controls, or decorative UI that cannot be clicked.

### 1.1 Success promises by audience

| Persona | Must be able to do | Experience standard |
|---|---|---|
| Enterprise architect | Navigate enterprise-to-cloud hierarchy; create and compare designs; apply approved patterns; review rule findings | Presentation-quality canvas, precise layout, deterministic editing |
| Solution architect | Build future-state options, inspect integration contracts, validate rules, explain trade-offs | Smooth draft-to-review workflow and readable dependency paths |
| Application developer | Find a service, its owner, API, repo, environment and dependencies | Search-first; useful answers with no diagramming knowledge required |
| Cloud/platform engineer | Explore subscriptions, resource groups, AKS, APIM, databases and resource provenance | Accurate Azure iconography and hierarchy; freshness shown |
| Security reviewer | Inspect trust boundaries, classified flows and policy findings | Evidence-based findings, explicit unknowns, no unsupported certainty |
| Support/operations | Locate owner, environment, upstream/downstream dependencies and runbooks | Clear static architecture context; **no runtime telemetry UI** |
| Engineering leader/product owner | Understand business capabilities, critical dependencies, completeness and change history | Readable summaries without losing access to technical detail |
| New joiner | Follow a guided architecture tour and learn key components | Accessible, guided, friendly and forgiving experience |

### 1.2 Non-negotiable experience principles

1. **Progressive disclosure:** Show the right 10–30 things first, not 1,000 tiny labels. Large graphs require clustering, bundling and drill-down.
2. **One model, many lenses:** Canvas, X-Ray, Passport, Contracts, Patterns and Rules are views over shared canonical IDs.
3. **Bright but legible:** White and very light neutral surfaces; vivid colors for entity identity and meaning; text contrast remains accessible.
4. **Visible provenance:** Discovered, documented, proposed, inferred and stale are never silently conflated.
5. **Every visible control works:** No dead buttons, placeholder context menus, fake filters or nonfunctional minimaps.
6. **Preserve context:** Selection, viewport, breadcrumb, filters and user intent survive navigation wherever possible.
7. **Safe by default:** Read-only exploration; editing requires explicit draft/edit state and role permissions.
8. **Elegant density:** The diagram gets most of the screen; detail is available in resizable panels, not permanent clutter.
9. **Predictable undo:** Draft edits support undo/redo; published facts follow approval and audit controls.
10. **Delight without gimmicks:** Subtle animation confirms meaning; reduced-motion users get an equivalent nonanimated experience.

## 2. Visual design system — bright and brilliant

### 2.1 Design direction

- **Default theme:** Bright/light. Dark mode may be a later optional theme; the flagship experience is light.
- **Canvas:** Warm white or faint blue-gray (#F8FAFE), optional extremely subtle dot/grid; no heavy gradients behind technical drawings.
- **Primary action:** Azure-inspired blue (#1769E0), with a darker accessible hover/focus state.
- **Semantic entity colors (proposed):** Application indigo (#5A54D6), API blue (#1674E8), Compute violet (#8C58D8), Messaging amber (#C47B13), Data teal (#087F8C), Security rose (#BD4D76), Business domain green (#22865E). Validate actual text/icon contrast before adoption.
- **Containers:** Pale category tint with 1–2px defined border; distinct from child nodes.
- **Lines:** Neutral slate for normal dependencies; selective category accents; no rainbow edge clutter. Selection uses blue emphasis.
- **Typography:** Highly readable sans serif; consistent weights; labels never reduced below an agreed accessible minimum in normal reading mode.
- **Shape language:** Rounded rectangles for applications/services, subtle service-specific icon tiles, well-defined grouped boundaries; connectors attach at clear ports.
- **Icons:** Official Azure SVG assets with correct licensing/usage, versioned asset registry and fallbacks; never approximate official services with random emojis in production diagrams.
- **Motion:** 120–220ms transitions for hover, selection and panel changes; expansion transitions should remain understandable and respect reduced motion.
- **Empty states:** Helpful illustrations or simple diagrams with meaningful next actions, never a giant empty gray workspace.

### 2.2 Density and color rules

| Situation | Requirement |
|---|---|
| Enterprise overview | Business domains and major systems visible; fine-grained resources summarized |
| Application view | APIs, services, messaging and data stores visible with selectively bundled connections |
| Azure infrastructure | Explicit nested Azure hierarchy; resource icons legible |
| 100+ visible edges | Bundle by source/target or relation type; reveal exact paths on selection |
| Stale or inferred facts | Use status chip, icon or pattern as well as color; color alone is insufficient |
| Selection | Clear 2px+ highlight and inspector focus; unrelated elements dim gently, not disappear unexpectedly |
| High contrast mode | Meaning preserved without relying on tint; keyboard focus ring remains obvious |
| Export | Crisp SVG/PDF/PNG; labels and icons retain sufficient readability at selected page size |

### 2.3 Layout shell and responsive behavior

**Desktop first** at 1440×900 reference viewport; usable at 1280×720; read-only exploration supported on tablets; editing on very small screens may be limited with explicit messaging.

```text
┌───────────────────────────────────────────────────────────────────────────────────────┐
│ ATLAS  [Search systems, APIs, resources...]      Workspace ▾  Help  +Create  Profile │
├─────────────┬──────────────────────────────────────────────────────────┬──────────────┤
│ NAVIGATION  │ [Breadcrumbs] [Lens] [Environment] [Time] [Share]       │ INSPECTOR    │
│             ├──────────────────────────────────────────────────────────┤              │
│ Enterprise  │                                                          │ Overview     │
│ Applications│                BRIGHT ARCHITECTURE CANVAS                │ Dependencies │
│ APIs        │                                                          │ Evidence     │
│ Patterns    │  [Nested Azure domains / clear icons / routed edges]    │ Ownership    │
│ Rules       │                                                          │ Actions      │
│ Saved views │                                                          │              │
│             │                         [Zoom] [Fit] [Mini-map]          │              │
├─────────────┴──────────────────────────────────────────────────────────┴──────────────┤
│ Status: Production · 138 visible / 4,850 total · 3 stale sources · Last sync 08:15     │
└───────────────────────────────────────────────────────────────────────────────────────┘
```

The side navigation is collapsible; the inspector opens on selection and can be resized or hidden. Canvas viewport must not jump when a panel opens unless user explicitly chooses “fit.”

## 3. Global information architecture

| Route / workspace | Primary purpose | Default mode |
|---|---|---|
| `/` | Home: recent, favorites, popular domains, source freshness, quick search | Explore |
| `/landscape/:viewId` | Enterprise architecture canvas with lens and filters | Read-only |
| `/applications/:id` | Architecture Passport and contextual X-Ray entry | Read-only |
| `/contracts` and `/contracts/:id` | Search, inspect and compare integration contracts | Read-only |
| `/patterns` and `/patterns/:id` | Discover approved patterns and instantiate draft | Read-only / draft |
| `/rules` and `/evaluations/:id` | Inspect rules and evidence-backed evaluations | Read-only |
| `/sandbox/:id` | Proposed future-state architecture and design alternatives | Edit by permission |
| `/history/:viewId` | Version comparison and snapshot navigation | Read-only |
| `/search` | Unified search across authorized architecture objects | Read-only |
| `/admin` | Sources, identities, rules, ownership and configuration | Restricted |

**Universal interactions:** Search keyboard shortcut; breadcrumbs; stable deep links; copy link to selection and viewport; clear filter reset; help on unfamiliar graph concepts; predictable Back behavior.

## 4. Screen A — Enterprise Landscape (flagship experience)

### 4.1 Default composition and visual hierarchy

- Open to a curated, legible enterprise landscape, grouped by business domain; user can change to technology, owner, environment or capability lenses.
- A **domain card** displays name, system count, health of documentation (not runtime health), and a few representative app icons.
- A **system node** displays official or curated icon, human-readable name, environment indicator when relevant, and owner indicator on selection.
- **Nested boundaries** are visually distinct: business domain → application → Azure subscription/resource group → cluster/namespace → resources, only at appropriate abstraction levels.
- Connections have arrows, relationship type, clear source/target ports and optional protocol; avoid crossing through node bodies.
- Toolbar: lens, environment, domain filters, search-in-view, zoom/fit, expand/collapse, export, share, edit (authorized), version.
- Minimap and keyboard shortcuts are discoverable but unobtrusive.
- The right inspector shows selection detail; no selection means optional legend, tips and current view metadata.

### 4.2 Canvas interaction requirements

| ID | Priority | User action / system behavior | Acceptance criteria |
|---|---|---|---|
| UX-CAN-001 | Must | Single-click node selects and opens inspector. | Selected entity is visibly emphasized; inspector shows correct canonical ID, type, evidence and owner. |
| UX-CAN-002 | Must | Double-click application enters X-Ray or opens a clear drill-down affordance. | No accidental edit or pan; breadcrumb records previous context. |
| UX-CAN-003 | Must | Hover reveals contextual affordances without hiding key labels. | Tooltip identifies entity and relationship; tooltip never blocks subsequent click. |
| UX-CAN-004 | Must | Drag empty canvas to pan; scroll/pinch to zoom around pointer. | Pan/zoom is smooth; user can fit selected or fit all; no unintended node movement in Explore mode. |
| UX-CAN-005 | Must | Search and highlight matching nodes; optionally center selected result. | Search never silently discards active filters; hidden matches are identified. |
| UX-CAN-006 | Must | Toggle lens and environment with clear data boundaries. | Production/UAT links never merge ambiguously; filters appear as visible chips. |
| UX-CAN-007 | Must | Expand group, collapse group, and expand one level only. | Collapsed group displays summary counts; expansion retains current viewport anchor. |
| UX-CAN-008 | Must | Select a connector to see direction, protocol, evidence, confidence and linked contract. | Edge selection is possible even in dense graph; inspector shows exact relationship. |
| UX-CAN-009 | Must | Group edges and reveal exact members on request. | Bundles show truthful counts and types; no relationship is silently dropped. |
| UX-CAN-010 | Must | Save a personal view of filters, lens, viewport, expanded groups and visible labels. | Reloading restores view state without changing canonical graph. |
| UX-CAN-011 | Must | Edit mode is explicitly entered with appropriate permissions. | Explore mode never modifies entities or layout; edit toolbar and save status are visible. |
| UX-CAN-012 | Must | In edit mode, add node from searchable Azure/component palette. | New object is proposed until approved; icon, parent boundary and required fields are validated. |
| UX-CAN-013 | Must | Create directed edge by connecting visible ports; choose relationship type. | Invalid connection is rejected with reason; successful edge appears and is undoable. |
| UX-CAN-014 | Must | Drag, align, distribute and resize editable nodes/containers. | Snapping and guides aid placement; save/reload preserves positions. |
| UX-CAN-015 | Must | Support orthogonal routing and manual waypoints in edit mode. | Route avoids node bodies where feasible; user can reset to auto-route. |
| UX-CAN-016 | Must | Undo/redo reversible draft edits with keyboard shortcuts. | Repeated undo/redo restores same draft state; publish/approval events are not silently undone. |
| UX-CAN-017 | Must | Show dirty, saving, saved, conflict and failed-save states. | Network failure retains local draft until retry/export; no false “Saved” status. |
| UX-CAN-018 | Must | Export visible view to PNG/SVG/PDF and architecture metadata when permitted. | Export includes legend, version, date and appropriate confidentiality marker; restrictions honored. |
| UX-CAN-019 | Must | Provide accessible keyboard node list and inspector navigation. | A keyboard-only user can find, select and inspect an entity without using canvas gestures. |
| UX-CAN-020 | Must | Handle thousands of total entities via semantic zoom and progressive rendering. | At 5,000 canonical entities, default view remains comprehensible and no attempt is made to render all labels simultaneously. |
| UX-CAN-021 | Should | Support pinned labels, bookmarks, annotation callouts and curated view layouts. | Annotations persist independently from discovered topology; permissions and attribution apply. |
| UX-CAN-022 | Should | Show edge-path focus: upstream, downstream, one-hop, N-hop. | Highlighted paths are reproducible and have explicit scope, direction and evidence. |
| UX-CAN-023 | Must | Show source freshness and uncertainty on visible entities. | Stale, proposed and inferred statuses use accessible visual distinctions and explanatory inspector text. |
| UX-CAN-024 | Must | Context menu offers only permitted actions. | Every visible menu item works; forbidden operations are absent or disabled with reason. |

### 4.3 Semantic zoom contract

| Zoom / intent | Visible information | Interaction |
|---|---|---|
| L0 Enterprise | Domains, strategic platforms, major flows | Click domain to focus; counts summarize hidden nodes |
| L1 Domain | Applications and cross-domain integrations | Expand application or inspect relation |
| L2 Application | APIs, logical services, queues, databases | Open X-Ray; inspect contract or Passport |
| L3 Infrastructure | Subscription, RG, network, AKS, namespace, Azure services | Expand resource hierarchy; follow evidence |
| L4 Detail | Selected resources, ports, schemas and relationship metadata | Inspector or Passport; no uncontrolled label explosion |

**Important:** Levels are semantic, not hardcoded zoom percentages. Wheel zoom changes visual scale; deliberate focus/expand changes abstraction. Atlas must not unexpectedly reveal 2,000 nodes merely because a user scrolls.

### 4.4 Canvas failure, conflict and empty states

| Condition | Required UI response |
|---|---|
| No systems imported | Attractive sample landscape clearly labeled demo; “Connect source” or “Create manually” CTA |
| No results for filter | Explain which filters excluded results; “Clear filters” action |
| Source synchronization stale | Nonblocking warning with timestamp and affected scope; graph remains usable |
| Layout algorithm fails | Preserve prior layout; offer retry/manual arrangement and error reference |
| User lacks permission for entity | Do not reveal restricted labels or edge details; show safe aggregate only if policy allows |
| Edit conflict | Show which version changed, compare options and explicit retry/merge flow; never overwrite silently |
| Graph exceeds rendering budget | Show grouped summary with counts and “Expand selected area”; no blank canvas |
| Export too large | Offer scoped export or paginated export with truthful limits |
| Invalid edge | Explain relationship schema/permission violation and keep current draft intact |

### 4.5 End-to-end landscape acceptance

**Given** a published landscape containing 5,000 canonical entities across business domains, **when** a developer searches for “Policy Administration,” selects the result, expands the application, follows its APIM dependency and shares the view, **then** another authorized developer opens the same focused selection and sees identical evidence-backed relationships without any topology modification.

**Given** an authorized architect edits a draft, **when** they add an Azure SQL node, connect it to a service, move it inside a resource group and save, **then** the draft reloads with identical hierarchy, route, positions and edit history, while the published view is unchanged.

## 5. Screen B — Architecture X-Ray

### 5.1 Interaction model

1. Enter X-Ray from a landscape node or Passport action.
2. Atlas anchors the selected application in place and gently dims neighboring systems; **does not remove them**.
3. Show an abstraction switcher: Application / Logical services / Integrations / Azure infrastructure.
4. Expand child containers one level at a time. Each level displays count of visible/hidden children and source freshness.
5. Highlight a selected service's external dependencies; offer “show all,” “one hop” and “back to context.”
6. Selecting a child opens its Passport in the inspector or full page without losing current X-Ray state.
7. Collapse restores prior grouping, position and surrounding context.
8. User may save the X-Ray view as a personal or curated view; published topology is not changed.

| ID | Priority | Requirement | Acceptance criteria |
|---|---|---|---|
| UX-XR-001 | Must | In-place expansion and collapse. | Surrounding landscape remains visible; collapsed node returns to its original anchor. |
| UX-XR-002 | Must | Multi-level nested navigation with breadcrumbs. | User can jump to any ancestor; no orphaned or duplicate graph nodes appear. |
| UX-XR-003 | Must | Abstraction level selector. | Switching levels shows accurate graph projection with stable IDs and clear omissions. |
| UX-XR-004 | Must | Cross-boundary edge bundling. | Bundles disclose counts, relationship types and precise constituent edges. |
| UX-XR-005 | Must | Evidence and uncertainty display. | Undocumented levels show “Not documented”; inferred links never look verified. |
| UX-XR-006 | Must | Per-view expansion state persistence. | Save/reload restores selection, expansion, lens and viewport. |
| UX-XR-007 | Must | Large-child-set handling. | For 1,000 child resources, Atlas initially shows bounded groups and progressive expansion. |
| UX-XR-008 | Should | Side-by-side logical and physical mapping. | Selecting logical service highlights corresponding known deployments; unmapped resources are clearly shown. |
| UX-XR-009 | Must | Permission-aware hierarchy. | Restricted descendants do not leak through counts, tooltips, search or export where forbidden. |
| UX-XR-010 | Should | “Explain this layer” helper. | Explanation references graph entities and documents; no unsupported claims. |

### 5.2 X-Ray edge cases

- Application with no discovered internals: show a friendly empty-state explanation and “Add documentation” action.
- Mixed Azure and on-prem components: show both with distinct boundaries; do not force Azure hierarchy onto on-prem systems.
- One service deployed to multiple clusters: show multiple deployments linked to one logical service, not duplicate logical identity.
- Cyclic service dependencies: preserve both directions and allow edge inspection.
- Unmapped logical service: show a clear “deployment not mapped” state.
- Stale cluster inventory: keep last-known data with timestamp and warning.

### 5.3 X-Ray acceptance journey

**Given** a Policy Administration app with APIM, two AKS namespaces, Service Bus and Azure SQL, **when** an architect expands it to logical services, switches to Azure deployment, selects a namespace, inspects the Service Bus edge and returns to enterprise view, **then** no canvas reset, hidden dependency loss or unauthorized topology change occurs.

## 6. Screen C — Architecture Passport

### 6.1 Page structure

```text
[Icon] Policy Administration   [Production] [Verified] [Critical]
Purpose and summary                                       [Follow] [Share] [Propose edit]
Owner: Core Platforms    Technical lead: Team X           Last verified: 22 Oct
────────────────────────────────────────────────────────────────────────────────
[Overview] [Dependencies] [Interfaces] [Infrastructure] [Documents] [History]
[Architecture mini-map]     [Upstream 8] [Downstream 12] [APIs 6] [Databases 2]
[Business purpose]          [Environment] [Data class] [Lifecycle]
[Source evidence and last sync]                            [Open X-Ray]
```

### 6.2 Information contract by entity type

| Entity | Mandatory Passport information | Conditional details |
|---|---|---|
| Business application | Canonical ID, purpose, business domain, lifecycle, owner, classification, known dependencies, provenance | Repositories, deployment environments, ADRs, runbooks |
| API | Canonical ID, provider, owning application, environment, contract/version, security model, known consumers | APIM gateway, route, operations, deprecation |
| Database | Canonical ID, engine/type, environment, owning application/team, classification, access relationships | Schemas, backup design references, region |
| Queue/topic | Canonical ID, broker/service, environment, producer/consumer, owner, contract references | Retry/dead-letter design, topic/subscription |
| AKS cluster/namespace | Azure resource ID or stable identity, subscription, RG, environment, owner, provenance | Workloads, ingress, network context |
| Azure resource | Azure resource ID, service type, subscription/RG, environment, owner or ownership gap, source freshness | Network associations, cost center, dependencies |

Mandatory means **the field is displayed and its completeness tracked**, not that Atlas invents a value or blocks read access when data is missing.

### 6.3 Passport interaction requirements

| ID | Priority | Requirement | Acceptance criteria |
|---|---|---|---|
| UX-PASS-001 | Must | Stable deep link and canonical identity. | URL resolves to same authorized entity across sessions; aliases redirect safely. |
| UX-PASS-002 | Must | Clear overview with owner, purpose, lifecycle and evidence freshness above the fold. | Core context visible without switching tabs at 1440×900. |
| UX-PASS-003 | Must | Dependency mini-map with upstream/downstream tabs. | Selecting a dependency opens its Passport or relationship detail and preserves back navigation. |
| UX-PASS-004 | Must | Links to contracts, diagrams, ADRs, runbooks and repositories. | Links have type, destination and validation status; broken links can be reported. |
| UX-PASS-005 | Must | Environment switcher with explicit environment scoping. | Production and UAT resource mappings are never silently merged. |
| UX-PASS-006 | Must | Proposed correction workflow. | Nonowners can suggest a correction; authoritative change requires approved permissions and audit. |
| UX-PASS-007 | Must | Provenance per important field. | User can see where owner, contract and relationship facts came from and when verified. |
| UX-PASS-008 | Must | Explicit missing, stale and conflicting information states. | Conflicting sources show review workflow; neither is silently chosen without precedence rule. |
| UX-PASS-009 | Should | Follow/bookmark and share exact Passport section. | Saved bookmark returns to same tab; share respects permissions. |
| UX-PASS-010 | Must | Restricted metadata redaction. | Search snippets, copied links, exports and AI output do not leak unauthorized fields. |
| UX-PASS-011 | Should | Completeness checklist and stewardship action. | Owner can attest facts; expired attestations visibly revert to stale status. |
| UX-PASS-012 | Must | One-click “Explore on canvas” and “Open X-Ray.” | Navigation focuses correct entity and preserves prior context on Back. |

### 6.4 Passport acceptance journey

**Given** a new developer with read permission, **when** they search “Claims API,” open its Passport, inspect technical ownership, open the current API specification, follow the downstream Policy Administration dependency and return, **then** they can complete the task without editing rights and without encountering a blank page or dead link.

## 7. Screen D — Integration Contract Registry

| ID | Priority | Requirement | Acceptance criteria |
|---|---|---|---|
| UX-ICR-001 | Must | Unified searchable inventory of OpenAPI, AsyncAPI and approved documented interfaces. | Search by API path, operation, event, schema, provider and consumer. |
| UX-ICR-002 | Must | Contract detail with version, owner, status, endpoints/topics and source. | Source revision and effective status visible above the fold. |
| UX-ICR-003 | Must | Producer/consumer map with Passport deep links. | Each edge reflects documented relation and source; no observed-traffic claims. |
| UX-ICR-004 | Must | Side-by-side version comparison. | Added/removed/changed fields and operations are highlighted; potential breaking changes explained. |
| UX-ICR-005 | Must | Access-aware schema display. | Sensitive fields masked or omitted per policy in UI and export. |
| UX-ICR-006 | Should | Deprecation notice and owner subscription. | Authorized owner can publish notice; documented consumers can be listed. |
| UX-ICR-007 | Must | Conflicting imported contract resolution. | Both versions/sources remain inspectable until governed resolution. |

**Interaction:** Search `POST /policies` → select v2 → inspect owning application → compare v1/v2 → highlight documented consumers → open relevant landscape edge.

## 8. Screen E — Pattern Library and sandbox

| ID | Priority | Requirement | Acceptance criteria |
|---|---|---|---|
| UX-PAT-001 | Must | Bright, visual pattern gallery with categories and approved badges. | Cards show purpose, components, owner, version and applicability; filters work. |
| UX-PAT-002 | Must | Pattern detail with preview diagram, constraints, trade-offs and references. | Diagram and documentation correspond to same approved version. |
| UX-PAT-003 | Must | “Use in sandbox” wizard-free parameter panel. | User configures required parameters in a single focused workspace and previews output. |
| UX-PAT-004 | Must | Draft isolation and versioned pattern lineage. | Creating an instance does not modify production inventory or existing approved designs. |
| UX-PAT-005 | Should | Rule evaluation before review submission. | Findings link to rule IDs and proposed entities; UNKNOWN is distinguished from FAIL. |
| UX-PAT-006 | Must | Approval/deprecation clarity. | Deprecated patterns show warning; only approved patterns recommended by default. |

**Pattern examples:** Private APIM-to-AKS API, Service Bus asynchronous integration, Azure SQL private endpoint, cross-domain API integration, secure file exchange.

## 9. Screen F — Architecture Rule Engine

| ID | Priority | Requirement | Acceptance criteria |
|---|---|---|---|
| UX-RULE-001 | Must | Rule catalog with category, owner, severity, version and applicability. | Search/filter works; draft rules not presented as approved. |
| UX-RULE-002 | Must | Evaluation report with PASS, FAIL, UNKNOWN, N/A, EXEMPT. | Every status includes reasoning, relevant entities and evidence. |
| UX-RULE-003 | Must | Click finding to focus exact node/edge on canvas. | Canvas highlights same canonical ID; inspector shows rule and source. |
| UX-RULE-004 | Must | Exception request and approval flow. | Justification, scope, approver, expiry and audit required; expired exception stops applying. |
| UX-RULE-005 | Must | Deterministic evaluation and safe testing. | Same snapshot/rule/config yields same result; synthetic test fixtures required before publish. |
| UX-RULE-006 | Should | Report export and saved filters. | Exports match authorized visible results and preserve evidence references. |

**Rule results must never masquerade as live security scans.** A documented/configuration-based assessment must disclose its coverage and limitations.

## 10. Cross-screen interaction and content requirements

| ID | Priority | Requirement | Acceptance criteria |
|---|---|---|---|
| UX-GLB-001 | Must | Global search supports aliases, synonyms and fuzzy matches. | Searching application, API or Azure resource returns type-labeled authorized results. |
| UX-GLB-002 | Must | Search result opens exact entity or relevant graph view. | Breadcrumb and Back restore prior query and filters. |
| UX-GLB-003 | Must | Role-aware actions and navigation. | Unauthorized operations are not offered; denied direct URLs remain secure. |
| UX-GLB-004 | Must | Contextual onboarding and empty states. | First-time user sees useful starter actions; no dead “coming soon” controls in production. |
| UX-GLB-005 | Must | Consistent save, draft, review and publish language. | Published and proposed architecture never appear visually identical without status. |
| UX-GLB-006 | Must | Toasts and errors identify action, outcome and recovery. | No silent failures; retry does not duplicate objects. |
| UX-GLB-007 | Must | Accessibility: keyboard, focus, labels, contrast, reduced motion. | WCAG 2.2 AA targeted for standard UI; documented alternatives for complex canvas gestures. |
| UX-GLB-008 | Must | Share links preserve entity, view, lens, filters and focus where authorized. | Reopening link reconstructs intended state; unauthorized users see no restricted content. |
| UX-GLB-009 | Should | User preferences for density, label size and panel width. | Preferences persist and do not modify shared layouts. |
| UX-GLB-010 | Must | Trust indicators show source, sync time, verified status and scope. | User can distinguish known, unknown, inferred, stale and proposed facts. |
| UX-GLB-011 | Must | Global feedback entry for incorrect architecture data. | Feedback creates traceable correction request and does not directly mutate source data. |
| UX-GLB-012 | Must | No PR or telemetry affordances. | Navigation, connectors, demo copy and exports contain no PR analysis, live traces or runtime monitoring promises. |

## 11. Scale, speed and quality gates (proposed targets)

| ID | Quality gate | Proposed acceptance |
|---|---|---|
| UX-NFR-001 | Search responsiveness | p95 indexed query response ≤ 1.5 s in pilot dataset, excluding cold startup |
| UX-NFR-002 | Passport navigation | p95 interactive page ≤ 2.5 s on agreed corporate laptop/network profile |
| UX-NFR-003 | Canvas initial view | p95 interactive curated view ≤ 3 s with default bounded visible objects |
| UX-NFR-004 | Large enterprise graph | 10,000+ total entities indexed; default rendering uses semantic grouping rather than displaying all at once |
| UX-NFR-005 | Canvas interaction | Pan/zoom aims for perceptually smooth interaction on reference hardware; profile with agreed browser/hardware benchmark |
| UX-NFR-006 | Data integrity | Save/reload retains layout, hierarchy, route waypoints and draft revision without silent loss |
| UX-NFR-007 | Export quality | SVG and PDF vector output where supported; PNG crisp at selected output scale; official icons remain recognizable |
| UX-NFR-008 | Accessibility | WCAG 2.2 AA for application chrome and equivalent keyboard access for essential graph exploration |
| UX-NFR-009 | Security | No unauthorized entity/field disclosure through UI, search, URL, exports, snapshots or AI |
| UX-NFR-010 | Reliability | Connector failure does not block exploration of last-known published graph; freshness warning shown |
| UX-NFR-011 | Browser E2E | All flagship flows tested in real Chromium and one additional supported browser |
| UX-NFR-012 | Visual regression | Golden screenshots at 1440×900 and 1280×720 for core screens; meaningful review of changes |
| UX-NFR-013 | Pilot usability | 5+ representatives per key persona group in moderated testing; track task completion, time and satisfaction |
| UX-NFR-014 | Data trust | Every imported fact carries source and timestamp; conflicts visible; no fabricated default ownership |

**Pilot usability tasks:** Find owner in ≤60 s; navigate from API to downstream database in ≤90 s; create and save a simple 6-node draft in ≤5 min after brief orientation; identify whether an edge is documented or inferred in ≤15 s. These are proposed design targets to validate, not guaranteed outcomes.

## 12. Responsive states and microinteractions

- **Navigation:** collapsible 240px left rail; inspector initially ~320px and resizable; on smaller desktops inspector overlays canvas rather than crushing it.
- **Selection:** quick emphasis, smooth inspector transition; no forced canvas recentering on each selection.
- **Hover:** clear ports and actions; do not flood the canvas with tooltips.
- **Expand/collapse:** preserve spatial anchor; if large, show skeleton groups and progressive counts.
- **Connection drawing:** ghost orthogonal route follows pointer; invalid target displays explicit reason.
- **Saving:** unobtrusive “Saving…” → “Saved” with revision; failure offers retry and copy/export draft.
- **Search:** instant local suggestions where possible; source and entity-type chips; keyboard Enter to open, Escape to close.
- **Keyboard:** `/` or Cmd/Ctrl+K for search, Escape clear selection, F fit, `+`/`-` zoom, arrow keys through accessible node list, Cmd/Ctrl+Z undo in edit mode.
- **Accessibility:** never rely on animation, color or hover alone to convey critical meaning.

## 13. End-to-end prototype validation matrix

| Scenario | Steps | Pass conditions |
|---|---|---|
| Architect creates diagram | Open landscape → Create draft → add Azure icons → nest resources → connect → route → save → reload | Fully interactive; all persisted; clear draft status |
| Developer investigates system | Search app → Passport → X-Ray → dependency → Contract → Back | No loss of context; correct identities and evidence |
| Large enterprise landscape | Load 10k total entities → filter domain → expand app → inspect dense edges | Bounded rendering; no blank screen; no misleading missing edges |
| Security review | Filter confidential flows → inspect rule finding → highlight entity → request exception | Evidence and status correct; authorization enforced |
| Pattern reuse | Open approved pattern → configure → instantiate sandbox → validate → review | No production mutation; lineage recorded |
| Source conflict | Two connectors disagree on ownership → Passport shows conflict → propose resolution | Both sources retained; review required |
| No access | Open restricted deep link → attempt search/export | No leakage through UI, URL, count, metadata or file |
| Offline / save failure | Edit draft → disconnect → save → reconnect | Clear unsaved state; no false success; recovery path |
| Export | Filter and select domain → export SVG/PDF/PNG | Export matches intended view, legends, restrictions and revision |
| Keyboard-only | Search → open Passport → inspect dependency → return | Essential journey fully accessible |

## 14. Release sequence — prioritize loveability

| Release | User-facing experience | Exit criterion |
|---|---|---|
| R0 Design system + interactive prototype | Bright shell, Azure icon palette, realistic seeded landscape, selection, pan/zoom, X-Ray, Passport navigation | 100% visible primary controls functional in browser prototype; stakeholder walkthrough |
| R1 Discover and understand | Search, canonical inventory, Passport, X-Ray, read-only enterprise map, evidence | Developers complete core lookup journeys; no invented graph facts |
| R2 Create and explain | Draft editing, orthogonal routing, saved views, export, presentation-ready layouts, patterns baseline | Architects build and save a real reference diagram end to end |
| R3 Govern and trust | Contract registry, rule engine, approvals, audit, architecture history, drift | Deterministic evidence-backed reviews and exception handling |
| R4 Intelligent architecture | AI-grounded navigation/design assistance, expanded lenses, advanced sandbox and costs | AI output cites actual sources; safe review and permissions enforced |

**No release passes solely because a static screenshot looks attractive.** Demonstrate every major interaction in a real browser with persistent state.

## 15. Open product decisions requiring validation

| ID | Decision | Proposed starting position |
|---|---|---|
| UX-OD-01 | Primary diagram rendering engine and graph-layout engine | Benchmark candidates on nested groups, orthogonal routing, editability and 10k-entity graph projections |
| UX-OD-02 | Official Azure icon asset update cadence | Pin versioned assets and provide reviewed updates |
| UX-OD-03 | Published-view vs personal-layout precedence | Curated default; personal view overrides only presentation state |
| UX-OD-04 | Exact semantic zoom transitions | Intent-driven levels, not automatic reveal on wheel zoom |
| UX-OD-05 | Desktop/tablet support | Desktop editing first; tablet exploration |
| UX-OD-06 | Passport mandatory fields by entity type | Display required fields even if missing; completeness score rather than invented values |
| UX-OD-07 | Approval workflow roles | Architecture owner/reviewer roles and delegated stewardship |
| UX-OD-08 | Performance reference device and dataset | Agree representative corporate laptop, browser and synthetic/real anonymized dataset |
| UX-OD-09 | Export fidelity and page sizing | Vector-first; allow fit-to-page and multi-page options |
| UX-OD-10 | Light-theme palette approval | Validate with accessibility checks and real Azure icon samples |
| UX-OD-11 | How unknown relationships are represented | Never infer from mere network proximity; show provenance and confidence |
| UX-OD-12 | Saved-view and sharing permissions | Per-user default, curated team views with review, public sharing disabled by default |

## 16. Explicit scope exclusions

- No pull-request ingestion, PR change-impact analysis, PR review workflow or PR-triggered rule checks.
- No OpenTelemetry ingestion, distributed tracing, live latency/error metrics, production request playback, live health dashboards or runtime traffic-derived dependencies.
- No uncontrolled automatic changes to Azure resources from drawing/editing a diagram.
- No claims of verified ownership, connectivity or security compliance without evidence.
- No dependence on a dark UI to make diagrams look visually impressive.

## 17. Definition of a lovable Atlas experience

Atlas is ready for serious enterprise adoption only when an architect says **“I can create a beautiful, accurate architecture diagram faster than in Visio,”** a developer says **“I can find the system and integration information I need without asking around,”** and a reviewer says **“I can trust what I see, understand what is unknown, and trace each important claim to evidence.”**

All three outcomes must be validated with actual users, real browser tests and representative enterprise-scale datasets.


## 18. V2.2 additional bright experiences and interaction acceptance

These interactions extend the V2.0/V2.2 BRD without adding a separate application. **Studio, Explore and Intelligence** share the same bright shell, canonical graph, permission system, source evidence and navigation.

| UX requirement ID | Experience | Expected user interaction | Acceptance |
| --- | --- | --- | --- |
| UX-MOD-01 | All | Switch context, application, component and deployment projection from view selector | Selected entity and evidence remain consistent; level is shown clearly |
| UX-BCM-01 | Intelligence | Browse color-coded capability map and expand Claims into supporting systems | Users can move business-to-technical without opening a separate tool |
| UX-REC-01 | Intelligence | Steward opens conflict inbox and compares field-level source evidence | Merge/split/defer actions are explicit, permissioned and reversible |
| UX-AAC-01 | Studio | Import YAML/JSON and inspect staged graph diff | Preview shows adds/updates/removals, conflicts and source status before confirmation |
| UX-BRN-01 | Studio | Compare baseline and alternative in split-screen | Topology changes differ visually from layout-only changes |
| UX-ADR-01 | Explore | Open contextual decision from node, edge or Passport | Current/superseded status, author and linked rationale visible |
| UX-LIN-01 | Explore / Intelligence | Follow documented dataset lineage with scope controls | Unknown edges and granularity clearly labeled; no runtime-flow claims |
| UX-SDK-01 | Admin | Configure connector and preview mapped entities | Source permissions, validation errors and sync state are visible |
| UX-NTF-01 | Explore | Follow component and manage digest/mute settings | Only approved record changes generate notices; no PR/telemetry triggers |
| UX-COL-01 | Studio | Comment on a draft node and resolve review thread | Comment anchors to exact entity/revision and persists |
| UX-CMD-01 | All | Cmd/Ctrl+K to search or invoke permitted action | Works from any workspace and supports keyboard-only use |
| UX-STORY-01 | Studio | Author and present stepwise architecture scenes | Scenes preserve focus, filters, snapshots, narration and accessibility |
| UX-IMP-01 | Studio | Upload draw.io/Visio interchange file and map shapes in preview | No imported line becomes a verified dependency without source validation |
| UX-FBK-01 | All | Report incorrect owner or relationship from current context | Correction ticket retains canonical ID, evidence and review status |

### 18.1 Bright design acceptance across the new experiences

- Capability maps use vivid but accessible business-domain colors, uncluttered group boundaries and meaningful icons; labels stay readable at normal zoom.
- Reconciliation and import review use side-by-side evidence panels with clear approve/reject/defer actions; never rely on red/green alone.
- Branch comparison uses clear added/removed/modified patterns and a persistent legend; layout changes are visually distinguished from graph facts.
- Command palette is immediate, searchable and keyboard-first; recent items are private to the user.
- Storytelling mode removes editing chrome but retains confidentiality, provenance and version indicators.
- Every new action must have loading, empty, success, failure, permission-denied and conflict states where applicable.
- At least one end-to-end automated browser journey per new experience must run against persisted backend state, not static mockups.

### 18.2 Open design decisions

- Define final bright theme tokens and verify contrast in representative architecture diagrams.
- Validate capability map density, business taxonomy and labels with nontechnical stakeholders.
- Confirm exact Visio interchange support before promising native `.vsdx` fidelity.
- Benchmark diagram branch diff and merge interactions on representative 1,000+ node views.
- Validate whether synchronous collaboration is needed before committing to real-time co-editing infrastructure.
