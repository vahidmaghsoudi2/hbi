"""Specialist Override — Mission B.

Records a specialist decision against an existing Recommendation without
mutating the original engine-produced row. Original eligibility, ranking,
and evidence_refs remain intact for full traceability.
"""
from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.models.base import Base


class SpecialistOverride(Base):
    __tablename__ = "SpecialistOverride"

    override_id = Column(String, primary_key=True)
    recommendation_id = Column(
        String,
        ForeignKey("Recommendation.recommendation_id", ondelete="CASCADE"),
        nullable=False,
    )
    case_id = Column(
        String,
        ForeignKey("Case.case_id", ondelete="CASCADE"),
        nullable=False,
    )
    specialist_id = Column(String, nullable=False)  # actor identity
    action = Column(String, nullable=False)  # ACCEPT | REJECT | MODIFY_SELECTION
    reason = Column(Text, nullable=False)
    original_eligibility = Column(String, nullable=True)  # snapshot at override time
    original_ranking_score = Column(String, nullable=True)  # stored as string for safety
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.current_timestamp())

    recommendation = relationship("Recommendation", backref="specialist_overrides")
    case = relationship("Case", backref="specialist_overrides")
