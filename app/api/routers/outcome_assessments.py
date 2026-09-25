from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.audit import audit_event
from app.core.deps import get_current_customer_id, get_db
from app.models.case import Case
from app.services.outcome_assessment_service import OutcomeAssessmentService

router = APIRouter()


def _assert_case_owned(db: Session, case_id: str, customer_id: str) -> Case:
    case = db.get(Case, case_id)
    if case is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    if case.customer_id != customer_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return case


class OutcomeAssessmentCreateRequest(BaseModel):
    case_id: str
    result_state: str
    recommendation_id: Optional[str] = None
    feedback_id: Optional[str] = None
    follow_up_id: Optional[str] = None
    product_id: Optional[str] = None
    observed_at: Optional[datetime] = None


def _to_dict(item) -> dict:
    return {
        "outcome_assessment_id": item.outcome_assessment_id,
        "case_id": item.case_id,
        "recommendation_id": item.recommendation_id,
        "feedback_id": item.feedback_id,
        "follow_up_id": item.follow_up_id,
        "product_id": item.product_id,
        "result_state": item.result_state,
        "provenance": item.provenance,
        "actor_id": item.actor_id,
        "observed_at": item.observed_at.isoformat() if item.observed_at else None,
        "created_at": item.created_at.isoformat() if item.created_at else None,
    }


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_outcome_assessment(
    body: OutcomeAssessmentCreateRequest,
    db: Session = Depends(get_db),
    customer_id: str = Depends(get_current_customer_id),
) -> dict:
    _assert_case_owned(db, body.case_id, customer_id)
    svc = OutcomeAssessmentService(db)
    try:
        assessment = svc.create(
            case_id=body.case_id,
            result_state=body.result_state,
            recommendation_id=body.recommendation_id,
            feedback_id=body.feedback_id,
            follow_up_id=body.follow_up_id,
            product_id=body.product_id,
            provenance="CUSTOMER",
            actor_id=customer_id,
            observed_at=body.observed_at,
        )
        db.commit()
        audit_event(
            "outcome_assessment_created",
            customer_id=customer_id,
            path="/api/v1/outcome-assessments",
            outcome="ok",
            detail=assessment.outcome_assessment_id,
            extra={
                "actor": customer_id,
                "provenance": assessment.provenance,
                "result_state": assessment.result_state,
                "target": {
                    "outcome_assessment_id": assessment.outcome_assessment_id,
                    "case_id": assessment.case_id,
                    "recommendation_id": assessment.recommendation_id,
                    "feedback_id": assessment.feedback_id,
                    "follow_up_id": assessment.follow_up_id,
                    "product_id": assessment.product_id,
                },
                "timestamp": assessment.observed_at.isoformat() if assessment.observed_at else None,
                "mutation_type": "CREATE",
            },
        )
        return _to_dict(assessment)
    except ValueError as exc:
        audit_event(
            "outcome_assessment_rejected",
            customer_id=customer_id,
            path="/api/v1/outcome-assessments",
            outcome="error",
            detail=str(exc),
            extra={
                "actor": customer_id,
                "target": {"case_id": body.case_id},
                "mutation_type": "CREATE",
            },
        )
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))


@router.get("/case/{case_id}")
async def list_outcome_assessments(
    case_id: str,
    recommendation_id: Optional[str] = None,
    db: Session = Depends(get_db),
    customer_id: str = Depends(get_current_customer_id),
) -> List[dict]:
    _assert_case_owned(db, case_id, customer_id)
    return [_to_dict(item) for item in OutcomeAssessmentService(db).list_by_case(case_id, recommendation_id)]


@router.get("/profile-history")
async def list_profile_outcome_assessment_history(
    db: Session = Depends(get_db),
    customer_id: str = Depends(get_current_customer_id),
) -> List[dict]:
    """Customer Profile longitudinal projection of Outcome Assessments.

    Case remains authoritative source of truth. This endpoint aggregates
    Case-owned assessments for the authenticated customer without creating
    ProfileFact records or becoming a second source of truth.
    """
    items = OutcomeAssessmentService(db).list_by_customer(customer_id)
    return [_to_dict(item) for item in items]
