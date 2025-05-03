from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.repositories.user_follow import UserFollowRepository

class UserFollowService:
    @staticmethod
    async def follow_user(db: AsyncSession, follower_id: int, following_id: int):
        if follower_id == following_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot follow yourself."
            )
        return await UserFollowRepository.follow_user(db, follower_id, following_id)

    @staticmethod
    async def unfollow_user(db: AsyncSession, follower_id: int, following_id: int):
        if follower_id == following_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot unfollow yourself."
            )
        await UserFollowRepository.unfollow_user(db, follower_id, following_id)

    @staticmethod
    async def get_followers(db: AsyncSession, user_id: int, limit: int, offset: int):
        return await UserFollowRepository.get_followers(db, user_id, limit=limit, offset=offset)

    @staticmethod
    async def get_following(db: AsyncSession, user_id: int, limit: int, offset: int):
        return await UserFollowRepository.get_following(db, user_id, limit=limit, offset=offset)