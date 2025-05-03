from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm

from app.database.session import get_db
from app.services.auth import AuthService
from app.services.user import UserService
from app.schemas.login import LoginResponse
from app.schemas.user import UserCreate, UserResponse

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """ Register a new user """
    try:
        return await UserService.register(db, user_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=LoginResponse)
async def login_user(
    request: Request,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """ Log in a user and issue JWT tokens """
    try:
        return await AuthService.login(db, form_data, request, response)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.post("/refresh", response_model=LoginResponse)
async def refresh_token(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """ Refresh the access token using a refresh token """
    try:
        return await AuthService.refresh(db, request, response)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.post("/logout")
async def logout_user(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """ Log out the current user by invalidating their token """
    try:
        return await AuthService.logout(db, request, response)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))