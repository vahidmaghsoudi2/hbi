from sqlalchemy import Column, String, DateTime, ForeignKey, CheckConstraint
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
        CheckConstraint(
            "claim_type IS NULL OR claim_type IN ('FACT', 'MANUFACTURER_CLAIM', 'EVIDENCE_SUPPORTED', 'INFERENCE', 'UNKNOWN')",
            name="ck_evidence_claim_type"
        ),
        CheckConstraint(
            "evidence_status IS NULL OR evidence_status IN ('SUPPORTED', 'PARTIAL', 'CONFLICT', 'UNKNOWN')",
            name="ck_evidence_evidence_status"
        ),
        CheckConstraint(
            "conflict_status IS NULL OR conflict_status IN ('NONE', 'CONFLICT')",
            name="ck_evidence_conflict_status"
        ),
    )

    product = relationship("Product", back_populates="evidences")
