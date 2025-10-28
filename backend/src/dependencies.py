"""Dependency injection functions for FastAPI routes.

Central location for common dependencies used across the application.
"""

from typing import Annotated, Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.db import get_session
from src.models.user import User
from src.security import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> User:
    """Get current authenticated user from JWT token.

    Args:
        token: JWT access token from Authorization header
        session: Database session

    Returns:
        User object if token is valid

    Raises:
        HTTPException 401: If token is invalid or user not found
    """
    payload = decode_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_token"
        )
    user_id = int(payload["sub"])
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="user_not_found"
        )
    return user


def require_roles(*roles: str) -> Callable[[User], User]:
    """Dependency to check if user has required roles.

    Args:
        *roles: Allowed roles (e.g., "admin", "user")

    Returns:
        Async function that validates user role
    """
    async def _dep(current: Annotated[User, Depends(get_current_user)]) -> User:
        if roles and current.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="forbidden"
            )
        return current

    return _dep
