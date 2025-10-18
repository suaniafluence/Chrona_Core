import os
from contextlib import asynccontextmanager

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel


def _database_url() -> str:
    # Default to local SQLite file for ease of dev/CI
    return os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./app.db")


engine: AsyncEngine = create_async_engine(_database_url(), future=True)
SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@asynccontextmanager
async def lifespan(app):  # type: ignore[no-untyped-def]
    # On startup, ensure metadata exists for SQLite (optional best-effort)
    if _database_url().startswith("sqlite+"):
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
    await engine.dispose()


async def db_health() -> bool:
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session
