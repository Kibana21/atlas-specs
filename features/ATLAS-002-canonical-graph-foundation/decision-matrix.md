# ATLAS-002 CP1 — Decision matrix (for final owner confirmation)

**Version:** revision 3 · **Date:** 25 October 2026 · **Status:** every row is still **Proposed** in the register. The owner reviewed revision 1 (verdicts in §1) and accepted revision 2's direction, then asked for a provider-agnostic review (§2). Register rows move to Confirmed, and the ADRs to Accepted, only when the owner gives final CP1 approval (Gate G1). No canonical-graph code, table, migration, role, privilege or connector exists.

## 1. Owner reviews

| Date | Review | Verdicts |
|---|---|---|
| 25 Oct 2026 | Revision 1 | Approved: D1, D2, D3, D5, D9, D10, D13, D14, D16, D18 (subject to consistency with the authoritative specifications). Clarify: D4, D11, D12. Amend: D6, D7, D8, D15, D17. CP0 accepted |
| 25 Oct 2026 | Revision 2 (PR #15) | Identity, data access, containment, provenance, revision consistency and least-privilege ingestion **directionally accepted**. `core.system` and `core.component` **approved**. `CONTAINS`/`MEMBER_OF` separation kept. D17's ingestion roles acceptable in principle; DEC-044 amendment to be prepared. Provider-agnostic final review requested before confirmation |

## 2. Revision 3: provider-agnostic review

**Requirement (owner, 25 Oct 2026):** represent Azure, AWS, Google Cloud, Alibaba Cloud, OCI, Huawei Cloud, Tencent Cloud, IBM Cloud, private clouds, on-premises infrastructure and custom technologies; Azure first; no other connector in ATLAS-002. This implements the BRD's "technology-neutral underlying model" and DEC-004 (Confirmed). It does not reopen any scope exclusion.

| Owner requirement | Answer | Where |
|---|---|---|
| Provider-qualified native identities with uniqueness scopes | Namespace registry: one namespace per provider identifier format, each with format, normalizer, case rule and the provider scope its key must embed; uniqueness is always `(org_id, namespace, normalized_key)`. Case folded only where documented (Azure) | ADR-0003 §Provider-qualified namespaces |
| Provider-neutral categories | 15 physical categories (scope, cluster, workload, compute host, API endpoint, data store, messaging channel, …); every type belongs to one | ADR-0019 §2 |
| Provider-specific types and attributes | `azure.*` now; others only when needed. `provider`, `native_type`, `platform`, validated `provider_attributes` on every physical entity | ADR-0019 §3, ADR-0017 §2.1 |
| Extensible, versioned taxonomy | Providers, categories, namespaces and `native_type → category` mappings are taxonomy reference data (MINOR additions) | ADR-0017 §1, ADR-0019 |
| Different account and resource hierarchies | `infra.scope` with per-provider `scope_kind` nesting rules; physical containment within one provider | ADR-0019 §4 |
| Cross-provider relationships | Rules are written against categories, so they apply across providers; computed `cross_provider` flag; one-sided evidence recorded as such | ADR-0019 §6, ADR-0017 §4 |
| Provider-neutral provenance, trust, revisions | No provider dependency; `provider_configuration` covers any provider or platform | ADR-0018, ADR-0008 |
| Logical and physical components | `core.*` logical (incl. `core.component`); physical per provider; `DEPLOYED_AS` the only bridge | ADR-0017 §3, §4 |
| Facts separate from visualization | No presentation columns in canonical tables; icons derived from category | ADR-0001, ADR-0019 §7 |
| No table redesign for a new provider; no plugin runtime | A new provider = reference rows + one reviewed normalizer per namespace | ADR-0019 §Onboarding |
| Six synthetic scenarios | Entity types, identifiers, relationships, containment and membership, evidence and trust, revisions for each | ADR-0019 §Scenarios S1–S6 |

## 3. G-T9, G-T10 and additional types

| Item | Resolution |
|---|---|
| **G-T9** non-Azure physical deployments | **Closed.** The minimum provider-neutral abstraction is **eight `infra.*` types**: `infra.scope`, `infra.compute`, `infra.cluster`, `infra.workload`, `infra.api_endpoint`, `infra.messaging_channel`, `infra.data_store` and the fallback `infra.resource`, which replaces `azure.generic_resource`. They exist only for categories that are endpoints of semantic rules, plus hierarchy and fallback. Kubernetes types now work on any provider's cluster. A single `infra.resource` with a `category` attribute was evaluated and rejected (rules would depend on an attribute) |
| **G-T10** application ↔ resource group | **Closed: not a gap.** No direct relationship: it would be logical-contains-physical, Azure-specific and unevidenced. "Where is this application deployed?" is a bounded read-time traversal (`DEPLOYED_AS` → physical → `CONTAINS` ancestors), labeled derived and never stored. Teams can `OWNS` a resource group; tags are future review inputs only (ADR-0017 §7.5) |
| Additional types | `core.system`, `core.component` (approved) and the eight `infra.*` types. **No other type is essential now**: gateways, brokers, database servers, secret stores, networks and subnets outside Azure use `infra.resource` (G-T12); provider-specific catalogs wait for onboarding (G-T13). Azure's MVP set is unchanged. Total: **38 types** (12 logical, 16 Azure, 2 Kubernetes, 8 neutral) |

## 4. Consistency with the BRD, UX and Technical baselines

None of these is resolved by editing a baseline. Deviations are recorded in `decisions/baseline-deviations.md` only on final confirmation.

| # | Baseline statement | This proposal | Kind | Rows |
|---|---|---|---|---|
| C-01 | BRD INV-02 relationship names | Tech names with documented aliases; `HOSTED_IN` becomes `CONTAINS` (**inverse**); `PROTECTS` defined, no pairs yet | **Deviation** | D6, D8, D10 |
| C-02 | Tech §3.3 catalog | Adds `READS_FROM`, `WRITES_TO`, `MEMBER_OF`, `DEPENDS_ON`, `PROTECTS`; narrows `CONTAINS` and `STORES_IN` | **Deviation** | D6, D8, D9, D11 |
| C-03 | BRD MOD-01 names system, container, component | `core.system`, `core.component` (owner-approved) | Resolved | D7 |
| C-04 | BRD INV-05 shared infrastructure | `environment_scope = shared` + `MEMBER_OF` environments | Resolved | D7, D11 |
| C-05 | Tech §3.4 lifecycle values | Used exactly; removal is `record_state` | Consistent | D7, D15 |
| C-06 | Tech §3.5 illustrative tables | Identity + version tables, `external_identity`, `evidence` + `fact_assertion`; classification waits for DEC-073 | Interpretation (recorded) | D15, D16 |
| C-07 | Tech §3.2 "ARM IDs with subscription/tenant scope" | Subscription in the key; tenant as modeled containment | Interpretation (recorded) | D4 |
| C-08 | DEC-044 (Confirmed, four roles); ATLAS-001 FR-28 | Six roles; canonical write grants to the ingestion role (`proposals/dec-044-amendment.md`) | **Amendment of a Confirmed decision** | D17 |
| C-09 | Tech §3.1 further types | Phased (G-T7) | Consistent with tech §18 | D7 |
| C-10 | DEC-004 (Confirmed), BRD "technology-neutral underlying model", UX "do not force Azure hierarchy onto on-prem systems" | Revision 2 had no non-Azure physical type. Revision 3: categories, `infra.*` types, provider hierarchies | **Resolved in revision 3** | D7, D19 |
| C-11 | UX "Verified" badge; BRD DEP-04; BRD E16 Passport "read/write links" | Verification dimension; evidence kinds; separate read and write records | Consistent | D8, D13 |
| C-12 | Tech §10 published baselines and branches | Every change set published in ATLAS-002; branches later; DEC-057 Open | Consistent (deferred) | D15 |
| C-13 | Tech §7 connectors are Azure-first; BRD E20 exclusions | No connector of any provider in ATLAS-002; no telemetry or traffic evidence for any provider | Consistent | D19 |
| C-14 | Tech §3.2 "AKS objects use cluster identity + Kubernetes UID" | Generalized to any cluster: `{cluster namespace}:{cluster key}#{uid}` | Consistent extension | D4, D19 |

No conflict was found with the UX baseline.

## 5. Final decision matrix (D1–D18, plus D19)

"Register" is the current status; nothing moves until final approval.

| # | Decision (register) | Final recommendation | Owner so far | Changed in rev 3 | Register | ADR |
|---|---|---|---|---|---|---|
| D1 | Tenancy (DEC-058) | One database; `org_id` leading every key, composite FKs; one default organization; **every provider's accounts** (Azure tenants, AWS organizations and accounts, GCP organizations and projects, OCI tenancies…) are entities inside an organization, never organization IDs; RLS evaluated in ATLAS-003 | Approved | Wording (all providers) | Proposed | 0016 |
| D2 | Canonical ID (DEC-037) | UUIDv7, native `uuid`, application-generated, immutable; fixtures carry explicit IDs | Approved | — | Proposed | 0015 |
| D3 | Matching precedence (DEC-025) | Provider ID → approved alias → organization key, identical for every provider; similarity only creates review candidates; ambiguity → no link plus a case | Approved | Provider-neutral wording | Proposed | 0003 |
| D4 | External identity (DEC-025) | Original + normalized keys for **every** namespace; provider-qualified namespace registry with embedded uniqueness scopes; case folded only where documented (Azure `arm-1`); identity-change and collision rules generalized | Directionally accepted | **Yes** | Proposed | 0003 |
| D5 | Merge and split (DEC-025) | Reversible change sets; tombstones keep IDs; bindings closed, never deleted | Approved | — | Proposed | 0003 |
| D6 | Taxonomy basis (DEC-050) | Tech §3.3 canonical, BRD aliases; deviations C-01/C-02; taxonomy carries providers, categories, namespaces and mappings as versioned reference data | Directionally accepted | **Yes** | Proposed | 0017, 0019 |
| D7 | v1 types (DEC-050, DEC-070) | 38 types: 12 logical (incl. approved `core.system`, `core.component`), Azure MVP set (16), Kubernetes (2, any provider), 8 provider-neutral `infra.*`; environment scopes; re-typing with kept IDs | `core.system`/`core.component` approved | **Yes** | Proposed | 0017, 0019 |
| D8 | Data access (DEC-050) | Separate `READS_FROM`, `WRITES_TO`; `STORES_IN` = direction not established | Directionally accepted | Targets by category | Proposed | 0017 |
| D9 | `DEPENDS_ON` (DEC-050) | Curated only; human or documentation evidence; rationale; paths never converted | Approved | — | Proposed | 0017 |
| D10 | `PROTECTS` (DEC-050) | Reserved until security-control types exist | Approved | — | Proposed | 0017 |
| D11 | Containment (DEC-050) | `CONTAINS` hierarchical (one parent, acyclic, families never mixed, physical within one provider); `MEMBER_OF` many-to-many, acyclic by construction | Separation kept by owner | Within-provider rule | Proposed | 0017 |
| D12 | Unknown input (DEC-050) | Neutral type of the mapped category, else `infra.resource` with stated limits; non-matrix relationships rejected, never stored or downgraded; absence = coverage unknown | Directionally accepted | **Yes** (fallback) | Proposed | 0017 |
| D13 | Trust model (DEC-056) | Four dimensions; no runtime evidence kind; allowed evidence per relationship type; provider-neutral sources | Approved | Wording | Proposed | 0018 |
| D14 | Conflicts (DEC-056) | Keep every assertion; prior approved value; `conflicted` + case; resolution closes losing assertions | Approved | — | Proposed | 0018 |
| D15 | Revision model (DEC-031) | Atomic, commit-ordered publication; immutable versions with set-once close; pointer snapshots with graph hash; endpoint validity; revert as a new change set | Directionally accepted | — | Proposed | 0008 |
| D16 | Store design (DEC-021) | Typed relational identity + version tables on PostgreSQL 15; provider-neutral reference tables; no extensions; no graph database | Approved | Reference tables, columns | Proposed | 0001 |
| D17 | Database privileges (DEC-021; **amends DEC-044**) | `atlas_ingest` / `atlas_test_ingest`; `atlas_app` read-only; grant matrix; owner-run bootstrap; rollback | Acceptable in principle | Exact amendment written | Proposed (DEC-044 stays four roles until approved) | 0001; `proposals/dec-044-amendment.md` |
| D18 | Bulk loading (DEC-021) | Validated `COPY` in one change set, as the ingestion role; Scale A data never on the shared server | Approved | — | Proposed | 0001 |
| **D19** | **Provider-neutral model (implements DEC-004)** | Categories; provider-specific types only where needed; eight `infra.*` types; provider reference data; per-provider hierarchies; cross-provider rules; onboarding without table changes or a plugin runtime | New in rev 3 | **New** | n/a (DEC-004 Confirmed; annotated) | 0019 |

## 6. Remaining architecture trade-offs

| Trade-off | Accepted cost | Mitigation |
|---|---|---|
| Neutral types are coarse | Lambda and ECS service are both `infra.workload` | Provider-specific types when needed; IDs survive re-typing |
| Category-based rules are permissive across providers | Any workload may consume any API endpoint | Evidence is still required for every fact |
| Case preserved for non-Azure keys | Possible duplicate identities where a provider is case-insensitive but undocumented | Reversible steward merge |
| One-sided cross-provider evidence | Facts rarely `verified` | Honest by design (invariant 3) |
| `infra.resource` outside Azure for gateways, brokers, networks | Not rule sources | Add neutral types when a rule needs them (G-T12) |
| Per-organization write lock | One writer per organization at a time | Batched change sets; measured in CP4 |
| Identity/version tables | One join per read; history growth | Partial indexes; measured in CP4 |
| No extensions | No fuzzy search in ATLAS-002 | Separate `pg_trgm` decision later |
| Local `trust` authentication | Ingestion-role separation is enforced only in CI | DEC-084 remains the owner's decision |

## 7. Onboarding a new provider later

Taxonomy MINOR (provider key, `scope_kind` rules, `native_type → category` mapping, optional attribute schema and optional provider-specific types) → identity namespace with golden examples → one reviewed normalizer per namespace in the backend → reference-data seed (no DDL) → synthetic fixtures and tests → later, separately approved, a read-only connector. No table changes, no plugin runtime, no new infrastructure. Details: ADR-0019 §Onboarding.

## 8. Platform confirmations

- **PostgreSQL 15 remains sufficient.** Everything uses B-tree and partial indexes, composite FKs, `NULLS NOT DISTINCT` (15), `jsonb`, recursive CTEs, PL/pgSQL triggers, column privileges and `COPY`. No extension and nothing from 16+ (ADR-0001 §PostgreSQL 15 remains sufficient).
- **No additional infrastructure is needed:** no graph database, search engine, broker, object store, cache, new Redis usage or new service. The only proposed server-level change is the two ingestion roles, run by the owner after approval.

## Not decided here (stay as they are)

- **DEC-057** (discovery publication): **Open**.
- **DEC-073** (classification), **DEC-051** (roles): **Open**; with authorization (ATLAS-003).
- **DEC-034:** principles only; per-field precedence with connectors (Phase 2).
- **DEC-066:** **Open** for its UX grammar.
- **DEC-081** (named decision owners): **Open**; the Atlas owner approves these rows.
- **DEC-084**, **E-07:** unchanged.
- **DEC-061** (visual assets, for example provider logos): unchanged.
- `pg_trgm` for search (BL-111): later decision.

## Effects of final approval

- DEC-021, DEC-025, DEC-031, DEC-037, DEC-050, DEC-056, DEC-058 and DEC-070 → **Confirmed**; DEC-044 amended (§2 of the amendment); DEC-004 annotated with ADR-0019; ADRs 0001, 0003, 0008 and 0015–0019 → Accepted.
- `baseline-deviations.md` gains C-01 and C-02.
- RTM readiness regenerated (register §E).
- CP2 becomes authorizable. CP2 still creates no tables, runs no migration and changes no role.
