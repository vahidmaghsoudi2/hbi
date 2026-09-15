"""HBI-RUNTIME-003 — only QA-approved Evidence contributes to Evidence Score."""
from types import SimpleNamespace

from app.services.recommendation_service import RecommendationService


def _evidence(source_type, qa_status):
    return SimpleNamespace(source_type=source_type, qa_status=qa_status)


def test_only_qa_approved_evidence_contributes_to_score():
    svc = RecommendationService.__new__(RecommendationService)
    evidences = [
        _evidence("PEER_REVIEWED", "APPROVED"),
        _evidence("PEER_REVIEWED", "PENDING"),
        _evidence("OFFICIAL_MANUFACTURER", "NEEDS_REVIEW"),
        _evidence("REGULATORY", "REJECTED"),
    ]

    assert svc._compute_evidence_score(evidences) == 1.0


def test_no_qa_approved_evidence_produces_zero_score():
    svc = RecommendationService.__new__(RecommendationService)
    evidences = [
        _evidence("PEER_REVIEWED", "PENDING"),
        _evidence("REGULATORY", "NEEDS_REVIEW"),
        _evidence("OFFICIAL_MANUFACTURER", "REJECTED"),
    ]

    assert svc._compute_evidence_score(evidences) == 0.0


def test_multiple_approved_evidence_uses_only_approved_denominator():
    svc = RecommendationService.__new__(RecommendationService)
    evidences = [
        _evidence("PEER_REVIEWED", "APPROVED"),
        _evidence("OFFICIAL_MANUFACTURER", "APPROVED"),
        _evidence("REPUTABLE_RETAILER", "PENDING"),
        _evidence("SECONDARY", "NEEDS_REVIEW"),
    ]

    # (1.0 + 0.6) / 2 approved Evidence rows
    assert svc._compute_evidence_score(evidences) == 0.8
