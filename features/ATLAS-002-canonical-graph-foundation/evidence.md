# ATLAS-002 — Evidence Record

**Status:** Gates **G0–G4 passed** (G0 2026-10-24; G1, G2, G3 and G4 2026-10-25). `atlas_db` is at `0002_canonical_graph` (owner approval, §11). **CP5 delivered (§12), awaiting the owner's G5 sign-off.** ATLAS-002 is **not** Accepted until the owner signs.

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

## 9. CP4 — Loader, reconstruction, reverts, trust recomputation, benchmark (G4 passed: §10)

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

### 9.4 Interpretations made in CP4 (confirmed by the owner at G4, §10.1)

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

## 10. Gate G4 — CP4 accepted (owner, 25 Oct 2026)

### 10.1 Owner decision (written, in the conversation, 25 Oct 2026)

The owner reviewed the CP4 report (§9) and decided as follows.

- **Approved:**
  - CP4-D1: historical replay evaluates trust at the recorded change set's time; live publishing evaluates it at transaction time;
  - CP4-D3: D-19 checks a verification when it is recorded or changed; a later trust recomputation may turn expired verification evidence `stale`.
- **Accepted:**
  - CP4-D2: trust recomputation reuses the existing `migration` change-set kind, with an explicit system actor and reason;
  - CP4-D4: fixture replay is attributed to the loader, and the original authors are kept as evidence.
- **Condition for G4 PASS:** close the reclassification-revert gap (A2-T28, AC-CP4-07):
  - test reverting an entity reclassification, including its historical taxonomy version;
  - fix any validation issue that blocks an otherwise valid revert;
  - confirm that the original revision still reconstructs and that the revert is a new attributed revision;
  - confirm that a conflicting revert writes nothing.
- **Performance:** the benchmark is recorded as a release limitation, and a future performance gate is defined (PG-1). There is no publishing-engine redesign in G4.
- **Separately:** controlled migration `0002` on the local `atlas_db` was authorized under ten preconditions (§11).

### 10.2 Reclassification revert: defect, fix, regression tests

**Reproduced before any change** (new integration tests on `atlas_test`, 4 failed):

- reverting the steward reclassification r6 (`infra.data_store` → `azure.sql_database`) or the taxonomy migration r7 (`infra.resource` → `infra.data_store` under `1.2.0-test.1`) was refused by D-10, which allowed a non-automatic re-type only in a `steward_edit` or `migration` change set;
- a restored version was re-stamped with the base taxonomy (`1.1.0`) instead of the version it recorded (`1.2.0-test.1`), and D-14 did not compare the taxonomy version;
- while reviewing the conflict case, a related gap appeared: a relationship was validated only at its own version's revision. A re-type, or a revert that re-types, could therefore strand a relationship that the new type does not allow, which ADR-0008 §5.4 forbids. Both the reference validator and the backend had this gap.

**Fix (contract first; narrowly scoped):**

- **Rules** (`contracts/canonical-validation-rules.md`; these clarify Accepted ADR text and add no new architecture):
  - D-10: a revert may re-type an entity only back to the version that was valid before the reverted revision (ADR-0008 §7);
  - D-14: the restored version must keep its recorded taxonomy version (ADR-0008 §6, ADR-0017 §1);
  - D-04: relationships are re-checked when an endpoint is re-typed (ADR-0008 §5.4).
- **Reference validator:** fixture unchanged (HARD 0, DOMAIN 0, ADVISORY 45; byte-identical). New tests: the positive case (a valid revert of r7) plus 3 mutations. The positive case and 2 of the mutations fail against the old validator. The third (a revert to another type) was already rejected, and now guards the narrow exception.
- **Backend `revert`:** a restored entity or relationship version keeps its recorded `taxonomy_version` and is validated against it. Rules match the reference; the same three ported cases fail against the old backend rules.
- **Identity rules unchanged:** the entity ID never changes. Bindings that the reverted revision closed are re-opened as new rows; those it opened are closed; history is never rewritten.

**Regression tests (integration, PostgreSQL 15; local `atlas_test` and CI):**

| Test | Result |
|---|---|
| Revert of r6 (after replaying r1–r6) | Revision 7, kind `revert`, `reverts_revision` 6, human steward actor (`oidc`), server-set `db_role`, reason kept. Graph hash = r5's; r6 still reconstructs with its own hash. The entity's r5 version is restored exactly (type `infra.data_store`, taxonomy `1.1.0`, re-parenting undone) and its r5 identity namespaces are bound again. Integrity is clean at every revision |
| Revert of r7 (after replaying r1–r7) | Revision 8; graph hash = r6's; `infra.resource` on `1.1.0` restored; the r7 version (`infra.data_store`, `1.2.0-test.1`) stays in history, closed at 8 |
| Historical taxonomy version | At head, a steward rename of the overlay-typed entity (r9), then a revert of r9: revision 10 restores the `1.2.0-test.1` version exactly, and the hash equals r8's |
| Conflicting reverts write nothing | Revert of r7 at head: refused with **D-04** (r8's `READS_FROM` would point at an `infra.resource`). Revert of r6 after a later rename: refused with **D-14** (fact changed again). Before and after each refusal, the revision and every stored row are identical |
| Existing CP4 reverts | Unchanged: r8 reverts to r7's hash; r4 is refused with D-14 |

### 10.3 Final commits and CI

| Repository | PR | Merge commit | PR head run | `main` run |
|---|---|---|---|---|
| atlas-specs | [#28](https://github.com/Kibana21/atlas-specs/pull/28): rules D-04/D-10/D-14, reference validator and tests, AC-CP4-07, A2-T28, limitation, PG-1 | `3d4002f11f675a4f7520e22abb1b1c4b10e29be1` | [40189008741](https://github.com/Kibana21/atlas-specs/actions/runs/40189008741): 6/6 required **success** | [40189106561](https://github.com/Kibana21/atlas-specs/actions/runs/40189106561): 6/6 **success** |
| atlas-backend | [#11](https://github.com/Kibana21/atlas-backend/pull/11): revert keeps the recorded taxonomy version; rules; tests; `specs.lock` → `3d4002f` | `e9737587c4f7e5c25eda62257aba43ea2d9cb7ed` | [40189533934](https://github.com/Kibana21/atlas-backend/actions/runs/40189533934): 6/6 required **success**, `benchmark` success | [40190186641](https://github.com/Kibana21/atlas-backend/actions/runs/40190186641): 6/6 **success** |

| Check | Result |
|---|---|
| atlas-specs `make check` (fresh clone) | All gates passed; `tools` 180 passed; canonical HARD 0, DOMAIN 0, ADVISORY 45; fixture byte-identical |
| Backend unit (CI and fresh clone) | 304 passed, coverage 86.33% |
| Backend `make contract` | 110 passed (82 pinned-canonical) |
| Backend `make security` | No known vulnerabilities; 32 passed |
| Integration, separated roles (CI) | **123 passed** (CP4: 119) |
| Integration, single-user (CI leg and local `atlas_test`, fresh clone) | **58 passed, 65 skipped** (CP4: 54); identical |

### 10.4 Benchmark (G4 head; disposable CI PostgreSQL 15, single-user account)

PR head run 40189533934, job `benchmark`. CP4 values (§9.3) are in brackets.

| Entities / relationships / assertions | Initial load | One-entity change | No-op | State load | Graph hash |
|---|---|---|---|---|---|
| 1,006 / 4,000 / 5,006 | 2.2 s [1.9] | 0.90 s [0.83] | 0.33 s [0.30] | 0.17 s [0.15] | 0.25 s [0.21] |
| 5,026 / 20,000 / 25,026 | 7.0 s [5.7] | 2.6 s [2.2] | 2.0 s [1.7] | 1.1 s [0.84] | 1.5 s [1.2] |
| 10,051 / 40,000 / 50,051 | 13.5 s [11.3] | 5.6 s [4.8] | 4.2 s [3.6] | 2.2 s [1.9] | 3.4 s [2.8] |

Single runs on shared CI runners, so the run-to-run variance is not known. Part of the increase is plausibly the new endpoint re-type check (D-04, ADR-0008 §5.4), which scans the entity versions on each publish, and part is runner variance. Costs stay linear in organization size.

### 10.5 Release limitations (owner instruction at G4)

- **Publication performance:** each publish loads and validates the organization's whole current state (CP3-D7). This is approved for fixture loads and batch imports, **not** as the implementation for interactive editing. At 10k/40k, a one-entity change takes about 5–6 s and a no-op about 4 s. It extrapolates to roughly a minute or more per change at Scale A. Recorded in `spec.md` §7.1.
- **Future gate PG-1** (`acceptance.md`) must pass before any release with interactive writes or Scale A data. It covers single-entity updates, no-op publishing, concurrent writers, increasing graph sizes and historical reconstruction, with thresholds set by the owner beforehand.
- No publishing-engine redesign was done in G4.

### 10.6 Gate G4

| Criterion | Result |
|---|---|
| Idempotent load with an equal graph hash (AC-CP4-01/02) | ✔ §9.2, unchanged at the G4 head |
| Integrity green at every revision (AC-CP4-04) | ✔ |
| Reverts, including reclassification and conflicts (AC-CP4-03, AC-CP4-07) | ✔ §10.2 |
| Trust recomputation (AC-CP4-06) | ✔ §9.2 |
| Benchmark recorded, with the state load (AC-CP4-05) | ✔ §9.3, §10.4; limitation §10.5 |
| Required checks green on PR and `main` | ✔ specs 6/6, backend 6/6 |
| ATLAS-001 tags unchanged | ✔ `contract-v0.1.0` → `bfe4a09`, backend `v0.1.0` → `585f3f5`, frontend `v0.1.0` → `b9f235e` |

**Verdict: Gate G4 — PASS.** The owner set this condition: G4 passes once the reclassification-revert regression is resolved, which §10.2–§10.3 show. **CP5 is not started**; it needs the owner's authorization.

## 11. Controlled migration `0002` on the local `atlas_db` (owner authorization, 25 Oct 2026)

Run from a clean clone of backend `main` at `b44c1e2`. The migration file there is byte-identical to the G4 head. The account is the approved local single-user `atlas_db_user`. No credential appears in any command or log.

| # | Precondition | Result |
|---|---|---|
| 1 | Target `localhost:5432/atlas_db` | ✔ settings (`ATLAS_ENV=local`, single-user model): runtime and migration URLs both `localhost:5432/atlas_db`. The connection reports `atlas_db`, port 5432, PostgreSQL 15.12 |
| 2 | Current revision `0001_baseline` | ✔ `alembic_version` = `0001_baseline`; schema `atlas` held one table. Re-checked immediately before running |
| 3 | Expected head and reviewed file | ✔ single head `0002_canonical_graph` (down revision `0001_baseline`). `alembic/versions/0002_canonical_graph.py` SHA-256 `13d071926c2bdfd47f42c5f143d76d7bdd5d582e81c6053fe581e2613c82370b`, identical at G3 acceptance `4689bf5`, at `b44c1e2` and at the G4 head. No migration, schema or taxonomy input changed since G3 |
| 4 | Timestamped `pg_dump` outside all repositories | ✔ `<backup-dir>/atlas_db-pre-0002-20261025T113718Z.dump`, where `<backup-dir>` is a private local directory outside all repositories; the full path was reported to the owner (custom format, pg_dump 15.12, 3,250 bytes, mode 600 in a 700 directory; SHA-256 `31934538bbcc8a47ab2bfc295048a425ebc4609fa8562e1b4fc9b80d3ac22542`). Taken in a read-only session |
| 5 | Backup readable; recovery documented | ✔ `pg_restore --list` reads 8 TOC entries: schema `atlas` (owner `atlas_migrator`) and its ACL, the `public` ACL, `alembic_version` with its ACL, data and key, and the migrator's default privileges. The data reads back as `0001_baseline`. Recovery: below |
| 6 | Cannot target `atlas_test` or another database | ✔ The runner reads only the settings' migration URL (no `-x` or URL override). The settings guard rejects `atlas_test` outside the test environment, and the pre-check requires every URL to be `atlas_db` on `localhost:5432`. Explicit target `alembic upgrade 0002_canonical_graph` |
| 7 | Only migration `0002`, approved local configuration | ✔ `Running upgrade 0001_baseline -> 0002_canonical_graph` (one transaction; transactional DDL), exit 0. The only other session was an idle pgAdmin session holding no locks |
| 8 | Schema, seed, revision, integrity | ✔ `alembic current` = `0002_canonical_graph (head)`. `alembic check`: no new upgrade operations (no drift). 26 tables, 2 functions, 6 triggers, 52 indexes (constraint indexes included), extensions `plpgsql` only. Taxonomy seed: 836 rows in 11 tables, equal to the packaged 1.1.0. Organization `default` at revision 0; no canonical facts; integrity checks clean. Schema digest identical to `atlas_test`'s; row counts identical; content differs only in the default organization's generated ID |
| 9 | `atlas_test` unchanged | ✔ Fingerprint before and after identical: `0002_canonical_graph`, 26 tables, row counts, schema and content digests |
| 10 | Report | This section |

**Ownership note (from the preflight, §9.5):** the 25 new tables are owned by `atlas_db_user`; `alembic_version` and schema `atlas` stay with `atlas_migrator`. Moving `atlas_db` to the separated-role model later needs an ownership and grant step.

**Recovery procedure (documented, not executed; each step needs the owner's approval):**

1. **Preferred, while `atlas_db` holds no canonical facts:** from the same backend commit and `.env`, run `alembic downgrade 0001_baseline`. It drops exactly what `0002` created.
2. **Fallback, from the backup:** first remove what `0002` created. `pg_restore --clean` alone cannot drop schema `atlas` while it holds the new tables. This is destructive, needs separate approval, and touches `atlas_db` only. Then run `pg_restore -h localhost -p 5432 -U atlas_db_user -d atlas_db --exit-on-error <dump>`. Finally verify `alembic_version` = `0001_baseline`, the owner `atlas_migrator` and the ACLs.

No rollback was needed or run. PostgreSQL authentication, roles, other databases and Redis were not touched.

## 12. CP5 — Evidence, traceability, release proposal (awaiting G5)

### 12.1 Authorization and owner decisions (written, in the conversation, 25 Oct 2026)

- **G4 confirmed:** the owner accepted the G4 evidence and confirmed G4 PASS.
- **CP5 authorized** within the approved scope (A2-T21…T23). No release tags, migrations, frontend, database-configuration or Redis changes, and no CP6.
- **Decision 1 (release):** Option A, no ATLAS-002 release tags. ATLAS-002 is accepted against the verified `main` commits. `info.version` is not bumped, and DEC-039 and `compatibility.md` are not amended. The conflict is documented (`release-proposal.md`).
- **Decision 2 (G5 terms):** on the same basis as ATLAS-001, subject to documented deviations, limitations and follow-ups. PG-1 stays binding before interactive editing or a Scale A release (`follow-ups.md`).
- **Decision 3 (traceability):** evidence first. The backlog, RTM and registry are not rewritten. Partly covered items are stated exactly (§12.5).
- **Additional approvals:**
  - a documentation-only backend `CLAUDE.md` update;
  - PG-1 keeps the latest baseline, and needs repeated, controlled benchmark runs before the thresholds are chosen. No threshold is invented in CP5.

### 12.2 Final verification of the `main` commits

| Repository | `main` commit | `main` CI run | Fresh-clone local gates (25 Oct 2026) |
|---|---|---|---|
| atlas-specs | `9ea2b7ed88fafdf483fc495a9fa67be89c1792f1` | [40191059640](https://github.com/Kibana21/atlas-specs/actions/runs/40191059640): `docs-lint`, `contract`, `tools`, `tokens`, `registry`, `breaking` success | `make check` all gates; `tools` 180 passed; canonical HARD 0, DOMAIN 0, ADVISORY 45; fixture regenerates byte-identically |
| atlas-backend | `e9737587c4f7e5c25eda62257aba43ea2d9cb7ed` (`specs.lock` → `3d4002f`) | [40190186641](https://github.com/Kibana21/atlas-backend/actions/runs/40190186641): `static`, `unit`, `contract`, `security`, `integration`, `images` success (`benchmark` success) | `make check` 304 passed, coverage 86.33%; `make contract` 110 passed; `make security` no known vulnerabilities, 32 passed; `make integration` (`atlas_test`) 58 passed, 65 skipped |
| atlas-frontend | `8ed5deb895dced78f98bff13cedd14c28a70f4ac` (unchanged since CP0) | [40095359958](https://github.com/Kibana21/atlas-frontend/actions/runs/40095359958): all seven success | Not rerun: no ATLAS-002 change after CP0 (§1.2) |

- The integration suite's migration round trip (AC-CP3-01) recreates `atlas_test`'s default organization, so its generated ID changed. Schema, row counts and every other row are unchanged.
- `atlas_db` was not touched in CP5.
- The CP5 documentation merges (atlas-specs, and atlas-backend [PR #12](https://github.com/Kibana21/atlas-backend/pull/12): `CLAUDE.md` only, merged at `0d37b6e0709a4f3603dd4b7373ac330ae7974b69`; PR head run [40193893740](https://github.com/Kibana21/atlas-backend/actions/runs/40193893740) and `main` run [40194599204](https://github.com/Kibana21/atlas-backend/actions/runs/40194599204), 6/6 success; its fresh-clone gates match §12.2) change no code, contract, rule or fixture.

**How to read §12.3** (runs at the commits above):

- **S** = specs `main` run 40191059640, job `tools` (`tools/tests/test_canonical.py`, `make canonical`).
- **B-u / B-c / B-i** = backend `main` run 40190186641, jobs `unit` / `contract` / `integration`.
  - The `integration` job runs the separated-role leg (123 passed) and the single-user leg (58 passed, 65 skipped). Tests marked `role_separation` run only in the separated leg.
- **B-b** = the non-required `benchmark` job.
- **L** = the fresh-clone local run.

### 12.3 Acceptance-criteria traceability (AC-CP5-01)

| AC | Verifying tests (repository · test) | Runs | Evidence |
|---|---|---|---|
| AC-CP2-01 | specs · `test_taxonomy_is_self_consistent` (T-01…T-10 clean; 38 types; 8 `infra.*`), `test_taxonomy_example_is_the_artifact`; backend · `test_packaged_taxonomy_is_the_pinned_artifact` | S, B-c, L | §3.3, §4.1 |
| AC-CP2-02 | specs · `make canonical` (16 schemas against the 2020-12 metaschema; 50 examples), `test_committed_contracts_and_fixture_pass` | S, L | §3.3 |
| AC-CP2-03 | specs · `test_committed_contracts_and_fixture_pass`; backend · `test_golden_fixture_has_no_blocking_finding`, `test_golden_fixture_advisories_match_the_expected_report` | S, B-c, L | §4.3, §5.3 |
| AC-CP2-04 | specs · `test_fixture_generation_is_deterministic`; `make canonical` byte-identical regeneration | S, L | §3.3 |
| AC-CP2-05 | specs · `test_import_replay_is_a_noop_and_rejections_are_reported`, `test_changed_batch_is_not_a_noop`; backend · `test_import_plan_reproduces_revision_2_and_its_report` | S, B-c, L | §3.3, §9.2 |
| AC-CP2-06 | specs · `test_negative_mutation_is_detected` (32 mutations), `test_actor_kind_mismatch_is_hard`, `test_snapshot_tamper_is_detected`, `test_manifest_tamper_is_detected`; backend · `test_atlas_specs_negative_mutation_is_detected` (ported, 32) | S, B-c, L | §4.3, §10.2 |
| AC-CP2-07 | specs · `test_import_payload_cannot_carry_attribution` | S, L | §3.3 |
| AC-CP2-08 | specs · `test_contract_evidence_for_containment_and_deployment` | S, L | §4.2 |
| AC-CP2-09 | specs · `test_trust_function_v1_truth_table` (36 cases), `test_trust_cases_target_the_artifact`; backend · `test_trust_function_truth_table`, `test_the_truth_table_has_36_cases`, `test_golden_trust_states_are_reproduced_by_the_backend_function` | S, B-c, L | §5.3, §6.3 |
| AC-CP3-01 | backend · `test_upgrade_downgrade_upgrade_round_trip`, `test_every_table_is_owned_by_the_migrator_and_no_extension_is_created`; `alembic check` on `atlas_db` (§11) | B-i, L | §6.3, §11 |
| AC-CP3-02 | backend · `test_runtime_role_cannot_write_canonical_tables` (25 tables), `test_the_runtime_role_cannot_publish`, `test_the_api_never_uses_the_ingestion_role` | B-i (separated leg) | §6.3 |
| AC-CP3-03 | backend · `test_ingestion_role_inserts_and_closes_once`, `test_ingestion_role_cannot_delete_truncate_rewrite_or_run_ddl`, `test_set_once_binds_the_owner_too`, `test_ingestion_roles_cannot_connect_to_the_other_environment`, `test_ingestion_grants_follow_the_matrix` | B-i (separated leg; set-once also single-user), L | §6.3 |
| AC-CP3-04 | backend · `test_change_set_time_and_role_are_set_by_the_server`, `test_change_set_structure_is_enforced` | B-i, L | §6.3 |
| AC-CP3-05 | backend · `test_golden_rows_load_and_pass_the_sql_integrity_checks`, `test_integrity_sql_detects_a_dangling_relationship` | B-i, L | §6.3 |
| AC-CP3-06 | backend · `test_invalid_change_sets_are_rejected_with_their_rule`, `test_attribution_must_fit_the_channel`, `test_cross_check_the_dependent_relationship_evidence`; unit `test_each_rule_fires` | B-i, B-u, L | §6.3 |
| AC-CP3-07 | backend · `test_reference_tables_equal_the_packaged_taxonomy`, unit `test_seed_rows_cover_every_reference_table`; `atlas_db` seed check (836 rows, §11) | B-i, B-u, L | §6.3, §11 |
| AC-CP3-08 | backend · `test_trust_function_truth_table`, `test_golden_trust_states_are_reproduced_by_the_backend_function`; unit `test_trust_rules`, `test_verification_needs_a_human_and_supporting_evidence`, `test_conflict_keeps_the_prior_value_and_drafts_are_proposed`, `test_d19_checks_a_verification_when_recorded_not_when_carried_forward` | B-c, B-u, L | §6.3, §10.1 |
| AC-CP3-09 | backend · the single-user integration leg: 58 passed, 65 skipped (53 `role_separation`, 12 CI-only password checks), identical to local; the separated leg in the same job | B-i, L | §7.3, §10.3 |
| AC-CP4-01 | backend · `test_golden_history_replays_revision_by_revision` (every as-of hash), `test_import_batch_creates_exactly_revision_2_and_replays_as_a_no_op`, `test_golden_fixture_as_of_hashes`, `test_recorded_drafts_cover_every_revision` | B-i, B-c, L | §9.2 |
| AC-CP4-02 | backend · `test_golden_history_replays_revision_by_revision` (re-publishing r8 and re-importing r2 write nothing), `test_publish_writes_one_change_set_and_a_replay_writes_nothing`; unit `test_an_unchanged_batch_plans_nothing` | B-i, B-u, L | §9.2 |
| AC-CP4-03 | backend · `test_revert_draft_of_revision_4_equals_the_recorded_revert`, `test_reverts_are_new_attributed_revisions_and_unsafe_ones_are_refused`; unit `test_revert_restores_the_prior_state_as_a_new_change_set`, `test_revert_of_a_creation_removes_and_refuses_unknown_or_conflicting_revisions` | B-c, B-i, B-u, L | §9.2 |
| AC-CP4-04 | backend · `test_golden_history_replays_revision_by_revision` (`revision_findings` at every revision, `history_findings` after), `test_golden_rows_load_and_pass_the_sql_integrity_checks` | B-i, L | §9.2 |
| AC-CP4-05 | backend · `scripts/benchmark_canonical.py` in the CI `benchmark` job (disposable database; state load reported). Results recorded with no thresholds | B-b; runs 40186564491 (CP4), 40189533934 (G4) | §9.3, §10.4 |
| AC-CP4-06 | backend · `test_trust_is_recomputed_when_evidence_ages_or_changes`, `test_an_expired_verification_turns_the_fact_stale` | B-i, L | §9.2 |
| AC-CP4-07 | backend · `test_reverting_a_steward_reclassification_restores_type_parent_and_identities`, `test_reverting_a_taxonomy_migration_restores_the_historical_taxonomy_version`, `test_a_reverted_version_keeps_the_taxonomy_version_it_was_validated_against`, `test_conflicting_reclassification_reverts_are_refused_and_write_nothing`, `test_a_reclassification_revert_restores_the_earlier_type_and_taxonomy_version`; specs · the same reference case and mutations | B-i, B-c, S, L | §10.2 |
| AC-CP5-01 | This section, `release-proposal.md`, `follow-ups.md`; the owner's sign-off (§12.8) | — | §12 |

Supporting tests for the above (unit, run in B-u):

- isolation: `test_other_organizations_are_not_found`, `test_composite_keys_keep_organizations_apart`;
- atomicity and ordering: `test_a_failure_after_writing_rolls_everything_back`, `test_concurrent_publishers_are_serialized_and_revisions_stay_gap_free`;
- normalizers: `test_arm_1_normalizes`, `test_golden_identities_normalize_as_stored`.

### 12.4 Requirement coverage (`spec.md` §3, §4)

| Requirement | Covered by | Note |
|---|---|---|
| A002-FR-01 Migration `0002` | AC-CP3-01, AC-CP3-05; `atlas_db` §11 | — |
| A002-FR-02 Two triggers | AC-CP3-03 (set-once), AC-CP3-04 (server fields) | — |
| A002-FR-03 Grants | AC-CP3-02/03 (separated model in CI) | Locally superseded by TD-DEV-010 (F-02) |
| A002-FR-04 Taxonomy seed | AC-CP3-07 | — |
| A002-FR-05 Normalizers | unit normalizer tests; `test_golden_identities_normalize_as_stored` | Non-Azure namespaces `validation_only` (F-05) |
| A002-FR-06 `OrgScope` | strict mypy in `make check`; `test_other_organizations_are_not_found`, `test_composite_keys_keep_organizations_apart` | — |
| A002-FR-07 Domain validator | AC-CP2-06, AC-CP3-06; G4 clarifications to D-04, D-10 and D-14 (§10.2) | — |
| A002-FR-08 Publishing procedure | AC-CP3-06/08, AC-CP4-02; failure and concurrency tests | Full-organization state load: release limitation (F-01) |
| A002-FR-09 Fixture loader CLI | AC-CP4-01 (through `history.replay`, `apply_import`) | **The CLI wrapper itself has no automated test (F-09)** |
| A002-FR-10 Revert | AC-CP4-03, AC-CP4-07 | — |
| A002-FR-11 As-of and graph hash | AC-CP4-01, AC-CP4-04 | — |
| A002-FR-12 Pilot-size benchmark | AC-CP4-05 (CI only, never the shared server) | Thresholds deferred to PG-1 (F-01) |
| A002-FR-13 Trust function v1 | AC-CP2-09, AC-CP3-08, AC-CP4-06 | — |
| A002-NFR-01 PostgreSQL 15, no extension, no server setting change | `test_every_table_is_owned_by_the_migrator_and_no_extension_is_created`; `atlas_db` extensions `plpgsql` only (§11) | — |
| A002-NFR-02 Synthetic data; Scale A never on the shared server | `acceptance/test-data/README.md`; the benchmark runs in CI only | — |
| A002-NFR-03 Quality gates | backend coverage 86.33% (gate 85%), ruff, strict mypy; specs `make check` | Persistence modules run in the integration suites, which run with `--no-cov`, so their unit coverage figures understate the testing |
| A002-NFR-04 No Redis for the canonical store | No Redis reference in `atlas.domain.canonical`, `atlas.persistence.canonical` or `atlas.tools.canonical` (code search, 25 Oct 2026) | By construction; no dedicated test |

### 12.5 Partly covered backlog items (owner decision 3; `prioritized-backlog.md`, RTM, registry not changed)

| Backlog item (authoritative text: `phase0/prioritized-backlog.md`) | What ATLAS-002 implemented | What remains outside ATLAS-002 |
|---|---|---|
| **BL-015** JSON Schemas v0.1: entity, relationship, provenance/evidence, projection request/response, view state and deep-link encoding, layout, draft command union, error envelope, capability set | Canonical schemas (16, `contracts/schemas/canonical/*.v1.json`) for organization, entity and entity version, relationship and relationship version, external identity, evidence, fact assertion, actor, change set, graph snapshot, import batch, taxonomy and overlay, fixture manifest; 50 valid and invalid examples | Projection request and response, view state and deep-link encoding, layout, draft command union, capability set. The error envelope was ATLAS-001 (OpenAPI) |
| **BL-016** Golden fixture: MVP vertical slice (Digital Channels → APIM → New Business → Policy Administration → Claims), 250 entities / 700 relationships, with ACL personas, trust-state mix, conflicts, cycles; spec for a 10k/100k generator | Deterministic synthetic fixture: 252 entities, 617 relationships (owner U-7), two organizations, 8 revisions, all trust states including one conflicted fact, cross-provider and cross-environment facts | **ACL personas** (no authorization model yet). The **MVP-slice naming** is not reproduced, and pilot sources are undecided (DEC-068). 700 relationships not reached (617 accepted). **Cycles**: the fixture has none. There are no directed cycles among its current relationships (checked 25 Oct 2026), and containment cycles are exercised only by mutation tests. The **10k/100k generator spec**: only a synthetic 10k/40k benchmark generator exists (`scripts/benchmark_canonical.py`) |
| **BL-101** Canonical graph schema, taxonomy validation, aliases, provenance, migrations (TE01); requirements INV-01–06, MOD-01, MOD-03/04, DEP-01, UX-NFR-014 (registry rows mapped to BL-101) | Migration `0002` (schema, revisions, identities, evidence and assertions, snapshots); taxonomy 1.1.0 validation (HARD and DOMAIN); trust function; publishing, revert, import planner | **Aliases:** an `entity_alias` table shell only, no alias workflow. Reconciliation (`reconciliation_case`, `match_candidate`): shells only. Every **read path and API** (`GET /entities/…`; RTM "entity write API MISSING"), authorization, and the UX-facing parts of these requirements |
| **BL-102** Synthetic graph generator + golden fixture loader | Golden fixture loader (recorded-history replay, import application) through the publishing procedure; synthetic 10k/40k benchmark generator | A general synthetic generator for E2E and performance at 100k scale (BL-125, DEC-054). An automated test of the loader CLI (F-09) |

The RTM (`phase0/requirement-traceability-matrix.md`) and `requirements-registry.csv` still list these requirements against BL-101 and the other items with their readiness. ATLAS-002 does not claim any of them is fully satisfied.

### 12.6 Deviations and interpretations register (for G5)

| ID | Kind | Summary | Status |
|---|---|---|---|
| TD-DEV-008, TD-DEV-009 | Baseline deviations | Relationship vocabulary differs from BRD INV-02 and Technical §3.1/§3.3 | Approved at G1 (`baseline-deviations.md`) |
| TD-DEV-010 | Baseline deviation | Local single-user superuser model | Approved (owner, 25 Oct 2026); F-02 |
| CP3-D1 | Interpretation | `specs.lock` release mode only for release builds | Recorded §6.4; G3 |
| CP3-D2 | Interpretation | Golden rows loaded as the migration role, rolled back, with organization keys prefixed | Recorded §6.4; G3 |
| CP3-D3 | Design detail | Additional reference tables `taxonomy_release`, `relationship_evidence_kind`; typed fact columns on assertions | Recorded §6.4; G3 |
| CP3-D4 | Design detail | Some rules enforced in the domain validator, not as database constraints | Recorded §6.4; G3 |
| CP3-D5 | Interpretation | A tombstone takes the trust label of its removal evidence | Recorded §6.4; G3 |
| CP3-D6 | Interpretation | Only touched facts are re-evaluated; time-driven changes need a recompute change set | Recorded §6.4; G3 |
| CP3-D7 | Limitation | Full-organization state load per publish | Release limitation; PG-1 (F-01) |
| CP3-D8 | Implementation detail | Migration engine sets `search_path=pg_catalog` | Recorded §6.4; G3 |
| CP4-D1…D4 | Interpretations | Replay evaluation time; recompute kind; D-19 timing; replay attribution | **Confirmed by the owner at G4** (§10.1) |
| G4 rule clarifications | Contract clarification | D-04 re-check on re-type, D-10 revert exception, D-14 taxonomy version | Merged with G4 (atlas-specs #28); implements ADR-0008 §5.4, §6, §7 |
| U-1…U-7, I-1, I-6 | Owner decisions at G2 | Taxonomy 1.1.0, trust function, limitations | Approved at G2 (§4, §5) |

### 12.7 Release (A2-T22)

`release-proposal.md`: **no ATLAS-002 release tags** (owner decision 1). The governance conflict between `compatibility.md` §3 and §8 is recorded and deferred to the first consumer release (F-07). ATLAS-001 tags unchanged: `contract-v0.1.0` → `bfe4a09`, backend `v0.1.0` → `585f3f5`, frontend `v0.1.0` → `b9f235e`.

### 12.8 G5 owner-acceptance package (A2-T23) — **awaiting the owner's sign-off**

| Item | Where |
|---|---|
| Acceptance criteria with tests, runs and SHAs | §12.3 |
| Requirement coverage and partly covered backlog items | §12.4, §12.5 |
| Deviations and interpretations | §12.6 |
| Release decision | `release-proposal.md`, §12.7 |
| Follow-ups, limitations, unresolved decisions (none completed) | `follow-ups.md` F-01…F-09; **PG-1 binding** |
| Final commits and runs | §12.2 |
| Development database state | §11 (`atlas_db` at `0002_canonical_graph`, verified; backup kept outside the repositories) |

**Proposed acceptance wording (for the owner; not signed):** "ATLAS-002 Canonical Graph Foundation is Accepted against atlas-backend `main` `0d37b6e` (code as verified at `e973758`; `specs.lock` → atlas-specs `3d4002f`) and the atlas-specs `main` commit that merges this CP5 record, subject to the deviations in §12.6 and the follow-ups F-01…F-09. PG-1 is binding before interactive editing or a Scale A release. No release tags."

| Gate | Decision | Date | By |
|---|---|---|---|
| G5 | **Pending.** Not signed; Claude does not sign on the owner's behalf | — | Owner |
