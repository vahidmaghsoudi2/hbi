from typing import Optional, List, Dict, Any
import json
from sqlalchemy.orm import Session
from app.models.case import Case
from app.repositories.case_repository import CaseRepository
from app.services.base import BaseService
from datetime import datetime
from uuid import uuid4

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
        # Microseconds + short uuid: concurrent creates in the same second stay unique.
        # Prefix CASE_ retained for existing contract/trace consumers.
        case_id = (
            f"CASE_{datetime.now().strftime('%Y%m%d%H%M%S%f')}_{uuid4().hex[:8]}"
        )
        return self.create(
            case_id=case_id,
            customer_id=customer_id,
            case_type=case_type
        )

    def save_consultation_context(self, case_id: str, context: Dict[str, Any]) -> Optional[Case]:
        case = self.repository.get_by_id(case_id)
        if case is None:
            return None
        raw = case.evidence_gaps
        try:
            envelope = json.loads(raw) if raw else {}
            if not isinstance(envelope, dict):
                envelope = {"legacy_value": raw}
        except (TypeError, ValueError):
            envelope = {"legacy_value": raw}
        envelope["consultation_v1"] = context
        case.evidence_gaps = json.dumps(envelope, ensure_ascii=False, separators=(",", ":"))
        self.db.flush()
        return case

    def get_consultation_context(self, case_id: str) -> Optional[Dict[str, Any]]:
        case = self.repository.get_by_id(case_id)
        if case is None:
            return None
        try:
            envelope = json.loads(case.evidence_gaps or "{}")
        except (TypeError, ValueError):
            return None
        if not isinstance(envelope, dict):
            return None
        context = envelope.get("consultation_v1")
        return context if isinstance(context, dict) else None

    def close_case(self, case_id: str) -> Optional[Case]:
        return self.update(case_id, case_type="CLOSED")
