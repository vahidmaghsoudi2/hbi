"""Integration checks for the separate gallery-operator identity and access boundary."""
from __future__ import annotations

from app.core.auth import create_access_token
from app.models.admin_credential import AdminCredential
from app.models.customer import Customer
from app.models.user_role import UserRole, ROLE_ADMIN, ROLE_GALLERY_OPERATOR


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



def test_public_guest_registration_is_disabled(client):
    response = client.post(
        "/api/v1/customers/guest",
        json={"name": "مشتری مهمان", "consent": 1, "concerns": "آبرسان"},
    )
    assert response.status_code == 403, response.text


def test_customer_token_issuance_is_disabled(client, db_session):
    db_session.add(Customer(customer_id="CUST-NO-TOKEN", name="مشتری بدون توکن"))
    db_session.commit()
    response = client.post(
        "/api/v1/auth/pilot-token",
        json={"customer_id": "CUST-NO-TOKEN"},
    )
    assert response.status_code == 403, response.text


def test_unassigned_customer_identity_cannot_access_authenticated_api(client, db_session):
    db_session.add(Customer(customer_id="CUST-NO-ROLE", name="مشتری بدون نقش"))
    db_session.commit()
    response = client.get(
        "/api/v1/customers/id/CUST-NO-ROLE",
        headers=_headers("CUST-NO-ROLE"),
    )
    assert response.status_code == 403, response.text

def test_customer_mobile_lookup_is_owner_scoped(client, db_session):
    db_session.add_all([
        Customer(customer_id="CUST-MOBILE-OWNER", name="مالک", mobile="09135550201"),
        Customer(customer_id="CUST-MOBILE-OTHER", name="دیگری", mobile="09135550202"),
    ])
    db_session.commit()
    response = client.get("/api/v1/customers/mobile/09135550202", headers=_headers("CUST-MOBILE-OWNER"))
    assert response.status_code == 403, response.text


def test_customer_search_requires_gallery_operator_role(client):
    response = client.get("/api/v1/customers/search?q=سارا", headers=_headers("CUST-UNPRIVILEGED"))
    assert response.status_code == 403


def test_customer_identity_cannot_access_customer_api_even_for_own_record(client, db_session):
    db_session.add(Customer(customer_id="CUST-SELF-1", name="خود مشتری"))
    db_session.commit()
    response = client.get(
        "/api/v1/customers/id/CUST-SELF-1",
        headers=_headers("CUST-SELF-1"),
    )
    assert response.status_code == 403, response.text


def test_gallery_operator_can_search_existing_customer(client, db_session):
    _assign_role(db_session, "USR_GALLERY_SEARCH")
    db_session.add(Customer(customer_id="CUST-SEARCH-1", name="سارا احمدی", mobile="09135550103"))
    db_session.commit()
    response = client.get(
        "/api/v1/customers/search?q=سارا",
        headers=_headers("USR_GALLERY_SEARCH"),
    )
    assert response.status_code == 200, response.text
    assert any(item["customer_id"] == "CUST-SEARCH-1" for item in response.json())

def test_customer_cannot_read_another_customers_sales_or_total(client, db_session):
    db_session.add_all([
        Customer(customer_id="CUST-SALES-SELF", name="مشتری خود"),
        Customer(customer_id="CUST-SALES-OTHER", name="مشتری دیگر"),
    ])
    db_session.commit()
    headers = _headers("CUST-SALES-SELF")

    history = client.get(
        "/api/v1/sales/customer/CUST-SALES-OTHER",
        headers=headers,
    )
    assert history.status_code == 403, history.text

    total = client.get(
        "/api/v1/sales/total?target_customer_id=CUST-SALES-OTHER",
        headers=headers,
    )
    assert total.status_code == 403, total.text


def test_gallery_operator_can_read_selected_customers_sales_history_and_total(client, db_session):
    _assign_role(db_session, "USR_GALLERY_SALES_READ")
    db_session.add(Customer(customer_id="CUST-SALES-READ", name="مشتری منتخب"))
    db_session.commit()
    headers = _headers("USR_GALLERY_SALES_READ")

    history = client.get(
        "/api/v1/sales/customer/CUST-SALES-READ",
        headers=headers,
    )
    assert history.status_code == 200, history.text
    assert history.json() == []

    total = client.get(
        "/api/v1/sales/total?target_customer_id=CUST-SALES-READ",
        headers=headers,
    )
    assert total.status_code == 200, total.text
    assert "total_sales" in total.json()



def test_admin_and_gallery_operator_login_roles_are_not_interchangeable(client, db_session, monkeypatch):
    db_session.add_all([
        AdminCredential(
            credential_id="ADMIN-CRED-ROLE-BOUNDARY",
            subject_id="USR_ROLE_BOUNDARY_ADMIN",
            username="admin-boundary",
            password_hash="test-hash",
        ),
        AdminCredential(
            credential_id="GALLERY-CRED-ROLE-BOUNDARY",
            subject_id="USR_ROLE_BOUNDARY_GALLERY",
            username="gallery-boundary",
            password_hash="test-hash",
        ),
    ])
    _assign_role(db_session, "USR_ROLE_BOUNDARY_ADMIN", ROLE_ADMIN)
    _assign_role(db_session, "USR_ROLE_BOUNDARY_GALLERY", ROLE_GALLERY_OPERATOR)
    monkeypatch.setattr("app.api.routers.auth.verify_admin_password", lambda credential, password: password == "valid")

    admin_on_operator_route = client.post(
        "/api/v1/auth/operator-login",
        json={"username": "admin-boundary", "password": "valid"},
    )
    gallery_on_admin_route = client.post(
        "/api/v1/auth/login",
        json={"username": "gallery-boundary", "password": "valid"},
    )

    assert admin_on_operator_route.status_code == 403, admin_on_operator_route.text
    assert gallery_on_admin_route.status_code == 403, gallery_on_admin_route.text


def test_dual_role_identity_cannot_login_as_admin_or_gallery_operator(client, db_session, monkeypatch):
    db_session.add(AdminCredential(
        credential_id="CRED-DUAL-ROLE-LOGIN",
        subject_id="USR_DUAL_ROLE_LOGIN",
        username="dual-role-login",
        password_hash="test-hash",
    ))
    _assign_role(db_session, "USR_DUAL_ROLE_LOGIN", ROLE_ADMIN)
    _assign_role(db_session, "USR_DUAL_ROLE_LOGIN", ROLE_GALLERY_OPERATOR)
    monkeypatch.setattr(
        "app.api.routers.auth.verify_admin_password",
        lambda credential, password: password == "valid",
    )

    admin_login = client.post(
        "/api/v1/auth/login",
        json={"username": "dual-role-login", "password": "valid"},
    )
    operator_login = client.post(
        "/api/v1/auth/operator-login",
        json={"username": "dual-role-login", "password": "valid"},
    )

    assert admin_login.status_code == 403, admin_login.text
    assert operator_login.status_code == 403, operator_login.text
    assert "identity conflict" in admin_login.json()["detail"].lower()
    assert "identity conflict" in operator_login.json()["detail"].lower()


def test_gallery_operator_provisioning_refuses_to_take_over_existing_non_admin_username(
    db_session, monkeypatch
):
    from app.services.admin_auth_service import ensure_gallery_operator_account

    existing = AdminCredential(
        credential_id="CRED-EXISTING-EDITOR",
        subject_id="USR_EXISTING_EDITOR",
        username="existing-editor",
        password_hash="existing-hash",
    )
    db_session.add(existing)
    _assign_role(db_session, "USR_EXISTING_EDITOR", "Editor")
    db_session.commit()
    monkeypatch.setenv("HBI_GALLERY_OPERATOR_USERNAME", "existing-editor")
    monkeypatch.setenv("HBI_GALLERY_OPERATOR_PASSWORD", "new-secret")
    monkeypatch.setenv("HBI_GALLERY_OPERATOR_SUBJECT", "USR_GALLERY_OPERATOR")

    try:
        ensure_gallery_operator_account(db_session)
        assert False, "Expected conflicting username to be rejected"
    except ValueError as exc:
        assert "different subject" in str(exc)

    db_session.refresh(existing)
    assert existing.subject_id == "USR_EXISTING_EDITOR"
    assert existing.password_hash == "existing-hash"
    assert db_session.query(UserRole).filter_by(
        subject_id="USR_EXISTING_EDITOR", role="Editor"
    ).one()


def test_gallery_operator_provisioning_refuses_subject_with_another_username(
    db_session, monkeypatch
):
    from app.services.admin_auth_service import ensure_gallery_operator_account

    existing = AdminCredential(
        credential_id="CRED-EXISTING-GALLERY-SUBJECT",
        subject_id="USR_GALLERY_OPERATOR",
        username="already-configured-login",
        password_hash="existing-hash",
    )
    db_session.add(existing)
    db_session.commit()
    monkeypatch.setenv("HBI_GALLERY_OPERATOR_USERNAME", "new-gallery-login")
    monkeypatch.setenv("HBI_GALLERY_OPERATOR_PASSWORD", "new-secret")
    monkeypatch.setenv("HBI_GALLERY_OPERATOR_SUBJECT", "USR_GALLERY_OPERATOR")

    try:
        ensure_gallery_operator_account(db_session)
        assert False, "Expected conflicting subject to be rejected"
    except ValueError as exc:
        assert "different username" in str(exc)

    assert db_session.query(AdminCredential).filter_by(
        username="already-configured-login"
    ).one().password_hash == "existing-hash"
    assert db_session.query(AdminCredential).filter_by(
        username="new-gallery-login"
    ).first() is None


def test_admin_provisioning_refuses_to_promote_an_existing_non_admin_username(
    db_session, monkeypatch
):
    from app.services.admin_auth_service import ensure_admin_account

    existing = AdminCredential(
        credential_id="CRED-EXISTING-PO",
        subject_id="USR_EXISTING_PO",
        username="existing-po-login",
        password_hash="existing-po-hash",
    )
    db_session.add(existing)
    _assign_role(db_session, "USR_EXISTING_PO", "PO")
    db_session.commit()
    monkeypatch.setenv("HBI_ADMIN_USERNAME", "existing-po-login")
    monkeypatch.setenv("HBI_ADMIN_PASSWORD", "admin-secret")
    monkeypatch.setenv("HBI_ADMIN_SUBJECT", "USR_ADMIN")

    try:
        ensure_admin_account(db_session)
        assert False, "Expected conflicting admin username to be rejected"
    except ValueError as exc:
        assert "different subject" in str(exc)

    db_session.refresh(existing)
    assert existing.subject_id == "USR_EXISTING_PO"
    assert existing.password_hash == "existing-po-hash"
    assert db_session.query(UserRole).filter_by(
        subject_id="USR_EXISTING_PO", role="PO"
    ).one()


def test_admin_provisioning_refuses_subject_with_another_username(db_session, monkeypatch):
    from app.services.admin_auth_service import ensure_admin_account

    existing = AdminCredential(
        credential_id="CRED-EXISTING-ADMIN-SUBJECT",
        subject_id="USR_ADMIN",
        username="already-admin-login",
        password_hash="existing-admin-hash",
    )
    db_session.add(existing)
    db_session.commit()
    monkeypatch.setenv("HBI_ADMIN_USERNAME", "new-admin-login")
    monkeypatch.setenv("HBI_ADMIN_PASSWORD", "admin-secret")
    monkeypatch.setenv("HBI_ADMIN_SUBJECT", "USR_ADMIN")

    try:
        ensure_admin_account(db_session)
        assert False, "Expected conflicting admin subject to be rejected"
    except ValueError as exc:
        assert "different username" in str(exc)

    assert db_session.query(AdminCredential).filter_by(
        username="already-admin-login"
    ).one().password_hash == "existing-admin-hash"
    assert db_session.query(AdminCredential).filter_by(
        username="new-admin-login"
    ).first() is None


def test_admin_provisioning_refuses_gallery_operator_subject(db_session, monkeypatch):
    from app.services.admin_auth_service import ensure_admin_account

    db_session.add(AdminCredential(
        credential_id="CRED-GALLERY-AS-ADMIN",
        subject_id="USR_SHARED_ROLE_BOUNDARY",
        username="shared-role-login",
        password_hash="existing-hash",
    ))
    _assign_role(db_session, "USR_SHARED_ROLE_BOUNDARY", ROLE_GALLERY_OPERATOR)
    monkeypatch.setenv("HBI_ADMIN_USERNAME", "shared-role-login")
    monkeypatch.setenv("HBI_ADMIN_PASSWORD", "admin-secret")
    monkeypatch.setenv("HBI_ADMIN_SUBJECT", "USR_SHARED_ROLE_BOUNDARY")

    try:
        ensure_admin_account(db_session)
        assert False, "Expected Admin/GalleryOperator identity conflict to be rejected"
    except ValueError as exc:
        assert "GalleryOperator" in str(exc)

    assert db_session.query(UserRole).filter_by(
        subject_id="USR_SHARED_ROLE_BOUNDARY", role=ROLE_GALLERY_OPERATOR
    ).one()
    assert db_session.query(UserRole).filter_by(
        subject_id="USR_SHARED_ROLE_BOUNDARY", role=ROLE_ADMIN
    ).first() is None
