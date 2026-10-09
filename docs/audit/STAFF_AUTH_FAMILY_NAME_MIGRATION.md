# Customer.family_name migration note

**Branch:** `feature/staff-auth-consultation-sale`  
**Date:** 2026-10-09

## Schema change
- Add nullable `Customer.family_name` (`VARCHAR` / SQLAlchemy `String`).
- Migration runner: `scripts/migrate_customer_family_name.py`
- SQL reference: `scripts/migrations/20261009_customer_family_name.sql`
- Supported runtime target currently documented by the script: SQLite.

## Identity and legacy-data rules
- Existing rows keep `family_name = NULL`.
- **No backfill from `name`** — guessing a family name from a display name is not allowed.
- Mobile is the primary identifier; family name confirms a mobile match. Given/first name is not an identity key.
- A mobile already owned by a different customer is rejected with HTTP 409 **before any customer update or Case creation**.
- Missing family name cannot confirm a service-level mobile match; silent rebind is refused.

## Migration validation performed on this branch
The new regression test `tests/test_staff_auth_consultation_sale_path.py::test_family_name_migration_is_idempotent_and_does_not_guess_legacy_names` creates a temporary SQLite database with a pre-existing `Customer` table and legacy row, runs the migration twice, and checks:
1. `family_name` is added;
2. the migration is idempotent;
3. the existing display name remains unchanged;
4. `family_name` remains NULL (no inferred backfill).

This is a schema-fixture test, **not** a claim that the actual runtime database was migrated.

## Actual target database status: NOT VERIFIED
The repository branch does not contain `data/hbi.db`, and no staging/production database connection or credentials are available in this execution context. Therefore the actual database's current schema/version and the migration result on that database cannot be truthfully confirmed here.

Before runtime rollout, an operator with access to the target SQLite file must:
```bash
python scripts/migrate_customer_family_name.py --db data/hbi.db
```
Then capture the command output and verify the target schema with:
```bash
python -c "import sqlite3; c=sqlite3.connect('data/hbi.db'); print([r[1] for r in c.execute('PRAGMA table_info(Customer)')]); print(c.execute('SELECT COUNT(*) FROM Customer WHERE family_name IS NULL OR TRIM(family_name) = \'\'').fetchone()[0])"
```
Do not report runtime migration success until that target-specific check has been run.
