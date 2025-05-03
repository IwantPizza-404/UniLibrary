from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.category import CategoryRepository
from app.schemas.category import CategoryResponse

class CategoryService:
    @staticmethod
    async def get_all(db: AsyncSession) -> List[CategoryResponse]:
        """ Get all categories """
        return await CategoryRepository.get_all(db)