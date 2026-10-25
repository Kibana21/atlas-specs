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
