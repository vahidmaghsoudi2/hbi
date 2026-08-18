#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import sys

print("Starting HBI GATE 6-4 Preflight Check...")
print(f"Python version: {sys.version}")

SCHEMA_SQL = """
CREATE TABLE Product (
    product_id TEXT PRIMARY KEY,
    brand TEXT NOT NULL,
    product_name TEXT NOT NULL,
    variant TEXT,
    size_value REAL,
    size_unit TEXT,
    barcode_gtin TEXT UNIQUE,
    market_region TEXT,
    country_of_origin TEXT,
    packaging_version TEXT,
    identity_status TEXT NOT NULL CHECK (
        identity_status IN ('VERIFIED','PARTIAL_IDENTITY','CONFLICT','NEEDS_REVIEW')
    ),
    identity_confidence REAL CHECK (identity_confidence >= 0.0 AND identity_confidence <= 1.0),
    identity_source_refs TEXT,
    qa_verdict TEXT DEFAULT 'PENDING' CHECK (
        qa_verdict IN ('PENDING','VALID','INVALID','CONFLICT','UNKNOWN','NEEDS_REVIEW')
    ),
    qa_reviewed_at DATETIME,
    qa_notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE ProductKnowledge (
    product_knowledge_id TEXT PRIMARY KEY,
    product_id TEXT NOT NULL,
    ingredients TEXT,
    ingredient_roles TEXT,
    claimed_benefits TEXT,
    known_use_cases TEXT,
    contraindications TEXT,
    usage_instructions TEXT,
    manufacturer_claims TEXT,
    evidence_refs TEXT,
    evidence_status TEXT CHECK (evidence_status IN ('SUPPORTED','PARTIAL','CONFLICT','UNKNOWN')),
    knowledge_confidence REAL CHECK (knowledge_confidence >= 0.0 AND knowledge_confidence <= 1.0),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES Product(product_id) ON DELETE RESTRICT
);

CREATE TABLE Evidence (
    evidence_id TEXT PRIMARY KEY,
    product_id TEXT NOT NULL,
    source_type TEXT NOT NULL,
    source_reference TEXT NOT NULL,
    claim TEXT NOT NULL,
    claim_type TEXT CHECK (
        claim_type IN ('FACT','MANUFACTURER_CLAIM','EVIDENCE_SUPPORTED','INFERENCE','UNKNOWN')
    ),
    source_date TEXT,
    evidence_level TEXT,
    evidence_status TEXT CHECK (evidence_status IN ('SUPPORTED','PARTIAL','CONFLICT','UNKNOWN')),
    conflict_status TEXT CHECK (conflict_status IN ('NONE','CONFLICT')),
    retrieved_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES Product(product_id) ON DELETE RESTRICT
);

CREATE TABLE Customer (
    customer_id TEXT PRIMARY KEY,
    name TEXT NOT NULL DEFAULT '',
    mobile TEXT,
    consent_to_store_data INTEGER NOT NULL DEFAULT 0 CHECK (consent_to_store_data IN (0, 1)),
    consent_date DATETIME,
    age_range TEXT,
    sex_if_relevant TEXT,
    skin_profile TEXT,
    hair_profile TEXT,
    scalp_profile TEXT,
    concerns TEXT,
    observations TEXT,
    answers TEXT,
    case_history TEXT,
    operator_notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE "Case" (
    case_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    case_type TEXT,
    identified_needs TEXT,
    evidence_gaps TEXT,
    confidence REAL CHECK (confidence >= 0.0 AND confidence <= 1.0),
    operator_override TEXT,
    reasoning_status TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id) ON DELETE RESTRICT
);

CREATE TABLE Recommendation (
    recommendation_id TEXT PRIMARY KEY,
    case_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    need_match_score REAL CHECK (need_match_score >= 0.0 AND need_match_score <= 1.0),
    evidence_score REAL CHECK (evidence_score >= 0.0 AND evidence_score <= 1.0),
    eligibility_status TEXT CHECK (
        eligibility_status IN ('ELIGIBLE','INELIGIBLE_PENDING_VERIFICATION','INELIGIBLE_CONFLICT','INELIGIBLE_PENDING_REVIEW','INELIGIBLE_OUT_OF_STOCK')
    ),
    ranking_score REAL,
    ranking_reasons TEXT,
    exclusion_reasons TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (case_id) REFERENCES "Case"(case_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES Product(product_id) ON DELETE RESTRICT
);

CREATE TABLE Inventory (
    inventory_id TEXT PRIMARY KEY,
    product_id TEXT NOT NULL UNIQUE,
    quantity_available INTEGER DEFAULT 0 CHECK (quantity_available >= 0),
    quantity_reserved INTEGER DEFAULT 0 CHECK (quantity_reserved >= 0),
    quantity_damaged INTEGER DEFAULT 0 CHECK (quantity_damaged >= 0),
    stock_status TEXT CHECK (stock_status IN ('AVAILABLE','RESERVED','DAMAGED','OUT_OF_STOCK')),
    purchase_price_toman INTEGER,
    sale_price_toman INTEGER,
    price_updated_at DATETIME,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES Product(product_id) ON DELETE RESTRICT
);

CREATE TABLE Sale (
    sale_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    total_amount_toman INTEGER NOT NULL CHECK (total_amount_toman >= 0),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id) ON DELETE RESTRICT
);

CREATE TABLE SaleItem (
    sale_item_id TEXT PRIMARY KEY,
    sale_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price_toman INTEGER NOT NULL CHECK (unit_price_toman >= 0),
    FOREIGN KEY (sale_id) REFERENCES Sale(sale_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES Product(product_id) ON DELETE RESTRICT
);

CREATE VIEW CustomerPurchaseHistory AS
SELECT c.customer_id, si.product_id, si.quantity, s.created_at AS purchase_date
FROM Sale s
JOIN SaleItem si ON s.sale_id = si.sale_id
JOIN Customer c ON s.customer_id = c.customer_id;

CREATE INDEX idx_recommendation_case ON Recommendation(case_id);
CREATE INDEX idx_recommendation_product ON Recommendation(product_id);
CREATE INDEX idx_sale_customer ON Sale(customer_id);
CREATE INDEX idx_saleitem_sale ON SaleItem(sale_id);
CREATE INDEX idx_saleitem_product ON SaleItem(product_id);
CREATE INDEX idx_evidence_product ON Evidence(product_id);
CREATE INDEX idx_productknowledge_product ON ProductKnowledge(product_id);

CREATE TRIGGER update_product_updated_at AFTER UPDATE ON Product
FOR EACH ROW WHEN NEW.updated_at = OLD.updated_at
BEGIN UPDATE Product SET updated_at = CURRENT_TIMESTAMP WHERE product_id = NEW.product_id; END;

CREATE TRIGGER update_productknowledge_updated_at AFTER UPDATE ON ProductKnowledge
FOR EACH ROW WHEN NEW.updated_at = OLD.updated_at
BEGIN UPDATE ProductKnowledge SET updated_at = CURRENT_TIMESTAMP WHERE product_knowledge_id = NEW.product_knowledge_id; END;

CREATE TRIGGER update_customer_updated_at AFTER UPDATE ON Customer
FOR EACH ROW WHEN NEW.updated_at = OLD.updated_at
BEGIN UPDATE Customer SET updated_at = CURRENT_TIMESTAMP WHERE customer_id = NEW.customer_id; END;

CREATE TRIGGER update_case_updated_at AFTER UPDATE ON "Case"
FOR EACH ROW WHEN NEW.updated_at = OLD.updated_at
BEGIN UPDATE "Case" SET updated_at = CURRENT_TIMESTAMP WHERE case_id = NEW.case_id; END;

CREATE TRIGGER update_inventory_updated_at AFTER UPDATE ON Inventory
FOR EACH ROW WHEN NEW.updated_at = OLD.updated_at
BEGIN UPDATE Inventory SET updated_at = CURRENT_TIMESTAMP WHERE inventory_id = NEW.inventory_id; END;
"""

def main():
    print("Connecting to in-memory SQLite database...")
    conn = sqlite3.connect(":memory:")
conn.execute('PRAGMA foreign_keys=ON')
    conn.execute("PRAGMA foreign_keys = ON;")
    
    print("Executing Schema v1.1 DDL...")
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    
    print("Checking tables...")
    tables = {"Product", "ProductKnowledge", "Evidence", "Customer", "Case", 
              "Recommendation", "Inventory", "Sale", "SaleItem"}
    actual_tables = {row[0] for row in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchall()}
    
    print(f"Expected tables: {len(tables)}")
    print(f"Actual tables: {len(actual_tables)}")
    
    missing = tables - actual_tables
    if missing:
        print(f"Missing tables: {missing}")
    else:
        print("All required tables exist.")
    
    print("\nTesting CHECK constraints...")
    
    # Test identity_status
    try:
        conn.execute("INSERT INTO Product (product_id, brand, product_name, identity_status) VALUES ('P1','B','N','BAD')")
        print("[FAIL] identity_status CHECK constraint failed")
    except sqlite3.IntegrityError:
        print("[PASS] identity_status CHECK constraint works")
    
    # Test qa_verdict
    try:
        conn.execute("INSERT INTO Product (product_id, brand, product_name, identity_status, qa_verdict) VALUES ('P2','B','N','VERIFIED','BAD')")
        print("[FAIL] qa_verdict CHECK constraint failed")
    except sqlite3.IntegrityError:
        print("[PASS] qa_verdict CHECK constraint works")
    
    print("\nTesting CASCADE delete...")
    conn.execute("INSERT INTO Customer (customer_id, name) VALUES ('C1','Test')")
    conn.execute('INSERT INTO "Case" (case_id, customer_id) VALUES (\'CASE1\',\'C1\')')
    conn.execute("INSERT INTO Product (product_id, brand, product_name, identity_status) VALUES ('PROD1','B','N','VERIFIED')")
    conn.execute("INSERT INTO Recommendation (recommendation_id, case_id, product_id, eligibility_status) VALUES ('REC1','CASE1','PROD1','ELIGIBLE')")
    conn.commit()
    
    conn.execute('DELETE FROM "Case" WHERE case_id=\'CASE1\'')
    conn.commit()
    
    rec_count = conn.execute("SELECT COUNT(*) FROM Recommendation WHERE recommendation_id='REC1'").fetchone()[0]
    if rec_count == 0:
        print("[PASS] Recommendation CASCADE on Case delete works")
    else:
        print(f"[FAIL] Recommendation still exists after Case delete: {rec_count}")
    
    print("\nGATE 6-4 Preflight Check completed successfully.")
    conn.close()

if __name__ == "__main__":
    main()