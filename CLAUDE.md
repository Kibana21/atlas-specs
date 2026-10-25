# atlas-specs

Source of truth for Atlas requirements, UX, technical architecture, ADRs, and **cross-repo contracts**. It holds specifications and portable fixtures only. It must never contain executable backend/frontend source, secrets, real architecture exports, runtime data, or generated build artifacts (tech §17.3). The generated golden fixture is test data, regenerated and verified byte-for-byte by CI.

Independent Git repo (`origin` = github.com/Kibana21/atlas-specs, **public**). It is the **authority** for the other two repos. This file is self-sufficient. A workspace-level file may exist locally, but it is not versioned.

## Current contents

```text
brd/  ux/  technical/          # BRD v2.2, UX v1.1, Technical v1.1 baselines (never edit silently)
phase0/                        # blueprint, RTM (.md + requirements-registry.csv), backlog
features/ATLAS-NNN-<slug>/     # spec, plan, tasks, acceptance, readiness, evidence (+ reviews, proposals)
decisions/decision-register.md # DEC-NNN: Confirmed / Proposed / Open / Provisional
decisions/baseline-deviations.md  # TD-DEV-NNN: approved deviations from the baselines
contracts/                     # conventions.md, style-guide.md, compatibility.md (pinning + release rules)
contracts/openapi/atlas-api.yaml  # authoritative API (released contract-v0.1.0)
contracts/schemas/  contracts/examples/  # JSON Schemas + valid/invalid examples (canonical graph: */canonical/)
contracts/taxonomy/            # versioned canonical taxonomy and provider registries (ATLAS-002)
contracts/canonical-validation-rules.md  # HARD / DOMAIN / ADVISORY rule catalog
acceptance/test-data/canonical-golden-v1/  # deterministic synthetic golden fixture (generated: make golden)
design/tokens.json  design/tokens.md     # design tokens + contrast pairs (frontend generates from these)
tools/                         # uv project: specs-lock, conformance, token, registry, canonical checkers + fixture generator + tests
adr/  acceptance/              # ADRs (see adr/README.md), acceptance scenarios and test data
Makefile  .github/workflows/specs-ci.yml
```

ATLAS-001 (engineering foundation) is **Accepted** (v0.1.0, 24 Oct 2026). ATLAS-002 (canonical graph foundation) status is in `features/ATLAS-002-canonical-graph-foundation/evidence.md`.

## Commands

`make check` runs everything CI runs: `docs-lint` (markdownlint, container), `contract` (Redocly lint, container), `schemas`, `tools` (pytest), `canonical` (canonical contracts and golden fixture), `tokens`, `registry` and `breaking` (oasdiff against the latest `contract-v*` tag). Container images are digest-pinned in `tools/images.lock`, and GitHub Actions are pinned by SHA. Required CI checks: `docs-lint, contract, tools, tokens, registry, breaking`.

## Workflow and approval boundaries

- Claude runs the whole workflow.
  1. Feature branch per approved task.
  2. Run `make check` from a fresh clone of the committed branch.
  3. Push, then open a PR to `main`.
  4. Wait until every required check reports success.
  5. Review the diff against the acceptance criteria.
  6. Merge with a merge commit and a head-SHA guard.
  7. Confirm `main` CI is green and record evidence.
- Never force-push, push to `main`, bypass branch protection, or merge failing or missing checks.
- Owner approval is required for:
  - material architecture or product changes;
  - destructive actions or shared-infrastructure changes;
  - privileged access or credentials;
  - significant cost or scope changes;
  - unresolved spec conflicts;
  - moving to the next checkpoint or gate;
  - **contract releases**.
- `contract-vX.Y.Z` tags are created only for an owner-approved release, on the merged `main` commit, with `info.version == X.Y.Z` (`contracts/compatibility.md` §3). Consumers pin a full 40-hex SHA in `specs.lock`.
- **Public repo:**
  - Never commit secrets, tokens, credentials, confidential company or customer data, internal infrastructure topology, or local-machine details (home paths, usernames).
  - Review the staged diff before every push.
- **Credentials:** never print credentials, and never forward `Authorization` headers to redirected storage or third-party hosts.
- **Evidence:** never claim checks passed without the actual run, never weaken a check to pass, and record runs in the feature's `evidence.md`.

## Document authority and how they relate

- **BRD v2.2** defines *what* and *why*. Requirement families: INV, CAN, DEV, DEP, CON, GOV, AI, KNOW, FLOW, HIST, SAN, SEC, COST, SELF, SCORE, AIX, EXP, XRAY, PASS, ICR, PAT, RULE (§5.1–5.22). It adds MOD, BCM, REC, AAC, BRN, ADR, LIN, SDK, NTF, COL, CMD, STORY, IMP, FBK (§5.23–5.38). Experience sections are E01–E20, journeys J01–J06 and J-*-01, user stories US-01–10.
- **UX v1.1** is normative for screen behaviour: UX-CAN-001–024, UX-XR-001–010, UX-PASS-001–012, UX-ICR, UX-PAT, UX-RULE, UX-GLB-001–012, UX-NFR-001–014, plus the §18 V2.2 additions (UX-MOD-01 … UX-FBK-01). Where the BRD is less specific, use the UX detail, subject to BRD security/evidence rules.
- **Technical v1.1** proposes the implementation: modules, tables, API surface, connectors, repo layouts, phases, and ADR backlog (§22).
- Conflict rule: the stricter security/evidence requirement wins, and the discrepancy goes to `decisions/decision-register.md` before anyone implements it.

## Editing rules

- **Requirement IDs are stable.** Never renumber or reuse an ID. Add new IDs in the existing family style and keep IDs unique across documents (a planned CI check).
- Bump the document version and add a change-log/revision entry when changing a baseline. Keep the filename version suffix (`_v2_2`, `_v1_1`) in sync. If you rename a file, update `README.md`, the cross-references inside the other documents, and §17.3 of the tech design.
- Keep "proposed" language. Don't turn a target into a commitment unless the user says it was approved.
- Never add excluded product scope:
  - PR impact analysis or GitHub PR integration;
  - live telemetry or monitoring;
  - distributed tracing;
  - live health dashboards;
  - inferred runtime traffic.

  If asked to, flag that it reopens an explicit exclusion (BRD E20). Ordinary Git PRs for developing Atlas are fine.
- Never silently modify the BRD, UX or Technical baselines. An approved deviation goes in `decisions/baseline-deviations.md`. A conflict between specs: stop and report it.
- Use sanitized, synthetic data only in examples and fixtures.

## ADRs and decisions

- ADR files: `adr/ADR-NNNN-kebab-title.md` (e.g. `ADR-0001-canonical-identity.md`). Planned first set is in tech §17.3: canonical identity, graph/layout separation, source precedence, projection and scale, auth, three-repo contract governance. Tech §22 also lists ADR-001…ADR-014 as decisions to resolve. Map them to the four-digit files and record the mapping in `adr/README.md`.
- Suggested ADR sections: Status (proposed/accepted/superseded), Context, Decision, Consequences, Alternatives, Related requirement IDs.
- Decisions live in `decisions/decision-register.md` as `DEC-NNN` (status Confirmed / Proposed / Open, owner, needed-by, blocked items). When accepted, write the ADR and set the row to Confirmed. Never mark a decision Confirmed without the user saying it was approved.
- `DEC-` IDs exist because `ADR-01…05` is a BRD *requirement* family and tech §22 uses `ADR-001…014`. Refer to tech backlog epics as `TE01–TE09` (BRD already uses E01–E20).
- When requirement mappings or decision statuses change, update `phase0/requirements-registry.csv` and the RTM markdown together. Every requirement must map to at least one `BL-` item and every `DEC-`/`BL-` reference must exist.

## Contracts

- `contracts/openapi/atlas-api.yaml` is the authoritative reviewed API (follow `contracts/conventions.md` and `style-guide.md`). Base `/api/v1`, cursor pagination, opaque UUID IDs, and the error envelope `{error:{code,message,correlation_id,details,recoverable}}` (tech §6).
- JSON Schemas go under `contracts/schemas/` (`<name>.v<N>.json`). Valid/invalid example payloads go under `contracts/examples/`.
- Every contract change states its breaking/non-breaking classification (`compatibility.md`), bumps `info.version` (`X.Y.Z-dev.N` between releases), and updates examples and affected acceptance scenarios. A merge here deploys nothing: consumers move only when their `specs.lock` is updated.
- Acceptance scenarios use Given/When/Then and reference requirement IDs. Golden test data stays small, deterministic, and sanitized. The seeded UX dataset is about 250 entities / 700 relationships (tech §4.4).

## Known inconsistencies to resolve (do not "fix" silently)

The full list with severity and resolution path is in the blueprint §3 (CF-01…CF-15, gaps G-01…G-18). Headline items:

- **Relationship types:** BRD INV-02 lists `CALLS_API, PUBLISHES, CONSUMES, READS, WRITES, DEPLOYED_ON, HOSTED_IN, OWNS, DEPENDS_ON, PROTECTS`. Tech §3.3 uses `CONTAINS, SUPPORTS_CAPABILITY, EXPOSES_API, CONSUMES_API, PUBLISHES_TO, SUBSCRIBES_TO, STORES_IN, DEPLOYED_AS, CONNECTS_TO, OWNS, PRODUCES_DATA/CONSUMES_DATA, DECIDED_BY`.
- **Roles:** BRD GOV-01/E17 (Viewer, Developer, Editor, Domain Owner, Architect Reviewer, Security Reviewer, Connector Operator, Administrator) vs tech §9.1 (Reader, Contributor, Architect, Steward, Reviewer, Security Reviewer, Source Admin, Platform Admin).
- **Phase numbering:** BRD §12 (phases 0–5), BRD E19 (releases 0–4), UX §14 (R0–R4), and tech §18 (phases 0–4) group features differently. For example, the Rule Engine is tech Phase 3 but BRD Phase 4.
- **Folder layout vs tech §17.3:** the repo has `contracts/schemas/` (plan: `contracts/jsonschema/` + `contracts/examples/`), `acceptance/scenarios|test-data/` (plan: `journeys|golden-datasets/`), and an extra `decisions/`.
- **Stale references:** the UX header says "Companion to BRD V2.0". BRD Appendix C cites `Atlas_Bright_UX_Interaction_Requirements_v1.md`. The BRD has two sections numbered 5.23.
- **Tokens:** UX §2.1 has Compute violet `#8C58D8`, which tech §5.3 omits (see `design/tokens.md`).
