"""Recommendation API tests — fixture/auth only; no production logic changes."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app as fastapi_app
from app.database import get_db
from app.models.base import Base
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.case import Case
from app.models.customer import Customer
from app.models.category import Category  # noqa: F401
from app.models.evidence import Evidence  # noqa: F401
from app.models.recommendation import Recommendation  # noqa: F401
from app.models.sale import Sale  # noqa: F401
from app.models.sale_item import SaleItem  # noqa: F401
from app.models.stock_movement import StockMovement  # noqa: F401
from app.models.payment import Payment  # noqa: F401
from app.models.sale_return import SaleReturn  # noqa: F401


@pytest.fixture()
def api_env():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def _fk(dbapi_conn, _):
        cur = dbapi_conn.cursor()
        cur.execute("PRAGMA foreign_keys=ON")
        cur.close()

    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    db = Session()

    def override_get_db():
        try:
            yield db
        finally:
            pass

    fastapi_app.dependency_overrides[get_db] = override_get_db
    client = TestClient(fastapi_app)

    customer = Customer(
        customer_id="test_customer",
        name="Test User",
        consent_to_store_data=1,
    )
    db.add(customer)
    case = Case(case_id="test_case", customer_id="test_customer")
    db.add(case)
    db.commit()

    yield client, db, case

    fastapi_app.dependency_overrides.clear()
    db.close()
    Base.metadata.drop_all(bind=engine)


def _token(client: TestClient) -> str:
    response = client.post(
        "/api/v1/auth/pilot-token", json={"customer_id": "test_customer"}
    )
    assert response.status_code == 200, response.text
    token = response.json().get("access_token")
    assert token, "Token not received"
    return token


def test_draft_products_excluded(api_env):
    client, db, case = api_env

    draft = Product(
        product_id="draft_test_001",
        brand="TestBrand",
        product_name="Draft Product",
        identity_status="VERIFIED",
        qa_verdict="VALID",
        status="DRAFT",
    )
    db.add(draft)

    active = Product(
        product_id="active_test_001",
        brand="TestBrand",
        product_name="Active Product",
        identity_status="VERIFIED",
        qa_verdict="VALID",
        status="ACTIVE",
    )
    db.add(active)
    db.flush()

    inv = Inventory(
        inventory_id="inv-active_test_001",
        product_id=active.product_id,
        quantity_available=10,
        quantity_reserved=0,
        quantity_damaged=0,
        stock_status="active",
    )
    db.add(inv)
    db.commit()

    token = _token(client)
    response = client.post(
        "/api/v1/recommendations/generate",
        json={
            "case_id": case.case_id,
            "customer_profile": {"concerns": "test"},
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    if isinstance(data, list):
        product_ids = [
            item.get("product_id") for item in data if isinstance(item, dict)
        ]
    else:
        product_ids = [
            item.get("product_id")
            for item in data.get("recommendations", data.get("products", []))
            if isinstance(item, dict)
        ]

    assert draft.product_id not in product_ids
    assert active.product_id in product_ids


def test_inventory_zero_excluded(api_env):
    client, db, case = api_env

    zero_inv = Product(
        product_id="zero_inv_test_001",
        brand="TestBrand",
        product_name="Zero Inventory Product",
        identity_status="VERIFIED",
        qa_verdict="VALID",
        status="ACTIVE",
    )
    db.add(zero_inv)
    db.flush()

    inv_zero = Inventory(
        inventory_id="inv-zero_inv_test_001",
        product_id=zero_inv.product_id,
        quantity_available=0,
        quantity_reserved=0,
        quantity_damaged=0,
        stock_status="out_of_stock",
    )
    db.add(inv_zero)
    db.commit()

    token = _token(client)
    response = client.post(
        "/api/v1/recommendations/generate",
        json={
            "case_id": case.case_id,
            "customer_profile": {"concerns": "test"},
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    if isinstance(data, list):
        product_ids = [
            item.get("product_id") for item in data if isinstance(item, dict)
        ]
    else:
        product_ids = [
            item.get("product_id")
            for item in data.get("recommendations", data.get("products", []))
            if isinstance(item, dict)
        ]

    assert zero_inv.product_id not in product_ids
