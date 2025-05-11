from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user import UserRepository
from app.repositories.user_follow import UserFollowRepository
from app.repositories.post import PostRepository
from app.repositories.vote import VoteRepository
from app.schemas.user import UserCreate, UserResponse, UserUpdate, UserProfile
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

    @staticmethod
    async def get_profile(db: AsyncSession, username: str) -> UserProfile:
        """Get a profile of a user by their username"""
        user = await UserRepository.get_by_username(db, username)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        followers_count = await UserFollowRepository.get_followers_count(db, user.id)
        following_count = await UserFollowRepository.get_following_count(db, user.id)
        uploads_count = await PostRepository.get_posts_count(db, user.id)
        upvotes_count = await VoteRepository.get_upvotes_count(db, user.id)
        downvotes_count = await VoteRepository.get_downvotes_count(db, user.id)
        
        user_profile = UserProfile(
            id=user.id,
            username=user.username,
            full_name=user.full_name,
            email=user.email,
            followers_count=followers_count,
            following_count=following_count,
            uploads_count=uploads_count,
            upvotes_count=upvotes_count,
            downvotes_count=downvotes_count,
            created_at=user.created_at,
            is_active=user.is_active,
        )
        return user_profile