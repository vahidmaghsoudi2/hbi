from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.base import Base

class Customer(Base):
    __tablename__ = "Customer"

    customer_id = Column(String, primary_key=True)
    name = Column(String, nullable=False, server_default="")
    mobile = Column(String, nullable=True)
    consent_to_store_data = Column(Integer, nullable=False, server_default="0")
    consent_date = Column(DateTime, nullable=True)

    age_range = Column(String, nullable=True)
    sex_if_relevant = Column(String, nullable=True)
    skin_profile = Column(String, nullable=True)
    hair_profile = Column(String, nullable=True)
    scalp_profile = Column(String, nullable=True)
    concerns = Column(String, nullable=True)
    observations = Column(String, nullable=True)
    answers = Column(String, nullable=True)
    case_history = Column(String, nullable=True)
    operator_notes = Column(String, nullable=True)

    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    def __init__(self, **kwargs):
        kwargs.setdefault('name', '')
        super().__init__(**kwargs)


    __table_args__ = (
            "consent_to_store_data IN (0, 1)",
            name="ck_customer_consent_to_store_data"
        ),
    )

    cases = relationship("Case", back_populates="customer")
    sales = relationship("Sale", back_populates="customer")
