import json
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from app.interface.dto import RecommendationDTO
from app.interface.facades import _to_recommendation_dto
from app.services.recommendation_service import RecommendationService


def _service():
    db = MagicMock()
    service = RecommendationService(db)
    service.product_repo = MagicMock()
    service.inventory_repo = MagicMock()
    service.pk_repo = MagicMock()
    service.evidence_repo = MagicMock()
    service.reasoning_engine = MagicMock()
    return service, db


def test_hard_gated_candidate_is_not_persisted_or_ranked():
    service, db = _service()
    product = SimpleNamespace(product_id="P1")
    service.product_repo.find_by_identity_status_and_active.return_value = [product]
    service.repository.find_by_case.return_value = []
    service.pk_repo.find_by_product.return_value = SimpleNamespace(known_use_cases="dry skin")
    service.inventory_repo.find_by_product.return_value = SimpleNamespace(quantity_available=1)
    service.evidence_repo.find_by_product.return_value = []
    service.reasoning_engine.run.return_value = {
        "evidence_refs": [],
        "warnings": ["EVIDENCE_MISSING"],
        "unknowns": [],
        "conflicts": [],
        "claim_boundary_violations": [],
        "eligibility": "NEEDS_REVIEW",
        "final_score": 0.6,
        "rationale": "hard gate",
    }

    result = service.generate_recommendations("CASE1", {"concerns": "dry skin"})

    assert result == []
    service.repository.create.assert_not_called()
    db.delete.assert_not_called()


def test_eligible_recommendation_persists_trace():
    service, db = _service()
    product = SimpleNamespace(product_id="P1")
    evidence = SimpleNamespace(
        evidence_id="E1", claim_id="C1", field="known_use_cases",
        claim_type="FACT", source_reference="source-1", source_type="PEER_REVIEWED",
        evidence_strength="HIGH", qa_status="APPROVED", claim="dry skin",
        conflict_status="NONE",
    )
    service.product_repo.find_by_identity_status_and_active.return_value = [product]
    service.repository.find_by_case.return_value = []
    service.pk_repo.find_by_product.return_value = SimpleNamespace(known_use_cases="dry skin")
    service.inventory_repo.find_by_product.return_value = SimpleNamespace(quantity_available=1)
    service.evidence_repo.find_by_product.return_value = [evidence]
    service.reasoning_engine.run.return_value = {
        "evidence_refs": [{"evidence_id": "E1", "qa_status": "APPROVED"}],
        "warnings": ["TRACE_WARNING"],
        "unknowns": [],
        "conflicts": [],
        "claim_boundary_violations": [],
        "eligibility": "ELIGIBLE",
        "final_score": 0.9,
        "rationale": "eligible",
    }
    service.repository.create.return_value = MagicMock(product_id="P1", ranking_score=0.9)

    result = service.generate_recommendations("CASE1", {"concerns": "dry skin"})

    assert len(result) == 1
    kwargs = service.repository.create.call_args.kwargs
    assert json.loads(kwargs["evidence_refs"])[0]["evidence_id"] == "E1"
    assert json.loads(kwargs["warnings"]) == ["TRACE_WARNING"]


def test_recommendation_dto_exposes_persisted_trace():
    recommendation = SimpleNamespace(
        recommendation_id="R1", case_id="CASE1", product_id="P1",
        need_match_score=0.8, evidence_score=0.9, eligibility_status="ELIGIBLE",
        ranking_score=0.85, ranking_reasons="eligible",
        evidence_refs=json.dumps([{"evidence_id": "E1"}]),
        warnings=json.dumps(["TRACE_WARNING"]),
    )
    with patch("app.interface.facades._get_availability", return_value="AVAILABLE"), patch("app.interface.facades._get_price", return_value=100):
        dto = _to_recommendation_dto(recommendation, MagicMock())

    assert isinstance(dto, RecommendationDTO)
    assert dto.evidence_refs == [{"evidence_id": "E1"}]
    assert dto.warnings == ["TRACE_WARNING"]
