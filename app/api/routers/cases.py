from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_customer_id
from app.interface.facades import CaseFacade


router = APIRouter()


class CaseCreateRequest(BaseModel):
    customer_id: str
    case_type: str = "OPEN"


def _to_dict(obj):
    return vars(obj) if hasattr(obj, "__dict__") else obj


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_case(
    data: CaseCreateRequest,
    db: Session = Depends(get_db),
    customer_id: str = Depends(get_current_customer_id),
):
    if data.customer_id != customer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    facade = CaseFacade(db)
    return _to_dict(
        facade.create(
            customer_id=customer_id,
            case_type=data.case_type,
        )
    )


@router.get("/customer/{customer_id}")
async def get_cases_by_customer(
    customer_id: str,
    db: Session = Depends(get_db),
    current_customer_id: str = Depends(get_current_customer_id),
):
    if customer_id != current_customer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    facade = CaseFacade(db)
    return [
        _to_dict(c)
        for c in facade.find_by_customer(current_customer_id)
    ]


@router.post("/{case_id}/close")
async def close_case(
    case_id: str,
    db: Session = Depends(get_db),
    customer_id: str = Depends(get_current_customer_id),
):
    # Authentication is mandatory here.
    # Ownership by case_id requires a case lookup method that is not
    # currently exposed by the supplied CaseFacade; do not guess schema.
    facade = CaseFacade(db)
    case = facade.close(case_id)

    if not case:
        raise HTTPException(
            status_code=404,
            detail="Case not found",
        )

    return _to_dict(case)