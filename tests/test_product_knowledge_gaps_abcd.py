"""Regression tests for Product Knowledge gaps A and D.

Gap A: empty-field approved evidence must land in other_attributes (not dropped).
Gap D: add_evidence conflict transitions must rebuild ProductKnowledge aggregates.
"""
from __future__ import annotations

import json

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.models.base import Base
from app.models.evidence import Evidence
from app.models.inventory import Inventory
from app.models.product import Product
from app.services.evidence_service import EvidenceService
from app.services.product_knowledge_service import ProductKnowledgeService


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


def _seed_product(db, pid: str):
    db.add(
        Product(
            product_id=pid,
            brand="Brand",
            product_name="Item",
            identity_status="NEEDS_REVIEW",
            qa_verdict="PENDING",
            status="DRAFT",
            product_line="SKIN",
        )
    )
    db.flush()
    db.add(
        Inventory(
            inventory_id=f"INV-{pid}",
            product_id=pid,
            quantity_available=0,
            quantity_reserved=0,
            quantity_damaged=0,
            stock_status="OUT_OF_STOCK",
        )
    )
    db.commit()


def test_empty_field_approved_evidence_routes_to_other_attributes(db):
    """Gap A: approved evidence with no field must populate other_attributes."""
    _seed_product(db, "P-GAP-A")
    db.add(
        Evidence(
            evidence_id="EV-GAP-A1",
            product_id="P-GAP-A",
            claim_id="CLM-GAP-A1",
            source_type="PEER_REVIEWED",
            source_reference="https://example.test/label",
            claim="فرم: سرم",
            field=None,
            claim_type="FACT",
            qa_status="VERIFIED",
            conflict_status="NONE",
            evidence_status="UNKNOWN",
            evidence_strength="MODERATE",
        )
    )
    db.commit()
    pk = ProductKnowledgeService(db).update_from_evidence("P-GAP-A")
    assert pk is not None
    attrs = json.loads(pk.other_attributes or "{}")
    assert attrs.get("فرم") == "سرم"


def test_conflict_on_add_rebuilds_stale_product_knowledge(db):
    """Gap D: conflicting add_evidence must clear previously aggregated trusted values."""
    _seed_product(db, "P-GAP-D")
    svc = EvidenceService(db)
    first = svc.add_evidence(
        {
            "product_id": "P-GAP-D",
            "source_type": "PEER_REVIEWED",
            "source_reference": "https://example.test/a",
            "claim": "niacinamide",
            "field": "ingredients",
            "claim_type": "FACT",
        }
    )
    svc.verify_evidence(first.evidence_id, "VERIFIED", actor_id="tester", reason="seed")
    pk1 = ProductKnowledgeService(db).get_or_create("P-GAP-D")
    assert "niacinamide" in (pk1.ingredients or "")

    second = svc.add_evidence(
        {
            "product_id": "P-GAP-D",
            "source_type": "PEER_REVIEWED",
            "source_reference": "https://example.test/b",
            "claim": "retinol",
            "field": "ingredients",
            "claim_type": "FACT",
        }
    )
    assert (second.conflict_status or "").upper() == "CONFLICT"
    reloaded_first = svc.get_by_id(first.evidence_id)
    assert (reloaded_first.conflict_status or "").upper() == "CONFLICT"

    pk2 = ProductKnowledgeService(db).get_or_create("P-GAP-D")
    ingredients = (pk2.ingredients or "").strip()
    domain = json.loads(pk2.domain_evidence_status or "{}")
    assert ingredients == "" or "niacinamide" not in ingredients
    assert domain.get("ingredients") == "CONFLICT" or (pk2.evidence_status or "").upper() == "CONFLICT"
