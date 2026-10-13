from sqlalchemy import create_engine, event, text, inspect
from sqlalchemy.orm import sessionmaker
from app.models.base import Base
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/hbi.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def _ensure_recommendation_trace_columns():
    """Additive compatibility migration for Decision-Quality trace fields."""
    inspector = inspect(engine)
    if "Recommendation" not in inspector.get_table_names():
        return
    columns = {c["name"] for c in inspector.get_columns("Recommendation")}
    with engine.begin() as conn:
        if "evidence_refs" not in columns:
            conn.execute(text('ALTER TABLE "Recommendation" ADD COLUMN evidence_refs TEXT'))
        if "warnings" not in columns:
            conn.execute(text('ALTER TABLE "Recommendation" ADD COLUMN warnings TEXT'))
    sale_item_inspector = inspect(engine)
    if "SaleItem" not in sale_item_inspector.get_table_names():
        return
    sale_item_columns = {c["name"] for c in sale_item_inspector.get_columns("SaleItem")}
    with engine.begin() as conn:
        if "recommendation_id" not in sale_item_columns:
            conn.execute(text('ALTER TABLE "SaleItem" ADD COLUMN recommendation_id TEXT'))


def _ensure_accounting_control_columns():
    """Additive columns for payment/sale idempotency (Accounting baseline §5)."""
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    with engine.begin() as conn:
        if "Payment" in tables:
            cols = {c["name"] for c in inspector.get_columns("Payment")}
            if "idempotency_key" not in cols:
                conn.execute(text('ALTER TABLE "Payment" ADD COLUMN idempotency_key TEXT'))
        if "Sale" in tables:
            cols = {c["name"] for c in inspector.get_columns("Sale")}
            if "idempotency_key" not in cols:
                conn.execute(text('ALTER TABLE "Sale" ADD COLUMN idempotency_key TEXT'))
            if "document_status" not in cols:
                conn.execute(text('ALTER TABLE "Sale" ADD COLUMN document_status TEXT DEFAULT \'ACTIVE\''))


def _ensure_sale_customer_optional():
    """SQLite table rebuild: allow direct sales without fabricating a customer record."""
    if engine.dialect.name != "sqlite":
        return
    inspector = inspect(engine)
    if "Sale" not in inspector.get_table_names():
        return
    customer_col = next((c for c in inspector.get_columns("Sale") if c["name"] == "customer_id"), None)
    # Skip when the column is already nullable; rebuild only legacy NOT NULL schemas.
    if not customer_col or customer_col.get("nullable", True):
        return

    # SQLite cannot drop NOT NULL in place. Disable FK enforcement only on this
    # dedicated connection while rebuilding the parent table; preserve all rows.
    raw = engine.raw_connection()
    try:
        cursor = raw.cursor()
        cursor.execute("PRAGMA foreign_keys=OFF")
        cursor.execute("BEGIN")
        cursor.execute("""
            CREATE TABLE "Sale_new" (
                sale_id VARCHAR NOT NULL PRIMARY KEY,
                customer_id VARCHAR NULL,
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
        """)
        old_columns = {c["name"] for c in inspect(engine).get_columns("Sale")}
        columns = [
            "sale_id", "customer_id", "total_amount_toman", "total_amount_usd",
            "fx_rate_usd_to_irr", "total_amount_irr", "idempotency_key",
            "document_status", "created_at",
        ]
        available = [c for c in columns if c in old_columns]
        quoted = ", ".join(f'"{c}"' for c in available)
        cursor.execute(f'INSERT INTO "Sale_new" ({quoted}) SELECT {quoted} FROM "Sale"')
        # The compatibility view references Sale and must be recreated around the rebuild.
        cursor.execute('DROP VIEW IF EXISTS "CustomerPurchaseHistory"')
        cursor.execute('DROP TABLE "Sale"')
        cursor.execute('ALTER TABLE "Sale_new" RENAME TO "Sale"')
        cursor.execute('CREATE INDEX IF NOT EXISTS ix_Sale_idempotency_key ON "Sale" (idempotency_key)')
        cursor.execute('CREATE VIEW IF NOT EXISTS CustomerPurchaseHistory AS SELECT c.customer_id, si.product_id, si.quantity, s.created_at AS purchase_date FROM "Sale" s JOIN "SaleItem" si ON s.sale_id = si.sale_id JOIN "Customer" c ON s.customer_id = c.customer_id')
        raw.commit()
        cursor.execute("PRAGMA foreign_keys=ON")
        violations = cursor.execute("PRAGMA foreign_key_check").fetchall()
        if violations:
            raise RuntimeError(f"Foreign-key violations after Sale table migration: {violations[:5]}")
    except Exception:
        raw.rollback()
        raise
    finally:
        raw.close()


def init_db():
    from app.models import product, product_knowledge, evidence, evidence_mutation_log, customer, case, recommendation, inventory, sale, sale_item, category, stock_movement, payment, sale_return, operational_fx_rate, product_mutation_log, duplicate_check_audit, user_role, profile_fact, admin_credential, feedback, follow_up, outcome_assessment
    Base.metadata.create_all(bind=engine)
    _ensure_recommendation_trace_columns()
    _ensure_accounting_control_columns()
    _ensure_sale_customer_optional()
    with engine.connect() as conn:
        conn.execute(text("CREATE VIEW IF NOT EXISTS CustomerPurchaseHistory AS SELECT c.customer_id, si.product_id, si.quantity, s.created_at AS purchase_date FROM Sale s JOIN SaleItem si ON s.sale_id = si.sale_id JOIN Customer c ON s.customer_id = c.customer_id"))
        conn.commit()
