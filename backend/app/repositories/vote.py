from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import func
from app.database.models import PostVote, Post


class VoteRepository:
    @staticmethod
    async def get_vote(db: AsyncSession, user_id: int, post_id: int) -> Optional[PostVote]:
        """Retrieve a user's vote on a specific post."""
        try:
            result = await db.execute(
                select(PostVote).filter(PostVote.user_id == user_id, PostVote.post_id == post_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            raise
    
    @staticmethod
    async def get_upvotes_count(db: AsyncSession, user_id: int) -> int:
        """Get the number of upvotes for a given user."""
        result = await db.execute(
            select(func.count())
            .select_from(PostVote)
            .join(Post, Post.id == PostVote.post_id)
            .filter(
                Post.author_id == user_id,
                PostVote.is_upvote == True
            )
        )
        return result.scalar() or 0
    
    @staticmethod
    async def get_downvotes_count(db: AsyncSession, user_id: int) -> int:
        """Get the number of downvotes for a given user."""
        result = await db.execute(
            select(func.count())
            .select_from(PostVote)
            .join(Post, Post.id == PostVote.post_id)
            .filter(
                Post.author_id == user_id,
                PostVote.is_upvote == False
            )
        )
        return result.scalar() or 0

    @staticmethod
    async def create_vote(db: AsyncSession, user_id: int, post_id: int, is_upvote: bool) -> PostVote:
        """Create a new vote."""
        vote = PostVote(user_id=user_id, post_id=post_id, is_upvote=is_upvote)
        db.add(vote)
        await db.commit()
        await db.refresh(vote)
        return vote

    @staticmethod
    async def update_vote(db: AsyncSession, vote: PostVote, is_upvote: bool) -> PostVote:
        """Update an existing vote."""
        vote.is_upvote = is_upvote
        await db.commit()
        await db.refresh(vote)
        return vote

    @staticmethod
    async def delete_vote(db: AsyncSession, vote: PostVote):
        """Delete an existing vote."""
        await db.delete(vote)
        await db.commit()