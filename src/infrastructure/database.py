"""Async SQLAlchemy database setup and models."""

from datetime import datetime
from typing import AsyncGenerator
from uuid import uuid4

from sqlalchemy import DateTime, String, Text, Integer, Index
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src.core.config import get_settings


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


class AgentProfileDB(Base):
    """Database model for agent profiles."""

    __tablename__ = "agent_profiles"

    # Primary key
    agent_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # Identity
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str | None] = mapped_column(String(100), nullable=True)
    backstory_summary: Mapped[str] = mapped_column(Text, nullable=False)
    years_experience: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Skills and personality (JSONB for flexibility)
    skills: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    personality_markers: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    social_markers: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    communication_style: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    # Knowledge
    knowledge_domains: Mapped[list] = mapped_column(JSONB, nullable=True, default=list)
    knowledge_gaps: Mapped[list] = mapped_column(JSONB, nullable=True, default=list)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Indexes defined via __table_args__
    __table_args__ = (
        Index("idx_agent_profiles_name", name, postgresql_where=(deleted_at.is_(None))),
        Index("idx_agent_profiles_role", role, postgresql_where=(deleted_at.is_(None))),
        Index("idx_agent_profiles_deleted", deleted_at),
    )


# Global engine and session factory (initialized lazily)
_engine = None
_async_session_factory = None


def get_engine():
    """Get or create the async database engine."""
    global _engine
    if _engine is None:
        settings = get_settings()
        _engine = create_async_engine(
            settings.database_url,
            pool_size=settings.database_pool_size,
            pool_pre_ping=True,
            echo=settings.environment == "development",
        )
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Get or create the async session factory."""
    global _async_session_factory
    if _async_session_factory is None:
        engine = get_engine()
        _async_session_factory = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _async_session_factory


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting database sessions."""
    session_factory = get_session_factory()
    async with session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize the database (create tables if they don't exist)."""
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Close database connections."""
    global _engine, _async_session_factory
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _async_session_factory = None

