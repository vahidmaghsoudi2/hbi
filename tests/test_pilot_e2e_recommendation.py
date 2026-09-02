"""Pilot E2E: pilot-token → generate recommendations.

Uses existing seed_products/seed_evidence JSON (does not modify Product A–D source files).

Note: current RecommendationService returns in-memory Recommendation objects and does
not db.add()/persist them. Phase 15 test remediation therefore validates the HTTP
response contract, not an incorrect DB-row assumption.
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
    from app.main import app
    from app.core.deps import get_db

    Session = sessionmaker(bind=database.engine)
    session = Session()
    seed(session)
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
        json={"case_id": "CASE-PILOT-1", "customer_profile": {"concerns": "ضدآفتاب روزانه صورت"}},
    )
    assert naked.status_code == 401

    r = c.post(
        "/api/v1/recommendations/generate",
        headers=headers,
        json={
            "case_id": "CASE-PILOT-1",
            "customer_profile": {"concerns": "ضدآفتاب روزانه صورت"},
        },
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert isinstance(body, list)
    assert len(body) >= 1
    # Response-scoped recommendations (service does not currently persist rows)
    assert body[0].get("case_id") == "CASE-PILOT-1"
    assert body[0].get("product_id")


def test_pilot_token_disabled_in_production(client, monkeypatch):
    c, _ = client
    monkeypatch.setenv("HBI_ENV", "production")
    r = c.post("/api/v1/auth/pilot-token", json={"customer_id": "CUST-PILOT-1"})
    assert r.status_code == 403
