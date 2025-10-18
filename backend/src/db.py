import os
from contextlib import asynccontextmanager
from typing import Any, Optional

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


class _EngineProxy:
    """Proxy used so tests importing ``engine`` see runtime updates."""

    def __init__(self) -> None:
        self._engine: Optional[AsyncEngine] = None

    def set(self, value: AsyncEngine) -> None:
        self._engine = value

    def get(self) -> Optional[AsyncEngine]:
        return self._engine

    def clear(self) -> None:
        self._engine = None

    def __getattr__(self, item: str) -> Any:  # type: ignore[override]
        engine = self._engine
        if engine is None:
            raise AttributeError("engine is not initialized")
        return getattr(engine, item)

    def __bool__(self) -> bool:
        return self._engine is not None


_engine_proxy = _EngineProxy()
engine = _engine_proxy
SessionLocal: Optional[async_sessionmaker[AsyncSession]] = None


def _setup_engine() -> None:
    global SessionLocal
    # Dispose previous engine if any (should not happen outside lifespan)
    url = _database_url()
    if url.endswith(":memory:"):
        current_engine = create_async_engine(url, future=True, poolclass=StaticPool)
    else:
        current_engine = create_async_engine(url, future=True)
    _engine_proxy.set(current_engine)
    SessionLocal = async_sessionmaker(
        current_engine, class_=AsyncSession, expire_on_commit=False
    )


@asynccontextmanager
async def lifespan(app):  # type: ignore[no-untyped-def]
    _setup_engine()
    current_engine = _engine_proxy.get()
    # On startup, ensure metadata exists for SQLite (optional best-effort)
    if _database_url().startswith("sqlite+") and current_engine is not None:
        # Import models to register tables in metadata
        try:
            import importlib

            importlib.import_module("src.models.user")
        except Exception:
            pass
        async with current_engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
    yield
    # graceful shutdown
    current_engine = _engine_proxy.get()
    if current_engine is not None:
        await current_engine.dispose()
    # Reset so subsequent test clients can re-init with new env
    _reset_engine()


def _reset_engine() -> None:
    global SessionLocal
    _engine_proxy.clear()
    SessionLocal = None


async def db_health() -> bool:
    try:
        current_engine = _engine_proxy.get()
        if current_engine is None:
            return False
        async with current_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


async def get_session() -> AsyncSession:
    if SessionLocal is None:
        raise RuntimeError("DB not initialized; ensure app lifespan has started")
    async with SessionLocal() as session:
        yield session
