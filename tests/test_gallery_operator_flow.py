"""Integration checks for the separate gallery-operator identity and access boundary."""
from __future__ import annotations

from app.core.auth import create_access_token
from app.models.admin_credential import AdminCredential
from app.models.customer import Customer
from app.models.user_role import UserRole, ROLE_GALLERY_OPERATOR


def _headers(subject_id: str) -> dict:
    return {"Authorization": f"Bearer {create_access_token({'sub': subject_id})}"}


def _assign_role(db_session, subject_id: str, role: str = ROLE_GALLERY_OPERATOR) -> None:
    db_session.add(UserRole(
        user_role_id=f"UR-{subject_id}-{role}",
        subject_id=subject_id,
        role=role,
    ))
    db_session.commit()


def test_gallery_operator_login_requires_separate_role(client, db_session, monkeypatch):
    db_session.add(AdminCredential(
        credential_id="GALLERY-CRED-TEST",
        subject_id="USR_GALLERY_TEST",
        username="gallery-test",
        password_hash="test-hash",
    ))
    _assign_role(db_session, "USR_GALLERY_TEST")
    monkeypatch.setattr("app.api.routers.auth.verify_admin_password", lambda credential, password: password == "valid")
    response = client.post("/api/v1/auth/operator-login", json={"username": "gallery-test", "password": "valid"})
    assert response.status_code == 200, response.text
    assert response.json()["access_token"]
    denied = client.post("/api/v1/auth/operator-login", json={"username": "gallery-test", "password": "wrong"})
    assert denied.status_code in (401, 429)


def test_gallery_operator_intake_creates_customer_and_case(client, db_session):
    _assign_role(db_session, "USR_GALLERY_INTAKE")
    response = client.post(
        "/api/v1/customers/intake",
        headers=_headers("USR_GALLERY_INTAKE"),
        json={
            "name": "سارا احمدی",
            "mobile": "09135550101",
            "concerns": "آبرسان",
            "consent": 1,
            "case_type": "SKIN",
            "open_case": True,
        },
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["customer"]["name"] == "سارا احمدی"
    assert body["customer"]["mobile"] == "09135550101"
    assert body["case"]["customer_id"] == body["customer"]["customer_id"]
    assert body["case"]["case_type"] == "SKIN"


def test_gallery_operator_cannot_rebind_mobile_to_different_surname(client, db_session):
    _assign_role(db_session, "USR_GALLERY_IDENTITY")
    db_session.add(Customer(customer_id="CUST-IDENTITY-1", name="سارا احمدی", mobile="09135550102"))
    db_session.commit()
    response = client.post(
        "/api/v1/customers/intake",
        headers=_headers("USR_GALLERY_IDENTITY"),
        json={
            "name": "مریم رضایی",
            "mobile": "09135550102",
            "concerns": "لک",
            "consent": 0,
            "open_case": False,
        },
    )
    assert response.status_code == 409
    assert db_session.query(Customer).filter_by(mobile="09135550102").count() == 1
    assert db_session.query(Customer).filter_by(customer_id="CUST-IDENTITY-1").one().name == "سارا احمدی"


def test_customer_cannot_create_case_for_another_customer(client, db_session):
    db_session.add_all([
        Customer(customer_id="CUST-OWNER-1", name="مالک"),
        Customer(customer_id="CUST-OTHER-1", name="دیگری"),
    ])
    db_session.commit()
    response = client.post(
        "/api/v1/cases/",
        headers=_headers("CUST-OWNER-1"),
        json={"customer_id": "CUST-OTHER-1", "case_type": "SKIN"},
    )
    assert response.status_code == 403


def test_gallery_operator_cannot_create_financial_sale(client, db_session):
    _assign_role(db_session, "USR_GALLERY_NO_SALE")
    response = client.post(
        "/api/v1/sales/",
        headers=_headers("USR_GALLERY_NO_SALE"),
        json={
            "customer_id": "CUST-ANY",
            "items": [{"product_id": "P-ANY", "quantity": 1}],
            "fx_rate_usd_to_irr": 1_000_000,
        },
    )
    assert response.status_code == 403


def test_customer_search_requires_gallery_operator_role(client):
    response = client.get("/api/v1/customers/search?q=سارا", headers=_headers("CUST-UNPRIVILEGED"))
    assert response.status_code == 403
