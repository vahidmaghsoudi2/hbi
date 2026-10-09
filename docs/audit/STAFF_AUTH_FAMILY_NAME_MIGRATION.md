# Customer.family_name migration note

**Branch:** `feature/staff-auth-consultation-sale`  
**Date:** 2026-10-09

## Schema change
- Add nullable column `Customer.family_name` (VARCHAR / String).
- Script: `scripts/migrate_customer_family_name.py`
- SQL note: `scripts/migrations/20261009_customer_family_name.sql`

## Legacy data
- Existing rows keep `family_name = NULL`.
- **No backfill from `name`** — guessing family name from full name is not allowed.
- Until staff sets `family_name`, mobile-match rebind is refused (safe default).

## Identity rule
- Mobile is primary identifier.
- Family name participates in match.
- First/given name does **not** affect identity decisions.
- Mobile owned by another customer → conflict, no row changes.

## Apply (existing SQLite runtime DB)
```bash
python scripts/migrate_customer_family_name.py --db data/hbi.db
```

Tests use in-memory DB created from SQLAlchemy metadata and do not prove this migration on a production file.
