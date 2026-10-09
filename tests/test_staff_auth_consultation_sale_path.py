from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from app.core.auth import create_access_token, decode_token
from app.models.case import Case
from app.models.customer import Customer
from app.models.user_role import ROLE_ADMIN, UserRole
from app.services.customer_service import CustomerService
from scripts.migrate_customer_family_name import migrate


def _admin_token(db_session) -> str:
    db_session.add(
        UserRole(
            user_role_id="UR-STAFF-AUTH-ADMIN",
            subject_id="STAFF_AUTH_ADMIN",
            role=ROLE_ADMIN,
        )
    )
    db_session.commit()
    return create_access_token({"sub": "STAFF_AUTH_ADMIN"})


def _staff_token(client, admin_token: str, customer_id: str) -> str:
    response = client.post(
        "/api/v1/auth/staff-customer-session",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"customer_id": customer_id},
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["customer_id"] == customer_id
    assert payload["purpose"] == "staff_customer_session"
    assert payload["expires_in"] > 0
    return payload["access_token"]


def test_admin_can_issue_short_lived_staff_customer_session(client, db_session):
    db_session.add(Customer(customer_id="CUST_STAFF_A", name="مینا"))
    admin_token = _admin_token(db_session)

    staff_token = _staff_token(client, admin_token, "CUST_STAFF_A")
    claims = decode_token(staff_token)

    assert claims is not None
    assert claims["sub"] == "CUST_STAFF_A"
    assert claims["purpose"] == "staff_customer_session"
    assert claims["staff_session"] is True
    assert claims["issued_by"] == "STAFF_AUTH_ADMIN"


def test_non_admin_cannot_issue_staff_customer_session(client, db_session):
    db_session.add(Customer(customer_id="CUST_STAFF_B", name="سارا"))
    db_session.commit()
    non_admin = create_access_token({"sub": "CUST_STAFF_B"})

    response = client.post(
        "/api/v1/auth/staff-customer-session",
        headers={"Authorization": f"Bearer {non_admin}"},
        json={"customer_id": "CUST_STAFF_B"},
    )

    assert response.status_code == 403


def test_family_name_flows_through_intake_and_mobile_conflict_precedes_mutation(client, db_session):
    db_session.add_all(
        [
            Customer(customer_id="CUST_INTAKE_A", name="نام قبلی", mobile=None),
            Customer(
                customer_id="CUST_INTAKE_B",
                name="مالک موبایل",
                family_name="رضایی",
                mobile="09120000000",
            ),
        ]
    )
    admin_token = _admin_token(db_session)
    staff_a = _staff_token(client, admin_token, "CUST_INTAKE_A")

    accepted = client.post(
        "/api/v1/customers/intake",
        headers={"Authorization": f"Bearer {staff_a}"},
        json={
            "name": "مینا",
            "family_name": "احمدی",
            "mobile": "09121111111",
            "consent": 0,
            "guest": False,
            "open_case": False,
        },
    )
    assert accepted.status_code == 201, accepted.text
    db_session.expire_all()
    customer_a = db_session.get(Customer, "CUST_INTAKE_A")
    assert customer_a.name == "مینا"
    assert customer_a.family_name == "احمدی"
    assert customer_a.mobile == "09121111111"

    conflict = client.post(
        "/api/v1/customers/intake",
        headers={"Authorization": f"Bearer {staff_a}"},
        json={
            "name": "نباید ذخیره شود",
            "family_name": "رضایی",
            "mobile": "09120000000",
            "consent": 1,
            "guest": False,
            "open_case": True,
        },
    )
    assert conflict.status_code == 409
    db_session.expire_all()
    customer_a = db_session.get(Customer, "CUST_INTAKE_A")
    customer_b = db_session.get(Customer, "CUST_INTAKE_B")
    assert customer_a.name == "مینا"
    assert customer_a.family_name == "احمدی"
    assert customer_a.mobile == "09121111111"
    assert customer_b.name == "مالک موبایل"
    assert db_session.query(Case).count() == 0


def test_first_name_does_not_override_family_name_identity_and_conflict_has_no_mutation(client, db_session):
    db_session.add(
        Customer(
            customer_id="CUST_IDENTITY_A",
            name="نام قبلی",
            family_name="احمدی",
            mobile="09124445555",
            consent_to_store_data=0,
        )
    )
    db_session.commit()
    admin_token = _admin_token(db_session)
    staff_token = _staff_token(client, admin_token, "CUST_IDENTITY_A")

    same_identity = client.post(
        "/api/v1/customers/intake",
        headers={"Authorization": f"Bearer {staff_token}"},
        json={
            "name": "نام کوچک متفاوت",
            "family_name": "احمدی",
            "mobile": "09124445555",
            "consent": 0,
            "guest": False,
            "open_case": False,
        },
    )
    assert same_identity.status_code == 201, same_identity.text
    db_session.expire_all()
    saved = db_session.get(Customer, "CUST_IDENTITY_A")
    assert saved.name == "نام کوچک متفاوت"

    conflict = client.post(
        "/api/v1/customers/intake",
        headers={"Authorization": f"Bearer {staff_token}"},
        json={
            "name": "نباید ذخیره شود",
            "family_name": "رضایی",
            "mobile": "09124445555",
            "consent": 1,
            "guest": False,
            "open_case": True,
        },
    )
    assert conflict.status_code == 409
    db_session.expire_all()
    saved = db_session.get(Customer, "CUST_IDENTITY_A")
    assert saved.name == "نام کوچک متفاوت"
    assert saved.family_name == "احمدی"
    assert saved.consent_to_store_data == 0
    assert db_session.query(Case).count() == 0


def test_staff_customer_token_cannot_create_sale_even_if_subject_has_admin_role(client, db_session):
    db_session.add(Customer(customer_id="CUST_SALE_A", name="مشتری"))
    db_session.commit()
    admin_token = _admin_token(db_session)
    # Defensive collision case: the customer subject must not inherit this role
    # through a staff-customer token, even if data is misconfigured.
    db_session.add(
        UserRole(
            user_role_id="UR-CUST-SALE-A-ADMIN",
            subject_id="CUST_SALE_A",
            role=ROLE_ADMIN,
        )
    )
    db_session.commit()
    staff_token = _staff_token(client, admin_token, "CUST_SALE_A")

    response = client.post(
        "/api/v1/sales/",
        headers={"Authorization": f"Bearer {staff_token}"},
        json={
            "customer_id": "CUST_SALE_A",
            "items": [],
            "fx_rate_usd_to_irr": 1,
        },
    )

    assert response.status_code == 403


def test_mobile_match_requires_explicit_family_name_in_service(db_session):
    db_session.add(
        Customer(
            customer_id="CUST_MATCH_A",
            name="نام ثبت‌شده",
            family_name="احمدی",
            mobile="09123334444",
        )
    )
    db_session.commit()

    with pytest.raises(ValueError, match="family_name is missing"):
        CustomerService(db_session).record_intake(
            name="نام جدید",
            mobile="09123334444",
            family_name=None,
            consent=0,
        )

    db_session.expire_all()
    saved = db_session.get(Customer, "CUST_MATCH_A")
    assert saved.name == "نام ثبت‌شده"
    assert saved.family_name == "احمدی"


def test_family_name_migration_is_idempotent_and_does_not_guess_legacy_names(tmp_path: Path):
    db_path = tmp_path / "hbi-existing.sqlite3"
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            'CREATE TABLE "Customer" (customer_id VARCHAR PRIMARY KEY, name VARCHAR NOT NULL, mobile VARCHAR)'
        )
        conn.execute(
            'INSERT INTO "Customer" (customer_id, name, mobile) VALUES (?, ?, ?)',
            ("CUST_LEGACY", "مینا احمدی", "09129999999"),
        )
        conn.commit()

    assert migrate(db_path) == 0
    assert migrate(db_path) == 0

    with sqlite3.connect(db_path) as conn:
        columns = {row[1] for row in conn.execute('PRAGMA table_info("Customer")')}
        assert "family_name" in columns
        row = conn.execute(
            'SELECT name, family_name FROM "Customer" WHERE customer_id = ?',
            ("CUST_LEGACY",),
        ).fetchone()

    assert row == ("مینا احمدی", None)
