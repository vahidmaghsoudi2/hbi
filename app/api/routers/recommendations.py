from typing import Dict, Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_customer_id
from app.interface.facades import RecommendationFacade
from app.models.case import Case
from app.models.customer import Customer
from app.services.customer_service import CustomerService
from app.interface.errors import NotFoundError, BusinessRuleError


router = APIRouter()


class RecommendationRequest(BaseModel):
    case_id: str
    customer_profile: Dict[str, Any] = {}


def _to_dict(obj) -> dict:
    if hasattr(obj, "__dict__"):
        return {k: v for k, v in vars(obj).items() if not k.startswith("_")}
    return dict(obj) if obj else {}


def _merge_profile_context(saved: Dict[str, Any], current: Dict[str, Any]) -> Dict[str, Any]:
    """Combine persistent customer context with the current consultation."""
    merged: Dict[str, Any] = dict(saved or {})
    current = current or {}

    def combine(*values: Any) -> str:
        parts: List[str] = []
        seen = set()
        for value in values:
            if value is None:
                continue
            raw = value if isinstance(value, list) else str(value).split(",")
            for item in raw:
                item = str(item).strip()
                if item and item not in seen:
                    seen.add(item)
                    parts.append(item)
        return ", ".join(parts)

    for key, value in current.items():
        if value is None or value == "":
            continue
        if key in {"concerns", "skin_profile", "skin_type", "hair_profile", "scalp_profile"}:
            merged[key] = combine(merged.get(key), value)
        else:
            merged[key] = value

    # RecommendationService consumes "concerns". Surface persisted profile
    # dimensions there without changing the scoring formula itself.
    recommendation_parts = [merged.get("concerns")]
    for key, prefix in (
        ("skin_profile", "پوست"),
        ("skin_type", "پوست"),
    ):
        if merged.get(key):
            recommendation_parts.append(", ".join(
                f"{prefix} {x.strip()}" for x in str(merged[key]).split(",") if x.strip()
            ))
    for key in ("hair_profile", "scalp_profile"):
        if merged.get(key):
            recommendation_parts.append(str(merged[key]))
    merged["concerns"] = combine(*recommendation_parts)
    return merged


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
    case = _assert_case_owned(db, request.case_id, customer_id)
    customer = db.get(Customer, case.customer_id)
    saved_profile = CustomerService(db).build_recommendation_profile(customer)
    merged_profile = _merge_profile_context(saved_profile, request.customer_profile)
    facade = RecommendationFacade(db)
    try:
        dtos = facade.generate(request.case_id, merged_profile)
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
