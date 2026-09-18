"""Regression coverage for Recommendation hard eligibility gates."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.models import Base
from app.models.product import Product
from app.models.inventory import Inventory
from app.repositories.product_repository import ProductRepository
from app.services.recommendation_service import RecommendationService
from app.reasoning.conflict_analyzer import ConflictSeverity


def test_product_candidates_require_active_and_valid_qa():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    db = sessionmaker(bind=engine)()

    for pid, status, qa in [
        ("P-DRAFT", "DRAFT", "PENDING"),
        ("P-APPROVED", "APPROVED", "VALID"),
        ("P-ACTIVE-BAD-QA", "ACTIVE", "PENDING"),
        ("P-ACTIVE", "ACTIVE", "VALID"),
    ]:
        db.add(Product(
            product_id=pid,
            brand="HBI",
            product_name=pid,
            identity_status="VERIFIED",
            qa_verdict=qa,
            status=status,
        ))
    db.commit()
    for pid in ("P-DRAFT", "P-APPROVED", "P-ACTIVE-BAD-QA", "P-ACTIVE"):
        db.add(Inventory(
            inventory_id=f"INV-{pid}",
            product_id=pid,
            quantity_available=10,
            quantity_reserved=0,
            stock_status="AVAILABLE",
            sale_price_toman=0,
        ))
    db.commit()

    candidates = ProductRepository(db).find_by_identity_status_and_active("VERIFIED")
    assert [p.product_id for p in candidates] == ["P-ACTIVE"]

    db.close()
    Base.metadata.drop_all(bind=engine)


def test_recommendation_hard_gates_block_claim_violation_and_high_conflict():
    service = RecommendationService.__new__(RecommendationService)

    base_state = {
        "medical_context_active": False,
        "needs": ["آبرسان و مرطوب‌کننده"],
        "unknowns": [],
    }
    eligible_engine = {"eligibility": "ELIGIBLE", "claim_boundary_violations": [], "conflicts": []}
    assert service._map_eligibility(eligible_engine, base_state, 1.0) == "ELIGIBLE"

    claim_bad = dict(eligible_engine, claim_boundary_violations=[{"reason": "overclaim"}])
    assert service._map_eligibility(claim_bad, base_state, 1.0) == "INELIGIBLE_PENDING_REVIEW"

    conflict_bad = dict(eligible_engine, conflicts=[{"severity": ConflictSeverity.HIGH.value}])
    assert service._map_eligibility(conflict_bad, base_state, 1.0) == "INELIGIBLE_PENDING_REVIEW"
