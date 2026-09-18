"""Pilot E2E: pilot-token → generate recommendations.

Uses existing seed_products/seed_evidence JSON (does not modify Product A–D source files).
The test adds one explicit QA-approved independent evidence fixture so the happy path
remains valid under Runtime-003's approved-only scoring contract.
"""
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

TEST_DB = Path(__file__).resolve().parents[1] / "data" / "hbi_pilot_e2e.db"


@pytest.fixture()
def client(monkeypatch):
    if TEST_DB.exists():
        TEST_DB.unlink()
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{TEST_DB}")
    monkeypatch.setenv("HBI_ENV", "development")

    import importlib
    import app.database as database

    importlib.reload(database)
    database.init_db()

    from scripts.seed_products_from_records import seed
    from app.models.customer import Customer
    from app.models.case import Case
    from app.models.evidence import Evidence
    from app.models.product import Product
    from app.models.product import Product
    from app.models.product_knowledge import ProductKnowledge
    from app.main import app
    from app.core.deps import get_db

    Session = sessionmaker(bind=database.engine)
    session = Session()
    seed(session)
    product = session.query(Product).filter_by(product_id="ISDIN-FOTOUTRA100-50ML").one()
    product.status = "ACTIVE"
    product.qa_verdict = "VALID"
    pk = session.query(ProductKnowledge).filter_by(
        product_id="ISDIN-FOTOUTRA100-50ML"
    ).one()
    pk.known_use_cases = "sun protection"
    session.add(Evidence(
        evidence_id="EV-PILOT-APPROVED-001",
        product_id="ISDIN-FOTOUTRA100-50ML",
        source_type="INDEPENDENT",
        source_reference="TEST-PILOT-FIXTURE",
        claim="approved test support for sunscreen use case",
        claim_type="FACT",
        evidence_status="SUPPORTED",
        qa_status="APPROVED",
        conflict_status="NONE",
    ))
    session.add(Customer(customer_id="CUST-PILOT-1", name="Pilot User"))
    session.add(Case(case_id="CASE-PILOT-1", customer_id="CUST-PILOT-1"))
    session.commit()

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
        yield c, Session

    app.dependency_overrides.clear()
    session.close()
    database.engine.dispose()
    if TEST_DB.exists():
        TEST_DB.unlink()


def test_pilot_token_and_generate_persist(client):
    c, _Session = client

    tok = c.post("/api/v1/auth/pilot-token", json={"customer_id": "CUST-PILOT-1"})
    assert tok.status_code == 200, tok.text
    access = tok.json()["access_token"]
    headers = {"Authorization": f"Bearer {access}"}

    naked = c.post(
        "/api/v1/recommendations/generate",
        json={"case_id": "CASE-PILOT-1", "customer_profile": {"concerns": "ضدآفتاب"}},
    )
    assert naked.status_code == 401

    r = c.post(
        "/api/v1/recommendations/generate",
        headers=headers,
        json={
            "case_id": "CASE-PILOT-1",
            "customer_profile": {"concerns": "ضدآفتاب"},
        },
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert isinstance(body, list)
    assert len(body) >= 1
    assert body[0].get("case_id") == "CASE-PILOT-1"
    assert body[0].get("product_id")


def test_pilot_token_disabled_in_production(client, monkeypatch):
    c, _ = client
    monkeypatch.setenv("HBI_ENV", "production")
    r = c.post("/api/v1/auth/pilot-token", json={"customer_id": "CUST-PILOT-1"})
    assert r.status_code == 403
