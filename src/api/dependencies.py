"""FastAPI dependencies for dependency injection."""

from typing import Annotated, AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.agents.repository import AgentRepository
from src.infrastructure.database import get_db


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting database sessions.

    Usage:
        @router.get("/")
        async def endpoint(db: Annotated[AsyncSession, Depends(get_db_session)]):
            ...
    """
    async for session in get_db():
        yield session


# Type alias for dependency injection
DbSession = Annotated[AsyncSession, Depends(get_db_session)]


async def get_agent_repository(
    session: DbSession,
) -> AgentRepository:
    """Dependency for getting agent repository.

    Usage:
        @router.get("/")
        async def endpoint(repo: Annotated[AgentRepository, Depends(get_agent_repository)]):
            ...
    """
    return AgentRepository(session)


# Type alias for repository dependency
AgentRepo = Annotated[AgentRepository, Depends(get_agent_repository)]
