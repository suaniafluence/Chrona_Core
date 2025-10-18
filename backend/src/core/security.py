"""Security helpers for password hashing and verification."""

from __future__ import annotations

import base64
import binascii
import hashlib
import hmac
import secrets

_ALGORITHM = "pbkdf2_sha256"
_ITERATIONS = 390_000
_SALT_SIZE = 16


def _ensure_bytes(password: str) -> bytes:
    """Return a UTF-8 encoded password."""

    if not isinstance(password, str):
        raise TypeError("password must be a string")

    return password.encode("utf-8")


def _encode_segment(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def _decode_segment(value: str) -> bytes:
    return base64.b64decode(value.encode("ascii"))


def hash_password(password: str) -> str:
    """Hash ``password`` using PBKDF2-HMAC with SHA-256."""

    password_bytes = _ensure_bytes(password)
    salt = secrets.token_bytes(_SALT_SIZE)
    derived = hashlib.pbkdf2_hmac("sha256", password_bytes, salt, _ITERATIONS)
    return f"{_ALGORITHM}${_encode_segment(salt)}${_encode_segment(derived)}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify ``plain_password`` against the provided ``hashed_password``."""

    try:
        algorithm, salt_b64, hash_b64 = hashed_password.split("$")
        if algorithm != _ALGORITHM:
            return False
        salt = _decode_segment(salt_b64)
        expected = _decode_segment(hash_b64)
    except (ValueError, binascii.Error):
        return False

    password_bytes = _ensure_bytes(plain_password)
    derived = hashlib.pbkdf2_hmac("sha256", password_bytes, salt, _ITERATIONS)
    return hmac.compare_digest(derived, expected)
