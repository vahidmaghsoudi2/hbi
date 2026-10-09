-- HBI migration: Customer.family_name for identity matching
-- Rule: mobile primary; family_name for match; first name ignored.
-- Legacy rows: family_name remains NULL until staff captures it.
-- NULL family_name blocks silent rebind on mobile match (safe default).

-- SQLite
-- ALTER TABLE Customer ADD COLUMN family_name VARCHAR;

-- PostgreSQL
-- ALTER TABLE "Customer" ADD COLUMN IF NOT EXISTS family_name VARCHAR;

-- Idempotent application is handled by scripts/migrate_customer_family_name.py
