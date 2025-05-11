from pydantic import BaseModel, EmailStr, validator
from app.core.hashing import get_password_hash
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

    @validator("password", pre=True)
    def hash_password(cls, value: str) -> str:
        """Hash the password before saving"""
        return get_password_hash(value)

class UserUpdate(UserBase):
    full_name: str

class UserResponse(UserBase):
    id: int
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True

class UserProfile(UserBase):
    id: int
    followers_count: int
    following_count: int
    upvotes_count: int
    downvotes_count: int
    uploads_count: int
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True