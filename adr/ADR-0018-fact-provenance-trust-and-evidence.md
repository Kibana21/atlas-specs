# ADR-0018 — Fact-level provenance, trust and evidence

| Field | Value |
|---|---|
| Status | **Accepted** (owner, 25 Oct 2026: ATLAS-002 CP1 final approval of D1–D19). Drafting history: D13 and D14 approved by the owner (25 Oct 2026), to be confirmed with the other rows. Revision 2 aligns it with the revised ADR-0008 and ADR-0017 (assertion validity intervals, allowed evidence per relationship type, `READS_FROM`/`WRITES_TO`); the four dimensions and the conflict procedure are unchanged |
| Register | DEC-056 (**Confirmed** 25 Oct 2026); informs DEC-066 (Open, P1) |
| Owner (proposed) | Enterprise Architecture + UX; approval: Atlas owner |
| Related | INV-03, INV-04, INV-06, DEP-04, PASS-07, E06, UX-PASS-011, RULE-04; tech §3.4, §7.3; ADR-0003, ADR-0008, ADR-0017 |

## Problem

Several vocabularies coexist:

| Source | States or types |
|---|---|
| Tech §3.4 trust states | discovered, documented, curated, inferred, proposed, stale, conflicted |
| BRD DEP-04 evidence types | configuration-derived, contract-derived, manually verified, inferred |
| BRD E06 | unknown, not applicable, not verified, stale |
| BRD PASS-07 | unknown, missing, verified, stale |

The UX shows a "Verified" badge that is not a tech trust state. INV-03 requires source, evidence pointer, discovery method, confidence, first/last seen, validity and verification **for each fact**.

**Owner direction (24 Oct 2026):**

- provenance and trust **per fact**, for entities and relationships;
- distinguish verified provider/configuration evidence, documented architecture, human assertions, inferred relationships, and unknown or conflicting evidence;
- **documentation is never proof of runtime traffic**;
- conflicting evidence is stored, surfaced and resolved **without silently collapsing trust states**.

## What a fact is

| Fact | Example |
|---|---|
| Entity existence | "APIM instance X exists in subscription S" |
| Attribute value (`field_path`) | "X.location = westeurope"; "app A.owner = team T" (as `OWNS`) |
| Relationship existence | "service B `CONSUMES_API` api C" |
| Relationship attribute | "W `CONNECTS_TO` K, connectivity_kind = private_link" |

"Service B reads database D" and "service B writes database D" are **two** facts (`READS_FROM`, `WRITES_TO`), each with its own assertions, trust state, verification and history (ADR-0017 §5).

Each fact has **zero or more evidence assertions**. Zero assertions means there is no fact: the information is *unknown*, not false.

## Four orthogonal dimensions (recommended)

### 1. Evidence kind: how a source knows it (per assertion)

| `evidence_kind` | Meaning | DEP-04 term |
|---|---|---|
| `provider_configuration` | Read from **any** provider's or platform's configuration or control plane (Azure, AWS, Google Cloud, OCI, …; a private-cloud platform; an on-premises CMDB or IaC state) by an approved source | configuration-derived |
| `contract` | Derived from a machine-readable artifact (OpenAPI, AsyncAPI, IaC manifest) | contract-derived |
| `documentation` | Documented architecture: documents, diagrams, imported drawings, ADRs | (documented) |
| `human_assertion` | Stated by an identified person (steward, owner) through Atlas or a reviewed import | manually verified, once verified (dimension 3) |
| `inferred` | Derived by a deterministic, versioned rule from other facts; records rule ID and version and the input fact IDs | inferred |

- **There is deliberately no "observed traffic" or "runtime" kind.** Telemetry, traces and traffic analysis are excluded scope (BRD E20).
- `documentation` and `contract` describe *intended* architecture. The UI legend and exports must say "documented" or "from contract", never "observed" or "live".
- **Each assertion records:**
  - `source_ref` (source system or connector, or the actor for human assertions);
  - `artifact_ref` (URI or path plus content hash, never a secret);
  - `method` (connector name and version, import ID or rule ID);
  - `confidence` (0–1, meaningful only for `inferred`; 1 for direct reads);
  - `observed_at` / `asserted_at`;
  - `valid_from` / `valid_to`;
  - for attribute facts, the `asserted_value`.

### 2. Trust state: the fact's current standing (per fact, derived)

`discovered` · `documented` · `curated` · `inferred` · `proposed` · `stale` · `conflicted` (tech §3.4).

A **pure, versioned function** of the fact's current assertions and policy computes it:

| Result | When |
|---|---|
| `discovered` | Current `provider_configuration` evidence, no conflict |
| `documented` | Only `documentation` or `contract` evidence |
| `curated` | Accepted by a steward (`human_assertion` with approval) |
| `inferred` | Only `inferred` evidence. Never upgrades itself: promotion needs a human assertion |
| `proposed` | Originates from a draft or design (branches, later) and is not part of the published graph |
| `stale` | The best evidence is past its freshness policy, or a source stopped seeing it without verified removal |
| `conflicted` | Two or more current assertions disagree and no precedence rule resolves them (ADR-0003, DEC-034) |

- The state is **stored** with each fact version for query speed. It can always be recomputed from evidence, and a test asserts that recomputation reproduces it.
- **The evidence rows are never collapsed.** A `discovered` relationship that also has documentation keeps both assertions.
- Any **summary** badge (for example per entity) is labeled as a summary and links to the per-fact detail.

### 3. Verification (per fact)

`unverified` | `verified`, with `verified_by`, `verified_at`, `expires_at`.

- Expiry turns the fact `stale` (UX-PASS-011).
- Verification is a `human_assertion` and does not replace the other evidence.
- "Verified" in the UI means this dimension, not a trust state.

### 4. Completeness (per required field or expected relationship of a type)

`present` · `not_documented` (missing) · `not_applicable` · `unknown_coverage` (the source cannot see it, or permissions are insufficient).

- This is how *unknown* is represented: as coverage, **never** as a drawn edge or an invented value (DEC-066, RULE-04 → `UNKNOWN`).
- It maps PASS-07: unknown → `unknown_coverage`; missing → `not_documented`; verified → dimension 3; stale → dimension 2.

## Provider neutrality (revision 3)

Nothing in this model depends on a provider. Evidence records **the source that knows**, not the provider of the fact. A cross-provider relationship usually has evidence from one side only (for example an Azure setting naming an AWS endpoint). It is recorded as exactly that, `provider_configuration` from the Azure source, and is never upgraded to verified without a human verification (ADR-0019 §6).

## Who changed a fact vs who knows it

The change set's actor (ADR-0008 §10) is who **committed** a change. Evidence's `source_ref` is who or what **knows** the fact. A human assertion's author is recorded on its evidence. These three are kept separate: for example, a fixture-loader service commits a fact whose evidence is a document written by an architect.

## Allowed evidence per relationship type

ADR-0017 §4.1 lists which evidence kinds each relationship type accepts. An assertion with a kind that is not allowed is rejected, in the service layer and by a database check on `fact_assertion`. In particular:

- `DEPENDS_ON` accepts only `human_assertion` and `documentation`. A traversal result is never stored as a dependency, and its trust state can never be `discovered` (ADR-0017 §4.3).
- `CONNECTS_TO` never accepts `inferred`.

## Conflicts: stored, surfaced, resolved (never collapsed)

1. **Stored:** every competing assertion is kept with its value and evidence.
2. **Selected value:**
   - precedence rules (DEC-034) may pick one;
   - when they can't, the fact's selected value stays the **prior approved value**, or none if there was none;
   - the fact becomes `conflicted` and a `reconciliation_case` is opened.
3. **Surfaced:** APIs return the trust state and, to authorized callers, the competing assertions. The UI shows a distinct conflicted marker (icon plus text).
4. **Resolved:**
   - a steward decision is a new `human_assertion` in a new change set (ADR-0008);
   - the losing assertions are closed (`revision_to`) by that change set, which records the decision. Their rows and evidence are unchanged and remain visible in history (ADR-0008).
5. **Existence conflicts** (one source sees it, another reports deletion):
   - "not seen" is not removal (INV-06);
   - a tombstone needs explicit provider deletion evidence or a steward decision;
   - otherwise the fact goes `stale` after the source's grace policy.

## Options considered

| Option | Verdict |
|---|---|
| **A. Four orthogonal dimensions with a per-fact evidence ledger** (above) | **Recommended**: satisfies INV-03 per fact, DEP-04, PASS-07 and E06; unknown and conflict are explicit; nothing collapses |
| B. One combined status enum per fact (e.g. verified / documented / inferred / unknown) | Rejected: conflates how something is known with how current it is, loses competing evidence, and forces a "winner" |
| C. Entity-level provenance only | Rejected: fails INV-03 ("each fact"); one stale attribute would taint the whole entity |

## Trade-offs and risks

- **Volume:** several assertions per fact. At the pilot size (10k entities, 40k relationships, ~10 fact fields each) that is roughly 0.5–1 M assertion rows. That's fine for PostgreSQL with `(org_id, fact_id)` indexes. Partitioning is considered only at Scale A+ after measurement (ADR-0001).
- **Complexity of the trust function:** it is pure, versioned and unit-tested with a truth table, never decided by an LLM (invariant 7).
- **Freshness policies** per source kind are needed for `stale`. ATLAS-002 defines the field. Values come with connectors (Phase 2) and are fixed for fixtures.

## Impact on the database schema

- `evidence`: append-only.
- `fact_assertion`: links a fact (entity, relationship, attribute path) to evidence, with the asserted value, the evidence kind and a validity interval `[revision_from, revision_to)`.
- Per-version columns: `trust_state`, `verification_state`, `verified_by/at`, `expires_at`.
- `completeness` derived per type rules, not stored as facts.
- No UPDATE or DELETE on evidence rows; assertions only get their `revision_to` set once.
- See ADR-0001.

## Impact on APIs and authorization (future)

- Every fact in API responses carries `trust_state`, `evidence_kinds[]`, `verification` and `last_evidence_at`.
- Evidence detail and artifact references are separately authorized: they can reveal source systems.
- Exports and AI receive the same fields, so they never imply runtime observation (DEP-04).

## Migration and compatibility

- New evidence kinds or trust states are a contract MINOR change plus a trust-function version.
- Stored states are recomputable, so a new function version is applied in one change set.

## Approved by the owner (25 Oct 2026)

1. The four dimensions and their exact value lists (no runtime or traffic evidence kind).
2. Trust state stored per fact version but always recomputable from evidence; no collapse; summaries labeled.
3. The conflict procedure (keep all assertions, keep the prior approved value, `conflicted` plus case, steward resolution as a new assertion).
4. "Not seen" ≠ removal; tombstones need deletion evidence or a steward decision.
