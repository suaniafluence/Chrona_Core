import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from src.config import settings

# Configure password context with explicit bcrypt settings
pwd_context = CryptContext(
    schemes=["bcrypt_sha256"],
    deprecated="auto",
    bcrypt_sha256__rounds=settings.BCRYPT_ROUNDS,
    bcrypt_sha256__ident="2b",
)


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt_sha256."""

    return pwd_context.hash(password)


MAX_PASSWORD_BYTES = 72


def _truncate_password(password: str) -> str:
    data = password.encode("utf-8")
    if len(data) <= MAX_PASSWORD_BYTES:
        return password
    # Truncate to 72 bytes boundary; drop partial multibyte char tails
    return data[:MAX_PASSWORD_BYTES].decode("utf-8", errors="ignore")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""

    return pwd_context.verify(plain_password, hashed_password)


def _get_signing_key() -> str:
    """Get the appropriate signing key based on algorithm."""
    if settings.ALGORITHM == "RS256":
        return settings.jwt_private_key
    return settings.SECRET_KEY


def _get_verification_key() -> str:
    """Get the appropriate verification key based on algorithm."""
    if settings.ALGORITHM == "RS256":
        return settings.jwt_public_key
    return settings.SECRET_KEY


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token (long-lived for user sessions).

    Args:
        data: Payload dict (should include 'sub' and 'role')
        expires_delta: Optional expiration time (default: ACCESS_TOKEN_EXPIRE_MINUTES)

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    encoded_jwt = jwt.encode(
        to_encode,
        _get_signing_key(),
        algorithm=settings.ALGORITHM,
    )
    return encoded_jwt


def create_ephemeral_qr_token(
    user_id: int, device_id: int, expires_seconds: Optional[int] = None
) -> tuple[str, dict]:
    """Create an ephemeral JWT token for QR code (short-lived, single-use).

    Args:
        user_id: User ID
        device_id: Device ID
        expires_seconds: Token expiration in seconds
            (default: EPHEMERAL_TOKEN_EXPIRE_SECONDS)

    Returns:
        Tuple of (encoded JWT string, payload dict with datetime objects)
    """
    nonce = str(uuid.uuid4())  # Random nonce for replay protection
    jti = str(uuid.uuid4())  # Unique token ID for single-use enforcement

    expires = expires_seconds or settings.EPHEMERAL_TOKEN_EXPIRE_SECONDS
    now = datetime.now(timezone.utc)
    expire = now + timedelta(seconds=expires)

    # JWT payload with timestamps (for encoding)
    jwt_payload = {
        "sub": str(user_id),
        "device_id": device_id,
        "nonce": nonce,
        "jti": jti,
        "iat": now,
        "exp": expire,
        "type": "ephemeral_qr",  # Token type identifier
    }

    encoded_jwt = jwt.encode(
        jwt_payload,
        _get_signing_key(),
        algorithm=settings.ALGORITHM,
    )

    # Return payload with datetime objects for database storage
    payload = {
        "sub": str(user_id),
        "device_id": device_id,
        "nonce": nonce,
        "jti": jti,
        "iat": now,  # datetime object
        "exp": expire,  # datetime object
        "type": "ephemeral_qr",
    }

    return encoded_jwt, payload


def decode_token(token: str) -> Optional[dict]:
    """Decode and verify a JWT token.

    Args:
        token: Encoded JWT string

    Returns:
        Decoded payload dict or None if invalid
    """
    try:
        return jwt.decode(
            token, _get_verification_key(), algorithms=[settings.ALGORITHM]
        )
    except JWTError:
        return None
