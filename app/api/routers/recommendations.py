from typing import Dict, Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_customer_id
from app.interface.facades import RecommendationFacade
from app.models.case import Case
from app.interface.errors import NotFoundError, BusinessRuleError


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
