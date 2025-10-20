"""
Script to create a test user for development/testing.
"""

import asyncio
import os

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.models import User
from src.security import get_password_hash


async def create_test_user():
    """Create a test user with username 'testuser'."""
    # Get database URL
    database_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./app.db")

    # Create async engine
    engine = create_async_engine(database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        print("[INFO] Creating test user...")

        # Check if user already exists
        from sqlalchemy import select

        result = await session.execute(select(User).where(User.email == "testuser@example.com"))
        existing_user = result.scalar_one_or_none()

        if existing_user:
            print(f"[OK] User already exists: {existing_user.email} (ID: {existing_user.id})")
            print(f"    Role: {existing_user.role}")
            return

        # Create new user
        hashed_password = get_password_hash("testpass123")
        user = User(
            email="testuser@example.com",
            hashed_password=hashed_password,
            role="user",
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        print(f"[OK] Created user: {user.email} (ID: {user.id})")
        print(f"    Role: {user.role}")
        print(f"    Password: testpass123")
        print()
        print("[TIP] You can now use this user to test the QR flow:")
        print("      Email: testuser@example.com")
        print("      Password: testpass123")


if __name__ == "__main__":
    asyncio.run(create_test_user())
