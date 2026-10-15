"""Regression tests for the legacy SQLite Sale.customer_id migration."""
from __future__ import annotations

from sqlalchemy import create_engine, inspect, text

import app.database as database


def test_legacy_sale_table_migrates_without_losing_history(tmp_path, monkeypatch):
    db_path = tmp_path / "legacy-sales.db"
    engine = create_engine(f"sqlite:///{db_path}")
    monkeypatch.setattr(database, "engine", engine)

    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE "Customer" (
                customer_id VARCHAR PRIMARY KEY,
                name VARCHAR NOT NULL
            )
        """))
        conn.execute(text("""
            CREATE TABLE "Sale" (
                sale_id VARCHAR NOT NULL PRIMARY KEY,
                customer_id VARCHAR NOT NULL,
                total_amount_toman INTEGER NOT NULL,
                total_amount_usd FLOAT,
                fx_rate_usd_to_irr FLOAT,
                total_amount_irr FLOAT,
                idempotency_key VARCHAR,
                document_status VARCHAR DEFAULT 'ACTIVE' NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT uq_sale_idempotency_key UNIQUE (idempotency_key),
                CONSTRAINT ck_sale_document_status CHECK (document_status IN ('ACTIVE', 'VOIDED')),
                FOREIGN KEY(customer_id) REFERENCES "Customer"(customer_id) ON DELETE RESTRICT
            )
        """))
        conn.execute(text("""
            CREATE TABLE "SaleItem" (
                sale_item_id VARCHAR PRIMARY KEY,
                sale_id VARCHAR NOT NULL,
                product_id VARCHAR NOT NULL,
                quantity INTEGER NOT NULL
            )
        """))
        conn.execute(text("""INSERT INTO "Customer" (customer_id, name) VALUES ('C-1', 'Buyer')"""))
        conn.execute(text("""
            INSERT INTO "Sale" (
                sale_id, customer_id, total_amount_toman, total_amount_usd,
                fx_rate_usd_to_irr, total_amount_irr, idempotency_key, document_status
            ) VALUES ('S-1', 'C-1', 2000, 2.0, 1000.0, 20000.0, 'key-1', 'ACTIVE')
        """))
        conn.execute(text("""
            INSERT INTO "SaleItem" (sale_item_id, sale_id, product_id, quantity)
            VALUES ('SI-1', 'S-1', 'P-1', 1)
        """))
        conn.execute(text("""
            CREATE VIEW CustomerPurchaseHistory AS
            SELECT c.customer_id, si.product_id, si.quantity, s.created_at AS purchase_date
            FROM "Sale" s
            JOIN "SaleItem" si ON s.sale_id = si.sale_id
            JOIN "Customer" c ON s.customer_id = c.customer_id
        """))

    database._ensure_sale_customer_optional()

    columns = {column["name"]: column for column in inspect(engine).get_columns("Sale")}
    assert columns["customer_id"]["nullable"] is True
    with engine.connect() as conn:
        sale = conn.execute(text('SELECT sale_id, customer_id, total_amount_toman, idempotency_key FROM "Sale"')).one()
        assert tuple(sale) == ("S-1", "C-1", 2000, "key-1")
        history = conn.execute(text("SELECT customer_id, product_id, quantity FROM CustomerPurchaseHistory")).one()
        assert tuple(history) == ("C-1", "P-1", 1)
        assert conn.execute(text('PRAGMA foreign_key_check("Sale")')).fetchall() == []

    engine.dispose()
