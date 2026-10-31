from sqlalchemy import Column, DateTime, Index, Integer, String, Text
from sqlalchemy.sql import func

from app.models.base import Base


class ProductProblemLinkAssessmentEvent(Base):
    """Append-only application history for assessment creation and reassessment."""

    __tablename__ = "ProductProblemLinkAssessmentEvent"

    event_id = Column(String, primary_key=True)
    # No FK by design: audit events must outlive the assessment row they describe.
    link_id = Column(String, nullable=False)
    assertion_key = Column(String, nullable=True, index=True)
    revision_no = Column(Integer, nullable=True)
    actor_id = Column(String, nullable=False)
    actor_role = Column(String, nullable=True)
    event_type = Column(String, nullable=False)
    reason = Column(Text, nullable=False)
    before_state = Column(Text, nullable=True)
    after_state = Column(Text, nullable=False)
    correlation_id = Column(String, nullable=True)
    timestamp = Column(DateTime, nullable=False, server_default=func.current_timestamp())

    __table_args__ = (Index("ix_ppl_event_link_time", "link_id", "timestamp"),)
