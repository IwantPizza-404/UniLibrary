from typing import List, Optional
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path
from app.repositories.vote import VoteRepository
from app.repositories.user import UserRepository
from app.repositories.category import CategoryRepository
from app.schemas.post import PostCreate, PostResponse
from app.repositories.post import PostRepository
from app.core.upload import upload_file
from fastapi.concurrency import run_in_threadpool

class PostService:
    @staticmethod
    async def create(db: AsyncSession, post_data: PostCreate, file: UploadFile, author_id: int) -> PostResponse:
        """
        Create a new post with file upload.
        """
        file_url = None
        if file:
            file_url = await PostService._handle_file_upload(file)

        post_dict = post_data.dict()
        post_dict.update({
            "author_id": author_id,
            "file_url": file_url,
        })

        try:
            post = await PostRepository.create(db, post_dict)
            post_with_details = await PostRepository.get_by_id(db, post.id)
            return post_with_details
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating post: {str(e)}"
            )

    @staticmethod
    async def get_all(db: AsyncSession, skip: int, limit: int) -> List[PostResponse]:
        """
        Retrieve all posts with pagination.
        """
        posts = await PostRepository.get_all(db, skip=skip, limit=limit)
        return posts
    
    @staticmethod
    async def get_following(db: AsyncSession, user_id: int, skip: int, limit: int) -> List[PostResponse]:
        """
        Retrieve all posts created by users the current user follows.
        """
        posts = await PostRepository.get_following(db, user_id=user_id, skip=skip, limit=limit)
        return posts
    
    @staticmethod
    async def get_by_id(db: AsyncSession, post_id: int, user_id: Optional[int] = None) -> PostResponse:
        """
        Retrieve a specific post by ID and include the user's current vote if `user_id` is provided.
        """
        post = await PostRepository.get_by_id(db, post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )

        user_vote = None
        if user_id:
            vote = await VoteRepository.get_vote(db, user_id, post_id)
            if vote:
                user_vote = vote.is_upvote

        return PostResponse(
            id=post.id,
            title=post.title,
            description=post.description,
            category_id=post.category_id,
            file_url=post.file_url,
            upvotes=post.upvotes,
            downvotes=post.downvotes,
            created_at=post.created_at,
            rating_percentage=post.rating_percentage,
            user_vote=user_vote,
            category=post.category,
            author=post.author,
        )

    @staticmethod
    async def get_by_user(db: AsyncSession, username: str) -> List[PostResponse]:
        """
        Retrieve all posts created by a specific user.
        """
        user = await UserRepository.get_by_username(db, username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        posts = await PostRepository.get_by_user(db, user.id)
        return posts

    @staticmethod
    async def delete(db: AsyncSession, post_id: int, current_user: dict):
        """
        Delete a post if the user is the owner or an admin.
        """
        post = await PostRepository.get_by_id(db, post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )

        if post.author_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to delete this post"
            )

        await PostRepository.delete(db, post_id)

    @staticmethod
    async def get_file_url(db: AsyncSession, post_id: int) -> str:
        """
        Retrieve the file URL for a specific post.
        """
        post = await PostRepository.get_by_id(db, post_id)
        if not post or not post.file_url:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found in the database"
            )

        file_path = Path("static/uploads") / Path(post.file_url).name
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File not found on the server: {file_path}"
            )

        return str(file_path)

    @staticmethod
    async def search(db: AsyncSession, query: str, category_id: Optional[int] = None, sort: Optional[str] = None, skip: int = 0, limit: int = 10) -> List[PostResponse]:
        """
        Search for posts by title, description, or category.
        """
        if not query:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Search query cannot be empty"
            )
        posts = await PostRepository.search(db, query=query, category_id=category_id, sort=sort, skip=skip, limit=limit)
        return posts

    @staticmethod
    async def search_by_category(db: AsyncSession, category_id: int, skip: int = 0, limit: int = 10) -> List[PostResponse]:
        """
        Get all posts from a specific category.
        """
        posts = await PostRepository.search_by_category(db, category_id=category_id, skip=skip, limit=limit)
        return posts

    @staticmethod
    async def _handle_file_upload(file: UploadFile) -> str:
        """
        Handle file upload and return the uploaded file URL.
        """
        try:
            return await run_in_threadpool(upload_file, file)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"File upload failed: {str(e)}"
            )
    
    @staticmethod
    async def vote(db: AsyncSession, user_id: int, post_id: int, is_upvote: Optional[bool]) -> PostResponse:
        """
        Handle voting logic (upvote, downvote, or remove vote).
        """
        post = await PostRepository.get_by_id(db, post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Post not found"
            )

        existing_vote = await VoteRepository.get_vote(db, user_id, post_id)

        if is_upvote is None:
            if not existing_vote:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"You have not voted on this post"
                )
            await VoteRepository.delete_vote(db, existing_vote)
            await PostRepository.update_vote_counts(db, post, is_upvote=existing_vote.is_upvote, is_new_vote=False, is_remove=True)
        elif existing_vote and existing_vote.is_upvote == is_upvote and is_upvote is True:
            await VoteRepository.delete_vote(db, existing_vote)
            await PostRepository.update_vote_counts(db, post, is_upvote=True, is_new_vote=False, is_remove=True)
        elif existing_vote and existing_vote.is_upvote == is_upvote and is_upvote is False:
            await VoteRepository.delete_vote(db, existing_vote)
            await PostRepository.update_vote_counts(db, post, is_upvote=False, is_new_vote=False, is_remove=True)
        else:
            if not existing_vote:
                await VoteRepository.create_vote(db, user_id, post_id, is_upvote)
                await PostRepository.update_vote_counts(db, post, is_upvote=is_upvote, is_new_vote=True, is_remove=False)
            else:
                await VoteRepository.update_vote(db, existing_vote, is_upvote)
                await PostRepository.update_vote_counts(db, post, is_upvote=is_upvote, is_new_vote=False, is_remove=False)

        return await PostService.get_by_id(db, post_id, user_id)