"""Loopback-only operator session for the single-user local HBI workstation."""
import os
import ipaddress

from fastapi import APIRouter, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.auth import create_access_token, create_refresh_token, TokenPair
from app.database import SessionLocal
from app.models.user_role import UserRole, ROLE_ADMIN

router = APIRouter()


@router.post("/local-session", response_model=TokenPair)
async def local_session(request: Request):
    """Issue an Admin token only when explicitly enabled for a loopback dev server."""
    if os.getenv("HBI_ENV", "development").lower() == "production":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Local session disabled in production")
    if os.getenv("HBI_LOCAL_AUTO_LOGIN") != "1":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Local session is not enabled")
    client_host = request.client.host if request.client else ""
    try:
        if not ipaddress.ip_address(client_host).is_loopback:
            raise ValueError("not loopback")
    except ValueError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Loopback access only")

    subject_id = "USR_LOCAL_ADMIN"
    db: Session = SessionLocal()
    try:
        role = db.query(UserRole).filter(
            UserRole.subject_id == subject_id,
            UserRole.role == ROLE_ADMIN,
        ).first()
        if role is None:
            db.add(UserRole(
                user_role_id="UR-USR_LOCAL_ADMIN-Admin",
                subject_id=subject_id,
                role=ROLE_ADMIN,
            ))
            db.commit()
    finally:
        db.close()

    payload = {"sub": subject_id}
    return TokenPair(
        access_token=create_access_token(payload),
        refresh_token=create_refresh_token(payload),
        token_type="bearer",
    )
