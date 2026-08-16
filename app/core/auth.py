import os
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

from jose import JWTError, jwt
from pydantic import BaseModel


_ENV = os.getenv("HBI_ENV", "development").lower()

if _ENV == "production":
    SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    if not SECRET_KEY:
        raise RuntimeError("JWT_SECRET_KEY must be configured in production")
else:
    SECRET_KEY = os.getenv(
        "JWT_SECRET_KEY",
        "hbi-dev-secret-change-in-production",
    )

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
)
REFRESH_TOKEN_EXPIRE_DAYS = int(
    os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7")
)


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: Dict[str, Any]) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        days=REFRESH_TOKEN_EXPIRE_DAYS
    )
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        return jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )
    except JWTError:
        return None


def validate_token_type(token: str, expected_type: str) -> bool:
    payload = decode_token(token)
    if payload is None:
        return False
    return payload.get("type") == expected_type


def refresh_access_token(refresh_token: str) -> Optional[str]:
    if not validate_token_type(refresh_token, "refresh"):
        return None

    payload = decode_token(refresh_token)
    if payload is None:
        return None

    new_payload = {
        k: v
        for k, v in payload.items()
        if k not in ("exp", "type")
    }

    return create_access_token(new_payload)