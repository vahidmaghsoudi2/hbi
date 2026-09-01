"""Accounting V1 — Payment (data model)."""
from sqlalchemy import CheckConstraint, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.base import Base


class Payment(Base):
    __tablename__ = "Payment"

    payment_id = Column(String, primary_key=True)
    sale_id = Column(String, ForeignKey("Sale.sale_id", ondelete="RESTRICT"), nullable=False, index=True)
    method = Column(String, nullable=False)
    amount_usd = Column(Float, nullable=True)
    fx_rate_usd_to_irr = Column(Float, nullable=True)
    amount_irr = Column(Float, nullable=True)
    amount_toman = Column(Integer, nullable=True)
    paid_at = Column(DateTime, server_default=func.current_timestamp())
    note = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.current_timestamp())

    __table_args__ = (
        CheckConstraint(
            "method IN ('CASH', 'CARD', 'TRANSFER', 'OTHER')",
            name="payment_method",
        ),
    )

    sale = relationship("Sale", back_populates="payments")
