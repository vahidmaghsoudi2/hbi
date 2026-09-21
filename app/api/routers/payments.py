from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_customer_id
from app.services.payment_service import PaymentService

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


class PaymentCreateRequest(BaseModel):
    sale_id: str
    method: str = Field(..., description="CASH | CARD | TRANSFER | OTHER")
    amount_usd: float = Field(..., gt=0)
    fx_rate_usd_to_irr: float = Field(..., gt=0)
    note: Optional[str] = None


@router.post("/")
async def record_payment(
    body: PaymentCreateRequest,
    db: Session = Depends(get_db),
    customer_id: str = Depends(get_current_customer_id),
):
    svc = PaymentService(db)
    try:
        payment = svc.record_payment(
            sale_id=body.sale_id,
            customer_id=customer_id,
            method=body.method,
            amount_usd=body.amount_usd,
            fx_rate_usd_to_irr=body.fx_rate_usd_to_irr,
            note=body.note,
        )
        db.commit()
        db.refresh(payment)
        return _to_dict(payment)
    except PermissionError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        db.rollback()
        status_code = 404 if str(e).startswith("Sale ") and str(e).endswith(" not found") else 422
        raise HTTPException(status_code=status_code, detail=str(e))


@router.get("/sale/{sale_id}")
async def list_payments_for_sale(
    sale_id: str,
    db: Session = Depends(get_db),
    customer_id: str = Depends(get_current_customer_id),
):
    svc = PaymentService(db)
    try:
        return [_to_dict(p) for p in svc.list_by_sale(sale_id, customer_id=customer_id)]
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{payment_id}")
async def get_payment(
    payment_id: str,
    db: Session = Depends(get_db),
    customer_id: str = Depends(get_current_customer_id),
):
    svc = PaymentService(db)
    try:
        payment = svc.get_by_id(payment_id, customer_id=customer_id)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    if not payment:
        raise HTTPException(status_code=404, detail=f"Payment {payment_id} not found")
    return _to_dict(payment)
