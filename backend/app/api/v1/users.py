from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import get_current_user
from app.database.session import get_db
from app.schemas.user import UserResponse, UserUpdate, UserProfile
from app.schemas.post import PostResponse
from app.services.user import UserService
from app.services.post import PostService

router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user=Depends(get_current_user)):
    """ Get the current user's profile """
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    user_data: UserUpdate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """ Update the current user's profile """
    return await UserService.update_profile(db, current_user, user_data)

@router.get("/{id}", response_model=UserResponse)
async def get_user_profile(id: int, db: AsyncSession = Depends(get_db)):
    """ Get a public profile of a user by their ID """
    user = await UserService.get_by_id(db, id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/me/uploads", response_model=list[PostResponse])
async def get_user_uploads(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """ Get the current user's uploaded files """
    return await PostService.get_by_user(db, current_user.id)

@router.get("/me/profile", response_model=UserProfile)
async def get_user_profile(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """ Get the current user's profile """
    return await UserService.get_profile(db, current_user.username)

@router.get("/{username}/profile", response_model=UserProfile)
async def get_user_profile(username: str, db: AsyncSession = Depends(get_db)):
    """ Get the user's profile """
    return await UserService.get_profile(db, username)