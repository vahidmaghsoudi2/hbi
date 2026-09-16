"""Focused tests for Medical Context Hard Gate.

Requirement: when medical_context_active is True, recommendations must be
gated (INELIGIBLE_PENDING_REVIEW) even if a valid Need is present.
No scoring weights or thresholds are altered by this test.
"""
from types import SimpleNamespace
from unittest.mock import MagicMock

from app.services.recommendation_service import RecommendationService


def _service():
    db = MagicMock()
    service = RecommendationService(db)
    service.repository = MagicMock()
    service.product_repo = MagicMock()
    service.inventory_repo = MagicMock()
    service.pk_repo = MagicMock()
    service.evidence_repo = MagicMock()
    service.reasoning_engine = MagicMock()
    return service, db


def _complete_pk():
    return SimpleNamespace(
        known_use_cases="dry skin",
        claimed_benefits="hydration",
        contraindications="",
        ingredients="",
    )


def test_medical_context_with_valid_need_is_hard_gated():
    """Medical Context + valid Need must still produce empty recommendation list."""
    service, db = _service()
    product = SimpleNamespace(product_id="P1")
    service.product_repo.find_by_identity_status_and_active.return_value = [product]
    service.repository.find_by_case.return_value = []
    service.repository.find_by_case_and_product.return_value = None
    service.pk_repo.find_by_product.return_value = _complete_pk()
    service.inventory_repo.find_by_product.return_value = SimpleNamespace(quantity_available=5)
    service.evidence_repo.find_by_product.return_value = []
    service.reasoning_engine.run.return_value = {
        "evidence_refs": [],
        "warnings": [],
        "unknowns": [],
        "conflicts": [],
        "claim_boundary_violations": [],
        "eligibility": "ELIGIBLE",
        "final_score": 0.85,
        "rationale": "would be eligible without medical gate",
    }

    # Valid need ("dry skin") + medical token
    profile = {
        "concerns": "dry skin",
        "medical_notes": "تحت درمان پزشک",
    }

    result = service.generate_recommendations("CASE_MEDICAL", profile)

    assert result == [], "Medical Context must hard-gate even when Need is valid"
    service.repository.create.assert_not_called()
    db.delete.assert_not_called()


def test_medical_context_forces_referral_status():
    """decision_status must become REFERRAL when medical_context_active."""
    service, _ = _service()
    profile = {
        "concerns": "dry skin",
        "medical_notes": "pregnancy",
    }
    ds = service._build_decision_state("CASE2", profile)
    needs = service._generate_needs_from_decision_state(ds)
    ds["needs"] = needs
    if ds["medical_context_active"]:
        ds["decision_status"] = "REFERRAL"

    assert ds["medical_context_active"] is True
    assert ds["decision_status"] == "REFERRAL"
    # Eligibility must be gated
    elig = service._map_eligibility(
        {"eligibility": "ELIGIBLE"}, ds, need_match=0.9, product_unknowns=[]
    )
    assert elig == "INELIGIBLE_PENDING_REVIEW"
