from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_customer_id
from app.services.return_service import ReturnService

router = APIRouter()


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


class ReturnCreateRequest(BaseModel):
    sale_id: str
    product_id: str
    quantity: int = Field(..., gt=0)
    fx_rate_usd_to_irr: Optional[float] = Field(
        None, gt=0, description="Optional if Sale already has FX snapshot"
    )
    reason: Optional[str] = None


@router.post("/")
async def create_return(
    body: ReturnCreateRequest,
    db: Session = Depends(get_db),
    _auth: str = Depends(get_current_customer_id),
):
    svc = ReturnService(db)
    try:
        ret = svc.create_return(
            sale_id=body.sale_id,
            product_id=body.product_id,
            quantity=body.quantity,
            fx_rate_usd_to_irr=body.fx_rate_usd_to_irr,
            reason=body.reason,
        )
        db.commit()
        db.refresh(ret)
        return _to_dict(ret)
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/sale/{sale_id}")
async def list_returns_for_sale(
    sale_id: str,
    db: Session = Depends(get_db),
    _auth: str = Depends(get_current_customer_id),
):
    svc = ReturnService(db)
    return [_to_dict(r) for r in svc.list_by_sale(sale_id)]
