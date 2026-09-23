"""INVENTORY-OUTFLOW-001 — non-customer stock outflow vs customer SALE."""
from __future__ import annotations

from datetime import datetime, timezone, timedelta

import pytest

from app.core.auth import create_access_token
from app.models.inventory import Inventory
from app.models.product import Product
from app.models.sale import Sale
from app.models.stock_movement import StockMovement
from app.models.user_role import ROLE_ADMIN, ROLE_EDITOR, UserRole
from app.services.inventory_service import InventoryService
from app.services.report_service import ReportService


def _headers(subject_id: str):
    return {"Authorization": f"Bearer {create_access_token({'sub': subject_id})}"}


def _seed(db, pid="P-OUT", qty=10):
    db.add(
        Product(
            product_id=pid,
            brand="B",
            product_name="Item",
            identity_status="VERIFIED",
            qa_verdict="VALID",
            status="ACTIVE",
        )
    )
    db.commit()
    db.add(
        Inventory(
            inventory_id=f"INV-{pid}",
            product_id=pid,
            quantity_available=qty,
            quantity_reserved=0,
            quantity_damaged=0,
            stock_status="active",
            sale_price_usd=12.0,
        )
    )
    db.commit()


def _grant(db, subject: str, role: str):
    db.add(UserRole(user_role_id=f"ROLE-{subject}-{role}", subject_id=subject, role=role))
    db.commit()


def test_damage_outflow_not_sale(db_session):
    _seed(db_session, qty=5)
    svc = InventoryService(db_session)
    result = svc.record_non_customer_outflow(
        "P-OUT", 2, reason="DAMAGE_WASTE", note="broken bottle", actor_id="admin-1"
    )
    db_session.commit()
    inv = result["inventory"]
    assert inv.quantity_available == 3
    mov = result["movement"]
    assert mov is not None
    assert mov.movement_type == "ADJUSTMENT"
    assert mov.reference_type == "OUTFLOW_DAMAGE_WASTE"
    assert mov.reference_id.startswith("OUTFLOW-")
    assert mov.quantity_delta == -2
    assert mov.amount_usd is None
    assert "reason=DAMAGE_WASTE" in (mov.note or "")
    assert "actor=admin-1" in (mov.note or "")
    assert db_session.query(Sale).count() == 0


def test_internal_and_shortage_reasons(db_session):
    _seed(db_session, pid="P-A", qty=8)
    svc = InventoryService(db_session)
    svc.record_non_customer_outflow("P-A", 1, reason="INTERNAL_USE")
    svc.record_non_customer_outflow("P-A", 1, reason="SHORTAGE_LOSS")
    db_session.commit()
    types = {m.reference_type for m in db_session.query(StockMovement).all()}
    assert "OUTFLOW_INTERNAL_USE" in types
    assert "OUTFLOW_SHORTAGE_LOSS" in types
    inv = db_session.query(Inventory).filter_by(product_id="P-A").one()
    assert inv.quantity_available == 6


def test_insufficient_stock_rejected(db_session):
    _seed(db_session, qty=1)
    svc = InventoryService(db_session)
    with pytest.raises(ValueError, match="insufficient"):
        svc.record_non_customer_outflow("P-OUT", 5, reason="OTHER")


def test_invalid_reason_rejected(db_session):
    _seed(db_session)
    svc = InventoryService(db_session)
    with pytest.raises(ValueError, match="invalid outflow reason"):
        svc.record_non_customer_outflow("P-OUT", 1, reason="FAKE_REASON")


def test_sale_still_uses_sale_movement(db_session):
    _seed(db_session, pid="P-SALE", qty=4)
    svc = InventoryService(db_session)
    svc.decrease_stock("P-SALE", 1, movement_type="SALE", note="customer sale")
    db_session.commit()
    mov = db_session.query(StockMovement).filter_by(movement_type="SALE").one()
    assert mov.quantity_delta == -1
    assert db_session.query(StockMovement).filter_by(movement_type="ADJUSTMENT").count() == 0


def test_outflow_does_not_inflate_sales_report(db_session):
    _seed(db_session, pid="P-REP", qty=10)
    InventoryService(db_session).record_non_customer_outflow("P-REP", 3, reason="DAMAGE_WASTE")
    db_session.commit()
    now = datetime.now(timezone.utc)
    report = ReportService(db_session).sales_report(
        start=now - timedelta(days=1), end=now + timedelta(days=1)
    )
    assert report["sale_count"] == 0


def test_api_outflow_admin_ok_and_editor_denied(client, db_session):
    _seed(db_session, qty=5)
    _grant(db_session, "admin-x", ROLE_ADMIN)
    _grant(db_session, "editor-x", ROLE_EDITOR)

    r = client.post(
        "/api/v1/inventory/outflow",
        json={"product_id": "P-OUT", "quantity": 1, "reason": "DAMAGE_WASTE", "note": "qa"},
        headers=_headers("admin-x"),
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["reason"] == "DAMAGE_WASTE"
    assert body["movement"]["movement_type"] == "ADJUSTMENT"
    assert body["movement"]["reference_type"] == "OUTFLOW_DAMAGE_WASTE"
    assert body["movement"].get("amount_usd") is None
    assert body["inventory"]["quantity_available"] == 4

    denied = client.post(
        "/api/v1/inventory/outflow",
        json={"product_id": "P-OUT", "quantity": 1, "reason": "INTERNAL_USE"},
        headers=_headers("editor-x"),
    )
    assert denied.status_code == 403
