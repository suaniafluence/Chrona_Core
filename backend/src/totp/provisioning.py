"""TOTP provisioning and activation logic.

Implements secure TOTP onboarding flow:
1. Initiate provisioning (generate secret, QR URI)
2. User scans QR code with authenticator app
3. Activate TOTP (verify first code)

Compliant with employee security spec:
- qr_provisioning.expiry: 300s
- qr_provisioning.usage: single
- qr_provisioning.transmission: HTTPS TLS1.2+
- qr_provisioning.session_binding: true
"""

from datetime import datetime, timedelta
from typing import Optional

from sqlmodel import Session, select

from src.models import TOTPSecret, User
from src.totp.core import generate_totp_secret, get_provisioning_uri, validate_totp_code
from src.totp.encryption import encrypt_secret


def initiate_totp_provisioning(
    db: Session,
    user_id: int,
    device_id: Optional[int] = None,
    encryption_key_id: str = "default",
    provisioning_expiry_seconds: int = 300,
) -> dict:
    """Initiate TOTP provisioning for a user.

    Generates a new TOTP secret and returns provisioning URI for QR code.

    Args:
        db: Database session
        user_id: User ID for provisioning
        device_id: Optional device binding
        encryption_key_id: KMS key ID for encryption (for key rotation)
        provisioning_expiry_seconds: QR code expiry in seconds (default: 300s = 5min)

    Returns:
        Dict with:
            - totp_secret_id: Database ID of TOTP secret
            - provisioning_uri: otpauth:// URI for QR code
            - expires_at: ISO timestamp when QR expires
            - secret: Base32 secret (for manual entry, optional)

    Raises:
        ValueError: If user already has active TOTP

    Example:
        >>> result = initiate_totp_provisioning(db, user_id=1)
        >>> result["provisioning_uri"].startswith("otpauth://totp/")
        True
    """
    # Check if user exists
    user = db.get(User, user_id)
    if not user:
        raise ValueError(f"User {user_id} not found")

    # Check if user already has active TOTP
    existing = db.exec(
        select(TOTPSecret).where(
            TOTPSecret.user_id == user_id,
            TOTPSecret.is_active == True,  # noqa: E712
            TOTPSecret.is_activated == True,  # noqa: E712
        )
    ).first()

    if existing:
        raise ValueError(
            f"User {user_id} already has active TOTP. "
            "Use reprovisioning flow (requires admin approval)."
        )

    # Generate TOTP secret (≥160 bits entropy, Base32)
    secret = generate_totp_secret(entropy_bits=160)

    # Encrypt secret (AES-GCM)
    encrypted_secret = encrypt_secret(secret)

    # Calculate expiry
    now = datetime.utcnow()
    expires_at = now + timedelta(seconds=provisioning_expiry_seconds)

    # Create TOTP secret record
    totp_secret = TOTPSecret(
        user_id=user_id,
        device_id=device_id,
        encrypted_secret=encrypted_secret,
        encryption_key_id=encryption_key_id,
        algorithm="SHA256",
        digits=6,
        period=30,
        provisioning_qr_expires_at=expires_at,
        is_activated=False,  # Not activated until first code verified
        is_active=True,
        created_at=now,
        # Key rotation: 90 days from now
        key_rotation_due_at=now + timedelta(days=90),
    )

    db.add(totp_secret)
    db.commit()
    db.refresh(totp_secret)

    # Generate provisioning URI for QR code
    provisioning_uri = get_provisioning_uri(
        secret=secret,
        account_name=user.email,
        issuer="Chrona",
        algorithm="SHA256",
        digits=6,
        period=30,
    )

    return {
        "totp_secret_id": totp_secret.id,
        "provisioning_uri": provisioning_uri,
        "expires_at": expires_at.isoformat(),
        "secret": secret,  # For manual entry (optional, can be omitted for security)
    }


def activate_totp(
    db: Session,
    totp_secret_id: int,
    verification_code: str,
) -> bool:
    """Activate TOTP after user scans QR code.

    Verifies the first TOTP code to ensure provisioning was successful.

    Args:
        db: Database session
        totp_secret_id: TOTP secret ID from provisioning
        verification_code: 6-digit TOTP code from authenticator app

    Returns:
        True if activation successful, False otherwise

    Raises:
        ValueError: If TOTP secret not found or expired

    Example:
        >>> result = initiate_totp_provisioning(db, user_id=1)
        >>> activate_totp(db, result["totp_secret_id"], "123456")
        True
    """
    # Get TOTP secret
    totp_secret = db.get(TOTPSecret, totp_secret_id)
    if not totp_secret:
        raise ValueError(f"TOTP secret {totp_secret_id} not found")

    # Check if already activated
    if totp_secret.is_activated:
        raise ValueError("TOTP already activated")

    # Check if provisioning expired
    now = datetime.utcnow()
    if (
        totp_secret.provisioning_qr_expires_at
        and now > totp_secret.provisioning_qr_expires_at
    ):
        raise ValueError(
            "Provisioning QR code expired. "
            f"Expired at {totp_secret.provisioning_qr_expires_at.isoformat()}"
        )

    # Decrypt secret
    from src.totp.encryption import decrypt_secret

    secret = decrypt_secret(totp_secret.encrypted_secret)

    # Validate TOTP code
    is_valid = validate_totp_code(
        secret=secret,
        code=verification_code,
        period=totp_secret.period,
        digits=totp_secret.digits,
        algorithm=totp_secret.algorithm,
        window=1,  # Allow ±1 time window (30s before/after)
    )

    if not is_valid:
        return False

    # Mark as activated
    totp_secret.is_activated = True
    totp_secret.activated_at = now
    totp_secret.last_used_at = now

    db.commit()

    return True
