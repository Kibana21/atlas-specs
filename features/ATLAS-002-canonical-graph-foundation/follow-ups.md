# ATLAS-002 — Follow-ups, limitations and deferred decisions

**Date:** 25 October 2026 · **Context:** prepared for the owner's G5 decision (owner instruction, CP5 decision 2). If accepted, ATLAS-002 is accepted *subject to* these items, as ATLAS-001 was. **None of them is completed by ATLAS-002**, except F-09 (closed before G5, owner condition). Scheduling any of them needs the owner's approval.

| ID | Kind | Summary | Binding on | State |
|---|---|---|---|---|
| F-01 | **Binding gate** | PG-1 performance gate before interactive editing or a Scale A release | Any release or feature with interactive canonical writes, or Scale A data | **Open** |
| F-02 | Accepted exception | TD-DEV-010: local single-user model with the superuser `atlas_db_user` | Every non-local environment (must not use it) | **Open** (local only) |
| F-03 | Future migration step | Database ownership and grant transition to the separated-role model | Any move of `atlas_db` (or a new environment) to separated roles | **Open** |
| F-04 | Deferred integration | DP-4: frontend E2E bootstrap once its backend pin passes migration `0002` | The next frontend `e2e/backend.ref` move past `2987262` | **Open** |
| F-05 | Recorded limitation | Provider-ID formats and non-Azure hierarchies | Cross-source identity matching and hierarchy validation for non-Azure providers | **Open** |
| F-06 | Recorded limitation | No source freshness policy or field precedence: no age-based staleness outside fixtures, no automatic conflict resolution | Connectors, reconciliation | **Open** |
| F-07 | Deferred decision | Release tagging for the canonical store (`release-proposal.md`) | The first consumer release | **Open** |
| F-08 | Unresolved decisions | Decisions still Proposed or Open, with their downstream dependencies (table below) | As listed | **Open** |
| F-09 | Test gap (found in CP5) | The loader CLI `atlas.tools.canonical` had no automated test | Any operational use of the CLI (for example loading `atlas_db`) | **Closed** (25 Oct 2026, `evidence.md` §13) |
| F-10 | Validation defect (found by F-09) | The D-04 re-check of existing relationships after a re-type is skipped when the relationship's taxonomy version is not loaded | Any caller that passes a partial taxonomy set; any second approved taxonomy | **Open** (`evidence.md` §13.4) |

## F-01 — PG-1 performance gate (binding)

**Requirement (owner, G4 and CP5):** PG-1 (`acceptance.md`, "Future performance acceptance gate") must pass before interactive editing or a Scale A release. It covers single-entity updates, no-op publishing, concurrent writers, increasing graph sizes and historical reconstruction.

**Why:** each publish loads and validates the organization's whole current state (CP3-D7). The cost grows linearly with organization size. This is approved for fixture loads and batch imports only (`spec.md` §7.1).

**Baseline: the latest measurement, kept as the PG-1 starting point.** Backend PR #11 head `95f4bc5`, CI run [40189533934](https://github.com/Kibana21/atlas-backend/actions/runs/40189533934), job `benchmark`. Disposable PostgreSQL 15, single-user account, one run each:

| Entities / relationships / assertions | Initial load | One-entity update | No-op | State load | Graph hash |
|---|---|---|---|---|---|
| 1,006 / 4,000 / 5,006 | 2.2 s | 0.90 s | 0.33 s | 0.17 s | 0.25 s |
| 5,026 / 20,000 / 25,026 | 7.0 s | 2.6 s | 2.0 s | 1.1 s | 1.5 s |
| **10,051 / 40,000 / 50,051** | 13.5 s | **5.6 s** | **4.2 s** | 2.2 s | 3.4 s |

The CP4 run (backend `cb9b52d`, run [40186564491](https://github.com/Kibana21/atlas-backend/actions/runs/40186564491)) measured 4.8 s and 3.6 s at 10k/40k. The difference is not explained: it may be runner variance or the D-04 re-check added at G4 (`evidence.md` §10.4).

**Before thresholds are chosen (owner instruction, CP5):**

- run the benchmark repeatedly with a controlled workload and environment (fixed runner or dedicated disposable host, fixed data generator seed, warm-up, several repetitions, spread reported), never on the shared server (A002-FR-12);
- extend the sizes towards Scale A and add the concurrent-writer and historical-reconstruction cases;
- the owner then sets the thresholds. **No threshold is set in ATLAS-002.**

**Depends on:** DEC-054 (Open: performance targets, reference hardware and datasets).

## F-02 — TD-DEV-010: local single-user superuser exception

- Local development and integration tests use one existing account, `atlas_db_user`, a PostgreSQL **superuser**, for every role (`ATLAS_DB_ROLE_MODEL=single`, refused outside `local`/`test`).
- Locally the database still enforces structure: keys, foreign keys, `CHECK`s and the two triggers. It does **not** enforce privilege separation: the API could write facts, and anyone could delete, truncate or disable triggers. `db_role` is always `atlas_db_user`.
- Unsuitable for production. The separated six-role model (DEC-044 as amended, G3-R scripts) is the default for non-local environments, and CI verifies it on every change.
- Related: DEC-084 (Open), local `trust` authentication on the shared server.

## F-03 — Database ownership and grant transition

- On `atlas_db` (migrated 25 Oct 2026) and `atlas_test`, the 25 canonical tables are owned by `atlas_db_user`. Schema `atlas` and `alembic_version` are owned by each database's migrator (`atlas_migrator`, `atlas_test_migrator`). The migrator's default privileges do not apply to the new tables. Verified read-only on 25 Oct 2026.
- Moving a database to the separated-role model needs a reviewed, owner-approved step:
  1. transfer ownership of the canonical tables to the migrator;
  2. run the G3-R setup and verification scripts (`proposals/postgres-ingest-roles*.sql`);
  3. apply the DEC-044 grant matrix;
  4. verify with the privilege tests.
- No such step is designed in detail or authorized. It touches roles and grants on the shared server, so it needs explicit owner authorization (`CLAUDE.md`, shared services).

## F-04 — DP-4: deferred frontend integration

- The frontend pins specs `bfe4a09` (`contract-v0.1.0`) and backend `2987262` (`e2e/backend.ref`). Both predate migration `0002`, and ATLAS-002 changed nothing in the frontend after CP0.
- When the frontend next moves `e2e/backend.ref` past `0002`, its CI `e2e` job must create the database objects `0002` expects. In the separated model that means the ingestion role from the same bootstrap as backend CI (`spec.md` §5 DP-4).
- No canonical graph UI or API is consumed by the frontend. That is later scope (ATLAS-003 or later), not this follow-up.

## F-05 — Provider-ID and hierarchy limitations (`spec.md` §7.1, owner decision U-6)

- **Identity namespaces:**
  - AWS, Google Cloud, Alibaba Cloud and OCI identities are `validation_only`: the format is checked and case is preserved, but there is no normalization rule, so they cannot match across sources;
  - Huawei Cloud, Tencent Cloud and IBM Cloud are `planned`, and rejected;
  - `apim.operation` is `reserved`.
- **Hierarchies:** `provider_scope_rules` for providers other than Azure are `intended_shape`. D-16 checks fixtures against the intended shape only, until each provider is onboarded (ADR-0019 §4).
- Each needs an approved rule (ADR-0003, ADR-0019 onboarding) before its identities match across sources or its hierarchy is confirmed.

## F-06 — Freshness and precedence

- There is no approved per-source freshness policy (DEC-072, Open) and no field precedence (DEC-034, Proposed).
- The trust function therefore never makes a fact stale by age, except under a fixture's synthetic, test-only policy, and never resolves a disagreement automatically: conflicting values stay unresolved, with no winner chosen (owner decision I-6).

## F-07 — Release tagging deferred

See `release-proposal.md`. No ATLAS-002 tags were created. The governance conflict between `compatibility.md` §3 and §8 is recorded, not resolved. It is decided at the first consumer release.

## F-08 — Unresolved decisions and their downstream dependencies

The status is that of `decisions/decision-register.md` on 25 Oct 2026. ATLAS-002 did not change any of these.

| Decision | Status | What it leaves open | Downstream work that depends on it |
|---|---|---|---|
| DEC-022 Traversal engine and graph-DB threshold | Proposed | Recursive CTE vs a graph read projection, decided by benchmark (BL-019) | Graph-reading projections (BL-108), dependency analysis (BL-211); any graph API built on the canonical store |
| DEC-034 Field-level source authority | Proposed | Per-source, per-field precedence | Reconciliation (BL-203); automatic conflict resolution (F-06) |
| DEC-054 Performance targets, reference hardware, datasets | Open | Targets, hardware, the 10k/40k vs 10k/100k pilot size | **PG-1 thresholds (F-01)**; performance harness (BL-125) |
| DEC-057 Discovery publication semantics | Open | Whether observations publish automatically or after approval | Connectors and discovery syncs; approval-based publication (ADR-0008 §9) |
| DEC-066 Representation of unknown relationships | Open | Visual grammar for "coverage unknown" | Canvas and inspector UI over the canonical store |
| DEC-068 Pilot domain, applications and subscriptions | Open | Real (non-sensitive) pilot sources | The full BL-016 MVP slice fixture; first real discovery |
| DEC-072 Sync SLAs and stale/tombstone grace policy | Open | Per-source freshness and tombstone rules | Connectors; age-based staleness in the trust function (F-06) |
| DEC-074 Retention, archival, backup/restore, legal hold | Open | Retention of history, evidence and snapshots; backup policy | History compaction or archiving (ADR-0008 §9); backup practice beyond the ad hoc pre-migration dump |
| DEC-084 Local PostgreSQL authentication (`trust`) | Open | Local `pg_hba` hardening | F-02; local security posture |

## F-09 — Loader CLI without an automated test (found in CP5) — **Closed**

- **Finding (CP5):** the command-line entry point `atlas.tools.canonical` (`atlas-canonical replay | import | revert | recompute-trust | snapshot`, A2-T16, A002-FR-09) had 0% coverage, and no test ran it.
- **Resolution (owner condition for G5, 25 Oct 2026):** backend [PR #13](https://github.com/Kibana21/atlas-backend/pull/13), merged at `dbb6c04`, `main` run [40203519070](https://github.com/Kibana21/atlas-backend/actions/runs/40203519070). 18 integration tests run the real entry point as a subprocess on `atlas_test` (and the disposable CI database), covering every sub-command, invalid arguments, missing configuration, exit codes and the ingestion connection. CLI module coverage 98% (106/106 statements). The tests found a defect, fixed in the CLI (fail closed on unloaded taxonomy versions), whose root cause is F-10.
- Details: `evidence.md` §13.

## F-10 — Validation with a partial taxonomy set (found by F-09) — **Open**

- **Defect:** `_retyped_endpoints` (the D-04 re-check of existing relationships when an endpoint is re-typed, ADR-0008 §5.4) skips a relationship whose recorded taxonomy version is not loaded by the caller. Every other taxonomy lookup either reports D-01 or only skips rows that D-01 already refuses. The SQL integrity suite does not check the taxonomy matrix.
- **Risk:** a caller that loads fewer taxonomy versions than the data uses can commit a re-type that strands a relationship (reproduced on `atlas_test` for the revert service and direct publishing; the import planner uses the same check). Current exposure: the CLI is the only production caller and now refuses; `atlas_db` holds no canonical facts; 1.1.0 is the only approved taxonomy.
- **Proposed resolution (awaiting owner approval):** report D-01 instead of skipping, in the backend and specs validators; clarify D-04 in the rule catalog; add a mutation; convert the `xfail` regression tests. Compatible with the golden fixture and the CP2 contracts (prototype: fixture byte-identical, all suites pass).
- **Binding on:** any new caller of `publish` (API, worker, connector) and the approval of a second taxonomy release, until resolved or accepted by the owner as a deferred limitation.
- Details: `evidence.md` §13.4.
