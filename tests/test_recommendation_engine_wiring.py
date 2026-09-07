"""WP-GATE63-A — RecommendationService must call ReasoningEngine (no hardcoded scores).

Finding reference:
docs/09_gate_reports/GATE_6-2_6-3_REALITY_RESOLUTION_2026-09-07.md item #4
"""
from __future__ import annotations

import pytest

from app.models.evidence import Evidence
from app.models.inventory import Inventory
from app.models.product import Product
from app.models.product_knowledge import ProductKnowledge
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
    db.flush()  # ensure Product PK exists before Inventory/Evidence FKs

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
    """Regression: previous stub always set 0.8 / 0.7 / 0.9."""
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


def test_out_of_stock_maps_eligibility(db_session):
    svc = RecommendationService(db_session)
    status = svc._map_eligibility({"eligibility": "ELIGIBLE", "conflicts": []}, 0.0)
    assert status == "INELIGIBLE_OUT_OF_STOCK"
