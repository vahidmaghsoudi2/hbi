from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.case import Case
from app.repositories.case_repository import CaseRepository
from app.services.base import BaseService
from datetime import datetime

class CaseService(BaseService[Case, CaseRepository]):
    def __init__(self, db: Session):
        super().__init__(CaseRepository(db), db)

    def find_by_customer(self, customer_id: str) -> List[Case]:
        return self.repository.find_by_customer(customer_id)

    def find_by_case_type(self, case_type: str) -> List[Case]:
        return self.repository.find_by_case_type(case_type)

    def get_with_recommendations(self, case_id: str) -> Optional[Case]:
        return self.repository.get_with_recommendations(case_id)

    def create_case(self, customer_id: str, case_type: str = "OPEN") -> Case:
        case_id = f"CASE_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        return self.create(
            case_id=case_id,
            customer_id=customer_id,
            case_type=case_type
        )

    def close_case(self, case_id: str) -> Optional[Case]:
        return self.update(case_id, case_type="CLOSED")
