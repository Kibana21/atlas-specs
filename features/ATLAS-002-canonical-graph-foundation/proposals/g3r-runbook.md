# Gate G3-R: ingestion-role setup runbook (owner-controlled)

**Status:** Prepared (CP3 task A2-T01), **not executed**. **Not required for local development** (owner decision, 25 Oct 2026: single-user model, ADR-0001 §Privileges, TD-DEV-010); kept as the production-hardening procedure and exercised by backend CI. Each step marked *Owner* is run only by the server owner, after the owner's explicit G3-R authorization. Claude never runs the setup or rollback script, and never creates, sees or stores a password.

**Design:** DEC-044 as amended (six roles; `proposals/dec-044-amendment.md`), ADR-0001 §Privileges. **Files:**

- `postgres-ingest-roles.sql`: additive setup. Creates `atlas_ingest` and `atlas_test_ingest` only;
- `postgres-ingest-roles-verify.sql`: read-only checks;
- `postgres-ingest-roles-rollback.sql`: removes the two roles only.

**Unchanged:**

- the ATLAS-001 script `postgres-local-setup.sql` (its guard aborts on a re-run, and it is not re-run);
- the four ATLAS-001 roles and both databases' ownership;
- every other role and database;
- server settings and `pg_hba.conf`;
- Redis.

## 1. Before running (read-only)

| Who | Step |
|---|---|
| Owner | Review the three SQL files at the merged atlas-specs commit |
| Claude (on request) | `make doctor` in atlas-backend (read-only): the server is PostgreSQL 15, the four ATLAS-001 roles and both databases exist, and `atlas_ingest`/`atlas_test_ingest` don't exist yet. Ownership, PUBLIC privileges and schema `atlas` in `atlas_test` are not doctor checks: the setup script's guards check them, and a read-only catalog query can confirm them beforehand |

The setup script re-checks all of this itself and aborts before any change if anything differs.

## 2. Create the roles (Owner)

```bash
cd <atlas-specs checkout>/features/ATLAS-002-canonical-graph-foundation/proposals
# Choose two different passwords; type them, don't paste them into files. `read -s` keeps
# them out of the terminal and the shell history.
read -rs ATLAS_INGEST_PASSWORD && export ATLAS_INGEST_PASSWORD
read -rs ATLAS_TEST_INGEST_PASSWORD && export ATLAS_TEST_INGEST_PASSWORD
psql -h localhost -d postgres -X -v ON_ERROR_STOP=1 -f postgres-ingest-roles.sql
```

Expected last line: `Atlas ingestion roles created. Run postgres-ingest-roles-verify.sql (read-only) next.` A guard failure prints `ABORT: …` and changes nothing.

## 3. Verify (Owner, read-only)

```bash
psql -h localhost -d postgres -X -v ON_ERROR_STOP=1 -f postgres-ingest-roles-verify.sql
unset ATLAS_INGEST_PASSWORD ATLAS_TEST_INGEST_PASSWORD
```

Expected last line: `OK: ingestion roles verified (read-only).` The script checks:

- six `atlas_*` login roles, no special attributes, connection limits 3/10/2;
- no role memberships;
- session limits 120 s / 60 s / 10 s;
- `CONNECT` on the role's own database only;
- no `TEMP` or `CREATE`;
- `USAGE` without `CREATE` on schema `atlas`;
- `search_path = atlas`;
- no table privilege before migration `0002`.

## 4. Local settings (Owner)

Add to the git-ignored atlas-backend files. Use the same form as the existing URLs; the passwords stay only in these files.

| File | Lines |
|---|---|
| `.env` | `ATLAS_INGEST_DATABASE_URL=postgresql+psycopg://atlas_ingest:<password>@localhost:5432/atlas_db` and `ATLAS_DB_INGEST_ROLE=atlas_ingest` |
| `.env.test` | `ATLAS_INGEST_DATABASE_URL=postgresql+psycopg://atlas_test_ingest:<password>@localhost:5432/atlas_test` and `ATLAS_DB_INGEST_ROLE=atlas_test_ingest` |

The API never reads these values; only migrations (the role name) and the ingestion entry points do.

## 5. After the owner reports completion (Claude)

1. `make doctor`: read-only. Records the ingestion roles' presence, attributes and connection, and confirms no excess privilege.
2. With G3-R recorded, run migration `0002` on the local **`atlas_test`** only (`make integration`). The suite cleans up the rows it creates.
3. Migration `0002` on the local **`atlas_db`** runs only with a separate owner approval (spec §6 step 4).

## 6. Rollback (Owner, only by decision)

1. Downgrade migration `0002` in both databases (empty databases only), or keep the tables and let the rollback script revoke the table privileges.
2. Run `psql -h localhost -d postgres -X -v ON_ERROR_STOP=1 -f postgres-ingest-roles-rollback.sql`. Expected last line: `Ingestion roles removed; the four ATLAS-001 roles are unchanged.`
3. Remove the two lines from `.env` and `.env.test`.

## 7. CI (no owner action)

Backend CI runs verbatim, drift-checked copies of the setup, verification and rollback scripts in its own ephemeral `postgres:15` service, with random masked per-job passwords. It never connects to the shared server. CI exercises all three scripts on every run, including the rollback after downgrading migration `0002`.
