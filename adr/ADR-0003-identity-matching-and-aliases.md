# ADR-0003 — External identity, matching precedence, aliases and merge/split

| Field | Value |
|---|---|
| Status | **Proposed** (CP1 of ATLAS-002, 24 Oct 2026) |
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
2. **External identity:** `(org_id, namespace, normalized_key) → entity_id`, unique per organization. Each identity has:
   - a `match_method`: `provider_id`, `approved_alias`, `org_key` or `steward`;
   - a `status`: `active`, `superseded` or `retired`;
   - the change set that created it (ADR-0008).
3. **Alias:** a human-meaningful name for an entity, scoped by `(type_key, environment_id or none)` with status `proposed`, `approved` or `retired`. Only **approved** aliases resolve. A display name is *never* an alias automatically.
4. **Organization key:** an organization-controlled key for manually modeled things (for example an application code `APP-0042`), stored as `namespace = org.key`.

### Namespaces and normalization (v1)

| Namespace | Key | Normalization |
|---|---|---|
| `azure.arm` | Azure Resource ID (`/subscriptions/{sub}/resourceGroups/{rg}/providers/{ns}/{type}/{name}[/…]`) | Trim; lowercase (ARM IDs are case-insensitive); collapse duplicate `/`; no trailing `/`; must start with `/subscriptions/` or `/providers/` |
| `azure.tenant_id` | Entra tenant GUID | Lowercase canonical GUID |
| `azure.subscription_id` | Subscription GUID | Lowercase canonical GUID (also embedded in ARM IDs) |
| `k8s.uid` | `{cluster ARM ID}#{metadata.uid}` | ARM part as above; UID lowercase |
| `apim.api` | `{APIM service ARM ID}#api:{apiId};rev={revision}` | ARM part as above |
| `apim.operation` | `{apim.api key}#op:{operationId}` | As above |
| `org.key` | Organization key | Trim, case-preserving, compared case-insensitively |
| `source.<connector>` | A source-native stable key without a better namespace | Per connector (Phase 2) |

**Azure Resource IDs are the preferred external identity for Azure resources** where available. They are exact, provider-issued and present in every ARM-based API. Limits we design for:

- **Moves and renames change the ARM ID:** resource group or subscription moves, and renames for some types.
  - A *new* ARM ID never silently re-points an existing entity.
  - If an independent stable key matches (for example `k8s.uid`, or a recorded provider GUID such as `resourceGuid` where the type exposes one), the move is linked automatically and recorded as a `superseded` identity.
  - Otherwise it becomes a **match candidate** for a steward.
- **Delete-and-recreate with the same ARM ID:** treated as the same entity unless a recorded stable secondary key differs. In that case it is a conflict case, not a merge.
- **Tenant scope:** ARM IDs contain the subscription. The subscription's tenant is a modeled relationship (`azure.tenant` CONTAINS `azure.subscription`), not part of the key.

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
| Incoming key already bound to another *active* entity | Not a new entity: step 1 links to the bound entity. If types conflict, the match is rejected and a case is opened |
| Two approved aliases would resolve the same scoped name to different entities | Prevented: partial unique index on approved aliases per `(org_id, scope, alias)` |
| An alias equals another entity's organization key | Alias approval is refused with an explanation |
| Suspected duplicates (same normalized name, parent and type) | `match_candidate` for review; never merged automatically |
| Same name in different environments | Distinct entities (no candidate unless other evidence agrees) |

## Merge and split (reversible, audited)

- **Merge (steward):**
  - the loser becomes a tombstone with `merged_into = survivor`, keeping its ID forever (ADR-0015);
  - identities and aliases move to the survivor, the old bindings are recorded as `superseded`;
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

Tables `external_identity`, `entity_alias`, `match_candidate`, `reconciliation_case` (shell in ATLAS-002), and `entity.merged_into`:

- unique `(org_id, namespace, normalized_key)` for active identities;
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

## Requires owner approval

1. Matching precedence: provider ID → approved alias → organization key; similarity never merges.
2. Azure Resource ID as the preferred Azure identity, with the move/recreate rules above.
3. Ambiguity, collision and type-conflict behaviour (no link, open a case).
4. Merge and split as reversible, audited change sets; tombstones keep IDs.
