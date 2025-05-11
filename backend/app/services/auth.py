from fastapi import Response, Request, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user import UserRepository
from app.repositories.auth import AuthRepository
from app.core.jwt import create_access_token, create_refresh_token, verify_refresh_token
from app.core.hashing import verify_password


class AuthService:
    @staticmethod
    async def login(db: AsyncSession, form_data, request: Request, response: Response):
        """ Log in a user and issue JWT tokens """
        user = await UserRepository.get_by_email_or_username(db, form_data.username)
        if not user or not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        access_token = create_access_token(str(user.id))
        refresh_token = create_refresh_token(str(user.id))

        # Save refresh token in the database
        await AuthRepository.save_refresh_token(
            db, user.id, refresh_token,
            request.headers.get("Device-Id", "unknown_device"),
            request.client.host,
            request.headers.get("User-Agent")
        )

        # Set refresh token as an HTTP-only cookie
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=False,  # Set to True in production
            samesite="Lax",
            path="/"
        )

        # Only return the access_token
        return {"access_token": access_token, "token_type": "bearer"}

    @staticmethod
    async def refresh(db: AsyncSession, request: Request, response: Response):
        """ Refresh the access token using a refresh token """
        refresh_token = request.cookies.get("refresh_token")
        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing refresh token"
            )

        try:
            user_id = verify_refresh_token(refresh_token)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e)
            )

        session = await AuthRepository.get_session_by_token(db, refresh_token)
        if not session or session.is_revoked:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token"
            )

        # Generate a new access token
        new_access_token = create_access_token(user_id)

        # Optionally rotate the refresh token
        new_refresh_token = create_refresh_token(user_id)
        await AuthRepository.revoke_refresh_token(db, refresh_token)
        await AuthRepository.save_refresh_token(
            db, user_id, new_refresh_token,
            request.headers.get("Device-Id", "unknown_device"),
            request.client.host,
            request.headers.get("User-Agent")
        )

        # Set the new refresh token as an HTTP-only cookie
        response.set_cookie(
            key="refresh_token",
            value=new_refresh_token,
            httponly=True,
            secure=False,  # Set to True in production
            samesite="Lax",
            path="/"
        )

        # Only return the access_token
        return {"access_token": new_access_token, "token_type": "bearer"}

    @staticmethod
    async def logout(db: AsyncSession, request: Request, response: Response):
        """ Log out the current user by invalidating their refresh token """
        refresh_token = request.cookies.get("refresh_token")
        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing refresh token"
            )

        await AuthRepository.revoke_refresh_token(db, refresh_token)
        response.delete_cookie("refresh_token")

        return {"message": "Successfully logged out"}