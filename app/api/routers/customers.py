from typing import Optional, Any, Dict, List
from collections import defaultdict
import time
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_customer_id
from app.core.audit import audit_event
from app.interface.facades import CustomerFacade
from app.services.customer_service import CustomerService
from app.services.case_service import CaseService
from app.services.feedback_service import FeedbackService
from app.models.case import Case


router = APIRouter()

# Public guest bootstrap rate limit (process-local; Pilot hardening)
_guest_rate_limit: Dict[str, List[float]] = defaultdict(list)
_GUEST_RATE_WINDOW = 60  # seconds
_GUEST_RATE_MAX = 10


class CustomerCreateRequest(BaseModel):
    name: str
    mobile: Optional[str] = None
    consent: int = 0


class GuestCreateRequest(BaseModel):
    name: str = "مهمان"
    consent: int = 0
    concerns: Optional[str] = None


class ProfileFactCreateRequest(BaseModel):
    attribute_key: str
    value: Optional[str] = None
    value_state: str = "KNOWN"
    provenance: str = "CUSTOMER"
    reason: Optional[str] = None


class ProfileFactSupersedeRequest(BaseModel):
    value: Optional[str] = None
    value_state: str = "KNOWN"
    provenance: str = "CUSTOMER"
    reason: Optional[str] = None


class ProfileFactRevokeRequest(BaseModel):
    reason: Optional[str] = None


class IntakeRequest(BaseModel):
    """ثبت سریع مراجعه گالری — نام، نام خانوادگی و اطلاعات همین مراجعه."""
    name: str
    family_name: Optional[str] = Field(
        default=None,
        description="نام خانوادگی برای تطبیق هویت؛ نام کوچک در تطبیق دخالت ندارد",
    )
    mobile: Optional[str] = None
    concerns: Optional[str] = Field(
        default=None,
        description="نیاز/دغدغه امروز؛ به موتور توصیه به‌صورت concerns پاس داده می‌شود",
    )
    consent: int = 0
    skin_profile: Optional[str] = None
    guest: bool = False
    case_type: str = Field(
        default="OPEN",
        description="Consultation scope / Case type. Home Skin consultation sends SKIN.",
    )
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


def _profile_fact_public(fact) -> Dict[str, Any]:
    return {
        "profile_fact_id": fact.profile_fact_id,
        "customer_id": fact.customer_id,
        "attribute_key": fact.attribute_key,
        "value": fact.value,
        "value_state": fact.value_state,
        "provenance": fact.provenance,
        "status": fact.status,
        "supersedes_fact_id": fact.supersedes_fact_id,
        "created_at": fact.created_at,
        "updated_at": fact.updated_at,
    }


def _customer_public(c) -> Dict[str, Any]:
    return {
        "customer_id": c.customer_id,
        "name": c.name,
        "family_name": getattr(c, "family_name", None),
        "mobile": c.mobile,
        "consent_to_store_data": c.consent_to_store_data,
        "concerns": getattr(c, "concerns", None),
        "skin_profile": getattr(c, "skin_profile", None),
    }


def _looks_like_mobile(value: Optional[str]) -> bool:
    """True only for mobile-shaped identifiers, not internal customer_ids.

    Guest ids like CUST_GUEST_2026... contain long digit runs and must not
    be treated as a mobile number for identity-mismatch checks.
    """
    if not value:
        return False
    cleaned = value.strip()
    if cleaned.upper().startswith("CUST"):
        return False
    digits = "".join(ch for ch in cleaned if ch.isdigit())
    return len(digits) >= 10


def _guest_client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


def _enforce_guest_rate_limit(request: Request) -> None:
    """IP-based limit for public POST /guest — max 10 per 60s."""
    client_ip = _guest_client_ip(request)
    now = time.time()
    window = _GUEST_RATE_WINDOW
    recent = [
        t for t in _guest_rate_limit[client_ip] if now - t < window
    ]
    if len(recent) >= _GUEST_RATE_MAX:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many guest registration requests. Try again later.",
        )
    recent.append(now)
    _guest_rate_limit[client_ip] = recent


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
    request: Request,
    db: Session = Depends(get_db),
):
    """Public guest bootstrap for Home Front Door (no JWT).

    Rate-limited by client IP (10 req / 60s). Enables:
    createGuest → staff-customer-session (Admin) → intake (no pilot dependency).
    """
    _enforce_guest_rate_limit(request)

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


@router.post("/profile-facts", status_code=status.HTTP_201_CREATED)
async def create_profile_fact(
    data: ProfileFactCreateRequest,
    db: Session = Depends(get_db),
    customer_id: str = Depends(get_current_customer_id),
):
    from app.services.profile_fact_service import ProfileFactService

    try:
        fact = ProfileFactService(db).create(
            customer_id=customer_id,
            authorized_customer_id=customer_id,
            attribute_key=data.attribute_key,
            value=data.value,
            value_state=data.value_state,
            provenance=data.provenance,
            actor_id=customer_id,
            reason=data.reason,
        )
        result = _profile_fact_public(fact)
        db.commit()
        return result
    except ValueError as e:
        message = str(e)
        if message in {"Customer not found", "ProfileFact not found"}:
            raise HTTPException(status_code=404, detail=message)
        raise HTTPException(status_code=422, detail=message)


@router.post("/profile-facts/{fact_id}/supersede", status_code=status.HTTP_200_OK)
async def supersede_profile_fact(
    fact_id: str,
    data: ProfileFactSupersedeRequest,
    db: Session = Depends(get_db),
    customer_id: str = Depends(get_current_customer_id),
):
    from app.services.profile_fact_service import ProfileFactService

    try:
        fact = ProfileFactService(db).supersede(
            fact_id=fact_id,
            authorized_customer_id=customer_id,
            value=data.value,
            value_state=data.value_state,
            provenance=data.provenance,
            actor_id=customer_id,
            reason=data.reason,
        )
        result = _profile_fact_public(fact)
        db.commit()
        return result
    except ValueError as e:
        message = str(e)
        if message == "ProfileFact not found":
            raise HTTPException(status_code=404, detail=message)
        if message == "Customer ownership mismatch":
            raise HTTPException(status_code=403, detail="Access denied")
        raise HTTPException(status_code=422, detail=message)


@router.post("/profile-facts/{fact_id}/revoke", status_code=status.HTTP_200_OK)
async def revoke_profile_fact(
    fact_id: str,
    data: ProfileFactRevokeRequest,
    db: Session = Depends(get_db),
    customer_id: str = Depends(get_current_customer_id),
):
    from app.services.profile_fact_service import ProfileFactService

    try:
        fact = ProfileFactService(db).revoke(
            fact_id=fact_id,
            authorized_customer_id=customer_id,
            actor_id=customer_id,
            reason=data.reason,
        )
        result = _profile_fact_public(fact)
        db.commit()
        return result
    except ValueError as e:
        message = str(e)
        if message == "ProfileFact not found":
            raise HTTPException(status_code=404, detail=message)
        if message == "Customer ownership mismatch":
            raise HTTPException(status_code=403, detail="Access denied")
        raise HTTPException(status_code=422, detail=message)


@router.get("/profile-facts")
async def list_profile_facts(
    db: Session = Depends(get_db),
    customer_id: str = Depends(get_current_customer_id),
):
    from app.services.profile_fact_service import ProfileFactService

    try:
        facts = ProfileFactService(db).list_active(customer_id, customer_id)
        return [_to_dict(fact) for fact in facts]
    except ValueError as e:
        message = str(e)
        if message == "Customer not found":
            raise HTTPException(status_code=404, detail=message)
        if message == "Customer ownership mismatch":
            raise HTTPException(status_code=403, detail="Access denied")
        raise HTTPException(status_code=422, detail=message)


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

    Home flow: createGuest → staff-customer-session (Admin) → intake.
    When the JWT already identifies a customer (e.g. CUST_GUEST_*), reuse that
    row instead of creating a second guest — otherwise Case belongs to B while
    token is A → generate returns 403 Access denied.
    """
    svc = CustomerService(db)
    mobile = (data.mobile or "").strip() or None

    if data.consent not in (0, 1):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="consent must be 0 or 1",
        )

    # Legacy mobile-subject guard for pure mobile JWT subjects only.
    # CUST_* staff-customer tokens must not be treated as mobile numbers.
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
        authenticated = svc.get_by_id(customer_id)

        # Ownership check before any mutation: mobile owned by another row → 409.
        if mobile and not data.guest:
            mobile_owner = svc.find_by_mobile(mobile)
            if mobile_owner is not None and (
                authenticated is None
                or mobile_owner.customer_id != authenticated.customer_id
            ):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=(
                        "Mobile already belongs to another customer; "
                        "select the existing customer"
                    ),
                )

        if authenticated is not None:
            fields: Dict[str, Any] = {
                "name": data.name,
                "consent_to_store_data": data.consent,
            }
            if data.family_name is not None:
                fields["family_name"] = (data.family_name or "").strip() or None
            if not data.open_case:
                if data.concerns is not None:
                    fields["concerns"] = data.concerns
                if data.skin_profile is not None:
                    fields["skin_profile"] = data.skin_profile
            if data.consent == 1:
                fields["consent_date"] = datetime.now()
            if mobile and not data.guest:
                # Confirm family-name identity only when reusing the same
                # mobile already attached to this customer. Assigning a new,
                # currently unowned mobile to this customer is not a mobile
                # match and must not be blocked by a legacy NULL family_name.
                existing_mobile = (getattr(authenticated, "mobile", None) or "").strip()
                if existing_mobile and existing_mobile == mobile:
                    from app.services.customer_service import assert_mobile_identity_allows_bind

                    try:
                        assert_mobile_identity_allows_bind(
                            existing=authenticated,
                            # Require the incoming surname explicitly even when the
                            # mobile already belongs to this customer. Falling back to
                            # the stored surname would silently approve an omitted identity
                            # field rather than confirming the caller's claim.
                            incoming_family_name=data.family_name,
                        )
                    except ValueError as e:
                        raise HTTPException(
                            status_code=status.HTTP_409_CONFLICT,
                            detail=str(e),
                        )
                fields["mobile"] = mobile
            customer = (
                svc.repository.update(authenticated.customer_id, **fields)
                or authenticated
            )
        else:
            customer = svc.record_intake(
                name=data.name,
                mobile=None if data.guest else mobile,
                concerns=data.concerns,
                consent=data.consent,
                skin_profile=data.skin_profile,
                guest=data.guest or not mobile,
                family_name=data.family_name,
            )

        profile = svc.build_recommendation_profile(
            customer, concerns=data.concerns
        )

        case_payload = None
        if data.open_case:
            case = CaseService(db).create_case(
                customer_id=customer.customer_id,
                case_type=(data.case_type or "OPEN").strip().upper(),
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
        message = str(e)
        if "identity conflict" in message.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail=message
            )
        raise HTTPException(status_code=422, detail=message)


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
async def search_customers_by_name_or_mobile(
    q: str = Query(..., min_length=1, description="بخشی از نام یا شماره موبایل مشتری"),
    db: Session = Depends(get_db),
    _auth: str = Depends(get_current_customer_id),
) -> List[Dict[str, Any]]:
    """جست‌وجوی سریع مشتری قبلی با نام یا شماره موبایل برای فروشنده گالری."""
    svc = CustomerService(db)
    query = q.strip()
    if _looks_like_mobile(query):
        found = svc.find_by_mobile(query)
        return [_customer_public(found)] if found else []
    found = svc.find_by_name(query)
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


class CustomerFeedbackRequest(BaseModel):
    case_id: str
    recommendation_id: str
    outcome: Optional[str] = None
    rating: Optional[str] = None
    comment: Optional[str] = None


def _feedback_public(feedback) -> Dict[str, Any]:
    return {
        "feedback_id": feedback.feedback_id,
        "case_id": feedback.case_id,
        "recommendation_id": feedback.recommendation_id,
        "source": feedback.source,
        "outcome": feedback.outcome,
        "rating": feedback.rating,
        "comment": feedback.comment,
        "follow_up_at": feedback.follow_up_at.isoformat() if feedback.follow_up_at else None,
        "created_at": feedback.created_at.isoformat() if feedback.created_at else None,
    }


@router.post("/feedback", status_code=status.HTTP_201_CREATED)
async def create_customer_feedback(
    data: CustomerFeedbackRequest,
    db: Session = Depends(get_db),
    customer_id: str = Depends(get_current_customer_id),
):
    """Record an authenticated customer's response to an existing Recommendation."""
    case = db.get(Case, data.case_id)
    if case is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    if case.customer_id != customer_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    svc = FeedbackService(db)
    try:
        feedback = svc.create_feedback(
            case_id=data.case_id,
            source="CUSTOMER",
            outcome=data.outcome,
            rating=data.rating,
            comment=data.comment,
            recommendation_id=data.recommendation_id,
        )
        db.commit()
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))

    audit_event(
        "customer_feedback_created",
        customer_id=customer_id,
        path="/api/v1/customers/feedback",
        outcome="ok",
        detail=feedback.feedback_id,
        extra={
            "target": {
                "case_id": feedback.case_id,
                "recommendation_id": feedback.recommendation_id,
            },
            "new_state": {
                "source": feedback.source,
                "outcome": feedback.outcome,
            },
        },
    )
    return _feedback_public(feedback)


@router.get("/feedback/case/{case_id}")
async def list_customer_feedback(
    case_id: str,
    db: Session = Depends(get_db),
    customer_id: str = Depends(get_current_customer_id),
) -> List[Dict[str, Any]]:
    """Retrieve customer responses only for a Case owned by the authenticated customer."""
    case = db.get(Case, case_id)
    if case is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    if case.customer_id != customer_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    feedbacks = FeedbackService(db).list_by_case(case_id)
    return [_feedback_public(feedback) for feedback in feedbacks if feedback.source == "CUSTOMER"]
