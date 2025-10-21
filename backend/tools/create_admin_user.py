"""Utility script to ensure an administrator account exists."""

import argparse
import asyncio
import os

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.models import User
from src.security import get_password_hash


async def ensure_admin_user(email: str, password: str, role: str = "admin", reset_password: bool = False) -> None:
    """Create or update an administrator user for the backoffice."""
    database_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./app.db")
    engine = create_async_engine(database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        print(f"[INFO] Ensuring admin user exists for email: {email}")

        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if user:
            updates = []

            if user.role != role:
                user.role = role
                updates.append("role")

            if reset_password:
                user.hashed_password = get_password_hash(password)
                updates.append("password")

            if updates:
                await session.commit()
                await session.refresh(user)
                print(f"[OK] Updated user {user.email} (ID: {user.id}) -> {', '.join(updates)}")
            else:
                print(f"[OK] User already exists: {user.email} (ID: {user.id})")
                print("    No changes required. Use --reset-password if you need to update credentials.")
            return

        hashed_password = get_password_hash(password)
        user = User(email=email, hashed_password=hashed_password, role=role)
        session.add(user)
        await session.commit()
        await session.refresh(user)

        print(f"[OK] Created admin user: {user.email} (ID: {user.id})")
        print(f"    Role: {user.role}")
        print(f"    Password: {password}")


async def async_main(args: argparse.Namespace) -> None:
    await ensure_admin_user(
        email=args.email,
        password=args.password,
        role=args.role,
        reset_password=args.reset_password,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Create or promote an administrator user.")
    parser.add_argument("--email", default="admin@example.com", help="Email of the admin user to create or update.")
    parser.add_argument(
        "--password",
        default="adminpass123",
        help="Password to set when creating the user (or when --reset-password is provided).",
    )
    parser.add_argument(
        "--role",
        default="admin",
        help="Role to enforce on the user (defaults to 'admin').",
    )
    parser.add_argument(
        "--reset-password",
        action="store_true",
        help="Also reset the password if the user already exists.",
    )

    args = parser.parse_args()
    asyncio.run(async_main(args))


if __name__ == "__main__":
    main()
