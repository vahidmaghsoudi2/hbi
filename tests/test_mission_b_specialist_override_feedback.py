"""Mission B — Specialist Override & Feedback core behaviour.

- Override never mutates original Recommendation eligibility/ranking.
- Feedback is linked to Case (and optionally Recommendation).
- No scoring/weight changes.
"""
import pytest
from app.models.customer import Customer
from app.models.case import Case
from app.models.product import Product
from app.models.recommendation import Recommendation
from app.models.specialist_override import SpecialistOverride
from app.models.feedback import Feedback
from app.services.specialist_override_service import SpecialistOverrideService
from app.services.feedback_service import FeedbackService


def _seed(db):
    db.add(Customer(customer_id="CUST-MB1", name="Mission B User", consent_to_store_data=1))
    db.flush()
    db.add(Case(case_id="CASE-MB1", customer_id="CUST-MB1", case_type="CONSULTATION"))
    db.add(Product(product_id="PROD-MB1", brand="Brand", product_name="Test Product", identity_status="VERIFIED"))
    db.flush()
    rec = Recommendation(
        recommendation_id="rec_CASE-MB1_PROD-MB1",
        case_id="CASE-MB1",
        product_id="PROD-MB1",
        need_match_score=0.8,
        evidence_score=0.7,
        eligibility_status="ELIGIBLE",
        ranking_score=0.75,
        ranking_reasons="test",
    )
    db.add(rec)
    db.flush()
    return rec


def test_override_preserves_original_recommendation(db_session):
    rec = _seed(db_session)
    original_elig = rec.eligibility_status
    original_rank = rec.ranking_score

    svc = SpecialistOverrideService(db_session)
    ovr = svc.create_override(
        recommendation_id=rec.recommendation_id,
        case_id="CASE-MB1",
        specialist_id="SPEC-001",
        action="REJECT",
        reason="Customer has known sensitivity not captured in engine",
    )
    db_session.commit()

    # Original row unchanged
    refreshed = db_session.get(Recommendation, rec.recommendation_id)
    assert refreshed.eligibility_status == original_elig
    assert refreshed.ranking_score == original_rank

    # Override record holds snapshot
    assert ovr.original_eligibility == "ELIGIBLE"
    assert ovr.action == "REJECT"
    assert ovr.reason
    assert ovr.specialist_id == "SPEC-001"

    listed = svc.list_by_case("CASE-MB1")
    assert len(listed) == 1
    assert listed[0].override_id == ovr.override_id


def test_override_requires_reason(db_session):
    rec = _seed(db_session)
    svc = SpecialistOverrideService(db_session)
    with pytest.raises(ValueError, match="reason"):
        svc.create_override(
            recommendation_id=rec.recommendation_id,
            case_id="CASE-MB1",
            specialist_id="SPEC-001",
            action="ACCEPT",
            reason="",
        )


def test_feedback_linked_to_case_and_recommendation(db_session):
    rec = _seed(db_session)
    svc = FeedbackService(db_session)
    fb = svc.create_feedback(
        case_id="CASE-MB1",
        source="SPECIALIST",
        outcome="ACCEPTED",
        comment="Customer satisfied after override discussion",
        recommendation_id=rec.recommendation_id,
    )
    db_session.commit()

    assert fb.case_id == "CASE-MB1"
    assert fb.recommendation_id == rec.recommendation_id
    assert fb.source == "SPECIALIST"
    assert fb.outcome == "ACCEPTED"

    listed = svc.list_by_case("CASE-MB1")
    assert len(listed) == 1
