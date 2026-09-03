"""P4 P0 — Unified append-only Product Mutation Log (Audit Trail + History)."""
from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.sql import func
from app.models.base import Base


class ProductMutationLog(Base):
    __tablename__ = "ProductMutationLog"

    log_id = Column(String, primary_key=True)
    timestamp = Column(DateTime, nullable=False, server_default=func.current_timestamp())
    actor_id = Column(String, nullable=False)
    actor_role = Column(String, nullable=True)
    action = Column(String, nullable=False)
    target_entity = Column(String, nullable=False, server_default="Product")
    target_id = Column(String, nullable=False, index=True)
    before_state = Column(Text, nullable=True)
    after_state = Column(Text, nullable=True)
    diff = Column(Text, nullable=True)
    reason = Column(String, nullable=True)
    resulting_state = Column(String, nullable=True)
    correlation_id = Column(String, nullable=True)
