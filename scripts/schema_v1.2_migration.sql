PRAGMA foreign_keys = OFF;
BEGIN TRANSACTION;

ALTER TABLE Evidence RENAME COLUMN evidence_level TO evidence_strength;
ALTER TABLE Evidence RENAME COLUMN retrieved_at TO evidence_date;

CREATE TABLE Evidence_v1_2 (
    evidence_id VARCHAR PRIMARY KEY,
    product_id VARCHAR NOT NULL,
    claim_id VARCHAR UNIQUE,
    source_type VARCHAR NOT NULL,
    source_reference VARCHAR NOT NULL,
    claim VARCHAR NOT NULL,
    field VARCHAR NULL,
    market_region VARCHAR NULL,
    notes VARCHAR NULL,
    claim_type VARCHAR NULL,
    evidence_strength VARCHAR NULL,
    evidence_status VARCHAR NULL,
    conflict_status VARCHAR NULL,
    source_date VARCHAR NULL,
    evidence_date DATETIME NULL,
    qa_status VARCHAR DEFAULT 'PENDING',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES Product(product_id) ON DELETE RESTRICT,
    CHECK (claim_type IS NULL OR claim_type IN ('FACT','MANUFACTURER_CLAIM','EVIDENCE_SUPPORTED','INFERENCE','UNKNOWN')),
    CHECK (evidence_strength IS NULL OR evidence_strength IN ('STRONG','MODERATE','WEAK','UNVERIFIED')),
    CHECK (evidence_status IS NULL OR evidence_status IN ('SUPPORTED','PARTIAL','CONFLICT','UNKNOWN')),
    CHECK (conflict_status IS NULL OR conflict_status IN ('NONE','CONFLICT')),
    CHECK (qa_status IS NULL OR qa_status IN ('PENDING','VERIFIED','REJECTED','NEEDS_REVIEW'))
);

INSERT INTO Evidence_v1_2 (
    evidence_id, product_id, claim_id, source_type, source_reference, claim,
    field, market_region, notes, claim_type, evidence_strength, evidence_status,
    conflict_status, source_date, evidence_date, qa_status, created_at
)
SELECT
    e.evidence_id, e.product_id,
    'EV-' || e.product_id || '-' || (SELECT COUNT(*) FROM Evidence e2 WHERE e2.product_id = e.product_id AND e2.evidence_id <= e.evidence_id),
    e.source_type, e.source_reference, e.claim,
    NULL, NULL, NULL,
    e.claim_type, e.evidence_strength, e.evidence_status,
    e.conflict_status, e.source_date, e.evidence_date,
    'PENDING', e.created_at
FROM Evidence e;

DROP TABLE Evidence;
ALTER TABLE Evidence_v1_2 RENAME TO Evidence;

PRAGMA user_version = 120;
COMMIT;
PRAGMA foreign_keys = ON;
