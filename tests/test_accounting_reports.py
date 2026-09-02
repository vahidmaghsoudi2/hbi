"""PHASE 12 — Accounting reports tests. In-memory only. No data/hbi.db."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.models.base import Base
from app.models.category import Category
from app.models.customer import Customer
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.sale import Sale
from app.services.sale_service import SaleService
from app.services.return_service import ReturnService
from app.services.report_service import ReportService, LOCKED_CATEGORIES, _period_bounds


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


def _seed(session):
    for cid, name in [
        ("BOOST", "بوست"),
        ("HAIR", "مو"),
        ("BEAUTY", "زیبایی"),
        ("TOOLS", "ابزار"),
        ("PERFUME", "ادکلن"),
        ("OTHER", "سایر"),
    ]:
        session.add(Category(category_id=cid, name_fa=name, sort_order=0))
    session.add(Customer(customer_id="C1", name="B", consent_to_store_data=1))
    session.add(
        Product(
            product_id="P-BOOST",
            brand="B",
            product_name="Boost",
            identity_status="VERIFIED",
            qa_verdict="PENDING",
            status="ACTIVE",
            category_id="BOOST",
        )
    )
    session.add(
        Product(
            product_id="P-HAIR",
            brand="B",
            product_name="Hair",
            identity_status="VERIFIED",
            qa_verdict="PENDING",
            status="ACTIVE",
            category_id="HAIR",
        )
    )
    session.flush()
    for pid, qty in [("P-BOOST", 10), ("P-HAIR", 2)]:
        session.add(
            Inventory(
                inventory_id=f"INV-{pid}",
                product_id=pid,
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


def test_empty_sales_report(session):
    _seed(session)
    start = datetime(2020, 1, 1, tzinfo=timezone.utc)
    end = datetime(2020, 1, 2, tzinfo=timezone.utc)
    r = ReportService(session).sales_report(start=start, end=end)
    assert r["sale_count"] == 0
    assert r["revenue_usd"] == 0


def test_sales_and_financial(session):
    _seed(session)
    sale = SaleService(session).create_sale(
        "C1",
        [{"product_id": "P-BOOST", "quantity": 1, "unit_price_usd": 10.0}],
        fx_rate_usd_to_irr=1_000_000.0,
    )
    session.commit()
    # widen window around now
    now = datetime.now(timezone.utc)
    start = now - timedelta(days=1)
    end = now + timedelta(days=1)
    sales = ReportService(session).sales_report(start=start, end=end)
    assert sales["sale_count"] == 1
    assert sales["revenue_usd"] == pytest.approx(10.0)
    assert sales["revenue_toman"] == 1_000_000

    ReturnService(session).create_return(
        sale_id=sale.sale_id, product_id="P-BOOST", quantity=1
    )
    session.commit()
    fin = ReportService(session).financial_summary(start=start, end=end)
    assert fin["returns_usd"] == pytest.approx(10.0)
    assert fin["cogs"]["status"] == "UNSUPPORTED"
    assert fin["discounts"]["status"] == "UNSUPPORTED"
    assert fin["gross_profit"]["status"] == "UNSUPPORTED"
    # historical sale fx still intact
    assert session.get(Sale, sale.sale_id).fx_rate_usd_to_irr == 1_000_000.0


def test_period_bounds():
    start, end = _period_bounds("today", datetime(2026, 9, 2, 15, 0, tzinfo=timezone.utc))
    assert start.day == 2 and end.day == 3
    start, end = _period_bounds("week", datetime(2026, 9, 2, 15, 0, tzinfo=timezone.utc))
    assert start.weekday() == 0
    start, end = _period_bounds("month", datetime(2026, 9, 15, tzinfo=timezone.utc))
    assert start.month == 9 and start.day == 1 and end.month == 10


def test_inventory_reports(session):
    _seed(session)
    all_inv = ReportService(session).inventory_all()
    assert len(all_inv) == 2
    boost = ReportService(session).inventory_by_category("BOOST")
    hair = ReportService(session).inventory_by_category("HAIR")
    assert len(boost) == 1 and boost[0]["product_id"] == "P-BOOST"
    assert len(hair) == 1 and hair[0]["product_id"] == "P-HAIR"
    assert "BOOST" in LOCKED_CATEGORIES and "HAIR" in LOCKED_CATEGORIES
    assert boost[0]["product_id"] != hair[0]["product_id"]
    low = ReportService(session).inventory_low_stock(threshold=3)
    assert any(r["product_id"] == "P-HAIR" for r in low)
    assert not any(r["product_id"] == "P-BOOST" for r in low)


def test_invalid_category(session):
    with pytest.raises(ValueError, match="invalid category"):
        ReportService(session).inventory_by_category("MERGED")


def test_read_only_no_mutation(session):
    _seed(session)
    before = session.get(Inventory, "INV-P-BOOST").quantity_available
    ReportService(session).inventory_all()
    ReportService(session).sales_period("today")
    assert session.get(Inventory, "INV-P-BOOST").quantity_available == before
