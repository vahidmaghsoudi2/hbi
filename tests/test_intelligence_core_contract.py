from types import SimpleNamespace
from unittest.mock import MagicMock

from app.services.need_normalization import (
    classify_phrase,
    normalize_needs_from_factors,
)
from app.services.recommendation_service import RecommendationService


def _service():
    db = MagicMock()
    service = RecommendationService(db)
    return service


def test_need_normalization_is_deterministic_and_traceable():
    factors = [
        {"name": "concern", "value": "خشکی پوست", "source": "customer_input", "validity": "DECLARED"},
        {"name": "concern", "value": "آبرسان", "source": "customer_input", "validity": "DECLARED"},
    ]

    first = normalize_needs_from_factors(factors)
    second = normalize_needs_from_factors(factors)

    assert first == second
    needs, mappings, unmapped, ambiguous = first
    assert needs == ["dry skin", "hydration"]
    assert len(mappings) == 2
    assert all(m["rule"] == "approved_synonym_map" for m in mappings)
    assert unmapped == []
    assert ambiguous == []


def test_unmapped_need_is_not_guessed():
    canonical, reason = classify_phrase("پوست شاداب")

    assert canonical is None
    assert reason == "no_approved_mapping"

    needs, mappings, unmapped, ambiguous = normalize_needs_from_factors([
        {"value": "پوست شاداب", "source": "customer_input", "validity": "DECLARED"}
    ])

    assert needs == []
    assert mappings == []
    assert len(unmapped) == 1
    assert ambiguous == []


def test_partial_mapping_remains_ambiguous():
    canonical, reason = classify_phrase("خیلی پوست خشک")

    assert canonical is None
    assert reason == "ambiguous"


def test_decision_state_keeps_raw_concerns_and_factor_provenance():
    service = _service()

    state = service._build_decision_state(
        "CASE-1",
        {"customer_id": "C-1", "concerns": "خشکی پوست, آبرسان"},
    )

    assert state["case_id"] == "CASE-1"
    assert state["customer_id"] == "C-1"
    assert state["raw_concerns"] == ["خشکی پوست", "آبرسان"]
    assert state["factors"] == [
        {"name": "concern", "value": "خشکی پوست", "source": "customer_input", "validity": "DECLARED"},
        {"name": "concern", "value": "آبرسان", "source": "customer_input", "validity": "DECLARED"},
    ]


def test_empty_or_unresolved_need_marks_decision_insufficient():
    service = _service()

    state = service._build_decision_state(
        "CASE-2",
        {"customer_id": "C-2", "concerns": "پوست شاداب"},
    )
    needs = service._generate_needs_from_decision_state(state)

    assert needs == []
    assert state["decision_status"] == "INSUFFICIENT"
    assert state["unmapped_need_factors"]


def test_medical_context_sets_referral_boundary_without_creating_need():
    service = _service()

    state = service._build_decision_state(
        "CASE-3",
        {"customer_id": "C-3", "concerns": "خشکی پوست", "medical_notes": "تحت درمان"},
    )

    assert state["medical_context_active"] is True
    assert "تحت درمان" in state["medical_context_notes"]


def test_eligibility_gate_rejects_candidate_before_ranking_result_is_accepted():
    service = _service()
    engine_result = {
        "eligibility": "ELIGIBLE",
        "final_score": 0.99,
    }
    decision_state = {
        "needs": ["dry skin"],
        "medical_context_active": False,
        "unknowns": [],
    }

    # Below the accepted minimum Need-match threshold, the candidate remains gated.
    eligibility = service._map_eligibility(engine_result, decision_state, 0.0)

    assert eligibility == "INELIGIBLE_PENDING_REVIEW"
