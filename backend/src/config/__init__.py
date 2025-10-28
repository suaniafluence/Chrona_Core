"""Application configuration settings loaded from environment variables."""

from __future__ import annotations

import os
from pathlib import Path


class Settings:
    """Container for runtime configuration values."""

    def __init__(self) -> None:
        # Legacy HS256 support (for backward compatibility during migration)
        self.SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")

        # JWT Algorithm: ES256 (recommended for TOTP), RS256 (legacy), or HS256 (legacy)
        self.ALGORITHM = os.getenv("ALGORITHM", "RS256")

        # RS256/ES256 Keys
        # For RS256: jwt_private_key.pem, jwt_public_key.pem
        # For ES256: jwt_ec_private_key.pem, jwt_ec_public_key.pem
        if self.ALGORITHM == "ES256":
            default_private = "jwt_ec_private_key.pem"
            default_public = "jwt_ec_public_key.pem"
        else:
            default_private = "jwt_private_key.pem"
            default_public = "jwt_public_key.pem"

        self.JWT_PRIVATE_KEY_PATH = os.getenv(
            "JWT_PRIVATE_KEY_PATH",
            str(Path(__file__).parent.parent.parent / default_private),
        )
        self.JWT_PUBLIC_KEY_PATH = os.getenv(
            "JWT_PUBLIC_KEY_PATH",
            str(Path(__file__).parent.parent.parent / default_public),
        )

        # Load keys if using asymmetric algorithms (RS256 or ES256)
        self._jwt_private_key: str | None = None
        self._jwt_public_key: str | None = None
        if self.ALGORITHM in ("RS256", "ES256"):
            self._load_jwt_keys()

        # Token expiration
        self.ACCESS_TOKEN_EXPIRE_MINUTES = self._get_int(
            "ACCESS_TOKEN_EXPIRE_MINUTES", 60
        )
        self.EPHEMERAL_TOKEN_EXPIRE_SECONDS = self._get_int(
            "EPHEMERAL_TOKEN_EXPIRE_SECONDS", 30
        )

        # Password hashing
        self.BCRYPT_ROUNDS = self._get_int("BCRYPT_ROUNDS", 12)

    def _load_jwt_keys(self) -> None:
        """Load RSA/EC keys for RS256/ES256 JWT signing."""
        try:
            with open(self.JWT_PRIVATE_KEY_PATH, "r") as f:
                self._jwt_private_key = f.read()
            with open(self.JWT_PUBLIC_KEY_PATH, "r") as f:
                self._jwt_public_key = f.read()
        except FileNotFoundError as e:
            if self.ALGORITHM == "ES256":
                raise RuntimeError(
                    f"JWT keys not found: {e}. "
                    "Run 'python tools/generate_ec_keys.py' to generate ES256 keys."
                )
            else:
                raise RuntimeError(
                    f"JWT keys not found: {e}. "
                    "Run 'python tools/generate_keys.py' to generate RS256 keys."
                )

    @property
    def jwt_private_key(self) -> str:
        """Get JWT private key for RS256/ES256 signing."""
        if self._jwt_private_key is None:
            raise RuntimeError(
                f"JWT private key not loaded (not using {self.ALGORITHM}?)"
            )
        return self._jwt_private_key

    @property
    def jwt_public_key(self) -> str:
        """Get JWT public key for RS256/ES256 verification."""
        if self._jwt_public_key is None:
            raise RuntimeError(
                f"JWT public key not loaded (not using {self.ALGORITHM}?)"
            )
        return self._jwt_public_key

    @staticmethod
    def _get_int(name: str, default: int) -> int:
        value = os.getenv(name)
        if value is None:
            return default
        try:
            return int(value)
        except ValueError:
            return default


settings = Settings()

__all__ = ["Settings", "settings"]
