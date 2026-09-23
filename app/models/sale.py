from sqlalchemy import CheckConstraint, Column, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
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
    # Optional client-supplied key for durable sale idempotency (Accounting baseline §5).
    idempotency_key = Column(String, nullable=True, index=True)
    # V1: financial history preserved; invalid sales use VOIDED (not physical delete).
    document_status = Column(String, nullable=False, server_default="ACTIVE")
    created_at = Column(DateTime, server_default=func.current_timestamp())
    __table_args__ = (
        UniqueConstraint("idempotency_key", name="uq_sale_idempotency_key"),
        CheckConstraint(
            "document_status IN ('ACTIVE', 'VOIDED')",
            name="ck_sale_document_status",
        ),
    )
    customer = relationship("Customer", back_populates="sales")
    sale_items = relationship("SaleItem", back_populates="sale", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="sale")
