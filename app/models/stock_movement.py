"""Accounting V1 — StockMovement ledger (data model only; services later)."""
from sqlalchemy import CheckConstraint, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.sql import func
from app.models.base import Base


class StockMovement(Base):
    __tablename__ = "StockMovement"

    movement_id = Column(String, primary_key=True)
    product_id = Column(String, ForeignKey("Product.product_id", ondelete="RESTRICT"), nullable=False, index=True)
    inventory_id = Column(String, ForeignKey("Inventory.inventory_id", ondelete="RESTRICT"), nullable=True)
    movement_type = Column(String, nullable=False)
    quantity_delta = Column(Integer, nullable=False)
    quantity_after = Column(Integer, nullable=True)
    amount_usd = Column(Float, nullable=True)
    fx_rate_usd_to_irr = Column(Float, nullable=True)
    amount_irr = Column(Float, nullable=True)
    amount_toman = Column(Float, nullable=True)
    reference_type = Column(String, nullable=True)
    reference_id = Column(String, nullable=True)
    note = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.current_timestamp())

    __table_args__ = (
        CheckConstraint(
            "movement_type IN ('STOCK_IN', 'PURCHASE', 'SALE', 'RETURN_IN', 'RETURN_OUT', 'ADJUSTMENT')",
            name="stock_movement_type",
        ),
    )
