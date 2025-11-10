import os
from pathlib import Path

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

# Module-level storage for test kiosk API keys
_kiosk_api_keys = {}


def pytest_configure() -> None:
    """Set default env vars for tests early without tripping flake8 E402."""
    os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
    os.environ.setdefault("ALLOWED_ORIGINS", "http://localhost:3000")

    # Set JWT key paths for tests
    project_root = Path(__file__).parent.parent.parent
    os.environ.setdefault("JWT_PRIVATE_KEY_PATH", str(project_root / "jwt_private_key.pem"))
    os.environ.setdefault("JWT_PUBLIC_KEY_PATH", str(project_root / "jwt_public_key.pem"))


@pytest_asyncio.fixture
async def test_db() -> AsyncSession:
    """Create a test database and yield a session."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///./test.db",
        echo=False,
        connect_args={"check_same_thread": False},
    )

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def test_session(test_db: AsyncSession):
    """Alias for test_db to maintain compatibility with existing tests."""
    return test_db


@pytest_asyncio.fixture
async def test_user(test_db: AsyncSession):
    from src.models.user import User
    from src.security import get_password_hash

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
async def test_admin(test_db: AsyncSession):
    from src.models.user import User
    from src.security import get_password_hash

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
async def auth_headers(test_user) -> dict:
    from src.security import create_access_token

    token = create_access_token({"sub": str(test_user.id), "role": test_user.role})
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def admin_headers(test_admin) -> dict:
    from src.security import create_access_token

    token = create_access_token({"sub": str(test_admin.id), "role": test_admin.role})
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def kiosk_headers(test_kiosk) -> dict:
    """Headers for kiosk API key authentication."""
    return {"X-Kiosk-API-Key": _kiosk_api_keys[test_kiosk.id]}


@pytest_asyncio.fixture
async def test_device(test_db: AsyncSession, test_user):
    from datetime import datetime, timezone

    from src.models.device import Device

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
async def test_kiosk(test_db: AsyncSession):
    from datetime import datetime, timezone

    from src.models.kiosk import Kiosk
    from src.routers.kiosk_auth import generate_kiosk_api_key, hash_kiosk_api_key

    # Generate API key for test kiosk
    api_key = generate_kiosk_api_key()

    kiosk = Kiosk(
        kiosk_name="Test Kiosk",
        location="Office Entrance",
        device_fingerprint="kiosk-fp-456",
        api_key_hash=hash_kiosk_api_key(api_key),
        is_active=True,
        created_at=datetime.now(timezone.utc),
    )
    test_db.add(kiosk)
    await test_db.commit()
    await test_db.refresh(kiosk)

    # Store the plain API key in module-level dictionary
    _kiosk_api_keys[kiosk.id] = api_key

    return kiosk


@pytest_asyncio.fixture
async def async_client(test_db: AsyncSession):
    """Create an async HTTP client with test database override."""

    async def override_get_session():
        yield test_db

    from src.db import get_session
    from src.main import app

    app.dependency_overrides[get_session] = override_get_session
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client
    app.dependency_overrides.clear()
