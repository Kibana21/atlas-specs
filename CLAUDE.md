# atlas-specs

Source of truth for Atlas requirements, UX, technical architecture, ADRs, and **cross-repo contracts**. It holds specifications and portable fixtures only. It must never contain executable backend/frontend source, secrets, real architecture exports, runtime data, or generated build artifacts (tech §17.3).

Independent Git repo (`origin` = github.com/Kibana21/atlas-specs). See `../CLAUDE.md` for the workspace and product invariants.

## Current contents

```
brd/Atlas_Enterprise_Architecture_BRD_v2_2.md                    # product requirements (1400 lines)
ux/Atlas_Bright_UX_Interaction_Requirements_v1_1.md              # screen/interaction spec
technical/Atlas_Technical_Architecture_System_Design_v1_1.md     # stack, model, API, repos, phases
phase0/Atlas_Phase0_Engineering_Blueprint_v0_1.md   # readiness assessment + implementation order (proposed)
phase0/requirement-traceability-matrix.md            # RTM (human-readable)
phase0/requirements-registry.csv                     # RTM (machine-readable; intended requirement-ID authority)
phase0/prioritized-backlog.md                        # BL-0xx…BL-5xx ranked backlog
features/ATLAS-NNN-<slug>/{spec,plan,tasks,acceptance}.md  # work-item specs; ATLAS-001 = engineering foundation (draft)
adr/README.md                    # empty; ADRs go here
decisions/decision-register.md   # all decisions: DEC-NNN, Confirmed/Proposed/Open
decisions/open-decisions.md      # pointer to the register
contracts/openapi/  contracts/schemas/        # empty (.gitkeep)
acceptance/scenarios/  acceptance/test-data/  # empty (.gitkeep)
```

No CI, linters, `atlas-api.yaml`, or `compatibility.md` exist yet.

## Document authority and how they relate

- **BRD v2.2** defines *what* and *why*. Requirement families: INV, CAN, DEV, DEP, CON, GOV, AI, KNOW, FLOW, HIST, SAN, SEC, COST, SELF, SCORE, AIX, EXP, XRAY, PASS, ICR, PAT, RULE (§5.1–5.22). It adds MOD, BCM, REC, AAC, BRN, ADR, LIN, SDK, NTF, COL, CMD, STORY, IMP, FBK (§5.23–5.38). Experience sections are E01–E20, journeys J01–J06 and J-*-01, user stories US-01–10.
- **UX v1.1** is normative for screen behaviour: UX-CAN-001–024, UX-XR-001–010, UX-PASS-001–012, UX-ICR, UX-PAT, UX-RULE, UX-GLB-001–012, UX-NFR-001–014, plus the §18 V2.2 additions (UX-MOD-01 … UX-FBK-01). Where the BRD is less specific, use the UX detail, subject to BRD security/evidence rules.
- **Technical v1.1** proposes the implementation: modules, tables, API surface, connectors, repo layouts, phases, and ADR backlog (§22).
- Conflict rule: the stricter security/evidence requirement wins, and the discrepancy goes to `decisions/decision-register.md` before anyone implements it.

## Editing rules

- **Requirement IDs are stable.** Never renumber or reuse an ID. Add new IDs in the existing family style and keep IDs unique across documents (a planned CI check).
- Bump the document version and add a change-log/revision entry when changing a baseline. Keep the filename version suffix (`_v2_2`, `_v1_1`) in sync. If you rename a file, update `README.md`, the cross-references inside the other documents, and §17.3 of the tech design.
- Keep "proposed" language. Don't turn a target into a commitment unless the user says it was approved.
- Never add PR/telemetry scope (see invariants). If asked to, flag that it reopens an explicit exclusion (BRD E20).
- Use sanitized, synthetic data only in examples and fixtures.

## ADRs and decisions

- ADR files: `adr/ADR-NNNN-kebab-title.md` (e.g. `ADR-0001-canonical-identity.md`). Planned first set is in tech §17.3: canonical identity, graph/layout separation, source precedence, projection and scale, auth, three-repo contract governance. Tech §22 also lists ADR-001…ADR-014 as decisions to resolve. Map them to the four-digit files and record the mapping in `adr/README.md`.
- Suggested ADR sections: Status (proposed/accepted/superseded), Context, Decision, Consequences, Alternatives, Related requirement IDs.
- Decisions live in `decisions/decision-register.md` as `DEC-NNN` (status Confirmed / Proposed / Open, owner, needed-by, blocked items). When accepted, write the ADR and set the row to Confirmed. Never mark a decision Confirmed without the user saying it was approved.
- `DEC-` IDs exist because `ADR-01…05` is a BRD *requirement* family and tech §22 uses `ADR-001…014`. Refer to tech backlog epics as `TE01–TE09` (BRD already uses E01–E20).
- When requirement mappings or decision statuses change, update `phase0/requirements-registry.csv` and the RTM markdown together. Every requirement must map to at least one `BL-` item and every `DEC-`/`BL-` reference must exist.

## Contracts (when created)

- `contracts/openapi/atlas-api.yaml` is the authoritative reviewed API. Base `/api/v1`, cursor pagination, opaque UUID IDs, and the error envelope `{error:{code,message,correlation_id,details,recoverable}}` (tech §6).
- JSON Schemas for graph, import/export (architecture-as-code), and connector payloads go under `contracts/schemas/`. Valid/invalid example payloads go next to them.
- Every contract change states its breaking/non-breaking classification and updates examples and affected acceptance scenarios. Consumers pin a commit SHA in `specs.lock`, so a merge here does not deploy anything.
- Acceptance scenarios use Given/When/Then and reference requirement IDs. Golden test data stays small, deterministic, and sanitized. The seeded UX dataset is about 250 entities / 700 relationships (tech §4.4).

## Known inconsistencies to resolve (do not "fix" silently)

The full list with severity and resolution path is in the blueprint §3 (CF-01…CF-15, gaps G-01…G-18). Headline items:


- **Relationship types:** BRD INV-02 lists `CALLS_API, PUBLISHES, CONSUMES, READS, WRITES, DEPLOYED_ON, HOSTED_IN, OWNS, DEPENDS_ON, PROTECTS`. Tech §3.3 uses `CONTAINS, SUPPORTS_CAPABILITY, EXPOSES_API, CONSUMES_API, PUBLISHES_TO, SUBSCRIBES_TO, STORES_IN, DEPLOYED_AS, CONNECTS_TO, OWNS, PRODUCES_DATA/CONSUMES_DATA, DECIDED_BY`.
- **Roles:** BRD GOV-01/E17 (Viewer, Developer, Editor, Domain Owner, Architect Reviewer, Security Reviewer, Connector Operator, Administrator) vs tech §9.1 (Reader, Contributor, Architect, Steward, Reviewer, Security Reviewer, Source Admin, Platform Admin).
- **Phase numbering:** BRD §12 (phases 0–5), BRD E19 (releases 0–4), UX §14 (R0–R4), and tech §18 (phases 0–4) group features differently. For example, the Rule Engine is tech Phase 3 but BRD Phase 4.
- **Folder layout vs tech §17.3:** the repo has `contracts/schemas/` (plan: `contracts/jsonschema/` + `contracts/examples/`), `acceptance/scenarios|test-data/` (plan: `journeys|golden-datasets/`), and an extra `decisions/`. `design/tokens.md` doesn't exist yet.
- **Stale references:** the UX header says "Companion to BRD V2.0". BRD Appendix C cites `Atlas_Bright_UX_Interaction_Requirements_v1.md`. The BRD has two sections numbered 5.23.
- **Tokens:** UX §2.1 has Compute violet `#8C58D8`, which tech §5.3 omits.
