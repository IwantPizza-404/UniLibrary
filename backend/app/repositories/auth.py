from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy import update
from app.database.models import UserSession
from app.core.config import settings


class AuthRepository:
    @staticmethod
    async def save_refresh_token(
        db: AsyncSession, user_id: int, token: str, device_id: str, ip: str, user_agent: str
    ):
        """ Save a refresh token in the database """
        try:
            db_token = UserSession(
                user_id=user_id,
                refresh_token=token,
                device_id=device_id,
                ip_address=ip,
                user_agent=user_agent,
                expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
            )
            db.add(db_token)
            await db.commit()
            return db_token
        except IntegrityError:
            await db.rollback()
            raise ValueError("Failed to save refresh token")

    @staticmethod
    async def get_and_lock_session(db: AsyncSession, token: str) -> UserSession:
        """ Get a session with row-level lock for token rotation """
        try:
            # Use SELECT FOR UPDATE to lock the row
            result = await db.execute(
                select(UserSession)
                .filter(
                    UserSession.refresh_token == token,
                    UserSession.is_revoked == False,
                    UserSession.expires_at > datetime.now(timezone.utc)
                )
                .with_for_update()
            )
            session = result.scalar_one_or_none()
            
            if session:
                # Update last used timestamp
                session.last_used_at = datetime.now(timezone.utc)
                await db.commit()
            
            return session
        except Exception:
            await db.rollback()
            raise ValueError("Failed to get session")

    @staticmethod
    async def revoke_refresh_token(db: AsyncSession, token: str):
        """ Revoke a refresh token """
        try:
            # Use UPDATE with row-level lock
            result = await db.execute(
                update(UserSession)
                .where(
                    UserSession.refresh_token == token,
                    UserSession.is_revoked == False
                )
                .values(
                    is_revoked=True,
                    revoked_at=datetime.now(timezone.utc)
                )
                .execution_options(synchronize_session="fetch")
            )
            await db.commit()
            return result.rowcount > 0
        except Exception:
            await db.rollback()
            raise ValueError("Failed to revoke refresh token")

    @staticmethod
    async def get_recent_session_by_token(
        db: AsyncSession, token: str, grace_period_hours: int
    ) -> UserSession:
        """ Check if a token was used recently """
        try:
            grace_period_start = datetime.now(timezone.utc) - timedelta(hours=grace_period_hours)
            result = await db.execute(
                select(UserSession).filter(
                    UserSession.refresh_token == token,
                    UserSession.last_used_at >= grace_period_start
                )
            )
            return result.scalar_one_or_none()
        except Exception:
            await db.rollback()
            raise ValueError("Failed to check recent session")

    @staticmethod
    async def revoke_all_user_sessions(db: AsyncSession, user_id: int):
        """ Revoke all sessions for a user """
        try:
            # Use UPDATE with row-level lock
            result = await db.execute(
                update(UserSession)
                .where(
                    UserSession.user_id == user_id,
                    UserSession.is_revoked == False
                )
                .values(
                    is_revoked=True,
                    revoked_at=datetime.now(timezone.utc)
                )
                .execution_options(synchronize_session="fetch")
            )
            await db.commit()
            return result.rowcount
        except Exception:
            await db.rollback()
            raise ValueError("Failed to revoke user sessions")