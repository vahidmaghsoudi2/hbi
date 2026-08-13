from typing import List
from sqlalchemy.orm import Session
from app.models.case import Case
from app.repositories.base import BaseRepository

class CaseRepository(BaseRepository[Case]):
    def __init__(self, db: Session):
        super().__init__(Case, db)

    def find_by_customer(self, customer_id: str) -> List[Case]:
        return self.db.query(Case).filter(Case.customer_id == customer_id).all()

    def find_by_case_type(self, case_type: str) -> List[Case]:
        return self.db.query(Case).filter(Case.case_type == case_type).all()

    def get_with_recommendations(self, case_id: str):
        return self.db.query(Case).filter(Case.case_id == case_id).first()
