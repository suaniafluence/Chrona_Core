"""
Create or promote an admin user in the configured database.

Usage (inside container):
  python tools/create_admin_user.py \
    --email admin@example.com --password 'Passw0rd!'

Environment variables (alternatives to flags):
  ADMIN_EMAIL, ADMIN_PASSWORD, ADMIN_ROLE (default: admin)
"""

from __future__ import annotations

import argparse
import asyncio
import os
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.models.user import User
from src.security import get_password_hash


def _get_env(name: str, default: Optional[str] = None) -> Optional[str]:
    val = os.getenv(name)
    return val if val is not None and val.strip() != "" else default


async def _create_or_promote_admin(
    email: str, password: str, role: str
) -> None:
    database_url = os.getenv(
        "DATABASE_URL",
        "sqlite+aiosqlite:///./app.db",
    )
    engine = create_async_engine(
        database_url,
        echo=False,
    )
    async_session = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if user:
            user.role = role
            # Do not change password silently; set only if provided explicitly
            if password:
                user.hashed_password = get_password_hash(password)
            session.add(user)
            await session.commit()
            await session.refresh(user)
            print(
                "[OK] User exists, updated role to '"
                f"{user.role}'"
                f": {user.email} (ID: {user.id})"
            )
            return

        hashed = get_password_hash(password)
        user = User(email=email, hashed_password=hashed, role=role)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        print(f"[OK] Created admin user: {user.email} (ID: {user.id})")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Create or promote an admin user"
        )
    )
    parser.add_argument(
        "--email", default=_get_env("ADMIN_EMAIL"), help="Admin email"
    )
    parser.add_argument(
        "--password",
        default=_get_env("ADMIN_PASSWORD"),
        help="Admin password (updates password if user exists)",
    )
    parser.add_argument(
        "--role", default=_get_env("ADMIN_ROLE", "admin"), help="Role"
    )
    args = parser.parse_args()

    if not args.email or not args.password:
        parser.error(
            "--email and --password are required "
            "(or set ADMIN_EMAIL/ADMIN_PASSWORD)"
        )

    asyncio.run(_create_or_promote_admin(args.email, args.password, args.role))


if __name__ == "__main__":
    main()
