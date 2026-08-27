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
)
from app.core.deps import get_db
from app.models.customer import Customer
from app.core.audit import audit_event
from app.core.brute_force import clear_failures, is_locked, make_key, record_failure

router = APIRouter()


class PilotTokenRequest(BaseModel):
    customer_id: str


@router.post("/login", response_model=TokenPair)
async def login():
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Auth pending PO decision (POD-001: OTP/Magic Link). Schema v1.1 has no password field.",
    )


@router.post("/pilot-token", response_model=TokenPair)
async def pilot_token(
    request: PilotTokenRequest,
    http_request: Request,
    db: Session = Depends(get_db),
):
    """Dev/Pilot only: issue JWT for an existing customer_id. Disabled in production."""
    forwarded = http_request.headers.get("x-forwarded-for")
    client_ip = (
        forwarded.split(",")[0].strip()
        if forwarded
        else (http_request.client.host if http_request.client else "unknown")
    )
    bf_key = make_key(client_ip, request.customer_id)

    remaining = is_locked(bf_key)
    if remaining is not None:
        audit_event(
            "pilot_token",
            customer_id=request.customer_id,
            path="/api/v1/auth/pilot-token",
            outcome="denied",
            detail="brute_force_lockout",
            extra={"retry_after": remaining, "client_ip": client_ip},
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many failed attempts. Retry after {remaining}s.",
            headers={"Retry-After": str(remaining)},
        )

    if os.getenv("HBI_ENV", "development").lower() == "production":
        audit_event(
            "pilot_token",
            customer_id=request.customer_id,
            path="/api/v1/auth/pilot-token",
            outcome="denied",
            detail="disabled_in_production",
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="pilot-token disabled in production",
        )
    customer = db.get(Customer, request.customer_id)
    if customer is None:
        lockout = record_failure(bf_key)
        audit_event(
            "pilot_token",
            customer_id=request.customer_id,
            path="/api/v1/auth/pilot-token",
            outcome="denied",
            detail="customer_not_found",
            extra={"client_ip": client_ip, "lockout": lockout},
        )
        if lockout is not None:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many failed attempts. Retry after {lockout}s.",
                headers={"Retry-After": str(lockout)},
            )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )
    clear_failures(bf_key)
    payload = {"sub": request.customer_id}
    audit_event(
        "pilot_token",
        customer_id=request.customer_id,
        path="/api/v1/auth/pilot-token",
        outcome="ok",
        extra={"client_ip": client_ip},
    )
    return TokenPair(
        access_token=create_access_token(payload),
        refresh_token=create_refresh_token(payload),
        token_type="bearer",
    )


@router.post("/refresh", response_model=TokenPair)
async def refresh(request: RefreshRequest):
    new_access = refresh_access_token(request.refresh_token)
    if not new_access:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    return TokenPair(
        access_token=new_access,
        refresh_token=request.refresh_token,
        token_type="bearer",
    )
