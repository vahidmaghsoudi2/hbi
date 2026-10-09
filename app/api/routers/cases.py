from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.core.authorization import get_current_subject_and_roles, is_gallery_operator_or_admin
from app.interface.facades import CaseFacade
from app.models.customer import Customer

router = APIRouter()

class CaseCreateRequest(BaseModel):
    customer_id: str
    case_type: str = "OPEN"

def _to_dict(obj):
    return vars(obj) if hasattr(obj, "__dict__") else obj

def _assert_case_access(db: Session, case_id: str, subject_id: str, roles: set):
    case = CaseFacade(db).get_by_id(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    if case.customer_id != subject_id and not is_gallery_operator_or_admin(roles):
        raise HTTPException(status_code=403, detail="Access denied")
    return case

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_case(data: CaseCreateRequest, db: Session = Depends(get_db), subject_and_roles: tuple = Depends(get_current_subject_and_roles)):
    subject_id, roles = subject_and_roles
    if is_gallery_operator_or_admin(roles):
        if db.get(Customer, data.customer_id) is None:
            raise HTTPException(status_code=404, detail="Customer not found")
        target_customer_id = data.customer_id
    else:
        if data.customer_id != subject_id:
            raise HTTPException(status_code=403, detail="Access denied")
        target_customer_id = subject_id
    return _to_dict(CaseFacade(db).create(customer_id=target_customer_id, case_type=data.case_type))

@router.get("/customer/{customer_id}")
async def get_cases_by_customer(customer_id: str, db: Session = Depends(get_db), subject_and_roles: tuple = Depends(get_current_subject_and_roles)):
    subject_id, roles = subject_and_roles
    if customer_id != subject_id and not is_gallery_operator_or_admin(roles):
        raise HTTPException(status_code=403, detail="Access denied")
    return [_to_dict(c) for c in CaseFacade(db).find_by_customer(customer_id)]

@router.post("/{case_id}/close")
async def close_case(case_id: str, db: Session = Depends(get_db), subject_and_roles: tuple = Depends(get_current_subject_and_roles)):
    subject_id, roles = subject_and_roles
    case = _assert_case_access(db, case_id, subject_id, roles)
    return _to_dict(CaseFacade(db).close(case.case_id))
