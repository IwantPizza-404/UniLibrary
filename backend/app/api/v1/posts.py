from typing import List
from fastapi import APIRouter, Depends, Query, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.post import PostCreate, PostResponse, PostVote
from app.services.post import PostService
from app.database.session import get_db
from app.core.deps import get_current_user, get_current_user_optional

router = APIRouter()

@router.post("/upload", response_model=PostResponse)
async def create_post(
    title: str = Form(...),
    description: str = Form(...),
    category_id: int = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    post_data = PostCreate(title=title, description=description, category_id=category_id)
    return await PostService.create(db, post_data, file, author_id=current_user.id)

@router.get("/", response_model=List[PostResponse])
async def get_posts(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
):
    return await PostService.get_all(db, skip=skip, limit=limit)

@router.get("/search", response_model=List[PostResponse])
async def search_posts(
    q: str = Query(..., min_length=1, description="Search query"),
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
):
    """ Search for posts by title or description """
    return await PostService.search(db, query=q, skip=skip, limit=limit)

@router.get("/search/category", response_model=List[PostResponse])
async def search_posts_by_category(
    category_id: int = Query(..., description="Category ID"),
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
):
    """ Search for posts by category ID """
    return await PostService.search_by_category(db, category_id=category_id, skip=skip, limit=limit)

@router.get("/{id}", response_model=PostResponse)
async def get_post(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user_optional),  # Use optional authentication
):
    """
    Get a post by ID and include the user's current vote if authenticated.
    """
    user_id = current_user.id if current_user else None  # Pass user ID if authenticated
    return await PostService.get_by_id(db, id, user_id=user_id)

@router.get("/user/{user_id}", response_model=List[PostResponse])
async def get_user_posts(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await PostService.get_by_user(db, user_id)

@router.delete("/{id}", response_model=dict)
async def delete_post(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    await PostService.delete(db, id, current_user)
    return {"message": "Post deleted successfully"}

@router.get("/{id}/download")
async def download_post_file(
    id: int,
    db: AsyncSession = Depends(get_db),
):
    file_url = await PostService.get_file_url(db, id)
    return FileResponse(file_url, media_type="application/octet-stream", filename=file_url.split("/")[-1])

@router.post("/{post_id}/vote", response_model=PostResponse)
async def vote_post(
    post_id: int,
    vote_data: PostVote,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Vote on a post (upvote, downvote, or remove vote).
    - `is_upvote`: True for upvote, False for downvote, None to remove vote.
    """
    return await PostService.vote(db, current_user.id, post_id, vote_data.is_upvote)
