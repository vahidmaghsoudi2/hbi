"""PHASE 08 — Sales workflow tests. In-memory only. No data/hbi.db."""
from __future__ import annotations

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.models.base import Base
from app.models.customer import Customer
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.sale import Sale
from app.models.sale_item import SaleItem
from app.models.stock_movement import StockMovement
from app.services.sale_service import SaleService


@pytest.fixture()
def session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def _fk(dbapi_connection, connection_record):
        cur = dbapi_connection.cursor()
        cur.execute("PRAGMA foreign_keys=ON")
        cur.close()

    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def _seed(session, pid="P-SALE-1", qty=10, status="ACTIVE"):
    session.add(
        Customer(customer_id="CUST-1", name="Buyer", consent_to_store_data=1)
    )
    session.add(
        Product(
            product_id=pid,
            brand="B",
            product_name="N",
            identity_status="VERIFIED",
            qa_verdict="PENDING",
            status=status,
        )
    )
    session.flush()
    session.add(
        Inventory(
            inventory_id=f"INV-{pid}",
            product_id=pid,
            quantity_available=qty,
            quantity_reserved=0,
            quantity_damaged=0,
            stock_status="active",
            sale_price_toman=2_000_000,
            sale_price_usd=20.0,
            purchase_price_toman=1_500_000,
        )
    )
    session.commit()


def test_successful_sale(session):
    _seed(session, qty=10)
    svc = SaleService(session)
    sale = svc.create_sale(
        "CUST-1",
        [{"product_id": "P-SALE-1", "quantity": 2, "unit_price_usd": 20.0}],
        fx_rate_usd_to_irr=1_000_000.0,
    )
    session.commit()
    assert sale.sale_id
    assert sale.customer_id == "CUST-1"
    assert sale.total_amount_usd == pytest.approx(40.0)
    assert sale.fx_rate_usd_to_irr == 1_000_000.0
    items = svc.get_sale_items(sale.sale_id)
    assert len(items) == 1
    assert items[0].quantity == 2
    inv = session.get(Inventory, "INV-P-SALE-1")
    assert inv.quantity_available == 8
    moves = session.query(StockMovement).filter_by(reference_id=sale.sale_id).all()
    assert len(moves) == 1
    assert moves[0].movement_type == "SALE"
    assert moves[0].quantity_delta == -2
    assert moves[0].quantity_after == 8


def test_insufficient_stock_rejected(session):
    _seed(session, qty=1)
    with pytest.raises(ValueError, match="insufficient"):
        SaleService(session).create_sale(
            "CUST-1",
            [{"product_id": "P-SALE-1", "quantity": 5, "unit_price_usd": 10.0}],
            fx_rate_usd_to_irr=1_000_000.0,
        )
    session.rollback()
    assert session.get(Inventory, "INV-P-SALE-1").quantity_available == 1
    assert session.query(Sale).count() == 0
    assert session.query(StockMovement).count() == 0


def test_inactive_product_rejected(session):
    _seed(session, status="DRAFT")
    with pytest.raises(ValueError, match="not ACTIVE"):
        SaleService(session).create_sale(
            "CUST-1",
            [{"product_id": "P-SALE-1", "quantity": 1, "unit_price_usd": 10.0}],
            fx_rate_usd_to_irr=1_000_000.0,
        )


def test_missing_product_rejected(session):
    session.add(Customer(customer_id="CUST-1", name="B", consent_to_store_data=0))
    session.commit()
    with pytest.raises(ValueError, match="Product .* not found"):
        SaleService(session).create_sale(
            "CUST-1",
            [{"product_id": "NOPE", "quantity": 1, "unit_price_usd": 1.0}],
            fx_rate_usd_to_irr=1_000_000.0,
        )


def test_missing_inventory_rejected(session):
    session.add(Customer(customer_id="CUST-1", name="B", consent_to_store_data=0))
    session.add(
        Product(
            product_id="P-ONLY",
            brand="B",
            product_name="N",
            identity_status="VERIFIED",
            qa_verdict="PENDING",
            status="ACTIVE",
        )
    )
    session.commit()
    with pytest.raises(ValueError, match="Inventory .* not found"):
        SaleService(session).create_sale(
            "CUST-1",
            [{"product_id": "P-ONLY", "quantity": 1, "unit_price_usd": 1.0}],
            fx_rate_usd_to_irr=1_000_000.0,
        )


def test_missing_customer_rejected(session):
    with pytest.raises(ValueError, match="Customer .* not found"):
        SaleService(session).create_sale(
            "NO-CUST",
            [{"product_id": "P", "quantity": 1, "unit_price_usd": 1.0}],
            fx_rate_usd_to_irr=1_000_000.0,
        )


def test_quantity_validation(session):
    _seed(session)
    with pytest.raises(ValueError, match="quantity must be positive"):
        SaleService(session).create_sale(
            "CUST-1",
            [{"product_id": "P-SALE-1", "quantity": 0, "unit_price_usd": 1.0}],
            fx_rate_usd_to_irr=1_000_000.0,
        )


def test_fx_required(session):
    _seed(session)
    with pytest.raises(ValueError, match="fx_rate_usd_to_irr"):
        SaleService(session).create_sale(
            "CUST-1",
            [{"product_id": "P-SALE-1", "quantity": 1, "unit_price_usd": 1.0}],
            fx_rate_usd_to_irr=0,
        )


def test_currency_and_fx_snapshot(session):
    _seed(session)
    sale = SaleService(session).create_sale(
        "CUST-1",
        [{"product_id": "P-SALE-1", "quantity": 1, "unit_price_usd": 15.0}],
        fx_rate_usd_to_irr=1_000_000.0,
    )
    session.commit()
    assert sale.total_amount_usd == pytest.approx(15.0)
    assert sale.total_amount_irr == pytest.approx(15_000_000.0)
    assert sale.total_amount_toman == 1_500_000
    item = SaleService(session).get_sale_items(sale.sale_id)[0]
    assert item.unit_price_usd == pytest.approx(15.0)
    assert item.fx_rate_usd_to_irr == 1_000_000.0
    mov = session.query(StockMovement).filter_by(reference_id=sale.sale_id).one()
    assert mov.fx_rate_usd_to_irr == 1_000_000.0


def test_purchase_toman_preserved(session):
    _seed(session)
    SaleService(session).create_sale(
        "CUST-1",
        [{"product_id": "P-SALE-1", "quantity": 1, "unit_price_usd": 20.0}],
        fx_rate_usd_to_irr=1_000_000.0,
    )
    session.commit()
    inv = session.get(Inventory, "INV-P-SALE-1")
    assert inv.purchase_price_toman == 1_500_000
