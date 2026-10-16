"""Regression tests for the SQLite walk-in-sale schema migration."""
from __future__ import annotations

import sqlite3

from sqlalchemy import create_engine

import app.database as database


def test_legacy_sale_customer_nullable_migration_preserves_rows_and_foreign_keys(monkeypatch, tmp_path):
    path = tmp_path / "legacy_sales.db"
    conn = sqlite3.connect(path)
    conn.executescript(
        """
        PRAGMA foreign_keys=ON;
        CREATE TABLE Customer (customer_id VARCHAR PRIMARY KEY, name VARCHAR);
        CREATE TABLE Sale (
          sale_id VARCHAR PRIMARY KEY,
          customer_id VARCHAR NOT NULL,
          total_amount_toman INTEGER NOT NULL,
          idempotency_key VARCHAR,
          document_status VARCHAR NOT NULL DEFAULT 'ACTIVE',
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          CONSTRAINT uq_sale_idempotency_key UNIQUE (idempotency_key),
          CONSTRAINT ck_sale_document_status CHECK (document_status IN ('ACTIVE', 'VOIDED')),
          FOREIGN KEY(customer_id) REFERENCES Customer(customer_id)
        );
        CREATE INDEX ix_sale_idempotency_key ON Sale(idempotency_key);
        CREATE TABLE SaleItem (
          sale_item_id VARCHAR PRIMARY KEY,
          sale_id VARCHAR NOT NULL,
          FOREIGN KEY(sale_id) REFERENCES Sale(sale_id)
        );
        INSERT INTO Customer(customer_id, name) VALUES ('C1', 'Legacy');
        INSERT INTO Sale(sale_id, customer_id, total_amount_toman, idempotency_key)
          VALUES ('S1', 'C1', 2000000, 'legacy-key');
        INSERT INTO SaleItem(sale_item_id, sale_id) VALUES ('SI1', 'S1');
        """
    )
    conn.commit()
    conn.close()

    test_engine = create_engine(f"sqlite:///{path}")
    monkeypatch.setattr(database, "engine", test_engine)
    database._ensure_sale_customer_optional()

    conn = sqlite3.connect(path)
    try:
        info = {row[1]: row for row in conn.execute('PRAGMA table_info("Sale")')}
        assert info["customer_id"][3] == 0
        assert conn.execute("SELECT sale_id, customer_id, total_amount_toman FROM Sale").fetchall() == [
            ("S1", "C1", 2000000)
        ]
        assert conn.execute("SELECT sale_item_id, sale_id FROM SaleItem").fetchall() == [("SI1", "S1")]
        assert conn.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='ix_sale_idempotency_key'").fetchone()
        assert conn.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='Sale'").fetchone()[0].find("ck_sale_document_status") >= 0
        conn.execute("PRAGMA foreign_keys=ON")
        assert conn.execute("PRAGMA foreign_key_check").fetchall() == []
        conn.execute("INSERT INTO Sale(sale_id, customer_id, total_amount_toman) VALUES ('S2', NULL, 500000)")
        conn.commit()
    finally:
        conn.close()
        test_engine.dispose()


def test_nullable_sale_migration_is_idempotent(monkeypatch, tmp_path):
    path = tmp_path / "already_nullable.db"
    conn = sqlite3.connect(path)
    conn.executescript(
        """
        CREATE TABLE Sale (sale_id VARCHAR PRIMARY KEY, customer_id VARCHAR, total_amount_toman INTEGER NOT NULL);
        INSERT INTO Sale VALUES ('S1', NULL, 500000);
        """
    )
    conn.commit()
    conn.close()
    test_engine = create_engine(f"sqlite:///{path}")
    monkeypatch.setattr(database, "engine", test_engine)
    database._ensure_sale_customer_optional()
    database._ensure_sale_customer_optional()
    conn = sqlite3.connect(path)
    try:
        assert conn.execute("SELECT sale_id, customer_id FROM Sale").fetchall() == [("S1", None)]
    finally:
        conn.close()
        test_engine.dispose()
