from datetime import datetime
from typing import List, Dict, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_customer_id
from app.core.authorization import require_any_role
from app.models.user_role import ROLE_ADMIN
from app.core.authorization import get_current_subject_and_roles, is_gallery_operator_or_admin
from app.interface.facades import SaleFacade
from app.interface.errors import BusinessRuleError


router = APIRouter()


class SaleCreateRequest(BaseModel):
    customer_id: str
    items: List[Dict[str, Any]]
    fx_rate_usd_to_irr: float = Field(..., gt=0, description="IRR per 1 USD; required, never invented")
    idempotency_key: Optional[str] = Field(None, description="Optional durable sale idempotency key")


def _to_dict(obj):
    if obj is None:
        return None
    if hasattr(obj, "__dict__"):
        data = {k: v for k, v in vars(obj).items() if not k.startswith("_")}
        for key, val in list(data.items()):
            if isinstance(val, datetime):
                data[key] = val.isoformat()
        return data
    return obj


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_sale(
    data: SaleCreateRequest,
    db: Session = Depends(get_db),
    admin=Depends(require_any_role(ROLE_ADMIN)),
):
    # V1 PO Contract: ADMIN owns financial mutations; body.customer_id is the buyer.
    facade = SaleFacade(db)
    try:
        sale = facade.create_sale(
            customer_id=data.customer_id,
            items=data.items,
            fx_rate_usd_to_irr=data.fx_rate_usd_to_irr,
            idempotency_key=data.idempotency_key,
        )
        db.commit()
        return _to_dict(sale)
    except (ValueError, BusinessRuleError) as e:
        db.rollback()
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/total")
async def get_total_sales(
    target_customer_id: Optional[str] = None,
    db: Session = Depends(get_db),
    subject_and_roles: tuple = Depends(get_current_subject_and_roles),
):
    subject_id, roles = subject_and_roles
    target_id = target_customer_id or subject_id
    if target_id != subject_id and not is_gallery_operator_or_admin(roles):
        raise HTTPException(status_code=403, detail="Access denied")
    facade = SaleFacade(db)
    return {"total_sales": facade.get_total_sales(target_id)}


@router.get("/customer/{target_customer_id}")
async def list_customer_purchase_history(
    target_customer_id: str,
    db: Session = Depends(get_db),
    subject_and_roles: tuple = Depends(get_current_subject_and_roles),
):
    """Return own history, or selected-customer history to an authorized gallery operator/admin."""
    subject_id, roles = subject_and_roles
    if target_customer_id != subject_id and not is_gallery_operator_or_admin(roles):
        raise HTTPException(status_code=403, detail="Access denied")
    sales = SaleFacade(db).list_by_customer(target_customer_id)
    return [
        {
            "sale_id": s.sale_id,
            "customer_id": s.customer_id,
            "total_amount_toman": s.total_amount_toman,
            "items": [
                {
                    "sale_item_id": it.sale_item_id,
                    "sale_id": it.sale_id,
                    "product_id": it.product_id,
                    "recommendation_id": it.recommendation_id,
                    "quantity": it.quantity,
                    "unit_price_toman": it.unit_price_toman,
                }
                for it in (s.items or [])
            ],
        }
        for s in sales
    ]
