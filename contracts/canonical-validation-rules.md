# Canonical graph validation rules (v1)

**Applies to:** `contracts/taxonomy/atlas-taxonomy.v1.json`, `contracts/schemas/canonical/*.v1.json`, canonical fixtures and, from CP3, the backend's canonical store · **Status:** ATLAS-002 CP2 deliverable, derived from the Accepted ADR-0001, 0003, 0008, 0015–0019; updated at Gate G2 (25 Oct 2026) for owner decisions U-1…U-3 and taxonomy 1.1.0 · **Reference implementation:** `tools/canonical_rules.py` (rule IDs below are the IDs it reports)

## 1. Classes

| Class | Meaning | Where it is enforced (CP3 onwards) | Effect |
|---|---|---|---|
| **HARD** | Identity, referential integrity, organization isolation, revision consistency, security | PostgreSQL constraints, column privileges and the two approved triggers wherever practical; otherwise the write path before commit | The change set is rejected |
| **DOMAIN** | Taxonomy and graph consistency required before a fact is published | The service layer (domain validator) inside the publishing transaction | The change set is rejected with a readable reason (MOD-03) |
| **ADVISORY** | Architecture standards, missing metadata, cross-environment concerns, incomplete discovery | Reports and, later, review queues | Never blocks; never changes facts |

Principles (owner guidance, 25 Oct 2026):

- Database constraints stay focused on structural integrity and security. Architecture rules are domain validation or advisory findings, not database rules.
- Imperfect real-world observations are **preserved** as evidence or reviewable findings when they can't safely become canonical facts. They are never silently discarded (see D-04 on imports).
- Only two triggers are proposed, both already in ADR-0008: set-once `revision_to`, and server-set `created_at`/`db_role` on change sets. There is no trigger for the relationship matrix, and no arbitrary structural limits (the only depth bound is the containment walk of ADR-0017 §3.1).

## 2. HARD rules

| ID | Rule | Source | Enforcement (CP3) |
|---|---|---|---|
| H-01 | Every record matches its JSON Schema (types, enumerations of system fields, UUIDv7 IDs, attribute names) | ADR-0001, ADR-0015 | Column types, `CHECK`, `NOT NULL` |
| H-02 | IDs are unique | ADR-0015 | Primary keys |
| H-03 | No reference crosses organizations | ADR-0016 | Composite FKs `(org_id, …)` |
| H-04 | Every reference resolves | ADR-0001 | Foreign keys |
| H-05 | Revisions are gap-free per organization; every revision used exists as a change set; `revision_to > revision_from`; a revert targets an earlier revision | ADR-0008 §3 | Counter row lock; `CHECK`; FKs to `change_set` |
| H-06 | Each fact has exactly one current version, and its versions are contiguous | ADR-0008 §2 | Partial unique index; set-once trigger |
| H-07 | A `(org, namespace, normalized_key)` is bound to at most one entity at a time | ADR-0003 | Partial unique index (current bindings) |
| H-08 | `normalized_key`, `normalization_version` and `key_parts` follow the namespace's approved rule; planned and reserved namespaces are rejected | ADR-0003 | Normalizer on the write path |
| H-09 | One relationship record per `(org, rel_type, from, to, discriminator)`; no self-relationships; the discriminator equals its defining attribute | ADR-0017 §4, ADR-0001 | Unique key; `CHECK (from_id <> to_id)` |
| H-10 | At every revision, a present relationship has present endpoints | ADR-0008 §5 | Publishing transaction (integrity step) |
| H-11 | The actor's namespace is bound to its kind; actor keys follow their namespace format | ADR-0008 §10 | `actor_namespace` reference table + `CHECK` |
| H-12 | An assertion's evidence is in the same organization, has the same kind, and existed by the assertion's revision | ADR-0018 | Composite FKs; `CHECK` |
| H-13 | Attribute names are snake case and never suggest secrets (`password`, `secret`, `token`, `connection_string`, `private_key`, `access_key`, `credential`) | DEC-010, public-repo rule | Schema (`attribute_name`); service layer |
| H-14 | At every revision: at most one containment parent per entity; containment is acyclic | ADR-0017 §3.1 | Publishing transaction (ancestor walk) |
| H-15 | Integrity of published artifacts: snapshot graph hashes, expected as-of results, change-set input hashes, manifest file hashes, the import plan and its replay | ADR-0008 §4, §8 | Fixture and loader tests |
| H-16 | Fixture determinism: regeneration is byte-identical | ADR-0008 §8 | CI |
| T-01…T-10 | Taxonomy self-consistency: unique keys; categories, parents, enumerations, namespaces, providers and pair references resolve; reserved types have no pairs; the type-level `MEMBER_OF` graph and `CONTAINS` graph are acyclic (beyond declared self-nesting) | ADR-0017 §1 | CI on the taxonomy artifact |

## 3. DOMAIN rules

| ID | Rule | Source |
|---|---|---|
| D-01 | The type exists in the taxonomy version the version row names; required attributes and enumeration values are valid. A required field that is **unresolved** (its current assertions conflict and there is no prior approved value) is accepted; a field that is simply missing is rejected (I-6) | ADR-0017 §2, ADR-0018 |
| D-02 | Category, provider and native type agree with the type: logical types have none; physical types have a registered provider and a `native_type` (except `azure.tenant`, which has no ARM type: ADR-0017 §2.1, ADR-0019 §3, decision U-2); Azure types have their fixed native type; Kubernetes objects take their cluster's provider; `private_cloud`, `on_premises` and `other` need `platform` | ADR-0017, ADR-0019 §3 |
| D-03 | Environment scope: environment-neutral types have none; environment-scoped types have `single`, `shared` or `unknown`; `single` points to a `core.environment`; `shared` has at least one evidenced `MEMBER_OF` environment at every revision | ADR-0017 §2.3 |
| D-04 | The relationship is allowed by the matrix of its taxonomy version (types or categories, attributes, discriminator values, `connectivity_kind` per pair); reserved types are rejected. On import, a rejected relationship is reported in the import report with its reasons, never stored or downgraded | ADR-0017 §4, §7.4 |
| D-05 | Every existence assertion of a relationship uses an evidence kind allowed for its type. From taxonomy 1.1.0, `contract` is allowed for `CONTAINS` and `DEPLOYED_AS` (decision U-1): such facts are `documented`, never observed | ADR-0017 §4.1, ADR-0018 |
| D-06 | Containment matches the provider's native hierarchy where the key shows it (an Azure child's ARM ID lies inside its parent's) | ADR-0017 §3.1 |
| D-07 | `MEMBER_OF` an environment only for entities with shared scope (part of D-04's pair check) | ADR-0017 §3.2 |
| D-08 | `cross_environment`, `shared_endpoint`, `cross_provider` and the relationship's `environment_id` equal the values derived from the endpoints; cross-environment only where allowed | ADR-0017 §4.4, ADR-0019 §6 |
| D-09 | `container_id` equals the current `CONTAINS` parent at every revision | ADR-0001 |
| D-10 | Re-typing: automatic transitions (neutral → provider-specific with the same native type; generic → neutral by mapping) in any change set; any other only by a steward or migration change set, and a migration only applies automatic transitions | ADR-0017 §2.4 |
| D-11 | `DEPENDS_ON` is never `discovered` | ADR-0017 §4.3 |
| D-12 | Every present fact has current evidence applicable to its claim, and its stored trust state equals trust function v1 (`contracts/trust-function.md`) at every revision where the version is current | ADR-0018, decision U-3 |
| D-13 | Attribution fits the channel: `fixture_cli`, `import` and `connector` are service identities; steward edits, merges and splits are human; migrations are system or service identities and use the `migration` channel | ADR-0008 §10 |
| D-14 | A revert leaves every fact touched by the reverted revision equal to its state before it | ADR-0008 §7 |
| D-15 | An identity namespace is allowed for the entity's type | ADR-0017 §2.2, ADR-0003 |
| D-16 | `infra.scope` nesting follows the provider's `scope_kind` rules | ADR-0019 §4 |
| D-17 | Import: identities resolving to different entities are ambiguous; no link (reported) | ADR-0003 |
| D-18 | Import: no identity match and no explicit fixture ID; never matched by name (reported) | ADR-0003, ADR-0015 |
| D-19 | A version stored as `verified` satisfies TF-V at its publication: a human verifier, not conflicted, stale or inferred, and current evidence that can support the claim (declared evidence alone never supports a physical claim) | ADR-0018 §3, decision U-3 |
| D-20 | Every asserted field's stored value equals the trust function's selected value: the agreed value, or for an unresolved conflict the prior approved value or none | ADR-0018 (conflict procedure) |

## 4. ADVISORY findings

| ID | Finding |
|---|---|
| A-01 | Application, system, service or dataset without an owner |
| A-02 | Cross-environment relationship (review it) |
| A-03 | Environment scope unknown on an environment-scoped resource (excluding scopes) |
| A-04 | Uncategorized resource (`infra.resource`) |
| A-05 | Cross-provider relationship that is not verified |
| A-06 | `STORES_IN` with no directional `READS_FROM`/`WRITES_TO` for the same pair |
| A-07 | `DEPLOYED_AS` without a `deployment_role` |
| A-08 | Physical resource without a known containment parent |
| A-09 | Application with no known deployment |
| A-10 | (Import) rejected items: reported in the import report (`expected-report.json` in fixtures) with rule and reasons, not as graph findings |
| A-11 | Neutral type whose native type is not in the provider's mapping for that category |
| A-12 | Stale or conflicted fact |

## 5. Interpretations (no new architecture decisions)

| # | Point | Interpretation used | Why |
|---|---|---|---|
| I-1 | Relationship `environment_id` when both endpoints are single-scoped in **different** environments | `null`; the `cross_environment` flag and the endpoints' memberships carry the classification. **Accepted by the owner at G2** (U-4) | ADR-0017 §4.4 says the relationship takes "the environment of its single-scoped endpoint(s)"; with two different ones there is no single value |
| I-2 | `native_type` of Kubernetes objects | The Kubernetes kind (`Namespace`, `Deployment`, …) | ADR-0019 §3 requires a native type; Kubernetes has no other provider type string |
| I-3 | `native_type` of `azure.tenant` | Absent. **Resolved at G2** (U-2): the exemption is retained and now stated in ADR-0017 §2.1 and §2.2 and ADR-0019 §3 | A tenant is not an ARM resource and has no ARM type. The taxonomy artifact already gives it no fixed native type |
| I-4 | Trust state for mixed evidence | **Superseded at G2** (U-3) by trust function v1 | `contracts/trust-function.md`; truth table `acceptance/test-data/trust-function-v1/cases.json` |
| I-5 | A re-type to a type that doesn't allow an existing identity namespace | The steward change set closes that binding (it stays in history) | ADR-0003: bindings close, never delete |
| I-6 | A required attribute whose sources disagree, with no prior approved value | The fact is published `conflicted` with the attribute absent; both assertions are kept and A-12 reports it. **Approved by the owner at G2 closure** | ADR-0018 conflict procedure (amended at G2 closure); invariant 3: unknown stays unknown, never an invented value |
