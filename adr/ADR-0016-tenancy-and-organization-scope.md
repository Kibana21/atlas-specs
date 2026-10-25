# ADR-0016 — Tenancy and organization scope

| Field | Value |
|---|---|
| Status | **Proposed** (CP1 of ATLAS-002, 24 Oct 2026). D1 approved by the owner on 25 Oct 2026, subject to consistency with the authoritative specifications; it becomes Accepted with the other rows at Gate G1. Content unchanged; no code depends on it yet |
| Register | DEC-058 (Open → Proposed) |
| Owner (proposed) | Architecture + Security; approval: Atlas owner |
| Related | INV-01, INV-05, MOD-04, MOD-06, GOV-01; tech §3.2, §9.3; ADR-0001, ADR-0003, ADR-0015 |

## Problem

The tech design says "segregate tenants and restricted domains if required" (§9.3) without deciding what a tenant is. The choice changes every table key, every uniqueness rule and the authorization model. It must be made before the first canonical table exists (blueprint §9).

**Owner direction (24 Oct 2026):**

- one organization;
- multiple Azure tenants inside it, with multiple subscriptions and environments;
- organization-level isolation designed into the schema from day one;
- future multi-organization support without a fundamental rewrite;
- an Azure tenant ID is **never** an Atlas organization ID.

## Terms

| Term | Meaning in Atlas |
|---|---|
| **Organization** | The isolation boundary for all Atlas data: canonical graph, identities, evidence, revisions, views, rules, users' grants. Atlas row `organization(id)` |
| **Azure tenant** | An Entra ID / Azure AD directory that owns subscriptions. A *source scope and a modeled object* inside one organization, identified by its tenant GUID as a provider key |
| **Subscription / resource group** | Azure resources inside an Azure tenant; canonical entities |
| **Environment** | An Atlas concept (prod, uat, dev, test…), a canonical entity; independent of tenants and subscriptions (one subscription can host several environments and vice versa) |
| **Restricted domain** | A part of the graph with tighter access inside one organization; handled by authorization (ABAC, DEC-051/073), not by tenancy |

## Options

### A. Implicit single organization (no organization column)

- Simplest schema and queries now.
- Adding a second organization later means adding a column and re-keying every unique constraint, foreign key and index, plus backfilling every row: the "fundamental rewrite" the owner wants to avoid.
- **Rejected.**

### B. Organization-scoped rows in one database (recommended)

- Table `organization`. Every organization-owned table carries `org_id uuid NOT NULL`.
- Every business uniqueness rule includes `org_id` (aliases, external identities, organization keys).
- Composite foreign keys `(org_id, x_id) → parent(org_id, id)`, so no row can reference another organization's row. A relationship can never connect entities of two organizations.
- IDs stay globally unique UUIDs (ADR-0015), so API paths need no organization segment.
- Exactly **one** organization row exists initially.
- Azure tenants are rows **inside** an organization:
  - modeled as entity type `azure.tenant` with provider key `azure.tenant_id`;
  - later also connector source scopes (P2).
- A second organization later is data plus authorization, not a schema change.

### C. Database (or schema) per organization

- Strongest isolation; per-organization backup and restore.
- Every migration runs N times, connection pools multiply, cross-organization operations become impossible, and local/CI complexity grows.
- Not needed for one organization.
- **Not chosen now.** Option B does not prevent a separate *deployment* for an organization that demands physical isolation later.

### D. Option B plus PostgreSQL row-level security (RLS) on `org_id`

- Defense in depth if a query forgets the organization filter.
- RLS policies need a per-session setting (`SET app.org_id`). They interact with connection pooling, and must never replace application authorization (tech §3.5).
- **Deferred.** Revisit with BL-104 (authorization) once request-scoped sessions exist. B keeps it possible because every table already has `org_id`.

## Recommendation

**Option B**, with D evaluated in ATLAS-003 (authorization).

1. `organization (id uuid PK, key text UNIQUE, display_name, created_revision)`. One row is created by the first migration that needs it, with a fixed, documented key (for example `default`). Its UUID is generated once, never derived from an Azure tenant.
2. Every organization-owned table: `org_id NOT NULL`, composite FKs to `(org_id, id)`, and `org_id` as the **leading** column of every business index (ADR-0001).
3. Azure tenant GUIDs are stored only as external identities (`namespace = azure.tenant_id`, ADR-0003) on `azure.tenant` entities.
   - The same Azure tenant GUID may appear in two organizations in a future multi-organization deployment (for example a shared provider). So uniqueness is `(org_id, namespace, key)`, never global.
4. The repository layer requires an `OrgScope` value on every query and write. A query without it does not type-check (mypy) and is rejected by tests. Cross-organization access returns "not found", never "forbidden" (anti-enumeration, DEC-035).
5. Revisions are per organization (ADR-0008). Organizations never share a revision sequence or a snapshot.

## Trade-offs and risks

| Benefit | Cost or risk | Mitigation |
|---|---|---|
| Multi-organization later needs no re-keying | `org_id` on every row and index (16 bytes per row; wider indexes) | Negligible at 10k–100k entities; measured in the CP4 benchmark |
| Cross-organization references impossible by construction | Composite FKs are more verbose | Generated migration helpers; tests |
| Same physical database: simple local/CI | A forgotten filter would leak across organizations | `OrgScope` required by the repository API; tests; optional RLS later |
| Azure tenants modeled as data | — | — |

## Impact on the database schema

- `organization` table; `org_id` column, composite PK-or-unique `(org_id, id)` and composite FKs on every canonical table (ADR-0001).
- Unique keys are always organization-scoped.

## Impact on APIs and authorization (future)

- The organization comes from the authenticated principal's grants (BL-104), not from a client parameter.
- With one organization, no API change is visible.
- Authorization decisions take `(principal, org, action, resource attributes)`. Restricted domains are ABAC attributes inside an organization.

## Migration and compatibility

- Additive: the first canonical migration creates `organization` and the default row.
- A future second organization: insert a row, assign grants. No data migration.
- If physical isolation is ever required: deploy a separate Atlas instance (same schema).

## Requires owner approval

1. Option B: organization-scoped rows, one database, one default organization now.
2. Azure tenant = entity plus provider key inside an organization; never an organization ID.
3. RLS deferred to ATLAS-003 (evaluate, not assumed).
