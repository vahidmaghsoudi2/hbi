"""Pilot E2E: pilot-token → generate recommendations → persistence.

Uses existing seed_products/seed_evidence JSON (does not modify Product A–D source files).
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
    c, Session = client

    tok = c.post("/api/v1/auth/pilot-token", json={"customer_id": "CUST-PILOT-1"})
    assert tok.status_code == 200, tok.text
    access = tok.json()["access_token"]
    headers = {"Authorization": f"Bearer {access}"}

    # unauthenticated generate must fail
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

    # persistence
    s = Session()
    try:
        from app.models.recommendation import Recommendation

        rows = s.query(Recommendation).filter_by(case_id="CASE-PILOT-1").all()
        assert len(rows) >= 1
    finally:
        s.close()


def test_pilot_token_disabled_in_production(client, monkeypatch):
    c, _ = client
    monkeypatch.setenv("HBI_ENV", "production")
    r = c.post("/api/v1/auth/pilot-token", json={"customer_id": "CUST-PILOT-1"})
    assert r.status_code == 403
