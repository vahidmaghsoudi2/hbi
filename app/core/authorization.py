"""P4 P0 — Server-side role resolution and authorization helpers."""
from __future__ import annotations
from typing import Set
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.deps import get_current_customer_id, get_db, oauth2_scheme
from app.core.auth import decode_token, STAFF_CUSTOMER_SESSION_PURPOSE
from app.models.user_role import VALID_ROLES, UserRole

def get_roles_for_subject(db: Session, subject_id: str) -> Set[str]:
    rows = db.query(UserRole).filter(UserRole.subject_id == subject_id).all()
    return {r.role for r in rows if r.role in VALID_ROLES}

async def get_current_subject_and_roles(
    subject_id: str = Depends(get_current_customer_id),
    db: Session = Depends(get_db),
) -> tuple:
    roles = get_roles_for_subject(db, subject_id)
    return subject_id, roles

def require_any_role(*allowed: str):
    async def _checker(
        subject_id: str = Depends(get_current_customer_id),
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db),
    ) -> tuple:
        # A staff-issued customer session is intentionally scoped to a customer.
        # Never let its customer subject inherit staff/Admin authority, even if
        # a role row is accidentally assigned to an identically named subject.
        payload = decode_token(token) if token else None
        if payload and payload.get("purpose") == STAFF_CUSTOMER_SESSION_PURPOSE:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Staff customer session cannot be used for staff authorization",
            )
        roles = get_roles_for_subject(db, subject_id)
        if not roles.intersection(set(allowed)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required role one of: {list(allowed)}; subject has: {sorted(roles) or 'none'}",
            )
        return subject_id, roles
    return _checker
