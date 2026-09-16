"""Feedback / Follow-up — Mission B.

Captures outcome feedback linked to Case and optional Recommendation.
Does not implement learning or automatic weight updates (Issue #37 remains OPEN).
"""
from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.models.base import Base


class Feedback(Base):
    __tablename__ = "Feedback"

    feedback_id = Column(String, primary_key=True)
    case_id = Column(
        String,
        ForeignKey("Case.case_id", ondelete="CASCADE"),
        nullable=False,
    )
    recommendation_id = Column(
        String,
        ForeignKey("Recommendation.recommendation_id", ondelete="SET NULL"),
        nullable=True,
    )
    source = Column(String, nullable=False)  # CUSTOMER | SPECIALIST | SYSTEM
    outcome = Column(String, nullable=True)  # ACCEPTED | REJECTED | PARTIAL | FOLLOW_UP_NEEDED
    rating = Column(String, nullable=True)  # optional simple scale as string
    comment = Column(Text, nullable=True)
    follow_up_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.current_timestamp())

    case = relationship("Case", backref="feedbacks")
    recommendation = relationship("Recommendation", backref="feedbacks")
