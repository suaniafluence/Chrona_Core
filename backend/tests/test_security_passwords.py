import pytest

from src.core.security import hash_password, verify_password


def test_hash_password_accepts_long_inputs():
    # Create password with more than 72 bytes when encoded as UTF-8.
    password = "pässword" * 20  # contains multibyte characters
    assert len(password.encode("utf-8")) > 72

    hashed = hash_password(password)
    assert hashed.startswith("pbkdf2_sha256$")


def test_verify_password_handles_long_inputs():
    password = "pässword" * 20
    hashed = hash_password(password)

    assert verify_password(password, hashed)
    assert not verify_password(password + "!", hashed)


def test_hash_password_rejects_non_string():
    with pytest.raises(TypeError):
        hash_password(123)  # type: ignore[arg-type]
