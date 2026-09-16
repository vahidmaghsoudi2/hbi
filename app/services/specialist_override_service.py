"""Specialist Override Service — Mission B.

Creates an audit record against an existing Recommendation.
Never mutates the original Recommendation row (engine output preserved).
Optionally records override_id on Case.operator_override as a pointer only.
"""
from typing import Optional
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.case import Case
from app.models.recommendation import Recommendation
from app.models.specialist_override import SpecialistOverride
from app.services.base import BaseService
from app.repositories.base import BaseRepository


class SpecialistOverrideRepository(BaseRepository[SpecialistOverride]):
    def __init__(self, db: Session):
        super().__init__(SpecialistOverride, db)

    def find_by_recommendation(self, recommendation_id: str):
        return (
            self.db.query(SpecialistOverride)
            .filter(SpecialistOverride.recommendation_id == recommendation_id)
            .order_by(SpecialistOverride.created_at.desc())
            .all()
        )

    def find_by_case(self, case_id: str):
        return (
            self.db.query(SpecialistOverride)
            .filter(SpecialistOverride.case_id == case_id)
            .order_by(SpecialistOverride.created_at.desc())
            .all()
        )


class SpecialistOverrideService(BaseService[SpecialistOverride, SpecialistOverrideRepository]):
    def __init__(self, db: Session):
        super().__init__(SpecialistOverrideRepository(db), db)

    def create_override(
        self,
        *,
        recommendation_id: str,
        case_id: str,
        specialist_id: str,
        action: str,
        reason: str,
        notes: Optional[str] = None,
    ) -> SpecialistOverride:
        action = (action or "").strip().upper()
        if action not in {"ACCEPT", "REJECT", "MODIFY_SELECTION"}:
            raise ValueError(f"Invalid override action: {action}")
        if not reason or not reason.strip():
            raise ValueError("Override reason is required for traceability")

        rec = self.db.get(Recommendation, recommendation_id)
        if rec is None:
            raise ValueError(f"Recommendation not found: {recommendation_id}")
        if rec.case_id != case_id:
            raise ValueError("Recommendation does not belong to the given case")

        override = SpecialistOverride(
            override_id=f"ovr_{uuid4().hex[:16]}",
            recommendation_id=recommendation_id,
            case_id=case_id,
            specialist_id=specialist_id,
            action=action,
            reason=reason.strip(),
            original_eligibility=rec.eligibility_status,
            original_ranking_score=str(rec.ranking_score) if rec.ranking_score is not None else None,
            notes=notes,
        )
        self.db.add(override)
        self.db.flush()

        # Pointer only on Case — does not alter Recommendation engine output
        case = self.db.get(Case, case_id)
        if case is not None:
            case.operator_override = override.override_id
            self.db.flush()

        return override

    def list_by_case(self, case_id: str):
        return self.repository.find_by_case(case_id)

    def list_by_recommendation(self, recommendation_id: str):
        return self.repository.find_by_recommendation(recommendation_id)
