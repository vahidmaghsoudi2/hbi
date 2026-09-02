"""PHASE 05 — Inventory management tests. In-memory SQLite only. No real data/hbi.db."""
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


def _seed_product_inv(session, pid="P-INV-1", qty=10, toman=1_500_000):
    session.add(
        Product(
            product_id=pid,
            brand="Test",
            product_name="Item",
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
            purchase_price_toman=toman,
            sale_price_toman=toman + 100_000,
        )
    )
    session.commit()


def test_inventory_persists_and_links_product(session):
    _seed_product_inv(session)
    svc = InventoryService(session)
    inv = svc.find_by_product("P-INV-1")
    assert inv is not None
    assert inv.quantity_available == 10
    assert inv.purchase_price_toman == 1_500_000


def test_list_and_available(session):
    _seed_product_inv(session, "P-A", 5)
    _seed_product_inv(session, "P-B", 0)
    svc = InventoryService(session)
    assert len(svc.list_all()) == 2
    avail = svc.find_available()
    assert all(i.quantity_available > 0 for i in avail)
    assert {i.product_id for i in avail} == {"P-A"}


def test_is_available_reflects_quantity(session):
    _seed_product_inv(session, "P-C", 3)
    svc = InventoryService(session)
    assert svc.is_available("P-C", 1) is True
    assert svc.is_available("P-C", 3) is True
    assert svc.is_available("P-C", 4) is False
    assert svc.is_available("MISSING", 1) is False


def test_increase_stock_and_movement(session):
    _seed_product_inv(session, "P-D", 2)
    svc = InventoryService(session)
    inv = svc.increase_stock("P-D", 5, note="phase05-test")
    session.commit()
    assert inv.quantity_available == 7
    moves = session.query(StockMovement).filter_by(product_id="P-D").all()
    assert len(moves) == 1
    assert moves[0].quantity_delta == 5
    assert moves[0].quantity_after == 7
    assert moves[0].movement_type == "STOCK_IN"


def test_decrease_stock_and_movement(session):
    _seed_product_inv(session, "P-E", 10)
    svc = InventoryService(session)
    inv = svc.decrease_stock("P-E", 3, note="phase05-test")
    session.commit()
    assert inv.quantity_available == 7
    moves = session.query(StockMovement).filter_by(product_id="P-E").all()
    assert len(moves) == 1
    assert moves[0].quantity_delta == -3


def test_insufficient_stock_rejected_no_change(session):
    _seed_product_inv(session, "P-F", 2, toman=999)
    svc = InventoryService(session)
    with pytest.raises(ValueError, match="insufficient"):
        svc.decrease_stock("P-F", 5)
    session.rollback()
    inv = svc.find_by_product("P-F")
    assert inv.quantity_available == 2
    assert inv.purchase_price_toman == 999
    assert session.query(StockMovement).count() == 0


def test_negative_absolute_quantity_rejected(session):
    _seed_product_inv(session, "P-G", 1)
    svc = InventoryService(session)
    with pytest.raises(ValueError):
        svc.update_quantity("P-G", -1)


def test_unknown_product_rejected(session):
    svc = InventoryService(session)
    with pytest.raises(ValueError, match="not found"):
        svc.increase_stock("NO-SUCH", 1)


def test_toman_unchanged_on_stock_ops(session):
    _seed_product_inv(session, "P-H", 4, toman=2_000_000)
    svc = InventoryService(session)
    svc.increase_stock("P-H", 1)
    svc.decrease_stock("P-H", 1)
    session.commit()
    inv = svc.find_by_product("P-H")
    assert inv.purchase_price_toman == 2_000_000
    assert inv.quantity_available == 4
