from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.models import User
from app.schemas.user import UserUpdate


class UserRepository:
    @staticmethod
    async def create(db: AsyncSession, user_data: dict) -> User:
        """Create a new user in the database."""
        # Rename 'password' to 'hashed_password' if necessary
        if "password" in user_data:
            user_data["hashed_password"] = user_data.pop("password")

        db_user = User(**user_data)
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user

    @staticmethod
    async def delete(db: AsyncSession, user_id: int):
        """Delete a user by their ID."""
        result = await db.execute(select(User).filter(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise RuntimeError("User not found")
        await db.delete(user)
        await db.commit()

    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        """Retrieve a user by their ID."""
        result = await db.execute(select(User).filter(User.id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_email_or_username(db: AsyncSession, username_or_email: str) -> Optional[User]:
        """Retrieve a user by their email or username."""
        result = await db.execute(
            select(User).filter(
                (User.username == username_or_email) | (User.email == username_or_email)
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def update_profile(db: AsyncSession, current_user: User, user_data: UserUpdate) -> User:
        """Update the profile of the current user."""
        for key, value in user_data.dict(exclude_unset=True).items():
            setattr(current_user, key, value)
        await db.commit()
        await db.refresh(current_user)
        return current_user