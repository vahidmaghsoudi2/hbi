"""PRICING-FX-002 — current sale display derives from operational FX without mutating snapshots."""
from app.core.auth import create_access_token
from app.models.customer import Customer
from app.models.inventory import Inventory
from app.models.product import Product
from app.models.sale import Sale
from app.models.user_role import ROLE_EDITOR, UserRole
from app.services.operational_fx_service import OperationalFxService


def _auth(subject: str):
    return {"Authorization": f"Bearer {create_access_token({'sub': subject})}"}


def _seed(db):
    db.add(Product(
        product_id="FX-PRICE-TEST",
        brand="TestBrand",
        product_name="FX Price Test",
        identity_status="VERIFIED",
        qa_verdict="VALID",
        status="ACTIVE",
    ))
    db.add(Customer(customer_id="FX-CUSTOMER", name="FX snapshot test"))
    db.flush()
    db.add(Inventory(
        inventory_id="INV-FX-PRICE-TEST",
        product_id="FX-PRICE-TEST",
        quantity_available=5,
        quantity_reserved=0,
        quantity_damaged=0,
        stock_status="active",
        purchase_price_usd=9.0,
        sale_price_usd=25.0,
        sale_price_toman=999,
        sale_price_irr=9990,
        price_fx_rate_usd_to_irr=399600,
    ))
    db.add(UserRole(
        user_role_id="ROLE-FX-EDITOR",
        subject_id="FX-EDITOR",
        role=ROLE_EDITOR,
    ))
    db.add(Sale(
        sale_id="SALE-FX-SNAPSHOT",
        customer_id="FX-CUSTOMER",
        total_amount_toman=4_000_000,
        total_amount_usd=40.0,
        fx_rate_usd_to_irr=1_000_000.0,
        total_amount_irr=40_000_000.0,
        document_status="ACTIVE",
    ))
    db.commit()


def test_current_sale_price_uses_current_fx_and_preserves_sale_snapshot(client, db_session):
    _seed(db_session)
    fx = OperationalFxService(db_session)
    fx.set_rate(1_000_000.0, note="fx-1")
    db_session.commit()

    sale = db_session.query(Sale).filter_by(sale_id="SALE-FX-SNAPSHOT").one()
    original_snapshot = (
        sale.total_amount_toman,
        sale.total_amount_usd,
        sale.fx_rate_usd_to_irr,
        sale.total_amount_irr,
    )

    first = client.get("/api/v1/inventory/product/FX-PRICE-TEST", headers=_auth("FX-EDITOR"))
    assert first.status_code == 200, first.text
    assert first.json()["sale_price_usd"] == 25.0
    assert first.json()["current_fx_rate_usd_to_irr"] == 1_000_000.0
    assert first.json()["current_sale_price_irr"] == 25_000_000.0
    assert first.json()["current_sale_price_toman"] == 2_500_000

    fx.set_rate(1_100_000.0, note="fx-2")
    db_session.commit()

    second = client.get("/api/v1/inventory/product/FX-PRICE-TEST", headers=_auth("FX-EDITOR"))
    assert second.status_code == 200, second.text
    assert second.json()["sale_price_usd"] == 25.0
    assert second.json()["current_fx_rate_usd_to_irr"] == 1_100_000.0
    assert second.json()["current_sale_price_irr"] == 27_500_000.0
    assert second.json()["current_sale_price_toman"] == 2_750_000

    db_session.refresh(sale)
    assert (
        sale.total_amount_toman,
        sale.total_amount_usd,
        sale.fx_rate_usd_to_irr,
        sale.total_amount_irr,
    ) == original_snapshot
    inventory = db_session.query(Inventory).filter_by(inventory_id="INV-FX-PRICE-TEST").one()
    assert inventory.sale_price_usd == 25.0
    assert inventory.purchase_price_usd == 9.0


def test_current_sale_price_stays_unavailable_without_fx(client, db_session):
    _seed(db_session)
    response = client.get("/api/v1/inventory/product/FX-PRICE-TEST", headers=_auth("FX-EDITOR"))
    assert response.status_code == 200, response.text
    assert response.json()["sale_price_usd"] == 25.0
    assert response.json()["current_fx_rate_usd_to_irr"] is None
    assert response.json()["current_sale_price_irr"] is None
    assert response.json()["current_sale_price_toman"] is None
