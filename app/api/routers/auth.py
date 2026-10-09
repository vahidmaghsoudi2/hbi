import os

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.auth import (
    TokenPair,
    RefreshRequest,
    refresh_access_token,
    create_access_token,
    create_refresh_token,
    create_staff_customer_access_token,
    STAFF_CUSTOMER_ACCESS_EXPIRE_MINUTES,
)
from app.core.deps import get_db
from app.core.authorization import require_any_role
from app.models.customer import Customer
from app.models.user_role import UserRole, ROLE_EDITOR, ROLE_PO, ROLE_ADMIN
from app.models.admin_credential import AdminCredential
from app.services.admin_auth_service import verify_admin_password
from app.core.audit import audit_event
from app.core.brute_force import clear_failures, is_locked, make_key, record_failure

router = APIRouter()


class PilotTokenRequest(BaseModel):
    customer_id: str


class AdminLoginRequest(BaseModel):
    username: str
    password: str


class StaffCustomerSessionRequest(BaseModel):
    customer_id: str


class StaffCustomerSessionResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    customer_id: str
    purpose: str = "staff_customer_session"


@router.post("/login", response_model=TokenPair)
async def login(
    request: AdminLoginRequest,
    http_request: Request,
    db: Session = Depends(get_db),
):
    forwarded = http_request.headers.get("x-forwarded-for")
    client_ip = (
        forwarded.split(",")[0].strip()
        if forwarded
        else (http_request.client.host if http_request.client else "unknown")
    )
    bf_key = make_key(client_ip, request.username.strip().lower())

    remaining = is_locked(bf_key)
    if remaining is not None:
        audit_event(
            "admin_login",
            customer_id=request.username,
            path="/api/v1/auth/login",
            outcome="denied",
            detail="brute_force_lockout",
            extra={"retry_after": remaining, "client_ip": client_ip},
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many failed attempts. Retry after {remaining}s.",
            headers={"Retry-After": str(remaining)},
        )

    credential = db.query(AdminCredential).filter(
        AdminCredential.username == request.username.strip()
    ).first()
    if credential is None or not verify_admin_password(credential, request.password):
        lockout = record_failure(bf_key)
        audit_event(
            "admin_login",
            customer_id=request.username,
            path="/api/v1/auth/login",
            outcome="denied",
            detail="invalid_credentials",
            extra={"client_ip": client_ip, "lockout": lockout},
        )
        if lockout is not None:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many failed attempts. Retry after {lockout}s.",
                headers={"Retry-After": str(lockout)},
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    role = db.query(UserRole).filter(
        UserRole.subject_id == credential.subject_id,
        UserRole.role == ROLE_ADMIN,
    ).first()
    if role is None:
        audit_event(
            "admin_login",
            customer_id=credential.subject_id,
            path="/api/v1/auth/login",
            outcome="denied",
            detail="admin_role_missing",
            extra={"client_ip": client_ip},
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role is not assigned",
        )

    clear_failures(bf_key)
    payload = {"sub": credential.subject_id}
    audit_event(
        "admin_login",
        customer_id=credential.subject_id,
        path="/api/v1/auth/login",
        outcome="ok",
        extra={"client_ip": client_ip, "role": ROLE_ADMIN},
    )
    return TokenPair(
        access_token=create_access_token(payload),
        refresh_token=create_refresh_token(payload),
        token_type="bearer",
    )


@router.post("/pilot-token", response_model=TokenPair)
async def pilot_token(
    request: PilotTokenRequest,
    http_request: Request,
    db: Session = Depends(get_db),
):
    """Dev/Pilot only: issue JWT for an existing customer_id. Disabled in production."""
    if not os.getenv("HBI_ALLOW_PILOT_TOKEN", "").strip().lower() in ("1", "true", "yes"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Pilot token issuance is disabled",
        )
    customer = db.query(Customer).filter(Customer.customer_id == request.customer_id).first()
    if customer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    payload = {"sub": request.customer_id}
    audit_event(
        "pilot_token",
        customer_id=request.customer_id,
        path="/api/v1/auth/pilot-token",
        outcome="ok",
    )
    return TokenPair(
        access_token=create_access_token(payload),
        refresh_token=create_refresh_token(payload),
        token_type="bearer",
    )


@router.post("/refresh", response_model=TokenPair)
async def refresh(request: RefreshRequest):
    return refresh_access_token(request.refresh_token)


@router.post("/staff-customer-session", response_model=StaffCustomerSessionResponse)
async def staff_customer_session(
    request: StaffCustomerSessionRequest,
    http_request: Request,
    db: Session = Depends(get_db),
    _admin=Depends(require_any_role([ROLE_ADMIN])),
):
    """Admin-only: issue short-lived access token bound to a specific customer.

    - Claims: sub=customer_id, purpose=staff_customer_session, issued_by=admin subject,
      staff_session=True
    - TTL: STAFF_CUSTOMER_ACCESS_EXPIRE_MINUTES (default 15)
    - No refresh token
    - Audited
    """
    admin_sub = getattr(_admin, "sub", None) or getattr(_admin, "subject_id", None) or "admin"
    customer = db.query(Customer).filter(Customer.customer_id == request.customer_id).first()
    if customer is None:
        audit_event(
            "staff_customer_session",
            customer_id=request.customer_id,
            path="/api/v1/auth/staff-customer-session",
            outcome="denied",
            detail="customer_not_found",
            extra={"issued_by": admin_sub},
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

    access = create_staff_customer_access_token(
        customer_id=request.customer_id,
        issued_by=str(admin_sub),
    )
    audit_event(
        "staff_customer_session",
        customer_id=request.customer_id,
        path="/api/v1/auth/staff-customer-session",
        outcome="ok",
        extra={"issued_by": admin_sub, "ttl_minutes": STAFF_CUSTOMER_ACCESS_EXPIRE_MINUTES},
    )
    return StaffCustomerSessionResponse(
        access_token=access,
        expires_in=STAFF_CUSTOMER_ACCESS_EXPIRE_MINUTES * 60,
        customer_id=request.customer_id,
    )
