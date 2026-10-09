"""Positive Admin sale persistence + negative staff-session / customer denial.

Contract sources (do not invent fields):
- POST /api/v1/sales/ requires Admin via require_any_role(ROLE_ADMIN)
- SaleCreateRequest: customer_id, items[{product_id, quantity, ...}], fx_rate_usd_to_irr > 0
- SaleService.create_sale decrements Inventory.quantity_available; needs sale_price_usd
- Sale row: sale_id, customer_id, total_amount_*, fx_rate_usd_to_irr, document_status
"""
from __future__ import annotations

from app.core.auth import create_access_token
from app.models.customer import Customer
from app.models.inventory import Inventory
from app.models.product import Product
from app.models.sale import Sale
from app.models.sale_item import SaleItem
from app.models.user_role import ROLE_ADMIN, UserRole


PRODUCT_ID = "PROD-ADMIN-SALE-PERSIST"
CUSTOMER_ID = "CUST-ADMIN-SALE-PERSIST"
ADMIN_SUB = "ADMIN-SALE-PERSIST"
INV_ID = "INV-ADMIN-SALE-PERSIST"
INITIAL_QTY = 5
SALE_QTY = 2
FX = 500000.0
UNIT_USD = 10.0


def _grant_admin(db_session, subject_id: str = ADMIN_SUB) -> str:
    db_session.add(
        UserRole(
            user_role_id=f"UR-{subject_id}",
            subject_id=subject_id,
            role=ROLE_ADMIN,
        )
    )
    db_session.commit()
    return create_access_token({"sub": subject_id})


def _seed_sellable(db_session) -> None:
    # Parent-first commits under PRAGMA foreign_keys=ON (same pattern as rec_sale_trace).
    db_session.add(
        Customer(customer_id=CUSTOMER_ID, name="خریدار تست", consent_to_store_data=1)
    )
    db_session.commit()
    db_session.add(
        Product(
            product_id=PRODUCT_ID,
            brand="Brand",
            product_name="Admin Sale Persist Product",
            identity_status="VERIFIED",
            qa_verdict="VALID",
            status="ACTIVE",
        )
    )
    db_session.commit()
    db_session.add(
        Inventory(
            inventory_id=INV_ID,
            product_id=PRODUCT_ID,
            quantity_available=INITIAL_QTY,
            quantity_reserved=0,
            quantity_damaged=0,
            stock_status="active",
            sale_price_usd=UNIT_USD,
            sale_price_toman=int(UNIT_USD * FX),
        )
    )
    db_session.commit()


def test_admin_sale_persists_sale_row_and_decrements_inventory(client, db_session):
    _seed_sellable(db_session)
    admin_token = _grant_admin(db_session)

    assert db_session.query(Sale).count() == 0
    inv_before = db_session.get(Inventory, INV_ID)
    assert inv_before is not None
    assert inv_before.quantity_available == INITIAL_QTY

    response = client.post(
        "/api/v1/sales/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "customer_id": CUSTOMER_ID,
            "items": [{"product_id": PRODUCT_ID, "quantity": SALE_QTY}],
            "fx_rate_usd_to_irr": FX,
            "idempotency_key": "idem-admin-sale-persist-001",
        },
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body.get("sale_id")
    assert body.get("customer_id") == CUSTOMER_ID

    db_session.expire_all()
    sales = db_session.query(Sale).all()
    assert len(sales) == 1
    sale = sales[0]
    assert sale.sale_id == body["sale_id"]
    assert sale.customer_id == CUSTOMER_ID
    assert sale.fx_rate_usd_to_irr == FX
    assert (sale.document_status or "ACTIVE") == "ACTIVE"

    items = db_session.query(SaleItem).filter(SaleItem.sale_id == sale.sale_id).all()
    assert len(items) == 1
    assert items[0].product_id == PRODUCT_ID
    assert items[0].quantity == SALE_QTY

    inv_after = db_session.get(Inventory, INV_ID)
    assert inv_after is not None
    assert inv_after.quantity_available == INITIAL_QTY - SALE_QTY


def test_customer_token_cannot_create_sale_or_change_inventory(client, db_session):
    _seed_sellable(db_session)
    customer_token = create_access_token({"sub": CUSTOMER_ID})

    response = client.post(
        "/api/v1/sales/",
        headers={"Authorization": f"Bearer {customer_token}"},
        json={
            "customer_id": CUSTOMER_ID,
            "items": [{"product_id": PRODUCT_ID, "quantity": 1}],
            "fx_rate_usd_to_irr": FX,
        },
    )
    assert response.status_code == 403, response.text

    db_session.expire_all()
    assert db_session.query(Sale).count() == 0
    inv = db_session.get(Inventory, INV_ID)
    assert inv is not None
    assert inv.quantity_available == INITIAL_QTY


def test_staff_customer_session_cannot_create_sale_or_change_inventory(client, db_session):
    _seed_sellable(db_session)
    admin_token = _grant_admin(db_session, "ADMIN-FOR-STAFF-SESSION")

    session_response = client.post(
        "/api/v1/auth/staff-customer-session",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"customer_id": CUSTOMER_ID},
    )
    assert session_response.status_code == 200, session_response.text
    staff_token = session_response.json()["access_token"]

    response = client.post(
        "/api/v1/sales/",
        headers={"Authorization": f"Bearer {staff_token}"},
        json={
            "customer_id": CUSTOMER_ID,
            "items": [{"product_id": PRODUCT_ID, "quantity": 1}],
            "fx_rate_usd_to_irr": FX,
        },
    )
    assert response.status_code == 403, response.text

    db_session.expire_all()
    assert db_session.query(Sale).count() == 0
    inv = db_session.get(Inventory, INV_ID)
    assert inv is not None
    assert inv.quantity_available == INITIAL_QTY
