"""Regression for Product Knowledge gaps B (DTO parity) and D (rebuild after conflict).

Gap B is frontend-type parity and is checked by string presence against the
backend schema contract. Gap D proves that conflict transitions on add_evidence
refresh an existing ProductKnowledge aggregate.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.models.base import Base
from app.models.product import Product
from app.models.product_knowledge import ProductKnowledge
from app.services.evidence_service import EvidenceService
from app.services.product_knowledge_service import ProductKnowledgeService


@pytest.fixture()
def db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def _product(db, product_id: str = "P-GAP-D") -> Product:
    p = Product(
        product_id=product_id,
        brand="TestBrand",
        product_name="Gap D Product",
        product_line="SKIN",
        identity_status="NEEDS_REVIEW",
        qa_verdict="PENDING",
        status="DRAFT",
        market_region="IR",
        packaging_version="v1",
    )
    db.add(p)
    db.commit()
    return p


def test_gap_b_frontend_product_knowledge_dto_matches_backend_fields():
    """Frontend ProductKnowledgeDTO must expose backend other_attributes + domain_evidence_status."""
    frontend = Path("frontend/src/types/api.ts").read_text(encoding="utf-8")
    start = frontend.find("export interface ProductKnowledgeDTO")
    assert start >= 0
    end = frontend.find("}", start)
    block = frontend[start : end + 1]
    assert "other_attributes" in block
    assert "domain_evidence_status" in block
    backend = Path("app/interface/schemas.py").read_text(encoding="utf-8")
    bstart = backend.find("class ProductKnowledgeResponse")
    bend = backend.find("\n\nclass ", bstart + 1)
    bblock = backend[bstart:bend]
    assert "other_attributes" in bblock
    assert "domain_evidence_status" in bblock


def test_gap_d_add_evidence_conflict_rebuilds_existing_product_knowledge(db):
    """When a second conflicting claim is added, existing PK overall status must become CONFLICT."""
    _product(db)
    ev = EvidenceService(db)

    first = ev.add_evidence(
        {
            "product_id": "P-GAP-D",
            "source_type": "MANUFACTURER",
            "source_reference": "https://example.test/a",
            "claim": "niacinamide 5%",
            "field": "ingredients",
            "claim_type": "MANUFACTURER_CLAIM",
            "market_region": "IR",
        }
    )
    ev.verify_evidence(first.evidence_id, "VERIFIED", reason="label verified")
    pk = ProductKnowledgeService(db).update_from_evidence("P-GAP-D")
    assert pk is not None
    assert pk.evidence_status in {"SUPPORTED", "PARTIAL"}
    assert "niacinamide" in (pk.ingredients or "").lower()

    second = ev.add_evidence(
        {
            "product_id": "P-GAP-D",
            "source_type": "MANUFACTURER",
            "source_reference": "https://example.test/b",
            "claim": "niacinamide 10%",
            "field": "ingredients",
            "claim_type": "MANUFACTURER_CLAIM",
            "market_region": "IR",
        }
    )
    assert (second.conflict_status or "").upper() == "CONFLICT"
    refreshed = (
        db.query(ProductKnowledge)
        .filter(ProductKnowledge.product_id == "P-GAP-D")
        .first()
    )
    assert refreshed is not None
    assert refreshed.evidence_status == "CONFLICT"
    domains = json.loads(refreshed.domain_evidence_status or "{}")
    assert domains.get("ingredients") == "CONFLICT"


def test_gap_d_pending_only_add_without_conflict_does_not_create_knowledge(db):
    """PENDING research drafts with no conflict must not create ProductKnowledge (preserve design)."""
    _product(db, "P-GAP-D-PEND")
    ev = EvidenceService(db)
    ev.add_evidence(
        {
            "product_id": "P-GAP-D-PEND",
            "source_type": "MANUFACTURER",
            "source_reference": "https://example.test/draft",
            "claim": "spf 50",
            "field": "other_attributes",
            "claim_type": "MANUFACTURER_CLAIM",
        }
    )
    pk = (
        db.query(ProductKnowledge)
        .filter(ProductKnowledge.product_id == "P-GAP-D-PEND")
        .first()
    )
    assert pk is None
