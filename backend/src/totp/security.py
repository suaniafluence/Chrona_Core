"""TOTP security controls: rate limiting, lockout, nonce blacklist.

Implements security measures compliant with kiosk spec:
- rate_limit: 5 attempts / 10min
- lockout: 15min
- replay_protection: nonce blacklist
"""

from datetime import datetime, timedelta
from typing import Optional

from sqlmodel import Session, func, select

from src.models import (
    TOTPLockout,
    TOTPNonceBlacklist,
    TOTPValidationAttempt,
)


class RateLimitExceeded(Exception):
    """Raised when rate limit is exceeded."""

    pass


class AccountLocked(Exception):
    """Raised when account is locked due to excessive failures."""

    pass


def check_rate_limit(
    db: Session,
    user_id: int,
    window_minutes: int = 10,
    max_attempts: int = 5,
) -> None:
    """Check if user has exceeded rate limit for TOTP validation.

    Args:
        db: Database session
        user_id: User ID to check
        window_minutes: Time window in minutes (default: 10)
        max_attempts: Maximum attempts in window (default: 5)

    Raises:
        RateLimitExceeded: If rate limit exceeded

    Example:
        >>> check_rate_limit(db, user_id=1)  # Raises if >5 attempts in 10min
    """
    now = datetime.utcnow()
    window_start = now - timedelta(minutes=window_minutes)

    # Count attempts in window
    attempt_count = db.execute(
        select(func.count(TOTPValidationAttempt.id)).where(
            TOTPValidationAttempt.user_id == user_id,
            TOTPValidationAttempt.attempted_at >= window_start,
        )
    ).one()

    if attempt_count >= max_attempts:
        msg = (
            f"Rate limit exceeded: {attempt_count} attempts in "
            f"{window_minutes} minutes. Maximum {max_attempts} attempts allowed."
        )
        raise RateLimitExceeded(msg)


def check_account_lockout(db: Session, user_id: int) -> None:
    """Check if user account is currently locked.

    Args:
        db: Database session
        user_id: User ID to check

    Raises:
        AccountLocked: If account is locked

    Example:
        >>> check_account_lockout(db, user_id=1)  # Raises if locked
    """
    now = datetime.utcnow()

    # Check for active lockout
    lockout = db.execute(
        select(TOTPLockout).where(
            TOTPLockout.user_id == user_id,
            TOTPLockout.is_active == True,  # noqa: E712
            TOTPLockout.locked_until > now,
        )
    ).first()

    if lockout:
        remaining_seconds = (lockout.locked_until - now).total_seconds()
        raise AccountLocked(
            f"Account locked until {lockout.locked_until.isoformat()}. "
            f"Remaining time: {int(remaining_seconds)} seconds. "
            f"Reason: {lockout.trigger_reason}"
        )


def record_validation_attempt(
    db: Session,
    user_id: int,
    is_success: bool,
    failure_reason: Optional[str] = None,
    kiosk_id: Optional[int] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    jwt_jti: Optional[str] = None,
    nonce: Optional[str] = None,
) -> TOTPValidationAttempt:
    """Record TOTP validation attempt for monitoring and rate limiting.

    Args:
        db: Database session
        user_id: User ID
        is_success: Whether validation succeeded
        failure_reason: Reason for failure (if applicable)
        kiosk_id: Kiosk ID (if applicable)
        ip_address: Source IP address
        user_agent: User agent string
        jwt_jti: JWT ID for duplication detection
        nonce: Nonce for duplication detection

    Returns:
        Created validation attempt record

    Example:
        >>> attempt = record_validation_attempt(db, user_id=1, is_success=True)
    """
    attempt = TOTPValidationAttempt(
        user_id=user_id,
        kiosk_id=kiosk_id,
        is_success=is_success,
        failure_reason=failure_reason,
        attempted_at=datetime.utcnow(),
        ip_address=ip_address,
        user_agent=user_agent,
        jwt_jti=jwt_jti,
        nonce=nonce,
    )

    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    return attempt


def trigger_lockout(
    db: Session,
    user_id: int,
    lockout_minutes: int = 15,
    trigger_reason: str = "rate_limit",
    ip_address: Optional[str] = None,
) -> TOTPLockout:
    """Trigger account lockout after excessive failures.

    Args:
        db: Database session
        user_id: User ID to lock
        lockout_minutes: Lockout duration in minutes (default: 15)
        trigger_reason: Reason for lockout
        ip_address: IP address associated with failures

    Returns:
        Created lockout record

    Example:
        >>> lockout = trigger_lockout(db, user_id=1, trigger_reason="rate_limit")
    """
    now = datetime.utcnow()
    locked_until = now + timedelta(minutes=lockout_minutes)

    # Count recent failed attempts
    window_start = now - timedelta(minutes=10)
    failed_count = db.execute(
        select(func.count(TOTPValidationAttempt.id)).where(
            TOTPValidationAttempt.user_id == user_id,
            TOTPValidationAttempt.is_success == False,  # noqa: E712
            TOTPValidationAttempt.attempted_at >= window_start,
        )
    ).one()

    # Deactivate any existing lockouts for this user
    existing_lockouts = db.execute(
        select(TOTPLockout).where(
            TOTPLockout.user_id == user_id, TOTPLockout.is_active == True  # noqa: E712
        )
    ).all()
    for lockout in existing_lockouts:
        lockout.is_active = False
        lockout.released_at = now
        lockout.released_by = "system"

    # Create new lockout
    lockout = TOTPLockout(
        user_id=user_id,
        locked_at=now,
        locked_until=locked_until,
        failed_attempts_count=failed_count,
        trigger_reason=trigger_reason,
        is_active=True,
        ip_address=ip_address,
    )

    db.add(lockout)
    db.commit()
    db.refresh(lockout)

    return lockout


def is_nonce_blacklisted(db: Session, nonce: str) -> bool:
    """Check if nonce is blacklisted (already used).

    Args:
        db: Database session
        nonce: Nonce to check

    Returns:
        True if nonce is blacklisted (already used)

    Example:
        >>> is_blacklisted = is_nonce_blacklisted(db, "abc123")
    """
    exists = db.execute(
        select(TOTPNonceBlacklist).where(TOTPNonceBlacklist.nonce == nonce)
    ).first()

    return exists is not None


def blacklist_nonce(
    db: Session,
    nonce: str,
    user_id: int,
    jwt_jti: str,
    jwt_expires_at: datetime,
    kiosk_id: Optional[int] = None,
    ip_address: Optional[str] = None,
) -> TOTPNonceBlacklist:
    """Add nonce to blacklist to prevent replay attacks.

    Args:
        db: Database session
        nonce: Nonce to blacklist
        user_id: User ID
        jwt_jti: JWT ID
        jwt_expires_at: JWT expiration timestamp
        kiosk_id: Kiosk ID that consumed nonce
        ip_address: IP address

    Returns:
        Created blacklist record

    Raises:
        ValueError: If nonce already blacklisted

    Example:
        >>> entry = blacklist_nonce(db, "abc123", user_id=1, jwt_jti="xyz")
    """
    # Check if already blacklisted
    if is_nonce_blacklisted(db, nonce):
        raise ValueError(f"Nonce {nonce} already blacklisted (replay attack detected)")

    entry = TOTPNonceBlacklist(
        nonce=nonce,
        user_id=user_id,
        kiosk_id=kiosk_id,
        jwt_jti=jwt_jti,
        jwt_expires_at=jwt_expires_at,
        consumed_at=datetime.utcnow(),
        consumed_from_ip=ip_address,
    )

    db.add(entry)
    db.commit()
    db.refresh(entry)

    return entry


def cleanup_expired_nonces(db: Session, batch_size: int = 1000) -> int:
    """Clean up expired nonces from blacklist (maintenance task).

    Args:
        db: Database session
        batch_size: Maximum number of records to delete (default: 1000)

    Returns:
        Number of deleted records

    Example:
        >>> deleted = cleanup_expired_nonces(db)
        >>> print(f"Deleted {deleted} expired nonces")
    """
    now = datetime.utcnow()

    # Find expired nonces (JWT expiration + grace period)
    grace_period_hours = 24
    cutoff = now - timedelta(hours=grace_period_hours)

    expired = db.execute(
        select(TOTPNonceBlacklist)
        .where(TOTPNonceBlacklist.jwt_expires_at < cutoff)
        .limit(batch_size)
    ).all()

    count = len(expired)
    for entry in expired:
        db.delete(entry)

    db.commit()

    return count


def get_failed_attempts_count(
    db: Session, user_id: int, window_minutes: int = 10
) -> int:
    """Get count of failed attempts in time window.

    Args:
        db: Database session
        user_id: User ID
        window_minutes: Time window in minutes (default: 10)

    Returns:
        Count of failed attempts

    Example:
        >>> count = get_failed_attempts_count(db, user_id=1)
    """
    now = datetime.utcnow()
    window_start = now - timedelta(minutes=window_minutes)

    count = db.execute(
        select(func.count(TOTPValidationAttempt.id)).where(
            TOTPValidationAttempt.user_id == user_id,
            TOTPValidationAttempt.is_success == False,  # noqa: E712
            TOTPValidationAttempt.attempted_at >= window_start,
        )
    ).one()

    return count


def should_trigger_alert(
    db: Session, user_id: int, window_minutes: int = 10, threshold: int = 3
) -> bool:
    """Check if failed attempts exceed alert threshold.

    Compliant with kiosk spec:
    - monitoring.alert_threshold: 3 failed / 10min

    Args:
        db: Database session
        user_id: User ID
        window_minutes: Time window in minutes (default: 10)
        threshold: Alert threshold (default: 3)

    Returns:
        True if alert should be triggered

    Example:
        >>> if should_trigger_alert(db, user_id=1):
        ...     send_security_alert()
    """
    failed_count = get_failed_attempts_count(db, user_id, window_minutes)
    return failed_count >= threshold
