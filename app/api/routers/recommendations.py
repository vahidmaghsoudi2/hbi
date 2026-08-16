from typing import Dict, Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_customer_id
from app.interface.facades import RecommendationFacade, InventoryFacade


router = APIRouter()


class RecommendationRequest(BaseModel):
    case_id: str
    customer_profile: Dict[str, Any] = {}


def _to_dict(obj):
    return vars(obj) if hasattr(obj, "__dict__") else obj


@router.post("/generate")
async def generate_recommendations(
    request: RecommendationRequest,
    db: Session = Depends(get_db),
    customer_id: str = Depends(get_current_customer_id),
):
    rec_facade = RecommendationFacade(db)
    inv_facade = InventoryFacade(db)

    dtos = rec_facade.generate(
        request.case_id,
        request.customer_profile,
    )

    responses = []

    for dto in dtos:
        item = _to_dict(dto)

        if not isinstance(item, dict):
            item = dict(item) if item else {}

        inventory = inv_facade.get_by_product(
            item.get("product_id", "")
        )

        if inventory:
            item["availability"] = getattr(
                inventory,
                "availability",
                None,
            )
            item["price"] = getattr(
                inventory,
                "sale_price_toman",
                None,
            )
        else:
            item["availability"] = None
            item["price"] = None

        responses.append(item)

    return responses


@router.get("/case/{case_id}")
async def get_recommendations_by_case(
    case_id: str,
    db: Session = Depends(get_db),
    customer_id: str = Depends(get_current_customer_id),
):
    facade = RecommendationFacade(db)

    return [
        _to_dict(d)
        for d in facade.find_by_case(case_id)
    ]