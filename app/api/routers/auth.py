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
from app.models.user_role import UserRole, ROLE_EDITOR, ROLE_PO, ROLE_ADMIN, ROLE_GALLERY_OPERATOR
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
    gallery_role = db.query(UserRole).filter(
        UserRole.subject_id == credential.subject_id,
        UserRole.role == ROLE_GALLERY_OPERATOR,
    ).first()
    if role is None or gallery_role is not None:
        detail = (
            "Admin/GalleryOperator identity conflict"
            if gallery_role is not None
            else "Admin role is not assigned"
        )
        audit_event(
            "admin_login",
            customer_id=credential.subject_id,
            path="/api/v1/auth/login",
            outcome="denied",
            detail="role_conflict" if gallery_role is not None else "admin_role_missing",
            extra={"client_ip": client_ip},
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
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



@router.post("/operator-login", response_model=TokenPair)
async def operator_login(
    request: AdminLoginRequest,
    http_request: Request,
    db: Session = Depends(get_db),
):
    """Production gallery-operator login using separately provisioned credentials."""
    forwarded = http_request.headers.get("x-forwarded-for")
    client_ip = forwarded.split(",")[0].strip() if forwarded else (
        http_request.client.host if http_request.client else "unknown"
    )
    username = request.username.strip()
    bf_key = make_key(client_ip, username.lower())
    remaining = is_locked(bf_key)
    if remaining is not None:
        audit_event(
            "gallery_operator_login", customer_id=username,
            path="/api/v1/auth/operator-login", outcome="denied",
            detail="brute_force_lockout",
            extra={"retry_after": remaining, "client_ip": client_ip},
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many failed attempts. Retry after {remaining}s.",
            headers={"Retry-After": str(remaining)},
        )
    credential = db.query(AdminCredential).filter(AdminCredential.username == username).first()
    if credential is None or not verify_admin_password(credential, request.password):
        lockout = record_failure(bf_key)
        audit_event(
            "gallery_operator_login", customer_id=username,
            path="/api/v1/auth/operator-login", outcome="denied",
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
        UserRole.role == ROLE_GALLERY_OPERATOR,
    ).first()
    admin_role = db.query(UserRole).filter(
        UserRole.subject_id == credential.subject_id,
        UserRole.role == ROLE_ADMIN,
    ).first()
    if role is None or admin_role is not None:
        conflict = admin_role is not None
        audit_event(
            "gallery_operator_login", customer_id=credential.subject_id,
            path="/api/v1/auth/operator-login", outcome="denied",
            detail="role_conflict" if conflict else "gallery_operator_role_missing",
            extra={"client_ip": client_ip},
        )
        detail = (
            "Admin/GalleryOperator identity conflict"
            if conflict else "Gallery operator role is not assigned"
        )
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)
    clear_failures(bf_key)
    payload = {"sub": credential.subject_id}
    audit_event(
        "gallery_operator_login", customer_id=credential.subject_id,
        path="/api/v1/auth/operator-login", outcome="ok",
        extra={"client_ip": client_ip, "role": ROLE_GALLERY_OPERATOR},
    )
    return TokenPair(
        access_token=create_access_token(payload),
        refresh_token=create_refresh_token(payload),
        token_type="bearer",
    )


@router.post("/pilot-token", response_model=TokenPair)
async def pilot_token():
    """Legacy customer-token issuance is disabled; customers are not system users."""
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Customer tokens are disabled. Use an authorized staff account.",
    )


@router.post("/pilot-operator-token", response_model=TokenPair)
async def pilot_operator_token(
    http_request: Request,
    db: Session = Depends(get_db),
):
    """Dev/Pilot only: issue a scoped Editor token for Product Intake operations."""
    if os.getenv("HBI_ENV", "development").lower() == "production":
        audit_event(
            "pilot_operator_token",
            path="/api/v1/auth/pilot-operator-token",
            outcome="denied",
            detail="disabled_in_production",
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="pilot-operator-token disabled in production",
        )

    subject_id = os.getenv("HBI_PILOT_OPERATOR_SUBJECT", "USR_PILOT_EDITOR")
    role = db.query(UserRole).filter(
        UserRole.subject_id == subject_id,
        UserRole.role == ROLE_EDITOR,
    ).first()
    if role is None:
        db.add(UserRole(
            user_role_id=f"UR-{subject_id}-{ROLE_EDITOR.replace('/', '-')}",
            subject_id=subject_id,
            role=ROLE_EDITOR,
        ))
        db.commit()

    payload = {"sub": subject_id}
    client_ip = http_request.client.host if http_request.client else "unknown"
    audit_event(
        "pilot_operator_token",
        customer_id=subject_id,
        path="/api/v1/auth/pilot-operator-token",
        outcome="ok",
        extra={"client_ip": client_ip, "role": ROLE_EDITOR},
    )
    return TokenPair(
        access_token=create_access_token(payload),
        refresh_token=create_refresh_token(payload),
        token_type="bearer",
    )


@router.post("/pilot-po-token", response_model=TokenPair)
async def pilot_po_token(
    http_request: Request,
    db: Session = Depends(get_db),
):
    """Dev/Pilot only: issue a scoped PO token for governed Product Review transitions."""
    if os.getenv("HBI_ENV", "development").lower() == "production":
        audit_event(
            "pilot_po_token",
            path="/api/v1/auth/pilot-po-token",
            outcome="denied",
            detail="disabled_in_production",
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="pilot-po-token disabled in production",
        )

    subject_id = os.getenv("HBI_PILOT_PO_SUBJECT", "USR_PILOT_PO")
    role = db.query(UserRole).filter(
        UserRole.subject_id == subject_id,
        UserRole.role == ROLE_PO,
    ).first()
    if role is None:
        db.add(UserRole(
            user_role_id=f"UR-{subject_id}-{ROLE_PO}",
            subject_id=subject_id,
            role=ROLE_PO,
        ))
        db.commit()

    client_ip = http_request.client.host if http_request.client else "unknown"
    audit_event(
        "pilot_po_token",
        customer_id=subject_id,
        path="/api/v1/auth/pilot-po-token",
        outcome="ok",
        extra={"client_ip": client_ip, "role": ROLE_PO},
    )
    payload = {"sub": subject_id}
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
