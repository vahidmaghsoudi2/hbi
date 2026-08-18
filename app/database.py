from sqlalchemy.engine import Engine
from sqlalchemy import event
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker
from app.models.base import Base
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/hbi.db")

engine = create_engine(
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

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
    finally:
        db.close()

def init_db():
    from app.models import (
        product, product_knowledge, evidence, customer,
        case, recommendation, inventory, sale, sale_item
    )
    Base.metadata.create_all(bind=engine)

    with engine.connect() as conn:
        conn.execute(text("""
            CREATE VIEW IF NOT EXISTS CustomerPurchaseHistory AS
            SELECT
                c.customer_id,
                si.product_id,
                si.quantity,
                s.created_at AS purchase_date
            FROM Sale s
            JOIN SaleItem si ON s.sale_id = si.sale_id
            JOIN Customer c ON s.customer_id = c.customer_id
        """))
        conn.commit()
