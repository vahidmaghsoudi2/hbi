-- P4 P0 schema changes (non-destructive)
-- Expand Product.status vocabulary; set server default to DRAFT for new rows.
-- Existing ACTIVE rows are grandfathered (N.9) and are NOT bulk-converted.

-- ProductMutationLog and UserRole tables are created by SQLAlchemy metadata
-- via app.database.init_db() which imports product_mutation_log and user_role.

-- Status CHECK expansion (PostgreSQL example):
-- ALTER TABLE "Product" DROP CONSTRAINT IF EXISTS ck_product_status;
-- ALTER TABLE "Product" ADD CONSTRAINT ck_product_status
--   CHECK (status IN ('DRAFT','SUBMITTED','QA_REVIEW','APPROVED','ACTIVE','REJECTED','ARCHIVED'));
-- ALTER TABLE "Product" ALTER COLUMN status SET DEFAULT 'DRAFT';
