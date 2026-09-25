from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.case import Case
from app.models.feedback import Feedback
from app.models.follow_up import FollowUp
from app.models.recommendation import Recommendation


SCHEDULED = "SCHEDULED"
COMPLETED = "COMPLETED"
CANCELLED = "CANCELLED"
TERMINAL_STATES = {COMPLETED, CANCELLED}


class FollowUpStateError(ValueError):
    pass


class FollowUpService:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        *,
        case_id: str,
        recommendation_id: str | None,
        feedback_id: str | None,
        scheduled_at: datetime,
        actor_id: str,
    ) -> FollowUp:
        if scheduled_at is None:
            raise ValueError("scheduled_at is required")
        case = self.db.get(Case, case_id)
        if case is None:
            raise ValueError(f"Case not found: {case_id}")
        self._validate_trace(case_id, recommendation_id, feedback_id)
        follow_up = FollowUp(
            follow_up_id=f"fu_{uuid4().hex[:16]}",
            case_id=case_id,
            recommendation_id=recommendation_id,
            feedback_id=feedback_id,
            scheduled_at=scheduled_at,
            status=SCHEDULED,
            created_by=actor_id,
            updated_by=actor_id,
        )
        self.db.add(follow_up)
        self.db.flush()
        return follow_up

    def list_by_case(self, case_id: str):
        return (
            self.db.query(FollowUp)
            .filter(FollowUp.case_id == case_id)
            .order_by(FollowUp.scheduled_at.asc(), FollowUp.created_at.desc())
            .all()
        )

    def get_owned(self, follow_up_id: str, case_id: str) -> FollowUp:
        follow_up = self.db.get(FollowUp, follow_up_id)
        if follow_up is None:
            raise ValueError(f"Follow-up not found: {follow_up_id}")
        if follow_up.case_id != case_id:
            raise PermissionError("Access denied")
        return follow_up

    def reschedule(self, follow_up: FollowUp, scheduled_at: datetime, actor_id: str) -> FollowUp:
        self._assert_active(follow_up)
        if scheduled_at is None:
            raise ValueError("scheduled_at is required")
        follow_up.scheduled_at = scheduled_at
        follow_up.updated_by = actor_id
        follow_up.updated_at = datetime.now(timezone.utc)
        self.db.flush()
        return follow_up

    def complete(self, follow_up: FollowUp, actor_id: str) -> FollowUp:
        self._assert_active(follow_up)
        now = datetime.now(timezone.utc)
        follow_up.status = COMPLETED
        follow_up.completed_at = now
        follow_up.updated_at = now
        follow_up.updated_by = actor_id
        self.db.flush()
        return follow_up

    def cancel(self, follow_up: FollowUp, actor_id: str) -> FollowUp:
        self._assert_active(follow_up)
        now = datetime.now(timezone.utc)
        follow_up.status = CANCELLED
        follow_up.cancelled_at = now
        follow_up.updated_at = now
        follow_up.updated_by = actor_id
        self.db.flush()
        return follow_up

    def _assert_active(self, follow_up: FollowUp) -> None:
        if follow_up.status != SCHEDULED:
            raise FollowUpStateError(
                f"Follow-up is terminal and cannot be mutated: {follow_up.status}"
            )

    def _validate_trace(
        self, case_id: str, recommendation_id: str | None, feedback_id: str | None
    ) -> None:
        if recommendation_id:
            recommendation = self.db.get(Recommendation, recommendation_id)
            if recommendation is None:
                raise ValueError(f"Recommendation not found: {recommendation_id}")
            if recommendation.case_id != case_id:
                raise ValueError("Recommendation does not belong to the given case")
        if feedback_id:
            feedback = self.db.get(Feedback, feedback_id)
            if feedback is None:
                raise ValueError(f"Feedback not found: {feedback_id}")
            if feedback.case_id != case_id:
                raise ValueError("Feedback does not belong to the given case")
