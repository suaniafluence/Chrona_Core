import os
from contextlib import asynccontextmanager
from typing import Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel


def _database_url() -> str:
    # Default to local SQLite file for ease of dev/CI
    return os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./app.db")

engine: Optional[AsyncEngine] = None
SessionLocal: Optional[async_sessionmaker[AsyncSession]] = None


def _setup_engine() -> None:
    global engine, SessionLocal
    # Dispose previous engine if any (should not happen outside lifespan)
    if engine is not None:
        # Disposal will be handled on shutdown, keep here for safety
        pass
    url = _database_url()
    if url.endswith(":memory:"):
        engine = create_async_engine(url, future=True, poolclass=StaticPool)
    else:
        engine = create_async_engine(url, future=True)
    SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@asynccontextmanager
async def lifespan(app):  # type: ignore[no-untyped-def]
    _setup_engine()
    # On startup, ensure metadata exists for SQLite (optional best-effort)
    if _database_url().startswith("sqlite+") and engine is not None:
        # Import models to register tables in metadata
        try:
            import importlib

            importlib.import_module("src.models.user")
        except Exception:
            pass
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
    yield
    # graceful shutdown
    if engine is not None:
        await engine.dispose()
    # Reset so subsequent test clients can re-init with new env
    _reset_engine()


def _reset_engine() -> None:
    global engine, SessionLocal
    engine = None
    SessionLocal = None


async def db_health() -> bool:
    try:
        if engine is None:
            return False
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


async def get_session() -> AsyncSession:
    if SessionLocal is None:
        raise RuntimeError("DB not initialized; ensure app lifespan has started")
    async with SessionLocal() as session:
        yield session
