from __future__ import annotations

import base64
import json

from app.core.auth import create_access_token, create_refresh_token, decode_token
from app.models.case import Case
from app.models.customer import Customer
from app.models.sale import Sale
from app.models.user_role import ROLE_ADMIN, UserRole


def _add_role(db_session, subject_id: str, role: str, role_id: str) -> None:
    db_session.add(
        UserRole(user_role_id=role_id, subject_id=subject_id, role=role)
    )
    db_session.commit()


def test_staff_customer_session_cannot_refresh(client, db_session):
    db_session.add(Customer(customer_id="CUST_REFRESH_GUARD", name="مشتری"))
    _add_role(db_session, "STAFF_REFRESH_ADMIN", ROLE_ADMIN, "UR-STAFF-REFRESH-ADMIN")

    admin_token = create_access_token({"sub": "STAFF_REFRESH_ADMIN"})
    session_response = client.post(
        "/api/v1/auth/staff-customer-session",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"customer_id": "CUST_REFRESH_GUARD"},
    )
    assert session_response.status_code == 200
    staff_token = session_response.json()["access_token"]

    refresh_response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": staff_token},
    )
    assert refresh_response.status_code == 401


def test_valid_refresh_does_not_promote_authorization_claims(client):
    refresh_token = create_refresh_token(
        {
            "sub": "CUST_REFRESH_CLAIMS",
            "purpose": "staff_customer_session",
            "staff_session": True,
            "role": "Admin",
        }
    )

    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert response.status_code == 200, response.text
    access_claims = decode_token(response.json()["access_token"])
    assert access_claims is not None
    assert access_claims["sub"] == "CUST_REFRESH_CLAIMS"
    assert access_claims["type"] == "access"
    assert "purpose" not in access_claims
    assert "staff_session" not in access_claims
    assert "role" not in access_claims


def test_tampered_refresh_claims_are_rejected(client):
    refresh_token = create_refresh_token({"sub": "CUST_REFRESH_TAMPER"})
    header, payload, signature = refresh_token.split(".")
    claims = json.loads(
        base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4))
    )
    claims["purpose"] = "staff_customer_session"
    claims["staff_session"] = True
    tampered_payload = base64.urlsafe_b64encode(
        json.dumps(claims, separators=(",", ":")).encode()
    ).decode().rstrip("=")
    tampered_token = f"{header}.{tampered_payload}.{signature}"

    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": tampered_token},
    )
    assert response.status_code == 401


def test_staff_customer_session_cannot_use_admin_role_even_if_customer_subject_has_role(
    client, db_session
):
    customer_id = "CUST_ROLE_COLLISION"
    db_session.add(Customer(customer_id=customer_id, name="مشتری"))
    _add_role(db_session, "STAFF_COLLISION_ADMIN", ROLE_ADMIN, "UR-STAFF-COLLISION-ADMIN")
    # Deliberately exercise a role/subject collision: the session's sub is the
    # customer ID, which also has an Admin role row in this adversarial fixture.
    _add_role(db_session, customer_id, ROLE_ADMIN, "UR-CUST-COLLISION-ADMIN")

    admin_token = create_access_token({"sub": "STAFF_COLLISION_ADMIN"})
    session_response = client.post(
        "/api/v1/auth/staff-customer-session",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"customer_id": customer_id},
    )
    assert session_response.status_code == 200
    staff_token = session_response.json()["access_token"]

    # This endpoint itself is Admin-only, so a 403 proves role privilege was
    # not inherited by the staff-mediated customer session.
    denied = client.post(
        "/api/v1/auth/staff-customer-session",
        headers={"Authorization": f"Bearer {staff_token}"},
        json={"customer_id": customer_id},
    )
    assert denied.status_code == 403

    sale_denied = client.post(
        "/api/v1/sales/",
        headers={"Authorization": f"Bearer {staff_token}"},
        json={
            "customer_id": customer_id,
            "items": [],
            "fx_rate_usd_to_irr": 1,
        },
    )
    assert sale_denied.status_code == 403
    db_session.expire_all()
    assert db_session.query(Sale).count() == 0


def test_admin_token_still_passes_role_gate_for_sale_endpoint(client, db_session):
    _add_role(db_session, "SALE_AUTH_ADMIN", ROLE_ADMIN, "UR-SALE-AUTH-ADMIN")
    admin_token = create_access_token({"sub": "SALE_AUTH_ADMIN"})

    # Empty items are rejected by sale business rules, but an Admin token must
    # pass the authorization gate (and therefore must not receive 401/403).
    response = client.post(
        "/api/v1/sales/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "customer_id": "CUST_SALE_AUTH_TEST",
            "items": [],
            "fx_rate_usd_to_irr": 1,
        },
    )
    assert response.status_code not in (401, 403)


def _staff_session_for(client, db_session, customer_id: str) -> str:
    admin_id = f"STAFF_IDENTITY_ADMIN_{customer_id}"
    _add_role(
        db_session,
        admin_id,
        ROLE_ADMIN,
        f"UR-IDENTITY-ADMIN-{customer_id}",
    )
    admin_token = create_access_token({"sub": admin_id})
    response = client.post(
        "/api/v1/auth/staff-customer-session",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"customer_id": customer_id},
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def test_same_mobile_requires_explicit_matching_surname_and_never_mutates_on_conflict(
    client, db_session
):
    customer_id = "CUST_IDENTITY_SAME_MOBILE"
    db_session.add(
        Customer(
            customer_id=customer_id,
            name="مینا",
            family_name="احمدی",
            mobile="09123334444",
        )
    )
    db_session.commit()
    staff_token = _staff_session_for(client, db_session, customer_id)

    # None/omitted, blank, a different surname, and first-name-as-surname
    # must all fail without changing Customer or creating a Case.
    for incoming in (None, "", "رضایی", "مینا"):
        payload = {
            "name": "نام نباید تغییر کند",
            "mobile": "09123334444",
            "consent": 1,
            "guest": False,
            "open_case": True,
        }
        if incoming is not None:
            payload["family_name"] = incoming
        response = client.post(
            "/api/v1/customers/intake",
            headers={"Authorization": f"Bearer {staff_token}"},
            json=payload,
        )
        assert response.status_code == 409, (incoming, response.text)
        db_session.expire_all()
        saved = db_session.get(Customer, customer_id)
        assert saved.name == "مینا"
        assert saved.family_name == "احمدی"
        assert saved.mobile == "09123334444"
        assert db_session.query(Case).count() == 0


def test_same_mobile_with_explicit_matching_surname_is_allowed(client, db_session):
    customer_id = "CUST_IDENTITY_MATCHING_SURNAME"
    db_session.add(
        Customer(
            customer_id=customer_id,
            name="مینا",
            family_name="احمدی",
            mobile="09125556666",
        )
    )
    db_session.commit()
    staff_token = _staff_session_for(client, db_session, customer_id)

    response = client.post(
        "/api/v1/customers/intake",
        headers={"Authorization": f"Bearer {staff_token}"},
        json={
            "name": "مینا جدید",
            "family_name": "احمدی",
            "mobile": "09125556666",
            "consent": 0,
            "guest": False,
            "open_case": False,
        },
    )
    assert response.status_code == 201, response.text
    db_session.expire_all()
    saved = db_session.get(Customer, customer_id)
    assert saved.name == "مینا جدید"
    assert saved.family_name == "احمدی"
    assert saved.mobile == "09125556666"
    assert db_session.query(Case).count() == 0
