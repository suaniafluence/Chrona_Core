import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.hash import bcrypt_sha256


def get_secret_key() -> str:
    return os.getenv("SECRET_KEY", "dev-secret-change-me")


def get_token_exp_minutes() -> int:
    try:
        return int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    except ValueError:
        return 60


MAX_PASSWORD_BYTES = 72


def _truncate_password(password: str) -> str:
    data = password.encode("utf-8")
    if len(data) <= MAX_PASSWORD_BYTES:
        return password
    # Truncate to 72 bytes boundary; drop partial multibyte char tails
    return data[:MAX_PASSWORD_BYTES].decode("utf-8", errors="ignore")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt_sha256.verify(_truncate_password(plain_password), hashed_password)


def get_password_hash(password: str) -> str:
    return bcrypt_sha256.hash(_truncate_password(password))


def create_access_token(subject: str, role: str, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = {"sub": subject, "role": role}
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=get_token_exp_minutes()))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, get_secret_key(), algorithm="HS256")
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, get_secret_key(), algorithms=["HS256"])
    except JWTError:
        return None
