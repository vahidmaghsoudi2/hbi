"""PHASE 02 — Schema migration on disposable SQLite clone. Real FK via PRAGMA foreign_key_list."""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.accounting_phase02_migrate import (  # noqa: E402
    OFFICIAL_CATEGORIES,
    capture_row_counts,
    capture_schema,
    capture_toman_samples,
    foreign_key_list,
    has_fk_to,
    migrate,
)


def _create_legacy_db(path: str) -> None:
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
    assert "category_id" not in {c["name"] for c in schema["Product"]}
    assert counts["Product"] == 1
    assert toman["Inventory"][0][1] == 1500000


def test_migration_execution_and_post_schema(legacy_clone):
    evidence = migrate(legacy_clone)
    assert evidence["status"] == "SUCCESS"
    assert evidence["toman_preserved"] == "YES"
    assert evidence["row_counts_preserved"] == "YES"
    assert evidence["fk_check"] == "PASS"
    post = evidence["post_schema"]
    assert "category_id" in {c["name"] for c in post["Product"]}
    for t in ("Category", "StockMovement", "Payment", "SaleReturn", "OperationalFxRate"):
        assert t in post


def test_product_category_real_fk(legacy_clone):
    evidence = migrate(legacy_clone)
    assert evidence["product_category_fk_present"] is True
    conn = sqlite3.connect(legacy_clone)
    conn.execute("PRAGMA foreign_keys=ON")
    assert has_fk_to(conn, "Product", "Category", "category_id", "category_id")
    assert any(r[2] == "Category" and r[3] == "category_id" for r in foreign_key_list(conn, "Product"))
    conn.close()


def test_all_accounting_fks_via_pragma(legacy_clone):
    migrate(legacy_clone)
    conn = sqlite3.connect(legacy_clone)
    conn.execute("PRAGMA foreign_keys=ON")
    assert has_fk_to(conn, "Product", "Category", "category_id", "category_id")
    assert has_fk_to(conn, "SaleReturn", "Product", "product_id", "product_id")
    assert has_fk_to(conn, "SaleReturn", "Sale", "sale_id", "sale_id")
    assert has_fk_to(conn, "Payment", "Sale", "sale_id", "sale_id")
    assert has_fk_to(conn, "StockMovement", "Product", "product_id", "product_id")
    assert has_fk_to(conn, "Inventory", "Product", "product_id", "product_id")
    assert has_fk_to(conn, "SaleItem", "Product", "product_id", "product_id")
    assert has_fk_to(conn, "SaleItem", "Sale", "sale_id", "sale_id")
    assert has_fk_to(conn, "Sale", "Customer", "customer_id", "customer_id")
    conn.close()


def test_fk_check_zero_and_invalid_rejection(legacy_clone):
    evidence = migrate(legacy_clone)
    assert evidence["fk_check"] == "PASS"
    assert evidence["fk_check_violations"] == []
    conn = sqlite3.connect(legacy_clone)
    conn.execute("PRAGMA foreign_keys=ON")
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO SaleReturn (return_id, sale_id, product_id, quantity) VALUES ('RX','S1','NOPE',1)"
        )
        conn.commit()
    conn.rollback()
    conn.execute(
        "INSERT INTO SaleReturn (return_id, sale_id, product_id, quantity) VALUES ('R1','S1','P1',1)"
    )
    conn.commit()
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("UPDATE Product SET category_id='NOT_A_CAT' WHERE product_id='P1'")
        conn.commit()
    conn.rollback()
    conn.execute("UPDATE Product SET category_id='BEAUTY' WHERE product_id='P1'")
    conn.commit()
    assert conn.execute("SELECT category_id FROM Product WHERE product_id='P1'").fetchone()[0] == "BEAUTY"
    conn.close()


def test_category_seed_exactly_six(legacy_clone):
    evidence = migrate(legacy_clone)
    ids = {r[0] for r in evidence["category_rows"]}
    assert ids == {c[0] for c in OFFICIAL_CATEGORIES}
    assert len(evidence["category_rows"]) == 6


def test_row_counts_and_ids_preserved(legacy_clone):
    evidence = migrate(legacy_clone)
    pre, post = evidence["pre_row_counts"], evidence["post_row_counts"]
    for t in ("Product", "Inventory", "Sale", "SaleItem", "Customer"):
        assert post[t] == pre[t]
    conn = sqlite3.connect(legacy_clone)
    assert conn.execute("SELECT product_id FROM Product").fetchone()[0] == "P1"
    conn.close()


def test_toman_and_no_fx_conversion(legacy_clone):
    evidence = migrate(legacy_clone)
    assert evidence["pre_toman_samples"] == evidence["post_toman_samples"]
    assert evidence["toman_preserved"] == "YES"
    conn = sqlite3.connect(legacy_clone)
    row = conn.execute(
        "SELECT purchase_price_usd, sale_price_usd, price_fx_rate_usd_to_irr FROM Inventory WHERE inventory_id='I1'"
    ).fetchone()
    assert all(v is None for v in row)
    conn.close()


def test_idempotent(legacy_clone):
    e1 = migrate(legacy_clone)
    e2 = migrate(legacy_clone)
    assert e1["status"] == e2["status"] == "SUCCESS"
    assert e2["idempotent_re_run"] == "OK"
    assert e2["product_category_fk_present"] is True


def test_real_db_path_refused(tmp_path):
    fake = tmp_path / "data" / "hbi.db"
    fake.parent.mkdir(parents=True)
    fake.write_bytes(b"")
    from scripts.accounting_phase02_migrate import main
    assert main(["--db", str(fake)]) == 2


def test_migration_does_not_touch_frozen_artifacts():
    src = (ROOT / "scripts" / "accounting_phase02_migrate.py").read_text(encoding="utf-8")
    for f in ("seed_products", "PRODUCT_A", "scoring", "recommendation"):
        assert f not in src
