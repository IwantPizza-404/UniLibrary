from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.models import UserFollow

class UserFollowRepository:
    @staticmethod
    async def follow_user(db: AsyncSession, follower_id: int, following_id: int) -> UserFollow:
        """
        Create a follow relationship between two users.
        """
        follow = UserFollow(follower_id=follower_id, following_id=following_id)
        db.add(follow)
        await db.commit()
        await db.refresh(follow)
        return follow

    @staticmethod
    async def unfollow_user(db: AsyncSession, follower_id: int, following_id: int):
        """
        Remove a follow relationship between two users.
        """
        result = await db.execute(
            select(UserFollow).filter(
                UserFollow.follower_id == follower_id,
                UserFollow.following_id == following_id
            )
        )
        follow = result.scalar_one_or_none()
        if follow:
            await db.delete(follow)
            await db.commit()

    @staticmethod
    async def get_followers(db: AsyncSession, user_id: int, limit: int, offset: int):
        """
        Get all followers of a user.
        """
        result = await db.execute(
            select(UserFollow).filter(UserFollow.following_id == user_id).limit(limit).offset(offset)
        )
        return result.scalars().all()

    @staticmethod
    async def get_following(db: AsyncSession, user_id: int, limit: int, offset: int):
        """
        Get all users a user is following.
        """
        result = await db.execute(
            select(UserFollow).filter(UserFollow.follower_id == user_id).limit(limit).offset(offset)
        )
        return result.scalars().all()