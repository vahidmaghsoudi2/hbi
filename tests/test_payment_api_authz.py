"""Payment API authorization tests for Team 2 Business Core.

Proves that authenticated customers cannot read or mutate payments belonging
to another customer's Sale.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.deps import get_db, get_current_customer_id
from app.models.customer import Customer
from app.models.sale import Sale
from app.models.payment import Payment


@pytest.fixture()
def api_client(db_session):
    def _override_db():
        yield db_session

    def _override_customer():
        return "CUST-PAY-A"

    app.dependency_overrides[get_db] = _override_db
    app.dependency_overrides[get_current_customer_id] = _override_customer

    db_session.add(Customer(customer_id="CUST-PAY-A", name="A", consent_to_store_data=1))
    db_session.add(Customer(customer_id="CUST-PAY-B", name="B", consent_to_store_data=1))
    db_session.add(Sale(
        sale_id="SALE-PAY-B",
        customer_id="CUST-PAY-B",
        total_amount_toman=100000,
        total_amount_usd=10.0,
        fx_rate_usd_to_irr=1000000,
        total_amount_irr=10000000,
    ))
    db_session.add(Payment(
        payment_id="PAY-B-1",
        sale_id="SALE-PAY-B",
        method="CASH",
        amount_usd=10.0,
        fx_rate_usd_to_irr=1000000,
        amount_irr=10000000,
        amount_toman=1000000,
    ))
    db_session.commit()

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


def test_other_customer_payment_sale_is_forbidden(api_client):
    client = api_client
    response = client.get("/api/v1/payments/sale/SALE-PAY-B")
    assert response.status_code == 403


def test_other_customer_payment_is_forbidden(api_client):
    client = api_client
    response = client.get("/api/v1/payments/PAY-B-1")
    assert response.status_code == 403


def test_other_customer_sale_cannot_receive_payment(api_client):
    client = api_client
    response = client.post("/api/v1/payments/", json={
        "sale_id": "SALE-PAY-B",
        "method": "CASH",
        "amount_usd": 1,
        "fx_rate_usd_to_irr": 1000000,
    })
    assert response.status_code == 403
