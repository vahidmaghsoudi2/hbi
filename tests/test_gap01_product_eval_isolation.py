"""GAP-01: Product Evaluation State isolation tests.

HBI-PO-DEC-GAP01-001:
- Product-level Unknown/Conflict must not mutate shared Case Decision State
- Unknown of Product A must not affect Eligibility of Product B via shared state
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


def test_product_unknowns_do_not_mutate_case_decision_state():
    svc = _make_svc()
    svc.product_repo.find_by_identity_status_and_active.return_value = [
        _product("PROD_A"),
        _product("PROD_B"),
    ]
    svc.pk_repo.find_by_product.return_value = MagicMock(known_use_cases="dry skin")
    svc.evidence_repo.find_by_product.return_value = []
    inv = MagicMock()
    inv.quantity_available = 5
    svc.inventory_repo.find_by_product.return_value = inv

    def engine_side_effect(**kwargs):
        pid = kwargs.get("product_id")
        if pid == "PROD_A":
            return {
                "unknowns": [{"field": "ingredient_x", "severity": "CRITICAL", "action": "ESCALATE", "notes": "missing"}],
                "conflicts": [{"id": "c1"}],
                "claim_boundary_violations": [],
                "eligibility": "NEEDS_REVIEW",
                "final_score": 0.1,
                "rationale": "A critical unknown",
            }
        return {
            "unknowns": [],
            "conflicts": [],
            "claim_boundary_violations": [],
            "eligibility": "ELIGIBLE",
            "final_score": 0.9,
            "rationale": "B clean",
        }

    svc.reasoning_engine.run.side_effect = engine_side_effect

    # Capture decision_state mutations by wrapping generate path indirectly:
    # after generate, case-level unknowns must still be empty (no product leakage).
    # We assert via eligibility isolation + by re-building and checking map with empty case unknowns.

    recs = svc.generate_recommendations("CASE1", {"concerns": "dry skin"})
    assert len(recs) == 2

    by_id = {r.product_id: r for r in recs}
    # PROD_A has critical product unknown → pending review
    assert by_id["PROD_A"].eligibility_status == "INELIGIBLE_PENDING_REVIEW"
    # PROD_B must NOT inherit PROD_A critical unknown via shared Case Decision State
    # (need_match may still gate; ensure engine ELIGIBLE path is reachable for B)
    assert by_id["PROD_B"].eligibility_status == "ELIGIBLE"


def test_map_eligibility_uses_product_unknowns_not_shared_accumulation():
    svc = _make_svc()
    decision_state = {
        "unknowns": [],  # case-level clean
        "needs": ["dry skin"],
        "medical_context_active": False,
        "decision_status": "READY",
    }
    engine_ok = {"eligibility": "ELIGIBLE"}
    product_critical = [{"unknown_priority": "CRITICAL_UNKNOWN", "field": "x"}]

    # Product-critical alone → pending
    assert svc._map_eligibility(engine_ok, decision_state, 0.5, product_unknowns=product_critical) == (
        "INELIGIBLE_PENDING_REVIEW"
    )
    # No product unknowns, clean engine → eligible
    assert svc._map_eligibility(engine_ok, decision_state, 0.5, product_unknowns=[]) == "ELIGIBLE"
    # Case-level critical still applies
    ds_case_critical = {
        **decision_state,
        "unknowns": [{"unknown_priority": "CRITICAL_UNKNOWN", "field": "skin_type"}],
    }
    assert svc._map_eligibility(engine_ok, ds_case_critical, 0.5, product_unknowns=[]) == (
        "INELIGIBLE_PENDING_REVIEW"
    )
