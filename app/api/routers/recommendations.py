from typing import Dict, Any, List, Optional as Opt

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_customer_id
from app.interface.facades import RecommendationFacade
from app.models.case import Case
from app.interface.errors import NotFoundError, BusinessRuleError
from app.services.recommendation_outcome_service import RecommendationOutcomeService


router = APIRouter()


class RecommendationRequest(BaseModel):
    case_id: str
    customer_profile: Dict[str, Any] = {}


def _to_dict(obj) -> dict:
    if hasattr(obj, "__dict__"):
        return {k: v for k, v in vars(obj).items() if not k.startswith("_")}
    return dict(obj) if obj else {}


def _assert_case_owned(db: Session, case_id: str, customer_id: str) -> Case:
    case = db.get(Case, case_id)
    if case is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    if case.customer_id != customer_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return case


@router.post("/generate")
async def generate_recommendations(
    request: RecommendationRequest,
    db: Session = Depends(get_db),
    customer_id: str = Depends(get_current_customer_id),
) -> List[dict]:
    _assert_case_owned(db, request.case_id, customer_id)
    facade = RecommendationFacade(db)
    try:
        dtos = facade.generate(request.case_id, request.customer_profile)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BusinessRuleError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    # availability/price already on RecommendationDTO (request-scoped db)
    return [_to_dict(d) for d in dtos]


@router.get("/case/{case_id}")
async def get_recommendations_by_case(
    case_id: str,
    db: Session = Depends(get_db),
    customer_id: str = Depends(get_current_customer_id),
) -> List[dict]:
    _assert_case_owned(db, case_id, customer_id)
    facade = RecommendationFacade(db)
    return [_to_dict(d) for d in facade.find_by_case(case_id)]


# --- Mission B: gallery, specialist override, outcome / follow-up ---


class OutcomeRequest(BaseModel):
    case_id: str
    product_id: str
    outcome_type: str
    recommendation_id: Opt[str] = None
    notes: Opt[str] = None
    follow_up_notes: Opt[str] = None
    follow_up_status: Opt[str] = None


class OverrideRequest(BaseModel):
    case_id: str
    reason: str
    override_action: str = Field(..., description="e.g. ACCEPT_ALTERNATIVE, REJECT_ALL, FORCE_REVIEW")
    product_id: Opt[str] = None


def _outcome_to_dict(row) -> dict:
    return {
        "outcome_id": row.outcome_id,
        "case_id": row.case_id,
        "product_id": row.product_id,
        "recommendation_id": row.recommendation_id,
        "outcome_type": row.outcome_type,
        "actor_id": row.actor_id,
        "notes": row.notes,
        "follow_up_notes": row.follow_up_notes,
        "follow_up_status": row.follow_up_status,
        "created_at": row.created_at.isoformat() if row.created_at else None,
    }


@router.get("/gallery/{case_id}")
async def recommendation_gallery(
    case_id: str,
    db: Session = Depends(get_db),
    customer_id: str = Depends(get_current_customer_id),
) -> List[dict]:
    """Front-door gallery: current recommendations for a case (Mission B)."""
    _assert_case_owned(db, case_id, customer_id)
    svc = RecommendationOutcomeService(db)
    return svc.gallery_for_case(case_id)


@router.post("/outcomes")
async def record_recommendation_outcome(
    request: OutcomeRequest,
    db: Session = Depends(get_db),
    customer_id: str = Depends(get_current_customer_id),
) -> dict:
    """Record recommendation outcome / feedback. Does not alter scoring or Need maps."""
    _assert_case_owned(db, request.case_id, customer_id)
    svc = RecommendationOutcomeService(db)
    try:
        row = svc.record_outcome(
            case_id=request.case_id,
            product_id=request.product_id,
            outcome_type=request.outcome_type,
            actor_id=customer_id,
            recommendation_id=request.recommendation_id,
            notes=request.notes,
            follow_up_notes=request.follow_up_notes,
            follow_up_status=request.follow_up_status,
        )
        db.commit()
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    return _outcome_to_dict(row)


@router.get("/outcomes/case/{case_id}")
async def list_outcomes_for_case(
    case_id: str,
    db: Session = Depends(get_db),
    customer_id: str = Depends(get_current_customer_id),
) -> List[dict]:
    _assert_case_owned(db, case_id, customer_id)
    svc = RecommendationOutcomeService(db)
    return [_outcome_to_dict(r) for r in svc.list_by_case(case_id)]


@router.post("/override")
async def specialist_override(
    request: OverrideRequest,
    db: Session = Depends(get_db),
    customer_id: str = Depends(get_current_customer_id),
) -> dict:
    """Auditable specialist override on Case.operator_override (Mission B)."""
    _assert_case_owned(db, request.case_id, customer_id)
    if not (request.reason or "").strip():
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="reason is required")
    svc = RecommendationOutcomeService(db)
    try:
        case = svc.apply_specialist_override(
            case_id=request.case_id,
            actor_id=customer_id,
            reason=request.reason,
            override_action=request.override_action,
            product_id=request.product_id,
        )
        db.commit()
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return {
        "case_id": case.case_id,
        "operator_override": case.operator_override,
    }
