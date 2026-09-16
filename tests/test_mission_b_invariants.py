"""Mission B invariants — protect red lines during Product & Business Integration.

Proves:
1. NEED_MATCH_SUFFICIENT and evidence weights unchanged
2. Medical Context remains a hard gate (independent of Need)
3. Specialist Override still does not mutate Recommendation

Issue #37 remains OPEN (not touched by these tests).
"""
from types import SimpleNamespace
from unittest.mock import MagicMock

from app.services.recommendation_service import (
    RecommendationService,
    NEED_MATCH_SUFFICIENT,
    _EVIDENCE_WEIGHTS,
)
from app.models.customer import Customer
from app.models.case import Case
from app.models.product import Product
from app.models.recommendation import Recommendation
from app.services.specialist_override_service import SpecialistOverrideService


def test_need_match_threshold_unchanged():
    assert NEED_MATCH_SUFFICIENT == 0.40


def test_evidence_weights_unchanged():
    assert _EVIDENCE_WEIGHTS["PEER_REVIEWED"] == 1.0
    assert _EVIDENCE_WEIGHTS["CLINICAL_TRIAL"] == 1.0
    assert _EVIDENCE_WEIGHTS["REGULATORY"] == 1.0
    assert _EVIDENCE_WEIGHTS["OFFICIAL_MANUFACTURER"] == 0.6
    assert _EVIDENCE_WEIGHTS["MANUFACTURER"] == 0.6
    assert _EVIDENCE_WEIGHTS["REPUTABLE_RETAILER"] == 0.4
    assert _EVIDENCE_WEIGHTS["SECONDARY"] == 0.2


def test_medical_context_still_hard_gates_with_valid_need():
    """Medical Hard Gate must remain active even when Need is present."""
    db = MagicMock()
    svc = RecommendationService(db)
    svc.product_repo = MagicMock()
    svc.inventory_repo = MagicMock()
    svc.pk_repo = MagicMock()
    svc.evidence_repo = MagicMock()
    svc.reasoning_engine = MagicMock()
    svc.repository = MagicMock()

    product = SimpleNamespace(product_id="P-MED")
    svc.product_repo.find_by_identity_status_and_active.return_value = [product]
    svc.repository.find_by_case.return_value = []
    svc.repository.find_by_case_and_product.return_value = None
    svc.pk_repo.find_by_product.return_value = SimpleNamespace(
        known_use_cases="dry skin",
        claimed_benefits="",
        contraindications="",
        ingredients="",
    )
    svc.inventory_repo.find_by_product.return_value = SimpleNamespace(quantity_available=5)
    svc.evidence_repo.find_by_product.return_value = []
    svc.reasoning_engine.run.return_value = {
        "evidence_refs": [],
        "warnings": [],
        "unknowns": [],
        "conflicts": [],
        "claim_boundary_violations": [],
        "eligibility": "ELIGIBLE",
        "final_score": 0.9,
        "rationale": "would be eligible without medical gate",
    }

    result = svc.generate_recommendations(
        "CASE-MED",
        {"concerns": "dry skin", "medical_notes": "تحت درمان پزشک"},
    )
    assert result == [], "Medical Context + valid Need must still hard-gate"
    svc.repository.create.assert_not_called()


def test_override_still_does_not_mutate_recommendation(db_session):
    db_session.add(Customer(customer_id="CUST-INV", name="Inv", consent_to_store_data=1))
    db_session.flush()
    db_session.add(Case(case_id="CASE-INV", customer_id="CUST-INV"))
    db_session.add(Product(
        product_id="PROD-INV", brand="B", product_name="P", identity_status="VERIFIED",
    ))
    db_session.flush()
    rec = Recommendation(
        recommendation_id="rec_CASE-INV_PROD-INV",
        case_id="CASE-INV",
        product_id="PROD-INV",
        eligibility_status="ELIGIBLE",
        ranking_score=0.77,
        need_match_score=0.8,
        evidence_score=0.6,
    )
    db_session.add(rec)
    db_session.commit()

    svc = SpecialistOverrideService(db_session)
    svc.create_override(
        recommendation_id=rec.recommendation_id,
        case_id="CASE-INV",
        specialist_id="SPEC-INV",
        action="REJECT",
        reason="Invariant check",
    )
    db_session.commit()

    refreshed = db_session.get(Recommendation, rec.recommendation_id)
    assert refreshed.eligibility_status == "ELIGIBLE"
    assert refreshed.ranking_score == 0.77
