from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_customer_id
from app.core.authorization import require_any_role
from app.models.user_role import ROLE_ADMIN
from app.services.return_service import ReturnService
from app.models.sale import Sale

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
    admin=Depends(require_any_role(ROLE_ADMIN)),
):
    # V1 PO Contract: ADMIN owns return financial mutation.
    sale = db.query(Sale).filter(Sale.sale_id == body.sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail=f"Sale {body.sale_id} not found")
    if getattr(sale, "document_status", "ACTIVE") == "VOIDED":
        raise HTTPException(status_code=422, detail=f"Sale {body.sale_id} is VOIDED")
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
    admin=Depends(require_any_role(ROLE_ADMIN)),
):
    sale = db.query(Sale).filter(Sale.sale_id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail=f"Sale {sale_id} not found")
    svc = ReturnService(db)
    return [_to_dict(r) for r in svc.list_by_sale(sale_id)]
