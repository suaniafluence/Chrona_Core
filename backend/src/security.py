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


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""

    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None
