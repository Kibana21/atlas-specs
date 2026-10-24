# ATLAS-002 CP1 — Decision matrix (for owner approval)

**Date:** 24 October 2026 · **Status:** every row is **Proposed**. Nothing is approved and no canonical-graph code exists. On approval, the register rows move to Confirmed, the ADRs to Accepted, and CP2 can be authorized.

Approve, amend or reject **each row**. Where an alternative is listed, the recommended choice is first.

| # | Decision (register) | Recommended choice | Alternative(s) | Main trade-off | ADR |
|---|---|---|---|---|---|
| D1 | Tenancy (DEC-058) | One database; `organization` table; `org_id` on every row, leading every key, with composite FKs; one default organization now; Azure tenants are entities with a provider key **inside** an organization, never an organization ID | Database or schema per organization (C); add RLS on `org_id` now (D) | `org_id` everywhere (small cost) vs a rewrite later. RLS deferred to ATLAS-003 | 0016 |
| D2 | Canonical ID (DEC-037) | UUIDv7, native `uuid`, application-generated, immutable, never reused; fixtures carry explicit IDs; no name-derived IDs | UUIDv4; bigint + public UUID | Index locality vs a millisecond creation-time disclosure | 0015 |
| D3 | Matching precedence (DEC-025) | Provider ID → approved alias → organization key; **anything similarity-based only creates review candidates**; ambiguity or type conflict → no link plus a case | Probabilistic auto-merge above a threshold; manual-only identity | Determinism and reversibility vs fewer automatic links | 0003 |
| D4 | Azure identity (DEC-025) | Normalized ARM Resource ID (lowercase) as the preferred Azure key. A changed ARM ID links automatically only via an independent stable key (e.g. `k8s.uid`, `resourceGuid`), otherwise via steward review. Same ARM ID recreated = same entity unless a stable secondary key differs | Treat every new ARM ID as a new entity; auto-link moves by name and type | Safety vs some manual review after moves | 0003 |
| D5 | Merge and split (DEC-025) | Reversible change sets; loser kept as a tombstone with `merged_into`; identities superseded, never deleted | Physical merge (delete the loser) | Complete history vs simpler tables | 0003 |
| D6 | Taxonomy basis (DEC-050) | Tech §3.3 catalog canonical; BRD INV-02 terms as documented aliases; record the INV-02 deviation on approval (baseline not edited) | BRD INV-02 verbatim; open vocabulary | Richer semantics vs BRD wording | 0017 |
| D7 | v1 entity types (DEC-050, DEC-070) | 29 types (ADR-0017 §2): business, application, integration, data, environment; Azure MVP set (APIM, AKS, Service Bus, SQL, Key Vault, VNet/subnet, Storage, App Service) + tenant, subscription, resource group; `azure.generic_resource` fallback | Larger v1 (Front Door, Cosmos DB, NSG, Firewall…) | Small, verifiable v1 vs fewer generic objects | 0017 |
| D8 | `READS` / `WRITES` (DEC-050) | `STORES_IN` with required `access_mode` (read, write, read_write, unknown) | Separate `READS` and `WRITES` relationship types | One edge per pair vs BRD names | 0017 |
| D9 | `DEPENDS_ON` (DEC-050) | Keep as a **curated-only** generic edge between logical types, with required rationale; never from connectors or inference | Drop `DEPENDS_ON` entirely | BRD coverage vs a possible catch-all | 0017 |
| D10 | `PROTECTS` (DEC-050) | **Reserved** (defined, no allowed pairs) until security-control types exist | Add NSG, Azure Firewall, WAF and private-endpoint types now and enable `PROTECTS` | No invented pairs vs earlier security modeling | 0017 |
| D11 | Containment and environment rules (DEC-050) | One `CONTAINS` parent; acyclic; parent types per table; same environment when both are environment-specific; cross-environment edges only for five types, flagged and evidenced; `CONTAINS`/`DEPLOYED_AS` never cross-environment | Allow multiple parents (DAG) | Simple hierarchy vs modeling shared containers | 0017 |
| D12 | Unknown input (DEC-050) | Unsupported ARM type → `azure.generic_resource`; a non-matrix relationship is rejected with a reason and never stored or downgraded; absence = coverage unknown; fixtures never invent edges | Coerce into the nearest type or `DEPENDS_ON` | Truthfulness vs connectivity | 0017 |
| D13 | Trust model (DEC-056) | Four orthogonal dimensions: evidence kind (`provider_configuration`, `contract`, `documentation`, `human_assertion`, `inferred`; **no runtime/traffic kind**), trust state (tech §3.4 list), verification (with expiry → stale), completeness (`present`, `not_documented`, `not_applicable`, `unknown_coverage`). Evidence ledger per fact | One combined status; entity-level provenance only | Expressiveness vs simplicity | 0018 |
| D14 | Conflicts (DEC-056) | Keep every assertion; keep the prior approved value; fact `conflicted` plus a case; a steward's resolution is a new assertion; "not seen" ≠ removal | Last-writer-wins; highest-confidence-wins | No silent collapse vs extra steward work | 0018 |
| D15 | Revision model (DEC-031) | Append-only version rows over a per-organization revision counter; one change set per transaction; snapshots = immutable pointers plus a deterministic graph hash; no physical deletion | Temporal tables (triggers or extension); snapshot copies; event sourcing | Plain PostgreSQL 15, cheap snapshots vs history growth and a per-organization write lock | 0008 |
| D16 | Canonical store design (DEC-021) | Typed relational graph: identity + version tables, JSONB type attributes, composite org FKs, partial indexes, `container_id` denormalized; **no extensions, no graph database**; bounded recursive CTEs | Generic node/edge JSONB; `ltree` containment (extension) | Integrity and indexability vs a join per read | 0001 |
| D17 | Runtime-role privileges (extends FR-28) | Per-table grants: INSERT; `UPDATE` only on `revision_to`, `merged_into` and `org_revision.last`; no DELETE or TRUNCATE; evidence insert-only | Writes through a separate "writer" role | Least privilege within the existing four roles vs a fifth role (would change shared-server roles) | 0001 |
| D18 | Bulk loading (DEC-021) | Validate in the application, then `COPY` into target tables inside one change set (no temp tables); Scale A data never on the shared server without approval | Row-by-row inserts; staging tables | Speed vs simplicity | 0001 |

## Not decided here (stay as they are)

- **DEC-057** (discovery publication semantics): stays **Open**; ADR-0008 supports either policy.
- **DEC-073** (classification) and **DEC-051** (roles): stay **Open**; classification is added with authorization (ATLAS-003).
- **DEC-034:** principles only (ADR-0003); per-field precedence values come with connectors (Phase 2).
- **DEC-066:** follows D13 (unknown coverage at entity level, never a drawn edge); stays **Open** for its UX grammar.
- **DEC-081** (named decision owners): stays **Open**. For these rows the Atlas owner is the approver.
- **DEC-084** and **E-07:** unchanged; no infrastructure or credential change.

## Effects of approval

- The register rows above go to **Confirmed**; ADRs 0001, 0003, 0008 and 0015–0018 go to Accepted.
- `baseline-deviations.md` gains the BRD INV-02 vocabulary deviation (D6/D8/D9/D10).
- The RTM readiness columns were already regenerated when these rows became Proposed (register §E; the registry check enforces it): R0 177 → 124. R1/R2 mean "no *Open* decision", not approval. Nothing is built on a Proposed decision.
- CP2 becomes authorizable.
