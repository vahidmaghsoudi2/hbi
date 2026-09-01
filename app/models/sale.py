from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.base import Base

class Sale(Base):
    __tablename__ = "Sale"
    sale_id = Column(String, primary_key=True)
    customer_id = Column(String, ForeignKey("Customer.customer_id", ondelete="RESTRICT"), nullable=False)
    total_amount_toman = Column(Integer, nullable=False)  # legacy retained
    total_amount_usd = Column(Float, nullable=True)
    fx_rate_usd_to_irr = Column(Float, nullable=True)  # IRR per 1 USD snapshot
    total_amount_irr = Column(Float, nullable=True)
    created_at = Column(DateTime, server_default=func.current_timestamp())
    __table_args__ = ()
    customer = relationship("Customer", back_populates="sales")
    sale_items = relationship("SaleItem", back_populates="sale", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="sale")
