from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.category import CategoryResponse
from app.services.category import CategoryService
from app.database.session import get_db
from app.core.deps import get_current_user

router = APIRouter()

@router.get("/", response_model=List[CategoryResponse])
async def get_categories(
    db: AsyncSession = Depends(get_db),
):
    """ Get all categories """
    return await CategoryService.get_all(db)