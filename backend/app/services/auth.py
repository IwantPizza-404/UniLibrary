from fastapi import Response, Request, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user import UserRepository
from app.repositories.auth import AuthRepository
from app.core.jwt import create_access_token, create_refresh_token, verify_refresh_token
from app.core.hashing import verify_password


class AuthService:
    GRACE_PERIOD_HOURS = 1  # Grace period for token reuse detection

    @staticmethod
    async def login(db: AsyncSession, form_data, request: Request, response: Response):
        """ Log in a user and issue JWT tokens """
        user = await UserRepository.get_by_email_or_username(db, form_data.username)
        if not user or not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        # Create new tokens
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

        return {"access_token": access_token, "token_type": "bearer"}

    @staticmethod
    async def refresh(db: AsyncSession, request: Request, response: Response):
        """ Refresh the access token using a refresh token """
        # Get refresh token from cookie
        refresh_token = request.cookies.get("refresh_token")
        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing refresh token"
            )

        try:
            # Verify refresh token
            user_id = verify_refresh_token(refresh_token)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        try:
            # Get and lock the current session
            current_session = await AuthRepository.get_and_lock_session(db, refresh_token)
            
            if current_session:
                # Valid session found - proceed with token rotation
                try:
                    # Generate new tokens
                    new_access_token = create_access_token(user_id)
                    new_refresh_token = create_refresh_token(user_id)

                    # First revoke the old token
                    if not await AuthRepository.revoke_refresh_token(db, refresh_token):
                        raise HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Token already used"
                        )

                    # Then save the new token
                    await AuthRepository.save_refresh_token(
                        db, user_id, new_refresh_token,
                        request.headers.get("Device-Id", "unknown_device"),
                        request.client.host,
                        request.headers.get("User-Agent")
                    )

                    # Set new refresh token cookie
                    response.set_cookie(
                        key="refresh_token",
                        value=new_refresh_token,
                        httponly=True,
                        secure=False,
                        samesite="Lax",
                        path="/"
                    )

                    return {"access_token": new_access_token, "token_type": "bearer"}
                except Exception as e:
                    # If anything fails during token rotation, revoke the current token
                    await AuthRepository.revoke_refresh_token(db, refresh_token)
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Failed to refresh token"
                    )
            else:
                # Check if token was recently used (within grace period)
                recent_session = await AuthRepository.get_recent_session_by_token(
                    db, 
                    refresh_token, 
                    AuthService.GRACE_PERIOD_HOURS
                )
                
                if recent_session:
                    # Token reuse detected - revoke all sessions for security
                    await AuthRepository.revoke_all_user_sessions(db, user_id)
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Security alert: Token reuse detected. Please log in again."
                    )
                
                # Token is invalid and not recently used
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired refresh token"
                )
        except Exception as e:
            # Handle any database errors
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process refresh token"
            )

    @staticmethod
    async def logout(db: AsyncSession, request: Request, response: Response):
        """ Log out the current user by invalidating their refresh token """
        refresh_token = request.cookies.get("refresh_token")
        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing refresh token"
            )

        # Revoke the token
        await AuthRepository.revoke_refresh_token(db, refresh_token)
        
        # Clear the cookie
        response.delete_cookie(
            key="refresh_token",
            path="/",
            httponly=True,
            secure=False,
            samesite="Lax"
        )

        return {"message": "Successfully logged out"}