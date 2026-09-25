from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.audit import audit_event
from app.core.deps import get_current_customer_id, get_db
from app.models.case import Case
from app.services.follow_up_service import FollowUpService, FollowUpStateError

router = APIRouter()


def _assert_case_owned(db: Session, case_id: str, customer_id: str) -> Case:
    case = db.get(Case, case_id)
    if case is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    if case.customer_id != customer_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return case


class FollowUpCreateRequest(BaseModel):
    case_id: str
    recommendation_id: Optional[str] = None
    feedback_id: Optional[str] = None
    scheduled_at: datetime


class FollowUpRescheduleRequest(BaseModel):
    scheduled_at: datetime


def _to_dict(follow_up) -> dict:
    return {
        "follow_up_id": follow_up.follow_up_id,
        "case_id": follow_up.case_id,
        "recommendation_id": follow_up.recommendation_id,
        "feedback_id": follow_up.feedback_id,
        "scheduled_at": follow_up.scheduled_at.isoformat() if follow_up.scheduled_at else None,
        "status": follow_up.status,
        "created_at": follow_up.created_at.isoformat() if follow_up.created_at else None,
        "created_by": follow_up.created_by,
        "updated_at": follow_up.updated_at.isoformat() if follow_up.updated_at else None,
        "updated_by": follow_up.updated_by,
        "completed_at": follow_up.completed_at.isoformat() if follow_up.completed_at else None,
        "cancelled_at": follow_up.cancelled_at.isoformat() if follow_up.cancelled_at else None,
    }


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_follow_up(
    body: FollowUpCreateRequest,
    db: Session = Depends(get_db),
    customer_id: str = Depends(get_current_customer_id),
) -> dict:
    _assert_case_owned(db, body.case_id, customer_id)
    svc = FollowUpService(db)
    try:
        follow_up = svc.create(
            case_id=body.case_id,
            recommendation_id=body.recommendation_id,
            feedback_id=body.feedback_id,
            scheduled_at=body.scheduled_at,
            actor_id=customer_id,
        )
        db.commit()
        audit_event(
            "follow_up_created",
            customer_id=customer_id,
            path="/api/v1/followups",
            detail=follow_up.follow_up_id,
            extra={
                "target": {"case_id": body.case_id, "follow_up_id": follow_up.follow_up_id},
                "recommendation_id": body.recommendation_id,
                "feedback_id": body.feedback_id,
                "scheduled_at": body.scheduled_at.isoformat(),
                "status": follow_up.status,
                "actor": customer_id,
            },
        )
    except ValueError as exc:
        audit_event(
            "follow_up_create_rejected",
            customer_id=customer_id,
            path="/api/v1/followups",
            outcome="error",
            detail=str(exc),
            extra={"target": {"case_id": body.case_id}, "actor": customer_id},
        )
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    return _to_dict(follow_up)


@router.get("/case/{case_id}")
async def list_follow_ups(
    case_id: str,
    db: Session = Depends(get_db),
    customer_id: str = Depends(get_current_customer_id),
) -> List[dict]:
    _assert_case_owned(db, case_id, customer_id)
    return [_to_dict(item) for item in FollowUpService(db).list_by_case(case_id)]


@router.patch("/{follow_up_id}")
async def reschedule_follow_up(
    follow_up_id: str,
    body: FollowUpRescheduleRequest,
    case_id: str,
    db: Session = Depends(get_db),
    customer_id: str = Depends(get_current_customer_id),
) -> dict:
    _assert_case_owned(db, case_id, customer_id)
    svc = FollowUpService(db)
    try:
        follow_up = svc.get_owned(follow_up_id, case_id)
        follow_up = svc.reschedule(follow_up, body.scheduled_at, customer_id)
        db.commit()
        audit_event(
            "follow_up_rescheduled",
            customer_id=customer_id,
            path=f"/api/v1/followups/{follow_up_id}",
            detail=follow_up_id,
            extra={"target": {"case_id": case_id, "follow_up_id": follow_up_id}, "scheduled_at": body.scheduled_at.isoformat(), "actor": customer_id},
        )
        return _to_dict(follow_up)
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    except FollowUpStateError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    except ValueError as exc:
        if str(exc).startswith("Follow-up not found"):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))


@router.post("/{follow_up_id}/complete")
async def complete_follow_up(
    follow_up_id: str,
    case_id: str,
    db: Session = Depends(get_db),
    customer_id: str = Depends(get_current_customer_id),
) -> dict:
    _assert_case_owned(db, case_id, customer_id)
    svc = FollowUpService(db)
    try:
        follow_up = svc.complete(svc.get_owned(follow_up_id, case_id), customer_id)
        db.commit()
        audit_event("follow_up_completed", customer_id=customer_id, path=f"/api/v1/followups/{follow_up_id}/complete", detail=follow_up_id, extra={"target": {"case_id": case_id, "follow_up_id": follow_up_id}, "actor": customer_id, "status": follow_up.status})
        return _to_dict(follow_up)
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    except FollowUpStateError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.post("/{follow_up_id}/cancel")
async def cancel_follow_up(
    follow_up_id: str,
    case_id: str,
    db: Session = Depends(get_db),
    customer_id: str = Depends(get_current_customer_id),
) -> dict:
    _assert_case_owned(db, case_id, customer_id)
    svc = FollowUpService(db)
    try:
        follow_up = svc.cancel(svc.get_owned(follow_up_id, case_id), customer_id)
        db.commit()
        audit_event("follow_up_cancelled", customer_id=customer_id, path=f"/api/v1/followups/{follow_up_id}/cancel", detail=follow_up_id, extra={"target": {"case_id": case_id, "follow_up_id": follow_up_id}, "actor": customer_id, "status": follow_up.status})
        return _to_dict(follow_up)
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    except FollowUpStateError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
