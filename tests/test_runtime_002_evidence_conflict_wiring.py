"""HBI-RUNTIME-002 — Evidence.conflict_status propagation into Recommendation path."""
from types import SimpleNamespace

from app.reasoning.reasoning_engine import ReasoningEngine
from app.services.recommendation_service import RecommendationService


def test_engine_receives_and_analyzes_existing_conflicts():
    engine = ReasoningEngine()
    result = engine.run(
        product_id="p1",
        evidence_list=[{
            "evidence_id": "e1",
            "field": "safety",
            "claim": "claim A",
            "claim_type": "FACT",
            "conflict_status": "CONFLICT",
            "source_reference": "src",
            "source_type": "PEER_REVIEWED",
        }],
        existing_conflicts=[{
            "field": "safety",
            "conflicting_values": ["claim A", "claim B"],
            "evidence_refs": ["e1"],
            "sources": ["src"],
        }],
        need_match=0.9,
        evidence_score=0.8,
        inventory_score=1.0,
    )
    assert len(result.get("conflicts") or []) >= 1
    assert result.get("eligibility") != "ELIGIBLE"


def test_no_conflict_keeps_eligible_when_scores_ok():
    engine = ReasoningEngine()
    result = engine.run(
        product_id="p1",
        evidence_list=[{
            "evidence_id": "e1",
            "field": "texture",
            "claim": "smooth",
            "claim_type": "FACT",
            "conflict_status": "NONE",
            "source_reference": "src",
            "source_type": "PEER_REVIEWED",
        }],
        existing_conflicts=[],
        need_match=0.9,
        evidence_score=0.8,
        inventory_score=1.0,
    )
    assert result.get("conflicts") == []
    assert result.get("eligibility") == "ELIGIBLE"


def test_existing_conflicts_from_evidence_helper():
    svc = RecommendationService.__new__(RecommendationService)
    evidences = [
        SimpleNamespace(
            evidence_id="e1", field="safety", claim="A",
            conflict_status="CONFLICT", source_reference="s1",
        ),
        SimpleNamespace(
            evidence_id="e2", field="texture", claim="B",
            conflict_status="NONE", source_reference="s2",
        ),
        SimpleNamespace(
            evidence_id="e3", field="allergy", claim="C",
            conflict_status="CONFLICT", source_reference="s3",
        ),
    ]
    out = svc._existing_conflicts_from_evidence(evidences, "prod-1")
    assert len(out) == 2
    fields = {c["field"] for c in out}
    assert fields == {"safety", "allergy"}
    assert all(c["product_id"] == "prod-1" for c in out)


def test_map_eligibility_with_engine_needs_review_from_conflict():
    svc = RecommendationService.__new__(RecommendationService)
    decision_state = {"unknowns": [], "needs": ["hydration"], "medical_context_active": False}
    engine_result = {
        "eligibility": "NEEDS_REVIEW",
        "conflicts": [{"field": "safety", "severity": "CRITICAL"}],
        "unknowns": [],
    }
    elig = svc._map_eligibility(engine_result, decision_state, need_match=0.9, product_unknowns=[])
    assert elig == "INELIGIBLE_PENDING_REVIEW"


def test_case_unknowns_not_mutated_by_product_conflicts():
    """GAP-01: product conflicts must not write into shared Case Decision State unknowns."""
    svc = RecommendationService.__new__(RecommendationService)
    decision_state = {
        "unknowns": [],
        "needs": ["hydration"],
        "medical_context_active": False,
        "factors": [{"value": "hydration", "source": "customer_input", "validity": "DECLARED"}],
    }
    before = list(decision_state["unknowns"])
    engine_result = {
        "eligibility": "NEEDS_REVIEW",
        "conflicts": [{"field": "safety", "severity": "CRITICAL"}],
        "unknowns": [{"field": "safety", "severity": "CRITICAL"}],
    }
    _ = svc._map_eligibility(engine_result, decision_state, need_match=0.9, product_unknowns=[])
    assert decision_state["unknowns"] == before
