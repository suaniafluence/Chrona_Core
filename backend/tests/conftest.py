import os

# Ensure DB URL is set before importing app/modules during test collection
# Use file-based SQLite by default to avoid in-memory connection pooling issues.
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
os.environ.setdefault("ALLOWED_ORIGINS", "http://localhost:3000")

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from src.db import get_session
from src.main import app
from src.models.device import Device
from src.models.kiosk import Kiosk
from src.models.user import User
from src.security import create_access_token, get_password_hash


@pytest_asyncio.fixture
async def test_db():
    """Create a test database and yield a session."""
    # Create async engine for test database
    engine = create_async_engine(
        "sqlite+aiosqlite:///./test.db",
        echo=False,
        connect_args={"check_same_thread": False},
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    # Create session
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session

    # Drop all tables after test
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def test_user(test_db: AsyncSession) -> User:
    """Create a test user."""
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword"),
        role="user",
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_admin(test_db: AsyncSession) -> User:
    """Create a test admin user."""
    admin = User(
        email="admin@example.com",
        hashed_password=get_password_hash("adminpassword"),
        role="admin",
    )
    test_db.add(admin)
    await test_db.commit()
    await test_db.refresh(admin)
    return admin


@pytest_asyncio.fixture
async def auth_headers(test_user: User) -> dict:
    """Generate authentication headers for test user."""
    token = create_access_token({"sub": str(test_user.id), "role": test_user.role})
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def admin_headers(test_admin: User) -> dict:
    """Generate authentication headers for admin user."""
    token = create_access_token({"sub": str(test_admin.id), "role": test_admin.role})
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def test_device(test_db: AsyncSession, test_user: User) -> Device:
    """Create a test device for the test user."""
    from datetime import datetime, timezone

    device = Device(
        user_id=test_user.id,
        device_fingerprint="test-device-fingerprint-123",
        device_name="Test iPhone",
        registered_at=datetime.now(timezone.utc),
        is_revoked=False,
    )
    test_db.add(device)
    await test_db.commit()
    await test_db.refresh(device)
    return device


@pytest_asyncio.fixture
async def test_kiosk(test_db: AsyncSession) -> Kiosk:
    """Create a test kiosk."""
    from datetime import datetime, timezone

    kiosk = Kiosk(
        kiosk_name="Test Kiosk",
        location="Office Entrance",
        device_fingerprint="kiosk-fp-456",
        is_active=True,
        created_at=datetime.now(timezone.utc),
    )
    test_db.add(kiosk)
    await test_db.commit()
    await test_db.refresh(kiosk)
    return kiosk


@pytest_asyncio.fixture
async def async_client(test_db: AsyncSession):
    """Create an async HTTP client with test database override."""

    async def override_get_session():
        yield test_db

    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client

    app.dependency_overrides.clear()
