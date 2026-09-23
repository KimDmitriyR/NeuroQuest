import os

# Point the app at a dedicated test database BEFORE importing anything from `app`,
# since app.core.config.settings is instantiated at import time.
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://neuroquest:neuroquest@127.0.0.1:5432/neuroquest_test",
)

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.base import Base
from app.db.session import engine as app_engine
from app.main import app
from app.api.deps import get_db
from app import models  # noqa: F401  (register models on Base.metadata)


@pytest.fixture(scope="session", autouse=True)
async def _create_schema():
    async with app_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with app_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(autouse=True)
async def _clean_tables():
    yield
    async with app_engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())


@pytest.fixture
async def db_session() -> AsyncSession:
    TestSessionLocal = async_sessionmaker(bind=app_engine, expire_on_commit=False)
    async with TestSessionLocal() as session:
        yield session


@pytest.fixture
async def client():
    async def _override_get_db():
        TestSessionLocal = async_sessionmaker(bind=app_engine, expire_on_commit=False)
        async with TestSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = _override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
