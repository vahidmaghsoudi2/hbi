from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_customer_id
from app.interface.facades import CustomerFacade


router = APIRouter()


class CustomerCreateRequest(BaseModel):
    name: str
    mobile: Optional[str] = None
    consent: int = 0


def _to_dict(obj):
    return vars(obj) if hasattr(obj, "__dict__") else obj


@router.post("/", status_code=status.HTTP_201_CREATED)
async def register_customer(
    data: CustomerCreateRequest,
    db: Session = Depends(get_db),
    customer_id: str = Depends(get_current_customer_id),
):
    if data.mobile and data.mobile != customer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Customer identity mismatch",
        )

    facade = CustomerFacade(db)
    return _to_dict(
        facade.register(
            name=data.name,
            mobile=data.mobile or customer_id,
            consent=data.consent,
        )
    )


@router.get("/mobile/{mobile}")
async def find_customer_by_mobile(
    mobile: str,
    db: Session = Depends(get_db),
    customer_id: str = Depends(get_current_customer_id),
):
    if mobile != customer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    facade = CustomerFacade(db)
    customer = facade.find_by_mobile(mobile)

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found",
        )

    return _to_dict(customer)