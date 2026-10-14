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
    """SQLite-safe migration: allow walk-in/direct sales without a Customer row.

    Rebuilds only Sale, preserving all rows and declared constraints. Foreign-key
    enforcement is disabled outside a transaction for the rebuild and restored
    immediately; callers should still run the normal integrity checks.
    """
    if engine.dialect.name != "sqlite":
        return
    with engine.connect() as conn:
        tables = inspect(conn).get_table_names()
        if "Sale" not in tables:
            return
        info = conn.execute(text('PRAGMA table_info("Sale")')).fetchall()
        customer_col = next((row for row in info if row[1] == "customer_id"), None)
        if customer_col is None or int(customer_col[3]) == 0:
            return
        create_row = conn.execute(text(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name='Sale'"
        )).fetchone()
        if not create_row or not create_row[0]:
            raise RuntimeError("Cannot migrate Sale.customer_id: table DDL unavailable")
        ddl = create_row[0]
        import re
        new_ddl = re.sub(
            r'(customer_id\s+VARCHAR)\s+NOT NULL,
            r'\1,
            ddl,
            count=1,
            flags=re.IGNORECASE,
        )
        if new_ddl == ddl:
            raise RuntimeError("Cannot safely migrate Sale.customer_id nullable constraint")
        new_ddl = re.sub(
            r'CREATE TABLE\s+(?:IF NOT EXISTS\s+)?["\[]?Sale["\]]?,
            'CREATE TABLE "Sale__direct_sale_new"',
            new_ddl,
            count=1,
            flags=re.IGNORECASE,
        )
        columns = [row[1] for row in info]
        quoted = ", ".join('"' + name.replace('"', '""') + '"' for name in columns)
        conn.commit()
        conn.exec_driver_sql("PRAGMA foreign_keys=OFF")
        try:
            conn.exec_driver_sql(new_ddl)
            conn.exec_driver_sql(
                f'INSERT INTO "Sale__direct_sale_new" ({quoted}) SELECT {quoted} FROM "Sale"'
            )
            conn.exec_driver_sql('DROP TABLE "Sale"')
            conn.exec_driver_sql('ALTER TABLE "Sale__direct_sale_new" RENAME TO "Sale"')
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.exec_driver_sql("PRAGMA foreign_keys=ON")
        violations = conn.exec_driver_sql("PRAGMA foreign_key_check").fetchall()
        if violations:
            raise RuntimeError(f"Foreign-key violations after Sale migration: {violations[:5]}")


def init_db():
    from app.models import product, product_knowledge, evidence, evidence_mutation_log, customer, case, recommendation, inventory, sale, sale_item, category, stock_movement, payment, sale_return, operational_fx_rate, product_mutation_log, duplicate_check_audit, user_role, profile_fact, admin_credential, feedback, follow_up, outcome_assessment
    Base.metadata.create_all(bind=engine)
    _ensure_recommendation_trace_columns()
    _ensure_accounting_control_columns()
    _ensure_sale_customer_optional()
    with engine.connect() as conn:
        conn.execute(text("CREATE VIEW IF NOT EXISTS CustomerPurchaseHistory AS SELECT c.customer_id, si.product_id, si.quantity, s.created_at AS purchase_date FROM Sale s JOIN SaleItem si ON s.sale_id = si.sale_id JOIN Customer c ON s.customer_id = c.customer_id"))
        conn.commit()
