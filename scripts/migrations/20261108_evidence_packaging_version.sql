-- Gap C (HBI-PO Decision 2026-11-08): optional per-Evidence packaging_version provenance.
-- Additive only. Nullable. No historical rewrite.
-- Repo schema source of truth is SQLAlchemy models (create_all for fresh DBs).
-- Do NOT run against operational databases without explicit PO authorization.
--
-- Semantics (must match app/services/product_knowledge_service.version_scope_key):
--   * Explicit Evidence.packaging_version takes precedence over Product.packaging_version.
--   * NULL Evidence.packaging_version is legacy: aggregation inherits Product packaging for
--     scope matching only; the Evidence row is never back-filled.
--   * Packaging version is NOT a formula-version identifier.
--   * Different packaging scopes never silently merge content or conflict flags.
--
-- Pre-check (SQLite): column must not already exist.
--   PRAGMA table_info(Evidence);
--
-- Upgrade (SQLite):
ALTER TABLE Evidence ADD COLUMN packaging_version VARCHAR NULL;

-- Upgrade (Postgres equivalent):
-- ALTER TABLE "Evidence" ADD COLUMN IF NOT EXISTS packaging_version VARCHAR NULL;

-- Downgrade (SQLite): SQLite cannot DROP COLUMN on older versions without table rebuild.
-- Prefer leaving the nullable column in place. If forced removal is required, rebuild:
--   CREATE TABLE Evidence_new (... without packaging_version ...);
--   INSERT INTO Evidence_new SELECT <all columns except packaging_version> FROM Evidence;
--   DROP TABLE Evidence; ALTER TABLE Evidence_new RENAME TO Evidence;
-- Downgrade (Postgres):
-- ALTER TABLE "Evidence" DROP COLUMN IF EXISTS packaging_version;
