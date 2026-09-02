from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_customer_id
from app.services.operational_fx_service import OperationalFxService

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


class FxSetRequest(BaseModel):
    fx_rate_usd_to_irr: float = Field(..., gt=0)
    note: Optional[str] = None


@router.get("/current")
async def get_current_fx(db: Session = Depends(get_db)):
    svc = OperationalFxService(db)
    row = svc.get_current()
    if not row:
        return {"fx_rate_usd_to_irr": None, "source": None}
    return {"fx_rate_usd_to_irr": row.fx_rate_usd_to_irr, "source": _to_dict(row)}


@router.post("/operational")
async def set_operational_fx(
    body: FxSetRequest,
    db: Session = Depends(get_db),
    _auth: str = Depends(get_current_customer_id),
):
    svc = OperationalFxService(db)
    try:
        row = svc.set_rate(body.fx_rate_usd_to_irr, note=body.note)
        db.commit()
        db.refresh(row)
        return _to_dict(row)
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=422, detail=str(e))
