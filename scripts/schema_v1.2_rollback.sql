PRAGMA foreign_keys = OFF;
BEGIN TRANSACTION;

CREATE TABLE Evidence_v1_1 (
    evidence_id VARCHAR PRIMARY KEY, product_id VARCHAR NOT NULL,
    source_type VARCHAR NOT NULL, source_reference VARCHAR NOT NULL, claim VARCHAR NOT NULL,
    claim_type VARCHAR NULL, evidence_level VARCHAR NULL, evidence_status VARCHAR NULL,
    conflict_status VARCHAR NULL, source_date VARCHAR NULL, retrieved_at DATETIME NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES Product(product_id) ON DELETE RESTRICT,
);

INSERT INTO Evidence_v1_1 (
    evidence_id, product_id, source_type, source_reference, claim, claim_type,
    evidence_level, evidence_status, conflict_status, source_date, retrieved_at, created_at
)
SELECT
    evidence_id, product_id, source_type, source_reference, claim, claim_type,
    CASE WHEN evidence_strength IN ('STRONG','MODERATE','WEAK','UNVERIFIED') THEN evidence_strength ELSE NULL END,
    evidence_status, conflict_status, source_date, evidence_date, created_at
FROM Evidence;

DROP TABLE Evidence;
ALTER TABLE Evidence_v1_1 RENAME TO Evidence;

PRAGMA user_version = 110;
COMMIT;
PRAGMA foreign_keys = ON;
