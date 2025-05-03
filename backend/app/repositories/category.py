from typing import List
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import Category

class CategoryRepository:
    @staticmethod
    async def get_all(db: AsyncSession) -> List[Category]:
        """ Retrieve all categories """
        result = await db.execute(select(Category))
        return result.scalars().all()

    @staticmethod
    async def get_by_id(db: AsyncSession, category_id: int) -> Category:
        """ Retrieve a category by ID """
        return await db.get(Category, category_id)