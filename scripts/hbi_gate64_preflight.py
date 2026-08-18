#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HBI GATE 6-4 Preflight / QA Contract Checker

Purpose:
- Validate locked Schema v1.1 contract in an isolated in-memory SQLite DB.
- Validate selected HBI QA framework rules as executable helper tests.
- Produce a report for delivery to Architecture Authority / ChatGPT.

Important:
- This script does NOT modify project source files.
- It creates only one report file: HBI_GATE64_PREFLIGHT_REPORT.txt
- It uses embedded Schema v1.1 DDL. Decorative SQL comments were ASCII-normalized.
"""

import io
import re
import sqlite3
import sys
import time
import unittest
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPORT_FILE = SCRIPT_DIR / "HBI_GATE64_PREFLIGHT_REPORT.txt"

SCHEMA_SQL = """
-- ===================================================
-- HBI SQL SCHEMA v1.1 LOCKED
-- Status: APPROVED by Qwen + Grok + Product Owner
-- Reference: V2.2 Master Protocol
-- ===================================================

-- UNIT CONVENTIONS
-- Monetary: INTEGER, Toman
-- Confidence: REAL, [0.0, 1.0]
-- Dates: TEXT, ISO 8601
-- Timestamps: DATETIME, SQLite CURRENT_TIMESTAMP

-- 1. Product
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

-- 2. ProductKnowledge
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

-- 3. Evidence
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

-- 4. Customer
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

-- 5. Case
CREATE TABLE Case (
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

-- 6. Recommendation
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
    FOREIGN KEY (case_id) REFERENCES Case(case_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES Product(product_id) ON DELETE RESTRICT
);

-- 7. Inventory
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

-- 8. Sale
CREATE TABLE Sale (
    sale_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    total_amount_toman INTEGER NOT NULL CHECK (total_amount_toman >= 0),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id) ON DELETE RESTRICT
);

-- 9. SaleItem
CREATE TABLE SaleItem (
    sale_item_id TEXT PRIMARY KEY,
    sale_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price_toman INTEGER NOT NULL CHECK (unit_price_toman >= 0),
    FOREIGN KEY (sale_id) REFERENCES Sale(sale_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES Product(product_id) ON DELETE RESTRICT
);

-- 10. Derived View
CREATE VIEW CustomerPurchaseHistory AS
SELECT c.customer_id, si.product_id, si.quantity, s.created_at AS purchase_date
FROM Sale s
JOIN SaleItem si ON s.sale_id = si.sale_id
JOIN Customer c ON s.customer_id = c.customer_id;

-- 11. Indexes
CREATE INDEX idx_recommendation_case ON Recommendation(case_id);
CREATE INDEX idx_recommendation_product ON Recommendation(product_id);
CREATE INDEX idx_sale_customer ON Sale(customer_id);
CREATE INDEX idx_saleitem_sale ON SaleItem(sale_id);
CREATE INDEX idx_saleitem_product ON SaleItem(product_id);
CREATE INDEX idx_evidence_product ON Evidence(product_id);
CREATE INDEX idx_productknowledge_product ON ProductKnowledge(product_id);

-- 12. Triggers
CREATE TRIGGER update_product_updated_at AFTER UPDATE ON Product
FOR EACH ROW WHEN NEW.updated_at = OLD.updated_at
BEGIN UPDATE Product SET updated_at = CURRENT_TIMESTAMP WHERE product_id = NEW.product_id; END;

CREATE TRIGGER update_productknowledge_updated_at AFTER UPDATE ON ProductKnowledge
FOR EACH ROW WHEN NEW.updated_at = OLD.updated_at
BEGIN UPDATE ProductKnowledge SET updated_at = CURRENT_TIMESTAMP WHERE product_knowledge_id = NEW.product_knowledge_id; END;

CREATE TRIGGER update_customer_updated_at AFTER UPDATE ON Customer
FOR EACH ROW WHEN NEW.updated_at = OLD.updated_at
BEGIN UPDATE Customer SET updated_at = CURRENT_TIMESTAMP WHERE customer_id = NEW.customer_id; END;

CREATE TRIGGER update_case_updated_at AFTER UPDATE ON Case
FOR EACH ROW WHEN NEW.updated_at = OLD.updated_at
BEGIN UPDATE Case SET updated_at = CURRENT_TIMESTAMP WHERE case_id = NEW.case_id; END;

CREATE TRIGGER update_inventory_updated_at AFTER UPDATE ON Inventory
FOR EACH ROW WHEN NEW.updated_at = OLD.updated_at
BEGIN UPDATE Inventory SET updated_at = CURRENT_TIMESTAMP WHERE inventory_id = NEW.inventory_id; END;
"""

CLAIM_TYPES = {
    "FACT",
    "MANUFACTURER_CLAIM",
    "EVIDENCE_SUPPORTED",
    "INFERENCE",
    "UNKNOWN",
}

EVIDENCE_STATUSES = {
    "SUPPORTED",
    "PARTIAL",
    "CONFLICT",
    "UNKNOWN",
}

SOURCE_TYPES = {
    "OFFICIAL_MANUFACTURER",
    "REGULATORY",
    "REPUTABLE_RETAILER",
    "SECONDARY",
}

EVIDENCE_STRENGTHS = {
    "STRONG",
    "MODERATE",
    "WEAK",
    "UNVERIFIED",
}

EVIDENCE_QA_STATUSES = {
    "PENDING",
    "VERIFIED",
    "REJECTED",
    "NEEDS_REVIEW",
}

PRODUCT_IDENTITY_VERDICTS = {
    "IDENTIFIED",
    "PARTIALLY_IDENTIFIED",
    "UNIDENTIFIED",
}

SOURCE_PRIORITY = {
    "OFFICIAL_MANUFACTURER": 0,
    "REGULATORY": 1,
    "REPUTABLE_RETAILER": 2,
    "SECONDARY": 3,
}

PRODUCT_IDENTITY_REQUIRED_FIELDS = (
    "product_id",
    "brand",
    "canonical_name",
    "variant",
    "size",
    "barcode_gtin",
    "market_region",
    "packaging_version",
    "inventory_confirmation",
    "inventory_confirmation_date",
)

EVIDENCE_LEDGER_REQUIRED_FIELDS = (
    "claim_id",
    "claim_text",
    "field",
    "claim_type",
    "source",
    "source_type",
    "source_date",
    "evidence_date",
    "evidence_strength",
    "market_region",
    "qa_status",
)


def is_iso_date(value):
    try:
        datetime.fromisoformat(str(value))
        return True
    except ValueError:
        return False


def validate_product_identity_record(record):
    """
    Contract-level validation based on FRAMEWORK 1.A.
    This is not a Schema v1.1 table validator; it validates the QA identity contract.
    """
    errors = []
    if not isinstance(record, dict):
        return ["invalid:record_type"]

    for field in PRODUCT_IDENTITY_REQUIRED_FIELDS:
        if field not in record or record[field] in (None, ""):
            errors.append(f"missing:{field}")

    verdict = record.get("verdict")
    if verdict not in PRODUCT_IDENTITY_VERDICTS:
        errors.append("invalid:verdict")

    date_value = record.get("inventory_confirmation_date")
    if date_value not in (None, "") and not is_iso_date(date_value):
        errors.append("format:inventory_confirmation_date")

    return errors


def validate_evidence_ledger_entry(entry):
    """
    Validates a single Evidence Ledger entry based on FRAMEWORK 3.
    """
    errors = []
    if not isinstance(entry, dict):
        return ["invalid:entry_type"]

    for field in EVIDENCE_LEDGER_REQUIRED_FIELDS:
        if field not in entry or entry[field] in (None, ""):
            errors.append(f"missing:{field}")

    claim_id = str(entry.get("claim_id", ""))
    if claim_id and not re.match(r"^EV-.+-\d+$", claim_id):
        errors.append("format:claim_id")

    claim_type = entry.get("claim_type")
    if claim_type and claim_type not in CLAIM_TYPES:
        errors.append("invalid:claim_type")

    source_type = entry.get("source_type")
    if source_type and source_type not in SOURCE_TYPES:
        errors.append("invalid:source_type")

    evidence_strength = entry.get("evidence_strength")
    if evidence_strength and evidence_strength not in EVIDENCE_STRENGTHS:
        errors.append("invalid:evidence_strength")

    qa_status = entry.get("qa_status")
    if qa_status and qa_status not in EVIDENCE_QA_STATUSES:
        errors.append("invalid:qa_status")

    for date_field in ("source_date", "evidence_date"):
        value = entry.get(date_field)
        if value not in (None, "") and not is_iso_date(value):
            errors.append(f"format:{date_field}")

    return errors


def can_promote_claim(from_type, to_type):
    """
    Conservative implementation of FRAMEWORK 4 promotion rules.
    UNKNOWN cannot be promoted to anything.
    Anything cannot be automatically promoted to FACT unless it is already FACT.
    """
    if from_type not in CLAIM_TYPES or to_type not in CLAIM_TYPES:
        return False

    if from_type == "UNKNOWN":
        return False

    if to_type == "FACT":
        return from_type == "FACT"

    return True


def unknown_field_action(is_critical):
    """
    FRAMEWORK 5: UNKNOWN handling.
    """
    if is_critical:
        return {
            "field_value": "UNKNOWN",
            "evidence_status": "UNKNOWN",
            "status": "UNVERIFIED",
            "product_verdict": "NEEDS_REVIEW",
            "warning": False,
            "action": "ESCALATE_PO",
            "register": "UNKNOWN_REGISTER",
        }

    return {
        "field_value": "UNKNOWN",
        "evidence_status": "UNKNOWN",
        "status": "UNVERIFIED",
        "product_verdict": "VALID",
        "warning": True,
        "action": "LOG_UNKNOWN_REGISTER",
        "register": "UNKNOWN_REGISTER",
    }


def resolve_conflict_by_priority(sources):
    known_sources = [source for source in sources if source in SOURCE_PRIORITY]
    if not known_sources:
        return None, "NEEDS_REVIEW"

    selected = min(known_sources, key=lambda source: SOURCE_PRIORITY[source])
    return selected, "RESOLVED_BY_PRIORITY_LOGGED"


def conflict_action(resolvable, sources=None):
    """
    FRAMEWORK 5: CONFLICT handling.
    Never silently pick a value; always log/escalate.
    """
    sources = sources or []

    if not resolvable:
        return {
            "status": "CONFLICT_UNRESOLVED",
            "action": "ESCALATE_PO",
            "severity": "CRITICAL",
            "register": "CONFLICT_REGISTER",
        }

    selected_source, resolution_status = resolve_conflict_by_priority(sources)

    if selected_source is None:
        return {
            "status": "NEEDS_REVIEW",
            "action": "ESCALATE_ARCHITECT_OR_PO",
            "severity": "HIGH",
            "register": "CONFLICT_REGISTER",
        }

    return {
        "status": resolution_status,
        "selected_source": selected_source,
        "action": "LOG_CONFLICT_REGISTER",
        "severity": "MEDIUM",
        "register": "CONFLICT_REGISTER",
    }


class HbiSchemaContractTests(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
conn.execute('PRAGMA foreign_keys=ON')
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self.conn.executescript(SCHEMA_SQL)
        self.conn.commit()

    def tearDown(self):
        self.conn.close()

    def scalar(self, query, params=()):
        cursor = self.conn.execute(query, params)
        row = cursor.fetchone()
        return row[0] if row else None

    def assert_integrity_error(self, query, params=()):
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute(query, params)
        self.conn.rollback()

    def insert_product(
        self,
        product_id="QA-TEST-PRODUCT-001",
        barcode_gtin=None,
        identity_status="VERIFIED",
        identity_confidence=1.0,
        qa_verdict="PENDING",
    ):
        self.conn.execute(
            """
            INSERT INTO Product (
                product_id, brand, product_name, variant, size_value, size_unit,
                barcode_gtin, market_region, country_of_origin, packaging_version,
                identity_status, identity_confidence, identity_source_refs, qa_verdict
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                product_id,
                "QA-BRAND",
                "QA TEST PRODUCT",
                "QA-VARIANT",
                100.0,
                "ml",
                barcode_gtin,
                "EU",
                "ES",
                "v1",
                identity_status,
                identity_confidence,
                "QA synthetic fixture",
                qa_verdict,
            ),
        )
        self.conn.commit()

    def insert_product_knowledge(
        self,
        product_knowledge_id="QA-PK-001",
        product_id="QA-TEST-PRODUCT-001",
        evidence_status="SUPPORTED",
        knowledge_confidence=1.0,
    ):
        self.conn.execute(
            """
            INSERT INTO ProductKnowledge (
                product_knowledge_id,
                product_id,
                evidence_status,
                knowledge_confidence
            ) VALUES (?,?,?,?)
            """,
            (
                product_knowledge_id,
                product_id,
                evidence_status,
                knowledge_confidence,
            ),
        )
        self.conn.commit()

    def insert_evidence(
        self,
        evidence_id="QA-EV-001",
        product_id="QA-TEST-PRODUCT-001",
        source_type="OFFICIAL_MANUFACTURER",
        claim_type="FACT",
        evidence_status="SUPPORTED",
        conflict_status="NONE",
    ):
        self.conn.execute(
            """
            INSERT INTO Evidence (
                evidence_id,
                product_id,
                source_type,
                source_reference,
                claim,
                claim_type,
                evidence_status,
                conflict_status,
                retrieved_at
            ) VALUES (?,?,?,?,?,?,?,?,CURRENT_TIMESTAMP)
            """,
            (
                evidence_id,
                product_id,
                source_type,
                "QA synthetic source reference",
                "QA synthetic evidence claim",
                claim_type,
                evidence_status,
                conflict_status,
            ),
        )
        self.conn.commit()

    def insert_customer(
        self,
        customer_id="QA-TEST-CUSTOMER-001",
        consent_to_store_data=1,
        name="QA Test Customer",
    ):
        self.conn.execute(
            """
            INSERT INTO Customer (
                customer_id,
                name,
                consent_to_store_data,
                consent_date
            ) VALUES (?,?,?,CURRENT_TIMESTAMP)
            """,
            (
                customer_id,
                name,
                consent_to_store_data,
            ),
        )
        self.conn.commit()

    def insert_case(
        self,
        case_id="QA-CASE-001",
        customer_id="QA-TEST-CUSTOMER-001",
        confidence=1.0,
    ):
        self.conn.execute(
            """
            INSERT INTO Case (
                case_id,
                customer_id,
                confidence
            ) VALUES (?,?,?)
            """,
            (
                case_id,
                customer_id,
                confidence,
            ),
        )
        self.conn.commit()

    def insert_recommendation(
        self,
        recommendation_id="QA-REC-001",
        case_id="QA-CASE-001",
        product_id="QA-TEST-PRODUCT-001",
        eligibility_status="ELIGIBLE",
        need_match_score=1.0,
        evidence_score=1.0,
        ranking_score=1.0,
    ):
        self.conn.execute(
            """
            INSERT INTO Recommendation (
                recommendation_id,
                case_id,
                product_id,
                need_match_score,
                evidence_score,
                eligibility_status,
                ranking_score,
                ranking_reasons,
                exclusion_reasons
            ) VALUES (?,?,?,?,?,?,?,?,?)
            """,
            (
                recommendation_id,
                case_id,
                product_id,
                need_match_score,
                evidence_score,
                eligibility_status,
                ranking_score,
                "QA synthetic ranking reason",
                None,
            ),
        )
        self.conn.commit()

    def insert_inventory(
        self,
        inventory_id="QA-INV-001",
        product_id="QA-TEST-PRODUCT-001",
        quantity_available=10,
        stock_status="AVAILABLE",
        sale_price_toman=1000,
    ):
        self.conn.execute(
            """
            INSERT INTO Inventory (
                inventory_id,
                product_id,
                quantity_available,
                quantity_reserved,
                quantity_damaged,
                stock_status,
                purchase_price_toman,
                sale_price_toman,
                price_updated_at
            ) VALUES (?,?,?,?,?,?,?,?,CURRENT_TIMESTAMP)
            """,
            (
                inventory_id,
                product_id,
                quantity_available,
                0,
                0,
                stock_status,
                900,
                sale_price_toman,
            ),
        )
        self.conn.commit()

    def insert_sale(
        self,
        sale_id="QA-SALE-001",
        customer_id="QA-TEST-CUSTOMER-001",
        total_amount_toman=1000,
    ):
        self.conn.execute(
            """
            INSERT INTO Sale (
                sale_id,
                customer_id,
                total_amount_toman
            ) VALUES (?,?,?)
            """,
            (
                sale_id,
                customer_id,
                total_amount_toman,
            ),
        )
        self.conn.commit()

    def insert_sale_item(
        self,
        sale_item_id="QA-SALEITEM-001",
        sale_id="QA-SALE-001",
        product_id="QA-TEST-PRODUCT-001",
        quantity=1,
        unit_price_toman=1000,
    ):
        self.conn.execute(
            """
            INSERT INTO SaleItem (
                sale_item_id,
                sale_id,
                product_id,
                quantity,
                unit_price_toman
            ) VALUES (?,?,?,?,?)
            """,
            (
                sale_item_id,
                sale_id,
                product_id,
                quantity,
                unit_price_toman,
            ),
        )
        self.conn.commit()

    def test_001_foreign_keys_enabled(self):
        self.assertEqual(self.scalar("PRAGMA foreign_keys;"), 1)

    def test_010_required_tables_exist(self):
        expected_tables = {
            "Product",
            "ProductKnowledge",
            "Evidence",
            "Customer",
            "Case",
            "Recommendation",
            "Inventory",
            "Sale",
            "SaleItem",
        }
        rows = self.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        ).fetchall()
        actual_tables = {row[0] for row in rows}
        self.assertTrue(expected_tables.issubset(actual_tables))

    def test_020_required_view_exists(self):
        count = self.scalar(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='view' AND name='CustomerPurchaseHistory'"
        )
        self.assertEqual(count, 1)

    def test_030_required_indexes_exist(self):
        expected_indexes = {
            "idx_recommendation_case",
            "idx_recommendation_product",
            "idx_sale_customer",
            "idx_saleitem_sale",
            "idx_saleitem_product",
            "idx_evidence_product",
            "idx_productknowledge_product",
        }
        rows = self.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%'"
        ).fetchall()
        actual_indexes = {row[0] for row in rows}
        self.assertTrue(expected_indexes.issubset(actual_indexes))

    def test_040_required_triggers_exist(self):
        expected_triggers = {
            "update_product_updated_at",
            "update_productknowledge_updated_at",
            "update_customer_updated_at",
            "update_case_updated_at",
            "update_inventory_updated_at",
        }
        rows = self.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='trigger'"
        ).fetchall()
        actual_triggers = {row[0] for row in rows}
        self.assertTrue(expected_triggers.issubset(actual_triggers))

    def test_050_product_defaults_and_checks(self):
        self.conn.execute(
            """
            INSERT INTO Product (product_id, brand, product_name, identity_status)
            VALUES ('QA-TEST-PRODUCT-DEFAULT','QA','QA','VERIFIED')
            """
        )
        self.conn.commit()

        qa_verdict = self.scalar(
            "SELECT qa_verdict FROM Product WHERE product_id='QA-TEST-PRODUCT-DEFAULT'"
        )
        self.assertEqual(qa_verdict, "PENDING")

        self.assert_integrity_error(
            """
            INSERT INTO Product (product_id, brand, product_name, identity_status)
            VALUES (?,?,?,?)
            """,
            ("QA-BAD-STATUS", "QA", "QA", "BAD_STATUS"),
        )

        self.assert_integrity_error(
            """
            INSERT INTO Product (product_id, brand, product_name, identity_status, qa_verdict)
            VALUES (?,?,?,?,?)
            """,
            ("QA-BAD-VERDICT", "QA", "QA", "VERIFIED", "BAD_VERDICT"),
        )

        self.assert_integrity_error(
            """
            INSERT INTO Product (product_id, brand, product_name, identity_status, identity_confidence)
            VALUES (?,?,?,?,?)
            """,
            ("QA-BAD-CONF-HIGH", "QA", "QA", "VERIFIED", 1.1),
        )

        self.assert_integrity_error(
            """
            INSERT INTO Product (product_id, brand, product_name, identity_status, identity_confidence)
            VALUES (?,?,?,?,?)
            """,
            ("QA-BAD-CONF-LOW", "QA", "QA", "VERIFIED", -0.1),
        )

        self.assert_integrity_error(
            """
            INSERT INTO Product (product_id, brand, product_name, identity_status)
            VALUES ('QA-TEST-PRODUCT-DEFAULT','QA','QA','VERIFIED')
            """
        )

        self.conn.execute(
            """
            INSERT INTO Product (product_id, brand, product_name, identity_status, barcode_gtin)
            VALUES ('QA-BC-1','QA','QA','VERIFIED','BC-001')
            """
        )
        self.conn.commit()

        self.assert_integrity_error(
            """
            INSERT INTO Product (product_id, brand, product_name, identity_status, barcode_gtin)
            VALUES ('QA-BC-2','QA','QA','VERIFIED','BC-001')
            """
        )

    def test_060_productknowledge_checks(self):
        self.insert_product()
        self.insert_product_knowledge()

        self.assert_integrity_error(
            """
            INSERT INTO ProductKnowledge (product_knowledge_id, product_id, evidence_status)
            VALUES ('QA-PK-BAD-STATUS','QA-TEST-PRODUCT-001','BAD')
            """
        )

        self.assert_integrity_error(
            """
            INSERT INTO ProductKnowledge (product_knowledge_id, product_id, knowledge_confidence)
            VALUES ('QA-PK-BAD-CONF-HIGH','QA-TEST-PRODUCT-001',1.1)
            """
        )

        self.assert_integrity_error(
            """
            INSERT INTO ProductKnowledge (product_knowledge_id, product_id, knowledge_confidence)
            VALUES ('QA-PK-BAD-CONF-LOW','QA-TEST-PRODUCT-001',-0.1)
            """
        )

        self.assert_integrity_error(
            """
            INSERT INTO ProductKnowledge (product_knowledge_id, product_id)
            VALUES ('QA-PK-MISSING-PRODUCT','MISSING-PRODUCT')
            """
        )

    def test_070_evidence_checks(self):
        self.insert_product()
        self.insert_evidence()

        self.assert_integrity_error(
            """
            INSERT INTO Evidence (evidence_id, product_id, source_type, source_reference, claim, claim_type)
            VALUES ('QA-EV-BAD-CLAIM-TYPE','QA-TEST-PRODUCT-001','OFFICIAL_MANUFACTURER','REF','CLAIM','BAD')
            """
        )

        self.assert_integrity_error(
            """
            INSERT INTO Evidence (evidence_id, product_id, source_type, source_reference, claim, claim_type, evidence_status)
            VALUES ('QA-EV-BAD-EV-STATUS','QA-TEST-PRODUCT-001','OFFICIAL_MANUFACTURER','REF','CLAIM','FACT','BAD')
            """
        )

        self.assert_integrity_error(
            """
            INSERT INTO Evidence (evidence_id, product_id, source_type, source_reference, claim, claim_type, conflict_status)
            VALUES ('QA-EV-BAD-CONFLICT','QA-TEST-PRODUCT-001','OFFICIAL_MANUFACTURER','REF','CLAIM','FACT','BAD')
            """
        )

        self.assert_integrity_error(
            """
            INSERT INTO Evidence (evidence_id, product_id, source_type, claim, claim_type)
            VALUES ('QA-EV-MISSING-REF','QA-TEST-PRODUCT-001','OFFICIAL_MANUFACTURER','CLAIM','FACT')
            """
        )

        self.assert_integrity_error(
            """
            INSERT INTO Evidence (evidence_id, product_id, source_type, source_reference, claim, claim_type)
            VALUES ('QA-EV-MISSING-PRODUCT','MISSING-PRODUCT','OFFICIAL_MANUFACTURER','REF','CLAIM','FACT')
            """
        )

    def test_080_customer_defaults_and_consent(self):
        self.conn.execute(
            "INSERT INTO Customer (customer_id) VALUES ('QA-CUST-DEFAULT')"
        )
        self.conn.commit()

        name = self.scalar(
            "SELECT name FROM Customer WHERE customer_id='QA-CUST-DEFAULT'"
        )
        consent = self.scalar(
            "SELECT consent_to_store_data FROM Customer WHERE customer_id='QA-CUST-DEFAULT'"
        )

        self.assertEqual(name, "")
        self.assertEqual(consent, 0)

        self.assert_integrity_error(
            "INSERT INTO Customer (customer_id, consent_to_store_data) VALUES ('QA-CUST-BAD', 2)"
        )

        self.assert_integrity_error(
            "INSERT INTO Customer (customer_id, name) VALUES ('QA-CUST-NULL-NAME', NULL)"
        )

    def test_090_case_confidence_bounds(self):
        self.insert_customer()
        self.insert_case()

        self.assert_integrity_error(
            "INSERT INTO Case (case_id, customer_id, confidence) VALUES ('QA-CASE-HIGH','QA-TEST-CUSTOMER-001',1.1)"
        )

        self.assert_integrity_error(
            "INSERT INTO Case (case_id, customer_id, confidence) VALUES ('QA-CASE-LOW','QA-TEST-CUSTOMER-001',-0.1)"
        )

        self.assert_integrity_error(
            "INSERT INTO Case (case_id, customer_id, confidence) VALUES ('QA-CASE-MISSING-CUST','MISSING',1.0)"
        )

    def test_100_recommendation_checks_and_case_cascade(self):
        self.insert_product()
        self.insert_customer()
        self.insert_case()
        self.insert_recommendation()

        self.assert_integrity_error(
            """
            INSERT INTO Recommendation (recommendation_id, case_id, product_id)
            VALUES ('QA-REC-MISSING-CASE','MISSING','QA-TEST-PRODUCT-001')
            """
        )

        self.assert_integrity_error(
            """
            INSERT INTO Recommendation (recommendation_id, case_id, product_id)
            VALUES ('QA-REC-MISSING-PRODUCT','QA-CASE-001','MISSING')
            """
        )

        self.assert_integrity_error(
            """
            INSERT INTO Recommendation (recommendation_id, case_id, product_id, eligibility_status)
            VALUES ('QA-REC-BAD-ELIG','QA-CASE-001','QA-TEST-PRODUCT-001','BAD')
            """
        )

        self.assert_integrity_error(
            """
            INSERT INTO Recommendation (recommendation_id, case_id, product_id, need_match_score)
            VALUES ('QA-REC-HIGH-NEED','QA-CASE-001','QA-TEST-PRODUCT-001',1.1)
            """
        )

        self.assert_integrity_error(
            """
            INSERT INTO Recommendation (recommendation_id, case_id, product_id, evidence_score)
            VALUES ('QA-REC-LOW-EVIDENCE','QA-CASE-001','QA-TEST-PRODUCT-001',-0.1)
            """
        )

        self.conn.execute("DELETE FROM Case WHERE case_id='QA-CASE-001'")
        self.conn.commit()

        count = self.scalar(
            "SELECT COUNT(*) FROM Recommendation WHERE recommendation_id='QA-REC-001'"
        )
        self.assertEqual(count, 0)

    def test_110_inventory_unique_and_checks(self):
        self.insert_product()
        self.insert_inventory()

        self.assert_integrity_error(
            """
            INSERT INTO Inventory (inventory_id, product_id, quantity_available)
            VALUES ('QA-INV-DUP','QA-TEST-PRODUCT-001',5)
            """
        )

        self.assert_integrity_error(
            "UPDATE Inventory SET quantity_available = -1 WHERE inventory_id='QA-INV-001'"
        )

        self.assert_integrity_error(
            "UPDATE Inventory SET quantity_reserved = -1 WHERE inventory_id='QA-INV-001'"
        )

        self.assert_integrity_error(
            "UPDATE Inventory SET quantity_damaged = -1 WHERE inventory_id='QA-INV-001'"
        )

        self.assert_integrity