"""Admin endpoints for kiosk access control management."""

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, select

from ..db import get_session
from ..models import User
from ..models.kiosk import Kiosk
from ..models.kiosk_access import KioskAccess, KioskAccessMode
from ..routers.auth import get_current_user
from ..services.access_control import (
    block_kiosk_access,
    grant_kiosk_access,
    revoke_kiosk_access,
)

router = APIRouter(prefix="/admin/kiosks", tags=["admin-kiosk-access"])


def require_admin(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    """Dependency to require admin role."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required",
        )
    return current_user


# Schemas
class KioskAccessModeUpdate(BaseModel):
    """Request to update kiosk access mode."""

    access_mode: str  # "public", "whitelist", "blacklist"


class GrantAccessRequest(BaseModel):
    """Request to grant access to a user."""

    user_id: int
    expires_at: datetime | None = None


class UserAccessInfo(BaseModel):
    """User access information."""

    user_id: int
    email: str
    granted: bool
    granted_at: datetime
    expires_at: datetime | None
    granted_by_admin_id: int | None


class KioskAccessListResponse(BaseModel):
    """Response for kiosk access list."""

    kiosk_id: int
    kiosk_name: str
    location: str
    access_mode: str
    is_active: bool
    authorized_users: list[UserAccessInfo]


# Endpoints


@router.get("/{kiosk_id}/access", response_model=KioskAccessListResponse)
async def get_kiosk_access_list(
    kiosk_id: int,
    session: Annotated[Session, Depends(get_session)],
    admin: Annotated[User, Depends(require_admin)],
):
    """
    Get the list of users authorized for a specific kiosk.

    Args:
        kiosk_id: Kiosk ID
        session: Database session
        admin: Admin user (authentication required)

    Returns:
        Kiosk information with list of authorized users
    """
    # Get kiosk
    kiosk = session.get(Kiosk, kiosk_id)
    if not kiosk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Kiosk not found"
        )

    # Get access list
    statement = (
        select(KioskAccess, User)
        .join(User, KioskAccess.user_id == User.id)
        .where(KioskAccess.kiosk_id == kiosk_id)
        .order_by(User.email)
    )
    results = session.exec(statement).all()

    authorized_users = [
        UserAccessInfo(
            user_id=access.user_id,
            email=user.email,
            granted=access.granted,
            granted_at=access.granted_at,
            expires_at=access.expires_at,
            granted_by_admin_id=access.granted_by_admin_id,
        )
        for access, user in results
    ]

    return KioskAccessListResponse(
        kiosk_id=kiosk.id,
        kiosk_name=kiosk.kiosk_name,
        location=kiosk.location,
        access_mode=kiosk.access_mode,
        is_active=kiosk.is_active,
        authorized_users=authorized_users,
    )


@router.patch("/{kiosk_id}/access-mode")
async def set_kiosk_access_mode(
    kiosk_id: int,
    update: KioskAccessModeUpdate,
    session: Annotated[Session, Depends(get_session)],
    admin: Annotated[User, Depends(require_admin)],
):
    """
    Change the access mode of a kiosk.

    Args:
        kiosk_id: Kiosk ID
        update: New access mode (public, whitelist, blacklist)
        session: Database session
        admin: Admin user

    Returns:
        Updated kiosk information
    """
    kiosk = session.get(Kiosk, kiosk_id)
    if not kiosk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Kiosk not found"
        )

    # Validate access mode
    if update.access_mode not in [mode.value for mode in KioskAccessMode]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid access mode. Must be one of: {[m.value for m in KioskAccessMode]}",
        )

    kiosk.access_mode = update.access_mode
    session.add(kiosk)
    session.commit()
    session.refresh(kiosk)

    return {
        "success": True,
        "message": f"Access mode changed to {update.access_mode}",
        "kiosk": {
            "id": kiosk.id,
            "kiosk_name": kiosk.kiosk_name,
            "access_mode": kiosk.access_mode,
        },
    }


@router.post("/{kiosk_id}/grant-access")
async def grant_access(
    kiosk_id: int,
    request: GrantAccessRequest,
    session: Annotated[Session, Depends(get_session)],
    admin: Annotated[User, Depends(require_admin)],
):
    """
    Grant access to a user for a specific kiosk (for whitelist mode).

    Args:
        kiosk_id: Kiosk ID
        request: User ID and optional expiration date
        session: Database session
        admin: Admin user

    Returns:
        Success message
    """
    # Verify kiosk exists
    kiosk = session.get(Kiosk, kiosk_id)
    if not kiosk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Kiosk not found"
        )

    # Verify user exists
    user = session.get(User, request.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Grant access
    access = grant_kiosk_access(
        kiosk_id=kiosk_id,
        user_id=request.user_id,
        granted_by_admin_id=admin.id,
        expires_at=request.expires_at,
        session=session,
    )

    return {
        "success": True,
        "message": f"Access granted to {user.email} for kiosk {kiosk.kiosk_name}",
        "access": {
            "user_id": access.user_id,
            "kiosk_id": access.kiosk_id,
            "granted": access.granted,
            "expires_at": access.expires_at,
        },
    }


@router.delete("/{kiosk_id}/revoke-access/{user_id}")
async def revoke_access(
    kiosk_id: int,
    user_id: int,
    session: Annotated[Session, Depends(get_session)],
    admin: Annotated[User, Depends(require_admin)],
):
    """
    Revoke access for a user to a specific kiosk.

    Args:
        kiosk_id: Kiosk ID
        user_id: User ID to revoke access from
        session: Database session
        admin: Admin user

    Returns:
        Success message
    """
    # Verify kiosk exists
    kiosk = session.get(Kiosk, kiosk_id)
    if not kiosk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Kiosk not found"
        )

    # Verify user exists
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Revoke access
    revoked = revoke_kiosk_access(kiosk_id=kiosk_id, user_id=user_id, session=session)

    if revoked:
        return {
            "success": True,
            "message": f"Access revoked for {user.email} from kiosk {kiosk.kiosk_name}",
        }
    else:
        return {
            "success": True,
            "message": f"No access found for {user.email} on kiosk {kiosk.kiosk_name}",
        }


@router.post("/{kiosk_id}/block-access")
async def block_access(
    kiosk_id: int,
    request: GrantAccessRequest,  # Reuse same schema (only user_id needed)
    session: Annotated[Session, Depends(get_session)],
    admin: Annotated[User, Depends(require_admin)],
):
    """
    Block access for a user to a specific kiosk (for blacklist mode).

    Args:
        kiosk_id: Kiosk ID
        request: User ID to block
        session: Database session
        admin: Admin user

    Returns:
        Success message
    """
    # Verify kiosk exists
    kiosk = session.get(Kiosk, kiosk_id)
    if not kiosk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Kiosk not found"
        )

    # Verify user exists
    user = session.get(User, request.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Block access
    access = block_kiosk_access(
        kiosk_id=kiosk_id,
        user_id=request.user_id,
        blocked_by_admin_id=admin.id,
        session=session,
    )

    return {
        "success": True,
        "message": f"Access blocked for {user.email} on kiosk {kiosk.kiosk_name}",
        "access": {
            "user_id": access.user_id,
            "kiosk_id": access.kiosk_id,
            "granted": access.granted,
        },
    }
