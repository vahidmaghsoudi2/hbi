from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.recommendation import Recommendation
from app.repositories.base import BaseRepository

class RecommendationRepository(BaseRepository[Recommendation]):
    def __init__(self, db: Session):
        super().__init__(Recommendation, db)

    def find_by_case(self, case_id: str) -> List[Recommendation]:
        return self.db.query(Recommendation).filter(Recommendation.case_id == case_id).all()

    def find_by_product(self, product_id: str) -> List[Recommendation]:
        return self.db.query(Recommendation).filter(Recommendation.product_id == product_id).all()

    def find_by_case_and_product(self, case_id: str, product_id: str) -> Optional[Recommendation]:
        """GAP-04: locate the single current Recommendation for Case + Product."""
        return (
            self.db.query(Recommendation)
            .filter(
                Recommendation.case_id == case_id,
                Recommendation.product_id == product_id,
            )
            .first()
        )

    def find_eligible(self) -> List[Recommendation]:
        return self.db.query(Recommendation).filter(Recommendation.eligibility_status == "ELIGIBLE").all()
