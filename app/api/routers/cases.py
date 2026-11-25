from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_customer_id
from app.interface.facades import CaseFacade
from app.services.case_service import CaseService


router = APIRouter()


class CaseCreateRequest(BaseModel):
    customer_id: str
    case_type: str = "OPEN"

class ConsultationContextRequest(BaseModel):
    affected_areas: List[str] = Field(default_factory=list, max_length=20)
    duration: Optional[str] = Field(default=None, max_length=120)
    severity: Optional[int] = Field(default=None, ge=0, le=10)
    aggravating_factors: List[str] = Field(default_factory=list, max_length=30)
    current_products: List[str] = Field(default_factory=list, max_length=50)
    notes: Optional[str] = Field(default=None, max_length=4000)



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


@router.put("/{case_id}/consultation")
async def save_case_consultation(
    case_id: str,
    data: ConsultationContextRequest,
    db: Session = Depends(get_db),
    customer_id: str = Depends(get_current_customer_id),
):
    """Save structured, visit-specific skin consultation data on its Case."""
    service = CaseService(db)
    case = service.repository.get_by_id(case_id)
    if case is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    if case.customer_id != customer_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    context = data.model_dump()
    service.save_consultation_context(case_id, context)
    db.commit()
    return {"case_id": case_id, "consultation_context": context}


@router.get("/{case_id}/consultation")
async def get_case_consultation(
    case_id: str,
    db: Session = Depends(get_db),
    customer_id: str = Depends(get_current_customer_id),
):
    """Read back structured, visit-specific skin consultation data."""
    service = CaseService(db)
    case = service.repository.get_by_id(case_id)
    if case is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    if case.customer_id != customer_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return {"case_id": case_id, "consultation_context": service.get_consultation_context(case_id)}


@router.post("/{case_id}/close")
async def close_case(
    case_id: str,
    db: Session = Depends(get_db),
    customer_id: str = Depends(get_current_customer_id),
):
    # Authentication is mandatory here.
    facade = CaseFacade(db)
    case = facade.get_by_id(case_id)

    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found",
        )

    if case.customer_id != customer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    return _to_dict(facade.close(case_id))