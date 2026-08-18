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
