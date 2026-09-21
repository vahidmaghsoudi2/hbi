"""INVENTORY-AUTHZ-001 — Admin-only Inventory authorization contract."""

import pytest

from app.core.auth import create_access_token
from app.models.inventory import Inventory
from app.models.product import Product
from app.models.stock_movement import StockMovement
from app.models.user_role import ROLE_ADMIN, ROLE_EDITOR, UserRole


def _headers(subject_id: str):
    return {'Authorization': f"Bearer {create_access_token({'sub': subject_id})}"}


def _seed_inventory(db_session):
    db_session.add(
        Product(
            product_id="INV-AUTHZ-P1",
            brand="B",
            product_name="Inventory AuthZ Product",
            identity_status="VERIFIED",
            qa_verdict="PENDING",
            status="ACTIVE",
        )
    )
    db_session.commit()
    db_session.add(
        Inventory(
            inventory_id="INV-AUTHZ-I1",
            product_id="INV-AUTHZ-P1",
            quantity_available=5,
            quantity_reserved=0,
            quantity_damaged=0,
            stock_status="active",
            sale_price_usd=10.0,
            sale_price_toman=1_000_000,
            purchase_price_toman=800_000,
        )
    )
    db_session.commit()


def _grant_admin(db_session, subject_id: str = "admin-user"):
    db_session.add(
        UserRole(
            user_role_id=f"ROLE-{subject_id}",
            subject_id=subject_id,
            role=ROLE_ADMIN,
        )
    )
    db_session.commit()


READ_CASES = [
    ("/api/v1/inventory/", 200),
    ("/api/v1/inventory/available", 200),
    ("/api/v1/inventory/movements", 200),
    ("/api/v1/inventory/movements/MISSING", 404),
    ("/api/v1/inventory/availability/INV-AUTHZ-P1", 200),
]


@pytest.mark.parametrize("path,_expected_admin_status", READ_CASES)
def test_inventory_reads_require_admin(client, db_session, path, _expected_admin_status):
    _seed_inventory(db_session)

    assert client.get(path).status_code == 401
    assert client.get(
        path, headers={"Authorization": "Bearer invalid-token"}
    ).status_code == 401

    ordinary = client.get(path, headers=_headers("ordinary-user"))
    assert ordinary.status_code == 403

    _grant_admin(db_session)
    admin = client.get(path, headers=_headers("admin-user"))
    assert admin.status_code == _expected_admin_status


@pytest.mark.parametrize(
    "method,path,payload",
    [
        (
            "post",
            "/api/v1/inventory/stock-in",
            {
                "product_id": "INV-AUTHZ-P1",
                "quantity": 2,
                "purchase_price_usd": 9.0,
                "fx_rate_usd_to_irr": 1_000_000.0,
            },
        ),
        (
            "post",
            "/api/v1/inventory/adjust",
            {
                "product_id": "INV-AUTHZ-P1",
                "quantity": 1,
                "direction": "increase",
            },
        ),
    ],
)
def test_inventory_mutations_require_admin(
    client, db_session, method, path, payload
):
    _seed_inventory(db_session)
    before_quantity = db_session.query(Inventory).filter_by(
        product_id="INV-AUTHZ-P1"
    ).one().quantity_available
    before_movements = db_session.query(StockMovement).count()

    request = getattr(client, method)
    assert request(path, json=payload).status_code == 401
    assert request(
        path, json=payload, headers={"Authorization": "Bearer invalid-token"}
    ).status_code == 401

    ordinary = request(path, json=payload, headers=_headers("ordinary-user"))
    assert ordinary.status_code == 403

    db_session.expire_all()
    assert db_session.query(Inventory).filter_by(
        product_id="INV-AUTHZ-P1"
    ).one().quantity_available == before_quantity
    assert db_session.query(StockMovement).count() == before_movements


def test_admin_can_stock_in_and_adjust_inventory(client, db_session):
    _seed_inventory(db_session)
    _grant_admin(db_session)

    stock_in = client.post(
        "/api/v1/inventory/stock-in",
        json={
            "product_id": "INV-AUTHZ-P1",
            "quantity": 2,
            "purchase_price_usd": 9.0,
            "fx_rate_usd_to_irr": 1_000_000.0,
        },
        headers=_headers("admin-user"),
    )
    assert stock_in.status_code == 200, stock_in.text
    movement_id = stock_in.json()["movement"]["movement_id"]
    assert stock_in.json()["before_quantity"] == 5

    db_session.expire_all()
    assert db_session.query(Inventory).filter_by(
        product_id="INV-AUTHZ-P1"
    ).one().quantity_available == 7

    adjustment = client.post(
        "/api/v1/inventory/adjust",
        json={
            "product_id": "INV-AUTHZ-P1",
            "quantity": 1,
            "direction": "decrease",
            "note": "authz regression test",
        },
        headers=_headers("admin-user"),
    )
    assert adjustment.status_code == 200, adjustment.text
    assert adjustment.json()["quantity_available"] == 6

    movement = client.get(
        f"/api/v1/inventory/movements/{movement_id}",
        headers=_headers("admin-user"),
    )
    assert movement.status_code == 200, movement.text


def test_product_inventory_read_denies_customer_allows_operator_and_admin(client, db_session):
    """Sell-read: customer 403; Editor/Admin 200; unauth 401."""
    _seed_inventory(db_session)
    path = "/api/v1/inventory/product/INV-AUTHZ-P1"
    assert client.get(path).status_code == 401
    assert client.get(path, headers={"Authorization": "Bearer invalid-token"}).status_code == 401
    assert client.get(path, headers=_headers("ordinary-customer")).status_code == 403

    db_session.add(UserRole(user_role_id="ROLE-op-Editor", subject_id="op-editor", role=ROLE_EDITOR))
    db_session.commit()
    assert client.get(path, headers=_headers("op-editor")).status_code == 200

    _grant_admin(db_session)
    assert client.get(path, headers=_headers("admin-user")).status_code == 200


def test_product_inventory_read_missing_returns_404_for_operator(client, db_session):
    db_session.add(UserRole(user_role_id="ROLE-op2", subject_id="op2", role=ROLE_EDITOR))
    db_session.commit()
    r = client.get(
        "/api/v1/inventory/product/NO-SUCH-PRODUCT",
        headers=_headers("op2"),
    )
    assert r.status_code == 404


def test_inventory_list_and_mutations_still_admin_only(client, db_session):
    _seed_inventory(db_session)
    db_session.add(UserRole(user_role_id="ROLE-ed", subject_id="editor-only", role=ROLE_EDITOR))
    db_session.commit()
    assert client.get("/api/v1/inventory/product/INV-AUTHZ-P1", headers=_headers("editor-only")).status_code == 200
    assert client.get("/api/v1/inventory/", headers=_headers("editor-only")).status_code == 403
    assert client.post(
        "/api/v1/inventory/stock-in",
        json={
            "product_id": "INV-AUTHZ-P1",
            "quantity": 1,
            "purchase_price_usd": 1.0,
            "fx_rate_usd_to_irr": 1_000_000.0,
        },
        headers=_headers("editor-only"),
    ).status_code == 403
    assert client.get("/api/v1/inventory/", headers=_headers("ordinary-customer")).status_code == 403
