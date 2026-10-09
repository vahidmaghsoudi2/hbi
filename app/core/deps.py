from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db  # re-export — single implementation
from app.core.auth import decode_token, validate_token_type
from app.models.user_role import UserRole, VALID_ROLES

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


async def get_current_customer_id(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> str:
    """Authenticate staff identities only; customers are records, never system users."""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    if not validate_token_type(token, "access"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    payload = decode_token(token)
    if payload is None or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    subject_id = payload["sub"]
    assigned_roles = {
        row.role
        for row in db.query(UserRole).filter(UserRole.subject_id == subject_id).all()
        if row.role in VALID_ROLES
    }
    if not assigned_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Customer identities cannot access the HBI system",
        )
    return subject_id
