from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.base import Base


class FollowUp(Base):
    __tablename__ = "FollowUp"

    follow_up_id = Column(String, primary_key=True)
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
    scheduled_at = Column(DateTime, nullable=False)
    status = Column(String, nullable=False, server_default="SCHEDULED", index=True)
    created_at = Column(DateTime, server_default=func.current_timestamp(), nullable=False)
    created_by = Column(String, nullable=False)
    updated_at = Column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    updated_by = Column(String, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)

    case = relationship("Case", backref="follow_ups")
    recommendation = relationship("Recommendation", backref="follow_ups")
    feedback = relationship("Feedback", backref="follow_ups")
