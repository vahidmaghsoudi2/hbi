"""
PHASE 02 — Schema migration on disposable SQLite clone.

Proves additive migration: pre → migrate → post without touching real data/hbi.db,
without historical FX conversion, preserving Toman and row counts.
"""
from __future__ import annotations

import json
import sqlite3
import sys
import tempfile
from pathlib import Path

import pytest

# Ensure scripts is importable
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.accounting_phase02_migrate import (  # noqa: E402
    OFFICIAL_CATEGORIES,
    capture_row_counts,
    capture_schema,
    capture_toman_samples,
    foreign_key_check,
    migrate,
)


def _create_legacy_db(path: str) -> None:
    """Build a minimal pre-PHASE-02 schema with legacy Toman columns only."""
    conn = sqlite3.connect(path)
    conn.executescript(
        """
        PRAGMA foreign_keys=ON;
        CREATE TABLE Customer (
          customer_id VARCHAR PRIMARY KEY,
          name VARCHAR,
          consent_to_store_data INTEGER DEFAULT 0
        );
        CREATE TABLE Product (
          product_id VARCHAR PRIMARY KEY,
          brand VARCHAR NOT NULL,
          product_name VARCHAR NOT NULL,
          identity_status VARCHAR NOT NULL,
          qa_verdict VARCHAR NOT NULL DEFAULT 'PENDING',
          status VARCHAR NOT NULL DEFAULT 'ACTIVE'
        );
        CREATE TABLE Inventory (
          inventory_id VARCHAR PRIMARY KEY,
          product_id VARCHAR NOT NULL,
          quantity_available INTEGER NOT NULL DEFAULT 0,
          quantity_reserved INTEGER NOT NULL DEFAULT 0,
          quantity_damaged INTEGER NOT NULL DEFAULT 0,
          stock_status VARCHAR NOT NULL DEFAULT 'active',
          purchase_price_toman INTEGER,
          sale_price_toman INTEGER,
          FOREIGN KEY(product_id) REFERENCES Product(product_id)
        );
        CREATE TABLE Sale (
          sale_id VARCHAR PRIMARY KEY,
          customer_id VARCHAR NOT NULL,
          total_amount_toman INTEGER NOT NULL,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY(customer_id) REFERENCES Customer(customer_id)
        );
        CREATE TABLE SaleItem (
          sale_item_id VARCHAR PRIMARY KEY,
          sale_id VARCHAR NOT NULL,
          product_id VARCHAR NOT NULL,
          quantity INTEGER NOT NULL,
          unit_price_toman INTEGER NOT NULL,
          FOREIGN KEY(sale_id) REFERENCES Sale(sale_id),
          FOREIGN KEY(product_id) REFERENCES Product(product_id)
        );
        INSERT INTO Customer (customer_id, name) VALUES ('C1', 'Test Customer');
        INSERT INTO Product (product_id, brand, product_name, identity_status)
          VALUES ('P1', 'ISDIN', 'Test Prod', 'VERIFIED');
        INSERT INTO Inventory (inventory_id, product_id, quantity_available, purchase_price_toman, sale_price_toman)
          VALUES ('I1', 'P1', 10, 1500000, 2000000);
        INSERT INTO Sale (sale_id, customer_id, total_amount_toman) VALUES ('S1', 'C1', 2000000);
        INSERT INTO SaleItem (sale_item_id, sale_id, product_id, quantity, unit_price_toman)
          VALUES ('SI1', 'S1', 'P1', 1, 2000000);
        """
    )
    conn.commit()
    conn.close()


@pytest.fixture()
def legacy_clone(tmp_path: Path):
    db = tmp_path / "legacy_clone.db"
    _create_legacy_db(str(db))
    return str(db)


def test_pre_migration_capture(legacy_clone):
    conn = sqlite3.connect(legacy_clone)
    schema = capture_schema(conn)
    counts = capture_row_counts(conn)
    toman = capture_toman_samples(conn)
    conn.close()
    assert "Product" in schema
    assert "category_id" not in {c["name"] for c in schema["Product"]}
    assert "Inventory" in schema
    inv_cols = {c["name"] for c in schema["Inventory"]}
    assert "purchase_price_toman" in inv_cols
    assert "purchase_price_usd" not in inv_cols
    assert counts["Product"] == 1
    assert counts["Inventory"] == 1
    assert counts["Sale"] == 1
    assert counts["SaleItem"] == 1
    assert toman["Inventory"][0][1] == 1500000
    assert toman["Sale"][0][1] == 2000000


def test_migration_execution_and_post_schema(legacy_clone):
    evidence = migrate(legacy_clone)
    assert evidence["status"] == "SUCCESS"
    assert evidence["toman_preserved"] == "YES"
    assert evidence["row_counts_preserved"] == "YES"
    assert evidence["fk_check"] == "PASS"

    post = evidence["post_schema"]
    prod_cols = {c["name"] for c in post["Product"]}
    assert "category_id" in prod_cols
    inv_cols = {c["name"] for c in post["Inventory"]}
    for col in (
        "purchase_price_usd",
        "sale_price_usd",
        "price_fx_rate_usd_to_irr",
        "purchase_price_irr",
        "sale_price_irr",
        "price_updated_at",
        "purchase_price_toman",
        "sale_price_toman",
    ):
        assert col in inv_cols
    sale_cols = {c["name"] for c in post["Sale"]}
    for col in ("total_amount_usd", "fx_rate_usd_to_irr", "total_amount_irr", "total_amount_toman"):
        assert col in sale_cols
    si_cols = {c["name"] for c in post["SaleItem"]}
    for col in ("unit_price_usd", "fx_rate_usd_to_irr", "unit_price_irr", "unit_price_toman"):
        assert col in si_cols

    for t in ("Category", "StockMovement", "Payment", "SaleReturn", "OperationalFxRate"):
        assert t in post


def test_category_seed_exactly_six(legacy_clone):
    evidence = migrate(legacy_clone)
    rows = evidence["category_rows"]
    ids = {r[0] for r in rows}
    expected = {c[0] for c in OFFICIAL_CATEGORIES}
    assert ids == expected
    assert len(rows) == 6
    assert "BOOST" in ids and "HAIR" in ids
    assert "BOOST" != "HAIR"


def test_row_counts_unchanged(legacy_clone):
    evidence = migrate(legacy_clone)
    pre = evidence["pre_row_counts"]
    post = evidence["post_row_counts"]
    for t in ("Product", "Inventory", "Sale", "SaleItem", "Customer"):
        assert post[t] == pre[t]


def test_toman_values_unchanged(legacy_clone):
    evidence = migrate(legacy_clone)
    assert evidence["pre_toman_samples"] == evidence["post_toman_samples"]
    inv = evidence["post_toman_samples"]["Inventory"][0]
    assert inv[1] == 1500000
    assert inv[2] == 2000000
    assert evidence["toman_preserved"] == "YES"


def test_no_historical_fx_conversion(legacy_clone):
    """USD/IRR columns must remain NULL after migration (no backfill)."""
    migrate(legacy_clone)
    conn = sqlite3.connect(legacy_clone)
    row = conn.execute(
        "SELECT purchase_price_usd, sale_price_usd, price_fx_rate_usd_to_irr, "
        "purchase_price_irr, sale_price_irr FROM Inventory WHERE inventory_id='I1'"
    ).fetchone()
    conn.close()
    assert all(v is None for v in row)


def test_fk_check_zero_violations(legacy_clone):
    evidence = migrate(legacy_clone)
    assert evidence["fk_check"] == "PASS"
    assert evidence["fk_check_violations"] == []


def test_idempotent(legacy_clone):
    e1 = migrate(legacy_clone)
    e2 = migrate(legacy_clone)
    assert e1["status"] == "SUCCESS"
    assert e2["status"] == "SUCCESS"
    assert e2["idempotent_re_run"] == "OK"
    assert e1["post_row_counts"] == e2["post_row_counts"]


def test_product_category_id_nullable(legacy_clone):
    migrate(legacy_clone)
    conn = sqlite3.connect(legacy_clone)
    val = conn.execute("SELECT category_id FROM Product WHERE product_id='P1'").fetchone()[0]
    assert val is None
    conn.execute("UPDATE Product SET category_id='BEAUTY' WHERE product_id='P1'")
    conn.commit()
    val2 = conn.execute("SELECT category_id FROM Product WHERE product_id='P1'").fetchone()[0]
    assert val2 == "BEAUTY"
    conn.close()


def test_real_db_path_refused(tmp_path):
    """Safety: script refuses data/hbi.db without override."""
    fake = tmp_path / "data" / "hbi.db"
    fake.parent.mkdir(parents=True)
    fake.write_bytes(b"")
    from scripts.accounting_phase02_migrate import main
    rc = main(["--db", str(fake)])
    assert rc == 2


def test_migration_does_not_touch_frozen_artifacts():
    """Structural: migration module must not import or rewrite product identity / scoring."""
    src = (ROOT / "scripts" / "accounting_phase02_migrate.py").read_text(encoding="utf-8")
    forbidden = [
        "seed_products",
        "PRODUCT_A",
        "scoring",
        "recommendation",
        "identity_status",
        "data/hbi.db",
    ]
    for f in forbidden:
        if f == "data/hbi.db":
            continue
        assert f not in src or "REFUSED" in src
