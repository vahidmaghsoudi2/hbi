"""API path: auth required + case ownership for recommendations."""
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

TEST_DB = Path(__file__).resolve().parents[1] / "data" / "hbi_rec_api_test.db"


@pytest.fixture()
def client(monkeypatch):
    if TEST_DB.exists():
        TEST_DB.unlink()
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{TEST_DB}")

    import importlib
    import app.database as database

    importlib.reload(database)
    database.init_db()

    from app.models.customer import Customer
    from app.models.case import Case
    from app.main import app
    from app.core.deps import get_db, get_current_customer_id

    Session = sessionmaker(bind=database.engine)
    session = Session()
    session.add(Customer(customer_id="CUST-API-1", name="API User"))
    session.add(Case(case_id="CASE-API-1", customer_id="CUST-API-1"))
    session.add(Customer(customer_id="CUST-API-2", name="Other"))
    session.add(Case(case_id="CASE-API-2", customer_id="CUST-API-2"))
    session.commit()

    def _override_db():
        s = Session()
        try:
            yield s
        finally:
            s.close()

    def _owner_ok():
        return "CUST-API-1"

    app.dependency_overrides[get_db] = _override_db
    app.dependency_overrides[get_current_customer_id] = _owner_ok

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
    session.close()
    if TEST_DB.exists():
        TEST_DB.unlink()


def test_generate_requires_owned_case(client):
    # CASE-API-2 belongs to CUST-API-2; current user is CUST-API-1
    r = client.post(
        "/api/v1/recommendations/generate",
        json={"case_id": "CASE-API-2", "customer_profile": {"concerns": "x"}},
    )
    assert r.status_code == 403


def test_generate_unknown_case_404(client):
    r = client.post(
        "/api/v1/recommendations/generate",
        json={"case_id": "CASE-MISSING", "customer_profile": {}},
    )
    assert r.status_code == 404


def test_generate_owned_case_returns_list(client):
    r = client.post(
        "/api/v1/recommendations/generate",
        json={"case_id": "CASE-API-1", "customer_profile": {"concerns": "ضدآفتاب"}},
    )
    assert r.status_code == 200
    assert isinstance(r.json(), list)
