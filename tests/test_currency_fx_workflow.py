"""PHASE 11 — Currency / FX tests. In-memory only. No data/hbi.db."""
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
from app.models.stock_movement import StockMovement
from app.models.payment import Payment
from app.models.sale_return import SaleReturn
from app.services.currency_fx import (
    irr_to_toman,
    irr_to_usd,
    toman_to_irr,
    toman_to_usd,
    usd_to_irr,
    usd_to_toman,
    validate_fx_rate,
)
from app.services.operational_fx_service import OperationalFxService
from app.services.stock_in_service import StockInService
from app.services.sale_service import SaleService
from app.services.payment_service import PaymentService
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


def test_conversions():
    r = 1_000_000.0
    assert usd_to_irr(12.5, r) == pytest.approx(12_500_000.0)
    assert irr_to_usd(12_500_000.0, r) == pytest.approx(12.5)
    assert irr_to_toman(12_500_000.0) == pytest.approx(1_250_000.0)
    assert toman_to_irr(1_250_000.0) == pytest.approx(12_500_000.0)
    assert usd_to_toman(12.5, r) == pytest.approx(1_250_000.0)
    assert toman_to_usd(1_250_000.0, r) == pytest.approx(12.5)


def test_fx_validation():
    assert validate_fx_rate(10) == 10.0
    with pytest.raises(ValueError):
        validate_fx_rate(0)
    with pytest.raises(ValueError):
        validate_fx_rate(-1)
    with pytest.raises(ValueError):
        validate_fx_rate(None)


def test_operational_fx_does_not_mutate_history(session):
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
            quantity_available=20,
            quantity_reserved=0,
            quantity_damaged=0,
            stock_status="active",
            sale_price_usd=10.0,
            sale_price_toman=1_000_000,
            purchase_price_toman=800_000,
        )
    )
    session.commit()

    r1 = 900_000.0
    StockInService(session).stock_in(
        product_id="P1",
        quantity=2,
        purchase_price_usd=5.0,
        fx_rate_usd_to_irr=r1,
    )
    sale = SaleService(session).create_sale(
        "C1",
        [{"product_id": "P1", "quantity": 1, "unit_price_usd": 10.0}],
        fx_rate_usd_to_irr=r1,
    )
    pay = PaymentService(session).record_payment(
        sale_id=sale.sale_id, method="CASH", amount_usd=10.0, fx_rate_usd_to_irr=r1
    )
    ret = ReturnService(session).create_return(
        sale_id=sale.sale_id, product_id="P1", quantity=1
    )
    session.commit()

    mov_fx = [
        m.fx_rate_usd_to_irr
        for m in session.query(StockMovement).all()
    ]
    sale_fx = session.get(Sale, sale.sale_id).fx_rate_usd_to_irr
    pay_fx = session.get(Payment, pay.payment_id).fx_rate_usd_to_irr
    ret_fx = session.get(SaleReturn, ret.return_id).fx_rate_usd_to_irr
    purchase_toman = session.get(Inventory, "INV-P1").purchase_price_toman

    # Update operational rate
    OperationalFxService(session).set_rate(1_500_000.0, note="new op rate")
    session.commit()

    assert session.get(Sale, sale.sale_id).fx_rate_usd_to_irr == sale_fx == r1
    assert session.get(Payment, pay.payment_id).fx_rate_usd_to_irr == pay_fx == r1
    assert session.get(SaleReturn, ret.return_id).fx_rate_usd_to_irr == ret_fx == r1
    for m in session.query(StockMovement).all():
        assert m.fx_rate_usd_to_irr in mov_fx
        assert m.fx_rate_usd_to_irr == r1
    assert session.get(Inventory, "INV-P1").purchase_price_toman == purchase_toman
    assert OperationalFxService(session).get_current_rate() == 1_500_000.0


def test_toman_preservation_on_stock_in(session):
    session.add(
        Product(
            product_id="P2",
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
            inventory_id="INV-P2",
            product_id="P2",
            quantity_available=1,
            quantity_reserved=0,
            quantity_damaged=0,
            stock_status="active",
            purchase_price_toman=500_000,
            sale_price_toman=700_000,
        )
    )
    session.commit()
    StockInService(session).stock_in(
        product_id="P2",
        quantity=1,
        purchase_price_usd=8.0,
        fx_rate_usd_to_irr=1_000_000.0,
    )
    session.commit()
    inv = session.get(Inventory, "INV-P2")
    assert inv.sale_price_toman == 700_000


def test_operational_fx_rollback(session):
    with pytest.raises(ValueError):
        OperationalFxService(session).set_rate(0)
    session.rollback()
    assert OperationalFxService(session).get_current() is None
