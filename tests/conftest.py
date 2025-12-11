"""Pytest fixtures for testing."""

import asyncio
import os
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from src.api.main import app
from src.api.dependencies import get_db_session
from src.agents.repository import AgentRepository


# Test database URL - use PostgreSQL for integration tests
# Set CAE_TEST_DATABASE_URL env var for PostgreSQL, otherwise use SQLite for unit tests
TEST_DATABASE_URL = os.environ.get(
    "CAE_TEST_DATABASE_URL",
    "sqlite+aiosqlite:///:memory:"
)


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_engine():
    """Create a test database engine."""
    # Use StaticPool for SQLite in-memory to share connection
    connect_args = {}
    poolclass = None
    
    if "sqlite" in TEST_DATABASE_URL:
        connect_args = {"check_same_thread": False}
        poolclass = StaticPool
    
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        connect_args=connect_args,
        poolclass=poolclass,
    )
    
    # Create tables based on database type
    async with engine.begin() as conn:
        if "postgresql" in TEST_DATABASE_URL:
            # For PostgreSQL, use the actual models
            from src.infrastructure.database import Base
            await conn.run_sync(Base.metadata.create_all)
        else:
            # For SQLite, create a compatible schema without PostgreSQL-specific types
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS agent_profiles (
                    agent_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    role TEXT NOT NULL,
                    title TEXT,
                    backstory_summary TEXT NOT NULL,
                    years_experience INTEGER,
                    skills TEXT NOT NULL DEFAULT '{}',
                    personality_markers TEXT NOT NULL DEFAULT '{}',
                    social_markers TEXT NOT NULL DEFAULT '{}',
                    communication_style TEXT NOT NULL DEFAULT '{}',
                    knowledge_domains TEXT DEFAULT '[]',
                    knowledge_gaps TEXT DEFAULT '[]',
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    deleted_at TIMESTAMP
                )
            """))
    
    yield engine
    
    # Cleanup
    async with engine.begin() as conn:
        if "postgresql" in TEST_DATABASE_URL:
            from src.infrastructure.database import Base
            await conn.run_sync(Base.metadata.drop_all)
        else:
            await conn.execute(text("DROP TABLE IF EXISTS agent_profiles"))
    
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_session_factory(test_engine):
    """Create a test session factory."""
    return async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


@pytest_asyncio.fixture(scope="function")
async def test_session(test_session_factory) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async with test_session_factory() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def client(test_session_factory) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client with overridden dependencies."""
    
    async def override_get_db_session() -> AsyncGenerator[AsyncSession, None]:
        async with test_session_factory() as session:
            yield session
    
    app.dependency_overrides[get_db_session] = override_get_db_session
    
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac
    
    app.dependency_overrides.clear()
