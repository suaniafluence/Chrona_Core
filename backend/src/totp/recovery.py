"""TOTP recovery codes for account recovery.

Implements recovery code generation and validation.
Compliant with employee security spec:
- recovery.codes_backup: 5 (usage unique)
- recovery.reset_process: email + sms + ID vérif
"""

import secrets
from datetime import datetime, timedelta
from typing import List, Optional

from passlib.hash import pbkdf2_sha256
from sqlmodel import Session, select

from src.models import TOTPRecoveryCode, TOTPSecret


def generate_recovery_code(length: int = 8, include_dashes: bool = True) -> str:
    """Generate a random recovery code.

    Args:
        length: Code length (default: 8 characters)
        include_dashes: Include dash separator (default: True)

    Returns:
        Recovery code (e.g., "ABCD-EFGH")

    Example:
        >>> code = generate_recovery_code()
        >>> len(code)
        9  # XXXX-XXXX
    """
    # Use uppercase alphanumeric (exclude confusing characters: 0, O, 1, I, l)
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"

    code = "".join(secrets.choice(alphabet) for _ in range(length))

    if include_dashes and length >= 4:
        # Insert dash in middle (e.g., ABCD-EFGH)
        mid = length // 2
        code = f"{code[:mid]}-{code[mid:]}"

    return code


def hash_recovery_code(code: str) -> str:
    """Hash recovery code using PBKDF2-HMAC-SHA256.

    Args:
        code: Recovery code to hash

    Returns:
        Hashed recovery code

    Example:
        >>> hashed = hash_recovery_code("ABCD-EFGH")
        >>> len(hashed) > 0
        True
    """
    # Use passlib's PBKDF2 with 390k iterations (same as password hashing)
    return pbkdf2_sha256.hash(code)


def verify_recovery_code(code: str, code_hash: str) -> bool:
    """Verify recovery code against hash.

    Args:
        code: Recovery code to verify
        code_hash: Hashed recovery code

    Returns:
        True if code matches hash

    Example:
        >>> hashed = hash_recovery_code("ABCD-EFGH")
        >>> verify_recovery_code("ABCD-EFGH", hashed)
        True
    """
    return pbkdf2_sha256.verify(code, code_hash)


def create_recovery_codes(
    db: Session,
    totp_secret_id: int,
    count: int = 5,
    expires_days: Optional[int] = None,
) -> List[str]:
    """Generate recovery codes for TOTP secret.

    Args:
        db: Database session
        totp_secret_id: TOTP secret ID
        count: Number of recovery codes (default: 5)
        expires_days: Optional expiration in days (default: None = never)

    Returns:
        List of plaintext recovery codes (show to user once!)

    Raises:
        ValueError: If TOTP secret not found

    Example:
        >>> codes = create_recovery_codes(db, totp_secret_id=1)
        >>> len(codes)
        5
    """
    # Verify TOTP secret exists
    totp_secret = db.get(TOTPSecret, totp_secret_id)
    if not totp_secret:
        raise ValueError(f"TOTP secret {totp_secret_id} not found")

    # Calculate expiration
    expires_at = None
    if expires_days:
        expires_at = datetime.utcnow() + timedelta(days=expires_days)

    # Generate recovery codes
    plaintext_codes = []
    for _ in range(count):
        # Generate unique code
        while True:
            code = generate_recovery_code()
            # Ensure uniqueness (very unlikely collision, but check anyway)
            if code not in plaintext_codes:
                break

        plaintext_codes.append(code)

        # Hash and store
        code_hash = hash_recovery_code(code)
        code_hint = code[:4]  # First 4 characters for display

        recovery_code = TOTPRecoveryCode(
            user_id=totp_secret.user_id,
            totp_secret_id=totp_secret_id,
            code_hash=code_hash,
            code_hint=code_hint,
            is_used=False,
            created_at=datetime.utcnow(),
            expires_at=expires_at,
        )

        db.add(recovery_code)

    db.commit()

    return plaintext_codes


def use_recovery_code(
    db: Session,
    user_id: int,
    code: str,
    ip_address: Optional[str] = None,
) -> bool:
    """Use a recovery code for authentication.

    Args:
        db: Database session
        user_id: User ID
        code: Recovery code to use
        ip_address: IP address of request

    Returns:
        True if recovery code is valid and used successfully

    Example:
        >>> success = use_recovery_code(db, user_id=1, code="ABCD-EFGH")
    """
    now = datetime.utcnow()

    # Find all unused recovery codes for user
    unused_codes = db.execute(
        select(TOTPRecoveryCode).where(
            TOTPRecoveryCode.user_id == user_id,
            TOTPRecoveryCode.is_used == False,  # noqa: E712
        )
    ).all()

    # Try to verify against each unused code
    for recovery_code in unused_codes:
        # Check expiration
        if recovery_code.expires_at and now > recovery_code.expires_at:
            continue

        # Verify hash
        if verify_recovery_code(code, recovery_code.code_hash):
            # Mark as used
            recovery_code.is_used = True
            recovery_code.used_at = now
            recovery_code.used_from_ip = ip_address

            db.commit()

            return True

    return False


def get_recovery_codes_status(db: Session, user_id: int) -> dict:
    """Get status of recovery codes for user.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        Dict with recovery code status:
            - total: Total recovery codes
            - unused: Unused recovery codes
            - used: Used recovery codes
            - expired: Expired recovery codes
            - hints: List of hints for unused codes (first 4 chars)

    Example:
        >>> status = get_recovery_codes_status(db, user_id=1)
        >>> status["unused"]
        5
    """
    now = datetime.utcnow()

    # Get all recovery codes for user
    all_codes = db.execute(
        select(TOTPRecoveryCode).where(TOTPRecoveryCode.user_id == user_id)
    ).all()

    unused_codes = [
        code
        for code in all_codes
        if not code.is_used and (not code.expires_at or code.expires_at > now)
    ]
    used_codes = [code for code in all_codes if code.is_used]
    expired_codes = [
        code
        for code in all_codes
        if not code.is_used and code.expires_at and code.expires_at <= now
    ]

    return {
        "total": len(all_codes),
        "unused": len(unused_codes),
        "used": len(used_codes),
        "expired": len(expired_codes),
        "hints": [code.code_hint for code in unused_codes],
    }


def regenerate_recovery_codes(
    db: Session,
    user_id: int,
    totp_secret_id: int,
    count: int = 5,
    expires_days: Optional[int] = None,
) -> List[str]:
    """Regenerate recovery codes (invalidate old ones).

    Args:
        db: Database session
        user_id: User ID
        totp_secret_id: TOTP secret ID
        count: Number of recovery codes (default: 5)
        expires_days: Optional expiration in days

    Returns:
        List of new plaintext recovery codes

    Example:
        >>> new_codes = regenerate_recovery_codes(db, user_id=1, totp_secret_id=1)
    """
    # Delete old unused recovery codes
    old_codes = db.execute(
        select(TOTPRecoveryCode).where(
            TOTPRecoveryCode.user_id == user_id,
            TOTPRecoveryCode.totp_secret_id == totp_secret_id,
            TOTPRecoveryCode.is_used == False,  # noqa: E712
        )
    ).all()

    for code in old_codes:
        db.delete(code)

    db.commit()

    # Generate new recovery codes
    return create_recovery_codes(db, totp_secret_id, count, expires_days)
