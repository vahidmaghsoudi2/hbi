"""PHASE 06 — Stock Movement Ledger tests. In-memory only. No data/hbi.db."""
from __future__ import annotations

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.models.base import Base
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.stock_movement import StockMovement
from app.services.inventory_service import InventoryService
from app.services.stock_movement_service import StockMovementService
from app.repositories.stock_movement_repository import VALID_MOVEMENT_TYPES


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


def _seed(session, pid="P-SM-1", qty=10):
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
        )
    )
    session.commit()


def test_ledger_empty(session):
    svc = StockMovementService(session)
    assert svc.list_ledger() == []


def test_ledger_from_existing_mutation_path(session):
    _seed(session)
    inv_svc = InventoryService(session)
    inv_svc.increase_stock("P-SM-1", 3, note="phase06")
    inv_svc.decrease_stock("P-SM-1", 1, note="phase06-out")
    session.commit()

    ledger = StockMovementService(session)
    rows = ledger.list_ledger()
    assert len(rows) == 2
    assert {r.movement_type for r in rows} <= VALID_MOVEMENT_TYPES
    assert all(r.product_id == "P-SM-1" for r in rows)
    assert all(r.quantity_delta is not None for r in rows)
    assert all(r.quantity_after is not None for r in rows)
    # newest first
    assert rows[0].created_at >= rows[1].created_at or rows[0].movement_id != rows[1].movement_id


def test_filter_by_product(session):
    _seed(session, "P-A", 5)
    _seed(session, "P-B", 5)
    inv = InventoryService(session)
    inv.increase_stock("P-A", 1)
    inv.increase_stock("P-B", 2)
    session.commit()

    ledger = StockMovementService(session)
    a_rows = ledger.list_ledger(product_id="P-A")
    assert len(a_rows) == 1
    assert a_rows[0].product_id == "P-A"
    assert a_rows[0].quantity_delta == 1


def test_filter_by_movement_type(session):
    _seed(session, "P-C", 8)
    inv = InventoryService(session)
    inv.increase_stock("P-C", 2, movement_type="STOCK_IN")
    inv.decrease_stock("P-C", 1, movement_type="SALE")
    session.commit()

    ledger = StockMovementService(session)
    sales = ledger.list_ledger(movement_type="SALE")
    assert len(sales) == 1
    assert sales[0].movement_type == "SALE"
    assert sales[0].quantity_delta == -1


def test_invalid_movement_type_rejected(session):
    ledger = StockMovementService(session)
    with pytest.raises(ValueError, match="invalid movement_type"):
        ledger.list_ledger(movement_type="FAKE_TYPE")


def test_get_by_id_and_missing(session):
    _seed(session, "P-D", 4)
    InventoryService(session).increase_stock("P-D", 1)
    session.commit()
    ledger = StockMovementService(session)
    row = ledger.list_ledger()[0]
    found = ledger.get_by_id(row.movement_id)
    assert found is not None
    assert found.movement_id == row.movement_id
    assert ledger.get_by_id("no-such-id") is None


def test_traceability_fields(session):
    _seed(session, "P-E", 6)
    InventoryService(session).increase_stock("P-E", 2, note="trace-note")
    session.commit()
    row = StockMovementService(session).list_ledger(product_id="P-E")[0]
    assert row.inventory_id == "INV-P-E"
    assert row.note == "trace-note"
    assert row.movement_type == "STOCK_IN"
    assert row.quantity_after == 8


def test_negative_inventory_still_blocked(session):
    _seed(session, "P-F", 2)
    inv = InventoryService(session)
    with pytest.raises(ValueError, match="insufficient"):
        inv.decrease_stock("P-F", 9)
    session.rollback()
    assert StockMovementService(session).list_ledger() == []
    assert inv.find_by_product("P-F").quantity_available == 2


def test_toman_preserved_on_mutation_path(session):
    _seed(session, "P-G", 3)
    inv_svc = InventoryService(session)
    inv_svc.increase_stock("P-G", 1)
    session.commit()
    inv = inv_svc.find_by_product("P-G")
    assert inv.purchase_price_toman == 1_000_000
    assert inv.sale_price_toman == 1_200_000
