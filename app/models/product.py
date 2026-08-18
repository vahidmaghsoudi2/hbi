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
