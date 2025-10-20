"""
Generate API key for a test kiosk.
This creates an API key that can be used for kiosk authentication.
"""

import asyncio
import os
import secrets

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.models import Kiosk
from src.security import get_password_hash


def generate_kiosk_api_key() -> str:
    """Generate a secure random API key for kiosks."""
    return secrets.token_urlsafe(32)


async def set_kiosk_api_key(kiosk_id: int = 1):
    """Generate and set API key for a kiosk."""
    # Get database URL
    database_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./app.db")

    # Create async engine
    engine = create_async_engine(database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        print(f"[INFO] Generating API key for kiosk ID {kiosk_id}...")
        print()

        # Get kiosk
        kiosk = await session.get(Kiosk, kiosk_id)
        if not kiosk:
            print(f"[ERROR] Kiosk with ID {kiosk_id} not found")
            print("[TIP] Run: cd backend && python -m tools.seed_kiosk")
            return

        # Generate new API key
        api_key = generate_kiosk_api_key()
        api_key_hash = get_password_hash(api_key)

        # Update kiosk
        kiosk.api_key_hash = api_key_hash
        session.add(kiosk)
        await session.commit()
        await session.refresh(kiosk)

        print(f"[OK] API key generated for kiosk: {kiosk.kiosk_name}")
        print(f"    Kiosk ID: {kiosk.id}")
        print(f"    Location: {kiosk.location}")
        print()
        print("=" * 70)
        print("IMPORTANT: Save this API key securely - it won't be shown again!")
        print("=" * 70)
        print()
        print(f"API KEY: {api_key}")
        print()
        print("=" * 70)
        print()
        print("[TIP] Add this to your kiosk app .env file:")
        print(f"      VITE_KIOSK_API_KEY={api_key}")
        print()


if __name__ == "__main__":
    import sys

    kiosk_id = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    asyncio.run(set_kiosk_api_key(kiosk_id))
