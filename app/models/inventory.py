from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.base import Base

class Inventory(Base):
    __tablename__ = "Inventory"

    inventory_id = Column(String, primary_key=True)
    product_id = Column(String, ForeignKey("Product.product_id", ondelete="RESTRICT"), nullable=False, unique=True)

    quantity_available = Column(Integer, nullable=False, server_default="0")
    quantity_reserved = Column(Integer, nullable=False, server_default="0")
    quantity_damaged = Column(Integer, nullable=False, server_default="0")
    stock_status = Column(String, nullable=False, server_default="OUT_OF_STOCK")

    purchase_price_toman = Column(Integer, nullable=True)
    sale_price_toman = Column(Integer, nullable=True)
    price_updated_at = Column(DateTime, nullable=True)

    updated_at = Column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    __table_args__ = (
        CheckConstraint("quantity_available >= 0", name="ck_inventory_quantity_available"),
        CheckConstraint("quantity_reserved >= 0", name="ck_inventory_quantity_reserved"),
        CheckConstraint("quantity_damaged >= 0", name="ck_inventory_quantity_damaged"),
        CheckConstraint(
            "stock_status IN ('AVAILABLE', 'RESERVED', 'DAMAGED', 'OUT_OF_STOCK')",
            name="ck_inventory_stock_status"
        ),
    )

    product = relationship("Product", back_populates="inventory")
