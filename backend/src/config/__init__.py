"""Application configuration settings loaded from environment variables."""

from __future__ import annotations

import os
from pathlib import Path


class Settings:
    """Container for runtime configuration values."""

    def __init__(self) -> None:
        # Legacy HS256 support (for backward compatibility during migration)
        self.SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")

        # JWT Algorithm: RS256 (recommended) or HS256 (legacy)
        self.ALGORITHM = os.getenv("ALGORITHM", "RS256")

        # RS256 Keys
        self.JWT_PRIVATE_KEY_PATH = os.getenv(
            "JWT_PRIVATE_KEY_PATH",
            str(Path(__file__).parent.parent.parent / "jwt_private_key.pem"),
        )
        self.JWT_PUBLIC_KEY_PATH = os.getenv(
            "JWT_PUBLIC_KEY_PATH",
            str(Path(__file__).parent.parent.parent / "jwt_public_key.pem"),
        )

        # Load keys if using RS256
        self._jwt_private_key: str | None = None
        self._jwt_public_key: str | None = None
        if self.ALGORITHM == "RS256":
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
        """Load RSA keys for RS256 JWT signing."""
        try:
            with open(self.JWT_PRIVATE_KEY_PATH, "r") as f:
                self._jwt_private_key = f.read()
            with open(self.JWT_PUBLIC_KEY_PATH, "r") as f:
                self._jwt_public_key = f.read()
        except FileNotFoundError as e:
            raise RuntimeError(
                f"JWT keys not found: {e}. Run 'python tools/generate_keys.py' to generate them."
            )

    @property
    def jwt_private_key(self) -> str:
        """Get JWT private key for RS256 signing."""
        if self._jwt_private_key is None:
            raise RuntimeError("JWT private key not loaded (not using RS256?)")
        return self._jwt_private_key

    @property
    def jwt_public_key(self) -> str:
        """Get JWT public key for RS256 verification."""
        if self._jwt_public_key is None:
            raise RuntimeError("JWT public key not loaded (not using RS256?)")
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
