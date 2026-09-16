"""Recommendation outcome / feedback capture (Mission B).

Records business outcomes only. Does NOT rewrite Need mappings, scoring,
or ProductKnowledge (Decision Contract Feedback boundary).
"""
from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.sql import func

from app.models.base import Base


class RecommendationOutcome(Base):
    __tablename__ = "RecommendationOutcome"

    outcome_id = Column(String, primary_key=True)
    case_id = Column(String, ForeignKey("Case.case_id", ondelete="CASCADE"), nullable=False)
    product_id = Column(String, ForeignKey("Product.product_id", ondelete="RESTRICT"), nullable=False)
    recommendation_id = Column(String, ForeignKey("Recommendation.recommendation_id", ondelete="SET NULL"), nullable=True)
    outcome_type = Column(String, nullable=False)
    actor_id = Column(String, nullable=False)
    notes = Column(Text, nullable=True)
    follow_up_notes = Column(Text, nullable=True)
    follow_up_status = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.current_timestamp())

    __table_args__ = (
        CheckConstraint(
            "outcome_type IN ('SHOWN', 'ACCEPTED', 'REJECTED', 'DEFERRED')",
            name="ck_recommendation_outcome_type",
        ),
        CheckConstraint(
            "follow_up_status IS NULL OR follow_up_status IN ('NONE', 'SCHEDULED', 'DONE', 'CANCELLED')",
            name="ck_recommendation_outcome_follow_up_status",
        ),
    )
