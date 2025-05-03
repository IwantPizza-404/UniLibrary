from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.core.hashing import get_password_hash


class UserService:
    @staticmethod
    async def register(db: AsyncSession, user_data: UserCreate) -> UserResponse:
        """Register a new user"""
        existing_user = await UserRepository.get_by_email_or_username(db, user_data.email)
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")

        new_user = await UserRepository.create(db, user_data.dict())
        return new_user

    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: int) -> UserResponse:
        """Retrieve a user by their ID"""
        user = await UserRepository.get_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user

    @staticmethod
    async def update_profile(db: AsyncSession, current_user: UserResponse, user_data: UserUpdate) -> UserResponse:
        """Update the current user's profile"""
        try:
            updated_user = await UserRepository.update_profile(db, current_user, user_data)
            return updated_user
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update profile: {str(e)}"
            )