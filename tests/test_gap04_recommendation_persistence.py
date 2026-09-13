"""GAP-04: Current Recommendation Persistence + Uniqueness (Option B)."""
import pytest
from unittest.mock import MagicMock

from app.models.customer import Customer
from app.models.case import Case
from app.models.product import Product
from app.models.recommendation import Recommendation
from app.services.recommendation_service import RecommendationService


def _seed_case_and_products(db, product_ids):
    db.add(Customer(customer_id="CUST1", name="Test", consent_to_store_data=1))
    db.flush()
    db.add(Case(case_id="CASE1", customer_id="CUST1", case_type="OPEN"))
    for pid in product_ids:
        db.add(
            Product(
                product_id=pid,
                brand="Brand",
                product_name=pid,
                identity_status="VERIFIED",
            )
        )
    db.flush()


def _svc_with_real_db(db):
    svc = RecommendationService(db)
    svc.product_repo = MagicMock()
    svc.inventory_repo = MagicMock()
    svc.pk_repo = MagicMock()
    svc.evidence_repo = MagicMock()
    svc.reasoning_engine = MagicMock()
    return svc


def test_first_generate_creates_one_persisted_recommendation(db_session):
    _seed_case_and_products(db_session, ["PROD1"])
    svc = _svc_with_real_db(db_session)
    p = MagicMock()
    p.product_id = "PROD1"
    svc.product_repo.find_by_identity_status_and_active.return_value = [p]
    inv = MagicMock()
    inv.quantity_available = 2
    svc.inventory_repo.find_by_product.return_value = inv
    svc.pk_repo.find_by_product.return_value = MagicMock(known_use_cases="dry skin")
    svc.evidence_repo.find_by_product.return_value = []
    svc.reasoning_engine.run.return_value = {
        "unknowns": [], "conflicts": [], "claim_boundary_violations": [],
        "eligibility": "ELIGIBLE", "final_score": 0.85, "rationale": "ok",
    }
    recs = svc.generate_recommendations("CASE1", {"concerns": "dry skin"})
    assert len(recs) == 1
    assert recs[0].recommendation_id == "rec_CASE1_PROD1"
    rows = db_session.query(Recommendation).filter_by(case_id="CASE1", product_id="PROD1").all()
    assert len(rows) == 1
    assert rows[0].ranking_score == 0.85


def test_second_generate_updates_same_row_count_remains_one(db_session):
    _seed_case_and_products(db_session, ["PROD1"])
    svc = _svc_with_real_db(db_session)
    p = MagicMock()
    p.product_id = "PROD1"
    svc.product_repo.find_by_identity_status_and_active.return_value = [p]
    inv = MagicMock()
    inv.quantity_available = 2
    svc.inventory_repo.find_by_product.return_value = inv
    svc.pk_repo.find_by_product.return_value = MagicMock(known_use_cases="dry skin")
    svc.evidence_repo.find_by_product.return_value = []
    svc.reasoning_engine.run.return_value = {
        "unknowns": [], "conflicts": [], "claim_boundary_violations": [],
        "eligibility": "ELIGIBLE", "final_score": 0.5, "rationale": "first",
    }
    first = svc.generate_recommendations("CASE1", {"concerns": "dry skin"})
    first_id = first[0].recommendation_id
    svc.reasoning_engine.run.return_value = {
        "unknowns": [], "conflicts": [], "claim_boundary_violations": [],
        "eligibility": "ELIGIBLE", "final_score": 0.95, "rationale": "second",
    }
    second = svc.generate_recommendations("CASE1", {"concerns": "dry skin"})
    assert second[0].recommendation_id == first_id
    assert second[0].ranking_score == 0.95
    assert db_session.query(Recommendation).filter_by(case_id="CASE1", product_id="PROD1").count() == 1


def test_two_products_yield_two_recommendations(db_session):
    _seed_case_and_products(db_session, ["PROD1", "PROD2"])
    svc = _svc_with_real_db(db_session)
    products = []
    for pid in ["PROD1", "PROD2"]:
        p = MagicMock()
        p.product_id = pid
        products.append(p)
    svc.product_repo.find_by_identity_status_and_active.return_value = products
    inv = MagicMock()
    inv.quantity_available = 1
    svc.inventory_repo.find_by_product.return_value = inv
    svc.pk_repo.find_by_product.return_value = MagicMock(known_use_cases="dry skin")
    svc.evidence_repo.find_by_product.return_value = []
    svc.reasoning_engine.run.return_value = {
        "unknowns": [], "conflicts": [], "claim_boundary_violations": [],
        "eligibility": "ELIGIBLE", "final_score": 0.7, "rationale": "ok",
    }
    recs = svc.generate_recommendations("CASE1", {"concerns": "dry skin"})
    assert len(recs) == 2
    assert db_session.query(Recommendation).filter_by(case_id="CASE1").count() == 2


def test_unique_constraint_rejects_duplicate_case_product(db_session):
    _seed_case_and_products(db_session, ["PROD1"])
    db_session.add(Recommendation(
        recommendation_id="rec_CASE1_PROD1", case_id="CASE1", product_id="PROD1",
        need_match_score=0.5, eligibility_status="ELIGIBLE",
    ))
    db_session.flush()
    db_session.add(Recommendation(
        recommendation_id="rec_CASE1_PROD1_dup", case_id="CASE1", product_id="PROD1",
        need_match_score=0.1, eligibility_status="ELIGIBLE",
    ))
    with pytest.raises(Exception):
        db_session.flush()
    db_session.rollback()


def test_gap03_oos_still_creates_no_recommendation(db_session):
    _seed_case_and_products(db_session, ["PROD_OOS"])
    svc = _svc_with_real_db(db_session)
    p = MagicMock()
    p.product_id = "PROD_OOS"
    svc.product_repo.find_by_identity_status_and_active.return_value = [p]
    inv = MagicMock()
    inv.quantity_available = 0
    svc.inventory_repo.find_by_product.return_value = inv
    recs = svc.generate_recommendations("CASE1", {"concerns": "dry skin"})
    assert recs == []
    assert db_session.query(Recommendation).count() == 0
    assert svc.reasoning_engine.run.call_count == 0
