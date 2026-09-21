"""PRICING-SALES-INTEGRATION-001 — authoritative USD sale price and operational FX wiring."""

from app.core.auth import create_access_token
from app.models.inventory import Inventory
from app.models.product import Product
from app.models.user_role import ROLE_ADMIN, ROLE_EDITOR, UserRole
from app.services.inventory_service import InventoryService


def _headers(subject_id: str):
    token = create_access_token({"sub": subject_id})
    return {"Authorization": f"Bearer {token}"}


def _seed_product_inventory(db_session, product_id: str = "PRICE-TEST"):
    db_session.add(
        Product(
            product_id=product_id,
            brand="TestBrand",
            product_name="Price Test",
            identity_status="VERIFIED",
            qa_verdict="VALID",
            status="ACTIVE",
        )
    )
    db_session.add(
        Inventory(
            inventory_id=f"INV-{product_id}",
            product_id=product_id,
            quantity_available=10,
            quantity_reserved=0,
            quantity_damaged=0,
            stock_status="active",
        )
    )
    db_session.commit()


def _grant_role(db_session, subject_id: str, role: str):
    db_session.add(
        UserRole(
            user_role_id=f"ROLE-{subject_id}-{role}",
            subject_id=subject_id,
            role=role,
        )
    )
    db_session.commit()


def test_set_sale_price_usd_updates_authoritative_inventory_value(db_session):
    _seed_product_inventory(db_session)
    service = InventoryService(db_session)

    inventory = service.set_sale_price_usd("PRICE-TEST", 12.0)
    db_session.commit()
    db_session.refresh(inventory)

    assert inventory.sale_price_usd == 12.0
    assert inventory.quantity_available == 10


def test_sale_price_endpoint_is_admin_only_and_returns_usd(client, db_session):
    _seed_product_inventory(db_session)

    assert client.put(
        "/api/v1/inventory/product/PRICE-TEST/sale-price",
        json={"sale_price_usd": 12.0},
    ).status_code == 401

    _grant_role(db_session, "editor-user", ROLE_EDITOR)
    response = client.put(
        "/api/v1/inventory/product/PRICE-TEST/sale-price",
        json={"sale_price_usd": 12.0},
        headers=_headers("editor-user"),
    )
    assert response.status_code == 403

    _grant_role(db_session, "admin-user", ROLE_ADMIN)
    response = client.put(
        "/api/v1/inventory/product/PRICE-TEST/sale-price",
        json={"sale_price_usd": 12.0},
        headers=_headers("admin-user"),
    )
    assert response.status_code == 200, response.text
    assert response.json()["sale_price_usd"] == 12.0


def test_sale_price_endpoint_rejects_unknown_product(client, db_session):
    _grant_role(db_session, "admin-user", ROLE_ADMIN)
    response = client.put(
        "/api/v1/inventory/product/MISSING/sale-price",
        json={"sale_price_usd": 12.0},
        headers=_headers("admin-user"),
    )
    assert response.status_code == 422


def test_current_fx_is_null_when_no_operational_rate_exists(client):
    response = client.get("/api/v1/fx/current")
    assert response.status_code == 200
    assert response.json()["fx_rate_usd_to_irr"] is None
