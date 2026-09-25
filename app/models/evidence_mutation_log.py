"""Append-only Evidence mutation audit trail for G4 Evidence Governance Parity."""
from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.sql import func
from app.models.base import Base


class EvidenceMutationLog(Base):
    __tablename__ = "EvidenceMutationLog"

    log_id = Column(String, primary_key=True)
    timestamp = Column(DateTime, nullable=False, server_default=func.current_timestamp())
    actor_id = Column(String, nullable=False)
    actor_role = Column(String, nullable=True)
    action = Column(String, nullable=False)
    target_entity = Column(String, nullable=False, server_default="Evidence")
    target_id = Column(String, nullable=False, index=True)
    product_id = Column(String, nullable=False, index=True)
    before_state = Column(Text, nullable=True)
    after_state = Column(Text, nullable=True)
    diff = Column(Text, nullable=True)
    reason = Column(String, nullable=True)
    resulting_state = Column(String, nullable=True)
    correlation_id = Column(String, nullable=True)
