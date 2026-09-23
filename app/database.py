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


def init_db():
    from app.models import product, product_knowledge, evidence, customer, case, recommendation, inventory, sale, sale_item, category, stock_movement, payment, sale_return, operational_fx_rate, product_mutation_log, user_role, profile_fact, admin_credential
    Base.metadata.create_all(bind=engine)
    _ensure_recommendation_trace_columns()
    _ensure_accounting_control_columns()
    with engine.connect() as conn:
        conn.execute(text("CREATE VIEW IF NOT EXISTS CustomerPurchaseHistory AS SELECT c.customer_id, si.product_id, si.quantity, s.created_at AS purchase_date FROM Sale s JOIN SaleItem si ON s.sale_id = si.sale_id JOIN Customer c ON s.customer_id = c.customer_id"))
        conn.commit()
