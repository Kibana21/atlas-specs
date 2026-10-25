# DEC-044 amendment proposal: dedicated ingestion roles (D17)

**Status:** **Proposed. Not approved, not applied.** No role, credential, grant or database change has been made. The SQL below is a design for review; it is turned into a reviewed script only in CP3, after approval, and is run **only by the server owner**.

**Date:** 25 October 2026 · **Decision:** DEC-044 (Confirmed, four roles) · **Related:** ADR-0001 §Privileges, ATLAS-001 FR-28 and FR-30, DEC-043, DEC-084 (Open), E-07 (open)

## 1. Current decision (unchanged until approved)

> DEC-044: dedicated Atlas databases and least-privilege roles on the local server. Runtime, migration and test credentials are separate (**four roles**, runtime read-only by default, per-table write grants).

The four roles: `atlas_migrator`, `atlas_app`, `atlas_test_migrator`, `atlas_test_app`.

## 2. Proposed amended text

> DEC-044 (amended by ATLAS-002 D17): dedicated Atlas databases and least-privilege roles on the local server. Runtime, migration, **ingestion** and test credentials are separate: **six roles**. `*_migrator` owns the schema and runs migrations. `*_app` (the API runtime) is read-only, with no write grant on canonical tables. `*_ingest` is the only role that writes canonical facts: `INSERT` plus `UPDATE` of `revision_to` (and the revision counter), granted per table by the migration that creates it; never `DELETE`, `TRUNCATE`, DDL or temporary tables. The ingestion roles are created by the server owner from a reviewed script; their credentials are created by the owner and never committed.

## 3. Why two new roles are necessary

| Need | Without a new role | With `atlas_ingest` |
|---|---|---|
| The API must not be able to write canonical facts before authorization exists (invariant 4; owner, 25 Oct 2026) | `atlas_app` would need INSERT and UPDATE: any API bug or injection could write facts | `atlas_app` stays read-only at the database level; only the ingestion entry points can write |
| The fixture loader (CP4) and later imports must write in bulk with `COPY` | — | `COPY … FROM STDIN` needs only `INSERT` |
| Writes must be attributable | All sessions look the same | `pg_stat_activity.usename` and logs show which identity wrote |
| A dedicated writer without a login role | `SET ROLE` from `atlas_app` (makes `atlas_app` a writer); `SECURITY DEFINER` functions (rules out `COPY`, moves logic into PL/pgSQL) | Rejected alternatives (ADR-0001 §Role options) |
| Test isolation (ATLAS-001 FR-30) | — | `atlas_test_ingest` mirrors it on `atlas_test`; neither ingestion role can connect to the other database |

## 4. Roles and attributes

| Attribute | `atlas_ingest` | `atlas_test_ingest` |
|---|---|---|
| Login | Yes | Yes |
| `SUPERUSER`, `CREATEDB`, `CREATEROLE`, `REPLICATION`, `BYPASSRLS` | No (defaults) | No (defaults) |
| Member of other roles | None | None |
| `CONNECTION LIMIT` | 2 | 2 |
| `statement_timeout` / `idle_in_transaction_session_timeout` / `lock_timeout` | 120 s / 60 s / 10 s | 120 s / 60 s / 10 s |
| Database | `CONNECT` on `atlas_db` only | `CONNECT` on `atlas_test` only |
| Schema `atlas` | `USAGE` (no `CREATE`) | `USAGE` (no `CREATE`) |
| `search_path` | `atlas` (in `atlas_db`) | `atlas` (in `atlas_test`) |
| Temporary tables | No (`PUBLIC` has no `TEMP` on either database, ATLAS-001) | No |
| Default privileges | None | None |

## 5. Least-privilege grants (made by migration `0002`, not by the bootstrap)

"S" `SELECT`, "I" `INSERT`, "U(c)" `UPDATE` of column c only.

| Tables | `*_app` | `*_ingest` |
|---|---|---|
| `alembic_version` | S | — |
| `organization`, `provider`, `category`, `identity_namespace`, `native_type_mapping`, `actor_namespace`, `entity_type`, `relationship_type`, `relationship_rule`, `attribute_rule` | S | S |
| `org_revision` | S | S, U(`last`) |
| `change_set`, `graph_snapshot`, `evidence`, `entity`, `relationship`, `match_candidate`, `reconciliation_case` | S | S, I |
| `entity_version`, `relationship_version`, `external_identity`, `entity_alias`, `fact_assertion` | S | S, I, U(`revision_to`) |
| Every table | No I, U, D | No D, `TRUNCATE`, `REFERENCES`, `TRIGGER` |

- `*_app` keeps exactly its ATLAS-001 rights (SELECT through the schema's default privileges).
- The set-once trigger (ADR-0008 §2) also rejects a second change of `revision_to`, whatever the role.
- No sequence privileges: IDs are application-generated UUIDv7; revisions come from `org_revision`.

## 6. How this changes the ATLAS-001 baseline

ATLAS-001 is Accepted (v0.1.0). Its documents, tags and released artifacts are **not edited**. ATLAS-002's spec states the new rule and the register records the amendment.

| ATLAS-001 item | Change |
|---|---|
| DEC-044 (four roles) | Six roles (§2) |
| FR-28 "any write privilege is granted per table … to `ATLAS_DB_APP_ROLE`" | For canonical tables the grantee is `ATLAS_DB_INGEST_ROLE`; `ATLAS_DB_APP_ROLE` receives no canonical write grant. Still per table, still inside the creating migration, still reviewed |
| FR-30 least-privilege tests | Extended to the ingestion roles (§9) |
| `postgres-local-setup.sql` (applied by the owner) | **Unchanged.** Its guard aborts if any `atlas_*` role exists, so it is never re-run; the ingestion roles come from a separate, additive script |
| Backend `scripts/db/bootstrap.sql` (CI copy) | Unchanged; a second verbatim copy (`bootstrap-ingest.sql`) runs after it |
| `atlas doctor` | Also reports the ingestion role (presence, connection, no excess privilege) |
| Settings | New `ATLAS_INGEST_DATABASE_URL`, `ATLAS_DB_INGEST_ROLE`; the API never reads them |
| ATLAS-001 v0.1.0 tags, contract `contract-v0.1.0`, pins | Unchanged |

## 7. Local bootstrap (server owner only, after approval)

Prerequisites: the four ATLAS-001 roles exist; `atlas_db` and `atlas_test` exist with schema `atlas`. The owner creates two new passwords and exports them in the shell (never in a file in a repository, never printed).

Design of the CP3 script (`proposals/postgres-ingest-roles.sql`), for review:

```sql
\set ON_ERROR_STOP on
\getenv atlas_ingest_password ATLAS_INGEST_PASSWORD
\getenv atlas_test_ingest_password ATLAS_TEST_INGEST_PASSWORD

-- 0. Guards: abort before any change unless the state is exactly as expected.
--    * server major version is 15
--    * the four ATLAS-001 roles exist, with no superuser/createdb/createrole/replication/bypassrls
--    * neither atlas_ingest nor atlas_test_ingest exists
--    * atlas_db is owned by atlas_migrator and atlas_test by atlas_test_migrator
--    * schema atlas exists in both databases
--    * both password variables are set and non-empty

-- 1. Roles (no special attributes)
BEGIN;
CREATE ROLE atlas_ingest      LOGIN CONNECTION LIMIT 2 PASSWORD :'atlas_ingest_password';
CREATE ROLE atlas_test_ingest LOGIN CONNECTION LIMIT 2 PASSWORD :'atlas_test_ingest_password';
ALTER ROLE atlas_ingest      SET statement_timeout = '120s';
ALTER ROLE atlas_ingest      SET idle_in_transaction_session_timeout = '60s';
ALTER ROLE atlas_ingest      SET lock_timeout = '10s';
ALTER ROLE atlas_test_ingest SET statement_timeout = '120s';
ALTER ROLE atlas_test_ingest SET idle_in_transaction_session_timeout = '60s';
ALTER ROLE atlas_test_ingest SET lock_timeout = '10s';
GRANT CONNECT ON DATABASE atlas_db   TO atlas_ingest;
GRANT CONNECT ON DATABASE atlas_test TO atlas_test_ingest;
COMMIT;

-- 2. Schema usage and search_path, per database
\connect atlas_db
BEGIN;
GRANT USAGE ON SCHEMA atlas TO atlas_ingest;
ALTER ROLE atlas_ingest IN DATABASE atlas_db SET search_path = atlas;
COMMIT;

\connect atlas_test
BEGIN;
GRANT USAGE ON SCHEMA atlas TO atlas_test_ingest;
ALTER ROLE atlas_test_ingest IN DATABASE atlas_test SET search_path = atlas;
COMMIT;
```

It touches no other role, database, extension, server setting or `pg_hba.conf`, and grants no table privilege (migrations do that).

**Verification (read-only, run by Claude afterwards through `atlas doctor`):**

- `pg_roles`: six `atlas_*` login roles, all special attributes false, limits 3/10/2;
- `has_database_privilege('atlas_ingest','atlas_test','CONNECT')` and the reverse are false;
- `has_database_privilege('atlas_ingest','atlas_db','TEMP')` is false;
- `has_schema_privilege('atlas_ingest','atlas','CREATE')` is false;
- before migration `0002`: `atlas_ingest` has no table privilege at all.

Then the owner adds `ATLAS_INGEST_DATABASE_URL` (and the test equivalent) to the git-ignored local `.env`.

## 8. CI bootstrap

| Repository | Change |
|---|---|
| atlas-backend CI (isolated `postgres:15` service) | After `bootstrap.sql`, run `scripts/db/bootstrap-ingest.sql`, a verbatim copy of the approved specs script at the pinned commit, checked by `check_bootstrap.py` like the first. Two more random passwords per job, masked. Integration tests receive the ingest URL and role |
| atlas-backend `images_check.sh` | Same extra step |
| atlas-frontend CI, `e2e` job | When `e2e/backend.ref` moves to a backend commit that has migration `0002`, also run the ingestion bootstrap from the checked-out backend; otherwise `alembic upgrade head` fails (the migration requires the role). No change before that |
| atlas-specs | None (no database) |

## 9. Tests (extend ATLAS-001 FR-30)

- `*_app` cannot INSERT, UPDATE or DELETE any canonical table.
- `*_ingest` can INSERT; can UPDATE only the listed columns; a second change of `revision_to` fails (trigger); cannot DELETE or TRUNCATE; cannot run DDL, create temporary tables or write reference tables.
- Neither ingestion role can connect to the other environment's database.
- No Atlas role is superuser or can create roles or databases, replicate or bypass RLS.
- The API process connects as `*_app` only (asserted).

## 10. Rollback

Rollback only while no canonical data must be kept, or after the owner decides so.

1. Downgrade migration `0002` in that database (revokes its grants and drops its tables; empty databases only, ADR-0008 §7). Alternatively, keep the tables and revoke: `REVOKE ALL ON ALL TABLES IN SCHEMA atlas FROM atlas_ingest;`.
2. Then, as the server owner:

```sql
\connect atlas_db
REVOKE USAGE ON SCHEMA atlas FROM atlas_ingest;
ALTER ROLE atlas_ingest IN DATABASE atlas_db RESET search_path;
\connect atlas_test
REVOKE USAGE ON SCHEMA atlas FROM atlas_test_ingest;
ALTER ROLE atlas_test_ingest IN DATABASE atlas_test RESET search_path;
\connect postgres
REVOKE CONNECT ON DATABASE atlas_db   FROM atlas_ingest;
REVOKE CONNECT ON DATABASE atlas_test FROM atlas_test_ingest;
DROP ROLE atlas_ingest, atlas_test_ingest;
```

`DROP ROLE` succeeds only if the role owns nothing and holds no privilege; the ingestion roles own no objects by design. No other role or database is affected.

## 11. Operational implications

| Topic | Implication |
|---|---|
| Connections | At most 4 more connections on the shared server (2 per environment) |
| Credentials | Two more secrets, created and rotated by the owner (`ALTER ROLE … PASSWORD`); stored only in the git-ignored `.env` locally and as masked per-job values in CI |
| Local authentication | The local server currently uses `trust` for loopback connections (ATLAS-001 finding; DEC-084 Open, E-07 open). Locally, role separation therefore protects against **mistakes**, not against a local user choosing another role name. CI uses password authentication (`scram`), so separation is enforced there. Unchanged by this amendment |
| Other projects' databases | Like the four existing roles, the ingestion roles could connect to other projects' databases on the shared server that still grant `CONNECT` to `PUBLIC` (DEC-084 finding), with only `PUBLIC`'s rights there. Atlas never configures such a connection; a `doctor` check for it is proposed for CP3 |
| Process separation | Only ingestion entry points (CP4 fixture loader CLI; later import and sync workers) are configured with the ingest URL |
| Blast radius of a leaked ingest credential | Can add facts and close versions, cannot delete or rewrite history. Every write is a change set with an actor; a revert change set undoes it (ADR-0008 §7) |
| Monitoring | `pg_stat_activity` and server logs show `atlas_ingest` sessions separately; `atlas doctor` checks privileges |
| Shared server | No server setting, extension, `pg_hba.conf` entry, other role or other database changes |

## 12. Approval requested

1. Amend DEC-044 to the text in §2 (six roles).
2. Accept the role attributes (§4) and grant matrix (§5).
3. Accept the ATLAS-001 baseline effects (§6), handled without editing ATLAS-001's documents.
4. Accept the local (§7) and CI (§8) bootstrap plan and the rollback (§10).

After approval, nothing is executed until CP3: Claude writes the script and the migration; the owner runs the script; Claude verifies read-only.
