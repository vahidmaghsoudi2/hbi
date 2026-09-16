"""Feedback Service — Mission B.

Records feedback / follow-up linked to Case and optional Recommendation.
No learning, no weight updates (Issue #37 remains OPEN).
"""
from typing import Optional
from datetime import datetime
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.feedback import Feedback
from app.models.case import Case
from app.models.recommendation import Recommendation
from app.services.base import BaseService
from app.repositories.base import BaseRepository


class FeedbackRepository(BaseRepository[Feedback]):
    def __init__(self, db: Session):
        super().__init__(Feedback, db)

    def find_by_case(self, case_id: str):
        return (
            self.db.query(Feedback)
            .filter(Feedback.case_id == case_id)
            .order_by(Feedback.created_at.desc())
            .all()
        )


class FeedbackService(BaseService[Feedback, FeedbackRepository]):
    def __init__(self, db: Session):
        super().__init__(FeedbackRepository(db), db)

    def create_feedback(
        self,
        *,
        case_id: str,
        source: str,
        outcome: Optional[str] = None,
        rating: Optional[str] = None,
        comment: Optional[str] = None,
        recommendation_id: Optional[str] = None,
        follow_up_at: Optional[datetime] = None,
    ) -> Feedback:
        source = (source or "").strip().upper()
        if source not in {"CUSTOMER", "SPECIALIST", "SYSTEM"}:
            raise ValueError(f"Invalid feedback source: {source}")

        case = self.db.get(Case, case_id)
        if case is None:
            raise ValueError(f"Case not found: {case_id}")

        if recommendation_id:
            rec = self.db.get(Recommendation, recommendation_id)
            if rec is None:
                raise ValueError(f"Recommendation not found: {recommendation_id}")
            if rec.case_id != case_id:
                raise ValueError("Recommendation does not belong to the given case")

        fb = Feedback(
            feedback_id=f"fb_{uuid4().hex[:16]}",
            case_id=case_id,
            recommendation_id=recommendation_id,
            source=source,
            outcome=(outcome or "").strip().upper() or None,
            rating=rating,
            comment=comment,
            follow_up_at=follow_up_at,
        )
        self.db.add(fb)
        self.db.flush()
        return fb

    def list_by_case(self, case_id: str):
        return self.repository.find_by_case(case_id)
