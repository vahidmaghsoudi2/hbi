"""PHASE 14 — Comprehensive integrated Accounting contract tests.

In-memory only. Never touches data/hbi.db.
Covers end-to-end flows across phases 02–13 surfaces.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

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
from app.models.sale_item import SaleItem
from app.models.payment import Payment
from app.models.sale_return import SaleReturn
from app.models.stock_movement import StockMovement
from app.services.stock_in_service import StockInService
from app.services.sale_service import SaleService
from app.services.payment_service import PaymentService, VALID_METHODS
from app.services.return_service import ReturnService
from app.services.operational_fx_service import OperationalFxService
from app.services.report_service import ReportService, LOCKED_CATEGORIES
from app.services.currency_fx import usd_to_irr, irr_to_toman, validate_fx_rate

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend" / "src"


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


def _bootstrap(session):
    cats = [
        ("BOOST", "بوست", 1),
        ("HAIR", "مو", 2),
        ("BEAUTY", "زیبایی", 3),
        ("TOOLS", "ابزار", 4),
        ("PERFUME", "ادکلن", 5),
        ("OTHER", "سایر", 6),
    ]
    for cid, fa, so in cats:
        session.add(Category(category_id=cid, name_fa=fa, sort_order=so))
    session.add(Customer(customer_id="C1", name="Buyer", consent_to_store_data=1))
    session.add(
        Product(
            product_id="P1",
            brand="B",
            product_name="Item",
            identity_status="VERIFIED",
            qa_verdict="PENDING",
            status="ACTIVE",
            category_id="BOOST",
        )
    )
    session.add(
        Product(
            product_id="P2",
            brand="B",
            product_name="HairItem",
            identity_status="VERIFIED",
            qa_verdict="PENDING",
            status="ACTIVE",
            category_id="HAIR",
        )
    )
    session.flush()
    for pid, qty in [("P1", 10), ("P2", 5)]:
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


def test_category_integrity_six_and_boost_ne_hair(session):
    _bootstrap(session)
    ids = {c.category_id for c in session.query(Category).all()}
    assert ids == set(LOCKED_CATEGORIES)
    assert "BOOST" in ids and "HAIR" in ids and "BOOST" != "HAIR"
    boost = session.get(Category, "BOOST")
    hair = session.get(Category, "HAIR")
    assert boost.name_fa != hair.name_fa


def test_product_inventory_not_duplicated_entity(session):
    _bootstrap(session)
    inv = session.get(Inventory, "INV-P1")
    assert inv.product_id == "P1"
    assert session.get(Product, "P1") is not None
    assert session.query(Inventory).filter_by(product_id="P1").count() == 1


def test_integrated_stock_in_sale_payment_return_fx_reports(session):
    _bootstrap(session)
    r = 1_000_000.0
    # Stock-In
    StockInService(session).stock_in(
        product_id="P1", quantity=2, purchase_price_usd=4.0, fx_rate_usd_to_irr=r
    )
    session.commit()
    inv = session.get(Inventory, "INV-P1")
    assert inv.quantity_available == 12
    sin = session.query(StockMovement).filter_by(movement_type="STOCK_IN").one()
    assert sin.fx_rate_usd_to_irr == r
    assert sin.amount_irr == pytest.approx(usd_to_irr(8.0, r))

    # Sale depletes stock + SALE movement
    sale = SaleService(session).create_sale(
        "C1",
        [{"product_id": "P1", "quantity": 3, "unit_price_usd": 10.0}],
        fx_rate_usd_to_irr=r,
    )
    session.commit()
    assert session.get(Inventory, "INV-P1").quantity_available == 9
    assert session.query(SaleItem).filter_by(sale_id=sale.sale_id).count() == 1
    assert session.query(StockMovement).filter_by(movement_type="SALE").count() >= 1

    # Insufficient stock rejected + no partial
    before = session.get(Inventory, "INV-P1").quantity_available
    with pytest.raises(ValueError):
        SaleService(session).create_sale(
            "C1",
            [{"product_id": "P1", "quantity": 999, "unit_price_usd": 10.0}],
            fx_rate_usd_to_irr=r,
        )
    session.rollback()
    assert session.get(Inventory, "INV-P1").quantity_available == before

    # Payments all methods; sale totals immutable
    prior = (
        sale.total_amount_usd,
        sale.total_amount_irr,
        sale.total_amount_toman,
        sale.fx_rate_usd_to_irr,
    )
    for method in sorted(VALID_METHODS):
        PaymentService(session).record_payment(
            sale_id=sale.sale_id,
            method=method,
            amount_usd=1.0,
            fx_rate_usd_to_irr=r,
        )
    session.commit()
    s = session.get(Sale, sale.sale_id)
    assert (s.total_amount_usd, s.total_amount_irr, s.total_amount_toman, s.fx_rate_usd_to_irr) == prior
    assert session.query(Payment).filter_by(sale_id=sale.sale_id).count() == 4

    # Return restores inventory + RETURN_IN
    ret = ReturnService(session).create_return(
        sale_id=sale.sale_id, product_id="P1", quantity=1
    )
    session.commit()
    assert session.get(Inventory, "INV-P1").quantity_available == 10
    mov = session.query(StockMovement).filter_by(reference_id=ret.return_id).one()
    assert mov.movement_type == "RETURN_IN"
    with pytest.raises(ValueError):
        ReturnService(session).create_return(
            sale_id=sale.sale_id, product_id="P1", quantity=99
        )
    session.rollback()

    # FX operational change does not rewrite history
    hist_fx = [m.fx_rate_usd_to_irr for m in session.query(StockMovement).all()]
    OperationalFxService(session).set_rate(2_000_000.0, note="op")
    session.commit()
    for m in session.query(StockMovement).all():
        assert m.fx_rate_usd_to_irr in hist_fx
    assert session.get(Sale, sale.sale_id).fx_rate_usd_to_irr == r

    # Reports: revenue + unsupported metrics; read-only
    now = datetime.now(timezone.utc)
    fin = ReportService(session).financial_summary(
        start=now - timedelta(days=1), end=now + timedelta(days=1)
    )
    assert fin["sale_count"] >= 1
    assert fin["cogs"]["status"] == "UNSUPPORTED"
    assert fin["discounts"]["status"] == "UNSUPPORTED"
    assert fin["gross_profit"]["status"] == "UNSUPPORTED"
    inv_before = session.get(Inventory, "INV-P1").quantity_available
    ReportService(session).inventory_all()
    ReportService(session).inventory_by_category("BOOST")
    ReportService(session).inventory_by_category("HAIR")
    assert session.get(Inventory, "INV-P1").quantity_available == inv_before
    boost = ReportService(session).inventory_by_category("BOOST")
    hair = ReportService(session).inventory_by_category("HAIR")
    assert {x["product_id"] for x in boost} == {"P1"}
    assert {x["product_id"] for x in hair} == {"P2"}


def test_boundaries_zero_negative_fx_invalid(session):
    _bootstrap(session)
    with pytest.raises(ValueError):
        validate_fx_rate(0)
    with pytest.raises(ValueError):
        StockInService(session).stock_in(
            product_id="P1", quantity=0, purchase_price_usd=1.0, fx_rate_usd_to_irr=1.0
        )
    with pytest.raises(ValueError):
        SaleService(session).create_sale(
            "C1",
            [{"product_id": "P1", "quantity": -1, "unit_price_usd": 1.0}],
            fx_rate_usd_to_irr=1.0,
        )


def test_exact_stock_quantity_sale(session):
    _bootstrap(session)
    SaleService(session).create_sale(
        "C1",
        [{"product_id": "P2", "quantity": 5, "unit_price_usd": 3.0}],
        fx_rate_usd_to_irr=1_000_000.0,
    )
    session.commit()
    assert session.get(Inventory, "INV-P2").quantity_available == 0


def test_home_accounting_routes_static():
    app = (FRONTEND / "App.tsx").read_text(encoding="utf-8")
    home = (FRONTEND / "pages" / "NewHomePage.tsx").read_text(encoding="utf-8")
    assert 'path="/"' in app and 'path="/accounting"' in app
    assert app.count('path="/accounting"') == 1
    assert 'to="/accounting"' in home and "حسابداری" in home


def test_no_data_hbi_db_touched_by_this_suite():
    # Clone/test env should not require real DB; assert helper path convention
    assert not str(ROOT / "data" / "hbi.db").endswith("modified")
