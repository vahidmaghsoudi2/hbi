"""AuthZ regression tests for POST /cases/{case_id}/close.

Contract source: Issue #157 / Team 3 Integration Reality GAP.
"""
from app.core.auth import create_access_token
from app.models.case import Case


def _auth_header(customer_id: str):
    return {"Authorization": f"Bearer {create_access_token({'sub': customer_id})}"}


def _make_case(db, case_id: str, customer_id: str, case_type: str = "OPEN"):
    case = Case(case_id=case_id, customer_id=customer_id, case_type=case_type)
    db.add(case)
    db.flush()
    return case


def test_close_case_owner_returns_200(client, db_session):
    _make_case(db_session, "CASE_AUTHZ_OWNER", "customer-a")

    response = client.post(
        "/api/v1/cases/CASE_AUTHZ_OWNER/close",
        headers=_auth_header("customer-a"),
    )

    assert response.status_code == 200
    assert response.json()["case_id"] == "CASE_AUTHZ_OWNER"
    assert response.json()["customer_id"] == "customer-a"
    assert response.json()["case_type"] == "CLOSED"


def test_close_case_other_customer_returns_403(client, db_session):
    _make_case(db_session, "CASE_AUTHZ_FOREIGN", "customer-a")

    response = client.post(
        "/api/v1/cases/CASE_AUTHZ_FOREIGN/close",
        headers=_auth_header("customer-b"),
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Access denied"


def test_close_case_without_token_returns_401(client, db_session):
    _make_case(db_session, "CASE_AUTHZ_NO_TOKEN", "customer-a")

    response = client.post("/api/v1/cases/CASE_AUTHZ_NO_TOKEN/close")

    assert response.status_code == 401


def test_close_case_invalid_token_returns_401(client, db_session):
    _make_case(db_session, "CASE_AUTHZ_BAD_TOKEN", "customer-a")

    response = client.post(
        "/api/v1/cases/CASE_AUTHZ_BAD_TOKEN/close",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401


def test_close_case_missing_returns_404(client, db_session):
    response = client.post(
        "/api/v1/cases/CASE_AUTHZ_MISSING/close",
        headers=_auth_header("customer-a"),
    )

    assert response.status_code == 404
