"""PHASE 10 — Returns workflow tests. In-memory only. No data/hbi.db."""
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
from app.models.sale_return import SaleReturn
from app.models.stock_movement import StockMovement
from app.services.sale_service import SaleService
from app.services.return_service import ReturnService


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


def _sold(session, qty_sold=3, stock_start=10):
    session.add(Customer(customer_id="C1", name="B", consent_to_store_data=1))
    session.add(
        Product(
            product_id="P1",
            brand="B",
            product_name="N",
            identity_status="VERIFIED",
            qa_verdict="PENDING",
            status="ACTIVE",
        )
    )
    session.flush()
    session.add(
        Inventory(
            inventory_id="INV-P1",
            product_id="P1",
            quantity_available=stock_start,
            quantity_reserved=0,
            quantity_damaged=0,
            stock_status="active",
            sale_price_usd=10.0,
            sale_price_toman=1_000_000,
            purchase_price_toman=800_000,
        )
    )
    session.commit()
    sale = SaleService(session).create_sale(
        "C1",
        [{"product_id": "P1", "quantity": qty_sold, "unit_price_usd": 10.0}],
        fx_rate_usd_to_irr=1_000_000.0,
    )
    session.commit()
    return sale


def test_successful_return(session):
    sale = _sold(session, qty_sold=3, stock_start=10)
    assert session.get(Inventory, "INV-P1").quantity_available == 7
    ret = ReturnService(session).create_return(
        sale_id=sale.sale_id, product_id="P1", quantity=2
    )
    session.commit()
    assert ret.quantity == 2
    assert ret.sale_id == sale.sale_id
    assert ret.product_id == "P1"
    assert session.get(Inventory, "INV-P1").quantity_available == 9
    mov = session.query(StockMovement).filter_by(reference_id=ret.return_id).one()
    assert mov.movement_type == "RETURN_IN"
    assert mov.quantity_delta == 2
    assert mov.quantity_after == 9


def test_zero_and_negative_rejected(session):
    sale = _sold(session)
    with pytest.raises(ValueError, match="quantity must be positive"):
        ReturnService(session).create_return(
            sale_id=sale.sale_id, product_id="P1", quantity=0
        )
    with pytest.raises(ValueError, match="quantity must be positive"):
        ReturnService(session).create_return(
            sale_id=sale.sale_id, product_id="P1", quantity=-1
        )


def test_exceeds_sold_rejected(session):
    sale = _sold(session, qty_sold=2)
    with pytest.raises(ValueError, match="exceeds remaining"):
        ReturnService(session).create_return(
            sale_id=sale.sale_id, product_id="P1", quantity=5
        )


def test_repeated_return_boundary(session):
    sale = _sold(session, qty_sold=3)
    svc = ReturnService(session)
    svc.create_return(sale_id=sale.sale_id, product_id="P1", quantity=2)
    session.commit()
    with pytest.raises(ValueError, match="exceeds remaining"):
        svc.create_return(sale_id=sale.sale_id, product_id="P1", quantity=2)
    session.rollback()
    svc.create_return(sale_id=sale.sale_id, product_id="P1", quantity=1)
    session.commit()
    assert session.query(SaleReturn).count() == 2


def test_missing_sale_and_item(session):
    with pytest.raises(ValueError, match="Sale .* not found"):
        ReturnService(session).create_return(
            sale_id="NO", product_id="P1", quantity=1
        )
    sale = _sold(session)
    with pytest.raises(ValueError, match="SaleItem .* not found"):
        ReturnService(session).create_return(
            sale_id=sale.sale_id, product_id="OTHER", quantity=1
        )


def test_sale_totals_unchanged(session):
    sale = _sold(session, qty_sold=2)
    prior = (
        sale.total_amount_usd,
        sale.total_amount_irr,
        sale.total_amount_toman,
        sale.fx_rate_usd_to_irr,
    )
    ReturnService(session).create_return(
        sale_id=sale.sale_id, product_id="P1", quantity=1
    )
    session.commit()
    s = session.get(Sale, sale.sale_id)
    assert (
        s.total_amount_usd,
        s.total_amount_irr,
        s.total_amount_toman,
        s.fx_rate_usd_to_irr,
    ) == prior


def test_rollback_on_failure(session):
    sale = _sold(session, qty_sold=1, stock_start=5)
    before = session.get(Inventory, "INV-P1").quantity_available
    with pytest.raises(ValueError):
        ReturnService(session).create_return(
            sale_id=sale.sale_id, product_id="P1", quantity=0
        )
    session.rollback()
    assert session.get(Inventory, "INV-P1").quantity_available == before
    assert session.query(SaleReturn).count() == 0
