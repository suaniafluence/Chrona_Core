"""
Script to create a test kiosk in the database.
This is useful for testing the kiosk app during development.
"""

import asyncio
import os

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.models import Kiosk


async def seed_kiosk():
    """Create a test kiosk with ID 1."""
    # Get database URL
    database_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./app.db")

    # Create async engine
    engine = create_async_engine(database_url, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Check if kiosk already exists
        result = await session.get(Kiosk, 1)
        if result:
            print(f"[OK] Kiosk already exists: {result.kiosk_name} (ID: {result.id})")
            return

        # Create new kiosk
        kiosk = Kiosk(
            id=1,
            kiosk_name="Test-Kiosk-ClockIn",
            location="Office Entrance",
            device_fingerprint="test-kiosk-fingerprint-001",
            public_key=None,  # Optional, can be set later if needed
            is_active=True,
        )
        session.add(kiosk)
        await session.commit()
        await session.refresh(kiosk)

        print(f"[OK] Created kiosk: {kiosk.kiosk_name} (ID: {kiosk.id})")
        print(f"   Location: {kiosk.location}")
        print(f"   Active: {kiosk.is_active}")


if __name__ == "__main__":
    print("[INFO] Seeding database with test kiosk...")
    asyncio.run(seed_kiosk())
    print("[OK] Done!")
