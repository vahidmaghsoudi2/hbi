from fastapi import APIRouter, HTTPException, status
from app.core.auth import TokenPair, RefreshRequest, refresh_access_token

router = APIRouter()


@router.post("/login", response_model=TokenPair)
async def login():
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Auth pending PO decision (POD-001: OTP/Magic Link). Schema v1.1 has no password field.")


@router.post("/refresh", response_model=TokenPair)
async def refresh(request: RefreshRequest):
    new_access = refresh_access_token(request.refresh_token)
    if not new_access:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    return TokenPair(access_token=new_access, refresh_token=request.refresh_token, token_type="bearer")
