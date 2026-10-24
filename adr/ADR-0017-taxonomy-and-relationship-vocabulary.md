# ADR-0017 — Canonical taxonomy and relationship vocabulary v1

| Field | Value |
|---|---|
| Status | **Proposed** (CP1 of ATLAS-002, 24 Oct 2026) |
| Register | DEC-050 (Open → Proposed), DEC-070 (Open → Proposed) |
| Owner (proposed) | Enterprise Architecture + Cloud Platform; approval: Atlas owner |
| Related | INV-01, INV-02, INV-05, MOD-01, MOD-03, MOD-04, DEP-01, DEP-04, CAN-02, E04; tech §3.1, §3.3; ADR-0001, ADR-0003, ADR-0018 |

## Problem

The two baselines disagree:

- **BRD INV-02** lists `CALLS_API, PUBLISHES, CONSUMES, READS, WRITES, DEPLOYED_ON, HOSTED_IN, OWNS, DEPENDS_ON, PROTECTS`.
- **Tech §3.3** lists `CONTAINS, SUPPORTS_CAPABILITY, EXPOSES_API, CONSUMES_API, PUBLISHES_TO, SUBSCRIBES_TO, STORES_IN, DEPLOYED_AS, CONNECTS_TO, OWNS, PRODUCES_DATA/CONSUMES_DATA, DECIDED_BY`.

MOD-01 and MOD-03 need a **versioned** type list with required attributes, allowed parent/child pairs and relationship rules that reject invalid input with a readable reason. E04 says unsupported resource types are kept as generic typed objects.

**Owner direction (24 Oct 2026):** cover the approved MVP Azure types and architectural concepts; define compatibility, required attributes, containment, extension/versioning and unknown types; **do not invent relationships to make a fixture connected**.

## Options

| Option | Verdict |
|---|---|
| **A. Tech §3.3 catalog as canonical, BRD terms as documented aliases**, plus explicit decisions on the BRD-only terms | **Recommended**: keeps containment, capability and ownership semantics that INV-02 lacks; every BRD term maps to a defined meaning |
| B. BRD INV-02 verbatim | Rejected: no containment or capability support, ambiguous `CONSUMES` (API or topic), and `DEPLOYED_ON`/`HOSTED_IN` overlap |
| C. Open vocabulary (free-form types in JSONB) | Rejected: no validation (violates MOD-01/03), and invites invented edges |

## Recommendation (v1.0.0)

### 1. Structure and versioning

- **Source of truth:** a versioned artifact in atlas-specs, `contracts/taxonomy/atlas-taxonomy.v1.json`. It is produced in **CP2 after this ADR is approved**, with a JSON Schema and valid/invalid examples.
- **Versioning (semver):**
  - MINOR adds types, relationship types, allowed pairs or optional attributes;
  - MAJOR removes or renames anything, or makes an attribute required;
  - every MAJOR needs a data migration plan and owner approval.
- **Stable keys:** `type_key` and `rel_type` are namespaced and lowercase (`core.application`, `azure.key_vault`) or upper snake case (`CONSUMES_API`). They are never reused once published. Deprecated keys stay readable and stop being writable.
- **Pinning:** the backend pins the taxonomy through `specs.lock`. Migrations seed `entity_type`, `relationship_type` and `relationship_rule` from the pinned artifact, and a CI check compares seed and artifact (as `make contract` does for OpenAPI).
- **Recorded version:** every entity and relationship version records the taxonomy version it was validated against.

### 2. Entity types

**Environment** column: **E** = environment-specific (requires an `environment` reference), **N** = environment-neutral, **O** = optional.

| Layer | `type_key` | Env | Required attributes (beyond `display_name`, `lifecycle`) | Identity (ADR-0003) | Allowed `CONTAINS` parent |
|---|---|---|---|---|---|
| Business | `core.capability` | N | — | — | `core.capability` |
| Business | `core.business_domain` | N | — | — | — |
| Ownership | `core.team` | N | — | — | — |
| Application | `core.application` | N | `org_key` | `org.key` | `core.business_domain` |
| Application | `core.service` (logical service) | N | — | `org.key` (optional) | `core.application` |
| Integration | `core.api` (logical API, DEP-01) | N | `api_version` | — | — |
| Integration | `core.api_operation` | N | `http_method`, `path_template` | — | `core.api` |
| Integration | `core.event_channel` (logical topic/queue) | N | `channel_kind` ∈ {queue, topic} | — | — |
| Data | `core.dataset` | N | — | — | — |
| Deployment | `core.environment` | N | `environment_kind` ∈ {prod, uat, test, dev, sandbox, other} | — | — |
| Azure | `azure.tenant` | N | — | `azure.tenant_id` | — |
| Azure | `azure.subscription` | O | — | `azure.subscription_id`, `azure.arm` | `azure.tenant` |
| Azure | `azure.resource_group` | O | `location` | `azure.arm` | `azure.subscription` |
| Azure | `azure.apim_service` | E | `azure_type`, `location` | `azure.arm` | `azure.resource_group` |
| Azure | `azure.apim_api` (API published in an APIM instance) | E | `api_revision` | `apim.api` | `azure.apim_service` |
| Azure | `azure.aks_cluster` | E | `azure_type`, `location` | `azure.arm` | `azure.resource_group` |
| Kubernetes | `k8s.namespace` | E | — | `k8s.uid` | `azure.aks_cluster` |
| Kubernetes | `k8s.workload` | E | `workload_kind` ∈ {Deployment, StatefulSet, DaemonSet, CronJob, Job, other} | `k8s.uid` | `k8s.namespace` |
| Azure | `azure.app_service` | E | `azure_type`, `location` | `azure.arm` | `azure.resource_group` |
| Azure | `azure.service_bus_namespace` | E | `azure_type`, `location` | `azure.arm` | `azure.resource_group` |
| Azure | `azure.service_bus_queue` | E | — | `azure.arm` | `azure.service_bus_namespace` |
| Azure | `azure.service_bus_topic` | E | — | `azure.arm` | `azure.service_bus_namespace` |
| Azure | `azure.sql_server` | E | `azure_type`, `location` | `azure.arm` | `azure.resource_group` |
| Azure | `azure.sql_database` | E | — | `azure.arm` | `azure.sql_server` |
| Azure | `azure.storage_account` | E | `azure_type`, `location` | `azure.arm` | `azure.resource_group` |
| Azure | `azure.key_vault` | E | `azure_type`, `location` | `azure.arm` | `azure.resource_group` |
| Azure | `azure.vnet` | E | `azure_type`, `location` | `azure.arm` | `azure.resource_group` |
| Azure | `azure.subnet` | E | — | `azure.arm` | `azure.vnet` |
| Azure | `azure.generic_resource` (fallback, E04) | O | `azure_type` (the ARM type string) | `azure.arm` | `azure.resource_group` |

- The MVP Azure set is DEC-070's recommendation: APIM, AKS, Service Bus, Azure SQL, Key Vault, VNet/subnet, Storage, App Service. To that it adds tenant, subscription and resource group for the hierarchy (CAN-02).
- Data-lineage, ADR, pattern and rule types are **not** in v1. They arrive with their phases as MINOR versions.

### 3. Containment rules (`CONTAINS`)

1. At most **one** `CONTAINS` parent per entity, and the parent type must be in the "allowed parent" column. A missing parent is allowed: unknown stays unknown.
2. **Acyclic:** a cycle is rejected (checked transactionally by walking ancestors, bounded by the hierarchy depth of at most 8).
3. **Environment:** when both parent and child are environment-specific, their environments must be equal. Environment-neutral parents can contain environment-specific children only where the table allows it (for example `azure.subscription` with optional environment).
4. Containment is a fact like any other: it needs evidence (ADR-0018).

### 4. Relationship types and compatibility matrix

| `rel_type` | From (any of) | To (any of) | Cardinality / attributes | Evidence it may come from (ADR-0018) |
|---|---|---|---|---|
| `CONTAINS` | per §2 parent column | per §2 | ≤ 1 parent per child | provider configuration, documentation, human assertion |
| `OWNS` | `core.team` | any type except `core.team` | many-to-many (INV-05) | human assertion, documentation |
| `SUPPORTS_CAPABILITY` | `core.application`, `core.service` | `core.capability` | — | human assertion, documentation |
| `EXPOSES_API` | `core.application`, `core.service` | `core.api` | — | contract, documentation, human assertion, provider configuration |
| `CONSUMES_API` | `core.application`, `core.service`, `k8s.workload`, `azure.app_service` | `core.api`, `azure.apim_api` | — | contract, provider configuration, documentation, human assertion |
| `PUBLISHES_TO` | same as `CONSUMES_API` sources | `core.event_channel`, `azure.service_bus_topic`, `azure.service_bus_queue` | — | provider configuration, contract (AsyncAPI), documentation, human assertion |
| `SUBSCRIBES_TO` | same as `CONSUMES_API` sources | `core.event_channel`, `azure.service_bus_topic`, `azure.service_bus_queue` | — | as `PUBLISHES_TO` |
| `STORES_IN` | same as `CONSUMES_API` sources | `core.dataset`, `azure.sql_database`, `azure.storage_account` | **required** `access_mode` ∈ {read, write, read_write, unknown} | provider configuration, documentation, human assertion |
| `DEPLOYED_AS` (logical → physical, one-to-many) | `core.application`, `core.service`; `core.api`; `core.event_channel` | `k8s.workload`, `azure.app_service` (from application/service); `azure.apim_api` (from API); `azure.service_bus_queue`, `azure.service_bus_topic` (from channel) | from environment-neutral to environment-specific only | provider configuration (deployment metadata), human assertion |
| `CONNECTS_TO` (explicitly configured infrastructure connectivity) | `k8s.workload`, `azure.app_service`, `azure.aks_cluster`, `azure.subnet`, `azure.vnet` | any `azure.*` resource type, `k8s.workload` | **required** `connectivity_kind` (text, e.g. vnet_peering, private_endpoint, configured_endpoint) | provider configuration, human assertion; **never** inferred from traffic |
| `DEPENDS_ON` (generic, curated) | `core.application`, `core.service` | `core.application`, `core.service`, `core.api`, `core.dataset` | **required** `rationale` | **human assertion or documentation only**; never produced by connectors or inference |

**Reserved** (defined meaning, no allowed pairs in v1, so writes are rejected):

- `PROTECTS` (security control → protected resource): v1 has no control types (NSG, Azure Firewall, WAF, private endpoint). Enabling it without them would mean inventing pairs. It becomes active in the MINOR version that adds those types.
- `DECIDED_BY` (ADRs, Phase 3).
- `PRODUCES_DATA` / `CONSUMES_DATA` (lineage, Phase 4).

**Dropped:** `REFERENCES_SELF` (in neither baseline's list). Self-relationships are forbidden for every type.

**Direction** is explicit and never inferred from layout (tech §3.3).

**Environment scope of relationships:**

- If one endpoint is environment-specific, the relationship carries that environment.
- If both are environment-specific with **different** environments, the relationship is allowed only for `CONSUMES_API`, `PUBLISHES_TO`, `SUBSCRIBES_TO`, `STORES_IN` and `CONNECTS_TO`, flagged `cross_environment = true`, and must have evidence. This makes for example a UAT service calling a production API visible, never hidden.
- `CONTAINS` and `DEPLOYED_AS` are never cross-environment.

### 5. BRD INV-02 mapping (documented aliases)

| BRD term | Canonical v1 |
|---|---|
| `CALLS_API` | `CONSUMES_API` |
| `PUBLISHES` | `PUBLISHES_TO` |
| `CONSUMES` | `SUBSCRIBES_TO` (messaging) or `CONSUMES_API` (APIs), decided by the target type |
| `READS` / `WRITES` | `STORES_IN` with `access_mode` |
| `DEPLOYED_ON` | `DEPLOYED_AS` (logical → workload) |
| `HOSTED_IN` | `CONTAINS` (workload in namespace or cluster; resource in resource group) |
| `OWNS` | `OWNS` |
| `DEPENDS_ON` | `DEPENDS_ON` (curated only) |
| `PROTECTS` | `PROTECTS` (reserved until security control types exist) |

Adopting this is a deviation from BRD INV-02's wording. On approval it is recorded in `decisions/baseline-deviations.md` and proposed for the next BRD revision. The baseline is **not** edited.

### 6. Unknown and unsupported input

- **Unsupported ARM resource type:** `azure.generic_resource` with `azure_type` and safe metadata only (E04). It is never coerced into a specific type.
- **Unknown Kubernetes workload kind:** `k8s.workload` with `workload_kind = other`.
- **A relationship that is not in the matrix:**
  - rejected with a readable reason (MOD-03), naming the type pair and the allowed alternatives;
  - imports report it;
  - connectors keep it as an unattached observation (Phase 2);
  - it is **never** stored as an edge, and never downgraded to `DEPENDS_ON`.
- **No relationship** is not a relationship. Absence is shown as "coverage unknown" at entity level (DEC-066), never as a drawn edge.
- **Fixtures** (CP2) contain only matrix-valid, evidence-backed facts. Disconnected entities are allowed and expected.

## Trade-offs and risks

- **A small v1:** some real architectures (firewalls, Front Door, Cosmos DB) start as `azure.generic_resource` until a MINOR version adds them. That is safer than guessing.
- **Curated `DEPENDS_ON`** can become a catch-all. That is limited by logical-layer-only endpoints, a required rationale and no automated source.
- **The matrix is enforced in the service layer**, with database FKs for the keys only. A trigger for the full matrix is possible later if bypass risk appears.

## Impact on the database schema

- Reference tables `entity_type`, `relationship_type`, `relationship_rule (rel_type, from_type, to_type, taxonomy_version)` and `attribute_rule`.
- FKs from versions to the type tables; `taxonomy_version` on versions.
- See ADR-0001.

## Impact on APIs and authorization (future)

- The API exposes the taxonomy read-only (MOD-01, "an administrator can inspect permitted types") and validation errors with reasons (422).
- Type and environment become ABAC attributes.

## Migration and compatibility

- MINOR versions are additive seeds.
- MAJOR versions need a migration that re-types or retires data in one change set, plus owner approval.
- IDs survive every upgrade (MOD-01).

## Requires owner approval

1. Option A (tech catalog + BRD aliases), and recording the INV-02 deviation on approval.
2. The v1 entity type list (incl. the DEC-070 Azure set) and required attributes.
3. The containment rules.
4. The compatibility matrix, including:
   - `STORES_IN.access_mode` replacing `READS`/`WRITES`;
   - `DEPENDS_ON` curated-only, **or** dropped (alternative);
   - `PROTECTS` reserved until control types exist, **or** adding NSG/Firewall/WAF/private-endpoint types now (alternative);
   - cross-environment rules.
5. Unknown and unsupported handling, and the "no invented relationships" fixture rule.
