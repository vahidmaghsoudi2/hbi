import os

from fastapi import APIRouter, Depends, HTTPException, status
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
    db: Session = Depends(get_db),
):
    """Dev/Pilot only: issue JWT for an existing customer_id. Disabled in production."""
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
        audit_event(
            "pilot_token",
            customer_id=request.customer_id,
            path="/api/v1/auth/pilot-token",
            outcome="denied",
            detail="customer_not_found",
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )
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
