from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

class PostVote(BaseModel):
    is_upvote: Optional[bool]

class PostBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., max_length=500)
    category_id: int = Field(..., gt=0)

class PostCreate(PostBase):
    pass

class CategorySummary(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class AuthorSummary(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True

class PostResponse(PostBase):
    id: int
    file_url: str
    created_at: datetime
    upvotes: int
    downvotes: int
    rating_percentage: float
    user_vote: Optional[bool] = None
    category: CategorySummary
    author: AuthorSummary

    class Config:
        from_attributes = True