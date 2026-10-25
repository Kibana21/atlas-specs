# ADR-0003 — External identity, matching precedence, aliases and merge/split

| Field | Value |
|---|---|
| Status | **Proposed**. Revision 2 (25 Oct 2026) after the owner's CP1 review: D3 and D5 approved, D4 approved with clarification (original and normalized keys, normalization, case, identity changes, collisions); revision 1 was 24 Oct 2026 |
| Register | DEC-025 (Proposed); field-authority principles of DEC-034 (Proposed) |
| Owner (proposed) | Data/Platform lead + Enterprise Architecture; approval: Atlas owner |
| Related | INV-01, INV-04, INV-06, MOD-04; tech §3.2, §7.3 (ADR-003, ADR-012 in tech §22); ADR-0015, ADR-0016, ADR-0018 |

## Problem

Atlas receives the same real-world thing from several sources: Azure Resource Graph, APIM, AKS, CSV import, human curation. It must decide when two records are the same canonical entity:

- deterministically;
- auditably;
- reversibly;
- **without ever merging two entities only because their names are similar** (owner, tech §3.2).

In ATLAS-002 the decision governs the schema and the fixture loader. Connector-driven reconciliation is Phase 2 (BL-203), but it must fit this model without schema changes.

## Model

1. **Canonical entity:** Atlas ID (UUIDv7, ADR-0015). It owns no provider key.
2. **External identity:** `(org_id, namespace, normalized_key) → entity_id`, unique per organization among current bindings. Each identity has:
   - `original_key`: the identifier **exactly as the provider or source supplied it** (case, encoding and spelling preserved), for display, copying (DEV-05) and audit;
   - `normalized_key`: the canonical comparison form, derived from `original_key` by the namespace's rule and its `normalization_version`;
   - a `match_method`: `provider_id`, `approved_alias`, `org_key` or `steward`;
   - a validity interval `[revision_from, revision_to)` (ADR-0008). "Active" means `revision_to IS NULL`; a superseded or retired binding is a closed interval plus the reason recorded in its change set. Rows are never edited or deleted.
3. **Alias:** a human-meaningful name for an entity, scoped by `(type_key, environment_id or none)` with status `proposed`, `approved` or `retired`. Only **approved** aliases resolve. A display name is *never* an alias automatically.
4. **Organization key:** an organization-controlled key for manually modeled things (for example an application code `APP-0042`), stored as `namespace = org.key`.

### Namespaces and normalization (v1)

| Namespace | Key | Normalization |
|---|---|---|
| `azure.arm` | Azure Resource ID (`/subscriptions/{sub}/resourceGroups/{rg}/providers/{ns}/{type}/{name}[/…]`) | See "Azure Resource IDs" below: validate, then lowercase; malformed IDs are rejected, never repaired |
| `azure.tenant_id` | Entra tenant GUID | Lowercase canonical GUID |
| `azure.subscription_id` | Subscription GUID | Lowercase canonical GUID (also embedded in ARM IDs) |
| `k8s.uid` | `{cluster ARM ID}#{metadata.uid}` | ARM part as above; UID lowercase |
| `apim.api` | `{APIM service ARM ID}#api:{apiId};rev={revision}` | ARM part as above |
| `apim.operation` | `{apim.api key}#op:{operationId}` | **Reserved**: no v1 type uses it (ADR-0017 G-T3) |
| `org.key` | Organization key | Trim, case-preserving, compared case-insensitively |
| `source.<connector>` | A source-native stable key without a better namespace | Per connector (Phase 2) |

## Azure Resource IDs (D4, revised)

**Azure Resource IDs are the preferred external identity for Azure resources** where available. They are exact, provider-issued and present in every ARM-based API.

### Both forms are stored

| Column | Content | Used for |
|---|---|---|
| `original_key` | The ARM ID exactly as received from the source (first sighting for this binding) | Display, copy-to-clipboard, links back to the provider, audit |
| `normalized_key` | The canonical form below | Uniqueness, lookup, matching |
| `normalization_version` | Version of the rule that produced `normalized_key` (starts at `arm-1`) | Re-normalization migrations |
| `key_parts` | Parsed, normalized parts: `subscription_id`, `resource_group`, `provider_namespace`, `type_path` (for example `servers/databases`), `name_path` | Type-compatibility checks, containment evidence (ADR-0017 §3.1) |

Later sightings with different casing or spelling of the **same** normalized key do not change `original_key`. They are recorded on their evidence rows (`artifact_ref`), so every variant is auditable.

### Normalization rule `arm-1`

1. **Validate first; reject, never repair.** The input must:
   - start with `/subscriptions/{guid}`, or `/providers/` for tenant-level resources (for example management groups);
   - have no empty segments (`//`), no query string or fragment, no whitespace inside, and no `.` or `..` segments;
   - after `/providers/{namespace}`, alternate type and name segments (an even count);
   - be at most 2 048 characters.

   A malformed ID is rejected with a reason and reported. It is not cleaned up, because "repairing" an ID can turn it into another resource's ID.
2. **Trim** surrounding whitespace and remove **one** trailing `/`.
3. **Case:** lowercase the whole ID with Unicode-aware simple case folding. Azure Resource Manager treats resource IDs as case-insensitive, and sources really do return mixed casing for the same resource (for example `resourceGroups` vs `resourcegroups`).
4. **GUID segments** (subscription) in lowercase canonical 8-4-4-4-12 form.
5. **Percent-encoding:** kept exactly as received; never decoded. Two IDs that differ only in encoding are therefore different keys. If that happens for one resource, a steward links them (an exceptional case, reported).
6. The `azure_type` system attribute (ADR-0017) is `provider_namespace/type_path`, also lowercase.

Changing any of these steps is a new `normalization_version` with a re-normalization migration in one change set and a collision report, reviewed like a breaking change.

### Identity changes

| Event | Effect on the ARM ID | Behaviour |
|---|---|---|
| Casing differs between sources | None after normalization | Same entity; variants kept on evidence |
| Tag, SKU or setting change | None | Same entity; a new version only if a modeled attribute changed |
| Subscription moved to another Azure tenant | None (the tenant is not in the ID) | Same entity; its `CONTAINS` from the old tenant closes and one from the new tenant opens |
| Resource moved to another resource group or subscription, or renamed (where the type allows) | **New ARM ID** | A new ID never silently re-points an existing entity. If an **independent stable key** matches (for example `k8s.uid`, or a recorded provider GUID such as `resourceGuid` where the type exposes one), the move is linked automatically: the old binding closes, the new one opens, both in one change set with the old ID kept in history. Otherwise: a `match_candidate` for a steward; until decided, the new ID is an unattached observation, and the old entity goes `stale` after the source's grace policy (never removed by absence, INV-06) |
| Deleted and recreated with the same ARM ID | Same ID | Same entity, **unless** a recorded stable secondary key differs: then a conflict case, not a silent continuation |
| Deleted, with provider deletion evidence | — | Tombstone (`record_state = removed`); the binding closes. A later reuse of the same ID by a new resource opens a case rather than reviving the tombstone automatically |

### Collisions specific to ARM IDs

| Situation | Behaviour |
|---|---|
| Two different `original_key`s normalize to the same key | One identity. If both arrive in one input for **different** entities (for example a fixture with two records), the whole input is rejected with both records named |
| A normalized key is already bound to an entity of an **incompatible type** (`azure_type` disagrees with the entity's type) | No link; a case. Typical cause: a generic resource that should be re-typed (ADR-0017 §2.4) |
| The ARM ID's parsed hierarchy contradicts a recorded `CONTAINS` (database ID naming another server) | The containment relationship is rejected; a case |
| The same ARM ID appears in two organizations (future) | Allowed: uniqueness is per organization (ADR-0016) |
| An `azure.subscription_id` identity and the subscription's `azure.arm` identity point to different entities | Rejected as ambiguous; a case |

**Tenant scope:** ARM IDs contain the subscription. The subscription's tenant is a modeled relationship (`azure.tenant` `CONTAINS` `azure.subscription`), not part of the key.

## Matching precedence (automatic steps stop at the first unique hit)

| Step | Rule | Automatic? |
|---|---|---|
| 1 | Exact `provider_id` identity in the same namespace (ARM ID, tenant/subscription GUID, `k8s.uid`, APIM keys) | **Yes**: links to that entity |
| 2 | Exact **approved** alias in the same scope (type plus environment) | **Yes** |
| 3 | Exact organization key (`org.key`) | **Yes** |
| 4 | Anything else: normalized-name similarity, same parent and type, fuzzy/trigram, heuristics | **Never.** Produces `match_candidate` rows (score, reasons) for steward review only (Phase 2 generation; ATLAS-002 stores the structure) |

**Ambiguity:** two or more different entities at the *same* step, or steps that disagree (step 1 says A, step 3 says B):

- no link is made;
- a `reconciliation_case` is opened with every candidate and its evidence;
- the incoming record stays an unattached observation until a steward decides.

**Type compatibility:** an automatic match is rejected if the existing entity's type is incompatible with the incoming type under the taxonomy (ADR-0017). For example, an ARM ID of type `Microsoft.Sql/servers/databases` can't match an `azure.key_vault` entity. A rejected match opens a case.

**Environment:** identities and approved aliases are environment-qualified where the namespace is environment-specific, so production and UAT objects never collapse (MOD-04).

## Collisions and duplicates

| Situation | Behaviour |
|---|---|
| Incoming key already bound to an entity by a current (open) binding | Not a new entity: step 1 links to the bound entity. If types conflict, the match is rejected and a case is opened |
| Two approved aliases would resolve the same scoped name to different entities | Prevented: partial unique index on approved aliases per `(org_id, scope, alias)` |
| An alias equals another entity's organization key | Alias approval is refused with an explanation |
| Suspected duplicates (same normalized name, parent and type) | `match_candidate` for review; never merged automatically |
| Same name in different environments | Distinct entities (no candidate unless other evidence agrees) |

## Merge and split (reversible, audited)

- **Merge (steward):**
  - the loser becomes a tombstone with `merged_into = survivor`, keeping its ID forever (ADR-0015);
  - identities and aliases move to the survivor: the old bindings close and new ones open in the same change set;
  - relationships are re-pointed by **new** relationship versions in the same change set;
  - evidence is never rewritten.
- **Split:** the reverse: a new entity receives selected identities and relationships, recorded in one change set.
- **Undo** is a new change set restoring the prior bindings. History is never deleted.
- In ATLAS-002 the schema supports this (columns, statuses, change sets). The steward workflow and UI are later work (BL-119, BL-203).

## Field-level source authority (DEC-034, principles only)

- Precedence is explicit per `(source kind, field)`. For example, Azure is authoritative for `location` and SKU, but not for the business owner.
- On a same-precedence conflict, the prior approved value is kept, the field becomes `conflicted` (ADR-0018) and a case is opened.
- Implementation is Phase 2. ATLAS-002 only needs the evidence model to hold competing values.

## Options considered

| Option | Verdict |
|---|---|
| **A. Deterministic precedence on exact keys + steward review for everything else** (above) | **Recommended**: auditable, reversible, never merges on names |
| B. Probabilistic entity resolution with automatic merge above a confidence threshold | Rejected: silent merges on similarity violate the owner's rule and are hard to explain or undo |
| C. Manual identity only (no automatic provider-ID matching) | Rejected: safe but does not scale to discovery, and humans re-type ARM IDs incorrectly |

## Impact on the database schema

Tables `external_identity` (with `original_key`, `normalized_key`, `normalization_version`, `key_parts`), `entity_alias`, `match_candidate`, `reconciliation_case` (shell in ATLAS-002), and `entity_version.merged_into`:

- unique `(org_id, namespace, normalized_key)` for current bindings (`revision_to IS NULL`);
- partial unique index for approved aliases;
- index `(org_id, entity_id)` for reverse lookup.

See ADR-0001.

## Impact on APIs and authorization (future)

- Provider keys can be sensitive (subscription structure), so they carry classification, and lookup by external key is an authorized operation.
- A failed lookup returns 404, revealing nothing about other scopes.
- Copyable resource IDs (DEV-05) come from active identities.

## Migration and compatibility

- New namespaces are additive (a taxonomy minor version).
- Changing a normalization rule needs a migration that re-normalizes keys inside a change set, plus a collision report. It is reviewed like a breaking change.

## Requires owner confirmation

1. Matching precedence: provider ID → approved alias → organization key; similarity never merges.
2. Azure Resource ID as the preferred Azure identity: both original and normalized forms stored; normalization `arm-1` (validate, reject, lowercase, no decoding); the identity-change and collision tables above.
3. Ambiguity, collision and type-conflict behaviour (no link, open a case).
4. Merge and split as reversible, audited change sets; tombstones keep IDs.
