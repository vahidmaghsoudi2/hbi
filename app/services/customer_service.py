from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.customer import Customer
from app.repositories.customer_repository import CustomerRepository
from app.services.base import BaseService
from datetime import datetime

class CustomerService(BaseService[Customer, CustomerRepository]):
    def __init__(self, db: Session):
        super().__init__(CustomerRepository(db), db)

    def find_by_mobile(self, mobile: str) -> Optional[Customer]:
        return self.repository.find_by_mobile(mobile)

    def find_by_name(self, name: str) -> List[Customer]:
        return self.repository.find_by_name(name)

    def get_with_cases(self, customer_id: str) -> Optional[Customer]:
        return self.repository.get_with_cases(customer_id)

    def register_customer(self, name: str, mobile: Optional[str] = None, **kwargs) -> Customer:
        if mobile:
            existing = self.find_by_mobile(mobile)
            if existing:
                raise ValueError(f"Customer with mobile {mobile} already exists")

        consent = kwargs.get("consent_to_store_data", 0)
        if consent not in (0, 1):
            raise ValueError("consent_to_store_data must be 0 or 1")

        if consent == 1 and "consent_date" not in kwargs:
            kwargs["consent_date"] = datetime.now()

        customer = self.create(
            customer_id=f"CUST_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            name=name,
            mobile=mobile,
            **kwargs
        )
        return customer
