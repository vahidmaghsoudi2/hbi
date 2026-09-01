"""Accounting V1 — Category (data-driven). بوست and مو are independent codes."""
from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, Integer, String
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.base import Base


class Category(Base):
    __tablename__ = "Category"

    category_id = Column(String, primary_key=True)  # e.g. BOOST, HAIR, BEAUTY, TOOLS, PERFUME, OTHER
    name_fa = Column(String, nullable=False)
    name_en = Column(String, nullable=True)
    is_active = Column(Boolean, nullable=False, server_default="1")
    sort_order = Column(Integer, nullable=False, server_default="0")
    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(
        DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp()
    )

    __table_args__ = (
        CheckConstraint(
            "category_id IN ('BOOST', 'HAIR', 'BEAUTY', 'TOOLS', 'PERFUME', 'OTHER')",
            name="category_id_v1",
        ),
    )

    products = relationship("Product", back_populates="category")
