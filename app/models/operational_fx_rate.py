"""Operational FX rate (not historical transaction snapshot)."""
from sqlalchemy import Column, DateTime, Float, String
from sqlalchemy.sql import func
from app.models.base import Base


class OperationalFxRate(Base):
    """Current operational rate; must never cascade-update historical money rows."""

    __tablename__ = "OperationalFxRate"

    rate_id = Column(String, primary_key=True)
    fx_rate_usd_to_irr = Column(Float, nullable=False)
    effective_at = Column(DateTime, server_default=func.current_timestamp())
    note = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.current_timestamp())
