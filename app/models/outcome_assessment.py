from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.models.base import Base


class OutcomeAssessment(Base):
    """Explicit observed/customer-reported result for a consultation Case."""

    __tablename__ = "OutcomeAssessment"

    outcome_assessment_id = Column(String, primary_key=True)
    case_id = Column(String, ForeignKey("Case.case_id", ondelete="CASCADE"), nullable=False, index=True)
    recommendation_id = Column(
        String,
        ForeignKey("Recommendation.recommendation_id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    feedback_id = Column(
        String,
        ForeignKey("Feedback.feedback_id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    follow_up_id = Column(
        String,
        ForeignKey("FollowUp.follow_up_id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    product_id = Column(
        String,
        ForeignKey("Product.product_id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    result_state = Column(String, nullable=False, index=True)
    provenance = Column(String, nullable=False, index=True)
    actor_id = Column(String, nullable=True, index=True)
    observed_at = Column(DateTime, server_default=func.current_timestamp(), nullable=False)
    created_at = Column(DateTime, server_default=func.current_timestamp(), nullable=False)

    case = relationship("Case", backref="outcome_assessments")
    recommendation = relationship("Recommendation", backref="outcome_assessments")
    feedback = relationship("Feedback", backref="outcome_assessments")
    follow_up = relationship("FollowUp", backref="outcome_assessments")
    product = relationship("Product", backref="outcome_assessments")
