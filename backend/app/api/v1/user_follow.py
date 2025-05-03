from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.core.deps import get_current_user
from app.services.user_follow import UserFollowService

router = APIRouter()

@router.post("/{user_id}/follow", status_code=status.HTTP_204_NO_CONTENT)
async def follow_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Follow a user.
    """
    await UserFollowService.follow_user(db, current_user.id, user_id)

@router.delete("/{user_id}/unfollow", status_code=status.HTTP_204_NO_CONTENT)
async def unfollow_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Unfollow a user.
    """
    await UserFollowService.unfollow_user(db, current_user.id, user_id)

@router.get("/{user_id}/followers")
async def get_followers(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    limit: int = 10,
    offset: int = 0
):
    """
    Get all followers of a user.
    """
    followers = await UserFollowService.get_followers(db, user_id, limit, offset)
    return [{"follower_id": f.follower_id, "created_at": f.created_at} for f in followers]

@router.get("/{user_id}/following")
async def get_following(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    limit: int = 10,
    offset: int = 0
):
    """
    Get all users a user is following.
    """
    following = await UserFollowService.get_following(db, user_id, limit, offset)
    return [{"following_id": f.following_id, "created_at": f.created_at} for f in following]