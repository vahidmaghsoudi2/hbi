"""PHASE 09 — Payment workflow tests. In-memory only. No data/hbi.db."""
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
from app.models.payment import Payment
from app.services.sale_service import SaleService
from app.services.payment_service import PaymentService, VALID_METHODS


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


def _sale(session, qty=5):
    session.add(Customer(customer_id="C1", name="Buyer", consent_to_store_data=1))
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
            quantity_available=qty,
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
        [{"product_id": "P1", "quantity": 1, "unit_price_usd": 10.0}],
        fx_rate_usd_to_irr=1_000_000.0,
    )
    session.commit()
    return sale


@pytest.mark.parametrize("method", sorted(VALID_METHODS))
def test_successful_methods(session, method):
    sale = _sale(session)
    pay = PaymentService(session).record_payment(
        sale_id=sale.sale_id,
        method=method,
        amount_usd=10.0,
        fx_rate_usd_to_irr=1_000_000.0,
    )
    session.commit()
    assert pay.method == method
    assert pay.sale_id == sale.sale_id
    assert pay.amount_usd == pytest.approx(10.0)


def test_invalid_method_rejected(session):
    sale = _sale(session)
    with pytest.raises(ValueError, match="invalid payment method"):
        PaymentService(session).record_payment(
            sale_id=sale.sale_id,
            method="CRYPTO",
            amount_usd=1.0,
            fx_rate_usd_to_irr=1_000_000.0,
        )


def test_missing_sale_rejected(session):
    with pytest.raises(ValueError, match="Sale .* not found"):
        PaymentService(session).record_payment(
            sale_id="NO-SALE",
            method="CASH",
            amount_usd=1.0,
            fx_rate_usd_to_irr=1_000_000.0,
        )


def test_invalid_amount_rejected(session):
    sale = _sale(session)
    with pytest.raises(ValueError, match="amount_usd must be > 0"):
        PaymentService(session).record_payment(
            sale_id=sale.sale_id,
            method="CASH",
            amount_usd=0,
            fx_rate_usd_to_irr=1_000_000.0,
        )


def test_currency_and_fx_snapshot(session):
    sale = _sale(session)
    r = 1_000_000.0
    pay = PaymentService(session).record_payment(
        sale_id=sale.sale_id,
        method="CARD",
        amount_usd=5.0,
        fx_rate_usd_to_irr=r,
    )
    session.commit()
    assert pay.amount_irr == pytest.approx(5_000_000.0)
    assert pay.amount_toman == 500_000
    assert pay.fx_rate_usd_to_irr == r


def test_sale_totals_unchanged(session):
    sale = _sale(session)
    prior_usd = sale.total_amount_usd
    prior_irr = sale.total_amount_irr
    prior_toman = sale.total_amount_toman
    prior_fx = sale.fx_rate_usd_to_irr
    PaymentService(session).record_payment(
        sale_id=sale.sale_id,
        method="TRANSFER",
        amount_usd=3.0,
        fx_rate_usd_to_irr=1_100_000.0,
    )
    session.commit()
    refreshed = session.get(Sale, sale.sale_id)
    assert refreshed.total_amount_usd == prior_usd
    assert refreshed.total_amount_irr == prior_irr
    assert refreshed.total_amount_toman == prior_toman
    assert refreshed.fx_rate_usd_to_irr == prior_fx


def test_list_by_sale_traceability(session):
    sale = _sale(session)
    svc = PaymentService(session)
    svc.record_payment(
        sale_id=sale.sale_id, method="CASH", amount_usd=2.0, fx_rate_usd_to_irr=1_000_000.0
    )
    svc.record_payment(
        sale_id=sale.sale_id, method="CARD", amount_usd=3.0, fx_rate_usd_to_irr=1_000_000.0
    )
    session.commit()
    rows = svc.list_by_sale(sale.sale_id)
    assert len(rows) == 2
    assert {r.method for r in rows} == {"CASH", "CARD"}


def test_rollback_on_failure(session):
    sale = _sale(session)
    with pytest.raises(ValueError):
        PaymentService(session).record_payment(
            sale_id=sale.sale_id,
            method="BAD",
            amount_usd=1.0,
            fx_rate_usd_to_irr=1_000_000.0,
        )
    session.rollback()
    assert session.query(Payment).count() == 0
