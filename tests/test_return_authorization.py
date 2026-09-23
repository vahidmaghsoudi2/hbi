"""RETURN-AUTHZ-001 — V1 PO Contract: ADMIN owns return financial mutations."""

from app.core.auth import create_access_token
from app.models.customer import Customer
from app.models.inventory import Inventory
from app.models.product import Product
from app.models.sale_return import SaleReturn
from app.models.user_role import ROLE_ADMIN, UserRole
from app.services.sale_service import SaleService


def _setup(db_session):
    db_session.add_all([
        Customer(customer_id="RET-C1", name="Owner", consent_to_store_data=1),
        Customer(customer_id="RET-C2", name="Foreign", consent_to_store_data=1),
        Product(
            product_id="RET-P1",
            brand="B",
            product_name="Return Product",
            identity_status="VERIFIED",
            qa_verdict="PENDING",
            status="ACTIVE",
        ),
        UserRole(user_role_id="UR-ADMIN-RET", subject_id="USR_ADMIN", role=ROLE_ADMIN),
    ])
    db_session.commit()
    # Persist Product before Inventory because SQLite FK enforcement is enabled in conftest.
    db_session.add(
        Inventory(
            inventory_id="RET-INV1",
            product_id="RET-P1",
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
    sale = SaleService(db_session).create_sale(
        "RET-C1",
        [{"product_id": "RET-P1", "quantity": 1, "unit_price_usd": 10.0}],
        fx_rate_usd_to_irr=1_000_000.0,
    )
    db_session.commit()
    return sale


def _headers(subject_id: str):
    return {"Authorization": f"Bearer {create_access_token({'sub': subject_id})}"}


def test_return_admin_create_and_list(client, db_session):
    sale = _setup(db_session)
    before_inventory = db_session.query(Inventory).filter_by(product_id="RET-P1").one().quantity_available

    payload = {
        "sale_id": sale.sale_id,
        "product_id": "RET-P1",
        "quantity": 1,
        "reason": "admin return",
    }
    # Customer must not create return (ADMIN-only).
    denied = client.post("/api/v1/returns/", json=payload, headers=_headers("RET-C1"))
    assert denied.status_code == 403, denied.text

    created = client.post("/api/v1/returns/", json=payload, headers=_headers("USR_ADMIN"))
    assert created.status_code == 200, created.text
    assert created.json()["sale_id"] == sale.sale_id
    assert db_session.query(SaleReturn).count() == 1
    after_inventory = db_session.query(Inventory).filter_by(product_id="RET-P1").one().quantity_available
    assert after_inventory == before_inventory + 1

    listed = client.get(f"/api/v1/returns/sale/{sale.sale_id}", headers=_headers("USR_ADMIN"))
    assert listed.status_code == 200, listed.text
    assert len(listed.json()) == 1


def test_return_customer_create_is_forbidden_and_state_unchanged(client, db_session):
    sale = _setup(db_session)
    before_count = db_session.query(SaleReturn).count()
    before_inventory = db_session.query(Inventory).filter_by(product_id="RET-P1").one().quantity_available

    payload = {
        "sale_id": sale.sale_id,
        "product_id": "RET-P1",
        "quantity": 1,
    }
    response = client.post("/api/v1/returns/", json=payload, headers=_headers("RET-C2"))
    assert response.status_code == 403, response.text
    assert db_session.query(SaleReturn).count() == before_count
    assert db_session.query(Inventory).filter_by(product_id="RET-P1").one().quantity_available == before_inventory


def test_return_customer_list_is_forbidden(client, db_session):
    sale = _setup(db_session)
    response = client.get(f"/api/v1/returns/sale/{sale.sale_id}", headers=_headers("RET-C2"))
    assert response.status_code == 403, response.text


def test_return_authentication_and_missing_sale_contract(client, db_session):
    sale = _setup(db_session)
    payload = {"sale_id": sale.sale_id, "product_id": "RET-P1", "quantity": 1}

    assert client.post("/api/v1/returns/", json=payload).status_code == 401
    assert client.post(
        "/api/v1/returns/",
        json=payload,
        headers={"Authorization": "Bearer invalid-token"},
    ).status_code == 401
    # Non-admin authenticated subject gets 403 before missing-resource check.
    assert client.get("/api/v1/returns/sale/MISSING", headers=_headers("RET-C1")).status_code == 403
    # Admin reaches resource check → 404 for missing sale.
    assert client.get("/api/v1/returns/sale/MISSING", headers=_headers("USR_ADMIN")).status_code == 404
    assert client.post(
        "/api/v1/returns/",
        json={**payload, "sale_id": "MISSING"},
        headers=_headers("USR_ADMIN"),
    ).status_code == 404
