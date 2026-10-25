# ADR-0017 — Canonical taxonomy and relationship vocabulary v1

| Field | Value |
|---|---|
| Status | **Accepted** (owner, 25 Oct 2026: ATLAS-002 CP1 final approval of D1–D19). Drafting history: Revision 4 (25 Oct 2026, compatibility gate): extensible environment kinds incl. `sit`, `dr`, `preprod`; optional `deployment_role` on `DEPLOYED_AS` (§2.5). Revision 3 (25 Oct 2026): provider-neutral categories and types (ADR-0019). Revision 2 (25 Oct 2026) followed the owner's CP1 review; revision 1 was 24 Oct 2026. **Not frozen**: the taxonomy is fixed only when the owner confirms this ADR, and the artifact is produced in CP2 after that |
| Register | DEC-050, DEC-070 (**Confirmed** 25 Oct 2026) |
| Owner (proposed) | Enterprise Architecture + Cloud Platform; approval: Atlas owner |
| Related | INV-01, INV-02, INV-05, MOD-01, MOD-03, MOD-04, BCM-01, BCM-03, DEP-01, DEP-04, CAN-02, E04; tech §3.1, §3.2, §3.3; ADR-0001, ADR-0003, ADR-0008, ADR-0018, ADR-0019 |

## Owner review of revision 1 (25 Oct 2026)

| Row | Owner decision | What changed in revision 2 |
|---|---|---|
| D6 Taxonomy basis | Amend: show the complete catalog, required attributes and matrix; demonstrate coverage; list gaps; do not freeze | §2–§4 complete catalog and matrix; §6 worked coverage; §7 gaps and limits |
| D7 v1 types | Amend (as D6) | Two types proposed **in addition** to the 29 (`core.system`, `core.component`) because MOD-01 names them; `type_key` moves to the version row so a generic resource can be re-typed with its ID kept |
| D8 Data access | Amend: keep reading and writing distinct | `READS_FROM` and `WRITES_TO` are separate relationship records; `STORES_IN` narrowed to "direction not established" (§5) |
| D9 `DEPENDS_ON` | Approved; require explicit provenance; never convert graph paths automatically | §4.3 provenance rules, enforced by the allowed-evidence column |
| D10 `PROTECTS` | Approved (reserved) | Unchanged |
| D11 Containment | Approve with clarification: physical containment vs logical membership | `CONTAINS` (hierarchical, single parent, acyclic) and new `MEMBER_OF` (logical, many-to-many, acyclic by construction) (§3) |
| D12 Unknown input | Approve with clarification | Generic-fallback limits stated (§7.2); re-typing rule (§2.4) |

**Final review (25 Oct 2026, revision 3):** the owner accepted revision 2's direction, **approved `core.system` and `core.component`**, kept `CONTAINS` vs `MEMBER_OF`, and asked for a provider-agnostic model (Azure, AWS, Google Cloud, Alibaba Cloud, OCI, Huawei Cloud, Tencent Cloud, IBM Cloud, private clouds, on-premises, custom technologies). Revision 3:

- every type belongs to a provider-neutral **category**, and relationship rules are written against categories (ADR-0019 §2);
- eight provider-neutral physical types `infra.*` (§2.2 rows 31–38) replace `azure.generic_resource`, which closes G-T9;
- Kubernetes types work on any provider's cluster;
- G-T10 is closed as "not a gap": no direct application ↔ resource-group relationship (§7.5).

## Problem

The two baselines disagree:

- **BRD INV-02** lists `CALLS_API, PUBLISHES, CONSUMES, READS, WRITES, DEPLOYED_ON, HOSTED_IN, OWNS, DEPENDS_ON, PROTECTS`.
- **Tech §3.3** lists `CONTAINS, SUPPORTS_CAPABILITY, EXPOSES_API, CONSUMES_API, PUBLISHES_TO, SUBSCRIBES_TO, STORES_IN, DEPLOYED_AS, CONNECTS_TO, OWNS, PRODUCES_DATA/CONSUMES_DATA, DECIDED_BY`.

MOD-01 and MOD-03 need a **versioned** type list with required attributes, allowed parent/child pairs and relationship rules that reject invalid input with a readable reason. MOD-01 names the types: capability, domain, application, system, container, component, API, data asset, deployment and cloud resource. E04 says unsupported resource types are kept as generic typed objects.

**Owner direction (24 Oct 2026):** cover the approved MVP Azure types and architectural concepts; define compatibility, required attributes, containment, extension/versioning and unknown types; **do not invent relationships to make a fixture connected**.

## Options

| Option | Verdict |
|---|---|
| **A. Tech §3.3 catalog as canonical, BRD terms as documented aliases**, plus explicit decisions on the BRD-only terms | **Recommended**: keeps containment, capability and ownership semantics that INV-02 lacks; every BRD term maps to a defined meaning |
| B. BRD INV-02 verbatim | Rejected: no containment or capability support, ambiguous `CONSUMES` (API or topic), and `DEPLOYED_ON`/`HOSTED_IN` overlap |
| C. Open vocabulary (free-form types in JSONB) | Rejected: no validation (violates MOD-01/03), and invites invented edges |

## 1. Structure and versioning

- **Source of truth:** a versioned artifact in atlas-specs, `contracts/taxonomy/atlas-taxonomy.v1.json`. It is produced in **CP2, after this ADR is confirmed**, with a JSON Schema and valid/invalid examples.
- **Versioning (semver):**
  - MINOR adds types, relationship types, allowed pairs, enumeration values or optional attributes;
  - MAJOR removes or renames anything, narrows a rule, or makes an attribute required;
  - every MAJOR needs a data migration plan and owner approval.
- **Stable keys:** `type_key` is namespaced lowercase (`core.application`, `azure.key_vault`); `rel_type` is upper snake case (`CONSUMES_API`). Keys are never reused once published. Deprecated keys stay readable and stop being writable.
- **Pinning:** the backend pins the taxonomy through `specs.lock`. Migrations seed the reference tables from the pinned artifact, and a CI check compares seed and artifact (as `make contract` does for OpenAPI).
- **Recorded version:** every entity and relationship version records the taxonomy version it was validated against.
- **Providers, categories and identity namespaces** are reference data in the same artifact (ADR-0019 §1–§2, ADR-0003). A new provider is a MINOR version.
- **Taxonomy self-checks (CI, CP2):** every type is reachable by at least one rule or is explicitly standalone; the type-level `MEMBER_OF` graph is acyclic (§3.2); the `CONTAINS` parent table is acyclic at type level except declared self-nesting types (§3.1); every alias in §8 maps to a defined type.

## 2. Entity types (v1 candidate: 38)

### 2.1 Attributes every type has

| Attribute | Rule |
|---|---|
| `display_name` | Required, 1–200 characters. Never an identity (ADR-0003) |
| `lifecycle` | Required: `active`, `deprecated` or `retired` (exactly tech §3.4's list; business lifecycle). Planned or proposed things belong in drafts (tech §10), not in the published graph |
| `record_state` | System-managed: `present`, `removed` (tombstone) or `merged` (ADR-0008). Not the same as lifecycle: a retired application is still present |
| `environment_scope` | Required for types marked **E**, optional for **O**, absent for **N** (§2.3) |
| `description` | Optional |
| `provider` | Physical types only, required (ADR-0019 §1). `k8s.*` take their cluster's provider |
| `native_type` | Physical types only, required: the provider's own type string; fixed per type for `azure.*` (formerly `azure_type`) |
| `platform` | Required for providers `private_cloud`, `on_premises`, `other` (ADR-0019 §3) |
| `provider_attributes` | Optional, validated by a provider profile where one exists, never used by rules (ADR-0019 §3) |

### 2.2 Catalog

**Env:** **E** = environment-scoped, **O** = optional scope, **N** = environment-neutral. **Kind:** **L** = logical, **P** = physical (resource). **Category:** ADR-0019 §2; logical types are their own category. Parent = the allowed `CONTAINS` parent (§3.1); "—" means the type has no containment parent and is a root.

| # | Layer | `type_key` | Category | Kind | Env | Required attributes (beyond §2.1) | Identity namespaces (ADR-0003) | `CONTAINS` parent |
|---|---|---|---|---|---|---|---|---|
| 1 | Business | `core.capability` | own | L | N | — | `org.key` (optional) | `core.capability` |
| 2 | Business | `core.business_domain` | own | L | N | — | `org.key` (optional) | `core.business_domain` |
| 3 | Ownership | `core.team` | own | L | N | — | `org.key` (optional) | — |
| 4 | Application | `core.system` **(added; owner-approved 25 Oct 2026)** | own | L | N | — | `org.key` (optional) | — |
| 5 | Application | `core.application` | own | L | N | `org_key` | `org.key` | — |
| 6 | Application | `core.service` (logical service; C4 "container") | own | L | N | — | `org.key` (optional) | `core.application` |
| 7 | Application | `core.component` **(added; owner-approved 25 Oct 2026)** | own | L | N | — | `org.key` (optional) | `core.service` |
| 8 | Integration | `core.api` (logical API, DEP-01) | own | L | N | `api_version` | `org.key` (optional) | — |
| 9 | Integration | `core.api_operation` | own | L | N | `http_method`, `path_template` | — | `core.api` |
| 10 | Integration | `core.event_channel` (logical topic or queue) | own | L | N | `channel_kind` ∈ {queue, topic} | `org.key` (optional) | — |
| 11 | Data | `core.dataset` (logical data asset) | own | L | N | — | `org.key` (optional) | — |
| 12 | Deployment | `core.environment` | own | L | N | `environment_kind` from the taxonomy vocabulary (v1: dev, sit, test, uat, preprod, prod, dr, sandbox, other; extended by MINOR versions); the environment's name and key are organization-defined | `org.key` | — |
| 13 | Azure | `azure.tenant` | `scope` | P | N | — | `azure.tenant_id` | — |
| 14 | Azure | `azure.subscription` | `scope` | P | O | — | `azure.subscription_id`, `azure.arm` | `azure.tenant` |
| 15 | Azure | `azure.resource_group` | `scope` | P | O | `location` | `azure.arm` | `azure.subscription` |
| 16 | Azure | `azure.apim_service` | `api_gateway` | P | E | `location`, `sku` | `azure.arm` | `azure.resource_group` |
| 17 | Azure | `azure.apim_api` (an API published in one APIM instance) | `api_endpoint` | P | E | `api_revision` | `azure.arm`, `apim.api` | `azure.apim_service` |
| 18 | Azure | `azure.aks_cluster` | `container_cluster` | P | E | `location`, `kubernetes_version` | `azure.arm` | `azure.resource_group` |
| 19 | Kubernetes | `k8s.namespace` | `container_namespace` | P | E | — | `k8s.uid` | `azure.aks_cluster`, `infra.cluster` |
| 20 | Kubernetes | `k8s.workload` | `runtime_workload` | P | E | `workload_kind` ∈ {Deployment, StatefulSet, DaemonSet, CronJob, Job, other} | `k8s.uid` | `k8s.namespace` |
| 21 | Azure | `azure.app_service` (Web App or Function App) | `runtime_workload` | P | E | `location`, `site_kind` ∈ {app, functionapp, other} | `azure.arm` | `azure.resource_group` |
| 22 | Azure | `azure.service_bus_namespace` | `messaging_broker` | P | E | `location`, `sku` | `azure.arm` | `azure.resource_group` |
| 23 | Azure | `azure.service_bus_queue` | `messaging_channel` | P | E | — | `azure.arm` | `azure.service_bus_namespace` |
| 24 | Azure | `azure.service_bus_topic` | `messaging_channel` | P | E | — | `azure.arm` | `azure.service_bus_namespace` |
| 25 | Azure | `azure.sql_server` | `database_server` | P | E | `location` | `azure.arm` | `azure.resource_group` |
| 26 | Azure | `azure.sql_database` | `data_store` | P | E | — | `azure.arm` | `azure.sql_server` |
| 27 | Azure | `azure.storage_account` | `data_store` | P | E | `location`, `sku` | `azure.arm` | `azure.resource_group` |
| 28 | Azure | `azure.key_vault` | `secret_store` | P | E | `location` | `azure.arm` | `azure.resource_group` |
| 29 | Azure | `azure.vnet` | `network` | P | E | `location` | `azure.arm` | `azure.resource_group` |
| 30 | Azure | `azure.subnet` | `subnet` | P | E | — | `azure.arm` | `azure.vnet` |
| 31 | Neutral | `infra.scope` (provider account or hierarchy node; ADR-0019 §4) | `scope` | P | O | `provider`, `scope_kind` (per provider profile) | provider namespace (for example `aws.account`, `gcp.resource_name`, `oci.ocid`) or `source.*` | `infra.scope` (same provider, nesting per profile) |
| 32 | Neutral | `infra.compute` (VM, instance, physical host) | `compute_host` | P | E | `compute_kind` ∈ {vm, bare_metal, physical, other}, `location` | provider namespace or `source.*` | scope-category type (same provider) |
| 33 | Neutral | `infra.cluster` (container orchestration cluster: EKS, GKE, OKE, ECS, on-premises Kubernetes…) | `container_cluster` | P | E | `cluster_kind` ∈ {kubernetes, ecs, other}, `location` | provider namespace or `source.*` | scope-category type (same provider) |
| 34 | Neutral | `infra.workload` (function, container service, service process) | `runtime_workload` | P | E | `workload_kind` ∈ {function, container_service, process, other} | provider namespace or `source.*` | scope-category type, `infra.compute`, `infra.cluster` (same provider) |
| 35 | Neutral | `infra.api_endpoint` (API on a gateway or platform) | `api_endpoint` | P | E | — | provider namespace or `source.*` | scope-category type, `infra.resource` (gateway) (same provider) |
| 36 | Neutral | `infra.messaging_channel` (queue, topic, stream) | `messaging_channel` | P | E | `channel_kind` ∈ {queue, topic, stream} | provider namespace or `source.*` | scope-category type, `infra.resource` (broker) (same provider) |
| 37 | Neutral | `infra.data_store` (database, bucket, file share, cache) | `data_store` | P | E | `store_kind` ∈ {relational_db, nosql_db, object_storage, file_storage, cache, other} | provider namespace or `source.*` | scope-category type, `infra.compute`, `infra.resource` (server) (same provider) |
| 38 | Neutral | `infra.resource` (fallback for any provider, E04; replaces revision 2's `azure.generic_resource`) | `generic` | P | O | — (`native_type` from §2.1) | provider namespace or `source.*` | any physical type of the same provider, only where the provider's native hierarchy shows it |

- For every `azure.*` type, `native_type` is the fixed ARM type (for example `microsoft.sql/servers/databases`). ADR-0003 uses it to reject a type-incompatible match.
- **`core.system` and `core.component`** were approved by the owner on 25 Oct 2026 (MOD-01 names them).
- **Choosing a type for a physical resource:** a provider-specific type if one exists; otherwise the neutral type of the resource's category from the provider profile's `native_type → category` mapping; otherwise `infra.resource`. An Azure VM in v1 is therefore `infra.compute` with provider `azure`, not a generic object.
- No other provider-neutral types are essential now (ADR-0019 §2: neutral types exist only for categories that are endpoints of semantic rules, plus scope and the fallback).
- C4 "container" maps to `core.service`, "data asset" to `core.dataset`, "deployment" to the physical `DEPLOYED_AS` targets, and "cloud resource" to the `azure.*` and `infra.*` types.
- No secrets, connection strings, keys or message payloads are ever attributes (DEC-010). Address ranges and other network detail are not v1 attributes: they wait for classification (DEC-073).

### 2.3 Environment scope (INV-05, MOD-04)

| `environment_scope` | Meaning | How it is stored |
|---|---|---|
| `single` | The resource belongs to exactly one environment | `environment_id` → a `core.environment` entity |
| `shared` | One resource serves several environments, for example one APIM instance for test and UAT (INV-05 "shared infrastructure") | No `environment_id`; one evidenced `MEMBER_OF` → `core.environment` per served environment (§3.2) |
| `unknown` | The source does not say | Completeness `unknown_coverage` (ADR-0018). Never defaulted to prod or any other value |

Revision 1 made every E type require exactly one environment. That could not represent shared infrastructure, so revision 2 adds `shared`.

### 2.4 Re-typing and type upgrades

- `type_key` is stored on the **version** row, not the identity row (ADR-0001, ADR-0008), so the ID never changes (MOD-01 "existing IDs survive taxonomy upgrades").
- Allowed automatically: an `infra.*` type → a later provider-specific type (same provider) whose `native_type` equals the resource's, in a later MINOR taxonomy version; and `infra.resource` → the neutral type of a newly mapped category. It is one change set that re-validates every relationship of that entity.
- Anything else (for example `core.service` → `core.application`) is a steward decision (one change set, audited), or part of a MAJOR migration.

### 2.5 Environments, regions and disaster recovery (revision 4)

- **Environments are organization-defined entities** (`core.environment`): any number, any name and key (for example "DEV", "SIT", "UAT-2", "PROD", "DR"). `environment_kind` only classifies them, so rules and filters can treat "any production-like environment" consistently. Its vocabulary is taxonomy data; a MINOR version adds values.
- **Region is `location`**, an attribute of the physical resource, never containment and never an environment.
- **DR is a deployment role, not only an environment label.** `DEPLOYED_AS` carries an optional `deployment_role` ∈ {primary, active_secondary, standby, unknown}, with its own evidence and history like any attribute:
  - a production standby in a DR region: physical resource with `environment_id` = PROD, `location` = the DR region, and `DEPLOYED_AS` with `deployment_role = standby`;
  - a DR resource that also serves production workloads: `deployment_role = active_secondary`, plus its own evidenced relationships (for example workloads that `READS_FROM` it);
  - an organization that runs DR as a separate environment can still create an environment with `environment_kind = dr`; both patterns use the same facts.
- An absent `deployment_role` means **not established**. It is never assumed to be primary.
- Comparing environments (future) is a read-time query over the same facts (`environment_id`, environment `MEMBER_OF`, `DEPLOYED_AS`, `deployment_role`), as of any revision. Nothing is copied per environment.

## 3. Containment and membership (D11)

Revision 1 had one hierarchy rule for everything. That forced a single parent onto groupings that are naturally many-to-many: an application can belong to two business domains, and a shared resource can serve several environments. Revision 2 separates two meanings.

| | `CONTAINS`: hierarchical containment | `MEMBER_OF`: logical membership |
|---|---|---|
| Meaning | Composition: the child is a part of exactly one parent and is located or scoped by it | Grouping: the member is counted in, governed by or reported under a group. The group does not locate or scope the member |
| Examples | Tenant → subscription → resource group → resource; AWS account → resource; GCP project → resource; on-premises site → host → database; SQL server → database; any Kubernetes cluster → namespace → workload; capability → sub-capability; application → service → component; API → operation | Application in business systems and domains; dataset in a data domain; shared APIM instance in the environments it serves |
| Parents per child | **At most one** current `CONTAINS` parent | **Many** |
| Cycles | Rejected: an ancestor walk (depth ≤ 8) runs in the writing transaction | Impossible by construction: the type-level membership graph is acyclic (CI-checked, §1), so no instance cycle can form |
| Families | Two, never mixed: **resource** (P → P, always within one provider) and **logical decomposition** (L → L). A logical type never contains a physical type, and vice versa | Members may be L or P; groups are always L |
| Environment | If both are `single`-scoped, the environments must be equal. A `single` child under a `shared` parent is allowed when the parent is a `MEMBER_OF` the child's environment | Not constrained; membership in `core.environment` *defines* a shared scope |
| Denormalized | The current parent is copied to `entity_version.container_id` for index lookups (ADR-0001) | Not denormalized |
| Evidence | Provider configuration (the native hierarchy: ARM ID, ARN, resource name, OCID…), documentation, human assertion | Documentation, human assertion; provider configuration for environment membership |
| BRD term | `HOSTED_IN` (inverse direction) | — (new term, deviation) |

### 3.1 `CONTAINS` rules

1. The parent's type must be in the child's "`CONTAINS` parent" column (§2.2). Self-nesting is allowed only for `core.capability`, `core.business_domain`, `infra.scope` (as the provider profile allows) and `infra.resource`.
2. At most one current parent; a missing parent is allowed (unknown stays unknown).
3. No cycle (ancestor walk ≤ 8 levels, in the writing transaction).
4. For provider resources, the native identifier's hierarchy is the evidence where it has one (ARM IDs, GCP resource names, OCIDs with compartments). A `CONTAINS` that contradicts it (for example a database whose ID names another server) is rejected.
5. Physical containment is always within one provider; `k8s.*` share their cluster's provider.
6. Moving a child to a new parent closes the old relationship and opens a new one in the same change set (ADR-0008).

### 3.2 `MEMBER_OF` pairs

| Member types | Group type |
|---|---|
| `core.application` | `core.system`, `core.business_domain` |
| `core.system` | `core.business_domain` |
| `core.api`, `core.event_channel`, `core.dataset` | `core.business_domain` |
| Any E or O type with `environment_scope = shared` | `core.environment` |

The type-level graph `application → system → business_domain` has no back edges, and groups never become members of their own members, so cycles cannot occur. Nesting of domains is containment (`CONTAINS`), which is cycle-checked.

## 4. Relationship types and compatibility matrix

Rules are written against **categories** (ADR-0019 §2), so they apply to every provider's types in that category. Sets used below:

- **Logical actors (LA):** `core.application`, `core.service`, `core.component`.
- **Runtime actors (RA):** categories `runtime_workload` and `compute_host` (v1: `k8s.workload`, `azure.app_service`, `infra.workload`, `infra.compute`).
- **API targets (AT):** `core.api` and category `api_endpoint` (`azure.apim_api`, `infra.api_endpoint`).
- **Data stores (DS):** `core.dataset` and category `data_store` (`azure.sql_database`, `azure.storage_account`, `infra.data_store`).
- **Channels (CH):** `core.event_channel` and category `messaging_channel` (`azure.service_bus_queue`, `azure.service_bus_topic`, `infra.messaging_channel`).
- **Connectivity sources (CS):** RA plus categories `container_cluster`, `api_gateway`, `api_endpoint`, `network`, `subnet`.

**Evidence kinds** are ADR-0018's: `provider_configuration` (prov), `contract` (contr), `documentation` (doc), `human_assertion` (human), `inferred` (inf). A write whose evidence kind is not allowed for its relationship type is rejected.

**Uniqueness:** at most one relationship record per `(org, rel_type, from, to, discriminator)`. The discriminator is empty except where stated. More evidence for the same fact adds assertions to that record; it never creates a duplicate edge.

### 4.1 Active in v1

| `rel_type` | From | To | Cardinality and attributes | Allowed evidence | Cross-env allowed |
|---|---|---|---|---|---|
| `CONTAINS` | per §2.2 | per §2.2 | ≤ 1 parent per child; §3.1 | prov, doc, human | No |
| `MEMBER_OF` | per §3.2 | per §3.2 | many-to-many | doc, human; prov (environment only) | n/a |
| `OWNS` | `core.team` | any type except `core.team`, `core.environment` | many-to-many (INV-05); optional `ownership_role` ∈ {accountable, technical, data_steward} | human, doc | n/a |
| `SUPPORTS_CAPABILITY` | `core.system`, LA | `core.capability` | **required** `support_kind` ∈ {direct, enabling} (BCM-03); discriminator = `support_kind` | human, doc | n/a |
| `EXPOSES_API` | LA | `core.api` | — | contr, doc, human, prov | n/a |
| `CONSUMES_API` | LA, RA | AT | — | contr, prov, doc, human | Yes |
| `PUBLISHES_TO` | LA, RA | CH | — | prov, contr (AsyncAPI), doc, human | Yes |
| `SUBSCRIBES_TO` | LA, RA | CH (receiving from a queue counts) | optional `subscription_name` | prov, contr, doc, human | Yes |
| `READS_FROM` | LA, RA | DS | — (§5) | prov, contr, doc, human | Yes |
| `WRITES_TO` | LA, RA | DS | — (§5) | prov, contr, doc, human | Yes |
| `STORES_IN` | LA, RA | DS | data-store dependency whose direction is **not established** (§5) | doc, human, prov | Yes |
| `DEPLOYED_AS` (logical → physical) | see the pairs below | see the pairs below | many-to-many (MOD-03: one logical service, several deployments); L → P only; optional `deployment_role` (§2.5) | prov (deployment metadata), human, doc | No |
| `CONNECTS_TO` (explicitly configured infrastructure connectivity) | CS | any P type | **required** `connectivity_kind` (discriminator), provider-neutral names restricted per category pair: `network_peering` (network → network); `dedicated_link` (network → network, for example VPN or private circuits); `subnet_placement`, `network_integration` (RA or cluster → subnet); `gateway_backend` (gateway or API endpoint → RA); `private_link`, `service_endpoint`, `configured_endpoint` (→ any P type). The provider's own term (for example "private endpoint") goes in optional `native_kind` | prov, human; **never** inf | Yes |
| `DEPENDS_ON` (curated) | `core.system`, LA | `core.system`, LA, `core.api`, `core.dataset` | **required** `rationale`; §4.3 | **human, doc only** | n/a (logical) |

`DEPLOYED_AS` pairs:

| From (logical) | To (physical) |
|---|---|
| `core.application`, `core.service` | RA |
| `core.api` | category `api_endpoint` |
| `core.event_channel` | category `messaging_channel` |
| `core.dataset` | category `data_store` |

All rules apply across providers. `CONTAINS` among physical types is the only rule restricted to one provider.

### 4.2 Reserved in v1 (defined meaning, no allowed pairs, so writes are rejected)

- `PROTECTS` (security control → protected resource): no security-control types in v1 (D10, approved).
- `DECIDED_BY` (ADRs, Phase 3).
- `PRODUCES_DATA` / `CONSUMES_DATA` (dataset lineage, LIN-01, Phase 4). These are data **flow**; `READS_FROM` and `WRITES_TO` are data **access**.

**Dropped:** `REFERENCES_SELF` (in neither baseline's list). Self-relationships are forbidden for every type.

**Direction** is explicit and never inferred from layout (tech §3.3). For data access, the edge points from the actor to the store in both `READS_FROM` and `WRITES_TO`. It is the dependency direction, not the direction data moves.

### 4.3 `DEPENDS_ON` provenance (D9, approved with conditions)

1. Only `human_assertion` or `documentation` evidence is accepted. Connectors, imports that map other relationship types, and inference rules can never write it. The allowed-evidence column enforces this in the service layer and in a database check on the assertion row (ADR-0018).
2. Every `DEPENDS_ON` needs a `rationale` and at least one assertion naming its `source_ref` (the person, or the document with its artifact reference).
3. **A graph path is never a dependency.** Traversal results (for example A `CONSUMES_API` B, and B `DEPLOYED_AS` W) are computed at read time and are never stored as `DEPENDS_ON`. A steward may record a `DEPENDS_ON` *citing* such a path, but that is a new human assertion with its own evidence, trust state `curated` at best, and verification only by an explicit human verification.
4. Its trust state can never be `discovered`.

### 4.4 Relationship environment

- The relationship takes the environment of its `single`-scoped endpoint(s).
- If both endpoints are `single`-scoped with **different** environments, the relationship is allowed only where "Cross-env allowed" is Yes, and is flagged `cross_environment = true`. It always needs evidence of its own; the UI must make it visible.
- An endpoint with `shared` scope gives no environment. The relationship is flagged `shared_endpoint = true`.
- Logical-to-logical relationships are environment-neutral. A cross-environment integration therefore shows up on the physical endpoints (§6.9).
- If both endpoints are physical with different providers, the relationship is flagged `cross_provider = true` (ADR-0019 §6). It is allowed wherever the categories allow; it is never a reason to relax evidence.

## 5. Data access: `READS_FROM` and `WRITES_TO` (D8, revised)

Revision 1 proposed one `STORES_IN` edge with `access_mode` ∈ {read, write, read_write, unknown}. The owner asked whether that can hold reads and writes as independent facts.

| Question | One `STORES_IN` + `access_mode` | Separate `READS_FROM` and `WRITES_TO` records |
|---|---|---|
| Separate evidence per direction | No: both directions are one attribute value; evidence attaches to the value `read_write` | **Yes**: each record has its own assertions |
| Separate trust per direction (for example read `discovered`, write only `documented`) | No: one trust state for the attribute | **Yes** |
| Two sources, one says read and the other says write | Recorded as a **conflict** on `access_mode` (ADR-0018), although both are true | Two facts, no conflict |
| Removing write access while keeping read | An attribute change `read_write → read`; history shows a value change, not the end of a fact | The `WRITES_TO` record is retired; `READS_FROM` history is untouched |
| Verification and expiry per direction | No | **Yes** |
| BRD INV-02 wording (`READS`, `WRITES`) | Deviation | Direct mapping (names lengthened only) |
| Cost | One row per pair | Up to two rows per pair (negligible) |

**Recommendation:** separate relationship records `READS_FROM` and `WRITES_TO`, each with its own evidence, trust, verification and revision history. `access_mode` is removed.

`STORES_IN` (tech §3.3) is kept with a narrower meaning: "uses this data store; the access direction is not established by the evidence". It exists so that documentation such as "the claims service uses database X" can be recorded without inventing a direction.

- A `STORES_IN` is **never** converted automatically into `READS_FROM` or `WRITES_TO`.
- When directional evidence arrives, the directional records are added with that evidence. The `STORES_IN` stays as a separate fact until a steward retires it, so its own evidence is not lost.
- `read_write` means two records.

## 6. Coverage: how v1 represents the owner's scenarios (Azure)

Multi-provider scenarios (Azure with AWS, Google Cloud, Alibaba Cloud, OCI, on-premises, and two organizations) are in ADR-0019 §Scenarios.

All names are synthetic. Arrows show relationship direction.

### 6.1 Applications and business systems

- `core.system` "Claims Platform"; `core.application` "Claims Portal" (`org_key` APP-0101) and "Claims Engine" (APP-0102).
- Claims Portal `MEMBER_OF` Claims Platform; Claims Engine `MEMBER_OF` Claims Platform; both `MEMBER_OF` business domain "Claims".
- Claims Engine `CONTAINS` service "Quote Service" `CONTAINS` component "Pricing Rules".
- Claims Platform `SUPPORTS_CAPABILITY` "Claims Settlement" (`support_kind` direct); team "Claims Team" `OWNS` Claims Engine.

### 6.2 Azure tenants, subscriptions and resource groups

- `azure.tenant` (key: tenant GUID) `CONTAINS` `azure.subscription` "sub-claims-nonprod" `CONTAINS` `azure.resource_group` "rg-claims-uat".
- Two Azure tenants in one organization are two `azure.tenant` entities. Neither is an organization (ADR-0016).
- A subscription transferred to another tenant keeps its entity and ARM ID: the old `CONTAINS` closes and a new one opens.

### 6.3 AKS clusters and namespaces

- `azure.aks_cluster` "aks-shared-nonprod" (`environment_scope = shared`, `MEMBER_OF` env UAT and env Test) `CONTAINS` `k8s.namespace` "claims-uat" (`single`: UAT) `CONTAINS` `k8s.workload` "quote-service" (Deployment).
- Quote Service `DEPLOYED_AS` the workload. One logical service with workloads in UAT and prod gives two `DEPLOYED_AS` records (MOD-03).
- Cluster `CONNECTS_TO` subnet (`subnet_placement`).

### 6.4 API Management and APIs

- Logical `core.api` "Quotes API" (`api_version` v2) `CONTAINS` `core.api_operation` "GET /quotes/{id}".
- Quote Service `EXPOSES_API` Quotes API; Quotes API `DEPLOYED_AS` `azure.apim_api` "quotes-v2" which the `azure.apim_service` "apim-nonprod" `CONTAINS`.
- The APIM API `CONNECTS_TO` the quote-service workload (`gateway_backend`, from APIM backend configuration).
- Claims Portal `CONSUMES_API` Quotes API (logical, from contract), and its workload `CONSUMES_API` the APIM API (physical, from configuration). Two facts with separate evidence.

### 6.5 Databases and storage

- `azure.sql_server` "sql-claims-uat" `CONTAINS` `azure.sql_database` "sqldb-quotes".
- Logical `core.dataset` "Quote Records" `DEPLOYED_AS` the database.
- Quote Service `READS_FROM` and `WRITES_TO` the dataset (two records). The workload `WRITES_TO` the database (from configuration).
- `azure.storage_account` as a data store target; containers and blobs inside it are not modeled in v1.

### 6.6 Messaging

- `azure.service_bus_namespace` `CONTAINS` `azure.service_bus_topic` "quote-issued" and a queue.
- Logical `core.event_channel` "QuoteIssued" (topic) `DEPLOYED_AS` the topic.
- Quote Service `PUBLISHES_TO` QuoteIssued; Claims Portal `SUBSCRIBES_TO` QuoteIssued (`subscription_name` optional).

### 6.7 Compute and network

- Compute: `k8s.workload`, `azure.app_service` (Web App or Function App), `azure.aks_cluster`.
- Network: `azure.vnet` `CONTAINS` `azure.subnet`; vnet `CONNECTS_TO` vnet (`network_peering`); app service `CONNECTS_TO` subnet (`network_integration`); workload `CONNECTS_TO` Key Vault (`private_link`, `native_kind` "private endpoint", or `configured_endpoint`).
- Network facts are configuration only. Nothing about traffic is stored.

### 6.8 Logical versus physical containment

- Logical decomposition: application `CONTAINS` service `CONTAINS` component; API `CONTAINS` operation; capability and domain trees.
- Physical containment: the ARM hierarchy and the Kubernetes hierarchy.
- The bridge is `DEPLOYED_AS` (L → P), never `CONTAINS`. Groupings are `MEMBER_OF`.

### 6.9 Cross-environment integrations

- The UAT workload of Claims Portal `CONSUMES_API` the **production** `azure.apim_api` "quotes-v2". Both endpoints are `single`-scoped with different environments, so the record is flagged `cross_environment = true` and needs its own evidence.
- The logical `CONSUMES_API` (portal → Quotes API) stays environment-neutral and is not flagged.
- `CONTAINS` and `DEPLOYED_AS` are never cross-environment: a UAT namespace can't sit in a prod-scoped cluster.

## 7. Gaps, unsupported relationships and fallback limits

### 7.1 Gaps (not representable, or only partly, in v1)

| # | Gap | v1 behaviour | Proposed path |
|---|---|---|---|
| G-T1 | Security controls (NSG, Azure Firewall, WAF, private endpoint as an entity) | `infra.resource`; `PROTECTS` reserved (D10) | MINOR with control types and `PROTECTS` pairs |
| G-T2 | Other Azure types: VMs, Container Apps, Cosmos DB, Event Hubs, Event Grid, Azure Cache for Redis, Front Door, Application Gateway, DNS, managed identities | The neutral type of their category where mapped (VM → `infra.compute`, Cosmos DB → `infra.data_store`, Event Hubs → `infra.messaging_channel`, Container Apps → `infra.workload`); otherwise `infra.resource` | Provider-specific types per need, driven by the pilot domain (DEC-068) |
| G-T3 | APIM products, subscriptions, policies and per-APIM operations | Not modeled; operations exist on the logical API. ADR-0003's `apim.operation` namespace is **reserved** until a type exists | MINOR |
| G-T4 | Service Bus topic subscriptions as entities | `SUBSCRIBES_TO` attribute only | MINOR if rules need them |
| G-T5 | Kubernetes Services, Ingress, config objects | Not modeled; pods never (ephemeral) | MINOR |
| G-T6 | Dataset lineage and transformations (LIN-01) | Reserved `PRODUCES_DATA`/`CONSUMES_DATA` | Phase 4 |
| G-T7 | Business process or journey, file interface, integration contract, ADR, pattern, rule, data classification | Not in v1 | Their phases (tech §3.1, §12) |
| G-T8 | Team hierarchy and people | `core.team` only | With DEC-051/081 |
| G-T9 | ~~Non-Azure physical deployments~~ | **Closed in revision 3:** the eight `infra.*` types and category-based rules (§2.2, ADR-0019) | — |
| G-T10 | ~~Application ↔ resource group~~ | **Closed as not a gap** (§7.5): derived by traversal, never stored | — |
| G-T11 | Secret-store usage semantics ("reads secrets from") | `CONNECTS_TO` only; no secret is ever collected | Accept, or a MINOR relationship type |
| G-T12 | Provider-neutral network, gateway, broker, database-server and secret-store types | `infra.resource` outside Azure (containers of other resources, not rule endpoints except as `CONNECTS_TO` targets) | Add when a rule needs them as sources |
| G-T13 | Provider-specific types for AWS, Google Cloud and the others | Neutral types plus `native_type` | Per provider, when onboarded (ADR-0019 §Onboarding) |

### 7.2 Generic fallback limits

`infra.resource` (any provider) keeps an uncategorized resource visible, located and owned, but not semantically connected:

- **Allowed:** `CONTAINS` child of a scope or of another physical resource of the same provider (native hierarchy only); `CONTAINS` parent of neutral types where §2.2 allows; target of `CONNECTS_TO`; target of `OWNS`; `MEMBER_OF` an environment when shared.
- **Not allowed:** any API, messaging, data-access, `DEPLOYED_AS` or `DEPENDS_ON` relationship. For example a resource whose native type is not mapped to `data_store` can't be read from or written to until it is mapped (Cosmos DB is mapped in v1, G-T2). The coverage of that entity reads `unknown_coverage`, never a substitute edge.
- **Re-typing:** when a MINOR adds the type, the entity is re-typed with the same ID (§2.4).

### 7.3 Examples of rejected relationships (readable reason, MOD-03)

| Attempt | Reason returned |
|---|---|
| `core.application` `CONTAINS` `azure.resource_group` | Containment never crosses logical and physical families; use `DEPLOYED_AS` from a service to its workloads |
| `k8s.workload` `CONTAINS` `k8s.workload` | Not an allowed parent type |
| A second `CONTAINS` parent for a resource group | At most one containment parent; close the current one first |
| `core.service` `DEPLOYED_AS` `azure.sql_database` | Pair not allowed; a dataset can be deployed as a database, a service reads or writes it |
| Anything `READS_FROM` an `infra.resource` | Generic resources take no data-access relationships (§7.2) |
| An AWS account `CONTAINS` an Azure resource group | Physical containment stays within one provider |
| `DEPENDS_ON` from a connector or an inference rule | Evidence kind not allowed for `DEPENDS_ON` |
| Any relationship whose type and pair aren't in §4.1 | Lists the allowed pairs for that type and the allowed types for that pair |

### 7.4 Unknown and unsupported input

- **Resource type without a specific type:** the neutral type of its mapped category, else `infra.resource`, with `native_type` and safe metadata only (E04). Never coerced into a provider-specific type it doesn't match.
- **Unknown Kubernetes workload kind:** `k8s.workload` with `workload_kind = other`.
- **A relationship that is not in the matrix:** rejected with a reason (§7.3); imports report it; connectors keep it as an unattached observation (Phase 2); it is **never** stored as an edge and never downgraded to `DEPENDS_ON` or `STORES_IN`.
- **No relationship** is not a relationship. Absence is shown as coverage unknown (DEC-066), never as a drawn edge.
- **Fixtures** (CP2) contain only matrix-valid, evidence-backed facts. Disconnected entities are allowed and expected.

### 7.5 G-T10: application ↔ resource group (closed: no direct relationship)

**Question:** is a stored link from an application to a resource group needed, or do `DEPLOYED_AS` and containment answer it?

| Candidate | Problem |
|---|---|
| Application `CONTAINS` resource group | Wrong meaning: a logical thing would contain a physical one; the resource group would get the application as its single parent, although it may hold resources of several applications |
| Application `MEMBER_OF`, or `OWNS` by the application | Provider-specific (an Azure resource group has no counterpart in AWS accounts or GCP projects), states a fact nobody evidenced, and invites inference from names or tags |
| **Derived, not stored (recommended)** | "Where is this application deployed?" = application → `DEPLOYED_AS` → physical resources → `CONTAINS` ancestors (resource group, account, project, compartment, site). It works for every provider, uses only evidenced facts and is bounded |

- The traversal result is labeled "derived from deployments" and is never stored, and never turned into `DEPENDS_ON` (§4.3).
- Resources that an application uses but doesn't deploy to (a key store, a database) are reached through `READS_FROM`, `WRITES_TO` or `CONNECTS_TO` from its workloads, not through the resource group.
- A team that manages a resource group is already expressible: `core.team` `OWNS` it.
- Tags or naming conventions (for example `app=APP-0101`) are future reconciliation **inputs**. They can produce review candidates for `DEPLOYED_AS` or `OWNS`; they are never a fact by themselves.

## 8. Baseline vocabulary mapping (documented aliases)

| BRD INV-02 term | Canonical v1 | Note |
|---|---|---|
| `CALLS_API` | `CONSUMES_API` | Rename |
| `PUBLISHES` | `PUBLISHES_TO` | Rename |
| `CONSUMES` | `SUBSCRIBES_TO` (channel target) or `CONSUMES_API` (API target) | Resolved by the target type |
| `READS` | `READS_FROM` | Rename (revision 2) |
| `WRITES` | `WRITES_TO` | Rename (revision 2) |
| `DEPLOYED_ON` | `DEPLOYED_AS` | Logical → physical |
| `HOSTED_IN` | `CONTAINS` | **Inverse direction** (parent → child) |
| `OWNS` | `OWNS` | Same |
| `DEPENDS_ON` | `DEPENDS_ON` | Curated only |
| `PROTECTS` | `PROTECTS` | Reserved |

| Tech §3.3 term | Canonical v1 | Note |
|---|---|---|
| `CONTAINS` | `CONTAINS` | Narrowed to hierarchical containment; groupings move to `MEMBER_OF` |
| `STORES_IN` | `STORES_IN` | Narrowed to "direction not established"; directional facts are `READS_FROM` / `WRITES_TO` |
| others | unchanged | `PRODUCES_DATA`, `CONSUMES_DATA`, `DECIDED_BY` reserved |

**Additions in neither baseline:** `READS_FROM`/`WRITES_TO` (as names), `MEMBER_OF`, the `support_kind` and `connectivity_kind` attributes, the types `core.system` and `core.component` (named by MOD-01, owner-approved), and the provider-neutral categories and `infra.*` types (implementing BRD's "technology-neutral underlying model" and DEC-004). On confirmation they are recorded as deviations in `decisions/baseline-deviations.md` and proposed for the next baseline revisions. The baselines are **not** edited.

## Trade-offs and risks

- **A small v1:** many resources start as neutral `infra.*` types (or `infra.resource`) until MINOR versions add provider-specific types. That is safer than guessing, and IDs survive re-typing.
- **Two containment-like relationships** are one more concept for users. The UI will label them differently ("contains" vs "member of").
- **Curated `DEPENDS_ON`** can become a catch-all. Limited by logical-only endpoints, a required rationale, no automated source and no conversion of paths.
- **Three data-access relationship types** (`READS_FROM`, `WRITES_TO`, `STORES_IN`). The cost is clarity in legends; the benefit is per-direction evidence and no invented direction.
- **The matrix is enforced in the service layer**, plus database FKs for type keys and a check for allowed evidence kinds. A trigger for the full matrix is possible later if bypass risk appears.

## Impact on the database schema

- Reference tables `entity_type`, `relationship_type`, `relationship_rule (rel_type, from_type, to_type, discriminator values, allowed evidence kinds, cross-environment flag, taxonomy_version)` and `attribute_rule`.
- `type_key` and `environment_scope` on `entity_version`; `discriminator` on `relationship` (part of its unique key); `cross_environment` and `shared_endpoint` on `relationship_version`.
- See ADR-0001.

## Impact on APIs and authorization (future)

- The API exposes the taxonomy read-only (MOD-01, "an administrator can inspect permitted types") and validation errors with reasons (422).
- Type, environment and scope are ABAC attributes.

## Migration and compatibility

- MINOR versions are additive seeds; re-typing generic resources runs in one change set.
- MAJOR versions need a migration that re-types or retires data in one change set, plus owner approval.
- IDs survive every upgrade (MOD-01).

## Approved by the owner (25 Oct 2026)

1. Option A (tech catalog + BRD aliases), recording the deviations in §8 on confirmation.
2. The 38-type catalog in §2.2 (`core.system` and `core.component` already approved; the eight `infra.*` types new in revision 3), environment scopes (§2.3) and re-typing (§2.4).
3. `CONTAINS` vs `MEMBER_OF` (§3).
4. The matrix (§4), including `READS_FROM`/`WRITES_TO` with narrowed `STORES_IN` (§5), `DEPENDS_ON` provenance (§4.3) and the relationship environment rules (§4.4).
5. G-T9 closed by the `infra.*` types; G-T10 closed as derived-only (§7.5); the fallback limits (§7.2) and unknown handling (§7.4).
6. Category-based rules across providers, physical containment within one provider (§3.1, §4).
