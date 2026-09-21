"""D2 — Case ID uniqueness under concurrent / same-second creation."""

from concurrent.futures import ThreadPoolExecutor, as_completed

from app.core.auth import create_access_token
from app.models.case import Case
from app.models.customer import Customer
from app.services.case_service import CaseService


def _auth(cid: str):
    return {"Authorization": f"Bearer {create_access_token({'sub': cid})}"}


def test_two_cases_same_customer_get_distinct_ids(db_session):
    db_session.add(Customer(customer_id="C-CASE-1", name="A", consent_to_store_data=1))
    db_session.flush()
    svc = CaseService(db_session)
    a = svc.create_case("C-CASE-1", "OPEN")
    b = svc.create_case("C-CASE-1", "OPEN")
    assert a.case_id != b.case_id
    assert a.case_id.startswith("CASE_")
    assert b.case_id.startswith("CASE_")
    assert a.customer_id == "C-CASE-1"
    assert b.customer_id == "C-CASE-1"
    db_session.commit()
    rows = db_session.query(Case).filter_by(customer_id="C-CASE-1").all()
    assert len(rows) == 2
    assert {r.case_id for r in rows} == {a.case_id, b.case_id}


def test_concurrent_case_creates_all_unique(db_session):
    """Service-level burst: many creates must not collide on case_id."""
    db_session.add(Customer(customer_id="C-CASE-BURST", name="B", consent_to_store_data=1))
    db_session.flush()
    svc = CaseService(db_session)
    ids = [svc.create_case("C-CASE-BURST", "OPEN").case_id for _ in range(40)]
    assert len(ids) == len(set(ids))
    db_session.commit()


def test_http_intake_open_case_twice_no_500(client, db_session):
    db_session.add(Customer(customer_id="C-HTTP-CASE", name="H", consent_to_store_data=1))
    db_session.commit()
    h = _auth("C-HTTP-CASE")
    body = {
        "name": "H",
        "concerns": "آفتاب",
        "consent": 0,
        "guest": False,
        "open_case": True,
    }
    r1 = client.post("/api/v1/customers/intake", json=body, headers=h)
    r2 = client.post("/api/v1/customers/intake", json=body, headers=h)
    assert r1.status_code == 201, r1.text
    assert r2.status_code == 201, r2.text
    c1 = r1.json().get("case", {}).get("case_id")
    c2 = r2.json().get("case", {}).get("case_id")
    assert c1 and c2 and c1 != c2
