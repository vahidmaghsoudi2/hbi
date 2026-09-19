"""HBI-CUST-HISTORY-FOLLOWUP-001 — customer purchase history + rec trace."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app as fastapi_app
from app.database import get_db
from app.models.base import Base
from app.models.case import Case
from app.models.customer import Customer
from app.models.inventory import Inventory
from app.models.product import Product
from app.models.recommendation import Recommendation
from app.models.sale import Sale  # noqa: F401
from app.models.sale_item import SaleItem  # noqa: F401
from app.models.stock_movement import StockMovement  # noqa: F401
from app.services.sale_service import SaleService
from app.interface.facades import SaleFacade


def _seed(db):
    db.add(Customer(customer_id="CUST-H", name="Hist", consent_to_store_data=1))
    db.commit()
    db.add(Case(case_id="CASE-H", customer_id="CUST-H", case_type="CONSULTATION"))
    db.commit()
    db.add(
        Product(
            product_id="PROD-H",
            brand="B",
            product_name="P",
            identity_status="VERIFIED",
            status="ACTIVE",
            qa_verdict="VALID",
        )
    )
    db.commit()
    db.add(
        Inventory(
            inventory_id="INV-H",
            product_id="PROD-H",
            quantity_available=5,
            quantity_reserved=0,
            sale_price_usd=10.0,
            sale_price_toman=500000,
        )
    )
    db.commit()
    db.add(
        Recommendation(
            recommendation_id="REC-H",
            case_id="CASE-H",
            product_id="PROD-H",
            eligibility_status="ELIGIBLE",
            need_match_score=1.0,
            evidence_score=1.0,
            ranking_score=1.0,
        )
    )
    db.commit()


def test_history_includes_sale_items_and_recommendation_trace(db_session):
    _seed(db_session)
    SaleService(db_session).create_sale(
        "CUST-H",
        [{"product_id": "PROD-H", "quantity": 1, "recommendation_id": "REC-H"}],
        fx_rate_usd_to_irr=500000.0,
    )
    db_session.commit()
    hist = SaleFacade(db_session).find_by_customer("CUST-H")
    assert len(hist) == 1
    assert hist[0].customer_id == "CUST-H"
    assert hist[0].items and hist[0].items[0].product_id == "PROD-H"
    assert hist[0].items[0].recommendation_id == "REC-H"


def test_history_empty_for_customer_without_sales(db_session):
    db_session.add(Customer(customer_id="CUST-EMPTY", name="E", consent_to_store_data=1))
    db_session.commit()
    assert SaleFacade(db_session).find_by_customer("CUST-EMPTY") == []


def test_history_does_not_leak_other_customer_sales(db_session):
    _seed(db_session)
    db_session.add(Customer(customer_id="CUST-OTHER", name="O", consent_to_store_data=1))
    db_session.commit()
    SaleService(db_session).create_sale(
        "CUST-H",
        [{"product_id": "PROD-H", "quantity": 1, "recommendation_id": "REC-H"}],
        fx_rate_usd_to_irr=500000.0,
    )
    db_session.commit()
    assert SaleFacade(db_session).find_by_customer("CUST-OTHER") == []
    assert len(SaleFacade(db_session).find_by_customer("CUST-H")) == 1


@pytest.fixture()
def history_api_env():
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
    _seed(db)
    SaleService(db).create_sale(
        "CUST-H",
        [{"product_id": "PROD-H", "quantity": 1, "recommendation_id": "REC-H"}],
        fx_rate_usd_to_irr=500000.0,
    )
    db.commit()
    db.add(Customer(customer_id="CUST-OTHER", name="Other", consent_to_store_data=1))
    db.commit()

    yield client, db

    fastapi_app.dependency_overrides.clear()
    db.close()
    Base.metadata.drop_all(bind=engine)


def _token(client: TestClient, customer_id: str) -> str:
    response = client.post("/api/v1/auth/pilot-token", json={"customer_id": customer_id})
    assert response.status_code == 200, response.text
    token = response.json().get("access_token")
    assert token
    return token


def test_api_history_ok_for_owner(history_api_env):
    client, _ = history_api_env
    token = _token(client, "CUST-H")
    res = client.get(
        "/api/v1/sales/customer/CUST-H",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200, res.text
    data = res.json()
    assert isinstance(data, list) and len(data) >= 1
    items = data[0].get("items") or []
    assert items and items[0].get("recommendation_id") == "REC-H"


def test_api_history_forbidden_for_other_customer(history_api_env):
    client, _ = history_api_env
    token = _token(client, "CUST-OTHER")
    res = client.get(
        "/api/v1/sales/customer/CUST-H",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 403, res.text


def test_api_history_unauthorized_without_token(history_api_env):
    client, _ = history_api_env
    res = client.get("/api/v1/sales/customer/CUST-H")
    assert res.status_code in (401, 403), res.text
