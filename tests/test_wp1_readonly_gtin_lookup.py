"""WP-1 — Read-only exact GTIN identification against Product Master.

Acceptance:
- unique match
- no match
- invalid / empty
- access control
- identify path creates no Product, does not change QA/status/identity, does not mutate inventory
Does not use DuplicateCheckService (which writes DuplicateCheckAudit).
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app as fastapi_app
from app.database import get_db
from app.models import Base
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.duplicate_check_audit import DuplicateCheckAudit


@pytest.fixture()
def api_env(monkeypatch):
    monkeypatch.setenv("HBI_ENV", "development")
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    db = Session()

    def override_get_db():
        try:
            yield db
        finally:
            pass

    fastapi_app.dependency_overrides[get_db] = override_get_db
    client = TestClient(fastapi_app)
    yield client, db
    fastapi_app.dependency_overrides.clear()
    db.close()
    Base.metadata.drop_all(bind=engine)


def _token(client: TestClient) -> str:
    r = client.post("/api/v1/auth/pilot-operator-token")
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


def _seed_product(db, *, product_id: str, gtin: str, status="DRAFT", qa="PENDING", identity="NEEDS_REVIEW"):
    p = Product(
        product_id=product_id,
        brand="HBI Test",
        product_name="WP1 Gtin Fixture",
        barcode_gtin=gtin,
        identity_status=identity,
        qa_verdict=qa,
        status=status,
        product_line="SKIN",
    )
    inv = Inventory(
        inventory_id=f"INV-{product_id}",
        product_id=product_id,
        quantity_available=0,
        quantity_reserved=0,
        stock_status="OUT_OF_STOCK",
    )
    db.add(p)
    db.add(inv)
    db.commit()
    return p


def test_unique_match_returns_existing_product_summary(api_env):
    client, db = api_env
    gtin = "8809598450011"
    _seed_product(db, product_id="WP1-MATCH-001", gtin=gtin)
    token = _token(client)

    r = client.get(
        f"/api/v1/products/by-gtin/{gtin}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["result"] == "MATCH"
    assert body["reason"] == "EXACT_BARCODE"
    assert body["product"]["product_id"] == "WP1-MATCH-001"
    assert body["product"]["barcode_gtin"] == gtin


def test_no_match_does_not_create_product_or_audit(api_env):
    client, db = api_env
    token = _token(client)
    gtin = "8809598450099"
    before_products = db.query(Product).count()
    before_inv = db.query(Inventory).count()
    before_audit = db.query(DuplicateCheckAudit).count()

    r = client.get(
        f"/api/v1/products/by-gtin/{gtin}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["result"] == "NO_MATCH"
    assert body["product"] is None
    assert "intake" in (body.get("intake_hint") or "").lower()

    assert db.query(Product).count() == before_products
    assert db.query(Inventory).count() == before_inv
    assert db.query(DuplicateCheckAudit).count() == before_audit


def test_invalid_empty_and_malformed_gtin(api_env):
    client, db = api_env
    token = _token(client)
    headers = {"Authorization": f"Bearer {token}"}

    for gtin in ["abc", "123", "12-34"]:
        r = client.get(f"/api/v1/products/by-gtin/{gtin}", headers=headers)
        assert r.status_code == 200, r.text
        assert r.json()["result"] == "INVALID"
        assert r.json()["product"] is None

    assert db.query(Product).count() == 0
    assert db.query(DuplicateCheckAudit).count() == 0


def test_unauthorized_without_token(api_env):
    client, _ = api_env
    r = client.get("/api/v1/products/by-gtin/8809598450011")
    assert r.status_code in (401, 403), r.text


def test_match_does_not_mutate_lifecycle_qa_or_inventory(api_env):
    client, db = api_env
    gtin = "8809598450028"
    _seed_product(
        db,
        product_id="WP1-STABLE-001",
        gtin=gtin,
        status="DRAFT",
        qa="PENDING",
        identity="NEEDS_REVIEW",
    )
    token = _token(client)

    r = client.get(
        f"/api/v1/products/by-gtin/{gtin}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200, r.text
    assert r.json()["result"] == "MATCH"

    product = db.query(Product).filter_by(product_id="WP1-STABLE-001").one()
    assert product.status == "DRAFT"
    assert product.qa_verdict == "PENDING"
    assert product.identity_status == "NEEDS_REVIEW"
    inv = db.query(Inventory).filter_by(product_id="WP1-STABLE-001").one()
    assert inv.quantity_available == 0
    assert inv.quantity_reserved == 0
    assert db.query(DuplicateCheckAudit).count() == 0
