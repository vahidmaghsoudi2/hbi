from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.models.base import Base

class SaleItem(Base):
    __tablename__ = "SaleItem"
    sale_item_id = Column(String, primary_key=True)
    sale_id = Column(String, ForeignKey("Sale.sale_id", ondelete="CASCADE"), nullable=False)
    product_id = Column(String, ForeignKey("Product.product_id", ondelete="RESTRICT"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price_toman = Column(Integer, nullable=False)  # legacy retained
    unit_price_usd = Column(Float, nullable=True)
    fx_rate_usd_to_irr = Column(Float, nullable=True)
    unit_price_irr = Column(Float, nullable=True)
    __table_args__ = ()
    sale = relationship("Sale", back_populates="sale_items")
    product = relationship("Product", back_populates="sale_items")
