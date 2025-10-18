"""Application configuration settings loaded from environment variables."""

from __future__ import annotations

import os


class Settings:
    """Container for runtime configuration values."""

    def __init__(self) -> None:
        self.SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
        self.ACCESS_TOKEN_EXPIRE_MINUTES = self._get_int(
            "ACCESS_TOKEN_EXPIRE_MINUTES", 60
        )
        self.ALGORITHM = os.getenv("ALGORITHM", "HS256")
        self.BCRYPT_ROUNDS = self._get_int("BCRYPT_ROUNDS", 12)

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
