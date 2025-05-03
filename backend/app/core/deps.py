from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, Request, status
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.security import OAuth2PasswordBearer
from app.repositories.user import UserRepository
from app.database.session import get_db
from app.core.jwt import decode_access_token
from app.schemas.token import TokenPayload

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

async def get_optional_token(request: Request) -> Optional[str]:
    """
    Extract the token from the Authorization header if it exists.
    Return None if the header is missing or invalid.
    """
    authorization: str = request.headers.get("Authorization")
    if not authorization:
        return None
    scheme, token = get_authorization_scheme_param(authorization)
    if scheme.lower() != "bearer":
        return None
    return token

async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """Retrieve the current user based on the access token"""
    try:
        payload = decode_access_token(token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    
    user_id: str = payload.sub if isinstance(payload, TokenPayload) else payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    user = await UserRepository.get_by_id(db, user_id=user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive or not found",
        )
    
    return user

async def get_current_user_optional(
    db: AsyncSession = Depends(get_db),
    token: Optional[str] = Depends(get_optional_token)
):
    if not token:
        return None

    try:
        payload = decode_access_token(token)
    except Exception:
        return None

    user_id: str = payload.sub if isinstance(payload, TokenPayload) else payload.get("sub")
    if not user_id:
        return None

    user = await UserRepository.get_by_id(db, user_id=user_id)
    if not user or not user.is_active:
        return None

    return user