"""Specialist Override & Feedback API — Mission B.

- Override creates an audit record; never mutates Recommendation.
- Feedback is linked to Case (and optional Recommendation).
- Case ownership enforced via customer_id from auth.
"""
from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_customer_id
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
    specialist_id: str
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
    svc = SpecialistOverrideService(db)
    try:
        ovr = svc.create_override(
            recommendation_id=body.recommendation_id,
            case_id=body.case_id,
            specialist_id=body.specialist_id,
            action=body.action,
            reason=body.reason,
            notes=body.notes,
        )
        db.commit()
    except ValueError as e:
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
    except ValueError as e:
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
