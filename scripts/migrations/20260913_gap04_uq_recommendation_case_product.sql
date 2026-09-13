-- GAP-04 (HBI-PO-DEC-GAP04-002): enforce one current Recommendation per Case + Product
-- Repo has no Alembic runtime; schema source of truth is SQLAlchemy models (create_all).
-- Apply this SQL on existing SQLite/Postgres deployments AFTER verifying no duplicate
-- (case_id, product_id) rows exist.
--
-- Pre-check (must return 0 rows before applying unique index):
--   SELECT case_id, product_id, COUNT(*) AS c
--   FROM Recommendation
--   GROUP BY case_id, product_id
--   HAVING COUNT(*) > 1;
--
-- If duplicates exist: STOP and escalate to PO (do not delete/merge without authorization).

-- SQLite
CREATE UNIQUE INDEX IF NOT EXISTS uq_recommendation_case_product
ON Recommendation (case_id, product_id);

-- Postgres equivalent (if not using model-driven migrate):
-- ALTER TABLE "Recommendation"
--   ADD CONSTRAINT uq_recommendation_case_product UNIQUE (case_id, product_id);
