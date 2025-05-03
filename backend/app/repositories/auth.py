from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.models import UserSession
from app.core.config import settings


class AuthRepository:
    @staticmethod
    async def save_refresh_token(
        db: AsyncSession, user_id: int, token: str, device_id: str, ip: str, user_agent: str
    ):
        """ Save a refresh token in the database """
        db_token = UserSession(
            user_id=user_id,
            refresh_token=token,
            device_id=device_id,
            ip_address=ip,
            user_agent=user_agent,
            expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )
        db.add(db_token)
        await db.commit()

    @staticmethod
    async def revoke_refresh_token(db: AsyncSession, token: str):
        """ Revoke a refresh token """
        result = await db.execute(
            select(UserSession).filter(UserSession.refresh_token == token)
        )
        session = result.scalar_one_or_none()
        if session:
            session.is_revoked = True
            await db.commit()

    @staticmethod
    async def get_session_by_token(db: AsyncSession, token: str) -> UserSession:
        """ Retrieve a session by its refresh token """
        result = await db.execute(
            select(UserSession).filter(
                UserSession.refresh_token == token,
                UserSession.is_revoked == False,
                UserSession.expires_at > datetime.now(timezone.utc),
            )
        )
        return result.scalar_one_or_none()