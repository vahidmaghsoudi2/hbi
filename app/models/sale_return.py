"""Accounting V1 — Return against a Sale (minimal entity; services later)."""
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.sql import func
from app.models.base import Base


class SaleReturn(Base):
    __tablename__ = "SaleReturn"

    return_id = Column(String, primary_key=True)
    sale_id = Column(String, ForeignKey("Sale.sale_id", ondelete="RESTRICT"), nullable=False, index=True)
    product_id = Column(String, ForeignKey("Product.product_id", ondelete="RESTRICT"), nullable=False)
    quantity = Column(Integer, nullable=False)
    amount_usd = Column(Float, nullable=True)
    fx_rate_usd_to_irr = Column(Float, nullable=True)
    amount_irr = Column(Float, nullable=True)
    amount_toman = Column(Integer, nullable=True)
    reason = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.current_timestamp())
