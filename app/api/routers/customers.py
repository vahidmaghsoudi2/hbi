from typing import Optional, Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_customer_id
from app.interface.facades import CustomerFacade
from app.services.customer_service import CustomerService
from app.services.case_service import CaseService


router = APIRouter()


class CustomerCreateRequest(BaseModel):
    name: str
    mobile: Optional[str] = None
    consent: int = 0


class GuestCreateRequest(BaseModel):
    name: str = "مهمان"
    consent: int = 0
    concerns: Optional[str] = None


class IntakeRequest(BaseModel):
    """ثبت سریع مراجعه گالری — نام، نگرانی امروز، موبایل اختیاری."""
    name: str
    mobile: Optional[str] = None
    concerns: Optional[str] = Field(
        default=None,
        description="نیاز/دغدغه امروز؛ به موتور توصیه به‌صورت concerns پاس داده می‌شود",
    )
    consent: int = 0
    skin_profile: Optional[str] = None
    guest: bool = False
    open_case: bool = Field(
        default=True,
        description="اگر true باشد یک Case OPEN برای همین مشتری ساخته می‌شود",
    )


def _to_dict(obj):
    if obj is None:
        return None
    if hasattr(obj, "__dict__"):
        return {k: v for k, v in vars(obj).items() if not k.startswith("_")}
    return obj


def _customer_public(c) -> Dict[str, Any]:
    return {
        "customer_id": c.customer_id,
        "name": c.name,
        "mobile": c.mobile,
        "consent_to_store_data": c.consent_to_store_data,
        "concerns": getattr(c, "concerns", None),
        "skin_profile": getattr(c, "skin_profile", None),
    }


def _looks_like_mobile(value: Optional[str]) -> bool:
    if not value:
        return False
    digits = "".join(ch for ch in value if ch.isdigit())
    return len(digits) >= 10


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


@router.post("/guest", status_code=status.HTTP_201_CREATED)
async def register_guest(
    data: GuestCreateRequest,
    db: Session = Depends(get_db),
    _auth: str = Depends(get_current_customer_id),
):
    svc = CustomerService(db)
    try:
        kwargs: Dict[str, Any] = {"consent_to_store_data": data.consent}
        if data.concerns is not None:
            kwargs["concerns"] = data.concerns
        customer = svc.register_guest(name=data.name, **kwargs)
        db.commit()
        return _customer_public(customer)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/intake", status_code=status.HTTP_201_CREATED)
async def quick_intake(
    data: IntakeRequest,
    db: Session = Depends(get_db),
    customer_id: str = Depends(get_current_customer_id),
):
    """
    Intake سریع گالری.
    برمی‌گرداند: customer + recommendation_profile + (اختیاری) case
    آماده برای generate(case_id, recommendation_profile).
    """
    svc = CustomerService(db)
    mobile = data.mobile

    # اگر هر دو طرف شبیه موبایل باشند و فرق کنند → رد
    # در غیر این صورت (توکن اپراتور/pilot) اجازه ثبت مشتری گالری
    if (
        mobile
        and not data.guest
        and _looks_like_mobile(mobile)
        and _looks_like_mobile(customer_id)
        and mobile != customer_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Customer identity mismatch",
        )

    try:
        customer = svc.record_intake(
            name=data.name,
            mobile=None if data.guest else mobile,
            concerns=data.concerns,
            consent=data.consent,
            skin_profile=data.skin_profile,
            guest=data.guest or not mobile,
        )
        profile = svc.build_recommendation_profile(
            customer, concerns=data.concerns
        )

        case_payload = None
        if data.open_case:
            case = CaseService(db).create_case(
                customer_id=customer.customer_id,
                case_type="OPEN",
            )
            case_payload = {
                "case_id": case.case_id,
                "customer_id": case.customer_id,
                "case_type": case.case_type,
            }

        db.commit()
        return {
            "customer": _customer_public(customer),
            "case": case_payload,
            "recommendation_profile": profile,
            "generate_hint": {
                "path": "POST /api/v1/recommendations/generate",
                "body": {
                    "case_id": case_payload["case_id"] if case_payload else "<case_id>",
                    "customer_profile": profile,
                },
            },
        }
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/recommendation-profile")
async def get_recommendation_profile(
    db: Session = Depends(get_db),
    customer_id: str = Depends(get_current_customer_id),
    concerns: Optional[str] = None,
):
    svc = CustomerService(db)
    customer = None
    if str(customer_id).startswith("CUST_"):
        customer = svc.get_by_id(customer_id)
    else:
        customer = svc.find_by_mobile(customer_id)

    profile = svc.build_recommendation_profile(customer, concerns=concerns)
    return {
        "customer_id": customer.customer_id if customer else None,
        "recommendation_profile": profile,
        "found": customer is not None,
    }


@router.get("/search")
async def search_customers_by_name(
    q: str = Query(..., min_length=1, description="بخشی از نام مشتری"),
    db: Session = Depends(get_db),
    _auth: str = Depends(get_current_customer_id),
) -> List[Dict[str, Any]]:
    """جست‌وجوی سریع مشتری قبلی برای فروشنده گالری (≤۱۵ ثانیه هدف)."""
    svc = CustomerService(db)
    found = svc.find_by_name(q.strip())
    return [_customer_public(c) for c in found[:20]]


@router.get("/id/{target_customer_id}")
async def get_customer_by_id(
    target_customer_id: str,
    db: Session = Depends(get_db),
    _auth: str = Depends(get_current_customer_id),
):
    svc = CustomerService(db)
    customer = svc.get_by_id(target_customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return _customer_public(customer)


@router.get("/mobile/{mobile}")
async def find_customer_by_mobile(
    mobile: str,
    db: Session = Depends(get_db),
    customer_id: str = Depends(get_current_customer_id),
):
    # فروشنده با توکن غیرموبایلی می‌تواند با موبایل جستجو کند
    if _looks_like_mobile(customer_id) and mobile != customer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    facade = CustomerFacade(db)
    try:
        customer = facade.find_by_mobile(mobile)
    except Exception:
        customer = None

    if not customer:
        svc = CustomerService(db)
        raw = svc.find_by_mobile(mobile)
        if not raw:
            raise HTTPException(status_code=404, detail="Customer not found")
        return _customer_public(raw)

    return _to_dict(customer)
