"""Auditable record of governed Product duplicate/naming checks."""
from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.sql import func
from app.models.base import Base


class DuplicateCheckAudit(Base):
    __tablename__ = "DuplicateCheckAudit"

    check_id = Column(String, primary_key=True)
    timestamp = Column(DateTime, nullable=False, server_default=func.current_timestamp(), index=True)
    actor_id = Column(String, nullable=False, index=True)
    actor_role = Column(String, nullable=True)
    result = Column(String, nullable=False)
    product_id = Column(String, nullable=True, index=True)
    input_snapshot = Column(Text, nullable=False)
    candidates = Column(Text, nullable=False)
    operator_decision = Column(String, nullable=True)
