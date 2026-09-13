"""GAP-03: Out-of-Stock Candidate Elimination (HBI-PO-DEC-GAP03-001 Option A).

Inventory = 0 → eliminated before Reasoning → no Ranking → no Recommendation object.
"""
from unittest.mock import MagicMock

from app.services.recommendation_service import RecommendationService


def _make_svc():
    db = MagicMock()
    svc = RecommendationService(db)
    svc.product_repo = MagicMock()
    svc.inventory_repo = MagicMock()
    svc.pk_repo = MagicMock()
    svc.evidence_repo = MagicMock()
    svc.reasoning_engine = MagicMock()
    return svc


def _product(pid):
    p = MagicMock()
    p.product_id = pid
    return p


def test_oos_product_eliminated_before_reasoning_and_no_recommendation():
    svc = _make_svc()
    svc.product_repo.find_by_identity_status_and_active.return_value = [
        _product("PROD_OOS"),
        _product("PROD_IN_STOCK"),
    ]
    svc.pk_repo.find_by_product.return_value = MagicMock(known_use_cases="dry skin")
    svc.evidence_repo.find_by_product.return_value = []

    def inv_side_effect(product_id):
        inv = MagicMock()
        if product_id == "PROD_OOS":
            inv.quantity_available = 0
        else:
            inv.quantity_available = 3
        return inv

    svc.inventory_repo.find_by_product.side_effect = inv_side_effect
    svc.reasoning_engine.run.return_value = {
        "unknowns": [],
        "conflicts": [],
        "claim_boundary_violations": [],
        "eligibility": "ELIGIBLE",
        "final_score": 0.8,
        "rationale": "ok",
    }

    recs = svc.generate_recommendations("CASE1", {"concerns": "dry skin"})

    product_ids = [r.product_id for r in recs]
    assert "PROD_OOS" not in product_ids
    assert "PROD_IN_STOCK" in product_ids

    called_pids = [
        c.kwargs.get("product_id") for c in svc.reasoning_engine.run.call_args_list
    ]
    assert "PROD_OOS" not in called_pids
    assert "PROD_IN_STOCK" in called_pids


def test_all_oos_yields_empty_recommendations_and_no_reasoning():
    svc = _make_svc()
    svc.product_repo.find_by_identity_status_and_active.return_value = [
        _product("P1"),
        _product("P2"),
    ]
    inv = MagicMock()
    inv.quantity_available = 0
    svc.inventory_repo.find_by_product.return_value = inv

    recs = svc.generate_recommendations("CASE1", {"concerns": "dry skin"})
    assert recs == []
    assert svc.reasoning_engine.run.call_count == 0
