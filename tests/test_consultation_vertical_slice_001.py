"""HBI-CONSULTATION-VERTICAL-SLICE-001 — HTTP acceptance matrix.

Contracts (Issue #214 / Phase 1 decisions on master):
- Customer + Case ownership via JWT (pilot-token in tests)
- Generate uses legacy Customer/consultation merge (not ProfileFact)
- Only ELIGIBLE recommendations are returned/persisted
- Empty list is a valid outcome (no fabricated Evidence Gap API)
- Optional Feedback path remains available

No Home redesign, no scoring changes, no new entities.
"""
from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

TEST_DB = Path(__file__).resolve().parents[1] / "data" / "hbi_consultation_vs_001.db"


@pytest.fixture()
def client(monkeypatch):
    if TEST_DB.exists():
        try:
            TEST_DB.unlink()
        except PermissionError:
            pass
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{TEST_DB}")
    monkeypatch.setenv("HBI_ENV", "development")

    import importlib
    import app.database as database

    importlib.reload(database)
    database.init_db()

    from app.core.deps import get_db
    from app.main import app
    from app.models.case import Case
    from app.models.customer import Customer
    from app.models.evidence import Evidence
    from app.models.product import Product
    from app.models.product_knowledge import ProductKnowledge
    from scripts.seed_products_from_records import seed

    Session = sessionmaker(bind=database.engine)
    session = Session()
    seed(session)

    product = session.query(Product).filter_by(product_id="ISDIN-FOTOUTRA100-50ML").one()
    product.status = "ACTIVE"
    product.qa_verdict = "VALID"
    product.identity_status = "VERIFIED"
    pk = session.query(ProductKnowledge).filter_by(
        product_id="ISDIN-FOTOUTRA100-50ML"
    ).one()
    pk.known_use_cases = "sun protection"
    session.add(
        Evidence(
            evidence_id="EV-CVS001-APPROVED",
            product_id="ISDIN-FOTOUTRA100-50ML",
            source_type="INDEPENDENT",
            source_reference="TEST-CVS-001",
            claim="approved support for sunscreen consultation slice",
            claim_type="FACT",
            evidence_status="SUPPORTED",
            qa_status="APPROVED",
            conflict_status="NONE",
        )
    )
    session.add(
        Customer(
            customer_id="CUST-CVS-1",
            name="Consultation VS Owner",
            consent_to_store_data=1,
        )
    )
    session.add(
        Customer(
            customer_id="CUST-CVS-2",
            name="Consultation VS Other",
            consent_to_store_data=1,
        )
    )
    session.add(Case(case_id="CASE-CVS-FOREIGN", customer_id="CUST-CVS-2", case_type="OPEN"))
    session.commit()
    session.close()

    def _override_db():
        s = Session()
        try:
            yield s
            s.commit()
        except Exception:
            s.rollback()
            raise
        finally:
            s.close()

    app.dependency_overrides[get_db] = _override_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    try:
        database.engine.dispose()
    except Exception:
        pass
    if TEST_DB.exists():
        try:
            TEST_DB.unlink()
        except PermissionError:
            pass


def _token(client: TestClient, customer_id: str) -> str:
    r = client.post("/api/v1/auth/pilot-token", json={"customer_id": customer_id})
    assert r.status_code == 200, r.text
    token = r.json().get("access_token")
    assert token
    return token


def test_unauthenticated_generate_returns_401(client):
    r = client.post(
        "/api/v1/recommendations/generate",
        json={"case_id": "CASE-ANY", "customer_profile": {"concerns": "ضدآفتاب"}},
    )
    assert r.status_code == 401


def test_foreign_case_generate_returns_403(client):
    token = _token(client, "CUST-CVS-1")
    r = client.post(
        "/api/v1/recommendations/generate",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "case_id": "CASE-CVS-FOREIGN",
            "customer_profile": {"concerns": "ضدآفتاب"},
        },
    )
    assert r.status_code == 403


def test_missing_case_generate_returns_404(client):
    token = _token(client, "CUST-CVS-1")
    r = client.post(
        "/api/v1/recommendations/generate",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "case_id": "CASE-DOES-NOT-EXIST",
            "customer_profile": {"concerns": "ضدآفتاب"},
        },
    )
    assert r.status_code == 404


def test_owned_case_consultation_generate_persist_retrieve_and_feedback(client):
    token = _token(client, "CUST-CVS-1")
    headers = {"Authorization": f"Bearer {token}"}

    created = client.post(
        "/api/v1/cases/",
        headers=headers,
        json={"customer_id": "CUST-CVS-1", "case_type": "OPEN"},
    )
    assert created.status_code == 201, created.text
    case_id = created.json()["case_id"]
    assert created.json()["customer_id"] == "CUST-CVS-1"

    gen = client.post(
        "/api/v1/recommendations/generate",
        headers=headers,
        json={
            "case_id": case_id,
            "customer_profile": {"concerns": "ضدآفتاب"},
        },
    )
    assert gen.status_code == 200, gen.text
    body = gen.json()
    assert isinstance(body, list)
    assert len(body) >= 1
    rec = body[0]
    assert rec["product_id"] == "ISDIN-FOTOUTRA100-50ML"
    assert rec.get("eligibility_status") == "ELIGIBLE"
    assert rec.get("case_id") == case_id
    assert rec.get("ranking_reasons")

    listed = client.get(f"/api/v1/recommendations/case/{case_id}", headers=headers)
    assert listed.status_code == 200, listed.text
    listed_body = listed.json()
    assert any(item.get("product_id") == "ISDIN-FOTOUTRA100-50ML" for item in listed_body)

    fb = client.post(
        "/api/v1/specialist/feedback",
        headers=headers,
        json={
            "case_id": case_id,
            "source": "CUSTOMER",
            "outcome": "ACCEPTED",
            "recommendation_id": rec.get("recommendation_id"),
            "comment": "consultation-vs-001",
        },
    )
    assert fb.status_code == 200, fb.text
    assert fb.json().get("case_id") == case_id
    assert fb.json().get("source") == "CUSTOMER"


def test_no_eligible_product_returns_empty_list(client):
    """non-matching concern → 200 → [] → no persisted recommendation for the case."""
    token = _token(client, "CUST-CVS-1")
    headers = {"Authorization": f"Bearer {token}"}

    created = client.post(
        "/api/v1/cases/",
        headers=headers,
        json={"customer_id": "CUST-CVS-1", "case_type": "OPEN"},
    )
    assert created.status_code == 201, created.text
    case_id = created.json()["case_id"]

    # Concerns that do not map to the seeded sunscreen use-case surface.
    gen = client.post(
        "/api/v1/recommendations/generate",
        headers=headers,
        json={
            "case_id": case_id,
            "customer_profile": {"concerns": "xyz-noncanonical-need-99"},
        },
    )
    assert gen.status_code == 200, gen.text
    body = gen.json()
    assert isinstance(body, list)
    # Strict: no eligible product must yield an empty generate payload.
    # Do not allow a non-empty ELIGIBLE list to satisfy this test.
    assert body == [], (
        "expected no recommendations for non-matching concern; "
        f"got {len(body)} item(s): {body!r}"
    )

    listed = client.get(f"/api/v1/recommendations/case/{case_id}", headers=headers)
    assert listed.status_code == 200, listed.text
    assert listed.json() == [], (
        "expected no persisted recommendations for case after empty generate; "
        f"got {listed.json()!r}"
    )


def test_create_case_for_other_customer_returns_403(client):
    token = _token(client, "CUST-CVS-1")
    r = client.post(
        "/api/v1/cases/",
        headers={"Authorization": f"Bearer {token}"},
        json={"customer_id": "CUST-CVS-2", "case_type": "OPEN"},
    )
    assert r.status_code == 403
