from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.customer import Customer
from app.repositories.base import BaseRepository

class CustomerRepository(BaseRepository[Customer]):
    def __init__(self, db: Session):
        super().__init__(Customer, db)

    def find_by_mobile(self, mobile: str) -> Optional[Customer]:
        return self.db.query(Customer).filter(Customer.mobile == mobile).first()

    def find_by_name(self, name: str) -> List[Customer]:
        return self.db.query(Customer).filter(Customer.name.ilike(f"%{name}%")).all()

    def get_with_cases(self, customer_id: str):
        return self.db.query(Customer).filter(Customer.customer_id == customer_id).first()
