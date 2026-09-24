"""Consultation Response Vertical Slice 001.

Customer -> owned Case -> existing Recommendation -> Customer Response
-> durable Feedback -> ownership-aware retrieval -> audit evidence.
"""
import pytest
from fastapi.testclient import TestClient

import app.api.routers.customers as customers_router
from app.core.deps import get_current_customer_id, get_db
from app.main import app
from app.models.case import Case
from app.models.customer import Customer
from app.models.product import Product
from app.models.recommendation import Recommendation


CUSTOMER_ID = "CUST-RESPONSE-001"
CASE_ID = "CASE-RESPONSE-001"
PRODUCT_ID = "PROD-RESPONSE-001"
REC_ID = "rec_CASE-RESPONSE-001_PROD-RESPONSE-001"


def _seed_owned_case_and_recommendation(db):
    db.add(Customer(customer_id=CUSTOMER_ID, name="Response User", consent_to_store_data=1))
    db.add(Customer(customer_id="CUST-OTHER-001", name="Other User", consent_to_store_data=1))
    db.flush()

    db.add(Case(case_id=CASE_ID, customer_id=CUSTOMER_ID, case_type="CONSULTATION"))
    db.add(Case(case_id="CASE-OTHER-001", customer_id="CUST-OTHER-001", case_type="CONSULTATION"))
    db.add(Product(product_id=PRODUCT_ID, brand="Test", product_name="Response Product", identity_status="VERIFIED"))
    db.flush()

    db.add(Recommendation(
        recommendation_id=REC_ID,
        case_id=CASE_ID,
        product_id=PRODUCT_ID,
        need_match_score=0.8,
        evidence_score=0.7,
        eligibility_status="ELIGIBLE",
        ranking_score=0.75,
        ranking_reasons="frozen recommendation fixture",
    ))
    db.flush()
    db.add(Recommendation(
        recommendation_id="rec_CASE-OTHER-001_PROD-RESPONSE-001",
        case_id="CASE-OTHER-001",
        product_id=PRODUCT_ID,
        need_match_score=0.8,
        evidence_score=0.7,
        eligibility_status="ELIGIBLE",
        ranking_score=0.75,
        ranking_reasons="other-case fixture",
    ))
    db.commit()


@pytest.fixture()
def authenticated_client(db_session):
    def override_db():
        yield db_session

    def override_customer():
        return CUSTOMER_ID

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_current_customer_id] = override_customer
    _seed_owned_case_and_recommendation(db_session)

    with TestClient(app) as client:
        yield client, db_session

    app.dependency_overrides.clear()


@pytest.fixture()
def unauthenticated_client(db_session):
    def override_db():
        yield db_session

    app.dependency_overrides[get_db] = override_db
    _seed_owned_case_and_recommendation(db_session)

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


def test_customer_response_requires_authentication(unauthenticated_client):
    response = unauthenticated_client.post(
        "/api/v1/customers/feedback",
        json={"case_id": CASE_ID, "recommendation_id": REC_ID, "outcome": "ACCEPTED"},
    )
    assert response.status_code == 401


def test_customer_response_creates_customer_feedback_and_audit(authenticated_client, monkeypatch):
    client, db = authenticated_client
    audit_events = []

    def capture_audit(event, **kwargs):
        audit_events.append((event, kwargs))

    monkeypatch.setattr(customers_router, "audit_event", capture_audit)

    response = client.post(
        "/api/v1/customers/feedback",
        json={
            "case_id": CASE_ID,
            "recommendation_id": REC_ID,
            "outcome": "ACCEPTED",
            "rating": "5",
            "comment": "Customer accepted the recommendation.",
        },
    )

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["source"] == "CUSTOMER"
    assert body["case_id"] == CASE_ID
    assert body["recommendation_id"] == REC_ID
    assert body["outcome"] == "ACCEPTED"

    assert len(audit_events) == 1
    event, kwargs = audit_events[0]
    assert event == "customer_feedback_created"
    assert kwargs["customer_id"] == CUSTOMER_ID
    assert kwargs["path"] == "/api/v1/customers/feedback"
    assert kwargs["extra"]["target"]["case_id"] == CASE_ID
    assert kwargs["extra"]["target"]["recommendation_id"] == REC_ID

    db.expire_all()
    feedback = client.get(f"/api/v1/customers/feedback/case/{CASE_ID}")
    assert feedback.status_code == 200
    rows = feedback.json()
    assert len(rows) == 1
    assert rows[0]["feedback_id"] == body["feedback_id"]
    assert rows[0]["source"] == "CUSTOMER"
    assert rows[0]["recommendation_id"] == REC_ID


def test_customer_response_rejects_other_case_ownership(authenticated_client):
    client, _ = authenticated_client
    response = client.post(
        "/api/v1/customers/feedback",
        json={
            "case_id": "CASE-OTHER-001",
            "recommendation_id": "rec_CASE-OTHER-001_PROD-RESPONSE-001",
            "outcome": "REJECTED",
        },
    )
    assert response.status_code == 403


def test_customer_response_missing_case_returns_404(authenticated_client):
    client, _ = authenticated_client
    response = client.post(
        "/api/v1/customers/feedback",
        json={
            "case_id": "CASE-MISSING-001",
            "recommendation_id": REC_ID,
            "outcome": "REJECTED",
        },
    )
    assert response.status_code == 404


def test_customer_response_rejects_missing_recommendation(authenticated_client):
    client, _ = authenticated_client
    response = client.post(
        "/api/v1/customers/feedback",
        json={
            "case_id": CASE_ID,
            "recommendation_id": "rec-MISSING-001",
            "outcome": "REJECTED",
        },
    )
    assert response.status_code == 422


def test_customer_response_rejects_cross_case_recommendation(authenticated_client):
    client, _ = authenticated_client
    response = client.post(
        "/api/v1/customers/feedback",
        json={
            "case_id": CASE_ID,
            "recommendation_id": "rec_CASE-OTHER-001_PROD-RESPONSE-001",
            "outcome": "REJECTED",
        },
    )
    assert response.status_code == 422
    assert "does not belong to the given case" in response.json()["detail"]


def test_customer_response_retrieval_is_ownership_aware(authenticated_client):
    client, db = authenticated_client
    response = client.post(
        "/api/v1/customers/feedback",
        json={"case_id": CASE_ID, "recommendation_id": REC_ID, "outcome": "PARTIAL"},
    )
    assert response.status_code == 201

    db.expire_all()
    owned = client.get(f"/api/v1/customers/feedback/case/{CASE_ID}")
    assert owned.status_code == 200
    assert owned.json()[0]["recommendation_id"] == REC_ID

    other_case = client.get("/api/v1/customers/feedback/case/CASE-OTHER-001")
    assert other_case.status_code == 403


def test_customer_response_endpoint_cannot_set_non_customer_source(authenticated_client):
    client, _ = authenticated_client
    response = client.post(
        "/api/v1/customers/feedback",
        json={
            "case_id": CASE_ID,
            "recommendation_id": REC_ID,
            "source": "SPECIALIST",
            "outcome": "ACCEPTED",
        },
    )
    assert response.status_code == 201
    assert response.json()["source"] == "CUSTOMER"
