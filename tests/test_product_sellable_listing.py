"""Sale catalog eligibility: only active, fully verified, stocked products with USD prices."""
from __future__ import annotations

import asyncio

from app.api.routers.products import list_sellable_products
from app.models.inventory import Inventory
from app.models.product import Product


def _seed_product(db, product_id: str, *, status="ACTIVE", identity_status="VERIFIED",
                  qa_verdict="VALID", quantity_available=5, quantity_reserved=0,
                  sale_price_usd=20.0):
    db.add(Product(
        product_id=product_id,
        brand="Test Brand",
        product_name=f"Product {product_id}",
        status=status,
        identity_status=identity_status,
        qa_verdict=qa_verdict,
    ))
    db.flush()
    db.add(Inventory(
        inventory_id=f"INV-{product_id}",
        product_id=product_id,
        quantity_available=quantity_available,
        quantity_reserved=quantity_reserved,
        sale_price_usd=sale_price_usd,
        stock_status="active",
    ))


def test_sellable_listing_filters_to_active_verified_stock_with_price(db_session):
    _seed_product(db_session, "SELLABLE")
    _seed_product(db_session, "DRAFT", status="DRAFT")
    _seed_product(db_session, "QA-PENDING", qa_verdict="PENDING")
    _seed_product(db_session, "IDENTITY-UNKNOWN", identity_status="NEEDS_REVIEW")
    _seed_product(db_session, "NO-STOCK", quantity_available=1, quantity_reserved=1)
    _seed_product(db_session, "NO-PRICE", sale_price_usd=None)
    db_session.commit()

    result = asyncio.run(list_sellable_products(db=db_session, auth=("admin", {"ADMIN"})))

    assert [product["product_id"] for product in result] == ["SELLABLE"]
