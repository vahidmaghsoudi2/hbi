"""D1 — Home Sales may read single-product inventory with customer token."""

from app.core.auth import create_access_token
from app.models.customer import Customer
from app.models.inventory import Inventory
from app.models.product import Product
from app.models.sale import Sale
from app.models.sale_item import SaleItem
from app.models.user_role import ROLE_ADMIN, UserRole


def _auth(sub: str):
    return {"Authorization": f"Bearer {create_access_token({'sub': sub})}"}


def _seed(db):
    db.add(Customer(customer_id="C-SALE", name="Seller Customer", consent_to_store_data=1))
    db.add(
        Product(
            product_id="P-SALE",
            brand="B",
            product_name="Sellable",
            identity_status="VERIFIED",
            qa_verdict="VALID",
            status="ACTIVE",
        )
    )
    db.flush()
    db.add(
        Inventory(
            inventory_id="INV-SALE",
            product_id="P-SALE",
            quantity_available=3,
            quantity_reserved=0,
            quantity_damaged=0,
            stock_status="active",
            sale_price_usd=12.0,
            sale_price_toman=1_200_000,
            purchase_price_toman=900_000,
        )
    )
    db.commit()


def test_customer_reads_inventory_then_creates_sale(client, db_session):
    _seed(db_session)
    h = _auth("C-SALE")
    inv = client.get("/api/v1/inventory/product/P-SALE", headers=h)
    assert inv.status_code == 200, inv.text
    assert inv.json()["sale_price_toman"] == 1_200_000
    assert inv.json()["quantity_available"] == 3

    sale = client.post(
        "/api/v1/sales/",
        json={
            "customer_id": "C-SALE",
            "items": [{"product_id": "P-SALE", "quantity": 1}],
            "fx_rate_usd_to_irr": 1_000_000.0,
        },
        headers=h,
    )
    assert sale.status_code == 201, sale.text
    inv2 = client.get("/api/v1/inventory/product/P-SALE", headers=h)
    assert inv2.status_code == 200
    assert inv2.json()["quantity_available"] == 2


def test_unauthenticated_cannot_read_or_mutate_inventory(client, db_session):
    _seed(db_session)
    assert client.get("/api/v1/inventory/product/P-SALE").status_code == 401
    assert client.post(
        "/api/v1/inventory/stock-in",
        json={
            "product_id": "P-SALE",
            "quantity": 1,
            "purchase_price_usd": 1.0,
            "fx_rate_usd_to_irr": 1_000_000.0,
        },
    ).status_code == 401


def test_customer_cannot_stock_in(client, db_session):
    _seed(db_session)
    r = client.post(
        "/api/v1/inventory/stock-in",
        json={
            "product_id": "P-SALE",
            "quantity": 5,
            "purchase_price_usd": 1.0,
            "fx_rate_usd_to_irr": 1_000_000.0,
        },
        headers=_auth("C-SALE"),
    )
    assert r.status_code == 403
    inv = client.get("/api/v1/inventory/product/P-SALE", headers=_auth("C-SALE"))
    assert inv.json()["quantity_available"] == 3
