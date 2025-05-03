from typing import List, Optional
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path
from app.repositories.vote import VoteRepository
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
        # Handle file upload
        file_url = None
        if file:
            file_url = await PostService._handle_file_upload(file)

        # Prepare post data
        post_dict = post_data.dict()
        post_dict.update({
            "author_id": author_id,
            "file_url": file_url,
        })

        # Save post to the database
        try:
            return await PostRepository.create(db, post_dict)
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
        return await PostRepository.get_all(db, skip=skip, limit=limit)

    @staticmethod
    async def get_by_id(db: AsyncSession, post_id: int, user_id: Optional[int] = None) -> PostResponse:
        """
        Retrieve a specific post by ID and include the user's current vote if `user_id` is provided.
        """
        # Fetch the post
        post = await PostRepository.get_by_id(db, post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )

        # Fetch the user's current vote if `user_id` is provided
        user_vote = None
        if user_id:
            vote = await VoteRepository.get_vote(db, user_id, post_id)
            if vote:
                user_vote = vote.is_upvote

        return PostResponse(
            id=post.id,
            title=post.title,
            description=post.description,
            author_id=post.author_id,
            file_url=post.file_url,
            upvotes=post.upvotes,
            downvotes=post.downvotes,
            category_id=post.category_id,
            created_at=post.created_at,
            user_vote=user_vote,
            rating_percentage=post.rating_percentage,
        )

    @staticmethod
    async def get_by_user(db: AsyncSession, user_id: int) -> List[PostResponse]:
        """
        Retrieve all posts created by a specific user.
        """
        return await PostRepository.get_by_user(db, user_id)

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

        # Check if the user is the owner of the post
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
        # Retrieve the post from the database
        post = await PostRepository.get_by_id(db, post_id)
        if not post or not post.file_url:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found in the database"
            )

        # Map the URL path to the file system path
        file_path = Path("static/uploads") / Path(post.file_url).name
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File not found on the server: {file_path}"
            )

        # Return the file system path for FileResponse
        return str(file_path)

    @staticmethod
    async def search(db: AsyncSession, query: str, skip: int, limit: int) -> List[PostResponse]:
        """
        Search for posts by title, description, or category.
        """
        if not query:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Search query cannot be empty"
            )
        return await PostRepository.search(db, query=query, skip=skip, limit=limit)

    @staticmethod
    async def search_by_category(db: AsyncSession, category_id: int, skip: int, limit: int) -> List[PostResponse]:
        """
        Search for posts by category ID.
        """
        return await PostRepository.search_by_category(db, category_id=category_id, skip=skip, limit=limit)

    @staticmethod
    async def _handle_file_upload(file: UploadFile) -> str:
        """
        Handle file upload and return the uploaded file URL.
        """
        try:
            # Run the synchronous file upload function in a thread pool
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
        - `is_upvote`: True for upvote, False for downvote, None to remove vote.
        """
        # Check if the post exists
        post = await PostRepository.get_by_id(db, post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Post not found"
            )

        # Check if the user has already voted
        existing_vote = await VoteRepository.get_vote(db, user_id, post_id)

        # If `is_upvote` is None, the user wants to remove their vote
        if is_upvote is None:
            if not existing_vote:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"You have not voted on this post"
                )
            await VoteRepository.delete_vote(db, existing_vote)
            await PostRepository.update_vote_counts(db, post, is_upvote=existing_vote.is_upvote, is_new_vote=False, is_remove=True)
            return post

        # If the user has already upvoted and clicks Upvote again, remove the vote
        if existing_vote and existing_vote.is_upvote == is_upvote and is_upvote is True:
            await VoteRepository.delete_vote(db, existing_vote)
            await PostRepository.update_vote_counts(db, post, is_upvote=True, is_new_vote=False, is_remove=True)
            return post

        # If the user has already downvoted and clicks Downvote again, remove the vote
        if existing_vote and existing_vote.is_upvote == is_upvote and is_upvote is False:
            await VoteRepository.delete_vote(db, existing_vote)
            await PostRepository.update_vote_counts(db, post, is_upvote=False, is_new_vote=False, is_remove=True)
            return post

        # Create or update the vote
        if not existing_vote:
            await VoteRepository.create_vote(db, user_id, post_id, is_upvote)
            await PostRepository.update_vote_counts(db, post, is_upvote=is_upvote, is_new_vote=True, is_remove=False)
        else:
            await VoteRepository.update_vote(db, existing_vote, is_upvote)
            await PostRepository.update_vote_counts(db, post, is_upvote=is_upvote, is_new_vote=False, is_remove=False)

        # Return the updated post with the user's vote
        return await PostService.get_by_id(db, post_id, user_id)