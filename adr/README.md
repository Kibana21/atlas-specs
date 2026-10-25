# Architecture Decision Records

ADRs live here as `ADR-NNNN-kebab-title.md`. Each one has a **Status** (Proposed, Accepted, Superseded) and links its register row (`decisions/decision-register.md`, `DEC-NNN`). The register stays the authority for decision status. An ADR becomes **Accepted** only when the owner approves it and the register row moves to Confirmed (register §E).

## Numbering

- `ADR-0001`…`ADR-0014` are reserved for the topics of Technical Design §22 (`ADR-001`…`ADR-014`), with the same number. So `ADR-0008` is the snapshot strategy (as DEC-057 anticipates).
- New topics start at `ADR-0015`.
- These IDs never collide with the BRD requirement family `ADR-01`…`ADR-05` (four digits; DEC-082).

| ADR | Topic | Tech §22 | Register | Status |
|---|---|---|---|---|
| [ADR-0001](ADR-0001-canonical-store-postgresql-schema.md) | Canonical store: PostgreSQL schema and scale design | ADR-001 | DEC-021, DEC-022 | Proposed |
| ADR-0002 | Diagram engine | ADR-002 | DEC-023 | not written |
| [ADR-0003](ADR-0003-identity-matching-and-aliases.md) | External identity, matching precedence, aliases, merge/split | ADR-003 (+ ADR-012 principles) | DEC-025, DEC-034 | Proposed |
| ADR-0004…0007 | Authentication; jobs; search; deployment | ADR-004…007 | DEC-026, DEC-028, DEC-029, DEC-030 | not written |
| [ADR-0008](ADR-0008-revisions-and-snapshots.md) | Revisions, history and snapshots | ADR-008 | DEC-031 (DEC-057 open) | Proposed |
| ADR-0009…0014 | Import security; AI boundary; graph-engine threshold; source authority; permissions; rule DSL | ADR-009…014 | various | not written |
| [ADR-0015](ADR-0015-canonical-identifier-format.md) | Canonical identifier format | — | DEC-037 | Proposed |
| [ADR-0016](ADR-0016-tenancy-and-organization-scope.md) | Tenancy and organization scope | — | DEC-058 | Proposed |
| [ADR-0017](ADR-0017-taxonomy-and-relationship-vocabulary.md) | Canonical taxonomy and relationship vocabulary v1 | — | DEC-050, DEC-070 | Proposed |
| [ADR-0018](ADR-0018-fact-provenance-trust-and-evidence.md) | Fact-level provenance, trust and evidence | — | DEC-056 | Proposed |
| [ADR-0019](ADR-0019-provider-neutral-model-and-onboarding.md) | Provider-neutral canonical model and provider onboarding | — | DEC-004 (Confirmed), DEC-050, DEC-070 | Proposed |

Proposed ADRs were drafted for ATLAS-002 CP1 (revisions 2 and 3 after the owner's reviews on 25 Oct 2026). See `features/ATLAS-002-canonical-graph-foundation/decision-matrix.md` for the exact choices awaiting approval.
