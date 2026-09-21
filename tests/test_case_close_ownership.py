"""CASE-CLOSE AUTHORIZATION OWNERSHIP — Team 2 P0 security fix.

POST /api/v1/cases/{case_id}/close must enforce:
- owner → 200
- other customer → 403
- missing/invalid auth → 401
- missing case → 404
"""
from __future__ import annotations

from app.core.auth import create_access_token
from app.models.case import Case
from app.models.customer import Customer


def _auth(customer_id: str) -> dict:
    return {"Authorization": f"Bearer {create_access_token({'sub': customer_id})}"}


def _seed_two_customers_and_case(db_session):
    db_session.add(Customer(customer_id="CUST-CLOSE-A", name="Owner", consent_to_store_data=1))
    db_session.add(Customer(customer_id="CUST-CLOSE-B", name="Other", consent_to_store_data=1))
    db_session.flush()
    db_session.add(
        Case(case_id="CASE-CLOSE-A", customer_id="CUST-CLOSE-A", case_type="OPEN")
    )
    db_session.flush()


def test_owner_close_returns_200(client, db_session):
    _seed_two_customers_and_case(db_session)
    r = client.post(
        "/api/v1/cases/CASE-CLOSE-A/close",
        headers=_auth("CUST-CLOSE-A"),
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body.get("case_id") == "CASE-CLOSE-A"
    assert body.get("customer_id") == "CUST-CLOSE-A"
    case = db_session.get(Case, "CASE-CLOSE-A")
    assert case is not None
    assert case.case_type == "CLOSED"


def test_other_customer_close_returns_403(client, db_session):
    _seed_two_customers_and_case(db_session)
    r = client.post(
        "/api/v1/cases/CASE-CLOSE-A/close",
        headers=_auth("CUST-CLOSE-B"),
    )
    assert r.status_code == 403, r.text
    assert "Access denied" in r.text
    case = db_session.get(Case, "CASE-CLOSE-A")
    assert case is not None
    assert case.case_type == "OPEN"


def test_unauthenticated_close_returns_401(client, db_session):
    _seed_two_customers_and_case(db_session)
    r = client.post("/api/v1/cases/CASE-CLOSE-A/close")
    assert r.status_code in (401, 403), r.text
    case = db_session.get(Case, "CASE-CLOSE-A")
    assert case is not None
    assert case.case_type == "OPEN"


def test_missing_case_returns_404(client, db_session):
    db_session.add(Customer(customer_id="CUST-CLOSE-A", name="Owner", consent_to_store_data=1))
    db_session.flush()
    r = client.post(
        "/api/v1/cases/CASE-DOES-NOT-EXIST/close",
        headers=_auth("CUST-CLOSE-A"),
    )
    assert r.status_code == 404, r.text
    assert "not found" in r.text.lower()
