"""PHASE 10 — Returns workflow tests. In-memory only. No data/hbi.db."""
from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
import pytest
from sqlalchemy import create_engine, event, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.models.base import Base
from app.models.customer import Customer
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.sale import Sale
from app.models.sale_item import SaleItem
from app.models.sale_return import SaleReturn
from app.models.stock_movement import StockMovement
from app.services.sale_service import SaleService
from app.services.return_service import ReturnService
from app.api.routers.sales import get_sale_detail
from app.api.routers.returns import ReturnCreateRequest
from pydantic import ValidationError


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


@pytest.mark.parametrize("quantity", [1.5, "1.5", float("nan"), float("inf")])
def test_fractional_or_non_finite_return_quantity_rejected(session, quantity):
    sale = _sold(session, qty_sold=3)
    before = session.get(Inventory, "INV-P1").quantity_available

    with pytest.raises(ValueError, match="quantity must be a positive integer"):
        ReturnService(session).create_return(
            sale_id=sale.sale_id, product_id="P1", quantity=quantity
        )

    session.rollback()
    assert session.get(Inventory, "INV-P1").quantity_available == before
    assert session.query(SaleReturn).count() == 0


@pytest.mark.parametrize("quantity", [1.5, 2.25])
def test_return_api_schema_rejects_fractional_quantity(quantity):
    with pytest.raises(ValidationError):
        ReturnCreateRequest(
            sale_id="SALE-1",
            product_id="P1",
            quantity=quantity,
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



def test_invoice_detail_reports_remaining_return_quantity(session):
    sale = _sold(session, qty_sold=4)
    ReturnService(session).create_return(
        sale_id=sale.sale_id, product_id="P1", quantity=1
    )
    session.commit()

    detail = asyncio.run(get_sale_detail(sale.sale_id, session, admin=object()))

    assert detail["sale_id"] == sale.sale_id
    assert len(detail["items"]) == 1
    item = detail["items"][0]
    assert item["product_id"] == "P1"
    assert item["sold_quantity"] == 4
    assert item["already_returned_quantity"] == 1
    assert item["remaining_quantity"] == 3


def test_invoice_detail_unknown_sale_is_404(session):
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc:
        asyncio.run(get_sale_detail("MISSING-SALE", session, admin=object()))
    assert exc.value.status_code == 404



def test_return_rejected_for_voided_sale(session):
    sale = _sold(session, qty_sold=2)
    sale.document_status = "VOIDED"
    session.commit()

    with pytest.raises(ValueError, match="cannot return against sale"):
        ReturnService(session).create_return(
            sale_id=sale.sale_id, product_id="P1", quantity=1
        )


def test_mixed_price_duplicate_product_lines_rejected(session):
    sale = _sold(session, qty_sold=2)
    original = session.query(SaleItem).filter_by(sale_id=sale.sale_id, product_id="P1").one()
    duplicate = SaleItem(
        sale_item_id="DUPLICATE-LINE",
        sale_id=sale.sale_id,
        product_id="P1",
        quantity=1,
        unit_price_toman=original.unit_price_toman,
        unit_price_usd=original.unit_price_usd + 5,
        fx_rate_usd_to_irr=original.fx_rate_usd_to_irr,
    )
    session.add(duplicate)
    session.commit()

    with pytest.raises(ValueError, match="mixed original unit prices"):
        ReturnService(session).create_return(
            sale_id=sale.sale_id, product_id="P1", quantity=1
        )


def test_mixed_fx_duplicate_product_lines_rejected_without_sale_fx_snapshot(session):
    sale = _sold(session, qty_sold=2)
    sale.fx_rate_usd_to_irr = None
    original = session.query(SaleItem).filter_by(sale_id=sale.sale_id, product_id="P1").one()
    original.fx_rate_usd_to_irr = 1_000_000.0
    duplicate = SaleItem(
        sale_item_id="DUPLICATE-FX-LINE",
        sale_id=sale.sale_id,
        product_id="P1",
        quantity=1,
        unit_price_toman=original.unit_price_toman,
        unit_price_usd=original.unit_price_usd,
        fx_rate_usd_to_irr=2_000_000.0,
    )
    session.add(duplicate)
    session.commit()

    with pytest.raises(ValueError, match="mixed original FX rates"):
        ReturnService(session).create_return(
            sale_id=sale.sale_id, product_id="P1", quantity=1
        )


def test_full_return_restores_sold_quantity_and_stock(session):
    sale = _sold(session, qty_sold=3, stock_start=10)
    assert session.get(Inventory, "INV-P1").quantity_available == 7

    ret = ReturnService(session).create_return(
        sale_id=sale.sale_id, product_id="P1", quantity=3
    )
    session.commit()

    assert ret.quantity == 3
    assert session.get(Inventory, "INV-P1").quantity_available == 10
    assert session.query(SaleReturn).filter_by(sale_id=sale.sale_id).with_entities(
        func.sum(SaleReturn.quantity)
    ).scalar() == 3
    movement = session.query(StockMovement).filter_by(reference_id=ret.return_id).one()
    assert movement.quantity_delta == 3
    assert movement.quantity_after == 10


def test_concurrent_returns_cannot_overreturn_sqlite(tmp_path):
    # Use a file-backed SQLite DB and independent connections. An in-memory
    # StaticPool test cannot model separate transactions competing for the lock.
    engine = create_engine(
        f"sqlite:///{tmp_path / 'returns-concurrency.db'}",
        connect_args={"check_same_thread": False, "timeout": 10},
    )

    @event.listens_for(engine, "connect")
    def _fk(dbapi_connection, connection_record):
        cur = dbapi_connection.cursor()
        cur.execute("PRAGMA foreign_keys=ON")
        cur.close()

    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    setup = Session()
    try:
        sale = _sold(setup, qty_sold=3, stock_start=10)
        sale_id = sale.sale_id
        setup.commit()
    finally:
        setup.close()

    start = Barrier(2)

    def attempt_return():
        db = Session()
        try:
            start.wait(timeout=5)
            ret = ReturnService(db).create_return(
                sale_id=sale_id, product_id="P1", quantity=2
            )
            db.commit()
            return ("ok", ret.return_id)
        except Exception as exc:
            db.rollback()
            return ("error", str(exc))
        finally:
            db.close()

    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            outcomes = list(pool.map(lambda _: attempt_return(), range(2)))

        assert sum(status == "ok" for status, _ in outcomes) == 1
        assert sum(status == "error" for status, _ in outcomes) == 1

        verify = Session()
        try:
            returned = verify.query(SaleReturn).filter_by(sale_id=sale_id).all()
            assert sum(row.quantity for row in returned) == 2
            assert verify.get(Inventory, "INV-P1").quantity_available == 9
            movements = verify.query(StockMovement).filter_by(
                reference_type="SALE_RETURN"
            ).all()
            assert sum(row.quantity_delta for row in movements) == 2
        finally:
            verify.close()
    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()
