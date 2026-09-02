from datetime import datetime
from typing import List, Dict, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_customer_id
from app.interface.facades import SaleFacade
from app.interface.errors import BusinessRuleError


router = APIRouter()


class SaleCreateRequest(BaseModel):
    customer_id: str
    items: List[Dict[str, Any]]
    fx_rate_usd_to_irr: float = Field(..., gt=0, description="IRR per 1 USD; required, never invented")


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
    customer_id: str = Depends(get_current_customer_id),
):
    if data.customer_id != customer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    facade = SaleFacade(db)
    try:
        sale = facade.create_sale(
            customer_id=customer_id,
            items=data.items,
            fx_rate_usd_to_irr=data.fx_rate_usd_to_irr,
        )
        db.commit()
        return _to_dict(sale)
    except (ValueError, BusinessRuleError) as e:
        db.rollback()
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/total")
async def get_total_sales(
    db: Session = Depends(get_db),
    customer_id: str = Depends(get_current_customer_id),
):
    facade = SaleFacade(db)
    return {"total_sales": facade.get_total_sales()}
