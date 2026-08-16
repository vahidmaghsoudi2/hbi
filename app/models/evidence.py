from sqlalchemy import Column, DateTime, ForeignKey, String, CheckConstraint, text
from sqlalchemy.orm import relationship
from app.models.base import Base

class Evidence(Base):
    __tablename__ = "Evidence"
    evidence_id = Column(String, primary_key=True)
    product_id = Column(String, ForeignKey("Product.product_id", ondelete="RESTRICT"), nullable=False)
    claim_id = Column(String, unique=True, nullable=True)
    source_type = Column(String, nullable=False)
    source_reference = Column(String, nullable=False)
    claim = Column(String, nullable=False)
    field = Column(String, nullable=True)
    market_region = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    claim_type = Column(String, nullable=True)
    evidence_strength = Column(String, nullable=True)
    evidence_status = Column(String, nullable=True)
    conflict_status = Column(String, nullable=True)
    source_date = Column(String, nullable=True)
    evidence_date = Column(DateTime, nullable=True)
    qa_status = Column(String, nullable=True, server_default=text("'PENDING'"))
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    product = relationship("Product", back_populates="evidences")

    __table_args__ = (
        CheckConstraint("claim_type IS NULL OR claim_type IN ('FACT','MANUFACTURER_CLAIM','EVIDENCE_SUPPORTED','INFERENCE','UNKNOWN')", name="ck_evidence_claim_type_v1_2"),
        CheckConstraint("evidence_strength IS NULL OR evidence_strength IN ('STRONG','MODERATE','WEAK','UNVERIFIED')", name="ck_evidence_strength_v1_2"),
        CheckConstraint("evidence_status IS NULL OR evidence_status IN ('SUPPORTED','PARTIAL','CONFLICT','UNKNOWN')", name="ck_evidence_status_v1_2"),
        CheckConstraint("conflict_status IS NULL OR conflict_status IN ('NONE','CONFLICT')", name="ck_evidence_conflict_status_v1_2"),
        CheckConstraint("qa_status IS NULL OR qa_status IN ('PENDING','VERIFIED','REJECTED','NEEDS_REVIEW')", name="ck_evidence_qa_status_v1_2"),
    )
