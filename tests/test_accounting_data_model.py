"""PHASE 02 — Accounting data model tests (schema + C-01 unit formula). No UI."""
from __future__ import annotations

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.models.base import Base
from app.models.category import Category
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.sale import Sale
from app.models.sale_item import SaleItem
from app.models.stock_movement import StockMovement
from app.models.payment import Payment
from app.models.sale_return import SaleReturn
from app.models.operational_fx_rate import OperationalFxRate
from app.models.customer import Customer


def _toman_to_usd(amount_toman: float, r_irr_per_usd: float) -> float:
    amount_irr = amount_toman * 10
    return amount_irr / r_irr_per_usd


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


def test_c01_conversion_formula_units():
    r = 1_000_000.0
    usd = _toman_to_usd(1_500_000, r)
    assert usd == pytest.approx(15.0)
    assert abs(usd - (1_500_000 / r)) > 1.0


def test_boost_and_hair_are_independent_categories(session):
    session.add_all(
        [
            Category(category_id="BOOST", name_fa="بوست", name_en="Boost", sort_order=1),
            Category(category_id="HAIR", name_fa="مو", name_en="Hair", sort_order=2),
        ]
    )
    session.commit()
    boost = session.get(Category, "BOOST")
    hair = session.get(Category, "HAIR")
    assert boost is not None and hair is not None
    assert boost.category_id != hair.category_id


def test_product_links_to_category_not_parallel_master(session):
    session.add(Category(category_id="BEAUTY", name_fa="زیبایی", sort_order=3))
    session.add(
        Product(
            product_id="TEST-P-001",
            brand="TestBrand",
            product_name="Test Product",
            identity_status="VERIFIED",
            qa_verdict="PENDING",
            status="ACTIVE",
            category_id="BEAUTY",
        )
    )
    session.commit()
    p = session.get(Product, "TEST-P-001")
    assert p.category_id == "BEAUTY"
    assert p.category.name_fa == "زیبایی"


def test_inventory_keeps_toman_and_accepts_usd_fields(session):
    session.add(
        Product(
            product_id="TEST-P-002",
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
            inventory_id="INV-TEST-002",
            product_id="TEST-P-002",
            quantity_available=5,
            quantity_reserved=0,
            quantity_damaged=0,
            stock_status="active",
            purchase_price_toman=1_500_000,
            sale_price_toman=2_000_000,
            purchase_price_usd=15.0,
            sale_price_usd=20.0,
            price_fx_rate_usd_to_irr=1_000_000.0,
            purchase_price_irr=15_000_000.0,
            sale_price_irr=20_000_000.0,
        )
    )
    session.commit()
    loaded = session.get(Inventory, "INV-TEST-002")
    assert loaded.purchase_price_toman == 1_500_000
    assert loaded.purchase_price_usd == pytest.approx(15.0)


def test_stock_movement_payment_return_tables(session):
    session.add(Customer(customer_id="CUST-T1", name="T", consent_to_store_data=0))
    session.flush()
    session.add(
        Product(
            product_id="TEST-P-003",
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
            inventory_id="INV-003",
            product_id="TEST-P-003",
            quantity_available=10,
            quantity_reserved=0,
            quantity_damaged=0,
            stock_status="active",
        )
    )
    session.add(
        Sale(
            sale_id="SALE-T1",
            customer_id="CUST-T1",
            total_amount_toman=0,
            total_amount_usd=15.0,
            fx_rate_usd_to_irr=1_000_000.0,
            total_amount_irr=15_000_000.0,
        )
    )
    session.add(
        SaleItem(
            sale_item_id="SI-T1",
            sale_id="SALE-T1",
            product_id="TEST-P-003",
            quantity=1,
            unit_price_toman=0,
            unit_price_usd=15.0,
            fx_rate_usd_to_irr=1_000_000.0,
        )
    )
    session.add(
        StockMovement(
            movement_id="MOV-1",
            product_id="TEST-P-003",
            inventory_id="INV-003",
            movement_type="SALE",
            quantity_delta=-1,
            quantity_after=9,
            reference_type="SALE",
            reference_id="SALE-T1",
        )
    )
    session.add(
        Payment(
            payment_id="PAY-1",
            sale_id="SALE-T1",
            method="CASH",
            amount_usd=15.0,
            fx_rate_usd_to_irr=1_000_000.0,
            amount_toman=1_500_000,
        )
    )
    session.add(
        SaleReturn(
            return_id="RET-1",
            sale_id="SALE-T1",
            product_id="TEST-P-003",
            quantity=1,
            amount_usd=15.0,
            fx_rate_usd_to_irr=1_000_000.0,
        )
    )
    session.add(OperationalFxRate(rate_id="FX-OP-1", fx_rate_usd_to_irr=1_000_000.0, note="test only"))
    session.commit()
    assert session.get(StockMovement, "MOV-1").quantity_delta == -1
    assert session.get(Payment, "PAY-1").method == "CASH"
    assert session.get(SaleReturn, "RET-1").quantity == 1
