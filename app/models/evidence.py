from sqlalchemy import Column, DateTime, ForeignKey, String, text
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
    __table_args__ = ()
