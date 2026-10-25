# ADR-0019 — Provider-neutral canonical model and provider onboarding

| Field | Value |
|---|---|
| Status | **Proposed** (ATLAS-002 CP1 revision 3, 25 Oct 2026). Not approved; no code depends on it |
| Register | Implements DEC-004 (Confirmed: "Azure-first … technology-neutral underlying model"); shapes DEC-050, DEC-070 (Proposed) and DEC-025 (Proposed) |
| Owner (proposed) | Enterprise Architecture + Cloud Platform; approval: Atlas owner |
| Related | BRD Document control ("technology-neutral underlying model"), INV-01, INV-05, MOD-01, MOD-04, SDK family; UX §5 ("do not force Azure hierarchy onto on-prem systems"); tech §1, §3.1, §3.2; ADR-0001, ADR-0003, ADR-0008, ADR-0016, ADR-0017, ADR-0018 |

## Problem

**Owner direction (25 Oct 2026):** Atlas must be able to represent Microsoft Azure, AWS, Google Cloud, Alibaba Cloud, Oracle Cloud Infrastructure, Huawei Cloud, Tencent Cloud, IBM Cloud, private clouds, on-premises infrastructure and custom enterprise technologies. Azure stays the first implementation target. No other connector is built in ATLAS-002.

Revision 2 of the proposals was Azure-shaped in four places:

1. physical types existed only as `azure.*` (and Kubernetes under AKS only);
2. the only fallback was `azure.generic_resource`;
3. relationship rules named Azure types directly;
4. the identity and tenancy text treated the Azure tenant and the ARM ID as the only provider concepts.

A new provider would then have meant new rules everywhere, or a redesign. The goal: **a new provider adds reference data and a small amount of reviewed code, never a change to the entity or relationship tables.** No plugin runtime.

## Options

| Option | How | Verdict |
|---|---|---|
| **A. Three-level typing: provider-neutral category → type → provider attributes** | Every type belongs to one provider-neutral **category**; relationship rules are written against categories; provider-specific types (`azure.*` now) and a small set of **provider-neutral physical types** (`infra.*`) both sit under those categories; provider detail lives in `native_type` and validated attributes | **Recommended** |
| B. One generic physical type with a required `category` attribute | Minimal type list (`infra.resource` + `category`) | Rejected: rules, required attributes and UI semantics would hang off an attribute instead of the type; validation becomes conditional everywhere; weaker than A for the same storage |
| C. Provider-specific types for every provider now | Full AWS/GCP/… catalogs | Rejected: large, speculative, unverifiable without sources; violates "compact MVP" |
| D. Provider plugins (runtime-loaded type and rule packages) | Extensions loaded at runtime | Rejected for now (owner: no premature plugin runtime). A can move to it later because providers are already data |

## Model (Option A)

### 1. Providers (reference data, versioned with the taxonomy)

| Provider key | Covers |
|---|---|
| `azure` | Microsoft Azure (first implementation target) |
| `aws` | Amazon Web Services |
| `gcp` | Google Cloud |
| `alibaba` | Alibaba Cloud (Aliyun) |
| `oci` | Oracle Cloud Infrastructure |
| `huawei` | Huawei Cloud |
| `tencent` | Tencent Cloud |
| `ibm` | IBM Cloud |
| `private_cloud` | Private clouds (for example OpenStack or VMware-based); the platform is the `platform` attribute |
| `on_premises` | On-premises infrastructure |
| `other` | Custom enterprise technologies and anything else; the technology is the `platform` attribute |

- Every **physical** entity has exactly one `provider`. Logical entities have none.
- A provider is reference data, not an entity: Atlas does not model "AWS" as a node. Provider **accounts** are entities (§3).
- Adding a provider key is a taxonomy MINOR change.

### 2. Categories (provider-neutral architectural categories)

Logical types are their own categories (`core.application`, `core.api`, …; ADR-0017 §2). Physical categories:

| Category | Meaning | Azure types (v1) | Provider-neutral type (v1) |
|---|---|---|---|
| `scope` | Provider account and resource hierarchy | `azure.tenant`, `azure.subscription`, `azure.resource_group` | `infra.scope` |
| `container_cluster` | Container orchestration cluster | `azure.aks_cluster` | `infra.cluster` |
| `container_namespace` | Namespace inside a cluster | `k8s.namespace` (any provider) | — |
| `runtime_workload` | A deployed runtime unit: container workload, web app, function, service process | `k8s.workload` (any provider), `azure.app_service` | `infra.workload` |
| `compute_host` | Virtual machine, instance or physical host | — | `infra.compute` |
| `api_gateway` | API gateway instance | `azure.apim_service` | — (`infra.resource`) |
| `api_endpoint` | An API published on a gateway or platform | `azure.apim_api` | `infra.api_endpoint` |
| `messaging_broker` | Broker or messaging namespace | `azure.service_bus_namespace` | — (`infra.resource`) |
| `messaging_channel` | Queue, topic or stream | `azure.service_bus_queue`, `azure.service_bus_topic` | `infra.messaging_channel` |
| `database_server` | Database server or instance hosting databases | `azure.sql_server` | — (`infra.resource`) |
| `data_store` | Database, bucket, file share or cache holding data | `azure.sql_database`, `azure.storage_account` | `infra.data_store` |
| `secret_store` | Secret or key store | `azure.key_vault` | — (`infra.resource`) |
| `network`, `subnet` | Virtual network and its subdivision | `azure.vnet`, `azure.subnet` | — (`infra.resource`) |
| `generic` | Anything not yet categorized | — | `infra.resource` |

- **Relationship rules use categories** (ADR-0017 §4). A new provider's resources are immediately usable by every rule through their category, without any rule change.
- A neutral type exists only where a category is an **endpoint of a semantic rule** (API, messaging, data access, deployment, connectivity) or is needed for hierarchy. Categories that only hold other resources (`api_gateway`, `messaging_broker`, `database_server`, `secret_store`, `network`, `subnet`) fall back to `infra.resource` outside Azure until a real need appears.

### 3. Provider-specific types and attributes

| Element | Rule |
|---|---|
| `native_type` | Required on every physical entity: the provider's own type string (for example `microsoft.sql/servers/databases`, `AWS::Lambda::Function`, `pubsub.googleapis.com/Topic`, `ACS::ECS::Instance`). For `azure.*` types it is fixed per type (formerly `azure_type`) |
| Provider-specific type (`azure.*`, later `aws.*`, …) | Added **only** when rules, required attributes or identity need more precision than the neutral type gives. Azure gets them first because it is the first discovery target |
| Neutral type (`infra.*`) | Used for every provider without a specific type. Chosen by the provider profile's `native_type → category` mapping; an unmapped native type becomes `infra.resource` |
| Required attributes | Per type (ADR-0017 §2). Neutral types add `provider`, `native_type` and a category attribute where needed (`compute_kind`, `cluster_kind`, `workload_kind`, `channel_kind`, `store_kind`, `scope_kind`) |
| `location` | Neutral name for region or site (Azure location, AWS region, on-premises site code) |
| `platform` | Required for `private_cloud`, `on_premises` and `other` (for example "VMware", "OpenShift", "Oracle Database"); optional otherwise |
| `provider_attributes` | JSON object for safe provider detail. Validated by the provider profile's attribute schema when one exists; otherwise stored but **never used by rules**. Never secrets, payloads or network addresses (DEC-010, DEC-073) |
| Re-typing | A neutral entity can be re-typed to a later provider-specific type with the same ID (ADR-0017 §2.4) |

### 4. Provider account and resource hierarchies

`infra.scope` has a `scope_kind` from the provider profile. The profile also states which `scope_kind` may contain which, so containment is validated per provider without new types.

| Provider | Hierarchy (`scope_kind`, outermost first) | Resources sit in |
|---|---|---|
| Azure | `azure.tenant` → `azure.subscription` → `azure.resource_group` (specific types) | Resource group |
| AWS | `organization` → `organizational_unit` (nests) → `account` | Account; region is `location`, not containment |
| GCP | `organization` → `folder` (nests) → `project` | Project |
| Alibaba Cloud | `account` → `resource_group` | Resource group (or account) |
| OCI | `tenancy` → `compartment` (nests) | Compartment |
| Huawei Cloud | `account` → `enterprise_project` / `project` | Project |
| Tencent Cloud | `account` → `project` | Project (or account) |
| IBM Cloud | `enterprise` → `account_group` (nests) → `account` → `resource_group` | Resource group |
| Private cloud | `platform_instance` → `tenant` / `project` | Tenant or project |
| On-premises | `site` → `zone` (optional, nests) | Site or zone; or a `compute_host` |
| Other | `platform_instance` (nests) | Platform instance |

- Physical `CONTAINS` stays within **one provider** (a resource is never "contained" by another provider's scope). The exception is Kubernetes: `k8s.*` entities take the provider of their cluster.
- The hierarchy vocabulary for each provider is reviewed reference data. Values for the providers other than Azure are taken from public provider documentation when that provider is onboarded and confirmed then; the table above is the intended shape, not a frozen list.
- **Atlas organization ≠ any provider account** (ADR-0016): an AWS organization, a GCP organization or an OCI tenancy is an `infra.scope` entity inside one Atlas organization.

### 5. Provider-qualified identities

ADR-0003 holds the namespace registry: one namespace per provider identifier format (`azure.arm`, `aws.arn`, `gcp.resource_name`, `alibaba.arn`, `oci.ocid`, …), each with its validation, normalization, case rule and the uniqueness scope that the normalized key must embed. Uniqueness is always `(org_id, namespace, normalized_key)`.

### 6. Cross-provider relationships

- Rules are category-based, so relationships cross providers wherever the categories allow (an Azure workload `CONSUMES_API` an AWS API endpoint).
- `relationship_version.cross_provider = true` when both endpoints are physical with different providers. Like `cross_environment`, it is computed, stored for querying and shown in the UI.
- They need evidence like any other fact. Cross-provider facts often have evidence from **one side only** (for example an Azure setting naming an AWS endpoint). That is recorded as exactly that: configuration of one side, `provider_configuration` from the Azure source. It is never upgraded to "verified" without a human verification, and never described as observed traffic.
- Physical containment and `DEPLOYED_AS` never need to cross providers to be useful: a business system spans providers through `MEMBER_OF` and `DEPLOYED_AS` (scenario 5).

### 7. What stays provider-neutral without change

- **Provenance and trust (ADR-0018):** `provider_configuration` means "read from **a** provider's or platform's control plane or configuration by an approved source", for any provider, including on-premises CMDBs and IaC state. Evidence records the source, not the provider of the fact.
- **Revisions (ADR-0008):** change sets, versions and snapshots know nothing about providers.
- **Tenancy (ADR-0016):** organization-scoped rows; provider accounts are data inside the organization.
- **Logical and physical:** logical types (`core.*`) are provider-free; `DEPLOYED_AS` is the only bridge from logical to physical, for every provider.
- **Facts vs visualization:** canonical tables hold no presentation data: no positions, colours, icons, provider logos or diagram grouping. Icons are derived from category (and optionally provider) by the frontend's design tokens; layouts belong to the separate view model (DEC-005, MOD-05, invariant 1).

## Scenarios (synthetic)

All names, IDs and account numbers are invented. Identifiers are shown in their namespace form (ADR-0003). "Trust" uses ADR-0018 trust states; "Verification" is separate and is `unverified` unless stated.

### S1. Azure application calling an AWS API

| Aspect | Model |
|---|---|
| Entities | `core.application` "Claims Portal"; `azure.app_service` "app-claims-portal-uat" (UAT); `core.api` "Rating API"; `infra.scope` AWS `account` "rating-prod"; `infra.api_endpoint` "rating-api" (provider `aws`, `native_type` `AWS::ApiGateway::RestApi`, prod) |
| Identifiers | App service: `azure.arm` `/subscriptions/00000000-0000-0000-0000-000000000001/resourcegroups/rg-claims-uat/providers/microsoft.web/sites/app-claims-portal-uat`. AWS account: `aws.account` `aws:111111111111`. Endpoint: `aws.arn` `arn:aws:apigateway:eu-west-1::/restapis/abc123exmp` |
| Relationships | Claims Portal `DEPLOYED_AS` app service; Rating API `DEPLOYED_AS` the AWS endpoint; Claims Portal `CONSUMES_API` Rating API (logical) |
| Containment | ARM hierarchy for the app service; AWS account `CONTAINS` the endpoint (region `eu-west-1` is `location`) |
| Evidence and trust | Only the architecture document says the portal calls the Rating API: the **logical** `CONSUMES_API` has `documentation` evidence, trust `documented`. **No physical** app service → endpoint relationship is recorded, because no configuration shows it. If the Azure source later reads an app setting naming the endpoint, a physical `CONSUMES_API` is added with `provider_configuration` evidence (trust `discovered`), flagged `cross_provider` and `cross_environment` (UAT → prod) |
| Revisions | R1 records the entities and the documented logical edge. The later configuration-based edge is a new relationship in R2; R1's view is unchanged when read as of R1 |

### S2. AWS workload consuming Google Cloud Pub/Sub

| Aspect | Model |
|---|---|
| Entities | `infra.scope` AWS `account`; `infra.cluster` "claims-ecs" (`cluster_kind` ecs); `infra.workload` "quote-consumer" (`native_type` `AWS::ECS::Service`); `infra.scope` GCP `organization` → `folder` → `project` "claims-events-prod"; `infra.messaging_channel` "quote-issued" (`native_type` `pubsub.googleapis.com/Topic`, `channel_kind` topic); `core.event_channel` "QuoteIssued" |
| Identifiers | Workload: `aws.arn` `arn:aws:ecs:eu-west-1:111111111111:service/claims-ecs/quote-consumer`. Project: `gcp.resource_name` `//cloudresourcemanager.googleapis.com/projects/claims-events-prod`. Topic: `gcp.resource_name` `//pubsub.googleapis.com/projects/claims-events-prod/topics/quote-issued` |
| Relationships | QuoteIssued `DEPLOYED_AS` the Pub/Sub topic; the workload `SUBSCRIBES_TO` the topic (`subscription_name` "quote-consumer-sub") |
| Containment | AWS account `CONTAINS` cluster `CONTAINS` workload; GCP organization → folder → project `CONTAINS` topic |
| Evidence and trust | `contract` evidence: the IaC manifest that declares the subscription and the consumer (artifact path plus content hash). Trust `documented`; flagged `cross_provider` |
| Revisions | If the consumer moves to a new ECS service (new ARN), ADR-0003 applies: no automatic re-pointing without a stable secondary key; the old workload's subscription stays in history |

### S3. Alibaba Cloud ECS instance connecting to an Azure service

| Aspect | Model |
|---|---|
| Entities | `infra.scope` Alibaba `account` → `resource_group` "rg-pricing"; `infra.compute` "ecs-pricing-01" (`native_type` `ACS::ECS::Instance`, `compute_kind` vm); `azure.service_bus_namespace` "sb-claims-prod" |
| Identifiers | ECS: `alibaba.arn` `acs:ecs:cn-hangzhou:1000000000000001:instance/i-exmp0001`. Service Bus: `azure.arm` `/subscriptions/00000000-0000-0000-0000-000000000002/resourcegroups/rg-claims-prod/providers/microsoft.servicebus/namespaces/sb-claims-prod` |
| Relationships | ECS `CONNECTS_TO` Service Bus namespace (`connectivity_kind` `configured_endpoint`) |
| Containment | Alibaba account `CONTAINS` resource group `CONTAINS` ECS; Azure hierarchy for the namespace |
| Evidence and trust | A network architect's assertion, accepted by a steward (`human_assertion`): trust `curated`, verification `unverified`, flagged `cross_provider`. It records that the endpoint is **configured**, not that traffic flows |
| Revisions | R1 records the connection. When the instance is replaced (new instance ID, so a new entity), R2 closes the old connection and the old instance gets `record_state = removed` with deletion evidence. A steward re-records the connection for the new instance with fresh evidence; it is not copied automatically |

### S4. Oracle Cloud workload connecting to an on-premises database

| Aspect | Model |
|---|---|
| Entities | `infra.scope` OCI `tenancy` → `compartment` "claims"; `infra.cluster` "oke-claims" (`cluster_kind` kubernetes); `k8s.namespace` "policy"; `k8s.workload` "policy-sync" (provider `oci`, from its cluster); `infra.scope` on-premises `site` "dc-north"; `infra.compute` "db-host-07" (`compute_kind` physical); `infra.data_store` "POLICYDB" (`store_kind` relational_db, `platform` "Oracle Database"); `core.dataset` "Policy Records" |
| Identifiers | Compartment: `oci.ocid` `ocid1.compartment.oc1..exmpcompartment0001`. Cluster: `oci.ocid` `ocid1.cluster.oc1.eu-frankfurt-1.exmpcluster0001`. Workload: `k8s.uid` `oci.ocid:ocid1.cluster.oc1.eu-frankfurt-1.exmpcluster0001#7a1c…`. On-premises host and database: no provider-issued key, so `source.cmdb` keys `CI-004211`, `CI-004212` (unique per organization and source) |
| Relationships | Policy Records `DEPLOYED_AS` POLICYDB; the workload `READS_FROM` POLICYDB and `WRITES_TO` POLICYDB (**two** records) |
| Containment | OCI tenancy `CONTAINS` compartment `CONTAINS` cluster `CONTAINS` namespace `CONTAINS` workload; site `CONTAINS` host `CONTAINS` database |
| Evidence and trust | The integration specification documents both reads and writes: `documentation`, trust `documented`, flagged `cross_provider` (`oci` → `on_premises`). **No `CONNECTS_TO` is recorded:** a documented read is not evidence of a network path. If the network team's configuration for the dedicated link is later imported, that is a separate fact with its own evidence |
| Revisions | If writes are decommissioned, a later change set retires only `WRITES_TO`; `READS_FROM` history and trust are untouched (ADR-0017 §5) |

### S5. A business system spanning Azure, AWS and Alibaba Cloud

| Aspect | Model |
|---|---|
| Entities | `core.system` "Claims Platform"; `core.application` "Claims Portal" (Azure, S1), "Rating Engine" (AWS), "Pricing Batch" (Alibaba, S3); their physical deployments |
| Identifiers | Applications: `org.key` APP-0101, APP-0103, APP-0104; physical entities as in S1–S3 |
| Relationships | Each application `MEMBER_OF` Claims Platform; each application `DEPLOYED_AS` its workloads or instances in its provider; Claims Platform `SUPPORTS_CAPABILITY` "Claims Settlement" (`direct`) |
| Containment and membership | `MEMBER_OF` is logical and many-to-many (Pricing Batch may also be `MEMBER_OF` a "Pricing" system). There is **no** `CONTAINS` from the system to any resource: a system is not located in any provider |
| Evidence and trust | Membership: `human_assertion` by the domain architect (trust `curated`); deployments: each provider's own evidence |
| How "spans three providers" is answered | By a bounded read-time traversal (system ← `MEMBER_OF` applications → `DEPLOYED_AS` → `provider`). It is computed and labeled as derived; it is **never** stored as a fact or as `DEPENDS_ON` |
| Revisions | Adding a fourth application to the system is one new `MEMBER_OF` in a new change set; the system as of an earlier revision still shows three |

### S6. Two Atlas organizations with similarly named resources

| Aspect | Model |
|---|---|
| Entities | Organization A (`default`) and organization B (a future second organization). Both have an `azure.resource_group` named "rg-claims-prod" and an `infra.scope` AWS account named "claims-prod" |
| Identifiers | Different subscriptions, so different ARM IDs: two entities. Even an **identical** provider key in both organizations (for example a provider account shared through a managed-service arrangement) gives two separate entities, because uniqueness is `(org_id, namespace, normalized_key)` |
| Relationships | None across organizations: composite foreign keys make a relationship between them impossible (ADR-0016) |
| Matching | Similar or equal names never match (ADR-0003). There is no cross-organization matching at all |
| Evidence and trust | Evidence, assertions and cases are organization-scoped; a source configured for organization A cannot write to B |
| Revisions | Each organization has its own revision counter and snapshots: A's revision 120 and B's revision 3 are unrelated, and neither can see the other's history |

## Onboarding a new provider later

Example: Huawei Cloud, once a pilot needs it.

| Step | Where | What | Table change? |
|---|---|---|---|
| 1 | atlas-specs | Taxonomy MINOR: provider key (if not listed); `scope_kind` vocabulary and nesting; `native_type → category` mapping; attribute schema for `provider_attributes`; optional provider-specific types **only if** rules or identity need them | No |
| 2 | atlas-specs | ADR-0003 registry: the provider's identity namespace(s), with validation, normalization, case rule and uniqueness scope, plus golden valid and invalid examples | No |
| 3 | atlas-backend | One reviewed, pure normalizer function per new namespace, tested against the golden examples; reference-data seed from the pinned taxonomy (a data migration, not DDL) | No |
| 4 | atlas-specs, backend | Synthetic fixture entries and tests for the new provider | No |
| 5 | Later phase, separate approval | A connector (BRD SDK family, tech §7), read-only and least-privilege (DEC-010). Not needed for manual modeling or import | No |
| 6 | atlas-frontend | Nothing for basic support: icons come from the category. An optional provider label or logo needs asset licensing (DEC-061) | No |

**Never needed:** new entity or relationship tables, new columns, changes to revisions, provenance or tenancy, a plugin runtime, a graph database, or a PostgreSQL extension.

## Trade-offs and risks

| Trade-off | Effect | Mitigation |
|---|---|---|
| Neutral types are coarse | An AWS Lambda function and an ECS service are both `infra.workload`, told apart only by `native_type` | Add provider-specific types when a rule or attribute needs the difference; re-typing keeps IDs |
| Category-based rules are broad | Any `runtime_workload` may `CONSUMES_API` any `api_endpoint`, whichever provider | That is the intended semantics; evidence is still required for every fact |
| `provider_attributes` without a profile are unvalidated | Inconsistent detail across sources | Never used by rules; profiles added per provider |
| Case preservation for non-Azure keys | A provider that is actually case-insensitive could produce two identities for one resource | Only fold case where documented; steward merge (reversible) handles the rest |
| Cross-provider evidence is often one-sided | Trust is honest but rarely `verified` | That is correct behaviour (invariant 3) |
| More types (38 instead of 31) | Slightly larger v1 | The eight `infra.*` types replace provider catalogs that would otherwise be needed for every provider |

## Impact on the database schema

- Reference tables `provider`, `category`, `identity_namespace` and `native_type_mapping`, seeded from the pinned taxonomy.
- `entity_version`: `provider`, `category` (denormalized from the type for indexes), `native_type`; index `(org_id, provider, category)` on current rows.
- `relationship_version`: `cross_provider`.
- `external_identity.namespace` references `identity_namespace`.
- See ADR-0001. No table is provider-specific.

## Impact on APIs and authorization (future)

- `provider` and `category` become filters and ABAC attributes, like type and environment.
- Provider keys may reveal account structure: they carry classification and are returned only to authorized callers (ADR-0003).

## Migration and compatibility

- A new provider or namespace is a MINOR taxonomy version plus reference-data seed.
- Replacing `azure.generic_resource` (revision 2) with `infra.resource` happens before any data exists, so it costs nothing now.

## Requires owner confirmation

1. Option A: categories, provider-specific types only where needed, eight provider-neutral `infra.*` types, rules by category.
2. The provider list and that providers are reference data, not entities.
3. Provider hierarchies through `infra.scope` with per-provider `scope_kind` rules; physical containment within one provider.
4. Cross-provider relationships with the computed `cross_provider` flag, and one-sided evidence recorded as such.
5. The onboarding procedure: no table changes, no plugin runtime.
