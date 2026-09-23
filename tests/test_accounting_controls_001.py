"""Accounting baseline v0.2 — operational control tests."""
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


def _seed(session, *, qty=5, price=10.0, customer_id="C1", product_id="P1"):
    session.add(Customer(customer_id=customer_id, name="Buyer", consent_to_store_data=1))
    session.add(
        Product(
            product_id=product_id,
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
            inventory_id=f"INV-{product_id}",
            product_id=product_id,
            quantity_available=qty,
            quantity_reserved=0,
            quantity_damaged=0,
            stock_status="active",
            sale_price_usd=price,
            sale_price_toman=1_000_000,
            purchase_price_toman=800_000,
        )
    )
    session.commit()


def _sale(session, *, qty=1, fx=1_000_000.0, key=None):
    return SaleService(session).create_sale(
        "C1",
        [{"product_id": "P1", "quantity": qty}],
        fx_rate_usd_to_irr=fx,
        idempotency_key=key,
    )


def test_sale_total_invariant(session):
    _seed(session, qty=10, price=12.5)
    sale = _sale(session, qty=3)
    session.commit()
    assert abs(float(sale.total_amount_usd) - 37.5) < 1e-9
    items = SaleService(session).get_sale_items(sale.sale_id)
    recomputed = sum(float(i.unit_price_usd) * i.quantity for i in items)
    assert abs(recomputed - float(sale.total_amount_usd)) < 1e-9


def test_payment_ceiling_rejects_overpay(session):
    _seed(session, qty=5, price=10.0)
    sale = _sale(session, qty=1)
    session.commit()
    svc = PaymentService(session)
    svc.record_payment(
        sale_id=sale.sale_id, customer_id="C1", method="CASH",
        amount_usd=10.0, fx_rate_usd_to_irr=1_000_000.0,
    )
    session.commit()
    with pytest.raises(ValueError, match="payment exceeds sale total"):
        svc.record_payment(
            sale_id=sale.sale_id, customer_id="C1", method="CASH",
            amount_usd=0.01, fx_rate_usd_to_irr=1_000_000.0,
        )


def test_payment_ceiling_allows_exact_and_partial(session):
    _seed(session, qty=5, price=10.0)
    sale = _sale(session, qty=1)
    session.commit()
    svc = PaymentService(session)
    svc.record_payment(
        sale_id=sale.sale_id, customer_id="C1", method="CASH",
        amount_usd=4.0, fx_rate_usd_to_irr=1_000_000.0,
    )
    session.commit()
    svc.record_payment(
        sale_id=sale.sale_id, customer_id="C1", method="CARD",
        amount_usd=6.0, fx_rate_usd_to_irr=1_000_000.0,
    )
    session.commit()
    with pytest.raises(ValueError, match="payment exceeds sale total"):
        svc.record_payment(
            sale_id=sale.sale_id, customer_id="C1", method="CASH",
            amount_usd=0.01, fx_rate_usd_to_irr=1_000_000.0,
        )


def test_payment_idempotency(session):
    _seed(session, qty=5, price=10.0)
    sale = _sale(session, qty=1)
    session.commit()
    svc = PaymentService(session)
    p1 = svc.record_payment(
        sale_id=sale.sale_id, customer_id="C1", method="CASH",
        amount_usd=5.0, fx_rate_usd_to_irr=1_000_000.0, idempotency_key="pay-1",
    )
    session.commit()
    p2 = svc.record_payment(
        sale_id=sale.sale_id, customer_id="C1", method="CASH",
        amount_usd=5.0, fx_rate_usd_to_irr=1_000_000.0, idempotency_key="pay-1",
    )
    session.commit()
    assert p1.payment_id == p2.payment_id
    assert len(svc.list_by_sale(sale.sale_id, customer_id="C1")) == 1


def test_sale_idempotency(session):
    _seed(session, qty=5, price=10.0)
    s1 = _sale(session, qty=1, key="sale-1")
    session.commit()
    s2 = _sale(session, qty=1, key="sale-1")
    session.commit()
    assert s1.sale_id == s2.sale_id
    inv = session.query(Inventory).filter_by(product_id="P1").one()
    assert inv.quantity_available == 4


def test_inventory_sequential_oversell_blocked(session):
    _seed(session, qty=1, price=10.0)
    _sale(session, qty=1)
    session.commit()
    with pytest.raises(ValueError, match="insufficient stock"):
        _sale(session, qty=1)


def test_return_quantity_boundary(session):
    _seed(session, qty=5, price=10.0)
    sale = _sale(session, qty=2)
    session.commit()
    ret = ReturnService(session)
    ret.create_return(sale_id=sale.sale_id, product_id="P1", quantity=2, reason="test")
    session.commit()
    with pytest.raises(ValueError, match="exceed|remaining|already"):
        ret.create_return(sale_id=sale.sale_id, product_id="P1", quantity=1, reason="again")


def test_payment_preserves_sale_historical_totals(session):
    _seed(session, qty=5, price=10.0)
    sale = _sale(session, qty=1)
    session.commit()
    prior = (sale.total_amount_usd, sale.total_amount_irr, sale.total_amount_toman, sale.fx_rate_usd_to_irr)
    PaymentService(session).record_payment(
        sale_id=sale.sale_id, customer_id="C1", method="CASH",
        amount_usd=10.0, fx_rate_usd_to_irr=1_000_000.0,
    )
    session.commit()
    session.refresh(sale)
    assert (sale.total_amount_usd, sale.total_amount_irr, sale.total_amount_toman, sale.fx_rate_usd_to_irr) == prior


def test_return_preserves_sale_historical_totals(session):
    _seed(session, qty=5, price=10.0)
    sale = _sale(session, qty=1)
    session.commit()
    prior = (sale.total_amount_usd, sale.total_amount_irr, sale.total_amount_toman, sale.fx_rate_usd_to_irr)
    ReturnService(session).create_return(sale_id=sale.sale_id, product_id="P1", quantity=1, reason="r")
    session.commit()
    session.refresh(sale)
    assert (sale.total_amount_usd, sale.total_amount_irr, sale.total_amount_toman, sale.fx_rate_usd_to_irr) == prior


def test_payment_authorization_foreign_customer(session):
    _seed(session, qty=5, price=10.0)
    sale = _sale(session, qty=1)
    session.commit()
    session.add(Customer(customer_id="C2", name="Other", consent_to_store_data=1))
    session.commit()
    with pytest.raises(PermissionError):
        PaymentService(session).record_payment(
            sale_id=sale.sale_id, customer_id="C2", method="CASH",
            amount_usd=1.0, fx_rate_usd_to_irr=1_000_000.0,
        )


def test_sale_rollback_leaves_no_orphan_on_failure(session):
    _seed(session, qty=5, price=10.0)
    session.add(Product(product_id="P2", brand="B", product_name="N2", identity_status="VERIFIED", qa_verdict="PENDING", status="ACTIVE"))
    session.commit()
    with pytest.raises(ValueError, match="Inventory"):
        SaleService(session).create_sale(
            "C1",
            [{"product_id": "P1", "quantity": 1}, {"product_id": "P2", "quantity": 1}],
            fx_rate_usd_to_irr=1_000_000.0,
        )
    session.rollback()
    assert session.query(Sale).count() == 0
    assert session.query(StockMovement).count() == 0
    assert session.query(Inventory).filter_by(product_id="P1").one().quantity_available == 5


def test_stock_movement_created_for_sale(session):
    _seed(session, qty=5, price=10.0)
    sale = _sale(session, qty=2)
    session.commit()
    moves = session.query(StockMovement).filter_by(reference_id=sale.sale_id).all()
    assert len(moves) == 1
    assert moves[0].movement_type == "SALE"
    assert moves[0].quantity_delta == -2
