from sqlalchemy import Column, String, Integer, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from app.models.base import Base

class SaleItem(Base):
    __tablename__ = "SaleItem"

    sale_item_id = Column(String, primary_key=True)
    sale_id = Column(String, ForeignKey("Sale.sale_id", ondelete="CASCADE"), nullable=False)
    product_id = Column(String, ForeignKey("Product.product_id", ondelete="RESTRICT"), nullable=False)

    quantity = Column(Integer, nullable=False)
    unit_price_toman = Column(Integer, nullable=False)

    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_saleitem_quantity"),
        CheckConstraint("unit_price_toman >= 0", name="ck_saleitem_unit_price_toman"),
    )

    sale = relationship("Sale", back_populates="sale_items")
    product = relationship("Product", back_populates="sale_items")
