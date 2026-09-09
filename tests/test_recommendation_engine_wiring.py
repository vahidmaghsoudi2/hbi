"""WP-GATE63-A — RecommendationService orchestrates; scoring owned by MatchScoringEngine.

Finding: docs/09_gate_reports/GATE_6-2_6-3_REALITY_RESOLUTION_2026-09-07.md #4
Ownership: Service = assembly; MatchScoringEngine = input + final scores;
ReasoningEngine.run = decision path (unchanged contract).
"""
from __future__ import annotations

from app.models.evidence import Evidence
from app.models.inventory import Inventory
from app.models.product import Product
from app.models.product_knowledge import ProductKnowledge
from app.reasoning.scoring import MatchScoringEngine
from app.services.recommendation_service import RecommendationService


def _seed_verified_product(db, pid="P_G63A_001"):
    p = Product(
        product_id=pid,
        brand="BrandX",
        product_name="Daily Sunscreen SPF50",
        identity_status="VERIFIED",
        qa_verdict="VALID",
        status="ACTIVE",
    )
    db.add(p)
    db.flush()

    db.add(
        Inventory(
            inventory_id=f"INV-{pid}",
            product_id=pid,
            quantity_available=5,
            quantity_reserved=0,
            stock_status="AVAILABLE",
            sale_price_toman=100000,
        )
    )
    db.add(
        ProductKnowledge(
            product_knowledge_id=f"PK-{pid}",
            product_id=pid,
            known_use_cases="daily sun protection, face sunscreen",
            claimed_benefits="UV protection",
        )
    )
    db.add(
        Evidence(
            evidence_id=f"EV-{pid}-1",
            product_id=pid,
            claim_id=f"EV-{pid}-001",
            source_type="PEER_REVIEWED",
            source_reference="DOI-TEST",
            claim="Protects against UV",
            claim_type="FACT",
            field="claimed_benefits",
            evidence_status="SUPPORTED",
            conflict_status="NONE",
            qa_status="VERIFIED",
        )
    )
    db.flush()
    return p


def test_generate_calls_reasoning_engine(db_session, monkeypatch):
    _seed_verified_product(db_session)
    svc = RecommendationService(db_session)
    calls = []
    original = svc.reasoning_engine.run

    def _spy(*args, **kwargs):
        calls.append(kwargs)
        return original(*args, **kwargs)

    monkeypatch.setattr(svc.reasoning_engine, "run", _spy)

    recs = svc.generate_recommendations(
        "CASE_G63A", {"concerns": "daily sun protection"}
    )
    assert len(calls) == 1
    assert calls[0]["product_id"] == "P_G63A_001"
    assert calls[0]["need_match"] is not None
    assert calls[0]["evidence_score"] is not None
    assert calls[0]["inventory_score"] is not None
    assert len(recs) == 1


def test_generate_scores_not_hardcoded_stub_values(db_session):
    """Regression: historical stub always set 0.8 / 0.7 / 0.9."""
    _seed_verified_product(db_session, "P_G63A_002")
    svc = RecommendationService(db_session)
    recs = svc.generate_recommendations(
        "CASE_G63A2", {"concerns": "daily sun protection"}
    )
    assert len(recs) == 1
    rec = recs[0]
    stub_triple = (
        rec.need_match_score == 0.8
        and rec.evidence_score == 0.7
        and rec.ranking_score == 0.9
    )
    assert not stub_triple
    assert rec.ranking_reasons
    assert "ReasoningEngine" in (rec.ranking_reasons or "")
    assert rec.eligibility_status in (
        "ELIGIBLE",
        "INELIGIBLE_PENDING_VERIFICATION",
        "INELIGIBLE_CONFLICT",
        "INELIGIBLE_PENDING_REVIEW",
        "INELIGIBLE_OUT_OF_STOCK",
    )


def test_schema_map_out_of_stock():
    svc = RecommendationService.__new__(RecommendationService)
    status = svc._map_eligibility_to_schema(
        {"eligibility": "ELIGIBLE", "conflicts": []}, 0.0
    )
    assert status == "INELIGIBLE_OUT_OF_STOCK"


def test_match_scoring_engine_owns_input_scores():
    """Traceability: input scores come from MatchScoringEngine, not Service."""
    scorer = MatchScoringEngine()
    need = scorer.score_need_match(
        ["daily sun protection"],
        product_name="Daily Sunscreen SPF50",
        known_use_cases="daily sun protection, face sunscreen",
    )
    assert need > 0.0
    evidence = scorer.score_evidence_from_source_types(["PEER_REVIEWED"])
    assert evidence == 1.0
    inv = scorer.score_inventory(quantity_available=5, stock_status="AVAILABLE")
    assert inv == 1.0
    inv0 = scorer.score_inventory(quantity_available=0, stock_status="AVAILABLE")
    assert inv0 == 0.0


def test_calculate_unchanged_contract():
    """MatchScoringEngine.calculate formula contract preserved."""
    scorer = MatchScoringEngine()
    out = scorer.calculate(need_match=0.8, evidence_score=0.9, inventory_score=1.0)
    assert "final_score" in out
    assert "eligibility" in out
    assert out["hard_gate_triggered"] is False
