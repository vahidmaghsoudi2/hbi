from sqlalchemy.engine import Engine
from sqlalchemy import event
import os
from pathlib import Path

BASE_DIR = Path(r"E:\HBI")
MODELS_DIR = BASE_DIR / "app" / "models"
APP_DIR = BASE_DIR / "app"

# ایجاد پوشه‌ها
MODELS_DIR.mkdir(parents=True, exist_ok=True)
APP_DIR.mkdir(parents=True, exist_ok=True)
(BASE_DIR / "data").mkdir(parents=True, exist_ok=True)

# ایجاد فایل خالی app/__init__.py (خیلی مهم)
(APP_DIR / "__init__.py").write_text("", encoding="utf-8")

files = {}

files["__init__.py"] = '''from app.models.base import Base
from app.models.product import Product
from app.models.product_knowledge import ProductKnowledge
from app.models.evidence import Evidence
from app.models.customer import Customer
from app.models.case import Case
from app.models.recommendation import Recommendation
from app.models.inventory import Inventory
from app.models.sale import Sale
from app.models.sale_item import SaleItem

__all__ = [
    "Base",
    "Product",
    "ProductKnowledge",
    "Evidence",
    "Customer",
    "Case",
    "Recommendation",
    "Inventory",
    "Sale",
    "SaleItem",
]
'''

files["base.py"] = '''from sqlalchemy.orm import declarative_base
from sqlalchemy import MetaData

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)
Base = declarative_base(metadata=metadata)
'''

from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.base import Base

class Product(Base):
    __tablename__ = "Product"

    product_id = Column(String, primary_key=True)
    brand = Column(String, nullable=False)
    product_name = Column(String, nullable=False)
    variant = Column(String, nullable=True)
    size_value = Column(Float, nullable=True)
    size_unit = Column(String, nullable=True)
    barcode_gtin = Column(String, unique=True, nullable=True)
    market_region = Column(String, nullable=True)
    country_of_origin = Column(String, nullable=True)
    packaging_version = Column(String, nullable=True)

    identity_status = Column(String, nullable=False)
    identity_confidence = Column(Float, nullable=True)
    identity_source_refs = Column(String, nullable=True)

    qa_verdict = Column(String, nullable=False, server_default="PENDING")
    qa_reviewed_at = Column(DateTime, nullable=True)
    qa_notes = Column(String, nullable=True)

    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    __table_args__ = (
            "identity_status IN ('VERIFIED', 'PARTIAL_IDENTITY', 'CONFLICT', 'NEEDS_REVIEW')",
            name="ck_product_identity_status"
        ),
            "identity_confidence IS NULL OR (identity_confidence >= 0.0 AND identity_confidence <= 1.0)",
            name="ck_product_identity_confidence"
        ),
            "qa_verdict IN ('PENDING', 'VALID', 'INVALID', 'CONFLICT', 'UNKNOWN', 'NEEDS_REVIEW')",
            name="ck_product_qa_verdict"
        ),
    )

    product_knowledge = relationship("ProductKnowledge", back_populates="product", uselist=False)
    evidences = relationship("Evidence", back_populates="product")
    inventory = relationship("Inventory", back_populates="product", uselist=False)
    recommendations = relationship("Recommendation", back_populates="product")
    sale_items = relationship("SaleItem", back_populates="product")
'''

from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.base import Base

class ProductKnowledge(Base):
    __tablename__ = "ProductKnowledge"

    product_knowledge_id = Column(String, primary_key=True)
    product_id = Column(String, ForeignKey("Product.product_id", ondelete="RESTRICT"), nullable=False, unique=True)

    ingredients = Column(String, nullable=True)
    ingredient_roles = Column(String, nullable=True)
    claimed_benefits = Column(String, nullable=True)
    known_use_cases = Column(String, nullable=True)
    contraindications = Column(String, nullable=True)
    usage_instructions = Column(String, nullable=True)
    manufacturer_claims = Column(String, nullable=True)
    evidence_refs = Column(String, nullable=True)

    evidence_status = Column(String, nullable=True)
    knowledge_confidence = Column(Float, nullable=True)

    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    __table_args__ = (
            "evidence_status IS NULL OR evidence_status IN ('SUPPORTED', 'PARTIAL', 'CONFLICT', 'UNKNOWN')",
            name="ck_productknowledge_evidence_status"
        ),
            "knowledge_confidence IS NULL OR (knowledge_confidence >= 0.0 AND knowledge_confidence <= 1.0)",
            name="ck_productknowledge_knowledge_confidence"
        ),
    )

    product = relationship("Product", back_populates="product_knowledge")
'''

from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.base import Base

class Evidence(Base):
    __tablename__ = "Evidence"

    evidence_id = Column(String, primary_key=True)
    product_id = Column(String, ForeignKey("Product.product_id", ondelete="RESTRICT"), nullable=False)

    source_type = Column(String, nullable=False)
    source_reference = Column(String, nullable=False)
    claim = Column(String, nullable=False)

    claim_type = Column(String, nullable=True)
    evidence_level = Column(String, nullable=True)
    evidence_status = Column(String, nullable=True)
    conflict_status = Column(String, nullable=True)
    source_date = Column(String, nullable=True)
    retrieved_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, server_default=func.current_timestamp())

    __table_args__ = (
            "claim_type IS NULL OR claim_type IN ('FACT', 'MANUFACTURER_CLAIM', 'EVIDENCE_SUPPORTED', 'INFERENCE', 'UNKNOWN')",
            name="ck_evidence_claim_type"
        ),
            "evidence_status IS NULL OR evidence_status IN ('SUPPORTED', 'PARTIAL', 'CONFLICT', 'UNKNOWN')",
            name="ck_evidence_evidence_status"
        ),
            "conflict_status IS NULL OR conflict_status IN ('NONE', 'CONFLICT')",
            name="ck_evidence_conflict_status"
        ),
    )

    product = relationship("Product", back_populates="evidences")
'''

from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.base import Base

class Customer(Base):
    __tablename__ = "Customer"

    customer_id = Column(String, primary_key=True)
    name = Column(String, nullable=False, server_default="")
    mobile = Column(String, nullable=True)
    consent_to_store_data = Column(Integer, nullable=False, server_default="0")
    consent_date = Column(DateTime, nullable=True)

    age_range = Column(String, nullable=True)
    sex_if_relevant = Column(String, nullable=True)
    skin_profile = Column(String, nullable=True)
    hair_profile = Column(String, nullable=True)
    scalp_profile = Column(String, nullable=True)
    concerns = Column(String, nullable=True)
    observations = Column(String, nullable=True)
    answers = Column(String, nullable=True)
    case_history = Column(String, nullable=True)
    operator_notes = Column(String, nullable=True)

    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    __table_args__ = (
            "consent_to_store_data IN (0, 1)",
            name="ck_customer_consent_to_store_data"
        ),
    )

    cases = relationship("Case", back_populates="customer")
    sales = relationship("Sale", back_populates="customer")
'''

from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.base import Base

class Case(Base):
    __tablename__ = "Case"

    case_id = Column(String, primary_key=True)
    customer_id = Column(String, ForeignKey("Customer.customer_id", ondelete="RESTRICT"), nullable=False)

    case_type = Column(String, nullable=True)
    identified_needs = Column(String, nullable=True)
    evidence_gaps = Column(String, nullable=True)
    confidence = Column(Float, nullable=True)
    operator_override = Column(String, nullable=True)
    reasoning_status = Column(String, nullable=True)

    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    __table_args__ = (
            "confidence IS NULL OR (confidence >= 0.0 AND confidence <= 1.0)",
            name="ck_case_confidence"
        ),
    )

    customer = relationship("Customer", back_populates="cases")
    recommendations = relationship("Recommendation", back_populates="case")
'''

from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.base import Base

class Recommendation(Base):
    __tablename__ = "Recommendation"

    recommendation_id = Column(String, primary_key=True)
    case_id = Column(String, ForeignKey("Case.case_id", ondelete="CASCADE"), nullable=False)
    product_id = Column(String, ForeignKey("Product.product_id", ondelete="RESTRICT"), nullable=False)

    need_match_score = Column(Float, nullable=True)
    evidence_score = Column(Float, nullable=True)
    eligibility_status = Column(String, nullable=True)
    ranking_score = Column(Float, nullable=True)
    ranking_reasons = Column(String, nullable=True)
    exclusion_reasons = Column(String, nullable=True)

    created_at = Column(DateTime, server_default=func.current_timestamp())

    __table_args__ = (
            "need_match_score IS NULL OR (need_match_score >= 0.0 AND need_match_score <= 1.0)",
            name="ck_recommendation_need_match_score"
        ),
            "evidence_score IS NULL OR (evidence_score >= 0.0 AND evidence_score <= 1.0)",
            name="ck_recommendation_evidence_score"
        ),
            "eligibility_status IS NULL OR eligibility_status IN ('ELIGIBLE', 'INELIGIBLE_PENDING_VERIFICATION', 'INELIGIBLE_CONFLICT', 'INELIGIBLE_PENDING_REVIEW', 'INELIGIBLE_OUT_OF_STOCK')",
            name="ck_recommendation_eligibility_status"
        ),
    )

    case = relationship("Case", back_populates="recommendations")
    product = relationship("Product", back_populates="recommendations")
'''

from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.base import Base

class Inventory(Base):
    __tablename__ = "Inventory"

    inventory_id = Column(String, primary_key=True)
    product_id = Column(String, ForeignKey("Product.product_id", ondelete="RESTRICT"), nullable=False, unique=True)

    quantity_available = Column(Integer, nullable=False, server_default="0")
    quantity_reserved = Column(Integer, nullable=False, server_default="0")
    quantity_damaged = Column(Integer, nullable=False, server_default="0")
    stock_status = Column(String, nullable=False, server_default="OUT_OF_STOCK")

    purchase_price_toman = Column(Integer, nullable=True)
    sale_price_toman = Column(Integer, nullable=True)
    price_updated_at = Column(DateTime, nullable=True)

    updated_at = Column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    __table_args__ = (
            "stock_status IN ('AVAILABLE', 'RESERVED', 'DAMAGED', 'OUT_OF_STOCK')",
            name="ck_inventory_stock_status"
        ),
    )

    product = relationship("Product", back_populates="inventory")
'''

from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.base import Base

class Sale(Base):
    __tablename__ = "Sale"

    sale_id = Column(String, primary_key=True)
    customer_id = Column(String, ForeignKey("Customer.customer_id", ondelete="RESTRICT"), nullable=False)
    total_amount_toman = Column(Integer, nullable=False)

    created_at = Column(DateTime, server_default=func.current_timestamp())

    __table_args__ = (
    )

    customer = relationship("Customer", back_populates="sales")
    sale_items = relationship("SaleItem", back_populates="sale", cascade="all, delete-orphan")
'''

from sqlalchemy.orm import relationship
from app.models.base import Base

class SaleItem(Base):
    __tablename__ = "SaleItem"

    sale_item_id = Column(String, primary_key=True)
    sale_id = Column(String, ForeignKey("Sale.sale_id", ondelete="CASCADE"), nullable=False)
    product_id = Column(String, ForeignKey("Product.product_id", ondelete="RESTRICT"), nullable=False)

    quantity = Column(Integer, nullable=False)
    unit_price_toman = Column(Integer, nullable=False)

    __table_args__ = (
    )

    sale = relationship("Sale", back_populates="sale_items")
    product = relationship("Product", back_populates="sale_items")
'''

# نوشتن فایل‌های models
for filename, content in files.items():
    file_path = MODELS_DIR / filename
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Created: {file_path}")

# فایل database.py
database_content = '''from sqlalchemy import create_engine, event, text
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
'''

db_path = APP_DIR / "database.py"
with open(db_path, "w", encoding="utf-8") as f:
    f.write(database_content)
print(f"Created: {db_path}")

print()
print("=" * 60)
print("All files created successfully!")
print("=" * 60)