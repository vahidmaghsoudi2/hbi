"""Identity contract: mobile primary + explicit family_name; first name ignored.

Rules under test:
1. Free mobile + legacy customer with family_name=NULL → assign allowed.
2. Mobile owned by another customer → 409 before any mutation/Case.
3. Same mobile with omitted/blank/different surname → 409, no mutation/Case.
4. Same mobile with explicit matching surname → process continues.
5. Given/first name never substitutes for family_name.
"""
from __future__ import annotations

from app.core.auth import create_access_token
from app.models.case import Case
from app.models.customer import Customer


def _staff_customer_token(customer_id: str) -> str:
    return create_access_token(
        {
            "sub": customer_id,
            "purpose": "staff_customer_session",
            "staff_session": True,
        }
    )


def test_unowned_mobile_assignable_to_legacy_null_family_name(client, db_session):
    """Free mobile + legacy family_name=NULL → assignment allowed."""
    customer_id = "CUST_LEGACY_NULL_FN"
    db_session.add(
        Customer(
            customer_id=customer_id,
            name="\u0645\u06cc\u0646\u0627",
            family_name=None,
            mobile=None,
        )
    )
    db_session.commit()

    staff = _staff_customer_token(customer_id)
    resp = client.post(
        "/api/v1/customers/intake",
        headers={"Authorization": f"Bearer {staff}"},
        json={
            "name": "\u0645\u06cc\u0646\u0627",
            "family_name": "\u0627\u062d\u0645\u062f\u06cc",
            "mobile": "09121112222",
            "consent": 0,
            "guest": False,
            "open_case": False,
        },
    )
    assert resp.status_code == 201, resp.text
    db_session.expire_all()
    saved = db_session.get(Customer, customer_id)
    assert saved.mobile == "09121112222"
    assert saved.family_name == "\u0627\u062d\u0645\u062f\u06cc"
    assert db_session.query(Case).count() == 0


def test_mobile_owned_by_other_customer_returns_409_without_mutation(client, db_session):
    db_session.add_all(
        [
            Customer(customer_id="CUST_OWNER_A", name="\u0627\u0644\u0641", family_name="\u0645\u0627\u0644\u06a9", mobile="09123330000"),
            Customer(customer_id="CUST_OWNER_B", name="\u0628", family_name=None, mobile=None),
        ]
    )
    db_session.commit()

    staff_b = _staff_customer_token("CUST_OWNER_B")
    resp = client.post(
        "/api/v1/customers/intake",
        headers={"Authorization": f"Bearer {staff_b}"},
        json={
            "name": "\u0646\u0628\u0627\u06cc\u062f \u062a\u063a\u06cc\u06cc\u0631 \u06a9\u0646\u062f",
            "family_name": "\u0645\u0627\u0644\u06a9",
            "mobile": "09123330000",
            "consent": 1,
            "guest": False,
            "open_case": True,
        },
    )
    assert resp.status_code == 409, resp.text
    db_session.expire_all()
    a = db_session.get(Customer, "CUST_OWNER_A")
    b = db_session.get(Customer, "CUST_OWNER_B")
    assert a.name == "\u0627\u0644\u0641"
    assert a.mobile == "09123330000"
    assert b.mobile is None
    assert db_session.query(Case).count() == 0


def test_same_mobile_omitted_blank_or_different_surname_is_409(client, db_session):
    customer_id = "CUST_SAME_MOBILE"
    db_session.add(
        Customer(
            customer_id=customer_id,
            name="\u0633\u0627\u0631\u0627",
            family_name="\u06a9\u0631\u06cc\u0645\u06cc",
            mobile="09124445555",
        )
    )
    db_session.commit()
    staff = _staff_customer_token(customer_id)

    for family_name in (None, "", " \t ", "\u062e\u0637\u0627"):
        payload = {
            "name": "\u0633\u0627\u0631\u0627",
            "mobile": "09124445555",
            "consent": 0,
            "guest": False,
            "open_case": True,
        }
        if family_name is not None:
            payload["family_name"] = family_name
        resp = client.post(
            "/api/v1/customers/intake",
            headers={"Authorization": f"Bearer {staff}"},
            json=payload,
        )
        assert resp.status_code == 409, (family_name, resp.text)

    db_session.expire_all()
    saved = db_session.get(Customer, customer_id)
    assert saved.family_name == "\u06a9\u0631\u06cc\u0645\u06cc"
    assert saved.name == "\u0633\u0627\u0631\u0627"
    assert db_session.query(Case).count() == 0


def test_same_mobile_with_explicit_matching_surname_is_allowed(client, db_session):
    customer_id = "CUST_MATCH_OK"
    db_session.add(
        Customer(
            customer_id=customer_id,
            name="\u0646\u06cc\u0645\u0627",
            family_name="\u0631\u0636\u0627\u06cc\u06cc",
            mobile="09125556666",
        )
    )
    db_session.commit()

    staff = _staff_customer_token(customer_id)
    resp = client.post(
        "/api/v1/customers/intake",
        headers={"Authorization": f"Bearer {staff}"},
        json={
            "name": "\u0646\u06cc\u0645\u0627",
            "family_name": "\u0631\u0636\u0627\u06cc\u06cc",
            "mobile": "09125556666",
            "consent": 0,
            "guest": False,
            "open_case": False,
        },
    )
    assert resp.status_code == 201, resp.text
    db_session.expire_all()
    saved = db_session.get(Customer, customer_id)
    assert saved.mobile == "09125556666"
    assert saved.family_name == "\u0631\u0636\u0627\u06cc\u06cc"
    assert db_session.query(Case).count() == 0
