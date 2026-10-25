# Acceptance test data

## `canonical-golden-v1/`: canonical graph golden fixture (ATLAS-002 CP2)

**Fixture version:** 1.0.0 · **Taxonomy:** 1.0.0, plus the synthetic, test-only overlay `1.1.0-test.1` · **Generator:** `tools/generate_golden.py` (`make golden`) · **Validator:** `tools/check_canonical.py` (`make canonical`, run in CI)

All names, keys, account numbers, GUIDs and artifacts are **synthetic**. The fixture is generated deterministically: regenerating it gives byte-identical files, and CI checks that. Every relationship is allowed by the taxonomy version its row names and carries evidence; nothing was added to reach a count.

### Files

| File | Content | Schema (`urn:atlas:schema:canonical:…:v1`) |
|---|---|---|
| `organizations.json` … `graph_snapshots.json` | Stored canonical rows, one table per file, one record per line | `organization`, `change-set`, `entity`, `entity-version`, `relationship`, `relationship-version`, `external-identity`, `evidence`, `fact-assertion`, `graph-snapshot` |
| `inputs/aws-inventory.r2.json` | Loader input (import batch) applied at revision 2; it carries no actor, revision or server fields (anti-spoofing) | `import-batch` |
| `inputs/aws-inventory.r2.expected-report.json` | Expected plan for first apply and replay, and the rejected items with reasons | — |
| `expected-as-of.json` | Entity and relationship counts and graph hash at every revision of every organization | — |
| `expected-findings.json` | Expected ADVISORY findings by rule; HARD and DOMAIN are zero | — |
| `taxonomy-overlay.1.1.0-test.1.json` | Synthetic overlay: maps `bigquery.googleapis.com/Dataset` to `data_store` | `taxonomy-overlay` |
| `manifest.json` | File inventory, record counts, content hashes and coverage counts | `fixture-manifest` |

The stored rows represent what the system records. `created_at` and `db_role` on change sets are representative values: in a database the server sets them (ADR-0008 §10), so database tests compare every other field.

### Size

252 entities and 617 relationships in two organizations. This is below the ~700-relationship target: the fixture was not padded with relationships to reach a count.

| Organization | Entities at head | Relationships at head | Revisions |
|---|---|---|---|
| `default` (Example Insurance Group) | 242 | 606 | 8 |
| `example-subsidiary` | 10 | 8 | 1 |

By provider (`default`, at head): 110 logical, Azure 88, AWS 14, Google Cloud 8, on-premises 8, Alibaba Cloud 5, OCI 5, private cloud 2, other (mainframe) 2. By environment: PROD 71, UAT 18, SIT 7, DEV 6, DR 2, UAT-2 2, PERF-LAB 1, shared 8, unknown 16. `manifest.json` has the full breakdown by category and relationship type.

### Coverage

| Required coverage | Where |
|---|---|
| Applications and business systems | 12 applications, 5 systems; `MEMBER_OF` systems and domains (many-to-many) |
| Azure, AWS, Google Cloud, Alibaba Cloud, OCI, on-premises (plus private cloud and a custom mainframe) | Provider sections of the generator; AWS arrives by import (R2) |
| DEV, SIT, UAT, PROD, DR and organization-defined environments | `DEV`, `SIT`, `UAT`, `UAT-2` (kind `uat`), `PROD`, `DR` (kind `dr`), `PERF-LAB` (kind `other`) |
| Shared resources with one identity | `apim-nonprod`, `aks-nonprod`, `rg-platform-nonprod`, `vnet-nonprod`, `kv-claims-nonprod`: `shared` scope with `MEMBER_OF` environments |
| Cross-provider and cross-environment relationships | 7 cross-provider; 5 cross-environment, each with its own evidence |
| Evidenced UAT-to-PROD connectivity | UAT BFF `CONSUMES_API` the prod APIM `quotes-api` (verified, with expiry); UAT `claims-api` `CONNECTS_TO` the prod Service Bus; UAT `uw-rules` consumes the prod policy API; UAT `policy-api` reads the prod database |
| Deployment roles | `primary`; `active_secondary` (DR SQL geo-secondary that also serves production reads); `standby` (DR AKS workloads, Alibaba ECS, on-premises `POLICYDB-DR`); `unknown`; and absent (A-07) |
| DR not only as an environment label | PROD resources in a DR region (`aks-dr`, `sql-claims-dr`) with standby roles, plus an on-premises DR site in the `DR` environment |
| Unknown provider resources | `infra.resource`: Azure Front Door profile, AWS DynamoDB table and CloudFront distribution, on-premises MQ broker, and Google BigQuery dataset until R7 |
| Reclassification without ID change | R6 neutral data store → `azure.sql_database` (steward links its ARM ID); R7 `infra.resource` → `infra.data_store` (taxonomy overlay) |
| Physical containment and logical membership | 173 `CONTAINS` (resource and logical families, single parent) and 78 `MEMBER_OF` |
| `READS_FROM` and `WRITES_TO` as separate facts | 39 and 25, plus `STORES_IN` where the direction isn't established |
| Missing or incomplete ownership | A-01 findings (8) |
| Different trust levels | `discovered`, `documented`, `curated`, `stale` (2024 document), `conflicted` (two sources disagree on a VM's location); `verified` facts with expiry |
| Two organizations with overlapping names and keys | `example-subsidiary` reuses names (`rg-claims-prod`, `Claims Portal`, `APP-0101`), the same Azure tenant GUID and the same AWS account key: separate entities, no collision |

### Revisions (organization `default`)

| R | Kind, channel, actor | Demonstrates |
|---|---|---|
| 1 | `fixture_load`, `fixture_cli`, service `fixture-loader` | Creation; snapshot `pilot-baseline` |
| 2 | `import`, `import`, service `import-worker` | Import batch → exactly its planned facts; the replay is a no-op; a non-representable read (`READS_FROM` an `infra.resource`) is rejected and reported, not stored |
| 3 | `steward_edit`, `api`, human steward | Modification (rename, same ID); ownership change; retiring a `STORES_IN` once directional facts exist |
| 4 | `steward_edit`, human | Relationship retirement (a mistake) |
| 5 | `revert` of 4, human | Reversion through a new revision; snapshot `after-revert`. Its graph hash equals revision 3's: the hash depends on facts, not history |
| 6 | `steward_edit`, human | Provider-specific reclassification and re-parenting; a document-key identity closed; ARM identity linked |
| 7 | `migration`, `migration`, system `taxonomy-migration` | Taxonomy-version-aware re-typing under `1.1.0-test.1` |
| 8 | `import`, service | A read that only became representable after R7; snapshot `head` |

Historical reconstruction: `expected-as-of.json` gives the graph at every revision; the tests check, for example, that the retired read is absent only at revision 4.

### Use in CP3/CP4

- CP3 loads the stored rows into `atlas_test` to test constraints, privileges and triggers, and re-runs the H-rules as SQL checks.
- CP4's loader applies `inputs/` and must reproduce revision 2 exactly, with a no-op replay and the same rejection report. The as-of graph hashes in `expected-as-of.json` are the acceptance oracle.
- Regenerate with `make golden` after changing the generator, and commit the result: CI fails if the committed files differ.
