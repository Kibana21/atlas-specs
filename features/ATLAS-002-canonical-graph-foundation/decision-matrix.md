# ATLAS-002 CP1 — Decision matrix (for owner confirmation)

**Version:** revision 2 · **Date:** 25 October 2026 · **Status:** every row is still **Proposed** in the register. The owner reviewed revision 1 on 25 Oct 2026 (approved, approved with clarification, or amend; recorded below). The register rows move to Confirmed and the ADRs to Accepted only when the owner confirms this revision (Gate G1). No canonical-graph code, table, migration, role or privilege exists.

## 1. Owner review of revision 1 (25 Oct 2026)

The owner approved the overall Canonical Graph Foundation direction and accepted CP0 as complete.

| Verdict | Rows |
|---|---|
| Approve (subject to consistency with the authoritative specifications, checked in §3) | D1, D2, D3, D5, D9, D10, D13, D14, D16, D18 |
| Approve with clarification | D4, D11, D12 |
| Amend before confirmation | D6, D7, D8, D15, D17 |

## 2. Revised rows

| # | Owner asked | Revision 2 | Where |
|---|---|---|---|
| D4 | Store the original provider ID and its normalized form; define normalization, case, identity changes, collisions | `original_key` (verbatim) and `normalized_key` plus `normalization_version` and parsed `key_parts`. Rule `arm-1`: validate and **reject** malformed IDs (never repair), trim, lowercase, no percent-decoding. Tables for identity changes (tenant transfer, move, rename, recreate, deletion) and ARM-specific collisions | ADR-0003 §Azure Resource IDs |
| D6–D7 | Complete catalog, required attributes, matrix; demonstrate coverage; gaps; don't freeze | Full catalog with required attributes, identity namespaces and parents; **two proposed additions** (`core.system`, `core.component`, both named by MOD-01); environment scope `single`/`shared`/`unknown` (shared infrastructure, INV-05); `type_key` on versions so generic resources can be re-typed with their ID; nine worked scenarios; gaps G-T1…G-T11; generic-fallback limits | ADR-0017 §2, §6, §7 |
| D8 | Keep read and write distinct; evaluate `STORES_IN.access_mode` | One edge with `access_mode` can't give each direction its own evidence, trust, verification or history, and turns "one source says read, another says write" into a false conflict. **Separate `READS_FROM` and `WRITES_TO` records.** `STORES_IN` kept only for "uses this store, direction not established", never auto-converted | ADR-0017 §5 |
| D9 | Curated-only; explicit provenance; no path-to-dependency conversion | Only `human_assertion` or `documentation` evidence (enforced); required rationale and source; graph paths never stored as `DEPENDS_ON`; never `discovered` | ADR-0017 §4.3, ADR-0018 |
| D11–D12 | Physical containment vs logical membership; no single-parent rule on membership | `CONTAINS` = composition: one parent, cycle-checked, resource and logical families never mixed. New `MEMBER_OF` = grouping: many-to-many, acyclic by construction (type-level DAG, CI-checked). Generic fallback limits stated | ADR-0017 §3, §7.2 |
| D15 | Atomic publication, immutable versions, snapshot consistency, reconstruction, endpoint validity, rollback; proportionate | Defined, with a worked example. Revisions are commit-ordered and gap-free; versions immutable except a set-once `revision_to` (trigger plus column privilege); no change set for an unchanged input; revert = new change set, refused on conflict; scope limits for ATLAS-002 | ADR-0008 |
| D17 | Don't broaden `atlas_app`; dedicated least-privilege ingestion role; exact changes; create nothing | New `atlas_ingest` / `atlas_test_ingest` login roles (owner-run proposal script, owner-created credentials); `atlas_app` unchanged (read-only); privilege matrix; exact specs, server, `.env`, migration, settings, CI, doctor and test changes | ADR-0001 §Privileges |

## 3. Consistency with the BRD, UX and Technical baselines

None of these is resolved by editing a baseline. Items marked **deviation** are recorded in `decisions/baseline-deviations.md` only when the owner confirms the row.

| # | Baseline statement | This proposal | Kind | Rows |
|---|---|---|---|---|
| C-01 | BRD INV-02 (Must): `CALLS_API, PUBLISHES, CONSUMES, READS, WRITES, DEPLOYED_ON, HOSTED_IN, OWNS, DEPENDS_ON, PROTECTS` | Tech names with documented aliases (ADR-0017 §8). `HOSTED_IN` becomes `CONTAINS` in the **inverse** direction. `PROTECTS` is defined but has no allowed pairs in v1 | **Deviation** (vocabulary) | D6, D8, D10 |
| C-02 | Tech §3.3 catalog | Adds `READS_FROM`, `WRITES_TO`, `MEMBER_OF`, `DEPENDS_ON`, `PROTECTS`; narrows `CONTAINS` (hierarchy only) and `STORES_IN` (direction not established) | **Deviation** (vocabulary) | D6, D8, D9, D11 |
| C-03 | BRD MOD-01 (Must) names system, container, component | Adds `core.system` and `core.component`. If the owner declines them, MOD-01 has a coverage gap instead | Resolved by D7 additions | D7 |
| C-04 | BRD INV-05 (Must): shared infrastructure | `environment_scope = shared` plus `MEMBER_OF` environments. Revision 1 could not represent it | Resolved in revision 2 | D7, D11 |
| C-05 | Tech §3.4 lifecycle `active, deprecated, retired` | Used exactly; removal and merge are a separate `record_state` | Consistent | D7, D15 |
| C-06 | Tech §3.5 illustrative tables (`entity` with mutable `revision`, `source_identity`, `fact_provenance`, `entity.classification`, snapshot "source cutoff") | Identity + version tables; `external_identity`; `evidence` + `fact_assertion`; classification waits for DEC-073; source cutoff comes with connectors. Tech marks the tables "illustrative" | Recorded interpretation, not a deviation | D15, D16 |
| C-07 | Tech §3.2: ARM IDs "with subscription/tenant scope" | Subscription is in the key; the tenant is a modeled `CONTAINS`, because a subscription can move between tenants without changing its ID | Interpretation (recorded) | D4 |
| C-08 | **DEC-044 (Confirmed): four Atlas roles**; ATLAS-001 FR-28: write grants go to `ATLAS_DB_APP_ROLE` | Two more roles; canonical-table write grants go to the ingestion role. ATLAS-001's documents are not edited: ATLAS-002's spec will state the new rule, and DEC-044 is amended | **Amendment of a Confirmed decision** (needs explicit owner approval) | D17 |
| C-09 | Tech §3.1 lists further types (business process, file interface, integration contract, data domain, schema, ADR, pattern, rule…) | Not in v1; arrive with their phases as MINOR versions (ADR-0017 G-T7) | Phasing, consistent with tech §18 | D7 |
| C-10 | DEC-004 (Confirmed): non-Azure systems modeled without Azure hierarchy | Logical types cover them; there is **no non-Azure physical type** in v1 (G-T9) | Gap for owner decision | D7 |
| C-11 | UX "Verified" badge; BRD DEP-04; BRD E16 Passport field contract ("read/write links" for databases and datasets) | Verification dimension (D13); evidence kinds; separate read and write records (D8) | Consistent | D8, D13 |
| C-12 | Tech §10 published baselines and branches | Every change set is published in ATLAS-002; branches later without reshaping tables; DEC-057 stays Open | Consistent (deferred) | D15 |

No conflict was found with the UX baseline. The approved rows (D1, D2, D3, D5, D13, D14, D16, D18) needed no change for consistency; D9 and D10 are consistent apart from C-01/C-02.

## 4. Confirmation table (D1–D18)

"Owner 25 Oct" is the review verdict. "Register" is the current status; nothing moves until the owner confirms this table.

| # | Decision (register) | Final recommendation | Owner 25 Oct | Revised | Register | ADR |
|---|---|---|---|---|---|---|
| D1 | Tenancy (DEC-058) | One database; `org_id` leading every key, composite FKs; one default organization; Azure tenants are entities, never organization IDs; RLS evaluated in ATLAS-003 | Approved | — | Proposed | 0016 |
| D2 | Canonical ID (DEC-037) | UUIDv7, native `uuid`, application-generated, immutable; fixtures carry explicit IDs | Approved | — | Proposed | 0015 |
| D3 | Matching precedence (DEC-025) | Provider ID → approved alias → organization key; similarity only creates review candidates; ambiguity → no link plus a case | Approved | — | Proposed | 0003 |
| D4 | Azure identity (DEC-025) | Original + normalized ARM ID; rule `arm-1` (validate and reject, lowercase, no decoding); identity-change and collision rules | Clarify | **Yes** | Proposed | 0003 |
| D5 | Merge and split (DEC-025) | Reversible change sets; tombstones keep IDs; bindings closed, never deleted | Approved | Wording only (versions) | Proposed | 0003 |
| D6 | Taxonomy basis (DEC-050) | Tech §3.3 canonical, BRD terms as aliases; deviations C-01/C-02 recorded on confirmation; not frozen until confirmed | Amend | **Yes** | Proposed | 0017 |
| D7 | v1 types (DEC-050, DEC-070) | 29 types + `core.system` + `core.component`; environment scopes; re-typing with kept IDs; gaps G-T1…G-T11 | Amend | **Yes** | Proposed | 0017 |
| D8 | Data access (DEC-050) | Separate `READS_FROM` and `WRITES_TO`; `STORES_IN` = direction not established | Amend | **Yes** | Proposed | 0017 |
| D9 | `DEPENDS_ON` (DEC-050) | Curated only; human or documentation evidence only; rationale; paths never converted | Approved (with conditions) | Conditions written in | Proposed | 0017 |
| D10 | `PROTECTS` (DEC-050) | Reserved until security-control types exist | Approved | — | Proposed | 0017 |
| D11 | Containment (DEC-050) | `CONTAINS` hierarchical (one parent, acyclic, families never mixed); `MEMBER_OF` many-to-many, acyclic by construction; environment rules | Clarify | **Yes** | Proposed | 0017 |
| D12 | Unknown input (DEC-050) | Generic fallback with stated limits; non-matrix relationships rejected with reasons, never stored or downgraded; absence = coverage unknown | Clarify | **Yes** | Proposed | 0017 |
| D13 | Trust model (DEC-056) | Four dimensions; no runtime evidence kind; allowed evidence per relationship type | Approved | Alignment only | Proposed | 0018 |
| D14 | Conflicts (DEC-056) | Keep every assertion; prior approved value; `conflicted` plus a case; resolution closes losing assertions, never deletes | Approved | Wording only (validity intervals) | Proposed | 0018 |
| D15 | Revision model (DEC-031) | ADR-0008 revision 2: atomic, commit-ordered publication; immutable versions with set-once close; pointer snapshots with graph hash; endpoint validity; revert as a new change set | Amend | **Yes** | Proposed | 0008 |
| D16 | Store design (DEC-021) | Typed relational identity + version tables on PostgreSQL 15; no extensions; no graph database; bounded recursive CTEs | Approved | Columns follow D4/D8/D15 | Proposed | 0001 |
| D17 | Database privileges (DEC-021; amends DEC-044) | Dedicated `atlas_ingest` / `atlas_test_ingest`; `atlas_app` stays read-only; privilege matrix; nothing created until approved, then the server owner runs the script | Amend | **Yes** | Proposed (DEC-044 stays Confirmed as four roles until then) | 0001 |
| D18 | Bulk loading (DEC-021) | Validated `COPY` into target tables in one change set, as the ingestion role; Scale A data never on the shared server | Approved | Role name only | Proposed | 0001 |

**Choices that need an explicit answer** (beyond a yes to the table):

1. D7: add `core.system` and `core.component` (recommended), or not.
2. D7: G-T9 (non-Azure physical type) and G-T10 (application ↔ resource group): accept as v1 limits (recommended), or add now.
3. D17: approve the DEC-044 amendment (four → six roles). After that, the proposal script is written in CP3 and run only by you.

## Not decided here (stay as they are)

- **DEC-057** (discovery publication semantics): stays **Open**; ADR-0008 supports either policy.
- **DEC-073** (classification) and **DEC-051** (roles): stay **Open**; classification arrives with authorization (ATLAS-003).
- **DEC-034:** principles only (ADR-0003); per-field precedence values come with connectors (Phase 2).
- **DEC-066:** follows D13; stays **Open** for its UX grammar.
- **DEC-081** (named decision owners): stays **Open**. For these rows the Atlas owner is the approver.
- **DEC-084** and **E-07:** unchanged; no infrastructure or credential change.
- `pg_trgm` for search (BL-111): a later owner decision; D16 means no extensions in ATLAS-002.

## Effects of confirmation

- Register rows DEC-021, DEC-025, DEC-031, DEC-037, DEC-050, DEC-056, DEC-058 and DEC-070 go to **Confirmed**; DEC-044 is amended; ADRs 0001, 0003, 0008 and 0015–0018 go to Accepted.
- `baseline-deviations.md` gains C-01 and C-02 (and C-03 if the additions are declined).
- RTM readiness columns are regenerated (register §E).
- CP2 becomes authorizable. CP2 still creates no tables, runs no migration and changes no role.
