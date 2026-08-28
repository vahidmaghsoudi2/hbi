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
    database.engine.dispose()
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


def test_draft_products_excluded(client, db_session):
    """Test that DRAFT products are not recommended."""
    # Create a DRAFT product
    draft_product = Product(
        product_id="DRAFT-001",
        brand="Test",
        product_name="Draft Product",
        identity_status="VERIFIED",
        status="DRAFT",
        inventory=10
    )
    db_session.add(draft_product)
    db_session.commit()
    
    # Create a case
    case = Case(case_id="CASE-001", customer_id="CUST-001")
    db_session.add(case)
    db_session.commit()
    
    # Request recommendations
    response = client.post("/api/v1/recommendations/generate", json={"case_id": "CASE-001"})
    
    # DRAFT product should NOT be in results
    assert response.status_code == 200
    product_ids = [p["product_id"] for p in response.json()["products"]]
    assert "DRAFT-001" not in product_ids


def test_inventory_zero_excluded(client, db_session):
    """Test that products with inventory=0 are not recommended."""
    # Create a product with inventory=0
    zero_inv_product = Product(
        product_id="ZERO-INV-001",
        brand="Test",
        product_name="Zero Inventory",
        identity_status="VERIFIED",
        status="ACTIVE",
        inventory=0
    )
    db_session.add(zero_inv_product)
    db_session.commit()
    
    # Create a case
    case = Case(case_id="CASE-002", customer_id="CUST-001")
    db_session.add(case)
    db_session.commit()
    
    # Request recommendations
    response = client.post("/api/v1/recommendations/generate", json={"case_id": "CASE-002"})
    
    # Zero inventory product should NOT be in results
    assert response.status_code == 200
    product_ids = [p["product_id"] for p in response.json()["products"]]
    assert "ZERO-INV-001" not in product_ids
