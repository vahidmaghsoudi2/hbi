from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.interface.facades import CaseFacade

router = APIRouter()


class CaseCreateRequest(BaseModel):
    customer_id: str
    case_type: str = "OPEN"


def _to_dict(obj):
    return vars(obj) if hasattr(obj, "__dict__") else obj


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_case(data: CaseCreateRequest, db: Session = Depends(get_db)):
    facade = CaseFacade(db)
    return _to_dict(facade.create(customer_id=data.customer_id, case_type=data.case_type))


@router.get("/customer/{customer_id}")
async def get_cases_by_customer(customer_id: str, db: Session = Depends(get_db)):
    facade = CaseFacade(db)
    return [_to_dict(c) for c in facade.find_by_customer(customer_id)]


@router.post("/{case_id}/close")
async def close_case(case_id: str, db: Session = Depends(get_db)):
    facade = CaseFacade(db)
    case = facade.close(case_id)
    if not case:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")
    return _to_dict(case)
