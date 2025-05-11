from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import func
from sqlalchemy.exc import SQLAlchemyError
from app.database.models import Post, PostVote
from sqlalchemy.orm import joinedload

class PostRepository:
    @staticmethod
    async def create(db: AsyncSession, post_data: dict) -> Post:
        """
        Create a new post in the database.
        """
        try:
            post = Post(**post_data)
            db.add(post)
            await db.commit()
            await db.refresh(post)
            return post
        except SQLAlchemyError as e:
            await db.rollback()
            raise e

    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 10) -> List[Post]:
        """
        Retrieve all posts with pagination, including related category and author.
        """
        result = await db.execute(
            select(Post)
            .options(joinedload(Post.category), joinedload(Post.author))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def get_by_id(db: AsyncSession, post_id: int) -> Optional[Post]:
        """
        Retrieve a specific post by ID, including related category and author.
        """
        result = await db.execute(
            select(Post)
            .options(joinedload(Post.category), joinedload(Post.author))
            .filter(Post.id == post_id)
        )
        return result.scalars().first()

    @staticmethod
    async def get_by_user(db: AsyncSession, user_id: int) -> List[Post]:
        """
        Retrieve all posts created by a specific user, including related category and author.
        """
        result = await db.execute(
            select(Post)
            .options(joinedload(Post.category), joinedload(Post.author))
            .filter(Post.author_id == user_id)
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_posts_count(db: AsyncSession, user_id: int) -> int:
        """
        Retrieve the count of posts created by a specific user.
        """
        result = await db.execute(
            select(func.count()).filter(Post.author_id == user_id)
        )
        return result.scalar() or 0

    @staticmethod
    async def delete(db: AsyncSession, post_id: int):
        """
        Delete a specific post by ID.
        """
        try:
            post = await db.get(Post, post_id)
            if post:
                await db.delete(post)
                await db.commit()
            else:
                raise ValueError("Post not found")
        except SQLAlchemyError as e:
            await db.rollback()
            raise e

    @staticmethod
    async def search(db: AsyncSession, query: str, skip: int, limit: int) -> List[Post]:
        """
        Search for posts by title or description, including related category and author.
        """
        try:
            result = await db.execute(
                select(Post)
                .options(joinedload(Post.category), joinedload(Post.author))
                .filter(
                    (Post.title.ilike(f"%{query}%")) |
                    (Post.description.ilike(f"%{query}%"))
                )
                .offset(skip)
                .limit(limit)
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            await db.rollback()
            raise e

    @staticmethod
    async def search_by_category(db: AsyncSession, category_id: int, skip: int, limit: int) -> List[Post]:
        """
        Search for posts by category ID, including related category and author.
        """
        try:
            result = await db.execute(
                select(Post)
                .options(joinedload(Post.category), joinedload(Post.author))
                .filter(Post.category_id == category_id)
                .offset(skip)
                .limit(limit)
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            await db.rollback()
            raise e
    
    @staticmethod
    async def update_vote_counts(db: AsyncSession, post: Post, is_upvote: bool, is_new_vote: bool, is_remove: bool):
        """Update the upvotes and downvotes counts for a post."""
        if is_remove:
            if is_upvote:
                post.upvotes -= 1
            else:
                post.downvotes -= 1
        elif is_new_vote:
            if is_upvote:
                post.upvotes += 1
            else:
                post.downvotes += 1
        else:
            if is_upvote:
                post.upvotes += 1
                post.downvotes -= 1
            else:
                post.upvotes -= 1
                post.downvotes += 1

        await db.commit()
        await db.refresh(post)