# ATLAS-002 — Evidence Record

**Status:** **CP0 complete** (G0 passed 2026-10-24; accepted by the owner 2026-10-25). **CP1 complete: Gate G1 passed** (2026-10-25). **CP2 delivered** (authorized 2026-10-25), awaiting owner review at Gate G2. CP3–CP5 not authorized. ATLAS-002 not Accepted.

## 1. CP0 — A001-DEF-01 / E-48: Redis readiness after an outage

**Authorization:** owner, 2026-10-24 (ATLAS-002 approved in principle; CP0 first, including the frontend `e2e/backend.ref` update).

### 1.1 Backend

| Item | Evidence |
|---|---|
| Defect reproduced first | New `tests/integration/test_ready_redis_recovery.py` on unfixed `585f3f5` (backend `v0.1.0`): the first readiness check after the outage gave **503 `failed_check: redis`**, logged `redis_command_failed` with `exc_type: ConnectionError`, `operation: ping`. The outage test passed (as designed) |
| Fix | `atlas.persistence.redis.AtlasRedis`: `Retry(NoBackoff(), 1, supported_errors=(ConnectionError,))`. One reconnect for a stale pooled connection, inside the existing 1 s wall-clock budget. Timeouts are not retried. Connection-level only, not a task retry (DEC-046 unaffected) |
| Regression tests | Integration (test-owned TCP fault proxy in front of the test Redis, DB 11, no keys written): (1) first readiness after an outage = 200 with `{database: ok, redis: ok}`; (2) during the outage 503 `failed_check: redis` in < 1.5 s with no host or port in the body, then recovery. Unit test pins the reconnect configuration. **Mutation check:** removing the fix makes (1) fail again |
| First CI run found a test defect | On Linux, `close()` from another thread does not interrupt a blocked `accept()`. The proxy kept accepting after "stop", so the restart hit "Address already in use". Fixed with a polled stop flag (50 ms accept timeout) and joining before close. Verified in the digest-pinned `python:3.12.15-slim-trixie` image without network (refuse, drop, same-port restart) before re-pushing |
| Pull request | [atlas-backend#8](https://github.com/Kibana21/atlas-backend/pull/8): 2 commits, 4 files (+179/−3), file list equal to the local diff |
| Merge commit | **`2987262db765586b7b3e99011074ff6bc2380ee5`** |
| CI | PR head `a3ad4a9` and `main` ([run 40094805311](https://github.com/Kibana21/atlas-backend/actions/runs/40094805311)): `static`, `unit`, `contract`, `security`, `integration`, `images` **6/6 success**. `integration` (job 120874710306): `test_ready_redis_recovery.py ..`, **37 passed** (35 before), `db 11: 0 keys match 'atlas:test:*'` |
| Local (fresh clone) | `make check` 164 passed, coverage 94.50 %; `make contract` conforms (28 passed); `make security` clean; `make integration` 29 passed, 8 `ci_auth` skipped by design |

### 1.2 Frontend

| Item | Evidence |
|---|---|
| `e2e/backend.ref` | `585f3f5…` → **`2987262db765586b7b3e99011074ff6bc2380ee5`** |
| New E2E test | "an API idle during a Redis outage reports Ready on its first check afterwards (A001-DEF-01)": open `/status` (Ready), Redis proxy down then up with no browser traffic, Check again → **Ready**, Redis Operational, response 200, no `redis_command_failed` log event for that correlation ID |
| Verified both ways | Against backend `v0.1.0` (temporary worktree): **1 failed** (`Expected "Ready"`, `Received "Degraded"`), 24 passed. Against `2987262`: 25/25 |
| Test-harness defect found and fixed | CP7 changed "Check again" from `disabled` to `aria-disabled` (focus fix, E-53). After that, the helper's `toBeEnabled()` returned immediately, so a test that expects the **same** state after "Check again" could pass on the previous screen. Tests expecting a state change still synchronized on the new label. `checkAgainAndWait` now waits for the readiness request to finish or fail and for `aria-disabled="false"`; the keyboard test likewise. No `toBeEnabled` remains in `e2e/` |
| Pull request | [atlas-frontend#9](https://github.com/Kibana21/atlas-frontend/pull/9): 1 commit, 6 files (+61/−11) |
| Merge commit | **`8ed5deb895dced78f98bff13cedd14c28a70f4ac`** |
| CI | PR head `5212682` and `main` ([run 40095359958](https://github.com/Kibana21/atlas-frontend/actions/runs/40095359958)): **7/7 success**. `e2e` (job 120876327973) checked out backend `2987262…`: **25 passed**, including the A001-DEF-01 test; `db 11: 0 keys match` |
| Local (fresh clone) | `pnpm check` 65 passed, 98.17 %; full audit clean; specs and generated OK; `pnpm e2e` 25/25 |

### 1.3 Gate G0

| Criterion | Result |
|---|---|
| Defect closed with a regression test that fails on the old code | ✔ backend integration and frontend E2E, both verified both ways |
| Required checks green on PR and `main` | ✔ backend 6/6, frontend 7/7 |
| ATLAS-001 tags and contract pins unchanged | ✔ `contract-v0.1.0` → `bfe4a09`, backend `v0.1.0` → `585f3f5`, frontend `v0.1.0` → `b9f235e`; both `specs.lock` = `bfe4a09` |
| Shared services | ✔ Redis DB 1 = 3 keys, DB 10 = 0, DB 11 = 0; no configuration change. PostgreSQL untouched (CP0 issues only `SELECT 1` through the runtime role) |

**Verdict: Gate G0 — PASS.**

### 1.4 Notes

| ID | Item | Status |
|---|---|---|
| N-01 | The harness weakness above went unnoticed in CP7 because every CP7 status test expected a *change* of state; it surfaced only when CP0 added a same-state test. Reviewed against the CP7 suite: every status, contract and accessibility test synchronized on a state change. The one weak spot was the keyboard test's **Enter** step, which did not prove that Enter triggered a refetch (its Space step did, through "Last checked"). It now waits for the readiness request. The G7 conclusions stand; this precision is recorded here | Fixed |
| N-02 | Stopping the preview worker by signalling its **child** process made taskiq's supervisor restart it and wait. A read-only check showed Ctrl+C (SIGINT to the process group), group SIGTERM and top-process SIGTERM all stop `make worker` cleanly in about 1 s, so there is no defect. Operate the worker through its top process or process group | Operations note |

## 2. CP1 — decision drafting (no product code)

| Deliverable | Location |
|---|---|
| Decision matrix (exact choices awaiting approval) | `decision-matrix.md` |
| Proposed ADRs | `adr/ADR-0001` (canonical store and scale), `ADR-0003` (identity matching), `ADR-0008` (revisions), `ADR-0015` (IDs), `ADR-0016` (tenancy), `ADR-0017` (taxonomy), `ADR-0018` (trust and evidence) |
| Register | DEC-050, DEC-056, DEC-058, DEC-070: Open → **Proposed**; DEC-021, DEC-025, DEC-031, DEC-034, DEC-037 stay Proposed with ADR links (register v0.6) |
| RTM | `requirements-registry.csv` and the matrix regenerated (68 requirements no longer list DEC-050/056/058/070 as Open; R0 177 → 124). R1/R2 mean "no Open decision", not approval |
| Baselines | Unchanged. The INV-02 deviation is recorded only after approval |

CP2 starts only after the owner approves the decisions.

### 2.1 Owner review and revision 2 (2026-10-25)

- **Owner review (written, in the conversation, 25 Oct 2026):** overall direction approved; CP0 accepted as complete. Approved: D1, D2, D3, D5, D9, D10, D13, D14, D16, D18 (subject to consistency with the authoritative specifications). Approved with clarification: D4, D11, D12. Amend: D6, D7, D8, D15, D17. Instruction: keep unapproved decisions Proposed; no CP2, graph tables, migrations or role changes until the revised decisions are approved.
- **Revision 2:** ADR-0017 (catalog, matrix, coverage, gaps, `READS_FROM`/`WRITES_TO`, `CONTAINS` vs `MEMBER_OF`), ADR-0003 (ARM original and normalized keys), ADR-0008 (revision lifecycle and example), ADR-0001 (schema alignment, ingestion role and privilege matrix), ADR-0018 (alignment); ADR-0015/0016 status notes only. `decision-matrix.md` revision 2 with the baseline-consistency review (C-01…C-12) and the confirmation table.
- **Register:** v0.7 annotations only; **no status changes** (totals unchanged). The approved rows are not moved to Confirmed individually: G1 confirms them together, after the consistency review in `decision-matrix.md` §3.
- **Not done:** no role, credential, grant, table, migration or product code. Baselines unchanged.

### 2.2 Owner review of revision 2 and revision 3 (2026-10-25)

- **Owner review (written, in the conversation, 25 Oct 2026):** revision 2 (PR #15, `d23dfeb`) directionally accepted; `core.system` and `core.component` approved; `CONTAINS`/`MEMBER_OF` kept; D17's ingestion roles acceptable in principle with an explicit DEC-044 amendment to be prepared; final provider-agnostic review requested (Azure, AWS, Google Cloud, Alibaba Cloud, OCI, Huawei Cloud, Tencent Cloud, IBM Cloud, private clouds, on-premises, custom technologies); no connectors, CP2, tables, migrations or role changes.
- **Revision 3:** new ADR-0019 (categories, eight `infra.*` types, providers as reference data, hierarchies, cross-provider rules, scenarios S1–S6, onboarding); ADR-0017 (38 types, rules by category, G-T9 and G-T10 closed); ADR-0003 (provider-qualified namespace registry); ADR-0016 and ADR-0018 (provider-neutral wording); ADR-0001 (reference tables, columns, PostgreSQL 15 assessment); `proposals/dec-044-amendment.md`; decision matrix revision 3 (D1–D19).
- **Register:** v0.8 annotations only; no status changes.
- **Not done:** no role, credential, grant, table, migration, connector or product code. Baselines unchanged.

### 2.3 Final compatibility gate, revision 4 (2026-10-25)

- **Owner review (written, in the conversation, 25 Oct 2026):** D1–D19 direction acceptable, including the provider-neutral categories, the eight `infra.*` types, provider-qualified identity and the DEC-044 amendment; a focused compatibility check requested (environments, unknown provider resources, relationship semantics), no redesign.
- **Result:** 17 checks PASS, 2 GAP (A1 environment kinds, A5 DR standby), each closed in ADR-0017 §2.5 without new types, relationships or tables (`decision-matrix.md` §9).
- **Not done:** no role, credential, grant, table, migration, connector or product code. Baselines unchanged. Register unchanged.

### 2.4 Change attribution check, revision 5 (2026-10-25)

- **Owner request (written, in the conversation, 25 Oct 2026):** verify that every change set can be attributed (initiator kind, namespaced actor ID, channel, action and affected IDs, server time and revision, reason, initiator vs approver, immutability), with no spoofing, service identities for connectors, stable IDs across renames, later maker-checker, and organization scope.
- **Result:** gap in `change_set` (untyped `actor`, writer-supplied `created_at`) fixed in ADR-0008 §10 and ADR-0001 (columns, `actor_namespace` reference data, one trigger); everything else maps to the existing model (`decision-matrix.md` §10).
- **Not done:** no login, RBAC, maker-checker, user management, audit UI, connector, role, migration or product code. Register and baselines unchanged.

### 2.5 Gate G1: CP1 final approval (2026-10-25)

- **Owner approval (written, in the conversation, 25 Oct 2026):** D1–D19 formally approved, including the provider-neutral canonical graph, environment modelling, evidence and trust model, immutable revisions, change-attribution amendments (PR #18) and the DEC-044 amendment to six roles. Authorized: CP1 governance finalization only.
- **Recorded:**
  - register v0.9: DEC-021, DEC-025, DEC-031, DEC-037, DEC-050, DEC-056, DEC-058, DEC-070 → Confirmed (A2.1); DEC-044 amended (design only); DEC-004 linked to ADR-0019; DEC-022 and DEC-034 stay Proposed;
  - ADR-0001, 0003, 0008, 0015, 0016, 0017, 0018, 0019 → Accepted;
  - `baseline-deviations.md` v0.2: TD-DEV-008 (BRD INV-02 vocabulary) and TD-DEV-009 (tech §3.1/§3.3 vocabulary and types); baselines not edited;
  - RTM regenerated from the register: **no readiness change** (the Open set is unchanged); header note updated.
- **Owner guidance for CP2/CP3 (recorded, not implemented):** keep actor namespace/kind integrity with PostgreSQL 15-compatible enforcement; derive attribution from trusted execution context, not payloads; keep database constraints to structural integrity and security; handle flexible architecture rules through domain validation and advisory findings; preserve imperfect source observations without corrupting canonical facts.
- **Not done:** no CP2 work, migration, role, credential, infrastructure change or product code.

## 3. CP2 — Canonical graph contracts and golden fixture

**Authorization (owner, written, in the conversation, 25 Oct 2026):** CP2 only, on the Accepted ADRs and Confirmed decisions at atlas-specs `4ffe1a9`; atlas-specs only; no tables, roles, credentials, migrations, APIs, connectors or UI; ATLAS-001 tags and `contract-v0.1.0` untouched.

### 3.1 Artifacts

| Artifact | Version | Content |
|---|---|---|
| `contracts/taxonomy/atlas-taxonomy.v1.json` | taxonomy **1.0.0** | 38 entity types (12 logical, 16 Azure, 2 Kubernetes, 8 `infra.*`), 15 categories, 11 providers, 18 relationship types (14 active, 4 reserved), provider scope rules, seed native-type mappings, 16 identity namespaces, 3 actor namespaces, enumerations |
| `contracts/schemas/canonical/*.v1.json` | 16 schemas, JSON Schema **2020-12**, `$id` `urn:atlas:schema:canonical:<name>:v1` | common, organization, entity, entity-version, relationship, relationship-version, external-identity, evidence, fact-assertion, actor, change-set, graph-snapshot, import-batch, taxonomy, taxonomy-overlay, fixture-manifest |
| `contracts/examples/canonical/` | — | 50 examples (23 valid, 27 invalid) for 15 schemas |
| `contracts/canonical-validation-rules.md` | rules v1 | 16 HARD rules + 10 taxonomy self-checks, 18 DOMAIN, 11 ADVISORY; enforcement points; interpretations I-1…I-5 |
| `acceptance/test-data/canonical-golden-v1/` | fixture **1.0.0** | 252 entities, 617 relationships, 2 organizations, 9 change sets; 255 entity versions, 622 relationship versions, 186 identities, 28 evidence, 880 assertions, 4 snapshots; import batch and report; expected as-of and findings; synthetic overlay `1.1.0-test.1` |
| `tools/canonical_model.py`, `canonical_rules.py`, `check_canonical.py`, `generate_golden.py`, `tests/test_canonical.py` | — | Reference model, rules, validator (`make canonical`), deterministic generator (`make golden`), 59 tests |
| `spec.md`, `plan.md`, `tasks.md`, `acceptance.md` | 0.1 Proposed | CP3–CP5 requirements, sequence, tasks, criteria; gate **G3-R** (owner-run role bootstrap); open items U-1…U-7 |

### 3.2 Fixture coverage

- **By provider (organization `default`, head):** logical 110, Azure 88, AWS 14, Google Cloud 8, on-premises 8, Alibaba Cloud 5, OCI 5, private cloud 2, other 2.
- **By environment:** PROD 71, UAT 18, SIT 7, DEV 6, DR 2, UAT-2 2, PERF-LAB 1, shared 8, unknown 16.
- **By category:** runtime workload 37, scope 24, container namespace 12, data store 12, API endpoint 8, container cluster 7, compute host 6, messaging channel 6, generic 4, and others (full list in `manifest.json`).
- **Relationship flags:** cross-environment 5 (each evidenced), cross-provider 7, shared endpoint 66.
- **Second organization:** 10 entities and 8 relationships, reusing names, `APP-0101`, the Azure tenant GUID and an AWS account key: no collision.
- **Revisions R1–R8** cover creation, modification, ownership change, retirement, revert, provider-specific re-typing, taxonomy-aware migration, service and system attribution, a no-op replay, and historical reconstruction. Mapping: `acceptance/test-data/README.md`.

### 3.3 Results (local and fresh clone)

| Check | Result |
|---|---|
| Canonical schemas against the 2020-12 metaschema | 16 / 16 valid |
| Examples | 50 checked: every valid accepted, every invalid rejected |
| Taxonomy self-checks T-01…T-10 | 0 findings |
| Golden fixture | HARD 0, DOMAIN 0, ADVISORY 44 (A-01 8, A-02 5, A-04 4, A-05 8, A-06 2, A-07 3, A-09 1, A-11 11, A-12 2), equal to `expected-findings.json` |
| Import | Planned against r1 = exactly r2's facts (14 entities, 8 relationships, 14 containments); 1 rejected and reported (`READS_FROM` an `infra.resource`, D-04); replay at r2 and at head: no change |
| Snapshots and as-of | 4 snapshot hashes and 9 expected as-of results reproduced; r3 and r5 hashes are equal (revert) |
| Determinism | Regenerated fixture byte-identical |
| Negative tests | 22 fixture mutations, each detected by its rule (H-01, H-03, H-05…H-10, H-14, D-03, D-04 ×3, D-05, D-08, D-10, D-12…D-14, D-16); plus actor kind (H-11), snapshot and manifest tampering (H-15), a changed batch (not a no-op), name-only matching (D-18), 4 anti-spoofing payload cases, normalization (12 cases), taxonomy membership cycle (T-09), overlay base mismatch |
| `make check` | All gates passed; `tools` 129 tests (70 existing + 59 new) |

### 3.4 Observations for the owner (no architecture changed)

- **U-1:** `CONTAINS` and `DEPLOYED_AS` don't accept `contract` evidence (ADR-0017 §4.1). The generator's self-check caught this for OpenAPI operations and Google Cloud IaC; the fixture uses documentation evidence for those facts.
- **U-2:** ADR-0019 §3 requires `native_type` on every physical entity, while ADR-0017 §2.2 exempts `azure.tenant`. CP2 follows the explicit exemption; the proposed minimum correction is one line in ADR-0019 §3.
- **U-3…U-7:** see `spec.md` §7.

## 4. Gate G2 — CP2 acceptance and decision closure

**Owner decision (written, in the conversation, 25 Oct 2026):**

- CP2 deliverables accepted, subject to focused clarifications and evidence completion;
- decisions U-1, U-2 and U-3, and confirmations U-4…U-7 (`spec.md` §7);
- minimum documentation, taxonomy, validation-test and evidence updates only;
- no backend, frontend, roles, migrations, credentials or infrastructure; CP3 not started.

### 4.1 CP2 CI evidence (PR #20)

| Item | Value |
|---|---|
| PR | atlas-specs #20, merged 2026-10-25T06:04:56Z with a merge commit |
| PR head | `5e77e2c835f3daeb9b6b4966b7402e0944e05db7`: run [40167767951](https://github.com/Kibana21/atlas-specs/actions/runs/40167767951). `docs-lint`, `contract`, `tools`, `tokens`, `registry`, `breaking` all **success** |
| Merge commit | `440b52ea49cbe9a14f0792f642ddc6fbbc7e7088`: `main` run [40167837795](https://github.com/Kibana21/atlas-specs/actions/runs/40167837795). All six jobs **success** |
| `tools` job, both runs | Steps `make tools` and `make canonical` success. Log: `129 passed`; `canonical: 50 schema examples checked; HARD 0, DOMAIN 0, ADVISORY 44`; `fixture regenerates byte-identically` |

### 4.2 Changes for the decisions

| Decision | Change |
|---|---|
| U-1 | Taxonomy **1.1.0** (MINOR): `contract` allowed for `CONTAINS` and `DEPLOYED_AS`. ADR-0017 §4.1 amended with the observed, declared and documented distinction. Fixture 1.1.0 evidences Google Cloud containment by IaC and API operations by OpenAPI, all `documented` |
| U-2 | Exemption retained. ADR-0017 §2.1 and §2.2 and ADR-0019 §3 now state it. **Correction to the CP2 report:** it said ADR-0017 §2.2 explicitly exempted the tenant. In fact the exemption was explicit only in the taxonomy artifact and the validator, and both ADRs used the general wording. The correction therefore covers both ADRs |
| U-3 | `contracts/trust-function.md` (trust function v1, Proposed for CP3), a truth table of 30 cases, and the reference `trust_v1`. Validator: D-12 now requires equality with the function at every revision; new D-19 (verification support) and D-20 (selected values) |
| U-4…U-7 | I-1 accepted; rejected import items stay in the import report; limitations recorded (`spec.md` §7.1); 617 relationships accepted |

Fixture corrections found by the trust function (both follow Accepted ADR-0018):

- the conflicted VM no longer stores one source's location (I-6);
- the MQ broker's containment from the 2024 document is `stale`.

Identified for the owner, not applied:

- **C-1:** ADR-0018 §1 lists IaC state as `provider_configuration`;
- **C-2:** claim-aware `discovered`;
- **I-6:** a conflicted required attribute is left absent.

### 4.3 Results (local, then from a fresh clone of the branch)

| Check | Result |
|---|---|
| Golden fixture 1.1.0 | HARD 0, DOMAIN 0, ADVISORY 45 (A-12 3, others unchanged), equal to `expected-findings.json`; 252 entities, 617 relationships; byte-identical regeneration |
| Trust function | 30 / 30 truth-table cases; every stored trust state equals the function at every revision |
| Negative tests | 28 fixture mutations (6 new: stale recorded as documented, declared recorded as observed, logical entity from provider configuration only → D-12; verification on declared evidence only, verification by a service → D-19; a conflicting value stored → D-20) |
| `make tools` | 169 passed (129 + 40 new) |

## 5. Gate G2 closure (2026-10-25)

**Owner decision (written, in the conversation, 25 Oct 2026):**

- G2 closure approved, subject to recording three decisions:
  1. IaC is contract (declared) evidence;
  2. provider configuration never establishes logical or business facts on its own;
  3. conflicting required values stay unresolved, with no winner chosen;
- CP3 authorized up to the owner-controlled gate G3-R.

### 5.1 PR #21 CI evidence

| Item | Value |
|---|---|
| PR | atlas-specs #21, merged with a merge commit at `2b546892e12da927482a1442df6171400fbeb37f` |
| PR head | `6ee5895603d8aa7d279f273618328e9e0321f955`: run [40173779787](https://github.com/Kibana21/atlas-specs/actions/runs/40173779787). All six required checks **success** |
| Merge commit | `main` run [40173850480](https://github.com/Kibana21/atlas-specs/actions/runs/40173850480). All six **success**. `tools` log: `169 passed`; `canonical: 50 schema examples checked; HARD 0, DOMAIN 0, ADVISORY 45`; `fixture regenerates byte-identically` |

### 5.2 Decisions recorded

| Decision | Change |
|---|---|
| 1 (C-1) | ADR-0018 §1: IaC templates, plans and state files are `contract`. Subtype and source metadata are preserved in `method`, `source_ref` and `artifact_ref`. IaC never proves live deployment or supports verifying a physical fact |
| 2 (C-2) | ADR-0018 §2: `discovered` is claim-specific. TF-A excludes provider configuration from logical entities and from relationships between logical entities. This closes a gap found while recording: `MEMBER_OF` accepts provider configuration in the taxonomy, so a logical membership backed only by a tag would otherwise have been `discovered` |
| 3 (I-6) | ADR-0018 conflict procedure: an unresolved required field is absent from the stored attributes, both assertions are kept and the fact is `conflicted`. D-01 accepts an unresolved field and rejects a missing one |

The trust function and truth table are approved for CP3: 36 cases, of which 6 (TC-31…TC-36) are new for decisions 1 and 2. No other Accepted ADR changed. The fixture is unchanged: no fixture fact relied on the closed gap.

### 5.3 Results

| Check | Result |
|---|---|
| `make tools` | 176 passed (169 + 6 truth-table cases + 1 mutation: an unresolved field without a conflict → D-01) |
| Canonical | HARD 0, DOMAIN 0, ADVISORY 45; byte-identical regeneration |

## 6. CP3 — Canonical store (in progress; stopped at gate G3-R)

**Authorization (owner, written, in the conversation, 25 Oct 2026):** CP3 after G2 closure, as far as the owner-controlled role gate G3-R permits. Prepare the six-role (additive) setup script with verification and rollback; do not run it, and create no role, password or credential. No frontend, graph read API, authentication, RBAC, connectors or CP4/CP5.

G2 closure: PR #22, merge `2d1d319f1dba37f08b1138fb88550decb84828a4`. PR head `cfc9c89` run [40174455030](https://github.com/Kibana21/atlas-specs/actions/runs/40174455030); `main` run [40174524706](https://github.com/Kibana21/atlas-specs/actions/runs/40174524706). All six checks **success**.

### 6.1 G3-R deliverables (this specs PR; A2-T01)

| File | Content |
|---|---|
| `proposals/postgres-ingest-roles.sql` | Additive setup with guards. Server major 15; exactly the four ATLAS-001 roles, unchanged; databases owned by their migrators; PUBLIC closed; schema `atlas` in both; two non-empty, different passwords from psql variables. Creates `atlas_ingest` and `atlas_test_ingest` with CONNECTION LIMIT 2, session limits, `CONNECT` on its own database, `USAGE` on `atlas` and `search_path`. No table privilege |
| `proposals/postgres-ingest-roles-verify.sql` | Read-only checks: six roles, no special attributes, limits 3/10/2, no memberships, session limits, `CONNECT` own database only, no `TEMP`/`CREATE`, schema privileges, `search_path`, and no table privilege before `0002` (`-v after_0002=1` afterwards) |
| `proposals/postgres-ingest-roles-rollback.sql` | Revokes table, schema and database privileges, resets `search_path`, drops only the two roles, and checks that exactly the four ATLAS-001 roles remain |
| `proposals/g3r-runbook.md` | Exact owner steps, local settings, Claude's read-only follow-up, rollback |

**Not executed.** No role, password or credential exists on the shared server. The local PostgreSQL 15.12 and Redis were not changed.

### 6.2 Backend implementation (atlas-backend draft PR #9; not mergeable before G3-R)

| Area | Files |
|---|---|
| Migration `0002_canonical_graph` | 25 tables in schema `atlas`: 11 taxonomy reference tables (incl. `taxonomy_release`, `relationship_evidence_kind`), organizations and the revision counter, change sets, entity/relationship identity and version tables, identities, aliases, evidence, assertions, snapshots, reconciliation shells. 62 composite or simple FKs, 67 `CHECK`s, 11 unique constraints, 15 indexes (9 partial, incl. one `NULLS NOT DISTINCT`). The two approved triggers. DEC-044 grants to the ingestion role. Taxonomy 1.1.0 seed (836 rows). Default organization. No extension. Fails without the ingestion role |
| `atlas.domain.canonical` | Packaged taxonomy 1.1.0 (byte-identical to the pinned artifact) and seed; approved normalizers; trust function v1; HARD/DOMAIN/ADVISORY rules with revision scoping |
| `atlas.persistence.canonical` | `OrgScope` repository; publishing procedure (ADR-0008 §3); in-database integrity SQL; row mapping |
| Settings, doctor, CI | `ATLAS_INGEST_DATABASE_URL`/`ATLAS_DB_INGEST_ROLE` (optional, guarded; the API never reads them); doctor ingest-role check; drift-checked CI copies of the three G3-R scripts; CI bootstrap, verification and a rollback drill |

### 6.3 Results (draft PR #9, head `7c9d96dbca701a4daf19930eb257ae19a2372fea`, run [40177297989](https://github.com/Kibana21/atlas-backend/actions/runs/40177297989))

| Check | Result |
|---|---|
| `static`, `unit`, `security`, `images` | **success**. Unit: 287 passed, coverage 90% (gate 85%). The `images` job ran the ingestion bootstrap and migration `0002` inside the built image |
| `integration` (isolated `postgres:15`, scram) | **success**. 111 passed. Bootstrap copies equal the pinned G3-R scripts; setup, then verification "OK"; `0002 (head)`; then downgrade of both databases and the rollback script; exactly the four ATLAS-001 roles remain |
| `contract` | **failure, expected**: `LOCK_NOT_ON_MAIN`. `specs.lock` pins this PR's unmerged specs commit; re-pinned after merge |
| Trust function | 36/36 truth-table cases (pinned-specs suite); every golden stored trust state reproduced |
| Golden fixture in memory | HARD 0, DOMAIN 0, ADVISORY equal to `expected-findings.json`; every as-of hash; all 29 atlas-specs mutations detected |
| Golden fixture in PostgreSQL (AC-CP3-05) | All rows accepted; integrity SQL clean at every revision; rows read back equal the fixture (server-set `created_at`/`db_role` aside); every as-of hash reproduced |
| Privileges and triggers (AC-CP3-02/03/04) | Runtime role denied INSERT/UPDATE/DELETE/TRUNCATE on all 25 tables. Ingestion role: matrix exactly; second `revision_to` change rejected; other columns, DELETE, TRUNCATE, DDL and TEMP denied; no cross-environment `CONNECT`. Server-set change-set time and role |
| Publishing (AC-CP3-06/08) | One change set per publish, replay no-op (no revision consumed). 11 rejection cases with their rule IDs; attribution and revert refusal; the runtime role cannot publish; other organizations not found |

### 6.4 Deviations and interpretations (no approved architecture changed)

| # | Item | Why |
|---|---|---|
| CP3-D1 | Backend `make specs` validates `specs.lock` in release mode only for release builds (`RELEASE=1`) | `contracts/compatibility.md` §2 allows any `main` commit for development and CI; plan DP-2 pins a non-release commit. Release mode still requires the `contract-v*` tag |
| CP3-D2 | Golden rows are loaded as the migration role in a rolled-back transaction, with organization keys prefixed `golden-` | Organizations are created by migrations only (the ingestion role has `SELECT` there), and migration `0002` already created `default` |
| CP3-D3 | Additional reference tables `taxonomy_release` and `relationship_evidence_kind`; `fact_assertion` carries typed fact columns | They make the taxonomy version, the assertion's fact and its allowed evidence kind (ADR-0001/0018 "database check on `fact_assertion`") foreign keys instead of triggers |
| CP3-D4 | Not database constraints: "physical types have provider and native type" (only `native_type ⇒ provider`); `external_identity.namespace` FK; the `lower(display_name)` index | The first needs the type's kind and the tenant exemption (D-02 covers it); `source.*` namespaces are a pattern; name search is BL-111 |
| CP3-D5 | A removal (tombstone) version takes the trust label of its `record_state` evidence | Not defined by trust-1, which covers present facts; it matches the fixture |
| CP3-D6 | The publishing procedure re-evaluates only the facts it touches; time-driven trust changes wait for a recompute change set | `contracts/trust-function.md` (storage and recomputation) |
| CP3-D7 | Each publish loads the organization's current state; reverts are refused | Correctness first; measured in CP4 (benchmark). Revert is FR-10 (CP4) |
| CP3-D8 | The migration engine sets `search_path=pg_catalog` at connect | All objects are schema-qualified; it makes `alembic check` compare schema `atlas` as a named schema |

### 6.5 Owner action required (G3-R)

Follow `proposals/g3r-runbook.md` at the merged commit. Run the setup script, then the verification script, as the local superuser with two new passwords. Then add the two settings lines to `.env` and `.env.test`. Afterwards Claude:

1. verifies read-only (`make doctor`);
2. runs the backend local gates from a fresh clone (`make check contract security integration` on `atlas_test`);
3. merges PR #9.

Migration `0002` on `atlas_db` needs a separate approval.

### 6.6 G3-R read-only preflight and CP4 follow-ups (owner request, 25 Oct 2026)

Read-only review of the scripts at `91755a4` and of the local server, using catalog `SELECT`s in sessions with `default_transaction_read_only=on`. Nothing was executed or changed.

- Every setup guard holds:
  - server 15.12;
  - exactly the four ATLAS-001 roles, with no special attributes, limits 3/10 and no memberships;
  - `atlas_db`/`atlas_test` owned by their migrators;
  - PUBLIC has no CONNECT or TEMP on either database;
  - schema `atlas` owned by the migrator in both databases, each at `0001_baseline`.
- Server logging: `log_statement=none`, no `pg_stat_statements`, `log_min_error_statement=error`. A `CREATE ROLE … PASSWORD` statement is therefore logged only if that statement fails, and the guards make that unlikely.
- Runbook correction: `make doctor` does not check database ownership; the script guards do.
- Follow-ups recorded as A2-T25…T27 and AC-CP4-05/06: benchmark the full-organization load during publication; implement and verify reverts; validate trust recomputation when evidence changes.

## 7. CP3 — Local single-user database model (owner decision, 25 Oct 2026)

**Owner decision (written, in the conversation):** local development and integration testing use one existing PostgreSQL account, `atlas_db_user`, for migrations, application access, ingestion and tests (`atlas_db` development, `atlas_test` tests). The ingestion roles are not created, and G3-R is not required locally. The six-role model is kept as a possible production hardening option. Organization isolation and domain validation must not weaken.

Before this decision, the owner's G3-R confirmation could not be verified: read-only checks showed neither ingestion role on the only local server (Homebrew PostgreSQL 15 on 5432) and no ingestion keys in the env files. Nothing was run.

### 7.1 Impact assessment

| Area | Effect |
|---|---|
| CP2 contracts (taxonomy, schemas, golden fixture, trust function) | None |
| Organization isolation, identity and version integrity, atomic publication, domain validation, trust | Unchanged: application (`OrgScope`, validator, publishing procedure) plus constraints |
| Keys, FKs, `CHECK`s, set-once trigger, server-set change-set fields | Still enforced (they bind superusers) |
| Lost locally | Privilege separation. `atlas_db_user` is a **superuser**, so the database no longer stops the API writing facts, or anyone deleting, truncating or disabling triggers. `db_role` is always `atlas_db_user`. Test runs are kept off `atlas_db` by the settings guard only. **Unsuitable for production** |
| Migration `0002` | Compatible. Grants are made only when the ingestion role differs from the migrating account. Canonical tables are owned by `atlas_db_user`; `alembic_version` keeps its ATLAS-001 owner |

Recorded in: DEC-044 (register v0.10), ADR-0001 §Privileges (local single-user model), ADR-0008 §10 note, TD-DEV-010, `spec.md` DP-1 and §6, AC-CP3-09, runbook and amendment status.

### 7.2 Backend changes (draft PR #9)

- **Setting `ATLAS_DB_ROLE_MODEL`:** `separated` (default) or `single`.
  - `single` is refused outside the `local`/`test` environments.
  - It requires one user in every URL and `db_app_role` equal to that user.
  - It derives the ingestion URL and role from that user.
- **Migration `0002`:** grants only to a distinct ingestion role.
- **Doctor:** reports the single-user model and warns about a superuser account.
- **Tests:** tests that need separated roles carry `role_separation` and are skipped with the stated reason in single-user mode.
- **CI:** keeps the six-role run and the rollback drill, and adds a single-user leg with a CI-only superuser `atlas_db_user`.
- **Local env files:** switched to `atlas_db_user`, with no password (local `trust`). The previous lines are commented in place.

### 7.3 Results

| Run | Result |
|---|---|
| Local, fresh clone of `79fa25c`, `atlas_test` only | `make check` 296 passed (coverage 91%); `make contract` 103 passed; `make security` no known vulnerabilities, 32 passed; `make integration` **46 passed, 65 skipped** (53 role-separation, 12 CI-only password checks), exit 0 |
| `make doctor` | PASS, except two WARNs: the single-user model with a SUPERUSER account, and loopback `trust` (DEC-084) |
| Local database state | `atlas_test` at `0002_canonical_graph` (26 tables, only the default organization; tests cleaned up). **`atlas_db` still at `0001_baseline`**. Roles: the four ATLAS-001 roles and `atlas_db_user`, all unchanged |
| CI, head `79fa25c`, run [40183920480](https://github.com/Kibana21/atlas-backend/actions/runs/40183920480) | All six checks **success**. Separated roles: 111 passed, then the rollback drill. Single-user leg: 46 passed, 65 skipped, identical to local |

## 8. Gate G3 — CP3 accepted (owner, 25 Oct 2026)

**Owner decision (written, in the conversation):** G3 approved, on the evidence below and the documented local single-user deviation. The approved local configuration uses `atlas_db_user` for database access; the separated-role model remains the default for non-local environments. CP4 authorized against `atlas_test` and isolated CI databases only.

| Item | Value |
|---|---|
| Gate | **CP3 G3: PASS** |
| Backend | atlas-backend PR #9, merged at `4689bf5005290db4f499bebeca645e893087b1e4` |
| CI | PR head `45f0a93` run [40184412078](https://github.com/Kibana21/atlas-backend/actions/runs/40184412078); `main` run [40184561319](https://github.com/Kibana21/atlas-backend/actions/runs/40184561319). All six checks success |
| Six-role CI integration (separated model) | 111 passed, then the G3-R rollback drill |
| Local integration (`atlas_test`, single-user model) | 46 passed, 65 skipped (53 role-separation, 12 CI-only password checks); the CI single-user leg is identical |
| Accepted exception | TD-DEV-010: local single-user model with the superuser `atlas_db_user` |
| Development database | `atlas_db` remains at `0001_baseline`; migration `0002` there needs separate owner approval |

## 9. CP4 — Loader, reconstruction, reverts, trust recomputation, benchmark (awaiting G4)

**Authorization (owner, 25 Oct 2026):** CP4 against `atlas_test` and isolated CI databases only. Separately, a read-only preflight for migrating `atlas_db` (§9.5); not executed.

Backend PR #10, merged at `b44c1e230992e34b8f6f696707bc5c225baa2caf`. PR head `cb9b52d` run [40186564491](https://github.com/Kibana21/atlas-backend/actions/runs/40186564491): all six required checks and the `benchmark` job **success**. `main` run [40186882964](https://github.com/Kibana21/atlas-backend/actions/runs/40186882964): required checks **success**.

### 9.1 What was built (A2-T16…T20, A2-T25…T27)

- **Recorded-history replay (fixture loader):** as the configured `fixture-loader` service. Recorded reverts replay as reverts.
- **Import application:** through the import planner (port of the reference), with the import report and evidence reuse.
- **`revert`:** a new attributed change set; refused with D-14 when a later revision changed the same facts.
- **`recompute_trust`:** a `migration`-kind change set by the system actor `trust-recompute`.
- **Snapshots:** create and verify.
- **CLI:** `atlas.tools.canonical`, using the ingestion connection only.
- **CI `benchmark` job:** disposable database only; not a required check.
- **Defects fixed in the publishing procedure:** a per-fact assertion index (it was quadratic), and relationship claims resolved from the plan's current versions (a latent bug: a relationship touched together with its endpoint skipped trust re-evaluation).

### 9.2 Results

| Check | Result |
|---|---|
| Unit (CI) | 304 passed, coverage 86% |
| `make contract` (CI) | 106 passed, 78 of them canonical pinned-specs tests: the CP3 suite plus the planner reproducing r2 with its rejection report, recorded drafts for all 8 revisions, and the revert draft of r4 equalling the recorded r5 |
| Integration, separated roles (CI) | 119 passed |
| Integration, single-user (CI leg and local `atlas_test`) | 54 passed, 65 skipped; identical |
| Replay of the golden history (AC-CP4-01/04) | Every revision's graph hash equals `expected-as-of.json` and the integrity checks are clean, at every revision and afterwards. Every stored row (entities, versions, relationships, identities, evidence, assertions) equals the fixture's. All change sets carry the configured `fixture-loader` and the server-set role; r5 is a revert of r4. All four snapshot hashes match; a label cannot move |
| Idempotency (AC-CP4-02) | Re-publishing r8's input and re-importing the r2 batch at head write nothing |
| Import (AC-CP4-01) | Against r1, revision 2 creates exactly the fixture's entities and reports the expected rejection. A replay is a no-op. Attributed to `import-worker` on the `import` channel |
| Reverts (AC-CP4-03) | Reverting r8 gives revision 9, whose hash equals r7's while r8's history still reconstructs. Reverting r4 is refused with D-14 and writes nothing |
| Trust recomputation (AC-CP4-06) | With a test-only 30-day policy, only the 3 document-only entities and 1 relationship turn `stale`. An expired verification turns its fact `stale`. A steward assertion makes a fact `curated`. A repeat recompute writes nothing |
| Failure and concurrency | A failure after writing rolls everything back and the revision number is reused (gap-free). A second publisher waits on the organization's counter and gets the next revision. Composite keys reject a cross-organization reference |

### 9.3 Benchmark (A2-T20, A2-T25; disposable CI PostgreSQL 15, single-user account)

| Entities / relationships / assertions | Initial load | One-entity change | No-op | State load | Graph hash |
|---|---|---|---|---|---|
| 1,006 / 4,000 / 5,006 | 1.9 s | 0.83 s | 0.30 s | 0.15 s | 0.21 s |
| 5,026 / 20,000 / 25,026 | 5.7 s | 2.2 s | 1.7 s | 0.84 s | 1.2 s |
| 10,051 / 40,000 / 50,051 | 11.3 s | 4.8 s | 3.6 s | 1.9 s | 2.8 s |

A small change costs time linear in the organization's size, because the procedure loads and validates its whole current state (CP3-D7). That is acceptable for fixture loads and batch imports at pilot size. It is **not** acceptable for interactive edits, and extrapolates to roughly a minute per change at Scale A. Optimization (load only the touched facts and their neighbours) is required before any release with interactive writes or Scale A data.

### 9.4 Interpretations made in CP4 (for owner confirmation at G4)

| # | Point | Choice |
|---|---|---|
| CP4-D1 | Evaluation time when replaying recorded history | The recorded change set's time (`evaluated_at`, never later than the server time). Otherwise the fixture's freshness policy and verification expiry would make its stored trust states depend on the date the test runs. Live publications keep the transaction time |
| CP4-D2 | Change-set kind for trust recomputation | `migration` on the `migration` channel by a system actor; no new kind was added |
| CP4-D3 | D-19 for a verification carried into a new version | Checked when recorded or changed only (contract text clarified) |
| CP4-D4 | Replayed history attribution | Every replayed revision is attributed to the loader's configured identity; recorded human authorship stays as evidence (ADR-0008 §10) |

### 9.5 Development database migration preflight (read-only; not executed)

| Item | Finding |
|---|---|
| Identity | `atlas_db` on the local PostgreSQL 15.12, port 5432; owner `atlas_migrator`; 7.7 MB; collation C |
| Revision and contents | `0001_baseline`. Only `atlas.alembic_version` (and its key) exists; no functions in `atlas`; extension `plpgsql` only. Schema `atlas` owned by `atlas_migrator` |
| Connection that would run it | Backend `.env` (local, single-user model): `atlas_db_user` on `atlas_db`, through `make migrate` |
| What `0002` does there | 25 tables and 15 indexes in schema `atlas` only, 2 functions and 6 triggers, 836 taxonomy seed rows, the default organization and its counter. No grants (the ingestion role is the migrating account), no extension, no role or database change, no other schema. Redis is not used |
| Ownership note | The new tables will be owned by `atlas_db_user`, not `atlas_migrator`, and the migrator's default privileges will not apply. Moving `atlas_db` to the separated model later needs an ownership and grant step |
| Other sessions | One idle pgAdmin session on `atlas_db`; the migration does not need to lock existing objects other than `alembic_version` |
| Backup | Before migrating: `pg_dump -h localhost -U atlas_db_user -d atlas_db -Fc -f <outside the repositories>/atlas_db-pre-0002.dump` (pg_dump 15.12 available) |
| Restoration | Preferred: `alembic downgrade 0001_baseline` with the same settings, which drops exactly what `0002` created (empty databases only). Fallback: `pg_restore -h localhost -U atlas_db_user -d atlas_db --clean --if-exists <dump>`, which touches `atlas_db` only |
