from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_customer_id
from app.interface.facades import CaseFacade
from app.interface.errors import NotFoundError
from app.models.case import Case


router = APIRouter()


class CaseCreateRequest(BaseModel):
    customer_id: str
    case_type: str = "OPEN"


def _to_dict(obj):
    return vars(obj) if hasattr(obj, "__dict__") else obj


def _assert_case_owned(db: Session, case_id: str, customer_id: str) -> Case:
    """Load case and enforce ownership. 404 if missing, 403 if not owner."""
    case = db.get(Case, case_id)
    if case is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found",
        )
    if case.customer_id != customer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    return case


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
    """Close a case. Auth required; only the owning customer may close."""
    _assert_case_owned(db, case_id, customer_id)
    facade = CaseFacade(db)
    try:
        case = facade.close(case_id)
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found",
        )
    return _to_dict(case)
