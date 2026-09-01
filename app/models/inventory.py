import uuid
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.models.base import Base

class Inventory(Base):
    __tablename__ = "Inventory"

    inventory_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id = Column(String, ForeignKey("Product.product_id"), nullable=False)
    quantity_available = Column(Integer, nullable=False, default=0)
    quantity_reserved = Column(Integer, nullable=False, default=0)
    quantity_damaged = Column(Integer, nullable=False, default=0)
    stock_status = Column(String, nullable=False, default="active")
    purchase_price_toman = Column(Integer, nullable=True)  # legacy; retained for migration
    sale_price_toman = Column(Integer, nullable=True)  # legacy; retained for migration
    # Accounting V1 — Currency of Record USD + FX snapshot (C-01)
    purchase_price_usd = Column(Float, nullable=True)
    sale_price_usd = Column(Float, nullable=True)
    price_fx_rate_usd_to_irr = Column(Float, nullable=True)  # IRR per 1 USD at price set
    purchase_price_irr = Column(Float, nullable=True)
    sale_price_irr = Column(Float, nullable=True)
    price_updated_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Inventory(product_id={self.product_id}, available={self.quantity_available})>"
