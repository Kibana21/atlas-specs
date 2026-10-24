# ATLAS

**Enterprise Architecture Intelligence & Developer Experience Platform**

Business Requirements Document (BRD) and Product Requirements Baseline

Version 2.2  |  Integrated enterprise modeling and adoption baseline  |  24 October 2026

**Change log (v2.2):** Added integrated C4-inspired modeling, business capability maps, reconciliation, architecture-as-code, architecture branches, contextual ADR knowledge, documented data lineage, connector SDK, notifications, collaboration, command palette, personal workspaces, storytelling, governed legacy diagram import and correction workflows. Updated journeys, data model, UX and phased release gates; no PR or telemetry scope.

**Change log (v2.0):** Consolidated role-based experiences, added detailed expected behaviors, failure modes, lifecycle rules, acceptance examples, visual interaction contracts, canonical data rules, release gates and a testable acceptance column for legacy functional requirements. PR functionality and production telemetry ingestion remain excluded.

**Change log (v1.1):** Added developer knowledge hub, design-time architecture playback, time machine, drift, sandbox, security/data-flow analysis, cost intelligence, self-service, quality scorecards and expanded AI capabilities. Explicitly excluded pull-request workflows and telemetry-based features.

**Change log (v1.2):** Added Architecture X-Ray, Architecture Passport, Integration Contract Registry, Architecture Pattern Library and Architecture Rule Engine, with unique requirement IDs, priorities, acceptance criteria, ownership, evidence handling and phased delivery. Explicit PR-related and telemetry exclusions remain unchanged.

Classification: Internal working draft. All examples and target values are proposed, not approved commitments.

Product vision: Every developer should be able to understand what exists, how it connects, who owns it, why it matters and what will break if it changes—without scheduling a meeting or hunting through multiple tools.

## Document control

| Field | Value |
| --- | --- |
| Product | Atlas |
| Document status | Proposed / requires validation |
| Primary sponsors | Enterprise Architecture, Engineering, Cloud Platform |
| Primary users | Developers, architects, support/operations, security, product teams |
| Deployment context | Azure-first enterprise; technology-neutral underlying model |
| Decision owners | To be nominated by sponsoring organization |

## Executive summary

Atlas is a living, evidence-backed enterprise technology map and developer portal. It combines a high-fidelity architecture editor with automated discovery, service catalog, dependency graph, developer workflows, architecture evolution, design intelligence, governance and AI-assisted exploration. It is not a replacement for source-of-truth systems such as Azure, source control, API gateways, or CMDB/ITSM; it connects them, reconciles them and makes their relationships understandable.

Success depends on two distinct promises: (1) the canvas is beautiful and truly interactive, with real Azure icons, nested boundaries, scalable layouts and editable routes; and (2) the information is sufficiently trustworthy and useful that engineers return daily for answers, onboarding, incidents and changes.

## V2.0 — Experience-led requirements expansion

This section is normative and **supplements** the ID-based requirements in Section 5. If statements conflict, the stricter security or evidence rule wins; unresolved product behavior must be logged as an open decision rather than implemented by assumption. All numeric targets below are **proposed pilot acceptance targets**, subject to baseline measurement and sponsor approval.

### Experience promise by audience

| Audience | Their first 60 seconds in Atlas should accomplish | What makes them return |
| --- | --- | --- |
| Application developer | Search a service, identify owner, contract, repository and dependencies | Reliable answers, X-Ray exploration, guided onboarding, fast deep links |
| Solution/enterprise architect | Open a beautiful business-to-Azure landscape and compare current vs proposed design | Reusable patterns, controlled diagram editing, design sandbox, rule validation |
| Cloud/platform engineer | Find resource hierarchy, configuration provenance and responsible application | Accurate Azure discovery, freshness, drift, actionable source links |
| Integration/API engineer | Find operation, version, producers, consumers and documented data schema | Contract registry, typed paths and deprecation notices |
| Security/data steward | See documented trust boundaries, sensitive-data paths and evidence gaps | Explainable rules, exceptions, classifications and audit |
| Support/operations | Find system owner, runbook and documented upstream/downstream relationships | Stable Passports, impact dossier and architecture history (not live monitoring) |
| Engineering manager/product owner | See domain coverage, ownership gaps and architecture progress | Quality scorecards, ownership accountability and exportable reviews |
| New team member | Follow a guided journey from business capability to application and API | A coherent learning path instead of fragmented documents |

### Cross-cutting interaction standards

- **Discoverability:** Search and contextual navigation are available from every major screen. A user never needs to know an Azure resource ID to start.
- **Trust:** Every discovered relationship is labeled by evidence type and freshness. Missing information is never rendered as a confirmed negative.
- **Continuity:** Selection, environment, filters, focus and back navigation survive transitions among landscape, X-Ray, Passport and contract pages.
- **Beautiful by default:** Curated overview first, intentional hierarchy and Azure iconography; no default thousand-node hairball.
- **User control:** Direct manipulation has undo, clear save status and explicit difference between editing a *view* and changing an *architecture fact*.
- **Graceful failure:** Every screen has specified loading, empty, stale, unauthorized, error and partial-result states.
- **Inclusive access:** Key exploration and editing tasks have keyboard-accessible alternatives and descriptive accessible labels.
- **Security:** Read, edit, approve, export and AI retrieval use the same scoped access policy. Shared links are not access grants.

### E01. Enterprise landscape and visual canvas

**Outcome and delight standard.** The first screen feels like a premium Azure architecture reference diagram: bright, orderly, recognizable icons, precise orthogonal connectors, clear boundaries and no accidental hairball.

**Primary users.** All; architects and developers are primary.

**Entry and starting state.** Global home opens the last authorized curated landscape or an intentional starter view; scope, environment, freshness, legend and search are visible.

**Expected interaction contract**

1. Choose a business domain, application landscape or Azure deployment perspective; Atlas loads a curated overview with collapsed systems and relationship bundles.
2. Hover a node for a lightweight summary; single-click selects and opens inspector; double-click expands or navigates according to a documented configurable gesture; breadcrumbs return to previous context.
3. Pan, zoom, fit, mini-map, focus selection and keyboard navigation work consistently; semantic zoom progressively shows labels, child services, contracts and resource details.
4. Select an edge to inspect protocol, source, target, contract, evidence, freshness and owner; expand a bundle to see actual edges.
5. Authorized editors drag nodes, resize boundaries, draw connections using typed ports, edit waypoints, align/distribute and undo/redo; save changes to a named view without silently changing topology.
6. Export SVG/PNG/PDF with legend, timestamp, source classification and page-safe text; published views have stable links and revisions.
**Business rules and data expectations**
- Official Azure icon licensing/versioning is maintained centrally; unknown resources use labeled neutral icons, never misleading Azure branding.
- Topology, view layout, proposed design and curated annotations have separate persistence and permission checks.
- A relationship requires direction and type; a manually drawn connection is a proposed/curated fact until validated or approved.
- Graph density budgets and semantic-zoom thresholds are documented per client hardware baseline; automatic bundling must never delete edges.
**Failure, ambiguity and boundary handling**
- 10,000+ components never render fully expanded by default; a clear summary and progressive expansion replace a frozen browser.
- Disconnected, circular and many-to-many relationships remain navigable; missing icons or stale sources display fallback and freshness.
- Save conflict, offline interruption and unauthorized edit show recovery actions; no silent overwrite or blank screen.
**Acceptance scenarios (Given / When / Then)**
- **1** Given a 2,000-node domain, when opening its landscape, then only a bounded meaningful overview appears and user can drill to a single AKS namespace.
- **2** Given an authorized editor, when moving five nodes and saving, then refresh restores positions and the underlying graph revision remains unchanged.
- **3** Given a relationship bundle, when expanded, then every constituent connection is accessible with direction and evidence.
- **4** Given a keyboard-only user, when navigating the canvas, then they can select, inspect, expand and return without a mouse.
**Experience quality bar.** A polished diagram is the default, not a special export; transitions feel predictable and direct manipulation is never decorative.
**Proposed outcome measure.** Pilot usability: ≥80% of target users complete “find application → dependency → owner” without assistance; proposed target.
**Dependencies / release gate.** MVP; canonical graph, icon catalog, layout service, browser E2E and performance fixture.

### E02. Search, navigation and developer workspace

**Outcome and delight standard.** A developer can get to the right application, API, queue or owner from anywhere in seconds without knowing the organizational taxonomy.

**Primary users.** Developers, support engineers, architects, security and product teams.

**Entry and starting state.** Persistent global search/command bar; recently viewed and favorites scoped to user permissions.

**Expected interaction contract**

1. Type free text, exact resource ID, API path, operation ID, alias or business capability; show incremental suggestions with type and environment.
2. Filter by entity type, domain, owner, environment, lifecycle and verification state; preserve filters in shareable URLs.
3. Open a result into its Passport or focus the matching object in a landscape; highlight matching paths and maintain back-navigation.
4. If ambiguous, present distinct candidates with environment, owning team and resource path; never silently choose Production over UAT.
5. Use keyboard command palette for jump-to-entity, focus graph, open Passport, copy ID and create draft view.
**Business rules and data expectations**
- Search indexes are permission filtered before snippets and facets are shown.
- Ranking prefers exact ID/name, verified aliases, relevance and user context; ranking rationale is documented and tunable.
- Saved searches are private by default; shared links re-evaluate authorization.
**Failure, ambiguity and boundary handling**
- No results suggests filters to remove and authorized data coverage; not an invented answer.
- Indexer lag is shown when source changes have not been indexed.
- Duplicate aliases require disambiguation; restricted names must not leak through autocomplete.
**Acceptance scenarios (Given / When / Then)**
- **1** Given two “Claims API” services in UAT and Production, when searching, then both are clearly distinguished.
- **2** Given a user without access to a confidential domain, when searching, then neither title nor facet counts leak restricted entities.
- **3** Given a deep link, when opened by an authorized colleague, then the same object and filters load.
**Experience quality bar.** Search is the main navigation pattern, not a secondary utility buried in menus.
**Proposed outcome measure.** Proposed: p95 search ≤1.5 s under pilot load; 90% of pilot tasks find target in ≤3 interactions.
**Dependencies / release gate.** MVP; index, access-aware APIs and entity Passport.

### E03. Canonical graph, evidence and reconciliation

**Outcome and delight standard.** Atlas feels trustworthy: users know which facts are verified, which are inferred and when the information was last checked.

**Primary users.** Architecture custodians, connector operators, all readers.

**Entry and starting state.** Graph populated from curated data and authorized source connectors.

**Expected interaction contract**

1. Ingest entities and edges with source IDs, evidence references, timestamps, environment, owner and classification.
2. Match source records to canonical IDs; display proposed merges when identity is uncertain rather than automatically combining unrelated systems.
3. Inspect conflicting names, ownership or relationships side by side; show source precedence and review workflow.
4. Publish approved graph snapshots; permit rollback of curated assertions without rewriting source-system history.
5. Traverse upstream/downstream with typed edges, hop limits, cycle detection and explicit incomplete coverage.
**Business rules and data expectations**
- Entity and edge IDs remain stable across aliases and source renames when identity is verified.
- Facts retain first/last seen, effective time, discovered/curated/inferred/proposed status and immutable evidence pointers.
- Absence from one sync is not deletion; tombstone only after source-specific grace policy and verification.
- Current, proposed and historical facts are never visually conflated.
**Failure, ambiguity and boundary handling**
- Connector permission loss yields “coverage unknown”, not deletion of previously known resources.
- Conflicting source claims remain reviewable with timestamps and source precedence.
- Very deep traversal is bounded and paginated with an explicit truncated result warning.
**Acceptance scenarios (Given / When / Then)**
- **1** Given duplicate APIM API records with a matching stable Azure ID, when synced, then one canonical entity links to both evidence records.
- **2** Given a resource missing from one failed sync, when viewed, then Atlas retains last-known state and marks freshness uncertain.
- **3** Given a cycle A→B→C→A, when tracing three hops, then traversal terminates and marks the cycle.
**Experience quality bar.** Every graph edge should answer “why do you believe this connection exists?”
**Proposed outcome measure.** Proposed: 95% of critical published edges have source evidence; 90% critical applications have an owner.
**Dependencies / release gate.** MVP foundation; schema, identity resolution and evidence storage.

### E04. Azure and enterprise connector discovery

**Outcome and delight standard.** Teams stop manually redrawing what Azure and approved documentation already know, without overclaiming connections.

**Primary users.** Platform engineering, connector operators, architects.

**Entry and starting state.** Admin selects a connector template and approved scope.

**Expected interaction contract**

1. Configure tenant/subscription/resource group, APIM, AKS, messaging, repository metadata, CMDB or billing scope with least-privilege identity.
2. Run connection test to show reachable sources, permissions, excluded regions/resources and expected metadata fields.
3. Preview import counts and conflicts; start full sync followed by incremental scheduled sync with checkpoints.
4. Inspect job status, records created/updated/unmatched, permission failures and per-source freshness.
5. Retry failed partitions idempotently; request review of ambiguous relationships; publish validated changes to graph.
**Business rules and data expectations**
- Read-only discovery by default; never deploy or modify cloud resources through ingestion.
- Azure hierarchy and configuration are not proof of actual runtime communication.
- Connector mapping, credential rotation, pagination, throttling and retry policy are documented per source.
- Secrets, message payloads and production request data are not collected.
**Failure, ambiguity and boundary handling**
- API throttling backs off and resumes; partially successful sync is explicitly labeled.
- Unsupported resource types are retained as generic typed objects with raw safe metadata.
- Expired permissions produce actionable administrator notices while readers retain last-known-good snapshots.
**Acceptance scenarios (Given / When / Then)**
- **1** Given a connector with only one authorized subscription, when synced, then no entities from other subscriptions appear.
- **2** Given APIM API configuration, when imported, then contract and configured backend relationships are labeled configuration-derived.
- **3** Given a sync failure halfway, when retried, then canonical records are not duplicated.
**Experience quality bar.** Connector setup should make coverage and limitations understandable without requiring users to read raw job logs.
**Proposed outcome measure.** Proposed: ≥95% of in-scope inventory refreshed within 24 hours when source APIs are available.
**Dependencies / release gate.** Phase 1–2; connector SDK, job queue, Azure identity and provenance model.

### E05. Architecture X-Ray

**Outcome and delight standard.** One click opens the internals of an application without losing surrounding systems or visual orientation.

**Primary users.** Developers, solution architects, operations.

**Entry and starting state.** Start from selected application in enterprise landscape.

**Expected interaction contract**

1. Expand application to logical services and internal integrations while keeping neighboring systems visible.
2. Switch abstraction level between application, service, integration and Azure infrastructure; use breadcrumb and back controls.
3. Expand subscription/resource group/AKS cluster/namespace and select workload or endpoint.
4. Bundle external relationships and expand only the subset of interest; save expansion state with the view.
**Business rules and data expectations**
- X-Ray reads canonical IDs and does not create a duplicate model.
- Unknown hierarchy levels are explicit; documented versus discovered children are visually distinct.
- Expansion preserves position and user-selected focus where possible.
**Failure, ambiguity and boundary handling**
- Excessive children switch to grouped summary with count and search.
- Mixed environments require explicit labels; hidden restricted children do not leak counts if policy disallows.
**Acceptance scenarios (Given / When / Then)**
- **1** Given Policy Administration, when expanded, then neighboring Claims remains visible.
- **2** Given an expanded namespace, when collapsed and re-opened, then saved curated state restores.
**Experience quality bar.** Zoom and expand should feel like exploring a coherent map, not jumping to unrelated pages.
**Proposed outcome measure.** Proposed: 80% of developers locate an internal workload in ≤60 s during pilot.
**Dependencies / release gate.** MVP / phase 2; canvas, graph hierarchy and access policy.

### E06. Architecture Passport and knowledge hub

**Outcome and delight standard.** Every component has a beautiful, authoritative profile that answers “what is this, who owns it and how do I work with it?”

**Primary users.** All roles, particularly new developers and support engineers.

**Entry and starting state.** Open from search, diagram inspector, deep link or onboarding journey.

**Expected interaction contract**

1. Show purpose, type, lifecycle, owner, environment, deployment, classification, verification and last update above the fold.
2. Navigate tabs for dependencies, contracts, infrastructure, documentation, ADRs, onboarding, history and evidence.
3. Copy resource identifiers, open approved repo/runbook/contract links and jump back to focused diagram.
4. Submit missing-owner claim or proposed correction; reviewers compare before/after and approve or reject with reason.
5. Offer guided domain journeys with checkpoints and suggested next components.
**Business rules and data expectations**
- Mandatory fields differ by entity type and are centrally defined.
- Passport is a projection of canonical records, not a separate manually maintained database.
- “Unknown”, “not applicable”, “not verified” and “stale” have distinct meanings.
**Failure, ambiguity and boundary handling**
- Broken document link is flagged and can be reported.
- Conflicting owner information shows both claims and review state.
- Unauthorized users see a scoped Passport, not an error that leaks sensitive attributes.
**Acceptance scenarios (Given / When / Then)**
- **1** Given a Claims API, when opened, then owner, contract, upstream/downstream and runbook are reachable.
- **2** Given a proposed ownership correction, when submitted, then published owner remains until approval.
**Experience quality bar.** A Passport should be useful on its own, even for users who never open the full canvas.
**Proposed outcome measure.** Proposed: owner lookup ≤60 s and ≥90% critical entity Passport completeness.
**Dependencies / release gate.** MVP; graph, ownership, docs links and review workflow.

### E07. Integration Contract Registry

**Outcome and delight standard.** Developers understand the exact documented API/event/data interfaces between systems, without analyzing PRs or observing live traffic.

**Primary users.** API engineers, integration architects, data stewards, security.

**Entry and starting state.** Search by operation, route, event, schema field or connected system.

**Expected interaction contract**

1. Import validated OpenAPI, AsyncAPI and approved documented file/data interface definitions.
2. Index version, operation, endpoint/topic, producer, consumer, payload schema, security requirements, environment and classification.
3. Open a connector in the architecture diagram and jump to its exact contract version.
4. Compare two published specifications and classify deterministic changes as additive, removed or potentially breaking with reasons.
5. Publish deprecation notices, ownership and lifecycle state; list documented consumers.
**Business rules and data expectations**
- Version comparison operates on specification artifacts, never pull requests.
- Inferred consumer links are labeled as inferred and never treated as observed runtime consumers.
- Sensitive field definitions are access-controlled and excluded from unauthorized exports and AI.
**Failure, ambiguity and boundary handling**
- Malformed spec is quarantined with line/validation detail; no partial silent publication.
- Two sources defining same route but different schemas remain in conflict-review state.
- No documented consumer is “unknown coverage”, not proof of zero consumers.
**Acceptance scenarios (Given / When / Then)**
- **1** Given v1/v2 OpenAPI, when a required field is removed, then a potential compatibility risk is displayed with affected schema path.
- **2** Given an unauthorized role, when opening a restricted payload, then sensitive fields are redacted in UI and export.
**Experience quality bar.** An API contract is one click from its architecture connection.
**Proposed outcome measure.** Proposed: 90% of critical documented interfaces linked to contracts by phase 3.
**Dependencies / release gate.** Phase 2; spec parser, catalog, provenance, classification.

### E08. Architecture Pattern Library and future-state sandbox

**Outcome and delight standard.** Architects can assemble beautiful, approved designs quickly and safely without accidentally changing production.

**Primary users.** Architects, platform teams, senior developers.

**Entry and starting state.** Pattern gallery or “Create future-state design” action.

**Expected interaction contract**

1. Filter approved patterns by problem, Azure services, security zone, integration style and data classification.
2. Open pattern detail for intent, trade-offs, boundaries, sample diagram, ADR and owner.
3. Instantiate a pattern in an isolated draft canvas; configure environment, names, identity and network parameters.
4. Validate completeness and architecture rules; compare proposed design against current baseline.
5. Submit for review, resolve comments, publish approved design snapshot or retire pattern version.
**Business rules and data expectations**
- Instantiating a pattern creates design artifacts only; never provisions Azure resources.
- Approved patterns are versioned and immutable after approval; changes produce a new revision.
- Pattern applicability and constraints are visible before use.
**Failure, ambiguity and boundary handling**
- Missing required parameters block submission with inline errors.
- Deprecated patterns remain discoverable but are not default recommendations.
- Conflicting edits require revision reconciliation.
**Acceptance scenarios (Given / When / Then)**
- **1** Given an approved private AKS pattern, when instantiated, then proposed resources are visually marked and production remains unchanged.
- **2** Given a deprecated pattern, when selected, then user sees warning and recommended replacement.
**Experience quality bar.** Starting a design should feel like choosing a professional template, not constructing every node from scratch.
**Proposed outcome measure.** Proposed: reduce time to create a review-ready common reference design by 40% in pilot.
**Dependencies / release gate.** Phase 3–4; sandbox, templates, approval workflow and rule engine.

### E09. Architecture Rule Engine and scorecards

**Outcome and delight standard.** Governance is transparent and constructive: explain exactly what failed, what is unknown and how to fix it.

**Primary users.** Architecture reviewers, security, domain owners, developers.

**Entry and starting state.** From Passport, proposed design or domain quality dashboard.

**Expected interaction contract**

1. Select applicable versioned rule pack and snapshot; evaluate without modifying topology.
2. Show PASS, FAIL, UNKNOWN, NOT_APPLICABLE and EXEMPT with severity, entity and evidence.
3. Click finding to focus exact object, see rule rationale, recommended remediation and source record.
4. Propose exception with scope, reason and expiry; authorized reviewer approves or rejects.
5. Export filtered findings and trend across snapshots; show completeness separate from conformance.
**Business rules and data expectations**
- Authoritative pass/fail is deterministic for identical snapshot, rules and configuration.
- Missing permissions/evidence produce UNKNOWN, not PASS or FAIL.
- Rule version, input graph snapshot and evaluation timestamp are immutable audit metadata.
**Failure, ambiguity and boundary handling**
- Rule execution timeout yields incomplete evaluation state and retry action.
- Expired exception reopens finding automatically on next evaluation.
- Sensitive evidence is masked based on viewer permissions.
**Acceptance scenarios (Given / When / Then)**
- **1** Given missing encryption evidence, when evaluated, then state is UNKNOWN.
- **2** Given a confirmed publicly reachable production database, when evaluated, then rule FAIL cites source and affected entity.
- **3** Given an expired exception, when evaluated, then EXEMPT no longer applies.
**Experience quality bar.** No unexplained red score; every issue has a traceable cause and next step.
**Proposed outcome measure.** Proposed: ≥95% of rule findings link to inspectable evidence; false-positive rate reviewed monthly.
**Dependencies / release gate.** Phase 3; deterministic rule DSL, provenance, approvals and test fixtures.

### E10. Dependency analysis, time machine and design-time playback

**Outcome and delight standard.** Developers and architects can explain architecture relationships, proposed change exposure and documented business journeys without production traces.

**Primary users.** Developers, architects, risk, change teams.

**Entry and starting state.** Select an entity, date snapshot or documented business process.

**Expected interaction contract**

1. Choose upstream/downstream direction, relationship types, environment and hop limit; Atlas highlights candidate affected systems with paths.
2. Show direct versus transitive links, confidence, verification, owners and unknown coverage.
3. Compare architecture snapshots for added/removed/changed resources, connections and ownership.
4. Play a curated design-time journey step by step, highlighting documented API, queue and data handoffs with explanatory annotations.
5. Export an impact dossier or presentation sequence with caveats and evidence.
**Business rules and data expectations**
- Potential impact is not guaranteed outage impact; language must remain probabilistic.
- Playback is a sequence of documented model steps, not runtime trace replay.
- Snapshot diffs retain source history and exclude failed-sync artifacts from confirmed deletions.
**Failure, ambiguity and boundary handling**
- Traversal budget reached yields truncated result and continuation options.
- Unknown environment or incomplete path is called out explicitly.
- Missing step evidence pauses story with “undocumented” rather than inventing an interface.
**Acceptance scenarios (Given / When / Then)**
- **1** Given A→B→C with documented links, when impact is run from A, then B and C appear with distinct hop counts and evidence.
- **2** Given snapshots before and after an APIM route change, when compared, then route difference is highlighted.
- **3** Given a design-time journey, when played, then no latency, trace ID or live traffic claims appear.
**Experience quality bar.** The same model supports technical investigation and compelling architecture storytelling.
**Proposed outcome measure.** Proposed: 50% faster documented dependency tracing than existing manual baseline.
**Dependencies / release gate.** Phase 2–3; graph traversal, snapshots, process models.

### E11. AI-assisted architecture intelligence

**Outcome and delight standard.** Ask Atlas makes complex architecture approachable but never replaces evidence, permission checks or human approvals.

**Primary users.** Developers, architects, security and platform teams.

**Entry and starting state.** Contextual Ask Atlas panel available from search, diagram and Passport.

**Expected interaction contract**

1. Ask “Which applications depend on Policy Administration?”; assistant resolves scope and asks clarification if ambiguous.
2. Retrieve only authorized graph objects, contract metadata and approved documents; answer with clickable citations, timestamps and unknowns.
3. Offer previewable actions such as focus nodes, expand path, create draft view or summarize a design.
4. For natural-language design creation, generate a proposed sandbox graph and list assumptions; user explicitly accepts before saving.
5. Collect feedback on incorrect answers with links to source corrections and review queues.
**Business rules and data expectations**
- AI cannot invent verified entities, dependencies, owners or security status.
- AI may suggest a rule or architecture pattern, but deterministic rule engine remains authoritative.
- Prompts, retrieval and outputs follow data classification, retention and audit policies.
**Failure, ambiguity and boundary handling**
- No evidence produces “cannot verify” with next useful search options.
- Ambiguous environment asks a question rather than choosing.
- Prompt injection in retrieved docs cannot override RBAC or tool permissions.
**Acceptance scenarios (Given / When / Then)**
- **1** Given conflicting sources, when asked for an owner, then answer discloses disagreement and source links.
- **2** Given restricted records, when user asks broadly, then assistant omits them entirely.
- **3** Given proposed diagram generation, when user declines preview, then no graph write occurs.
**Experience quality bar.** Answers should be concise, visual when useful and verifiably grounded.
**Proposed outcome measure.** Proposed: ≥90% citation correctness on curated evaluation set; zero known unauthorized disclosures.
**Dependencies / release gate.** Phase 3–4; retrieval layer, authorization, evaluation dataset and guarded actions.

### E12. Security, data flows, cost and self-service

**Outcome and delight standard.** Atlas helps teams make responsible architecture decisions without becoming a privileged production control plane.

**Primary users.** Security, platform, finance, architects, developers.

**Entry and starting state.** Lens selection from any graph or Passport.

**Expected interaction contract**

1. Security lens highlights documented trust boundaries, identities, public endpoints and data classification.
2. Data lens shows documented source/target, data category, contract and steward; flags unknown transfer semantics.
3. Cost lens maps authorized billing-export allocation to resources, applications and shared platforms with attribution confidence.
4. Self-service links open approved external portals for access requests, scaffolding or architecture reviews; any future write action needs explicit authorization and approval.
**Business rules and data expectations**
- No runtime packet inspection, message payload ingestion or telemetry is implied.
- Billing allocations are estimates/showback unless financial reconciliation is approved.
- Actions use least privilege and preserve full audit of approvals and external references.
**Failure, ambiguity and boundary handling**
- Unallocated shared costs are explicitly unallocated, not silently assigned.
- Unknown data classification remains unknown; no false assurance.
- External self-service system unavailable gives a deep link and retry guidance.
**Acceptance scenarios (Given / When / Then)**
- **1** Given confidential data flow, when viewed by unauthorized user, then payload field metadata is hidden.
- **2** Given 30% shared cloud cost unallocated, when viewing report, then unallocated portion is visible.
**Experience quality bar.** Lenses change the explanation, not the underlying truth.
**Proposed outcome measure.** Proposed: 90% of critical systems have a documented classification; cost coverage targets require finance sign-off.
**Dependencies / release gate.** Phase 3–4; classification policy, billing exports and approved self-service integrations.

### E13. Governance, collaboration and enterprise trust

**Outcome and delight standard.** Teams can collaborate without destroying curated diagrams, losing decisions or exposing sensitive infrastructure.

**Primary users.** Domain owners, architects, editors, auditors, administrators.

**Entry and starting state.** Draft/published design or Passport correction workflow.

**Expected interaction contract**

1. Create draft, comment at node/edge/diagram level and request review from named domain owner.
2. Compare proposed change against published baseline, including topology, layout and evidence differences.
3. Approve or reject with comments; publish immutable revision and notify interested subscribers.
4. Use audit history to explain who changed what, when and under which permission.
5. Use shareable links that re-check viewer authorization and preserve focus/filters.
**Business rules and data expectations**
- Role and resource scope control view, edit, approve, export and connector operations separately.
- A reviewer cannot approve their own restricted change where separation-of-duties policy applies.
- Draft, published, superseded and archived states are explicit and versioned.
**Failure, ambiguity and boundary handling**
- Concurrent edits use revision conflict handling, not last-write-wins.
- Rejected drafts remain visible to authors with reasons.
- Restricted nodes are hidden or aggregated only according to policy; shared links never bypass controls.
**Acceptance scenarios (Given / When / Then)**
- **1** Given two editors changing same revision, when second saves, then conflict is shown with reconciliation options.
- **2** Given a viewer, when trying to publish, then action is denied and audited.
- **3** Given a rejected change, when author opens it, then reviewer comments and diff remain visible.
**Experience quality bar.** Collaboration should feel like modern design software, with enterprise auditability underneath.
**Proposed outcome measure.** Proposed: zero unauthorized publishes in security tests; 100% published revisions attributable to actor.
**Dependencies / release gate.** MVP governance core, expanded phase 2–3.

### E14. Performance, accessibility and resilience

**Outcome and delight standard.** Atlas must feel fast, predictable and inclusive even with a huge enterprise estate.

**Primary users.** All users; QA, accessibility and platform teams.

**Entry and starting state.** Any supported browser or keyboard-accessible entry point.

**Expected interaction contract**

1. Progressively load graph data and render a meaningful curated overview before optional detail.
2. Keep pan/zoom and selection responsive; run heavy layout and traversals outside blocking interaction paths.
3. Provide accessible list/table alternative for graph exploration, high contrast, visible focus and full keyboard traversal.
4. Show last-known-good graph and stale banner when connectors fail; show clear loading, empty and permission states.
5. Capture product reliability and performance diagnostics only; no production application telemetry ingestion.
**Business rules and data expectations**
- Pilot dataset: 10k resources/100k edges; architecture designed for 100k+/1m+ with progressive loading.
- Browser matrix, performance hardware profile, network profile and thresholds are fixed before acceptance.
- Accessibility target WCAG 2.2 AA with documented exceptions and remediation plan.
**Failure, ambiguity and boundary handling**
- Graph query timeout returns partial scoped result and retry; never browser freeze.
- Unsupported browser shows clear compatibility guidance.
- Offline or sync outage does not make published diagrams vanish.
**Acceptance scenarios (Given / When / Then)**
- **1** Given 10k/100k fixture, when opening curated domain, then first meaningful content meets agreed p75 target.
- **2** Given keyboard-only navigation, when moving through graph list, then focus, inspect and open are available.
- **3** Given connector outage, when viewing published map, then last-known snapshot remains with freshness warning.
**Experience quality bar.** The most beautiful view is worthless if it hangs or fails to open.
**Proposed outcome measure.** Proposed: p75 meaningful render ≤2 s, common indexed search p95 ≤1.5 s; benchmark environment to be approved.
**Dependencies / release gate.** Cross-cutting release gate; browser E2E, accessibility and load test suites.

### E16. Core entity Passport field contract

| Entity class | Mandatory fields at creation | Recommended fields | Explicit unknown handling |
| --- | --- | --- | --- |
| Business capability | ID, name, domain, owner state, lifecycle | Outcomes, processes, linked applications | Missing owner = unassigned, not inferred |
| Application | ID, name, environment scope, owner state, lifecycle | Purpose, criticality, support group, repo, runbook | Missing dependencies = coverage unknown |
| API / operation | ID, owning application, interface type, environment, version state | Method/path, auth, schema, APIM route | Missing consumer = undocumented, not unused |
| Event / queue / topic | ID, platform, environment, owner state | Publisher, consumer, schema, DLQ policy | Missing subscribers = unknown coverage |
| Database / dataset | ID, environment, owning domain, classification state | Engine, steward, schema, read/write links | Missing classification = needs review |
| Azure resource | Canonical ID, resource type, subscription, region, discovery source | Resource group, tags, identity, network zone | Missing field = source unavailable/unknown |
| Relationship | Source ID, target ID, direction, type, evidence status | Contract, protocol, owner, first/last seen | Missing evidence = proposed/inferred, not verified |

### E17. Lifecycle and permission expectations

| Object | Draft | Review | Published | Superseded / retired |
| --- | --- | --- | --- | --- |
| Diagram view | Editor can change layout/annotations | Reviewer sees visual diff | Stable deep link and immutable revision | Historical view remains available |
| Curated graph assertion | Proposed with evidence | Owner checks conflict | Becomes approved assertion | Retained with effective dates |
| Architecture pattern | Template authoring | Architect + policy review | Approved, versioned instantiation | Warning and recommended replacement |
| Integration contract | Imported/proposed | Steward validates source/version | Searchable approved revision | Deprecated/retired, history retained |
| Rule pack | Author/test fixtures | Governance review | Deterministic evaluation version | Historical evaluations reproducible |
| Rule exception | Request with rationale | Authorized approval | Time-bound exception | Expiry restores original finding |

**Minimum role separation:** Viewer reads authorized published data; Developer can create personal views and proposals; Editor can modify scoped drafts; Domain Owner verifies owned entities; Architect Reviewer approves designs/patterns; Security Reviewer approves applicable exceptions; Connector Operator manages read-only integrations; Administrator configures roles and policies but does not implicitly bypass all data classifications. Exact permissions require an approved RBAC matrix before development.

### E18. Quality and design acceptance matrix

| Quality gate | Minimum expected evidence | Release blocker |
| --- | --- | --- |
| Visual integrity | Screenshot comparison of overview, nested Azure deployment, 1k-edge dense view, exports and small viewport | Missing icons, overlapping labels in curated fixtures, blank canvas |
| Interaction integrity | Real-browser automated tests for click, double-click, drag, edge inspect, undo/redo, save/reload, deep link | Decorative/nonworking primary controls |
| Evidence integrity | Fixture proving discovered vs inferred vs proposed; failed sync; source conflict; tombstone grace | Unverified edge shown as confirmed; failed sync causes false deletion |
| Security | Role-by-resource matrix for search, canvas, Passport, exports, AI and connectors | Any cross-role metadata leak or unauthorized publication |
| Scale | 10k/100k fixture with curated initial viewport and graph budgets; 100k+/1m+ architecture benchmark plan | Browser freeze, unbounded expansion, query timeout without recovery |
| Contract integrity | OpenAPI/AsyncAPI import, invalid specs, version diff and restricted schema fields | Incorrect contract identity or unauthorized field disclosure |
| Rule integrity | Pass/fail/unknown/not-applicable/exempt fixtures and expired exception | Missing evidence evaluated as pass/fail; nondeterministic outcomes |
| Workflow | Draft→review→publish→supersede, correction request and conflict resolution | Lost changes or bypassed approvals |
| Accessibility | Keyboard journey and accessible graph alternative; WCAG 2.2 AA audit | Critical task impossible without pointer |
| Resilience | Connector outage, stale index, API error and browser reload | Loss of last-known-good published architecture |

### E19. Delivery expectations and decision log

**Release 0 — Product validation and foundations:** Confirm role-based tasks with real architects/developers; approve terminology, graph identity, source precedence, data classification, RBAC, diagram interaction model, performance fixture and Azure icon licensing. Deliver clickable browser prototype and usability study. No backend feature counts substitute for user validation.

**Release 1 — Lovable architecture exploration:** Ship search-first home, curated enterprise map, professional Azure canvas, in-place X-Ray, baseline Passport, manual/CSV import, ownership, deep links, diagram save/export and permissions. Gate: user can find, understand and share a representative system without assistance.

**Release 2 — Trustworthy living graph:** Add Azure/APIM/AKS/messaging discovery, connector coverage, reconciliation, versioned evidence, Contract Registry, graph traversal and historical snapshots. Gate: sources reconcile reproducibly and all claims reveal provenance.

**Release 3 — Architecture intelligence:** Add drift comparison, design-time journeys, deterministic Rule Engine, quality scorecards, governed exceptions, and expanded AI Q&A with citations. Gate: evaluation fixtures, evidence and permissions pass independently.

**Release 4 — Design excellence and enterprise expansion:** Add Pattern Library, sandbox comparison, advanced security/data-flow lens, cloud cost showback, richer guided onboarding, collaboration and controlled self-service links. Gate: proposed designs never mutate deployed resources; governance and accessibility are production-ready.

**Decisions requiring sponsor approval:** definition of authoritative owner; source precedence; supported initial Azure resource types; exact semantic-zoom thresholds; contract compatibility policy; approval/SoD matrix; restricted metadata treatment; sync SLAs; pilot performance hardware and load; cost allocation policy; AI data retention; licensing; deployment/hosting region; archival retention.

### E20. Scope exclusions — non-negotiable unless explicitly reopened

- No pull-request integration, PR review, PR-triggered change analysis, or repository commit impact automation.
- No production application telemetry ingestion, distributed tracing, OpenTelemetry, live health overlays, incident event correlation or observed transaction playback.
- No claim that a documented/configured dependency is proof of runtime communication.
- No cloud resource provisioning from the design canvas or pattern instantiation.
- No unsupervised AI publication of authoritative architecture facts or rule outcomes.
- Internal **Atlas product diagnostics** (UI errors, API latency, connector job status) are allowed for operating Atlas itself; they are not telemetry ingestion from the enterprise applications being mapped.


## 1. Business context and problem statement

Enterprise application estates are fragmented across cloud consoles, CMDBs, API gateways, Kubernetes, source repositories and architecture diagrams. Existing diagrams become stale, omit cross-system relationships and cannot reliably answer cross-system impact questions. Developers struggle to find owners, contracts, dependencies and deployment locations. Architects spend time recreating maps; security and operations teams lack consistent context.

## 1.1 Business objectives

- Create one navigable, federated architecture knowledge layer spanning business capabilities, applications, integrations, data and infrastructure.
- Reduce time-to-understand for unfamiliar services and time-to-identify owners/dependencies during changes and incidents.
- Make architecture views attractive, precise and maintainable enough for technical design and executive communication.
- Establish traceable evidence and freshness for relationships instead of presenting all discovered or inferred links as facts.
- Improve engineering self-service, architecture governance, security visibility and operational resilience.
## 1.2 Success measures (proposed pilot targets)

| Metric | Baseline | Pilot target / measurement |
| --- | --- | --- |
| Time to find service owner | Measure in discovery | Median under 60 seconds in usability study |
| Time to trace a critical dependency | Measure in discovery | At least 50% reduction versus current process |
| Verified ownership coverage | Measure in discovery | At least 90% of pilot critical applications |
| Architecture freshness | Measure in discovery | At least 95% of discovered cloud inventory refreshed within 24h |
| Canvas interaction reliability | Not yet established | 100% of release-blocking interaction E2E tests pass |
| Developer adoption | Measure in discovery | At least 60% weekly active among invited pilot engineers |
| Impact explanation quality | Golden-set benchmark | At least 90% of reported paths include inspectable evidence |

## 2. Scope and boundaries

## 2.1 In scope

- Azure-centric infrastructure mapping: tenants, subscriptions, management groups, resource groups, VNets, subnets, APIM, AKS, namespaces, services, databases, messaging and supporting services.
- Application/service catalog with owners, repositories, APIs, deployments, runbooks, business capabilities and environments.
- Directed, typed, versioned relationships with provenance, confidence, validity and source timestamps.
- Interactive architecture canvas, diagram editing, saved perspectives, exports and collaboration.
- Search, discovery, declared/configured dependency tracing, change-impact assessment, architecture design workflows and AI-assisted exploration.
- Architecture evolution, drift detection, design-time process playback, security/data-flow analysis, cost attribution, guided onboarding, governed self-service and quality scorecards.
- Connectors and synchronization with approved enterprise systems; RBAC, audit and enterprise security.
## 2.2 Explicitly out of scope for initial release

- Replacing Azure Portal, source control, ITSM or API gateways as their operational systems of record.
- Pull-request scanning, PR review comments, PR-based change impact and code-review automation.
- Production telemetry ingestion, distributed tracing, live service health overlays, log ingestion and runtime transaction replay.
- Claiming complete runtime topology or verified traffic flows from configuration/inventory sources alone.
- Automatically changing production cloud resources from diagram actions.
- Autonomous deployment, remediation or approval of high-impact changes.
- Guaranteed perfect auto-layout for arbitrary fully expanded 10,000-node diagrams.
## 3. Personas and jobs to be done

| Persona | Primary job | Delight moment |
| --- | --- | --- |
| Developer / new joiner | Understand service, owners, dependencies, APIs and code | Find everything about a service from one search |
| Tech lead / architect | Design, compare, document and review systems | Publish precise diagrams without rebuilding metadata |
| Operations / support | Understand service ownership and configured dependencies | Find relevant system documentation and runbooks |
| Security / compliance | Trace data, trust boundaries and exposure | Inspect sensitive flows with evidence |
| Platform / cloud engineer | Find workloads, resources, drift and shared infrastructure | Navigate Azure hierarchy with live context |
| Engineering manager / product owner | Understand capabilities, criticality and risk | Clear system-to-business mapping |
| Change / release manager | Review likely impact and sign-offs | Attach an explainable impact dossier |

## 4. Product experience principles

- Architecture first: technical diagrams must look and behave like high-quality Visio/Lucidchart/Azure reference diagrams, not generic node cards.
- Progressive disclosure: enterprise → domain → application → integration → deployment → workload → resource; never overwhelm the canvas by default.
- One model, many views: diagrams are projections of a shared graph, not disconnected copies of facts.
- Developer-first: search, copy links, deep links, keyboard shortcuts, code/API/runbook links and fast navigation are core workflows.
- Trust by design: source, last seen, evidence, inferred versus observed, and confidence are visible on every relationship.
- Editable without corruption: manual layout changes do not alter topology; graph updates do not unexpectedly destroy curated layouts.
- No dead controls: every interactive control is keyboard accessible, tested and has meaningful feedback.
## 5. Core functional requirements

## 5.1 Enterprise inventory and canonical graph

| ID | Requirement / expected behavior | Priority | Verifiable acceptance expectation |
| --- | --- | --- | --- |
| INV-01 | Maintain canonical IDs for business capabilities, domains, systems, applications, services, deployments, cloud resources, APIs, events, datasets and owners. | Must | Given authorized representative fixtures and the required source data, the user can verify: maintain canonical IDs for business capabilities, domains, systems, applications, services, deployments, cloud resources, APIs, events, datasets and owners; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| INV-02 | Support directed typed relationships: CALLS_API, PUBLISHES, CONSUMES, READS, WRITES, DEPLOYED_ON, HOSTED_IN, OWNS, DEPENDS_ON and PROTECTS. | Must | Given authorized representative fixtures and the required source data, the user can verify: support directed typed relationships: CALLS_API, PUBLISHES, CONSUMES, READS, WRITES, DEPLOYED_ON, HOSTED_IN, OWNS, DEPENDS_ON and PROTECTS; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| INV-03 | Record source system, evidence pointer, discovery method, confidence, first/last seen, validity period and verification state for each fact. | Must | Given authorized representative fixtures and the required source data, the user can verify: record source system, evidence pointer, discovery method, confidence, first/last seen, validity period and verification state for each fact; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| INV-04 | Support deduplication, alias matching, merge review and conflict resolution across multiple discovery sources. | Must | Given authorized representative fixtures and the required source data, the user can verify: support deduplication, alias matching, merge review and conflict resolution across multiple discovery sources; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| INV-05 | Represent environment and regional separation, shared infrastructure and many-to-many ownership. | Must | Given authorized representative fixtures and the required source data, the user can verify: represent environment and regional separation, shared infrastructure and many-to-many ownership; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| INV-06 | Retain history and soft deletion/tombstones for removed resources; distinguish missing data from verified removal. | Must | Given authorized representative fixtures and the required source data, the user can verify: retain history and soft deletion/tombstones for removed resources; distinguish missing data from verified removal; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| INV-07 | Provide graph and catalog APIs with pagination, filters and access-aware responses. | Must | Given authorized representative fixtures and the required source data, the user can verify: provide graph and catalog APIs with pagination, filters and access-aware responses; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |

## 5.2 Premium diagramming canvas

| ID | Requirement / expected behavior | Priority | Verifiable acceptance expectation |
| --- | --- | --- | --- |
| CAN-01 | Render official licensed Microsoft Azure Architecture Icons using a centrally maintained asset library; preserve labels and source attribution where required. | Must | Given authorized representative fixtures and the required source data, the user can verify: render official licensed Microsoft Azure Architecture Icons using a centrally maintained asset library; preserve labels and source attribution where required; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| CAN-02 | Support nested containers: tenant, subscription, resource group, VNet, subnet, AKS cluster, namespace, workload and application boundaries. | Must | Given authorized representative fixtures and the required source data, the user can verify: support nested containers: tenant, subscription, resource group, VNet, subnet, AKS cluster, namespace, workload and application boundaries; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| CAN-03 | Provide orthogonal routing with port anchors, arrowheads, waypoints, edge labels, obstacle avoidance and visual distinction by relationship type. | Must | Given authorized representative fixtures and the required source data, the user can verify: provide orthogonal routing with port anchors, arrowheads, waypoints, edge labels, obstacle avoidance and visual distinction by relationship type; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| CAN-04 | Support expand/collapse and semantic zoom with configurable visibility rules by scale and user intent. | Must | Given authorized representative fixtures and the required source data, the user can verify: support expand/collapse and semantic zoom with configurable visibility rules by scale and user intent; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| CAN-05 | Allow free positioning, resize, multi-select, alignment, distribution, grid snapping, copy/paste, undo/redo and connector editing. | Must | Given authorized representative fixtures and the required source data, the user can verify: allow free positioning, resize, multi-select, alignment, distribution, grid snapping, copy/paste, undo/redo and connector editing; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| CAN-06 | Persist manual layouts separately from topology and support named, shared, versioned curated diagrams. | Must | Given authorized representative fixtures and the required source data, the user can verify: persist manual layouts separately from topology and support named, shared, versioned curated diagrams; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| CAN-07 | Provide pan/zoom, fit-to-view, mini-map, breadcrumb navigation, focus mode and performant selection/hover states. | Must | Given authorized representative fixtures and the required source data, the user can verify: provide pan/zoom, fit-to-view, mini-map, breadcrumb navigation, focus mode and performant selection/hover states; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| CAN-08 | Bundle related edges with counts and expansion; offer path highlighting and crossing reduction. | Must | Given authorized representative fixtures and the required source data, the user can verify: bundle related edges with counts and expansion; offer path highlighting and crossing reduction; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| CAN-09 | Export high-resolution SVG, PNG and PDF with labels, boundaries, legends and optional provenance. | Must | Given authorized representative fixtures and the required source data, the user can verify: export high-resolution SVG, PNG and PDF with labels, boundaries, legends and optional provenance; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| CAN-10 | Support keyboard shortcuts, accessible selection, readable contrast, tooltips and screen-reader alternatives. | Must | Given authorized representative fixtures and the required source data, the user can verify: support keyboard shortcuts, accessible selection, readable contrast, tooltips and screen-reader alternatives; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| CAN-11 | Offer auto-layout presets for landscape, layered flow, deployment hierarchy and integration sequence. | Should | Given authorized representative fixtures and the required source data, the user can verify: offer auto-layout presets for landscape, layered flow, deployment hierarchy and integration sequence; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| CAN-12 | Enable diagram comments, annotations, review status, templates and presentation mode. | Should | Given authorized representative fixtures and the required source data, the user can verify: enable diagram comments, annotations, review status, templates and presentation mode; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |

## 5.3 Search, navigation and developer portal

| ID | Requirement / expected behavior | Priority | Verifiable acceptance expectation |
| --- | --- | --- | --- |
| DEV-01 | Provide global search over names, aliases, resource IDs, APIs, routes, repositories, owners, tags and business capabilities. | Must | Given authorized representative fixtures and the required source data, the user can verify: provide global search over names, aliases, resource IDs, APIs, routes, repositories, owners, tags and business capabilities; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| DEV-02 | Return relevant results with type, environment, owner, last-seen and deep link to focused diagram. | Must | Given authorized representative fixtures and the required source data, the user can verify: return relevant results with type, environment, owner, last-seen and deep link to focused diagram; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| DEV-03 | Provide a service home page showing purpose, owner/team, contacts, repositories, deployments, APIs, dependencies, runbooks, approved operational documentation and architecture history. | Must | Given authorized representative fixtures and the required source data, the user can verify: provide a service home page showing purpose, owner/team, contacts, repositories, deployments, APIs, dependencies, runbooks, approved operational documentation and architecture history; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| DEV-04 | Support saved views, recently viewed items, favorites and shareable deep links with access control. | Must | Given authorized representative fixtures and the required source data, the user can verify: support saved views, recently viewed items, favorites and shareable deep links with access control; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| DEV-05 | Offer one-click copy for resource IDs, API endpoints, repository URLs and documentation references. | Must | Given authorized representative fixtures and the required source data, the user can verify: offer one-click copy for resource IDs, API endpoints, repository URLs and documentation references; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| DEV-06 | Provide ownership claim, correction and verification workflows with approval and audit. | Must | Given authorized representative fixtures and the required source data, the user can verify: provide ownership claim, correction and verification workflows with approval and audit; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| DEV-07 | Support keyboard-first command palette and fast navigation. | Should | Given authorized representative fixtures and the required source data, the user can verify: support keyboard-first command palette and fast navigation; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| DEV-08 | Provide onboarding journeys: start from a business process, trace to code and deployment. | Should | Given authorized representative fixtures and the required source data, the user can verify: provide onboarding journeys: start from a business process, trace to code and deployment; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |

## 5.4 Integration and dependency intelligence

| ID | Requirement / expected behavior | Priority | Verifiable acceptance expectation |
| --- | --- | --- | --- |
| DEP-01 | Model APIs and event contracts as first-class entities, not only labels on edges. | Must | Given authorized representative fixtures and the required source data, the user can verify: model APIs and event contracts as first-class entities, not only labels on edges; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| DEP-02 | Inspect endpoint/method, contract/version, configured producer/consumer, authentication, data classification and evidence where available; no traffic analytics required. | Must | Given authorized representative fixtures and the required source data, the user can verify: inspect endpoint/method, contract/version, configured producer/consumer, authentication, data classification and evidence where available; no traffic analytics required; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| DEP-03 | Trace upstream/downstream dependencies with direction, hop limits, environment filters and cycle-safe traversal. | Must | Given authorized representative fixtures and the required source data, the user can verify: trace upstream/downstream dependencies with direction, hop limits, environment filters and cycle-safe traversal; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| DEP-04 | Distinguish configuration-derived, contract-derived, manually verified and inferred links in UI and export; do not imply runtime observation. | Must | Given authorized representative fixtures and the required source data, the user can verify: distinguish configuration-derived, contract-derived, manually verified and inferred links in UI and export; do not imply runtime observation; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| DEP-05 | Offer business process and data lineage overlays where supporting sources exist. | Must | Given authorized representative fixtures and the required source data, the user can verify: offer business process and data lineage overlays where supporting sources exist; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| DEP-06 | Provide explainable impact reports listing candidate affected systems, paths, owners, criticality, confidence and unknowns. | Must | Given authorized representative fixtures and the required source data, the user can verify: provide explainable impact reports listing candidate affected systems, paths, owners, criticality, confidence and unknowns; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| DEP-07 | Avoid presenting potential blast radius as guaranteed failure impact; expose assumptions and missing evidence. | Must | Given authorized representative fixtures and the required source data, the user can verify: avoid presenting potential blast radius as guaranteed failure impact; expose assumptions and missing evidence; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| DEP-08 | Provide design-time dependency and business-criticality overlays without live health or telemetry integration. | Should | Given authorized representative fixtures and the required source data, the user can verify: provide design-time dependency and business-criticality overlays without live health or telemetry integration; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| DEP-09 | Detect stale contracts, unowned interfaces, unsupported API versions and dangling dependencies. | Should | Given authorized representative fixtures and the required source data, the user can verify: detect stale contracts, unowned interfaces, unsupported API versions and dangling dependencies; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |

## 5.5 Discovery, connectors and synchronization

| ID | Requirement / expected behavior | Priority | Verifiable acceptance expectation |
| --- | --- | --- | --- |
| CON-01 | Read Azure Resource Graph and approved Azure APIs for resource inventory and hierarchy. | Must | Given authorized representative fixtures and the required source data, the user can verify: read Azure Resource Graph and approved Azure APIs for resource inventory and hierarchy; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| CON-02 | Ingest APIM APIs, operations and policy metadata where permitted. | Must | Given authorized representative fixtures and the required source data, the user can verify: ingest APIM APIs, operations and policy metadata where permitted; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| CON-03 | Discover AKS namespaces, services, ingress, workloads and deployment metadata with least-privilege access. | Must | Given authorized representative fixtures and the required source data, the user can verify: discover AKS namespaces, services, ingress, workloads and deployment metadata with least-privilege access; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| CON-04 | Ingest repositories, IaC manifests, OpenAPI/AsyncAPI, deployment metadata and documentation from approved source control. | Must | Given authorized representative fixtures and the required source data, the user can verify: ingest repositories, IaC manifests, OpenAPI/AsyncAPI, deployment metadata and documentation from approved source control; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| CON-05 | Ingest messaging topology and configuration metadata (queues, topics, subscriptions, routing rules) without message payloads, runtime telemetry or distributed traces. | Must | Given authorized representative fixtures and the required source data, the user can verify: ingest messaging topology and configuration metadata (queues, topics, subscriptions, routing rules) without message payloads, runtime telemetry or distributed traces; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| CON-06 | Support scheduled incremental sync, manual refresh, connector health, rate limiting, retries and idempotency. | Must | Given authorized representative fixtures and the required source data, the user can verify: support scheduled incremental sync, manual refresh, connector health, rate limiting, retries and idempotency; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| CON-07 | Expose connector coverage, sync lag, permissions, errors and provenance at record level. | Must | Given authorized representative fixtures and the required source data, the user can verify: expose connector coverage, sync lag, permissions, errors and provenance at record level; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| CON-08 | Provide an import path for curated Visio/draw.io/CSV architecture inventory with validation. | Must | Given authorized representative fixtures and the required source data, the user can verify: provide an import path for curated Visio/draw.io/CSV architecture inventory with validation; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| CON-09 | Add CMDB, ITSM, identity directory, cloud billing exports and data catalog integrations; exclude production-application telemetry ingestion. | Should | Given authorized representative fixtures and the required source data, the user can verify: add CMDB, ITSM, identity directory, cloud billing exports and data catalog integrations; exclude production-application telemetry ingestion; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| CON-10 | Allow extensible connector SDK and event-driven synchronization. | Should | Given authorized representative fixtures and the required source data, the user can verify: allow extensible connector SDK and event-driven synchronization; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |

## 5.6 Architecture collaboration and governance

| ID | Requirement / expected behavior | Priority | Verifiable acceptance expectation |
| --- | --- | --- | --- |
| GOV-01 | Define roles: viewer, developer, editor, domain owner, architect reviewer, administrator and connector operator. | Must | Given authorized representative fixtures and the required source data, the user can verify: define roles: viewer, developer, editor, domain owner, architect reviewer, administrator and connector operator; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| GOV-02 | Provide draft/published diagram lifecycle, review/approval, version history and comparison. | Must | Given authorized representative fixtures and the required source data, the user can verify: provide draft/published diagram lifecycle, review/approval, version history and comparison; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| GOV-03 | Show ownership, verification status, exceptions, policy violations and freshness indicators. | Must | Given authorized representative fixtures and the required source data, the user can verify: show ownership, verification status, exceptions, policy violations and freshness indicators; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| GOV-04 | Maintain immutable audit events for access-sensitive edits, publication, approvals, imports and permission changes. | Must | Given authorized representative fixtures and the required source data, the user can verify: maintain immutable audit events for access-sensitive edits, publication, approvals, imports and permission changes; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| GOV-05 | Support architecture snapshots and diff of resources, relationships, ownership and deployment changes. | Must | Given authorized representative fixtures and the required source data, the user can verify: support architecture snapshots and diff of resources, relationships, ownership and deployment changes; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| GOV-06 | Attach diagrams and impact dossiers to ADRs, change tickets and release reviews. | Should | Given authorized representative fixtures and the required source data, the user can verify: attach diagrams and impact dossiers to ADRs, change tickets and release reviews; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| GOV-07 | Support design proposals versus discovered current state, with clear visual differentiation. | Should | Given authorized representative fixtures and the required source data, the user can verify: support design proposals versus discovered current state, with clear visual differentiation; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |

## 5.7 AI architecture assistant

| ID | Requirement / expected behavior | Priority | Verifiable acceptance expectation |
| --- | --- | --- | --- |
| AI-01 | Answer natural-language questions using authorized graph, catalog and documentation evidence. | Must | Given authorized representative fixtures and the required source data, the user can verify: answer natural-language questions using authorized graph, catalog and documentation evidence; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| AI-02 | Return cited paths, source timestamps and confidence; never fabricate nodes, edges, owners or production states. | Must | Given authorized representative fixtures and the required source data, the user can verify: return cited paths, source timestamps and confidence; never fabricate nodes, edges, owners or production states; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| AI-03 | Offer user-approved canvas actions: focus, expand, filter, highlight path and create draft view. | Must | Given authorized representative fixtures and the required source data, the user can verify: offer user-approved canvas actions: focus, expand, filter, highlight path and create draft view; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| AI-04 | Respect RBAC in retrieval, reasoning, response text and generated diagrams. | Must | Given authorized representative fixtures and the required source data, the user can verify: respect RBAC in retrieval, reasoning, response text and generated diagrams; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| AI-05 | Request clarification for ambiguous application names or environments and disclose coverage gaps. | Must | Given authorized representative fixtures and the required source data, the user can verify: request clarification for ambiguous application names or environments and disclose coverage gaps; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| AI-06 | Log prompts, retrieved references and actions under enterprise privacy controls. | Must | Given authorized representative fixtures and the required source data, the user can verify: log prompts, retrieved references and actions under enterprise privacy controls; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| AI-07 | Generate draft diagrams and architecture summaries from grounded data. | Should | Given authorized representative fixtures and the required source data, the user can verify: generate draft diagrams and architecture summaries from grounded data; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| AI-08 | Suggest ownership gaps, likely stale diagrams and candidate architecture review questions. | Should | Given authorized representative fixtures and the required source data, the user can verify: suggest ownership gaps, likely stale diagrams and candidate architecture review questions; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |

## 5.8 Developer knowledge hub and guided onboarding

| ID | Requirement / expected behavior | Priority | Verifiable acceptance expectation |
| --- | --- | --- | --- |
| KNOW-01 | Provide a unified developer homepage for each application/service with purpose, business capability, owner, support contacts, repositories, APIs, dependencies, environments, runbooks, ADRs and documentation. | Must | Given authorized representative fixtures and the required source data, the user can verify: provide a unified developer homepage for each application/service with purpose, business capability, owner, support contacts, repositories, APIs, dependencies, environments, runbooks, ADRs and documentation; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| KNOW-02 | Offer guided learning journeys (for example, “Understand Policy Issuance”) combining diagrams, relevant docs and key interfaces. | Should | Given authorized representative fixtures and the required source data, the user can verify: offer guided learning journeys (for example, “Understand Policy Issuance”) combining diagrams, relevant docs and key interfaces; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| KNOW-03 | Identify missing, stale or conflicting documentation and provide a review workflow. | Should | Given authorized representative fixtures and the required source data, the user can verify: identify missing, stale or conflicting documentation and provide a review workflow; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| KNOW-04 | Support deep links, bookmarks, recently visited systems, saved collections and role-aware recommendations. | Should | Given authorized representative fixtures and the required source data, the user can verify: support deep links, bookmarks, recently visited systems, saved collections and role-aware recommendations; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| KNOW-05 | Enable a “new joiner” orientation experience with curated reading order, glossary and system map. | Should | Given authorized representative fixtures and the required source data, the user can verify: enable a “new joiner” orientation experience with curated reading order, glossary and system map; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |

## 5.9 Design-time architecture playback and process journeys

**Scope guardrail:** Playback is an animation of *documented or modeled process flows*, not a replay of real requests. Atlas will not ingest traces, spans, application logs or live telemetry for this feature.

| ID | Requirement / expected behavior | Priority | Verifiable acceptance expectation |
| --- | --- | --- | --- |
| FLOW-01 | Model a business/technical journey as an ordered graph of steps, applications, APIs, queues, databases and human approvals. | Should | Given authorized representative fixtures and the required source data, the user can verify: model a business/technical journey as an ordered graph of steps, applications, APIs, queues, databases and human approvals; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| FLOW-02 | Animate the journey on the architecture canvas with play/pause, step, speed and jump-to-component controls. | Should | Given authorized representative fixtures and the required source data, the user can verify: animate the journey on the architecture canvas with play/pause, step, speed and jump-to-component controls; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| FLOW-03 | Label each step with protocol, input/output contract, sync/async behavior, error paths and source evidence where documented. | Should | Given authorized representative fixtures and the required source data, the user can verify: label each step with protocol, input/output contract, sync/async behavior, error paths and source evidence where documented; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| FLOW-04 | Support alternate paths and failure branches, explicitly marked as design scenarios rather than observed executions. | Could | Given authorized representative fixtures and the required source data, the user can verify: support alternate paths and failure branches, explicitly marked as design scenarios rather than observed executions; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| FLOW-05 | Export a static sequence diagram or shareable process walkthrough. | Should | Given authorized representative fixtures and the required source data, the user can verify: export a static sequence diagram or shareable process walkthrough; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |

## 5.10 Architecture time machine, drift and evolution

| ID | Requirement / expected behavior | Priority | Verifiable acceptance expectation |
| --- | --- | --- | --- |
| HIST-01 | Retain immutable, timestamped architecture snapshots with source and publication status. | Must | Given authorized representative fixtures and the required source data, the user can verify: retain immutable, timestamped architecture snapshots with source and publication status; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| HIST-02 | Compare any two snapshots for added/removed resources, connections, owners, contracts and deployment configuration. | Must | Given authorized representative fixtures and the required source data, the user can verify: compare any two snapshots for added/removed resources, connections, owners, contracts and deployment configuration; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| HIST-03 | Visually highlight changes on the same canvas and generate an explainable diff report. | Should | Given authorized representative fixtures and the required source data, the user can verify: visually highlight changes on the same canvas and generate an explainable diff report; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| HIST-04 | Compare an approved target-state design with imported/discovered configuration to identify drift and unapproved additions. | Should | Given authorized representative fixtures and the required source data, the user can verify: compare an approved target-state design with imported/discovered configuration to identify drift and unapproved additions; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| HIST-05 | Distinguish confirmed drift from incomplete discovery, permission gaps and connector lag. | Must | Given authorized representative fixtures and the required source data, the user can verify: distinguish confirmed drift from incomplete discovery, permission gaps and connector lag; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| HIST-06 | Support time-based browsing without overwriting curated historical diagrams. | Should | Given authorized representative fixtures and the required source data, the user can verify: support time-based browsing without overwriting curated historical diagrams; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |

## 5.11 Architecture sandbox and future-state planning

| ID | Requirement / expected behavior | Priority | Verifiable acceptance expectation |
| --- | --- | --- | --- |
| SAN-01 | Fork an existing architecture into an isolated proposal workspace without changing the published baseline. | Should | Given authorized representative fixtures and the required source data, the user can verify: fork an existing architecture into an isolated proposal workspace without changing the published baseline; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| SAN-02 | Add/remove components and dependencies; compare as-is versus to-be architecture side by side. | Should | Given authorized representative fixtures and the required source data, the user can verify: add/remove components and dependencies; compare as-is versus to-be architecture side by side; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| SAN-03 | Recalculate candidate downstream dependencies and governance checks for proposed changes, showing assumptions. | Should | Given authorized representative fixtures and the required source data, the user can verify: recalculate candidate downstream dependencies and governance checks for proposed changes, showing assumptions; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| SAN-04 | Attach rationale, ADRs, estimated cost assumptions and review comments to proposals. | Should | Given authorized representative fixtures and the required source data, the user can verify: attach rationale, ADRs, estimated cost assumptions and review comments to proposals; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| SAN-05 | Publish approved changes through an explicit review workflow; no direct Azure provisioning required. | Must | Given authorized representative fixtures and the required source data, the user can verify: publish approved changes through an explicit review workflow; no direct Azure provisioning required; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |

## 5.12 Security and data-flow intelligence

| ID | Requirement / expected behavior | Priority | Verifiable acceptance expectation |
| --- | --- | --- | --- |
| SEC-01 | Visualize trust zones, VNets/subnets, ingress/egress, public endpoints, identity boundaries and sensitive data classifications. | Should | Given authorized representative fixtures and the required source data, the user can verify: visualize trust zones, VNets/subnets, ingress/egress, public endpoints, identity boundaries and sensitive data classifications; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| SEC-02 | Map documented data flows across applications, stores, APIs and messaging endpoints. | Should | Given authorized representative fixtures and the required source data, the user can verify: map documented data flows across applications, stores, APIs and messaging endpoints; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| SEC-03 | Flag configuration-derived risks such as undocumented exposure, missing ownership or violations of approved architecture rules. | Should | Given authorized representative fixtures and the required source data, the user can verify: flag configuration-derived risks such as undocumented exposure, missing ownership or violations of approved architecture rules; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| SEC-04 | Generate a draft threat-model inventory (assets, trust boundaries, entry points, data flows) for human review. | Could | Given authorized representative fixtures and the required source data, the user can verify: generate a draft threat-model inventory (assets, trust boundaries, entry points, data flows) for human review; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| SEC-05 | Apply RBAC to security-sensitive metadata and exported diagrams. | Must | Given authorized representative fixtures and the required source data, the user can verify: apply RBAC to security-sensitive metadata and exported diagrams; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |

## 5.13 Cloud cost, ownership and sustainability insights

| ID | Requirement / expected behavior | Priority | Verifiable acceptance expectation |
| --- | --- | --- | --- |
| COST-01 | Import approved cloud billing/cost export data and map costs to resource, application, platform and business domain. | Should | Given authorized representative fixtures and the required source data, the user can verify: import approved cloud billing/cost export data and map costs to resource, application, platform and business domain; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| COST-02 | Support cost showback with transparent allocation rules for shared services. | Should | Given authorized representative fixtures and the required source data, the user can verify: support cost showback with transparent allocation rules for shared services; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| COST-03 | Show month-over-month cost trends and budget variance without requiring operational telemetry. | Could | Given authorized representative fixtures and the required source data, the user can verify: show month-over-month cost trends and budget variance without requiring operational telemetry; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| COST-04 | Identify orphaned/unowned resources and candidates for cost review; avoid declaring resources unused without adequate evidence. | Should | Given authorized representative fixtures and the required source data, the user can verify: identify orphaned/unowned resources and candidates for cost review; avoid declaring resources unused without adequate evidence; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| COST-05 | Provide scenario-based estimates for proposed architectures with explicit assumptions and uncertainty. | Could | Given authorized representative fixtures and the required source data, the user can verify: provide scenario-based estimates for proposed architectures with explicit assumptions and uncertainty; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |

## 5.14 Governed developer self-service

| ID | Requirement / expected behavior | Priority | Verifiable acceptance expectation |
| --- | --- | --- | --- |
| SELF-01 | Offer one-click links to approved repositories, API specifications, CI/CD systems, runbooks and architecture records. | Must | Given authorized representative fixtures and the required source data, the user can verify: offer one-click links to approved repositories, API specifications, CI/CD systems, runbooks and architecture records; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| SELF-02 | Support governed requests for API access, ownership updates, documentation corrections and architecture reviews. | Should | Given authorized representative fixtures and the required source data, the user can verify: support governed requests for API access, ownership updates, documentation corrections and architecture reviews; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| SELF-03 | Allow approved service templates or scaffolding requests only through explicit authorization and audit. | Could | Given authorized representative fixtures and the required source data, the user can verify: allow approved service templates or scaffolding requests only through explicit authorization and audit; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| SELF-04 | Make all actions permission-aware, auditable and reversible where applicable; no unapproved production mutations. | Must | Given authorized representative fixtures and the required source data, the user can verify: make all actions permission-aware, auditable and reversible where applicable; no unapproved production mutations; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |

## 5.15 Architecture quality scorecards

| ID | Requirement / expected behavior | Priority | Verifiable acceptance expectation |
| --- | --- | --- | --- |
| SCORE-01 | Define transparent, versioned standards for ownership, documentation, API lifecycle, architecture freshness, security boundaries and recovery readiness. | Should | Given authorized representative fixtures and the required source data, the user can verify: define transparent, versioned standards for ownership, documentation, API lifecycle, architecture freshness, security boundaries and recovery readiness; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| SCORE-02 | Score applications/domains using documented rules and linked evidence. | Should | Given authorized representative fixtures and the required source data, the user can verify: score applications/domains using documented rules and linked evidence; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| SCORE-03 | Show “unknown/not assessed” separately from “failed” to avoid penalizing missing source coverage as a verified defect. | Must | Given authorized representative fixtures and the required source data, the user can verify: show “unknown/not assessed” separately from “failed” to avoid penalizing missing source coverage as a verified defect; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| SCORE-04 | Assign remediation owners, exceptions, due dates and review status. | Should | Given authorized representative fixtures and the required source data, the user can verify: assign remediation owners, exceptions, due dates and review status; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| SCORE-05 | Provide domain/team trends and exportable scorecards, with configurable visibility. | Could | Given authorized representative fixtures and the required source data, the user can verify: provide domain/team trends and exportable scorecards, with configurable visibility; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |

## 5.16 Architecture assistant — expanded design intelligence

| ID | Requirement / expected behavior | Priority | Verifiable acceptance expectation |
| --- | --- | --- | --- |
| AIX-01 | Convert a natural-language architecture question into a focused, evidence-backed canvas view. | Should | Given authorized representative fixtures and the required source data, the user can verify: convert a natural-language architecture question into a focused, evidence-backed canvas view; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| AIX-02 | Draft ADRs, architecture summaries, design review checklists and impact dossiers from authorized graph/document evidence. | Should | Given authorized representative fixtures and the required source data, the user can verify: draft ADRs, architecture summaries, design review checklists and impact dossiers from authorized graph/document evidence; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| AIX-03 | Propose future-state design options and trade-offs in a sandbox without automatically publishing changes. | Could | Given authorized representative fixtures and the required source data, the user can verify: propose future-state design options and trade-offs in a sandbox without automatically publishing changes; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| AIX-04 | Provide source links, confidence and explicit unknowns for every generated architectural assertion. | Must | Given authorized representative fixtures and the required source data, the user can verify: provide source links, confidence and explicit unknowns for every generated architectural assertion; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| AIX-05 | Never perform PR analysis, ingest telemetry or claim observed transaction behavior. | Must | Given authorized representative fixtures and the required source data, the user can verify: never perform PR analysis, ingest telemetry or claim observed transaction behavior; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |

## 5.17 Product experience and extensibility enhancements

| ID | Requirement / expected behavior | Priority | Verifiable acceptance expectation |
| --- | --- | --- | --- |
| EXP-01 | Offer search-first command palette, keyboard shortcuts, recent history, pinned views and shareable deep links. | Must | Given authorized representative fixtures and the required source data, the user can verify: offer search-first command palette, keyboard shortcuts, recent history, pinned views and shareable deep links; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| EXP-02 | Provide responsive, accessible, high-performance diagram interactions with browser-based end-to-end tests. | Must | Given authorized representative fixtures and the required source data, the user can verify: provide responsive, accessible, high-performance diagram interactions with browser-based end-to-end tests; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| EXP-03 | Allow extensions for approved connectors, entity types, policies and developer portal widgets without compromising the core graph schema. | Should | Given authorized representative fixtures and the required source data, the user can verify: allow extensions for approved connectors, entity types, policies and developer portal widgets without compromising the core graph schema; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| EXP-04 | Support collaborative annotations, comments, diagram ownership and publication review. | Should | Given authorized representative fixtures and the required source data, the user can verify: support collaborative annotations, comments, diagram ownership and publication review; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |
| EXP-05 | Expose a clear distinction between curated, discovered, inferred and proposed architecture states. | Must | Given authorized representative fixtures and the required source data, the user can verify: expose a clear distinction between curated, discovered, inferred and proposed architecture states; missing/unauthorized inputs produce an explicit non-success state; save/reload and audit are checked where changes occur. |

## 5.18 Architecture X-Ray — contextual system exploration

**Business outcome:** A developer can understand the internal structure of an application while retaining its enterprise-level context. X-Ray is a visual projection of the architecture knowledge graph, not a separate editable copy of topology.

| Requirement ID | Requirement | Priority | Acceptance criteria |
| --- | --- | --- | --- |
| XRAY-01 | Expand an application in place to show logical services, APIs, data stores, messaging endpoints and infrastructure children without replacing the surrounding landscape. | Must | Given a collapsed application on a published landscape, expanding it reveals authorized children while adjacent applications and their context remain visible. |
| XRAY-02 | Provide selectable abstraction levels: business application, logical services, integration and Azure deployment. | Must | Switching levels preserves selected application and breadcrumb; displayed entities are traceable to the same canonical identifiers. |
| XRAY-03 | Support Azure hierarchy traversal through subscription, resource group, VNet/subnet, AKS cluster, namespace and service where evidence exists. | Must | User can traverse supported hierarchy and return to any ancestor without losing focus; missing levels are explicitly marked unknown. |
| XRAY-04 | Reveal and collapse cross-boundary dependencies with grouped connector counts and on-demand expansion. | Should | Bundled edges display counts and relationship types; expanding a bundle reveals constituent edges with direction and source evidence. |
| XRAY-05 | Preserve per-user and curated X-Ray layout state independently of topology data. | Should | Reloading a saved view restores expansion state and positions without creating or deleting graph entities. |
| XRAY-06 | Provide keyboard navigation, accessible node list, and controlled rendering budgets for large nested systems. | Must | Browser E2E tests verify mouse and keyboard expansion, no blank canvas, and graceful summary mode when node budget is exceeded. |
| XRAY-07 | Label discovered, curated, inferred and proposed elements distinctly at every level. | Must | Inspector and canvas legend expose status, evidence and freshness for each displayed element. |

**Acceptance scenario XRAY-S1:** From the enterprise landscape, a developer expands Policy Administration, drills into its AKS cluster and namespace, selects Policy API, inspects an APIM dependency, then collapses the application. The surrounding landscape remains available and no relationship metadata is altered.

## 5.19 Architecture Passport — authoritative component profile

**Business outcome:** Every important application, API, database, queue and infrastructure component has one deep-linkable, permission-aware profile that answers what it is, who owns it, how it connects and whether its documentation is trustworthy.

| Requirement ID | Requirement | Priority | Acceptance criteria |
| --- | --- | --- | --- |
| PASS-01 | Generate a canonical Passport page for every supported entity type with stable identifier, name, type, purpose, lifecycle, environment and classification. | Must | Every indexed entity has a stable deep link; unavailable attributes display “Not documented” rather than invented defaults. |
| PASS-02 | Display business owner, technical owner, support group, contact method and stewardship status. | Must | Owner fields show their authoritative source and last verification date; unowned entities are filterable. |
| PASS-03 | Show direct dependencies and integrations with typed direction, related contract and supporting evidence. | Must | Clicking a dependency opens the relationship inspector or connected Passport; access controls are preserved. |
| PASS-04 | Link to approved repositories, ADRs, API specifications, deployment diagrams, runbooks, onboarding material and service documentation. | Must | Links open correct authorized destinations; invalid links are flagged for correction rather than silently removed. |
| PASS-05 | Display environment-specific deployment locations, Azure resource references and last successful source synchronization where available. | Should | Switching Production/UAT changes environment-specific fields and never mixes their dependencies without explicit labeling. |
| PASS-06 | Support proposed corrections, owner attestation, audit history and approval before publishing authoritative changes. | Must | A non-owner can propose a correction but cannot silently overwrite approved metadata; all transitions are audited. |
| PASS-07 | Provide a completeness checklist with unknown, missing, verified and stale states. | Should | Missing evidence is not represented as a verified control failure; checklist items link to their underlying fields. |
| PASS-08 | Offer shareable links and embeddable references without bypassing authentication or leaking restricted metadata. | Should | Deep links resolve to the same entity for authorized users; unauthorized users receive no sensitive metadata. |

**Acceptance scenario PASS-S1:** A new Claims developer searches for Claims API, opens its Passport, identifies the owner, opens the API contract, sees upstream and downstream systems, and follows its approved runbook. Missing fields are visibly identified and correctable through a governed workflow.

## 5.20 Integration Contract Registry — APIs, events and data interfaces

**Business outcome:** Developers can discover what systems exchange, not merely which boxes are connected. Contracts are versioned, searchable and linked to architecture relationships.

| Requirement ID | Requirement | Priority | Acceptance criteria |
| --- | --- | --- | --- |
| ICR-01 | Ingest and catalog approved OpenAPI specifications, AsyncAPI specifications and explicitly documented file/data exchange contracts. | Must | Valid source documents produce searchable contract records with source URI, import status and immutable source revision; invalid documents return actionable validation errors. |
| ICR-02 | Model producers, consumers, operations/topics, endpoints, payload schemas, protocol, authentication and environment as first-class contract metadata. | Must | An authorized user can navigate from a connector to its contract and see direction, producer, consumer, interface and environment. |
| ICR-03 | Support contract version history, lifecycle state, deprecation notices and effective dates. | Must | At least two versions can coexist; users can identify current, deprecated and proposed versions without ambiguity. |
| ICR-04 | Provide semantic contract comparison, including additive and potentially breaking schema changes, based on published contract artifacts. | Should | Comparison highlights changed operations, fields, requiredness and schema types with deterministic findings and documented limits; it does not analyze pull requests. |
| ICR-05 | Search by API path, operation ID, event name, topic, schema field, owning system and consumer. | Must | Search results link to the exact contract version and related graph objects, respecting access controls. |
| ICR-06 | Reconcile contracts imported from APIM and approved documentation sources, flagging duplicates and mismatches. | Should | Conflicting definitions remain reviewable with provenance; no source silently overwrites another. |
| ICR-07 | Record data classification and sensitive fields at the contract level, with field-level visibility controls where required. | Must | Restricted payload details are hidden from unauthorized roles in UI, search, exports and AI responses. |
| ICR-08 | Support ownership, review status, contract stewardship and subscriptions to lifecycle notices. | Should | Owners can publish a deprecation notice and affected documented consumers are listed without relying on runtime telemetry. |
| ICR-09 | Export an authorized contract inventory and integration map for design reviews. | Should | Export includes version, ownership and evidence, and excludes restricted fields for unauthorized users. |

**Acceptance scenario ICR-S1:** A developer searches `POST /policies`, finds the documented operation and its OpenAPI version, sees APIM exposure and declared consumers, and compares v1 and v2. A removed required response field is flagged as a potentially breaking change based solely on specification differences.

## 5.21 Architecture Pattern Library — reusable approved designs

**Business outcome:** Teams start from consistent, enterprise-approved patterns rather than repeatedly inventing network, identity and integration architecture.

| Requirement ID | Requirement | Priority | Acceptance criteria |
| --- | --- | --- | --- |
| PAT-01 | Maintain a searchable library of versioned architecture patterns with title, intent, context, constraints, owner, status and applicability. | Must | A developer can find approved patterns by use case, technology, domain and architecture characteristics. |
| PAT-02 | Include reusable graph templates with Azure service roles, boundaries, required interfaces and configurable placeholders. | Must | Instantiating a pattern in a sandbox creates proposed entities and relationships, not deployed resources. |
| PAT-03 | Attach reference diagrams, ADRs, security controls, operational considerations and known trade-offs to each pattern. | Must | Pattern detail page shows approved references and design constraints with source links. |
| PAT-04 | Support configuration of pattern parameters, including environment, network boundary, identity approach and data classification. | Should | Invalid or missing required parameters block publication and explain which constraint is unmet. |
| PAT-05 | Support draft, reviewed, approved, deprecated and retired lifecycle states with versioned approvals. | Must | Only approved versions appear as recommended defaults; deprecated versions remain discoverable with warnings. |
| PAT-06 | Validate a proposed pattern instance against applicable architecture rules before review. | Should | Validation returns linked rule IDs, evidence and exceptions; no automatic production changes occur. |
| PAT-07 | Track adoption through documented pattern references in published architecture models. | Could | Usage counts distinguish explicit references from inferred similarity and do not depend on telemetry. |
| PAT-08 | Allow curated organization-specific and reusable general patterns without hard-coding a single Azure topology. | Should | Pattern maintainers can create variants and maintain version lineage without modifying historical approved instances. |

**Acceptance scenario PAT-S1:** An architect selects the approved “Private AKS API with APIM” pattern, sets Production and confidential-data parameters, previews the resulting architecture in a sandbox and requests approval. The published baseline and Azure tenant remain unchanged.

## 5.22 Architecture Rule Engine — transparent design governance

**Business outcome:** Architecture reviews become repeatable and explainable while preserving human judgment. Rules assess documented or discovered evidence; they must not fabricate runtime findings.

| Requirement ID | Requirement | Priority | Acceptance criteria |
| --- | --- | --- | --- |
| RULE-01 | Define versioned, machine-evaluable rules with ID, title, scope, severity, owner, rationale and required evidence. | Must | A rule administrator can create, test, publish and retire a rule; each evaluation records the exact rule version. |
| RULE-02 | Evaluate published, imported and proposed architectures against applicable rules without modifying the underlying resources. | Must | Evaluating a sandbox produces findings only and does not provision or mutate Azure infrastructure. |
| RULE-03 | Support initial rule categories for ownership, public exposure, approved authentication, network boundaries, data classification, contract documentation and lifecycle status. | Must | Representative fixtures for each category yield the expected pass, fail, unknown and not-applicable outcomes. |
| RULE-04 | Distinguish PASS, FAIL, UNKNOWN, NOT_APPLICABLE and EXEMPT with evidence and confidence. | Must | Missing data or insufficient connector permissions result in UNKNOWN, never an unsupported FAIL or PASS. |
| RULE-05 | Link each finding to affected graph entities, relevant rule text, evidence sources and recommended remediation. | Must | Clicking a finding highlights the exact architecture object and displays the evidence used. |
| RULE-06 | Support governed exceptions with justification, approver, scope, expiry and audit trail. | Must | Expired exceptions cease to suppress findings; only authorized reviewers may approve exemptions. |
| RULE-07 | Run rule checks on demand and after approved architecture snapshot or connector-sync events, with bounded workloads. | Should | Evaluation jobs are idempotent, report completion status and never require operational telemetry or PR events. |
| RULE-08 | Produce review-ready reports grouped by domain, application, severity and rule, with access-controlled export. | Should | Export totals reconcile to the displayed filtered findings and honor data-access restrictions. |
| RULE-09 | Offer a safe rule test harness with synthetic fixtures and expected outcomes before publication. | Must | Rule publication requires passing fixtures and authorization; regressions are visible in version history. |
| RULE-10 | Keep the rule engine deterministic for authoritative pass/fail judgments; AI may draft explanations but not override evidence-based results. | Must | Given identical graph snapshot, rule version and configuration, evaluations produce identical results. |

**Acceptance scenario RULE-S1:** A security architect evaluates a proposed production design containing a publicly reachable database and an application without a technical owner. The engine flags confirmed public exposure and missing ownership with entity-level evidence, while an unassessed encryption attribute is UNKNOWN. The reviewer can record a time-bound approved exception with an audit trail.

### 5.23 Cross-feature consistency and exclusions

- All five capabilities operate on canonical graph entity IDs and access-aware relationships; no parallel source of truth is created by the Passport, X-Ray or Contract Registry.
- Passport metadata, contract revisions, patterns and rule evaluations must retain source provenance, freshness, ownership and immutable audit history where appropriate.
- The X-Ray view and pattern instantiation must use the same layout persistence and review boundaries as the Architecture Studio and Sandbox.
- Integration contracts are sourced from documented specifications, APIM metadata or approved configuration artifacts, **not** production traffic observation.
- Architecture Rule Engine assessments use documented/discovered configuration and approved metadata; no live telemetry, tracing, PR hooks or PR impact analysis are introduced.
- New screens and workflows must pass automated real-browser click, double-click, keyboard, navigation, save/reload and export tests. Static HTML preview rendering alone is not acceptance evidence.


## 5.23–5.38 Integrated enterprise modeling and adoption requirements
**Consolidation rule:** These are extensions of the canonical graph, Studio, Explore and Intelligence capabilities already defined above. They do not create separate databases or duplicate Passports, search, governance or diagram editors. Requirement IDs below are authoritative additions; existing requirements remain applicable. **Priority P0** = essential foundation, **P1** = high-value planned release, **P2** = later enhancement. Must/Should/Could express requirement strength within each feature.
### Three integrated product experiences

| Experience | Primary audience | Principal workflows |
| --- | --- | --- |
| **Atlas Studio** | Enterprise/solution architects | Visual modeling, C4-inspired projections, architecture-as-code, alternatives, approved patterns, design review, storytelling |
| **Atlas Explore** | Developers and platform engineers | Search, Passport, X-Ray, contracts, documented lineage, decisions, favorites, command palette |
| **Atlas Intelligence** | Architecture governance, security and business teams | Business capability maps, reconciliation, rule evaluation, source trust, data classification, completeness and governed corrections |

All experiences use the same graph IDs, access controls, evidence and versioning. Users switch experience without changing product or losing context.
### 5.23 Canonical multi-level architecture modeling

**Priority:** P0. **Expected outcome:** Architects and developers navigate one consistent architecture from business capabilities through software systems, logical services and physical deployment. C4-inspired views are supported without enforcing a one-to-one C4 taxonomy on Azure resources.

| Requirement ID | Strength | Functional requirement | Acceptance criteria |
| --- | --- | --- | --- |
| MOD-01 | Define a versioned type taxonomy for capability, domain, application, system, container, component, API, data asset, deployment and cloud resource. | Must | An administrator can inspect permitted types, required attributes and allowed relationships; existing IDs survive taxonomy upgrades. |
| MOD-02 | Support context, system, container/component and deployment projections over the same canonical graph. | Must | Changing view level preserves canonical identities and correctly represents cross-level relationships. |
| MOD-03 | Validate parent-child and relationship-type rules, including multi-deployment logical services. | Must | Invalid parentage is rejected with a readable explanation; one logical service may map to multiple deployments. |
| MOD-04 | Support aliases, environment-qualified identities and lifecycle states. | Must | Aliases resolve to one canonical ID; Production and UAT deployments remain distinct. |
| MOD-05 | Maintain explicit view provenance, authorship and revision independent of graph facts. | Must | Repositioning a node does not change topology or entity provenance. |
| MOD-06 | Support cross-view navigation and scoped access control. | Must | Selecting an object in one view opens its matching Passport in another without leaking restricted descendants. |

### 5.24 Business capability mapping

**Priority:** P0. **Expected outcome:** Nontechnical stakeholders can trace business capabilities and journeys to supporting applications, contracts, datasets and cloud infrastructure.

| Requirement ID | Strength | Functional requirement | Acceptance criteria |
| --- | --- | --- | --- |
| BCM-01 | Model capability hierarchy, business owner, criticality, lifecycle and supporting applications. | Must | A capability page lists direct and indirect supporting applications with evidence. |
| BCM-02 | Provide business-first heatmaps and capability-to-technology drill-down. | Must | A user selects Claims Settlement and reaches documented systems and interfaces without manually searching resource IDs. |
| BCM-03 | Distinguish direct support, enabling dependency and inferred associations. | Must | Legend and inspector display relationship type and evidence; inferred associations are never presented as confirmed. |
| BCM-04 | Allow curated capability maps with ownership and approval. | Must | Draft changes require review and published revisions are auditable. |
| BCM-05 | Filter by business domain, region, environment, criticality and ownership. | Should | Combined filters produce consistent counts and a clear empty state. |
| BCM-06 | Support capability gap and redundancy review without automatic recommendations being treated as facts. | Should | Potential duplicate support is labeled a candidate for human review. |

### 5.25 Intelligent source reconciliation

**Priority:** P0. **Expected outcome:** Multiple connectors and curated sources resolve to one trustworthy enterprise model instead of duplicate or conflicting objects.

| Requirement ID | Strength | Functional requirement | Acceptance criteria |
| --- | --- | --- | --- |
| REC-01 | Implement source-specific stable identifiers, alias matching and scoped identity rules. | Must | The same Azure resource reported by Resource Graph and APIM resolves to one canonical entity when identity evidence matches. |
| REC-02 | Provide deterministic matching precedence and configurable conflict policy. | Must | Same inputs and policy yield the same merge outcome; no silent overwrite of conflicting owners. |
| REC-03 | Create a reconciliation inbox for ambiguous matches, conflicting fields and orphaned relationships. | Must | Steward can inspect both evidence sources, approve merge/split or defer with reason. |
| REC-04 | Retain source observations, timestamps, field-level provenance and audit history. | Must | Inspector exposes which source supplied each contested value and when. |
| REC-05 | Support idempotent incremental sync, deletions/tombstones and reappearance. | Must | Reprocessing a source snapshot creates no duplicates; missing resource is marked stale before removal under policy. |
| REC-06 | Expose connector coverage, unknowns and reconciliation backlog. | Must | Source dashboard distinguishes sync failure, missing permissions, unresolved conflicts and verified data. |
| REC-07 | Allow reversible merge decisions and protected manual overrides. | Should | A steward can reverse an erroneous merge without losing source history. |

### 5.26 Architecture-as-Code

**Priority:** P1. **Expected outcome:** Teams can describe architecture in validated declarative YAML/JSON while keeping Atlas the governed visual workspace.

| Requirement ID | Strength | Functional requirement | Acceptance criteria |
| --- | --- | --- | --- |
| AAC-01 | Publish versioned schemas for entities, relationships, environment scope and metadata. | Must | Valid YAML and JSON fixtures import to equivalent draft graph objects. |
| AAC-02 | Support dry-run import with preview of additions, updates, removals and conflicts. | Must | No published entity changes until authorized confirmation and approval. |
| AAC-03 | Provide schema validation and precise line/path errors. | Must | Malformed relationship references identify the offending field and preserve current draft. |
| AAC-04 | Export authorized architecture snapshots to stable, deterministic YAML/JSON. | Must | Re-export of unchanged snapshot is semantically equivalent and excludes restricted metadata. |
| AAC-05 | Support explicit merge rules between declarative, discovered and curated sources. | Must | Import cannot silently override authoritative cloud identity or verified owner. |
| AAC-06 | Document local CLI/API import workflow without requiring repository hooks or PR integration. | Should | Developer can validate a local architecture file and upload via UI or authenticated API. |

### 5.27 Architecture alternatives, branching and merging

**Priority:** P1. **Expected outcome:** Architects explore future states safely, compare options and promote approved designs without confusing proposals with deployed reality.

| Requirement ID | Strength | Functional requirement | Acceptance criteria |
| --- | --- | --- | --- |
| BRN-01 | Create a named draft branch from a pinned published architecture snapshot. | Must | Branch stores baseline revision and never mutates published inventory. |
| BRN-02 | Compare two branches or a branch against baseline at entity, relationship and layout levels. | Must | Diff distinguishes topology changes from visual layout changes. |
| BRN-03 | Detect concurrent changes and show merge conflicts with source details. | Must | Conflicting relationship deletion/update requires explicit resolution. |
| BRN-04 | Require authorization and rule checks before promoting an approved design. | Must | Promotion records approver, decision and exact resulting revision. |
| BRN-05 | Allow discard, archive and restore of draft branches. | Should | Archived alternatives remain auditable and are not shown as deployed. |
| BRN-06 | Provide a readable side-by-side comparison and rationale log. | Should | Reviewer can inspect trade-offs, assumptions and comments without switching to external slides. |

### 5.28 Contextual decisions and architecture knowledge

**Priority:** P1. **Expected outcome:** Engineers learn why a design exists, not only what is connected.

| Requirement ID | Strength | Functional requirement | Acceptance criteria |
| --- | --- | --- | --- |
| ADR-01 | Attach versioned ADRs, rationale, trade-offs, review notes and approved documents to entities and relationships. | Must | Passport shows linked decisions with author, status, date and source. |
| ADR-02 | Support searchable decision status: proposed, accepted, superseded and retired. | Must | Superseded ADR clearly links to replacement and does not appear current. |
| ADR-03 | Allow comments and suggested corrections without changing approved source records. | Must | Feedback creates a reviewable request with attribution and audit. |
| ADR-04 | Show context-specific knowledge when inspecting a component or dependency. | Should | User can navigate from a selected connector to the ADR justifying it. |
| ADR-05 | Enforce document-level permissions in search, summaries and exports. | Must | Restricted decision content is not leaked by previews or AI answers. |

### 5.29 Documented data lineage and information movement

**Priority:** P1. **Expected outcome:** Users can follow known business data movement using documented contracts and curated mappings, not observed traffic.

| Requirement ID | Strength | Functional requirement | Acceptance criteria |
| --- | --- | --- | --- |
| LIN-01 | Model dataset, data domain, classification, producer, transformation and consumer relationships. | Must | A dataset page shows documented upstream and downstream flow with evidence. |
| LIN-02 | Support system-level and dataset-level lineage as initial scope. | Must | User can trace Customer Profile from onboarding to policy systems with explicitly documented hops. |
| LIN-03 | Represent transformations, data residency, retention classification and cross-boundary movement where known. | Should | Unknown transformation details remain unknown, not fabricated. |
| LIN-04 | Provide lineage impact exploration with bounded traversal and cycle handling. | Must | Cycles are shown safely and traversal scope is visible. |
| LIN-05 | Link lineage edges to approved schemas, interface contracts or curated documentation. | Must | Every confirmed edge opens its evidence source. |
| LIN-06 | Protect sensitive datasets and field names in all views and exports. | Must | Unauthorized users cannot infer restricted data via search or counts. |
| LIN-07 | Defer column-level lineage unless reliable metadata sources are available. | Could | UI explicitly labels granularity and does not imply field-level completeness. |

### 5.30 Connector SDK and extension framework

**Priority:** P1. **Expected outcome:** Platform teams can safely onboard legacy, on-prem and non-Azure architecture sources.

| Requirement ID | Strength | Functional requirement | Acceptance criteria |
| --- | --- | --- | --- |
| SDK-01 | Publish connector contracts for entities, relationships, identity keys, provenance, sync cursors and errors. | Must | Reference connector passes contract conformance suite. |
| SDK-02 | Support least-privilege connector credentials, secret rotation and scoped source permissions. | Must | Credentials never appear in logs, exported graph or UI. |
| SDK-03 | Provide dry-run preview, schema mapping, incremental sync and retry semantics. | Must | Failed sync does not erase last-known graph; replay is idempotent. |
| SDK-04 | Expose source health, sync freshness, field coverage and reconciliation outcomes. | Must | Admin distinguishes connector error from empty source data. |
| SDK-05 | Provide sandboxed validation and version compatibility for connector packages. | Should | Incompatible package is blocked before activation with diagnostic reason. |
| SDK-06 | Support curated legacy-system connectors without requiring cloud resource IDs. | Must | Stable organization-defined identities prevent duplicates across reimports. |

### 5.31 Architecture subscriptions and change notices

**Priority:** P2. **Expected outcome:** Users follow relevant architecture objects and receive useful, low-noise notifications about approved information changes.

| Requirement ID | Strength | Functional requirement | Acceptance criteria |
| --- | --- | --- | --- |
| NTF-01 | Subscribe to applications, contracts, patterns, domains and owner changes. | Should | User can follow/unfollow and see subscriptions. |
| NTF-02 | Generate notices for approved revision, deprecation, ownership or contract changes. | Should | Notice links to exact revision diff and evidence. |
| NTF-03 | Provide digest, mute and notification preferences. | Should | Muted items do not generate user-visible notifications. |
| NTF-04 | Deduplicate repeated connector observations and respect permissions. | Must | Idempotent re-sync produces no duplicate alert; restricted data remains hidden. |
| NTF-05 | Exclude PR activity, runtime telemetry and production incident alerts. | Must | Notification source catalog contains no PR or telemetry triggers. |

### 5.32 Collaborative architecture review

**Priority:** P2. **Expected outcome:** Teams review designs together without losing authorship, control or trust.

| Requirement ID | Strength | Functional requirement | Acceptance criteria |
| --- | --- | --- | --- |
| COL-01 | Attach threaded comments and mentions to graph entities, connectors and draft revisions. | Should | Comment deep link reopens correct object and revision. |
| COL-02 | Provide reviewer assignments, resolution status and audit trail. | Should | Reviewer can resolve a thread without changing published topology. |
| COL-03 | Show presence and editing ownership in shared drafts. | Could | Users see who is viewing/editing without implying live co-editing. |
| COL-04 | Support simultaneous editing only with explicit conflict-safe concurrency semantics. | Could | Two users editing same node cannot silently overwrite each other. |
| COL-05 | Keep architecture reviews independent from source-code PR workflows. | Must | Review screen contains no PR approvals or code-diff features. |

### 5.33 Command palette and personal workspace

**Priority:** P1. **Expected outcome:** Developers and architects reach useful information quickly without memorizing navigation.

| Requirement ID | Strength | Functional requirement | Acceptance criteria |
| --- | --- | --- | --- |
| CMD-01 | Provide Cmd/Ctrl+K command palette for search, navigation and permitted actions. | Must | Keyboard-only user finds a system, opens Passport and returns without mouse. |
| CMD-02 | Offer recent, favorite, pinned views and user-specific saved filters. | Must | Preferences persist without modifying shared diagrams. |
| CMD-03 | Use context-aware actions for selected entities and current role. | Must | Unauthorized actions are absent or clearly disabled. |
| CMD-04 | Provide command aliases and fuzzy matching with accessible result announcements. | Should | Synonym search returns type-labeled results and correct deep links. |
| CMD-05 | Show useful home dashboard with assigned stewardship tasks and recently viewed objects. | Should | Empty first-use state offers safe sample content and onboarding. |

### 5.34 Architecture storytelling and presentation

**Priority:** P1. **Expected outcome:** Architects communicate complex designs through sequenced, presentation-ready views.

| Requirement ID | Strength | Functional requirement | Acceptance criteria |
| --- | --- | --- | --- |
| STORY-01 | Create a story as ordered scenes referencing saved graph view state. | Must | Each scene stores selection, focus, filters, visibility and narration. |
| STORY-02 | Step through scenes with keyboard controls and reduced-motion support. | Must | Scene transitions never change topology or hide critical evidence without explanation. |
| STORY-03 | Support shareable presentation links and access-controlled export. | Must | Recipient sees same authorized scenes; restricted entities are redacted. |
| STORY-04 | Provide annotation, callout and speaker-note support. | Should | Notes persist with story version and are not mistaken for graph facts. |
| STORY-05 | Preserve version and evidence context in exported story. | Must | Export identifies graph snapshot and author. |

### 5.35 Legacy diagram import and migration

**Priority:** P1. **Expected outcome:** Architects can bring existing Visio and draw.io work into Atlas without redrawing everything or falsely certifying the imported topology.

| Requirement ID | Strength | Functional requirement | Acceptance criteria |
| --- | --- | --- | --- |
| IMP-01 | Accept supported draw.io XML and documented Visio interchange/export formats through staged import. | Must | Importer reports exact supported file types and unsupported features before conversion. |
| IMP-02 | Preview shapes, connectors, group boundaries and icon mappings before applying. | Must | User can confirm each mapping; unmatched shapes remain clearly marked. |
| IMP-03 | Separate visual-only import from canonical graph reconciliation. | Must | Import does not create verified infrastructure dependencies solely from drawn lines. |
| IMP-04 | Detect duplicates against existing graph and route ambiguous matches to steward review. | Must | Preview shows proposed match, confidence and evidence; no silent merge. |
| IMP-05 | Preserve original file, import report and traceable source references. | Must | Auditor can identify original drawing and approved changes. |
| IMP-06 | Allow partial import, rollback and clear error recovery. | Should | Failed mapping does not corrupt published graph or existing layouts. |

### 5.36 Architecture feedback and correction loop

**Priority:** P1. **Expected outcome:** Every user can flag incorrect or incomplete architecture information and help improve its accuracy.

| Requirement ID | Strength | Functional requirement | Acceptance criteria |
| --- | --- | --- | --- |
| FBK-01 | Provide Report issue / Suggest correction on Passport, canvas node, edge and contract. | Must | Submission references canonical entity, current revision and source field. |
| FBK-02 | Route requests to owner or steward with status, severity and comment history. | Must | Reporter can track open, triaged, approved, rejected and resolved states. |
| FBK-03 | Support evidence attachments and proposed replacement values. | Should | Reviewer sees old value, proposed value and supporting source. |
| FBK-04 | Require approval before authoritative metadata or relationships change. | Must | Unapproved suggestions never appear as verified facts. |
| FBK-05 | Provide correction backlog and quality trends by domain. | Should | Counts distinguish missing data, stale data and confirmed errors. |

### 5.37 Cross-feature design rules and acceptance expectations

1. **Identity and hierarchy:** C4-style levels, business capabilities, Passport, X-Ray, lineage and imported drawings reference the same canonical graph entities and permitted relationship types.
2. **Truth boundaries:** Discovered Azure configuration, imported architecture-as-code, manual drawings and proposed designs have separate source types and trust states. A drawn arrow is not evidence that an integration is live.
3. **Architecture changes are not code PRs:** Branching and review apply only to Atlas architecture models. There are no repository pull-request hooks, code-review workflows or PR impact analysis.
4. **No runtime telemetry:** Lineage, integration mapping, architecture stories, drift and change notices use configuration, approved contracts and curated records, never traces, metrics or production traffic.
5. **Governed promotion:** Drafts, imported files and suggestions do not modify published facts until authorized validation and approval.
6. **Bright design remains mandatory:** All new capabilities inherit the bright visual tokens, readable nested graph, accessible keyboard interaction and no-dead-controls rule from the UX companion.
7. **Meaningful uncertainty:** All graph-derived recommendations and rule findings expose evidence, unknowns, source freshness and scope.
8. **Scale:** Never render thousands of ungrouped labels; large capability maps, imported diagrams and lineage views must use bounded projections, progressive disclosure and filtered traversal.

### 5.38 New cross-persona acceptance journeys

| Journey ID | Persona | Scenario and expected behavior |
| --- | --- | --- |
| J-BCM-01 | Business leader | Search “Claims Settlement” → open capability map → inspect supporting apps and integration paths → share view. Every connection has a known source or is explicitly unknown. |
| J-MOD-01 | Enterprise architect | Open enterprise context → switch to application/container/deployment views → select same logical service across views. Canonical identity remains stable. |
| J-REC-01 | Platform steward | Import overlapping APIM/Azure data → inspect candidate duplicate → review source evidence → merge → re-sync. No duplicate reappears; merge is auditable. |
| J-AAC-01 | Developer | Upload valid YAML design → preview diff → resolve ambiguous mappings → save draft → export same design. Published architecture remains unchanged. |
| J-BRN-01 | Solution architect | Branch published baseline → model alternative → compare topology/layout diffs → request approval → promote. Exact approved revision is retained. |
| J-LIN-01 | Data architect | Search Customer Profile dataset → follow documented onboarding-to-policy lineage → inspect schema evidence. Unknown hops remain unknown. |
| J-IMP-01 | Architect | Import draw.io diagram → map Azure icons and edges → reject unsupported connections → publish approved view. Imported lines are not marked verified automatically. |
| J-FBK-01 | Developer | Flag wrong API owner → attach documentation → owner reviews and approves → Passport updates with audit and optional subscriber notice. |
| J-STORY-01 | Architect | Build four architecture scenes → present by keyboard → export. Scene transitions are readable, preserve source snapshot and respect access rights. |

## 6. High-value end-to-end journeys

### J01: Developer onboarding

Flow: Search “Policy Issuance” → inspect service home → view API contracts → follow dependency path to APIM, AKS and database → open repo/runbook → save view.

Acceptance: Developer reaches a usable service overview in three interactions from search; all links are valid or clearly unavailable.

### J02: APIM change impact

Flow: Select API operation → choose environment → trace verified consumers and transitive candidates → review owners, confidence and unknowns → export change dossier.

Acceptance: Every reported dependency includes path and provenance; unverified dependencies are labeled.

### J03: Production incident

Flow: Select an Azure Service Bus namespace → inspect documented producers/consumers and configured subscriptions → identify owners, critical business processes and runbooks.

Acceptance: Graph remains usable during partial connector outages; dependency evidence and last configuration sync are timestamped.

### J04: Architecture design review

Flow: Open published current state → create proposal branch → add/move components and relationships → compare → comment → request approval → publish.

Acceptance: Manual layout survives graph refresh; review history and approvals are preserved.

### J05: Security review

Flow: Filter customer-data flows → inspect API authentication, private endpoints, cross-network routes and data stores → flag evidence gaps.

Acceptance: Sensitive metadata obeys authorization; reports distinguish verified versus inferred flows.

### J06: Cloud platform discovery

Flow: Open subscription → resource group → VNet → AKS → namespace → service; search a resource ID and focus it in the correct hierarchy.

Acceptance: Hierarchy is correct and searchable even when thousands of resources exist.

## 7. Information architecture and data model

| Entity | Key attributes / relationships |
| --- | --- |
| Business capability | Stable ID, hierarchy, owner, domain, criticality; supported by applications and business journeys |
| Application / service | ID, aliases, purpose, owner, lifecycle, environment, repositories, runbooks |
| Cloud resource | Provider ID, type, subscription, resource group, region, tags, parent hierarchy |
| API / event contract | Method/path or topic, version, auth, schema, publisher, consumer, classification |
| Relationship | Source, target, type, direction, environment, provenance, confidence, last seen |
| Diagram / view | Version, owner, scope, layout, filters, visibility, annotations, published state |
| Evidence | Connector, reference URI/ID, observation time, confidence, access classification |
| Snapshot / change | Graph revision, documented/discovered changes, approvals, associated releases or tickets |
| Architecture type/schema | Versioned type ID, permitted parent-child hierarchy, relationship constraints and required metadata |
| Source observation / reconciliation | Source ID, external key, canonical match, field-level evidence, conflict status, steward decision and sync cursor |
| Architecture branch / alternative | Baseline revision, proposed entity/edge changes, layout delta, reviewers, promotion status and merge resolution |
| Decision / ADR | Decision ID, status, author, rationale, supersession link and related graph entities |
| Dataset / lineage | Dataset ID, classification, producer/consumer, transformation reference, granularity and evidence |
| Pattern instance / declarative import | Pattern or file revision, parameters, mapping decisions, proposed graph changes and validation results |
| Story / scene | Story ID, ordered scene, snapshot, view state, annotations, author and access scope |
| Feedback / subscription | Target canonical ID, reporter/follower, change type, status, steward decision and notification preference |

Architecture principle: maintain a canonical topology graph plus a separate presentation/layout model. Use stable identifiers, scoped access controls and explicit provenance. The storage technology (e.g., PostgreSQL plus graph projections, or a graph database) is an architecture decision, not a business requirement.

## 8. Non-functional requirements and engineering quality gates

| Category | Proposed requirement / acceptance |
| --- | --- |
| Scale | Pilot: 10,000 resources / 100,000 relationships; design for 100,000+ resources and 1,000,000+ relationships via progressive loading. |
| Rendering | Default view first meaningful render within 2 seconds at p75 on approved desktop baseline; pan/zoom target 45–60 FPS for typical curated views. |
| Interaction | No blocking main-thread layout; click/selection, drill-down and inspector actions covered by automated browser E2E tests. |
| Search | p95 under 1.5 seconds for indexed common queries under agreed pilot load. |
| Graph queries | p95 under 3 seconds for bounded 1–3 hop traces on pilot dataset; deeper traversals async/progressive. |
| Availability | Pilot SLO proposal 99.5%; production target and disaster recovery objectives to be approved. |
| Security | Enterprise SSO, RBAC/ABAC as needed, least-privilege connectors, encryption in transit/at rest, audit, secrets management. |
| Privacy | Data minimization, redaction of secrets/PII, classification-aware search and AI grounding. |
| Resilience | Connector failures must not blank the canvas; show last-known-good snapshot and freshness warnings. |
| Accessibility | Keyboard-operable core functions, visible focus, accessible alternatives to canvas, WCAG 2.2 AA target. |
| Portability | Modern approved Chrome/Edge/Safari; no dependence on chat/file preview execution; browser-tested deployment URL. |
| Observability | Instrument client errors, render time, graph-query latency, sync lag, connector failures and feature adoption. |
| Quality | Unit, integration, contract, accessibility, performance, security and Playwright/Cypress E2E release gates. |

## 9. UX specification and visual quality bar

- Bright, restrained Azure-native aesthetic with generous whitespace, crisp service labels, meaningful colors and official SVG icon assets.
- Containers visually distinguish business/application scope from Azure infrastructure hierarchy; nesting must remain legible at every supported zoom.
- Connection routing must not cut through node labels or obscure service icons; edge bundling and filters manage density.
- Every diagram must have a title, legend, environment, timestamp/freshness and clear current/proposed state indicator.
- The default landing view should be a polished, useful curated landscape—not an unstyled random graph or 1,000 simultaneously expanded cards.
- Offer a high-quality inspector with overview, dependencies, contracts, deployments, ownership, documentation, evidence and change tabs.
- Loading, empty, error, stale and permission-denied states must be intentionally designed; never show a blank canvas without explanation.
- Diagram editor must have direct manipulation, undo/redo, autosave status, accessible toolbar and keyboard shortcuts.
## 10. Security, governance and risk

- Threat model graph enumeration, cross-tenant leakage, prompt injection via ingested documents, unsafe external links, secrets in imported configuration and connector credential compromise.
- Use read-only service principals or managed identities by default; connector permissions reviewed per source.
- Enforce authorization on graph traversal and search, not only on UI components; prevent inferred relationships from leaking restricted entity names.
- Record source classification and retention requirements; support deletion/expiry and legal hold where applicable.
- Human approval required for publishing authoritative architecture, changing ownership and accepting inferred links.
- Define data ownership, stewardship, escalation and dispute resolution before broad rollout.
## 11. Integration landscape

| System | Candidate data | Important caveat |
| --- | --- | --- |
| Azure Resource Graph / ARM | Inventory and resource hierarchy | Does not prove runtime dependencies |
| Azure API Management | APIs, operations, policies, products | Actual consumers may be unknown without runtime evidence; label unknowns |
| AKS / Kubernetes | Workloads, services, ingress, namespace | Configured routing does not establish actual runtime traffic |
| GitHub / Azure DevOps (read-only repository metadata) | Repos, IaC, OpenAPI, ownership | No pull-request processing; declared intent may differ from deployment |
| Service Bus / Event Hubs | Namespaces, topics, queues, subscriptions | Publisher/consumer mapping may be incomplete |
| CMDB / ITSM | Ownership, incidents, changes | Data quality and freshness vary |
| Identity / directory | Teams and owner contacts | Group membership and privacy controls apply |
| Data catalog / lineage | Datasets, sensitivity and flows | Lineage coverage depends on source integrations |

## 12. Release plan and prioritization

| Phase | Outcome | Included capabilities | Exit gate |
| --- | --- | --- | --- |
| 0 — Discovery / design | Validate lovable UX and canonical model | Personas, C4-inspired type taxonomy, business capability sample, source authority matrix, bright interactive prototype | Architects and developers complete pilot journeys; taxonomy and identity rules reviewed |
| 1 — Studio + Explore foundation | Beautiful, useful daily architecture workspace | Official Azure icons, canvas editor, semantic zoom, search, command palette, Passport, X-Ray, curated capability maps, personal views, saved layouts, exports | Real-browser E2E, save/reload and accessibility gates; users locate owner and dependencies |
| 2 — Trustworthy living graph | Reliable and extensible architecture data | Azure/APIM/AKS discovery, deterministic reconciliation, steward inbox, field provenance, connector SDK baseline, Contract Registry, correction workflow | Idempotent sync and duplicate/conflict golden tests pass; freshness/coverage visible |
| 3 — Architecture design productivity | Design, reuse and explain | Architecture-as-Code import/export, governed Visio/draw.io migration, architecture branching, approved patterns, ADR knowledge, storytelling and design-time playback | Draft/published isolation, merge, import preview and presentation tests pass |
| 4 — Intelligence and data context | Explainable enterprise understanding | Documented lineage, rule engine, drift, time machine, impact exploration, AI assistant, quality scorecards, advanced business lenses | Evidence/unknown-state golden tests, security review and usability sign-off |
| 5 — Enterprise collaboration and scale | Broad governed adoption | Shared reviews, notifications, simultaneous editing if justified, advanced sandbox, security/data-flow, cloud cost showback, self-service | Concurrency, authorization, stewardship, scale and accessibility acceptance |

## 12.1 Explicit exclusions carried through every phase

Atlas will **not** implement pull-request processing or pull-request impact checks, distributed tracing, production telemetry ingestion, live health dashboards, request/span replay or traffic analytics. Product-internal diagnostics (e.g. error reporting and connector sync status) remain necessary for reliable operation and are not user-facing telemetry integrations. Architecture playback uses authored or imported design-time process steps only.

## 13. MVP definition and exclusions

MVP should solve one realistic vertical slice extremely well: Digital Channels → APIM → New Business → Policy Administration → Claims, including a fully explorable Azure deployment view, accurate component metadata, a developer service page, a working relationship inspector, source evidence and shareable curated diagrams. The pilot should use representative real metadata from an approved non-sensitive environment alongside synthetic fixtures.

MVP excludes autonomous cloud changes, broad cross-cloud parity, unbounded graph visualization, and unsupported claims of complete impact analysis. AI assistance should follow trustworthy inventory and graph evidence, not precede it.

## 14. User stories and acceptance criteria

| ID | Story | Acceptance |
| --- | --- | --- |
| US-01 | As a developer, I can search for an API or resource and open its architecture context. | Given a matching authorized resource, search returns type, owner, environment and a link that selects it on canvas. |
| US-02 | As an architect, I can expand AKS cluster → namespace → service. | The correct child nodes render, breadcrumb updates, and back navigation preserves focus. |
| US-03 | As an architect, I can manually route a connector and save a named view. | After reload, positions, waypoints and labels remain unchanged; topology is not modified. |
| US-04 | As an SRE, I can trace a Service Bus dependency. | Directed producers and consumers are distinguishable, with evidence and timestamps. |
| US-05 | As a reviewer, I can compare current and proposed architectures. | Added, removed and modified entities and relationships are clearly marked. |
| US-06 | As a security analyst, I can inspect data classification and trust boundaries. | Restricted details remain hidden without permission; access attempts are audited. |
| US-07 | As a developer, I can inspect service code and runbook links. | Links are accurate, deep-linkable and report missing ownership/docs. |
| US-08 | As an engineer, I can use all canvas controls in a real browser. | Automated E2E tests verify click, double-click, zoom, pan, search, inspector, filters, save, reload and export. |
| US-09 | As an owner, I can correct an inaccurate dependency. | Proposed correction retains provenance and requires review before authoritative publication. |
| US-10 | As a user, I can ask Atlas which systems depend on an API. | Assistant returns grounded paths with evidence and a highlighted diagram, or explains uncertainty. |

## 15. Architecture considerations (solution-neutral recommendations)

- Frontend: dedicated browser-hosted application with diagram renderer, layout worker, incremental graph loading, state management and component inspector; do not rely on standalone HTML previews for production.
- Backend: catalog/query APIs, graph traversal, sync orchestration, authorization, evidence service, diagram versioning and audit.
- Storage: normalized entity/relationship store with graph-optimized indexes or projection; separate search index and immutable evidence history.
- Connector pipeline: scheduled/event-driven collectors → normalization → identity resolution → confidence/verification → graph publication.
- Graph operations: bounded traversals, precomputed summaries, progressive query results and authorization-aware caching.
- Architecture diagram editing: canonical graph remains immutable until explicit model edits; presentation coordinates are view-scoped.
- AI: tool-mediated retrieval and deterministic graph queries; citations, RBAC enforcement and evaluation against golden scenarios.
## 16. Risks and mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Beautiful diagrams but no trusted data | Low recurring adoption | Prioritize ownership, provenance and connector coverage |
| Graph hairball at scale | Unusable UX | Semantic zoom, hierarchy, clustering, edge bundling, scoped queries |
| Auto-discovery creates false links | Bad change decisions | Confidence, evidence, human verification, observed/inferred labels |
| Stale architecture views | Loss of trust | Freshness SLAs, drift indicators, last-known-good snapshots |
| Security leakage through search or AI | Compliance exposure | Authorization-aware traversal, redaction and security testing |
| Unresponsive or non-clickable canvas | Product rejection | Automated browser interaction gates, deployed staging URL, client error reporting |
| Manual curation becomes a bottleneck | Maintenance cost | Automated discovery plus stewardship workflows |
| Connector rate limits / permissions | Incomplete topology | Incremental sync, retries, coverage dashboard and source-specific permissions |

## 17. Dependencies and open decisions

| Decision | Question / owner to resolve |
| --- | --- |
| Primary sponsor | Who funds the platform and owns adoption KPIs? |
| Pilot domain | Which 5–10 applications and Azure subscriptions provide the first credible slice? |
| Authoritative ownership | Which source wins when CMDB, Git and application teams disagree? |
| Access model | What cross-domain, cross-environment and sensitive-data restrictions apply? |
| Discovery permissions | Which Azure, APIM, AKS and repository metadata scopes can be accessed read-only? |
| Data model / graph store | Which persistence and traversal approach fits volume and operational standards? |
| Visual assets | Confirm Microsoft Azure icon asset licensing and distribution rules. |
| SLOs and performance | Validate targets on approved browsers and representative enterprise dataset. |
| Collaboration | Who may edit/publish official diagrams and approve changes? |
| Deployment | Approved hosting, networking, identity, retention and observability stack. |

## 17.1 New feature acceptance scenarios

- **Onboarding:** A developer opens a service page and can reach the owner, API contract, deployment view, repository and runbook within two interactions.
- **Playback:** A curated Policy Issuance process can be stepped through on the canvas; UI labels it as a modeled flow and never displays fabricated runtime timing.
- **Time machine:** Comparing two snapshots identifies resource and dependency changes with inspectable provenance.
- **Drift:** Missing discovery evidence is shown as “unknown,” not a confirmed violation.
- **Sandbox:** Editing a proposed architecture does not mutate the published baseline or any Azure resource.
- **Security:** Sensitive flow labels and exports are filtered by role.
- **Cost:** Shared-resource allocation rules are visible and total allocated cost reconciles to imported source totals.
- **Self-service:** An unauthorized user cannot submit restricted actions; every request is audited.
- **Scorecards:** Every failing result links to a rule and evidence, and “not assessed” is distinct from failure.
- **AI:** Generated views and documents cite permitted sources and clearly label unsupported claims.

## 17.2 Acceptance scenarios for v1.2 additions

- **X-Ray:** In-place expansion preserves enterprise context, supports hierarchical drill-down and restores saved state without altering topology.
- **Passport:** Authorized users can locate owner, contract, dependencies and approved documentation; unknown values are explicit.
- **Contract Registry:** Versioned OpenAPI/AsyncAPI contracts are searchable and comparable using source specifications, not PR events or traffic observation.
- **Pattern Library:** An approved template can be instantiated in a sandbox, validated and reviewed without touching production resources.
- **Rule Engine:** Deterministic rule results distinguish PASS, FAIL, UNKNOWN, NOT_APPLICABLE and EXEMPT and link to evidence.

## 18. Definition of done

- Pilot personas can complete the six end-to-end journeys without facilitator assistance.
- Official iconography, nested Azure boundaries and connectors meet approved visual reference quality.
- All controls work in supported desktop browsers, with no console errors or dead interactions in release E2E suite.
- Graph facts expose provenance, freshness and verification; impact results are explainable and appropriately qualified.
- Search, deep links, service pages, owner links, diagram persistence and exports are reliable.
- Security review, penetration testing, performance testing, accessibility checks, operations runbook and recovery tests are complete.
- Product analytics demonstrate real developer task completion and pilot adoption—not just diagram views.
## Appendix A — Example developer-facing screens

| Screen | Essential elements |
| --- | --- |
| Enterprise landscape | Business capability lanes, systems, summarized integrations, search, environment selector, mini-map |
| Application home / Architecture Passport | Purpose, owner, dependencies, contracts, repos, environments, runbooks, evidence, freshness and correction workflow |
| Azure deployment canvas | Official icons, subscriptions, VNets, subnets, AKS namespaces, databases, routes |
| Relationship inspector | Contract, protocol, producer/consumer, traffic, auth, evidence, last seen |
| Impact workbench | Selected change, paths, affected candidates, criticality, confidence, export |
| Architecture diff | Snapshot selectors, added/removed/changed elements, approval status |
| Architecture X-Ray | In-place expansion, abstraction levels, nested boundaries, grouped edges and evidence labels |
| Integration Contract Registry | API/event schema browser, producer-consumer graph, versions, deprecation and specification diffs |
| Pattern Library | Approved design gallery, parameterized templates, sandbox instantiation and review |
| Architecture Rule Engine | Rule catalog, evidence-backed findings, exceptions, unknown state and export |
| Governance dashboard | Coverage, stale facts, unowned services, pending verification, drift |
| Ask Atlas | Natural-language prompt, grounded answer, source links, focused canvas actions |

## Appendix B — Proposed engineering test matrix

| Area | Mandatory checks |
| --- | --- |
| Canvas | Click, double-click, pointer capture, pan, zoom, keyboard selection, hit testing, nested expansion |
| Rendering | 1k/10k/100k inventory stress, edge density, labels, no blank canvas, resize, browser support |
| Persistence | Autosave, version restore, concurrent edits, layout isolation from graph facts |
| Connectors | Incremental sync, duplicate handling, retry, permissions, deleted resources, stale status |
| Graph | Directionality, cycles, access-aware traversal, confidence/provenance, query budgets |
| X-Ray | Expand/collapse, view state persistence, nested performance, keyboard navigation and provenance |
| Contracts | OpenAPI/AsyncAPI import, versioning, specification diff, RBAC and provenance |
| Patterns and rules | Sandbox isolation, approval state, deterministic rule fixtures, exception expiry and audit |
| Security | RBAC enumeration, sensitive relationships, connector credentials, injection, audit |
| AI | Citation fidelity, tool authorization, ambiguity, hallucination resistance, stale-data disclosure |
| Accessibility | Keyboard paths, focus, contrast, alternative graph listing, screen reader labels |

End of proposed BRD. This is a product-definition baseline for stakeholder review, not a finalized solution architecture or implementation commitment.


## Appendix C — Bright Application UX and Interaction Specification (V2.2 companion)

The companion document **`Atlas_Bright_UX_Interaction_Requirements_v1.md`** is the normative screen-level and interaction-level specification for the enterprise landscape, Architecture X-Ray, Architecture Passport, Contract Registry, Pattern Library and Rule Engine. It defines UX-CAN-001–024, UX-XR-001–010, UX-PASS-001–012, UX-ICR-001–007, UX-PAT-001–006, UX-RULE-001–006, UX-GLB-001–012 and UX-NFR-001–014, including acceptance criteria, bright visual tokens, failure states, cross-screen flows, proposed performance gates and release expectations. Where an earlier requirement is less specific, use the companion's testable interaction detail, subject to BRD security and evidence constraints.

**Design mandate:** Bright, vibrant, precise, professional, Azure-icon-rich and genuinely usable by architects, developers and enterprise teams. No static-only canvas, fake clickable controls, uncontrolled node clutter, PR-related functionality or production telemetry.


## Appendix D — V2.2 requirement governance and implementation readiness

**Traceability:** New requirements MOD-01–06, BCM-01–06, REC-01–07, AAC-01–06, BRN-01–06, ADR-01–05, LIN-01–07, SDK-01–06, NTF-01–05, COL-01–05, CMD-01–05, STORY-01–05, IMP-01–06 and FBK-01–05 must be linked to design stories, API/data contracts and QA evidence. Related original requirements remain in force and should be referenced rather than duplicated in implementation tickets.

**Expected stakeholder sign-off:** Enterprise Architecture approves type taxonomy and model semantics; Cloud Platform approves connector scope and identity rules; Security approves access and data-classification policy; Developer representatives approve search, Passport and command-palette journeys; UX/design approves bright canvas, interaction states and accessible visual language; Product approves release boundaries.

**Readiness gate:** Before development of a feature, confirm the authoritative data source, owner/steward, role matrix, screen states, positive and negative acceptance cases, performance workload, migration/backward-compatibility behavior and audit obligations. Unknowns are tracked as open decisions, not silently treated as approved.

**Explicit exclusions unchanged:** No PR ingestion or analysis, code review, production telemetry, distributed tracing, live traffic-derived dependencies, live monitoring dashboards or autonomous cloud modifications.
