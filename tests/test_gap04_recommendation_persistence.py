"""GAP-04: Current Recommendation Persistence + Uniqueness (Option B)."""
import json
import pytest
from unittest.mock import MagicMock
from types import SimpleNamespace

from app.models.customer import Customer
from app.models.case import Case
from app.models.product import Product
from app.models.recommendation import Recommendation
from app.services.recommendation_service import RecommendationService
from app.services.skin_next_question_service import SkinNextQuestionService


def _seed_case_and_products(db, product_ids):
    db.add(Customer(customer_id="CUST1", name="Test", consent_to_store_data=1))
    db.flush()
    case = Case(case_id="CASE1", customer_id="CUST1", case_type="OPEN")
    db.add(case)
    db.flush()
    SkinNextQuestionService(db).capture_answer(
        case, "skin.primary_need.v1", "hydration"
    )
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
    svc._has_minimum_consultation_evidence = MagicMock(return_value=True)
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
    svc.evidence_repo.find_by_product.return_value = [MagicMock(qa_status="APPROVED", conflict_status="NONE", source_type="PEER_REVIEWED")]
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
    svc.evidence_repo.find_by_product.return_value = [MagicMock(qa_status="APPROVED", conflict_status="NONE", source_type="PEER_REVIEWED")]
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
    svc.evidence_repo.find_by_product.return_value = [MagicMock(qa_status="APPROVED", conflict_status="NONE", source_type="PEER_REVIEWED")]
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


def test_evaluated_ineligible_candidate_is_persisted_with_reason_and_survives_regeneration(db_session):
    import json

    _seed_case_and_products(db_session, ["PROD_REJECTED"])
    svc = _svc_with_real_db(db_session)
    p = MagicMock()
    p.product_id = "PROD_REJECTED"
    svc.product_repo.find_by_identity_status_and_active.return_value = [p]
    inv = MagicMock()
    inv.quantity_available = 2
    svc.inventory_repo.find_by_product.return_value = inv
    svc.pk_repo.find_by_product.return_value = MagicMock(known_use_cases="dry skin")
    svc.evidence_repo.find_by_product.return_value = [
        MagicMock(qa_status="PENDING", conflict_status="NONE", source_type="SECONDARY", evidence_id="EV-PENDING")
    ]
    svc.reasoning_engine.run.return_value = {
        "unknowns": [], "conflicts": [], "claim_boundary_violations": [],
        "final_score": 0.0, "rationale": "evidence not approved",
        "evidence_refs": ["EV-PENDING"], "warnings": ["Evidence requires QA"],
    }

    first = svc.generate_recommendations("CASE1", {"concerns": "dry skin"})
    assert first == []
    row = db_session.query(Recommendation).filter_by(case_id="CASE1", product_id="PROD_REJECTED").one()
    first_id = row.recommendation_id
    assert row.eligibility_status == "INELIGIBLE_PENDING_REVIEW"
    assert json.loads(row.exclusion_reasons) == ["NO_APPROVED_EVIDENCE"]
    persisted_warnings = json.loads(row.warnings)
    assert persisted_warnings[0] == "Evidence requires QA"
    assert any("اطلاعات ناقص محصول" in warning for warning in persisted_warnings)
    assert json.loads(row.evidence_refs) == ["EV-PENDING"]

    second = svc.generate_recommendations("CASE1", {"concerns": "dry skin"})
    assert second == []
    rows = db_session.query(Recommendation).filter_by(case_id="CASE1", product_id="PROD_REJECTED").all()
    assert len(rows) == 1
    assert rows[0].recommendation_id == first_id
    assert json.loads(rows[0].exclusion_reasons) == ["NO_APPROVED_EVIDENCE"]


def test_evaluated_ineligible_candidate_records_first_gate_without_changing_status(db_session):
    import json

    _seed_case_and_products(db_session, ["PROD_MEDICAL"])
    svc = _svc_with_real_db(db_session)
    p = MagicMock()
    p.product_id = "PROD_MEDICAL"
    svc.product_repo.find_by_identity_status_and_active.return_value = [p]
    inv = MagicMock()
    inv.quantity_available = 1
    svc.inventory_repo.find_by_product.return_value = inv
    svc.pk_repo.find_by_product.return_value = MagicMock(known_use_cases="dry skin")
    svc.evidence_repo.find_by_product.return_value = []
    svc.reasoning_engine.run.return_value = {
        "unknowns": [], "conflicts": [], "claim_boundary_violations": [],
        "final_score": 0.0, "rationale": "medical context gate",
    }

    recs = svc.generate_recommendations("CASE1", {"concerns": "نیاز به پزشک"})
    assert recs == []
    row = db_session.query(Recommendation).filter_by(case_id="CASE1", product_id="PROD_MEDICAL").one()
    assert row.eligibility_status == "INELIGIBLE_PENDING_REVIEW"
    assert json.loads(row.exclusion_reasons) == ["MEDICAL_CONTEXT_REVIEW_REQUIRED"]



def _run_candidate_with_pk_gaps(db_session, missing_fields):
    import json

    _seed_case_and_products(db_session, ["PROD_PK_GAP"])
    svc = _svc_with_real_db(db_session)
    product = MagicMock()
    product.product_id = "PROD_PK_GAP"
    product.market_region = "EU"
    svc.product_repo.find_by_identity_status_and_active.return_value = [product]
    svc.inventory_repo.find_by_product.return_value = SimpleNamespace(
        quantity_available=3, quantity_reserved=0, stock_status="AVAILABLE"
    )

    pk_values = {
        "product_id": "PROD_PK_GAP",
        "market_region": "EU",
        "ingredients": "glycerin",
        "known_use_cases": "dry skin",
        "claimed_benefits": "hydrating",
        "usage_instructions": "apply daily",
        "contraindications": "avoid eye area",
        "evidence_refs": '["claim-1"]',
        "domain_evidence_status": json.dumps({
            "ingredients": "SUPPORTED",
            "known_use_cases": "SUPPORTED",
            "usage_instructions": "SUPPORTED",
            "contraindications": "SUPPORTED",
        }),
    }
    for field in missing_fields:
        pk_values[field] = None
    svc.pk_repo.find_by_product.return_value = SimpleNamespace(**pk_values)
    svc.evidence_repo.find_by_product.return_value = [SimpleNamespace(
        evidence_id="EV-PK-GAP",
        claim_id="claim-1",
        product_id="PROD_PK_GAP",
        market_region="EU",
        field="ingredients",
        claim_type="FACT",
        source_reference="synthetic://evidence",
        source_type="PEER_REVIEWED",
        evidence_strength="HIGH",
        qa_status="APPROVED",
        claim="glycerin",
        conflict_status="NONE",
    )]
    svc.reasoning_engine.run.return_value = {
        "unknowns": [], "conflicts": [], "claim_boundary_violations": [],
        "eligibility": "ELIGIBLE", "final_score": 0.85, "rationale": "synthetic eligible",
        "evidence_refs": ["EV-PK-GAP"], "warnings": [],
    }
    recs = svc.generate_recommendations("CASE1", {"concerns": "dry skin"})
    return recs


def test_t1_one_missing_pk_domain_keeps_candidate_and_discloses_gap(db_session):
    recs = _run_candidate_with_pk_gaps(db_session, ["ingredients"])
    assert len(recs) == 1
    assert recs[0].eligibility_status == "ELIGIBLE"
    warnings = json.loads(recs[0].warnings)
    assert any("ترکیبات" in warning for warning in warnings)
    assert "pk_completeness=partial" in recs[0].ranking_reasons
    assert '"ingredients"' in recs[0].ranking_reasons


def test_t2_two_missing_pk_domains_keep_candidate_and_return_warnings(db_session):
    recs = _run_candidate_with_pk_gaps(
        db_session, ["ingredients", "usage_instructions"]
    )
    assert len(recs) == 1
    assert recs[0].eligibility_status == "ELIGIBLE"
    warnings = json.loads(recs[0].warnings)
    assert any("ترکیبات" in warning for warning in warnings)
    assert any("دستور مصرف" in warning for warning in warnings)
    assert "pk_missing_domains=" in recs[0].ranking_reasons


def test_t3_absent_pk_record_keeps_candidate_with_explicit_severe_warning(db_session):
    import json

    _seed_case_and_products(db_session, ["PROD_NO_PK"])
    svc = _svc_with_real_db(db_session)
    product = MagicMock()
    product.product_id = "PROD_NO_PK"
    product.market_region = "EU"
    svc.product_repo.find_by_identity_status_and_active.return_value = [product]
    svc.inventory_repo.find_by_product.return_value = SimpleNamespace(
        quantity_available=2, quantity_reserved=0, stock_status="AVAILABLE"
    )
    svc.pk_repo.find_by_product.return_value = None
    svc.evidence_repo.find_by_product.return_value = [SimpleNamespace(
        evidence_id="EV-NO-PK", claim_id="claim-1", product_id="PROD_NO_PK",
        market_region="EU", field="ingredients", claim_type="FACT",
        source_reference="synthetic://evidence", source_type="PEER_REVIEWED",
        evidence_strength="HIGH", qa_status="APPROVED", claim="glycerin",
        conflict_status="NONE",
    )]
    svc.reasoning_engine.run.return_value = {
        "unknowns": [], "conflicts": [], "claim_boundary_violations": [],
        "eligibility": "ELIGIBLE", "final_score": 0.8, "rationale": "synthetic eligible",
        "evidence_refs": ["EV-NO-PK"], "warnings": [],
    }
    recs = svc.generate_recommendations("CASE1", {"concerns": "dry skin"})
    assert len(recs) == 1
    warnings = json.loads(recs[0].warnings)
    assert any("هشدار جدی PK" in warning for warning in warnings)
    assert "contraindications_unreviewed=True" in recs[0].ranking_reasons
