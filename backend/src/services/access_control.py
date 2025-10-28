"""Access control service for kiosk permissions."""

from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from ..models.kiosk import Kiosk
from ..models.kiosk_access import KioskAccess, KioskAccessMode


async def check_kiosk_access(
    user_id: int, kiosk_id: int, session: AsyncSession
) -> tuple[bool, str]:
    """
    Check if a user has access to a specific kiosk.

    Args:
        user_id: User ID to check
        kiosk_id: Kiosk ID to check
        session: Database session

    Returns:
        Tuple of (is_authorized: bool, reason: str)

    Examples:
        >>> authorized, reason = await check_kiosk_access(5, 1, session)
        >>> if not authorized:
        ...     raise HTTPException(403, reason)
    """
    # Get kiosk
    kiosk = await session.get(Kiosk, kiosk_id)
    if not kiosk:
        return False, "Kiosk inexistant"

    # Check if kiosk is active
    if not kiosk.is_active:
        return False, "Kiosk désactivé"

    # PUBLIC mode: everyone has access
    if kiosk.access_mode == KioskAccessMode.PUBLIC:
        return True, "Accès public"

    # WHITELIST mode: only authorized users
    if kiosk.access_mode == KioskAccessMode.WHITELIST:
        statement = (
            select(KioskAccess)
            .where(KioskAccess.kiosk_id == kiosk_id)
            .where(KioskAccess.user_id == user_id)
            .where(KioskAccess.granted == True)  # noqa: E712
        )
        result = await session.execute(statement)
        access = result.first()

        if not access:
            return False, "Accès non autorisé pour ce kiosk"

        # Check expiration
        if access.expires_at and datetime.utcnow() > access.expires_at:
            return False, "Accès expiré"

        return True, "Accès autorisé (whitelist)"

    # BLACKLIST mode: everyone except blocked users
    if kiosk.access_mode == KioskAccessMode.BLACKLIST:
        statement = (
            select(KioskAccess)
            .where(KioskAccess.kiosk_id == kiosk_id)
            .where(KioskAccess.user_id == user_id)
            .where(KioskAccess.granted == False)  # noqa: E712
        )
        result = await session.execute(statement)
        access = result.first()

        if access:
            return False, "Accès bloqué pour ce kiosk"

        return True, "Accès autorisé (non bloqué)"

    # Unknown access mode
    return False, f"Mode d'accès inconnu: {kiosk.access_mode}"


async def grant_kiosk_access(
    kiosk_id: int,
    user_id: int,
    granted_by_admin_id: int,
    expires_at: datetime | None,
    session: AsyncSession,
) -> KioskAccess:
    """
    Grant access to a user for a specific kiosk.

    Args:
        kiosk_id: Kiosk ID
        user_id: User ID to grant access to
        granted_by_admin_id: Admin who granted the access
        expires_at: Optional expiration date
        session: Database session

    Returns:
        KioskAccess object
    """
    # Check if access already exists
    statement = (
        select(KioskAccess)
        .where(KioskAccess.kiosk_id == kiosk_id)
        .where(KioskAccess.user_id == user_id)
    )
    result = await session.execute(statement)
    access = result.first()

    if access:
        # Update existing access
        access.granted = True
        access.granted_by_admin_id = granted_by_admin_id
        access.granted_at = datetime.utcnow()
        access.expires_at = expires_at
    else:
        # Create new access
        access = KioskAccess(
            kiosk_id=kiosk_id,
            user_id=user_id,
            granted=True,
            granted_by_admin_id=granted_by_admin_id,
            expires_at=expires_at,
        )
        session.add(access)

    await session.commit()
    await session.refresh(access)
    return access


async def revoke_kiosk_access(
    kiosk_id: int, user_id: int, session: AsyncSession
) -> bool:
    """
    Revoke access for a user to a specific kiosk.

    Args:
        kiosk_id: Kiosk ID
        user_id: User ID to revoke access from
        session: Database session

    Returns:
        True if access was revoked, False if no access existed
    """
    statement = (
        select(KioskAccess)
        .where(KioskAccess.kiosk_id == kiosk_id)
        .where(KioskAccess.user_id == user_id)
    )
    result = await session.execute(statement)
    access = result.first()

    if access:
        await session.delete(access)
        await session.commit()
        return True

    return False


async def block_kiosk_access(
    kiosk_id: int,
    user_id: int,
    blocked_by_admin_id: int,
    session: AsyncSession,
) -> KioskAccess:
    """
    Block access to a user for a specific kiosk (for BLACKLIST mode).

    Args:
        kiosk_id: Kiosk ID
        user_id: User ID to block
        blocked_by_admin_id: Admin who blocked the access
        session: Database session

    Returns:
        KioskAccess object with granted=False
    """
    # Check if access already exists
    statement = (
        select(KioskAccess)
        .where(KioskAccess.kiosk_id == kiosk_id)
        .where(KioskAccess.user_id == user_id)
    )
    result = await session.execute(statement)
    access = result.first()

    if access:
        # Update to blocked
        access.granted = False
        access.granted_by_admin_id = blocked_by_admin_id
        access.granted_at = datetime.utcnow()
    else:
        # Create new block
        access = KioskAccess(
            kiosk_id=kiosk_id,
            user_id=user_id,
            granted=False,
            granted_by_admin_id=blocked_by_admin_id,
        )
        session.add(access)

    await session.commit()
    await session.refresh(access)
    return access
