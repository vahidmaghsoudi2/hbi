from typing import Optional, Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_customer_id
from app.interface.facades import CustomerFacade
from app.services.customer_service import CustomerService


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
    """مشتری مهمان بدون موبایل — فقط واحد پروفایل."""
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
    خروجی شامل recommendation_profile آماده برای
    RecommendationFacade.generate(case_id, customer_profile).
    """
    svc = CustomerService(db)
    mobile = data.mobile
    if mobile and mobile != customer_id and not data.guest:
        # در حالت pilot-token گاهی customer_id همان موبایل است
        if customer_id and not customer_id.startswith("CUST_"):
            if mobile != customer_id:
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
        db.commit()
        profile = svc.build_recommendation_profile(
            customer, concerns=data.concerns
        )
        return {
            "customer": _customer_public(customer),
            "recommendation_profile": profile,
            "next_step": "ایجاد Case با customer_id سپس generate(case_id, recommendation_profile)",
        }
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/recommendation-profile")
async def get_recommendation_profile(
    db: Session = Depends(get_db),
    customer_id: str = Depends(get_current_customer_id),
    concerns: Optional[str] = None,
):
    """
    دیکشنری آماده قرارداد Qwen1.
    اگر customer_id از نوع CUST_* باشد از روی id؛ وگرنه جست‌وجوی موبایل.
    """
    svc = CustomerService(db)
    customer = None
    if customer_id.startswith("CUST_"):
        customer = svc.get_by_id(customer_id)
    else:
        customer = svc.find_by_mobile(customer_id)

    profile = svc.build_recommendation_profile(customer, concerns=concerns)
    return {
        "customer_id": customer.customer_id if customer else None,
        "recommendation_profile": profile,
        "found": customer is not None,
    }


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
