from types import SimpleNamespace

import pytest

from app.services.recommendation_trust_trace_service import (
    RecommendationTrustTraceService,
    TrustTraceIntegrityError,
)


def ev(
    evidence_id,
    *,
    product_id="P1",
    claim_id=None,
    qa_status="APPROVED",
    conflict_status="NONE",
    claim="Supports hydration",
):
    return SimpleNamespace(
        evidence_id=evidence_id,
        claim_id=claim_id or f"C-{evidence_id}",
        product_id=product_id,
        claim=claim,
        field="claimed_benefits",
        claim_type="BENEFIT",
        source_type="OFFICIAL_MANUFACTURER",
        source_reference="https://example.test/source",
        evidence_strength="HIGH",
        evidence_status="SUPPORTED",
        qa_status=qa_status,
        conflict_status=conflict_status,
        source_date=None,
        evidence_date=None,
    )


def rec(*refs, eligibility="ELIGIBLE"):
    return SimpleNamespace(
        recommendation_id="R1",
        case_id="CASE1",
        product_id="P1",
        eligibility_status=eligibility,
        need_match_score=0.8,
        evidence_score=0.9,
        evidence_refs=__import__("json").dumps(list(refs)),
        warnings=__import__("json").dumps([]),
        exclusion_reasons="",
        ranking_reasons="Hydration need matched by supported evidence.",
    )


def test_approved_trace_is_supporting_and_pending_is_excluded():
    recommendation = rec("E1", "E2")
    result = RecommendationTrustTraceService(None).build(
        recommendation,
        evidences=[
            ev("E1", qa_status="APPROVED"),
            ev("E2", qa_status="PENDING"),
        ],
        case=SimpleNamespace(identified_needs="hydration"),
    )

    assert [item["evidence_id"] for item in result["supporting_evidence"]] == ["E1"]
    excluded = {item["evidence_id"]: item["exclusion_reason"] for item in result["excluded_evidence"]}
    assert excluded["E2"] == "QA_STATUS_PENDING"
    assert result["trace_integrity"]["status"] == "VALID"


def test_rejected_loser_never_returns_as_supporting():
    recommendation = rec("WINNER", "LOSER")
    result = RecommendationTrustTraceService(None).build(
        recommendation,
        evidences=[
            ev("WINNER", qa_status="APPROVED", conflict_status="NONE", claim="Winner claim"),
            ev("LOSER", qa_status="REJECTED", conflict_status="NONE", claim="Rejected loser"),
        ],
    )

    assert [item["evidence_id"] for item in result["supporting_evidence"]] == ["WINNER"]
    assert any(
        item["evidence_id"] == "LOSER"
        and item["exclusion_reason"] == "QA_STATUS_REJECTED"
        for item in result["excluded_evidence"]
    )


def test_unresolved_conflict_is_excluded_and_visible_as_warning():
    recommendation = rec("E1")
    result = RecommendationTrustTraceService(None).build(
        recommendation,
        evidences=[ev("E1", qa_status="APPROVED", conflict_status="CONFLICT")],
    )

    assert result["supporting_evidence"] == []
    assert result["excluded_evidence"][0]["exclusion_reason"] == "UNRESOLVED_CONFLICT"
    assert "Unresolved evidence conflict exists for this product." in result["warnings"]


def test_missing_reference_is_trace_integrity_failure():
    with pytest.raises(TrustTraceIntegrityError):
        RecommendationTrustTraceService(None).build(
            rec("MISSING"),
            evidences=[ev("E1")],
        )


def test_cross_product_reference_cannot_be_supporting():
    recommendation = rec("E2")
    result = RecommendationTrustTraceService(None).build(
        recommendation,
        evidences=[ev("E2", product_id="P2")],
    )

    assert result["supporting_evidence"] == []
    assert result["excluded_evidence"][0]["exclusion_reason"] == "CROSS_PRODUCT_REFERENCE"


def test_projection_does_not_change_recommendation_scoring_or_ranking():
    recommendation = rec("E1")
    before = (
        recommendation.need_match_score,
        recommendation.evidence_score,
        recommendation.ranking_score if hasattr(recommendation, "ranking_score") else None,
    )

    RecommendationTrustTraceService(None).build(
        recommendation,
        evidences=[ev("E1")],
    )

    after = (
        recommendation.need_match_score,
        recommendation.evidence_score,
        recommendation.ranking_score if hasattr(recommendation, "ranking_score") else None,
    )
    assert after == before
