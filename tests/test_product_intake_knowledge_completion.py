"""WP-INTAKE-KNOWLEDGE-COMPLETION-001 — approved Evidence rebuild coverage."""
from __future__ import annotations

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.models.base import Base
from app.models.evidence import Evidence
from app.models.product import Product
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


def _product(db, product_id="P-KC-001"):
    db.add(
        Product(
            product_id=product_id,
            brand="TestBrand",
            product_name="Knowledge Completion Test",
            identity_status="VERIFIED",
            qa_verdict="VALID",
            status="ACTIVE",
        )
    )
    db.commit()


def _evidence(db, *, product_id, evidence_id, field, claim, qa_status="VERIFIED", conflict_status="NONE"):
    db.add(
        Evidence(
            evidence_id=evidence_id,
            product_id=product_id,
            claim_id=f"CLM-{evidence_id}",
            source_type="MANUFACTURER",
            source_reference=f"ref:{evidence_id}",
            claim=claim,
            field=field,
            claim_type="MANUFACTURER_CLAIM",
            evidence_strength="STRONG",
            evidence_status="SUPPORTED",
            qa_status=qa_status,
            conflict_status=conflict_status,
        )
    )
    db.commit()


def test_approved_evidence_populates_completion_fields(db):
    _product(db)

    _evidence(db, product_id="P-KC-001", evidence_id="E-ROLE", field="ingredient_roles", claim="humectant, emollient")
    _evidence(db, product_id="P-KC-001", evidence_id="E-USAGE", field="usage_instructions", claim="apply twice daily, use after cleansing")
    _evidence(db, product_id="P-KC-001", evidence_id="E-MFG", field="manufacturer_claims", claim="fragrance-free, dermatologist tested")

    knowledge = ProductKnowledgeService(db).update_from_evidence("P-KC-001")

    assert set(knowledge.ingredient_roles.split(", ")) == {"humectant", "emollient"}
    assert set(knowledge.usage_instructions.split(", ")) == {"apply twice daily", "use after cleansing"}
    assert set(knowledge.manufacturer_claims.split(", ")) == {"fragrance-free", "dermatologist tested"}


@pytest.mark.parametrize("qa_status", ["PENDING", "REJECTED", "NEEDS_REVIEW"])
def test_non_approved_evidence_does_not_populate_completion_fields(db, qa_status):
    _product(db)
    _evidence(
        db,
        product_id="P-KC-001",
        evidence_id=f"E-{qa_status}",
        field="usage_instructions",
        claim="apply twice daily",
        qa_status=qa_status,
    )

    knowledge = ProductKnowledgeService(db).update_from_evidence("P-KC-001")
    assert knowledge.usage_instructions is None


def test_conflicting_evidence_does_not_populate_completion_fields(db):
    _product(db)
    _evidence(
        db,
        product_id="P-KC-001",
        evidence_id="E-CONFLICT",
        field="manufacturer_claims",
        claim="clinically proven",
        conflict_status="CONFLICT",
    )

    knowledge = ProductKnowledgeService(db).update_from_evidence("P-KC-001")
    assert knowledge.manufacturer_claims is None


def test_rebuild_clears_completion_field_when_eligible_evidence_is_removed_by_qa(db):
    _product(db)
    _evidence(
        db,
        product_id="P-KC-001",
        evidence_id="E-CLEAR",
        field="ingredient_roles",
        claim="humectant",
    )

    service = ProductKnowledgeService(db)
    first = service.update_from_evidence("P-KC-001")
    assert first.ingredient_roles == "humectant"

    evidence = db.query(Evidence).filter_by(evidence_id="E-CLEAR").one()
    evidence.qa_status = "REJECTED"
    db.commit()

    second = service.update_from_evidence("P-KC-001")
    assert second.ingredient_roles is None
