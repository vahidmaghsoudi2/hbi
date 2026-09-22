"""HBI-CATALOG-INTAKE-FIX-001 — ProductKnowledge only from QA-approved Evidence.

PO rules:
1. ProductKnowledge must not include PENDING / REJECTED / NEEDS_REVIEW claims.
2. After Evidence QA change, ProductKnowledge must be rebuilt.
"""
from __future__ import annotations

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.models.base import Base
from app.models.evidence import Evidence
from app.models.inventory import Inventory
from app.models.product import Product
from app.models.product_knowledge import ProductKnowledge
from app.services.evidence_service import EvidenceService
from app.services.product_knowledge_service import ProductKnowledgeService
from app.services.recommendation_service import RecommendationService


@pytest.fixture()
def db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def _fk(conn, _):
        conn.cursor().execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


def _seed_product(db, pid="P-PK-QA"):
    db.add(
        Product(
            product_id=pid,
            brand="B",
            product_name="Sunscreen",
            identity_status="VERIFIED",
            qa_verdict="VALID",
            status="ACTIVE",
        )
    )
    db.flush()
    db.add(
        Inventory(
            inventory_id=f"INV-{pid}",
            product_id=pid,
            quantity_available=1,
            quantity_reserved=0,
            quantity_damaged=0,
            stock_status="active",
        )
    )
    db.commit()


def _add_use_case_evidence(db, *, pid, eid, claim="sunscreen", qa="PENDING"):
    db.add(
        Evidence(
            evidence_id=eid,
            product_id=pid,
            claim_id=f"CLM-{eid}",
            source_type="OFFICIAL_MANUFACTURER",
            source_reference="label",
            claim=claim,
            field="known_use_cases",
            qa_status=qa,
            evidence_status="UNKNOWN",
            conflict_status="NONE",
        )
    )
    db.commit()


def test_pending_evidence_not_in_product_knowledge(db):
    _seed_product(db)
    _add_use_case_evidence(db, pid="P-PK-QA", eid="E-PEND", qa="PENDING")
    pk = ProductKnowledgeService(db).update_from_evidence("P-PK-QA")
    assert pk.known_use_cases is None or "sunscreen" not in (pk.known_use_cases or "")


def test_verify_then_reject_then_reverify_rebuilds_knowledge(db):
    _seed_product(db)
    _add_use_case_evidence(db, pid="P-PK-QA", eid="E1", claim="sunscreen", qa="PENDING")

    pk0 = ProductKnowledgeService(db).update_from_evidence("P-PK-QA")
    assert not (pk0.known_use_cases and "sunscreen" in pk0.known_use_cases)

    EvidenceService(db).verify_evidence("E1", "VERIFIED")
    db.commit()
    pk1 = db.query(ProductKnowledge).filter_by(product_id="P-PK-QA").one()
    assert pk1.known_use_cases is not None
    assert "sunscreen" in pk1.known_use_cases

    svc = RecommendationService(db)
    nm1 = svc._calculate_need_match(["sun protection"], pk1.known_use_cases)
    assert nm1 == 1.0

    EvidenceService(db).verify_evidence("E1", "REJECTED")
    db.commit()
    db.expire_all()
    pk2 = db.query(ProductKnowledge).filter_by(product_id="P-PK-QA").one()
    assert not (pk2.known_use_cases and "sunscreen" in pk2.known_use_cases)
    nm2 = svc._calculate_need_match(["sun protection"], pk2.known_use_cases)
    assert nm2 == 0.0

    EvidenceService(db).verify_evidence("E1", "VERIFIED")
    db.commit()
    db.expire_all()
    pk3 = db.query(ProductKnowledge).filter_by(product_id="P-PK-QA").one()
    assert pk3.known_use_cases is not None and "sunscreen" in pk3.known_use_cases
    assert svc._calculate_need_match(["sun protection"], pk3.known_use_cases) == 1.0


def test_needs_review_verdict_clears_approved_claim(db):
    _seed_product(db)
    _add_use_case_evidence(db, pid="P-PK-QA", eid="E2", claim="sunscreen", qa="VERIFIED")
    ProductKnowledgeService(db).update_from_evidence("P-PK-QA")
    EvidenceService(db).verify_evidence("E2", "NEEDS_REVIEW")
    db.commit()
    db.expire_all()
    pk = db.query(ProductKnowledge).filter_by(product_id="P-PK-QA").one()
    assert not (pk.known_use_cases and "sunscreen" in pk.known_use_cases)
