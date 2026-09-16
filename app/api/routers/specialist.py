"""Specialist Override & Feedback API — Mission B.

- Override creates an audit record; never mutates Recommendation.
- specialist_id is ALWAYS the authenticated identity (not client-supplied).
- Audit trail: operator → target → previous_state → new_state → reason → timestamp.
- Case ownership enforced via customer_id from auth.
"""
from typing import Optional, List
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_customer_id
from app.core.audit import audit_event
from app.models.case import Case
from app.services.specialist_override_service import SpecialistOverrideService
from app.services.feedback_service import FeedbackService

router = APIRouter()


def _assert_case_owned(db: Session, case_id: str, customer_id: str) -> Case:
    case = db.get(Case, case_id)
    if case is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    if case.customer_id != customer_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return case


class OverrideRequest(BaseModel):
    recommendation_id: str
    case_id: str
    # specialist_id is NOT accepted from client — derived from authenticated identity only
    action: str = Field(..., description="ACCEPT | REJECT | MODIFY_SELECTION")
    reason: str
    notes: Optional[str] = None


class FeedbackRequest(BaseModel):
    case_id: str
    source: str = Field(..., description="CUSTOMER | SPECIALIST | SYSTEM")
    outcome: Optional[str] = None
    rating: Optional[str] = None
    comment: Optional[str] = None
    recommendation_id: Optional[str] = None
    follow_up_at: Optional[datetime] = None


def _override_to_dict(o) -> dict:
    return {
        "override_id": o.override_id,
        "recommendation_id": o.recommendation_id,
        "case_id": o.case_id,
        "specialist_id": o.specialist_id,
        "action": o.action,
        "reason": o.reason,
        "original_eligibility": o.original_eligibility,
        "original_ranking_score": o.original_ranking_score,
        "notes": o.notes,
        "created_at": o.created_at.isoformat() if o.created_at else None,
    }


def _feedback_to_dict(f) -> dict:
    return {
        "feedback_id": f.feedback_id,
        "case_id": f.case_id,
        "recommendation_id": f.recommendation_id,
        "source": f.source,
        "outcome": f.outcome,
        "rating": f.rating,
        "comment": f.comment,
        "follow_up_at": f.follow_up_at.isoformat() if f.follow_up_at else None,
        "created_at": f.created_at.isoformat() if f.created_at else None,
    }


@router.post("/overrides")
async def create_override(
    body: OverrideRequest,
    db: Session = Depends(get_db),
    customer_id: str = Depends(get_current_customer_id),
) -> dict:
    _assert_case_owned(db, body.case_id, customer_id)
    # Operator identity ONLY from authenticated token — never from request body
    operator_id = customer_id
    svc = SpecialistOverrideService(db)
    try:
        ovr = svc.create_override(
            recommendation_id=body.recommendation_id,
            case_id=body.case_id,
            specialist_id=operator_id,
            action=body.action,
            reason=body.reason,
            notes=body.notes,
        )
        db.commit()
        # Full audit trail per Specialist Override contract
        audit_event(
            "specialist_override_created",
            customer_id=operator_id,
            path="/api/v1/specialist/overrides",
            outcome="ok",
            detail=ovr.override_id,
            extra={
                "operator": operator_id,
                "target": {
                    "recommendation_id": body.recommendation_id,
                    "case_id": body.case_id,
                },
                "previous_state": {
                    "eligibility": ovr.original_eligibility,
                    "ranking_score": ovr.original_ranking_score,
                },
                "new_state": {
                    "action": ovr.action,
                    "override_id": ovr.override_id,
                    # Recommendation row itself is unchanged; new_state is the override decision
                    "recommendation_mutated": False,
                },
                "reason": ovr.reason,
                "timestamp": (
                    ovr.created_at.isoformat()
                    if ovr.created_at
                    else datetime.now(timezone.utc).isoformat()
                ),
            },
        )
    except ValueError as e:
        audit_event(
            "specialist_override_rejected",
            customer_id=operator_id,
            path="/api/v1/specialist/overrides",
            outcome="error",
            detail=str(e),
            extra={
                "operator": operator_id,
                "target": {
                    "recommendation_id": body.recommendation_id,
                    "case_id": body.case_id,
                },
                "reason": body.reason,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    return _override_to_dict(ovr)


@router.get("/overrides/case/{case_id}")
async def list_overrides_for_case(
    case_id: str,
    db: Session = Depends(get_db),
    customer_id: str = Depends(get_current_customer_id),
) -> List[dict]:
    _assert_case_owned(db, case_id, customer_id)
    svc = SpecialistOverrideService(db)
    return [_override_to_dict(o) for o in svc.list_by_case(case_id)]


@router.post("/feedback")
async def create_feedback(
    body: FeedbackRequest,
    db: Session = Depends(get_db),
    customer_id: str = Depends(get_current_customer_id),
) -> dict:
    _assert_case_owned(db, body.case_id, customer_id)
    svc = FeedbackService(db)
    try:
        fb = svc.create_feedback(
            case_id=body.case_id,
            source=body.source,
            outcome=body.outcome,
            rating=body.rating,
            comment=body.comment,
            recommendation_id=body.recommendation_id,
            follow_up_at=body.follow_up_at,
        )
        db.commit()
        audit_event(
            "feedback_created",
            customer_id=customer_id,
            path="/api/v1/specialist/feedback",
            outcome="ok",
            detail=fb.feedback_id,
            extra={
                "operator": customer_id,
                "target": {
                    "case_id": body.case_id,
                    "recommendation_id": body.recommendation_id,
                },
                "new_state": {
                    "source": fb.source,
                    "outcome": fb.outcome,
                    "follow_up_at": (
                        fb.follow_up_at.isoformat() if fb.follow_up_at else None
                    ),
                },
                "reason": fb.comment,
                "timestamp": (
                    fb.created_at.isoformat()
                    if fb.created_at
                    else datetime.now(timezone.utc).isoformat()
                ),
            },
        )
    except ValueError as e:
        audit_event(
            "feedback_rejected",
            customer_id=customer_id,
            path="/api/v1/specialist/feedback",
            outcome="error",
            detail=str(e),
            extra={
                "operator": customer_id,
                "target": {"case_id": body.case_id},
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    return _feedback_to_dict(fb)


@router.get("/feedback/case/{case_id}")
async def list_feedback_for_case(
    case_id: str,
    db: Session = Depends(get_db),
    customer_id: str = Depends(get_current_customer_id),
) -> List[dict]:
    _assert_case_owned(db, case_id, customer_id)
    svc = FeedbackService(db)
    return [_feedback_to_dict(f) for f in svc.list_by_case(case_id)]
