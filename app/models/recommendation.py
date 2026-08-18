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
