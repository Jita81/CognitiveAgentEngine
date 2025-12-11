"""Agent API routes."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from src.agents.models import (
    AgentProfile,
    AgentProfileCreate,
    AgentProfileList,
    AgentProfileUpdate,
)
from src.api.dependencies import AgentRepo

router = APIRouter(prefix="/v1/agents", tags=["agents"])


@router.post(
    "",
    response_model=AgentProfile,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new agent",
    description="Create a new agent with the specified profile.",
)
async def create_agent(
    profile: AgentProfileCreate,
    repo: AgentRepo,
) -> AgentProfile:
    """Create a new agent with the given profile."""
    return await repo.create(profile)


@router.get(
    "/{agent_id}",
    response_model=AgentProfile,
    summary="Get agent by ID",
    description="Retrieve a specific agent by their UUID.",
)
async def get_agent(
    agent_id: UUID,
    repo: AgentRepo,
) -> AgentProfile:
    """Get agent by ID."""
    agent = await repo.get(agent_id)
    if agent is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found",
        )
    return agent


@router.get(
    "",
    response_model=AgentProfileList,
    summary="List agents",
    description="List agents with optional filtering and pagination.",
)
async def list_agents(
    repo: AgentRepo,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    role: Optional[str] = Query(None, description="Filter by role (partial match)"),
) -> AgentProfileList:
    """List agents with optional filtering."""
    agents, total = await repo.list(skip=skip, limit=limit, role=role)
    return AgentProfileList(
        agents=agents,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.patch(
    "/{agent_id}",
    response_model=AgentProfile,
    summary="Update agent",
    description="Update an existing agent's profile (partial update).",
)
async def update_agent(
    agent_id: UUID,
    updates: AgentProfileUpdate,
    repo: AgentRepo,
) -> AgentProfile:
    """Update agent profile."""
    agent = await repo.update(agent_id, updates)
    if agent is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found",
        )
    return agent


@router.delete(
    "/{agent_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete agent",
    description="Soft delete an agent (can be restored).",
)
async def delete_agent(
    agent_id: UUID,
    repo: AgentRepo,
) -> None:
    """Delete agent (soft delete)."""
    deleted = await repo.delete(agent_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found",
        )
