"""Focused F2 unit tests for Recommendation Decision Pipeline.

Covers the five required behaviours from the verified F2 Implementation Design:
1. Need is generated only through Decision State
2. need_match threshold behaviour
3. UnknownPriority mapping
4. Medical Context activation and non-diagnostic boundary
5. Inference is represented as computed output
"""
import pytest
from unittest.mock import MagicMock, patch

from app.services.recommendation_service import (
    RecommendationService,
    NEED_MATCH_SUFFICIENT,
)
from app.reasoning.conflict_analyzer import ConflictSeverity


@pytest.fixture
def svc():
    """Service with mocked repositories (no DB required)."""
    db = MagicMock()
    service = RecommendationService(db)
    service.product_repo = MagicMock()
    service.inventory_repo = MagicMock()
    service.pk_repo = MagicMock()
    service.evidence_repo = MagicMock()
    service.reasoning_engine = MagicMock()
    return service


# ------------------------------------------------------------------
# 1. Need only through Decision State
# ------------------------------------------------------------------
def test_need_never_taken_directly_from_raw_concerns(svc):
    profile = {"concerns": "dry skin, tightness"}
    ds = svc._build_decision_state("CASE1", profile)
    needs = svc._generate_needs_from_decision_state(ds)

    assert "dry skin" in needs or any("dry" in n.lower() for n in needs)
    # Critical invariant: needs come from factors inside Decision State, not raw string
    assert ds["factors"], "factors must be populated from concerns"
    assert needs == svc._generate_needs_from_decision_state(ds)


def test_empty_concerns_produce_no_needs(svc):
    ds = svc._build_decision_state("CASE1", {"concerns": ""})
    needs = svc._generate_needs_from_decision_state(ds)
    assert needs == []


# ------------------------------------------------------------------
# 2. need_match threshold
# ------------------------------------------------------------------
def test_need_match_sufficient_threshold(svc):
    needs = ["dry skin", "hydration"]
    # perfect overlap
    score = svc._calculate_need_match(needs, "dry skin, hydration, barrier")
    assert score >= NEED_MATCH_SUFFICIENT


def test_need_match_insufficient_when_no_overlap(svc):
    needs = ["dry skin"]
    score = svc._calculate_need_match(needs, "anti-aging, brightening")
    assert score < NEED_MATCH_SUFFICIENT


def test_need_match_zero_when_no_needs(svc):
    assert svc._calculate_need_match([], "anything") == 0.0


# ------------------------------------------------------------------
# 3. UnknownPriority mapping
# ------------------------------------------------------------------
def test_unknown_priority_mapping(svc):
    assert svc._map_unknown_priority(ConflictSeverity.CRITICAL.value) == "CRITICAL_UNKNOWN"
    assert svc._map_unknown_priority(ConflictSeverity.HIGH.value) == "IMPORTANT_UNKNOWN"
    assert svc._map_unknown_priority(ConflictSeverity.MEDIUM.value) == "OPTIONAL_UNKNOWN"
    assert svc._map_unknown_priority(ConflictSeverity.LOW.value) == "OPTIONAL_UNKNOWN"
    assert svc._map_unknown_priority("UNKNOWN_VALUE") == "OPTIONAL_UNKNOWN"


# ------------------------------------------------------------------
# 4. Medical Context — activation + non-diagnostic boundary
# ------------------------------------------------------------------
def test_medical_context_activates_on_token(svc):
    profile = {"concerns": "خشکی پوست", "medical_notes": "تحت درمان پزشک"}
    active, notes = svc._detect_medical_context(profile, [])
    assert active is True
    assert "پزشک" in notes or "تحت درمان" in notes


def test_medical_context_does_not_activate_on_ordinary_concern(svc):
    profile = {"concerns": "dry skin, tightness"}
    active, notes = svc._detect_medical_context(profile, [])
    assert active is False
    assert notes == ""


def test_medical_context_never_contains_diagnosis_language(svc):
    """Boundary: detector only flags tokens; it must not invent a diagnosis."""
    profile = {"concerns": "بیماری پوستی"}
    active, notes = svc._detect_medical_context(profile, [])
    assert active is True
    # Must not contain diagnostic conclusions
    forbidden = ["diagnosis", "تشخیص", "شما مبتلا", "you have"]
    for word in forbidden:
        assert word not in notes.lower()


# ------------------------------------------------------------------
# 5. Inference as computed output
# ------------------------------------------------------------------
def test_inference_is_computed_output(svc):
    engine_result = {
        "unknowns": [{"field": "brand", "severity": "CRITICAL", "action": "ESCALATE_PO", "notes": "missing"}],
        "claim_boundary_violations": [{"reason": "INFERENCE_TO_FACT"}],
        "conflicts": [],
    }
    decision_state = {
        "medical_context_active": True,
        "factors": [{"value": "dry skin"}],
        "unknowns": [],
        "conflicts": [],
    }
    inferences = svc._build_inferences(engine_result, decision_state, "PROD1")

    assert isinstance(inferences, list)
    assert len(inferences) >= 1
    for inf in inferences:
        assert "statement" in inf
        assert "confidence" in inf
        assert "source" in inf
        # Must never be marked as Fact
        assert inf.get("validity") != "FACT"
        assert "diagnosis" not in inf.get("statement", "").lower()


def test_inference_empty_when_engine_clean_and_no_medical(svc):
    engine_result = {"unknowns": [], "claim_boundary_violations": [], "conflicts": []}
    decision_state = {"medical_context_active": False, "factors": [], "unknowns": [], "conflicts": []}
    inferences = svc._build_inferences(engine_result, decision_state, "PROD1")
    assert inferences == []
