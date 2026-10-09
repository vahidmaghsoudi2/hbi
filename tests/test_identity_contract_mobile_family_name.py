"""Identity contract: mobile primary + explicit family_name; first name ignored.

Rules under test:
1. Free mobile + legacy customer with family_name=NULL -> assign allowed.
2. Mobile owned by another customer -> 409 before any mutation/Case.
3. Same mobile with omitted/blank/different surname -> 409, no mutation/Case.
4. Same mobile with explicit matching surname -> process continues.
5. Given/first name never substitutes for family_name.
"""
from __future__ import annotations

from app.core.auth import create_access_token
from app.models.case import Case
from app.models.customer import Customer
from app.models.user_role import ROLE_ADMIN, UserRole


def _admin_headers(db_session, subject_id: str = "ID_CONTRACT_ADMIN") -> dict:
    db_session.add(
        UserRole(
            user_role_id=f"UR-{subject_id}",
            subject_id=subject_id,
            role=ROLE_ADMIN,
        )
    )
    db_session.commit()
    token = create_access_token({"sub": subject_id})
    return {"Authorization": f"Bearer {token}"}


def _staff_token(client, admin_headers: dict, customer_id: str) -> str:
    response = client.post(
        "/api/v1/auth/staff-customer-session",
        headers=admin_headers,
        json={"customer_id": customer_id},
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def test_unowned_mobile_assignable_to_legacy_null_family_name(client, db_session):
    """Free mobile + legacy family_name=NULL -> assignment allowed."""
    customer_id = "CUST_LEGACY_NULL_FN"
    db_session.add(
        Customer(
            customer_id=customer_id,
            name="مینا",
            family_name=None,
            mobile=None,
        )
    )
    db_session.commit()
    admin = _admin_headers(db_session)
    staff = _staff_token(client, admin, customer_id)

    response = client.post(
        "/api/v1/customers/intake",
        headers={"Authorization": f"Bearer {staff}"},
        json={
            "name": "مینا",
            "family_name": "احمدی",
            "mobile": "09121112222",
            "consent": 0,
            "guest": False,
            "open_case": False,
        },
    )
    assert response.status_code == 201, response.text
    db_session.expire_all()
    saved = db_session.get(Customer, customer_id)
    assert saved.mobile == "09121112222"
    assert saved.family_name == "احمدی"
    assert db_session.query(Case).count() == 0


def test_mobile_owned_by_other_customer_returns_409_without_mutation(client, db_session):
    db_session.add_all(
        [
            Customer(customer_id="CUST_OWNER_A", name="الف", family_name="مالک", mobile="09123330000"),
            Customer(customer_id="CUST_OWNER_B", name="ب", family_name=None, mobile=None),
        ]
    )
    db_session.commit()
    admin = _admin_headers(db_session, "ID_OWNER_ADMIN")
    staff_b = _staff_token(client, admin, "CUST_OWNER_B")

    response = client.post(
        "/api/v1/customers/intake",
        headers={"Authorization": f"Bearer {staff_b}"},
        json={
            "name": "نباید تغییر کند",
            "family_name": "مالک",
            "mobile": "09123330000",
            "consent": 1,
            "guest": False,
            "open_case": True,
        },
    )
    assert response.status_code == 409, response.text
    db_session.expire_all()
    a = db_session.get(Customer, "CUST_OWNER_A")
    b = db_session.get(Customer, "CUST_OWNER_B")
    assert a.name == "الف"
    assert a.mobile == "09123330000"
    assert b.name == "ب"
    assert b.mobile is None
    assert db_session.query(Case).count() == 0


def test_same_mobile_omitted_blank_or_different_surname_is_409(client, db_session):
    customer_id = "CUST_SAME_MOBILE_CONFLICT"
    db_session.add(
        Customer(
            customer_id=customer_id,
            name="مینا",
            family_name="احمدی",
            mobile="09124445555",
        )
    )
    db_session.commit()
    admin = _admin_headers(db_session, "ID_SAME_ADMIN")
    staff = _staff_token(client, admin, customer_id)

    cases = [
        {"label": "omitted", "payload_extra": {}},
        {"label": "blank", "payload_extra": {"family_name": ""}},
        {"label": "different", "payload_extra": {"family_name": "رضایی"}},
        {"label": "first_name_as_surname", "payload_extra": {"family_name": "مینا"}},
    ]
    for case in cases:
        payload = {
            "name": "نام نباید تغییر کند",
            "mobile": "09124445555",
            "consent": 1,
            "guest": False,
            "open_case": True,
        }
        payload.update(case["payload_extra"])
        response = client.post(
            "/api/v1/customers/intake",
            headers={"Authorization": f"Bearer {staff}"},
            json=payload,
        )
        assert response.status_code == 409, (case["label"], response.text)
        db_session.expire_all()
        saved = db_session.get(Customer, customer_id)
        assert saved.name == "مینا", case["label"]
        assert saved.family_name == "احمدی", case["label"]
        assert saved.mobile == "09124445555", case["label"]
        assert db_session.query(Case).count() == 0, case["label"]


def test_same_mobile_with_explicit_matching_surname_is_allowed(client, db_session):
    customer_id = "CUST_SAME_MOBILE_OK"
    db_session.add(
        Customer(
            customer_id=customer_id,
            name="مینا",
            family_name="احمدی",
            mobile="09126667777",
        )
    )
    db_session.commit()
    admin = _admin_headers(db_session, "ID_MATCH_ADMIN")
    staff = _staff_token(client, admin, customer_id)

    response = client.post(
        "/api/v1/customers/intake",
        headers={"Authorization": f"Bearer {staff}"},
        json={
            "name": "مینا به‌روز",
            "family_name": "احمدی",
            "mobile": "09126667777",
            "consent": 0,
            "guest": False,
            "open_case": False,
        },
    )
    assert response.status_code == 201, response.text
    db_session.expire_all()
    saved = db_session.get(Customer, customer_id)
    assert saved.name == "مینا به‌روز"
    assert saved.family_name == "احمدی"
    assert saved.mobile == "09126667777"
    assert db_session.query(Case).count() == 0
