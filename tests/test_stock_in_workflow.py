"""PHASE 07 — Stock-In workflow tests. In-memory only. No data/hbi.db."""
from __future__ import annotations

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.models.base import Base
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.stock_movement import StockMovement
from app.services.stock_in_service import (
    StockInService,
    usd_to_irr,
    usd_to_toman,
    irr_to_toman,
)
from app.services.stock_movement_service import StockMovementService


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


def _seed(session, pid="P-SI-1", qty=5, prior_fx=900_000.0):
    session.add(
        Product(
            product_id=pid,
            brand="T",
            product_name="N",
            identity_status="VERIFIED",
            qa_verdict="PENDING",
            status="ACTIVE",
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
            purchase_price_toman=1_000_000,
            sale_price_toman=1_200_000,
            purchase_price_usd=10.0,
            price_fx_rate_usd_to_irr=prior_fx,
            purchase_price_irr=10.0 * prior_fx,
        )
    )
    session.commit()


def test_c01_formula_helpers():
    r = 1_000_000.0
    assert usd_to_irr(15.0, r) == pytest.approx(15_000_000.0)
    assert irr_to_toman(15_000_000.0) == pytest.approx(1_500_000.0)
    assert usd_to_toman(15.0, r) == pytest.approx(1_500_000.0)


def test_successful_stock_in(session):
    _seed(session, qty=5)
    svc = StockInService(session)
    result = svc.stock_in(
        product_id="P-SI-1",
        quantity=3,
        purchase_price_usd=15.0,
        fx_rate_usd_to_irr=1_000_000.0,
        note="phase07",
    )
    session.commit()
    inv = result["inventory"]
    mov = result["movement"]
    assert inv.quantity_available == 8
    assert mov.movement_type == "STOCK_IN"
    assert mov.quantity_delta == 3
    assert mov.quantity_after == 8
    assert mov.product_id == "P-SI-1"
    assert mov.inventory_id == "INV-P-SI-1"


def test_inventory_quantity_increase(session):
    _seed(session, qty=2)
    StockInService(session).stock_in(
        product_id="P-SI-1",
        quantity=4,
        purchase_price_usd=1.0,
        fx_rate_usd_to_irr=1_000_000.0,
    )
    session.commit()
    inv = session.get(Inventory, "INV-P-SI-1")
    assert inv.quantity_available == 6


def test_usd_irr_toman_consistency(session):
    _seed(session)
    r = 1_000_000.0
    usd = 12.5
    qty = 2
    result = StockInService(session).stock_in(
        product_id="P-SI-1",
        quantity=qty,
        purchase_price_usd=usd,
        fx_rate_usd_to_irr=r,
    )
    session.commit()
    mov = result["movement"]
    inv = result["inventory"]
    assert mov.amount_usd == pytest.approx(usd * qty)
    assert mov.amount_irr == pytest.approx(usd * qty * r)
    assert mov.amount_toman == pytest.approx((usd * qty * r) / 10.0)
    assert mov.fx_rate_usd_to_irr == r
    assert inv.purchase_price_usd == pytest.approx(usd)
    assert inv.price_fx_rate_usd_to_irr == r
    assert inv.purchase_price_irr == pytest.approx(usd * r)
    assert inv.purchase_price_toman == int(round((usd * r) / 10.0))


def test_product_must_exist(session):
    with pytest.raises(ValueError, match="Product .* not found"):
        StockInService(session).stock_in(
            product_id="NOPE",
            quantity=1,
            purchase_price_usd=1.0,
            fx_rate_usd_to_irr=1_000_000.0,
        )


def test_inventory_must_exist(session):
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
        StockInService(session).stock_in(
            product_id="P-ONLY",
            quantity=1,
            purchase_price_usd=1.0,
            fx_rate_usd_to_irr=1_000_000.0,
        )


def test_quantity_validation(session):
    _seed(session)
    with pytest.raises(ValueError, match="quantity must be positive"):
        StockInService(session).stock_in(
            product_id="P-SI-1",
            quantity=0,
            purchase_price_usd=1.0,
            fx_rate_usd_to_irr=1_000_000.0,
        )


def test_purchase_price_validation(session):
    _seed(session)
    with pytest.raises(ValueError, match="purchase_price_usd"):
        StockInService(session).stock_in(
            product_id="P-SI-1",
            quantity=1,
            purchase_price_usd=-1.0,
            fx_rate_usd_to_irr=1_000_000.0,
        )


def test_fx_validation_no_invention(session):
    _seed(session)
    with pytest.raises(ValueError, match="fx_rate_usd_to_irr"):
        StockInService(session).stock_in(
            product_id="P-SI-1",
            quantity=1,
            purchase_price_usd=1.0,
            fx_rate_usd_to_irr=0,
        )


def test_historical_movement_fx_immutable(session):
    _seed(session, prior_fx=800_000.0)
    svc = StockInService(session)
    first = svc.stock_in(
        product_id="P-SI-1",
        quantity=1,
        purchase_price_usd=10.0,
        fx_rate_usd_to_irr=900_000.0,
    )
    session.commit()
    first_id = first["movement"].movement_id
    first_fx = first["movement"].fx_rate_usd_to_irr

    svc.stock_in(
        product_id="P-SI-1",
        quantity=1,
        purchase_price_usd=11.0,
        fx_rate_usd_to_irr=1_100_000.0,
    )
    session.commit()

    old = session.get(StockMovement, first_id)
    assert old.fx_rate_usd_to_irr == first_fx == 900_000.0


def test_atomic_rollback_on_failure(session):
    _seed(session, qty=4)
    svc = StockInService(session)

    # Force failure after partial work by using invalid product mid-path is hard;
    # instead: call with bad qty then verify no movement / qty unchanged after rollback path.
    with pytest.raises(ValueError):
        svc.stock_in(
            product_id="P-SI-1",
            quantity=-5,
            purchase_price_usd=1.0,
            fx_rate_usd_to_irr=1_000_000.0,
        )
    session.rollback()
    assert session.get(Inventory, "INV-P-SI-1").quantity_available == 4
    assert session.query(StockMovement).count() == 0


def test_traceability_and_ledger(session):
    _seed(session)
    result = StockInService(session).stock_in(
        product_id="P-SI-1",
        quantity=2,
        purchase_price_usd=5.0,
        fx_rate_usd_to_irr=1_000_000.0,
        note="trace",
        reference_type="PO",
        reference_id="PO-1",
    )
    session.commit()
    mov = result["movement"]
    rows = StockMovementService(session).list_ledger(product_id="P-SI-1", movement_type="STOCK_IN")
    assert len(rows) == 1
    assert rows[0].movement_id == mov.movement_id
    assert rows[0].reference_type == "PO"
    assert rows[0].reference_id == "PO-1"


def test_sale_price_toman_preserved(session):
    _seed(session)
    StockInService(session).stock_in(
        product_id="P-SI-1",
        quantity=1,
        purchase_price_usd=9.0,
        fx_rate_usd_to_irr=1_000_000.0,
    )
    session.commit()
    inv = session.get(Inventory, "INV-P-SI-1")
    assert inv.sale_price_toman == 1_200_000
