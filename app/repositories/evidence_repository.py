from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.evidence import Evidence
from app.repositories.base import BaseRepository
import re


class EvidenceRepository(BaseRepository[Evidence]):
    def __init__(self, db: Session):
        super().__init__(Evidence, db)

    def find_by_product(self, product_id: str) -> List[Evidence]:
        return self.db.query(Evidence).filter(Evidence.product_id == product_id).all()

    def find_conflicts(self, product_id: str) -> List[Evidence]:
        return self.db.query(Evidence).filter(
            Evidence.product_id == product_id,
            Evidence.conflict_status == "CONFLICT"
        ).all()

    def find_unverified(self, product_id: str) -> List[Evidence]:
        return self.db.query(Evidence).filter(
            Evidence.product_id == product_id,
            Evidence.qa_status.in_(["PENDING", "NEEDS_REVIEW"])
        ).all()

    def get_next_claim_seq(self, product_id: str) -> int:
        results = self.db.query(Evidence.claim_id).filter(
            Evidence.product_id == product_id,
            Evidence.claim_id.isnot(None)
        ).all()
        max_seq = 0
        pattern = re.compile(rf"^EV-{re.escape(product_id)}-(\d+)$")
        for (claim_id,) in results:
            if claim_id:
                match = pattern.match(claim_id)
                if match:
                    seq = int(match.group(1))
                    if seq > max_seq:
                        max_seq = seq
        return max_seq + 1
