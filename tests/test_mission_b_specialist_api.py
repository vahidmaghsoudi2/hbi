"""Mission B — API tests for Specialist Override & Feedback.

Covers:
- Case ownership enforcement
- Override does not mutate Recommendation
- Feedback + follow_up_at via API
- specialist_id ALWAYS from authenticated identity (client cannot forge)
- Auth required
"""
from datetime import datetime, timezone, timedelta

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.customer import Customer
from app.models.case import Case
from app.models.product import Product
from app.models.recommendation import Recommendation
from app.core.deps import get_db, get_current_customer_id


@pytest.fixture()
def api_client(db_session):
    def _override_db():
        try:
            yield db_session
        finally:
            pass

    def _override_customer():
        return "CUST-API-MB"

    app.dependency_overrides[get_db] = _override_db
    app.dependency_overrides[get_current_customer_id] = _override_customer

    db_session.add(Customer(customer_id="CUST-API-MB", name="API MB User", consent_to_store_data=1))
    db_session.flush()
    db_session.add(Case(case_id="CASE-API-MB", customer_id="CUST-API-MB", case_type="CONSULTATION"))
    db_session.add(Product(product_id="PROD-API-MB", brand="B", product_name="P", identity_status="VERIFIED"))
    db_session.flush()
    db_session.add(Recommendation(
        recommendation_id="rec_CASE-API-MB_PROD-API-MB",
        case_id="CASE-API-MB",
        product_id="PROD-API-MB",
        need_match_score=0.9,
        evidence_score=0.8,
        eligibility_status="ELIGIBLE",
        ranking_score=0.85,
        ranking_reasons="api-test",
    ))
    db_session.commit()

    with TestClient(app) as c:
        yield c, db_session

    app.dependency_overrides.clear()


def test_create_override_via_api_preserves_recommendation(api_client):
    client, db = api_client
    r = client.post("/api/v1/specialist/overrides", json={
        "recommendation_id": "rec_CASE-API-MB_PROD-API-MB",
        "case_id": "CASE-API-MB",
        "action": "REJECT",
        "reason": "Clinical note not reflected in engine output",
    })
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["action"] == "REJECT"
    assert body["original_eligibility"] == "ELIGIBLE"
    assert body["specialist_id"] == "CUST-API-MB"  # from auth only
    assert body["reason"]

    rec = db.get(Recommendation, "rec_CASE-API-MB_PROD-API-MB")
    assert rec.eligibility_status == "ELIGIBLE"
    assert rec.ranking_score == 0.85

    case = db.get(Case, "CASE-API-MB")
    assert case.operator_override == body["override_id"]


def test_forged_specialist_id_in_body_is_ignored(api_client):
    """Client-supplied specialist_id must not become the operator."""
    client, _ = api_client
    r = client.post("/api/v1/specialist/overrides", json={
        "recommendation_id": "rec_CASE-API-MB_PROD-API-MB",
        "case_id": "CASE-API-MB",
        "specialist_id": "FORGED-ATTACKER-ID",
        "action": "ACCEPT",
        "reason": "Attempting to forge operator identity",
    })
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["specialist_id"] == "CUST-API-MB"
    assert body["specialist_id"] != "FORGED-ATTACKER-ID"


def test_override_forbidden_for_other_customer_case(api_client):
    client, db = api_client
    db.add(Customer(customer_id="OTHER", name="Other", consent_to_store_data=1))
    db.flush()
    db.add(Case(case_id="CASE-OTHER", customer_id="OTHER"))
    db.commit()

    r = client.post("/api/v1/specialist/overrides", json={
        "recommendation_id": "rec_CASE-API-MB_PROD-API-MB",
        "case_id": "CASE-OTHER",
        "action": "ACCEPT",
        "reason": "should fail ownership",
    })
    assert r.status_code == 403


def test_create_and_list_feedback_via_api(api_client):
    client, _ = api_client
    r = client.post("/api/v1/specialist/feedback", json={
        "case_id": "CASE-API-MB",
        "source": "SPECIALIST",
        "outcome": "ACCEPTED",
        "comment": "Discussed with customer",
        "recommendation_id": "rec_CASE-API-MB_PROD-API-MB",
    })
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["source"] == "SPECIALIST"
    assert body["outcome"] == "ACCEPTED"

    listed = client.get("/api/v1/specialist/feedback/case/CASE-API-MB")
    assert listed.status_code == 200
    assert len(listed.json()) >= 1


def test_override_requires_reason_api(api_client):
    client, _ = api_client
    r = client.post("/api/v1/specialist/overrides", json={
        "recommendation_id": "rec_CASE-API-MB_PROD-API-MB",
        "case_id": "CASE-API-MB",
        "action": "ACCEPT",
        "reason": "",
    })
    assert r.status_code == 422


def test_api_full_path_override_then_feedback_with_follow_up(api_client):
    client, db = api_client
    follow_at = (datetime.now(timezone.utc) + timedelta(days=3)).isoformat()

    ovr = client.post("/api/v1/specialist/overrides", json={
        "recommendation_id": "rec_CASE-API-MB_PROD-API-MB",
        "case_id": "CASE-API-MB",
        "action": "ACCEPT",
        "reason": "Suitable after review",
    })
    assert ovr.status_code == 200, ovr.text
    ovr_body = ovr.json()
    assert ovr_body["specialist_id"] == "CUST-API-MB"
    assert ovr_body["original_eligibility"] == "ELIGIBLE"

    rec = db.get(Recommendation, "rec_CASE-API-MB_PROD-API-MB")
    assert rec.eligibility_status == "ELIGIBLE"

    fb = client.post("/api/v1/specialist/feedback", json={
        "case_id": "CASE-API-MB",
        "source": "SPECIALIST",
        "outcome": "FOLLOW_UP_NEEDED",
        "recommendation_id": "rec_CASE-API-MB_PROD-API-MB",
        "comment": "Call back in 3 days",
        "follow_up_at": follow_at,
    })
    assert fb.status_code == 200, fb.text
    fb_body = fb.json()
    assert fb_body["outcome"] == "FOLLOW_UP_NEEDED"
    assert fb_body["follow_up_at"] is not None

    overrides = client.get("/api/v1/specialist/overrides/case/CASE-API-MB")
    feedbacks = client.get("/api/v1/specialist/feedback/case/CASE-API-MB")
    assert overrides.status_code == 200
    assert feedbacks.status_code == 200
    assert len(overrides.json()) >= 1
    assert any(f.get("outcome") == "FOLLOW_UP_NEEDED" for f in feedbacks.json())
