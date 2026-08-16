from typing import List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_customer_id
from app.interface.facades import SaleFacade


router = APIRouter()


class SaleCreateRequest(BaseModel):
    customer_id: str
    items: List[Dict[str, Any]]


def _to_dict(obj):
    return vars(obj) if hasattr(obj, "__dict__") else obj


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

    return _to_dict(
        facade.create_sale(
            customer_id=customer_id,
            items=data.items,
        )
    )


@router.get("/total")
async def get_total_sales(
    db: Session = Depends(get_db),
    customer_id: str = Depends(get_current_customer_id),
):
    facade = SaleFacade(db)
    return {"total_sales": facade.get_total_sales()}