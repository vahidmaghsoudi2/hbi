from sqlalchemy import CheckConstraint, Column, DateTime, Float, ForeignKey, String
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
        CheckConstraint("evidence_status IS NULL OR evidence_status IN ('SUPPORTED', 'PARTIAL', 'CONFLICT', 'UNKNOWN')", name="ck_productknowledge_evidence_status"),
        CheckConstraint("knowledge_confidence IS NULL OR (knowledge_confidence >= 0.0 AND knowledge_confidence <= 1.0)", name="ck_productknowledge_knowledge_confidence"),
    )
    product = relationship("Product", back_populates="product_knowledge")
