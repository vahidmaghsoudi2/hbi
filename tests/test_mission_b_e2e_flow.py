"""Mission B — Integrated business flow test.

Path proven:
  Customer + Case + Product + Recommendation (persisted)
  → Specialist Override (non-mutating)
  → Feedback / Follow-up

Does not invent Problem/Need/Decision entities.
Does not change scoring/weights. Issue #37 remains OPEN.
"""
from app.models.customer import Customer
from app.models.case import Case
from app.models.product import Product
from app.models.recommendation import Recommendation
from app.services.specialist_override_service import SpecialistOverrideService
from app.services.feedback_service import FeedbackService


def test_full_path_customer_case_rec_override_feedback(db_session):
    # 1. Customer
    db_session.add(Customer(customer_id="CUST-E2E-MB", name="E2E User", consent_to_store_data=1))
    db_session.flush()

    # 2. Case
    db_session.add(Case(case_id="CASE-E2E-MB", customer_id="CUST-E2E-MB", case_type="CONSULTATION"))
    db_session.flush()

    # 3. Product + Recommendation (simulates engine output already gated)
    db_session.add(Product(
        product_id="PROD-E2E-MB", brand="Brand", product_name="E2E Product",
        identity_status="VERIFIED",
    ))
    db_session.flush()
    rec = Recommendation(
        recommendation_id="rec_CASE-E2E-MB_PROD-E2E-MB",
        case_id="CASE-E2E-MB",
        product_id="PROD-E2E-MB",
        need_match_score=0.85,
        evidence_score=0.7,
        eligibility_status="ELIGIBLE",
        ranking_score=0.8,
        ranking_reasons="e2e-flow",
        evidence_refs="[]",
        warnings="[]",
    )
    db_session.add(rec)
    db_session.commit()

    original_elig = rec.eligibility_status
    original_rank = rec.ranking_score

    # 4. Specialist Override (audit only)
    ovr_svc = SpecialistOverrideService(db_session)
    ovr = ovr_svc.create_override(
        recommendation_id=rec.recommendation_id,
        case_id="CASE-E2E-MB",
        specialist_id="SPEC-E2E",
        action="ACCEPT",
        reason="Confirmed suitable after specialist review",
    )
    db_session.commit()

    refreshed = db_session.get(Recommendation, rec.recommendation_id)
    assert refreshed.eligibility_status == original_elig
    assert refreshed.ranking_score == original_rank
    assert ovr.original_eligibility == "ELIGIBLE"

    # 5. Feedback / Follow-up
    fb_svc = FeedbackService(db_session)
    fb = fb_svc.create_feedback(
        case_id="CASE-E2E-MB",
        source="SPECIALIST",
        outcome="ACCEPTED",
        recommendation_id=rec.recommendation_id,
        comment="Path complete",
    )
    db_session.commit()

    assert fb.case_id == "CASE-E2E-MB"
    assert fb.recommendation_id == rec.recommendation_id
    assert fb.outcome == "ACCEPTED"

    # Traceability: both lists non-empty for the case
    assert len(ovr_svc.list_by_case("CASE-E2E-MB")) == 1
    assert len(fb_svc.list_by_case("CASE-E2E-MB")) == 1
