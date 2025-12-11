"""Memory API routes.

Phase 6: Memory architecture endpoints for recording, querying,
and managing agent memories across all tiers.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.agents.repository import AgentRepository
from src.api.dependencies import AgentRepo
from src.cognitive.tiers import CognitiveTier
from src.infrastructure.database import get_db
from src.memory import (
    MemoryManager,
    WorkingMemory,
    ShortTermMemory,
    LongTermMemory,
    ShortTermMemoryEntry,
    ProjectChapter,
    create_memory_manager,
)

router = APIRouter(prefix="/v1/memory", tags=["memory"])


# ==========================================
# Request/Response Models
# ==========================================


class RecordMemoryRequest(BaseModel):
    """Request to record a memory."""
    
    content: str = Field(..., min_length=1, description="Memory content")
    memory_type: str = Field(
        ...,
        description="Type: observation, decision, interaction, insight",
    )
    significance: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Importance score",
    )
    topic: str = Field(default="", description="Topic/context")
    project_id: Optional[UUID] = Field(None, description="Related project ID")
    related_agents: Optional[List[str]] = Field(
        None,
        description="Related agent IDs",
    )


class MemoryResponse(BaseModel):
    """Response for a memory entry."""
    
    memory_id: str
    agent_id: str
    memory_type: str
    content: str
    significance: float
    topic_keywords: List[str]
    created_at: str
    expires_at: str
    project_id: Optional[str] = None
    related_agents: Optional[List[str]] = None


class QueryMemoriesRequest(BaseModel):
    """Request to query memories."""
    
    topic: Optional[str] = Field(None, description="Topic to search for")
    memory_type: Optional[str] = Field(None, description="Filter by type")
    min_significance: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Minimum significance",
    )
    max_results: int = Field(default=10, ge=1, le=50, description="Max results")


class MemoryContextRequest(BaseModel):
    """Request for tier-appropriate memory context."""
    
    tier: str = Field(..., description="Cognitive tier (REFLEX, REACTIVE, etc.)")
    topic: Optional[str] = Field(None, description="Topic to focus retrieval")


class MemoryContextResponse(BaseModel):
    """Response containing memory context."""
    
    tier: str
    context: str
    token_estimate: int


class AddChapterRequest(BaseModel):
    """Request to add a project chapter."""
    
    project_id: UUID = Field(..., description="Project ID")
    title: str = Field(..., min_length=1, description="Chapter title")
    summary: str = Field(..., min_length=1, description="Chapter summary")
    role: Optional[str] = Field(None, description="Agent's role")
    outcome: Optional[str] = Field(
        None,
        description="Outcome: success, partial_success, failure, ongoing",
    )
    significance: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Importance score",
    )
    lessons: Optional[str] = Field(None, description="Lessons learned")
    collaborators: Optional[List[str]] = Field(None, description="Collaborator IDs")


class ChapterResponse(BaseModel):
    """Response for a project chapter."""
    
    chapter_id: str
    agent_id: str
    project_id: str
    title: str
    summary: str
    role_in_project: Optional[str]
    start_date: str
    end_date: Optional[str]
    outcome: Optional[str]
    significance: float
    lessons_learned: Optional[str]
    collaborators: Optional[List[str]]


class SearchChaptersRequest(BaseModel):
    """Request to search chapters."""
    
    topic: Optional[str] = Field(None, description="Topic to search for")
    outcome: Optional[str] = Field(None, description="Filter by outcome")
    project_id: Optional[UUID] = Field(None, description="Filter by project")
    max_results: int = Field(default=10, ge=1, le=50, description="Max results")


class WorkingMemoryStateResponse(BaseModel):
    """Response for working memory state."""
    
    turn_count: int
    max_turns: int
    current_topic: str
    current_mood: str
    confidence_level: float
    cache_size: int


class PromoteMemoryRequest(BaseModel):
    """Request to promote a short-term memory to long-term."""
    
    memory_id: UUID = Field(..., description="Memory to promote")
    project_id: UUID = Field(..., description="Project to associate with")
    title: str = Field(..., description="Chapter title")
    lessons: Optional[str] = Field(None, description="Additional lessons")


# ==========================================
# Helper Functions
# ==========================================


async def get_memory_manager(
    agent_id: UUID,
    session: AsyncSession,
    repo: AgentRepository,
) -> MemoryManager:
    """Get or create a memory manager for an agent.
    
    Args:
        agent_id: Agent ID
        session: Database session
        repo: Agent repository
        
    Returns:
        MemoryManager instance
        
    Raises:
        HTTPException: If agent not found
    """
    agent = await repo.get(agent_id)
    if agent is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found",
        )
    
    return await create_memory_manager(session, agent_id)


def memory_entry_to_response(entry: ShortTermMemoryEntry) -> MemoryResponse:
    """Convert ShortTermMemoryEntry to response model."""
    return MemoryResponse(
        memory_id=str(entry.memory_id),
        agent_id=str(entry.agent_id),
        memory_type=entry.memory_type,
        content=entry.content,
        significance=entry.significance,
        topic_keywords=entry.topic_keywords,
        created_at=entry.created_at.isoformat(),
        expires_at=entry.expires_at.isoformat(),
        project_id=str(entry.project_id) if entry.project_id else None,
        related_agents=entry.related_agents,
    )


def chapter_to_response(chapter: ProjectChapter) -> ChapterResponse:
    """Convert ProjectChapter to response model."""
    return ChapterResponse(
        chapter_id=str(chapter.chapter_id),
        agent_id=str(chapter.agent_id),
        project_id=str(chapter.project_id),
        title=chapter.title,
        summary=chapter.summary,
        role_in_project=chapter.role_in_project,
        start_date=chapter.start_date.isoformat(),
        end_date=chapter.end_date.isoformat() if chapter.end_date else None,
        outcome=chapter.outcome,
        significance=chapter.significance,
        lessons_learned=chapter.lessons_learned,
        collaborators=chapter.collaborators,
    )


# ==========================================
# API Endpoints
# ==========================================


@router.post(
    "/agents/{agent_id}/memories",
    response_model=MemoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record a memory",
    description="Record a significant event to short-term memory.",
)
async def record_memory(
    agent_id: UUID,
    request: RecordMemoryRequest,
    session: AsyncSession = Depends(get_db),
    repo: AgentRepository = Depends(AgentRepo),
) -> MemoryResponse:
    """Record a memory for an agent."""
    manager = await get_memory_manager(agent_id, session, repo)
    
    entry = await manager.record_significant_event(
        content=request.content,
        memory_type=request.memory_type,
        significance=request.significance,
        topic=request.topic,
        project_id=request.project_id,
        related_agents=request.related_agents,
    )
    
    return memory_entry_to_response(entry)


@router.get(
    "/agents/{agent_id}/memories",
    response_model=List[MemoryResponse],
    summary="Query memories",
    description="Query short-term memories with optional filters.",
)
async def query_memories(
    agent_id: UUID,
    topic: Optional[str] = Query(None, description="Topic to search for"),
    memory_type: Optional[str] = Query(None, description="Filter by type"),
    min_significance: float = Query(0.0, ge=0.0, le=1.0, description="Min significance"),
    max_results: int = Query(10, ge=1, le=50, description="Max results"),
    session: AsyncSession = Depends(get_db),
    repo: AgentRepository = Depends(AgentRepo),
) -> List[MemoryResponse]:
    """Query memories for an agent."""
    manager = await get_memory_manager(agent_id, session, repo)
    
    entries = await manager.short_term.query_entries(
        keywords=[topic] if topic else None,
        memory_type=memory_type,
        min_significance=min_significance,
        max_results=max_results,
    )
    
    return [memory_entry_to_response(entry) for entry in entries]


@router.post(
    "/agents/{agent_id}/memories/context",
    response_model=MemoryContextResponse,
    summary="Get tier-appropriate memory context",
    description="Get memory context formatted for a specific cognitive tier.",
)
async def get_memory_context(
    agent_id: UUID,
    request: MemoryContextRequest,
    session: AsyncSession = Depends(get_db),
    repo: AgentRepository = Depends(AgentRepo),
) -> MemoryContextResponse:
    """Get memory context for a cognitive tier."""
    manager = await get_memory_manager(agent_id, session, repo)
    
    # Parse tier
    try:
        tier = CognitiveTier[request.tier.upper()]
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid tier: {request.tier}. Valid: REFLEX, REACTIVE, DELIBERATE, ANALYTICAL, COMPREHENSIVE",
        )
    
    context = await manager.get_context_for_tier(tier, topic=request.topic)
    
    # Estimate tokens (chars / 4)
    token_estimate = len(context) // 4
    
    return MemoryContextResponse(
        tier=request.tier.upper(),
        context=context,
        token_estimate=token_estimate,
    )


@router.post(
    "/agents/{agent_id}/chapters",
    response_model=ChapterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a project chapter",
    description="Add a long-term memory chapter for a project.",
)
async def add_chapter(
    agent_id: UUID,
    request: AddChapterRequest,
    session: AsyncSession = Depends(get_db),
    repo: AgentRepository = Depends(AgentRepo),
) -> ChapterResponse:
    """Add a project chapter for an agent."""
    manager = await get_memory_manager(agent_id, session, repo)
    
    chapter = await manager.long_term.add_chapter(
        project_id=request.project_id,
        title=request.title,
        summary=request.summary,
        role=request.role,
        outcome=request.outcome,
        significance=request.significance,
        lessons=request.lessons,
        collaborators=request.collaborators,
    )
    
    return chapter_to_response(chapter)


@router.get(
    "/agents/{agent_id}/chapters",
    response_model=List[ChapterResponse],
    summary="Search project chapters",
    description="Search long-term memory chapters.",
)
async def search_chapters(
    agent_id: UUID,
    topic: Optional[str] = Query(None, description="Topic to search for"),
    outcome: Optional[str] = Query(None, description="Filter by outcome"),
    project_id: Optional[UUID] = Query(None, description="Filter by project"),
    max_results: int = Query(10, ge=1, le=50, description="Max results"),
    session: AsyncSession = Depends(get_db),
    repo: AgentRepository = Depends(AgentRepo),
) -> List[ChapterResponse]:
    """Search chapters for an agent."""
    manager = await get_memory_manager(agent_id, session, repo)
    
    chapters = await manager.long_term.search_chapters(
        topic=topic,
        outcome=outcome,
        project_id=project_id,
        max_results=max_results,
    )
    
    return [chapter_to_response(chapter) for chapter in chapters]


@router.get(
    "/agents/{agent_id}/chapters/{chapter_id}",
    response_model=ChapterResponse,
    summary="Get a chapter by ID",
    description="Retrieve a specific project chapter.",
)
async def get_chapter(
    agent_id: UUID,
    chapter_id: UUID,
    session: AsyncSession = Depends(get_db),
    repo: AgentRepository = Depends(AgentRepo),
) -> ChapterResponse:
    """Get a chapter by ID."""
    manager = await get_memory_manager(agent_id, session, repo)
    
    chapter = await manager.long_term.get_by_id(chapter_id)
    
    if chapter is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chapter {chapter_id} not found",
        )
    
    return chapter_to_response(chapter)


@router.get(
    "/agents/{agent_id}/working",
    response_model=WorkingMemoryStateResponse,
    summary="Get working memory state",
    description="Get the current state of working memory.",
)
async def get_working_memory_state(
    agent_id: UUID,
    repo: AgentRepository = Depends(AgentRepo),
) -> WorkingMemoryStateResponse:
    """Get working memory state for an agent."""
    # Verify agent exists
    agent = await repo.get(agent_id)
    if agent is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found",
        )
    
    # Create fresh working memory for this request
    # In production, this would be managed by AgentManager
    working = WorkingMemory()
    state = working.get_state()
    
    return WorkingMemoryStateResponse(**state)


@router.post(
    "/agents/{agent_id}/memories/promote",
    response_model=ChapterResponse,
    summary="Promote memory to long-term",
    description="Promote a short-term memory to a long-term chapter.",
)
async def promote_memory(
    agent_id: UUID,
    request: PromoteMemoryRequest,
    session: AsyncSession = Depends(get_db),
    repo: AgentRepository = Depends(AgentRepo),
) -> ChapterResponse:
    """Promote a short-term memory to long-term."""
    manager = await get_memory_manager(agent_id, session, repo)
    
    chapter = await manager.promote_memory(
        memory_id=request.memory_id,
        project_id=request.project_id,
        title=request.title,
        lessons=request.lessons,
    )
    
    if chapter is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Memory {request.memory_id} not found",
        )
    
    return chapter_to_response(chapter)


@router.delete(
    "/agents/{agent_id}/memories/expired",
    status_code=status.HTTP_200_OK,
    summary="Clean up expired memories",
    description="Delete all expired short-term memories.",
)
async def cleanup_expired_memories(
    agent_id: UUID,
    session: AsyncSession = Depends(get_db),
    repo: AgentRepository = Depends(AgentRepo),
) -> Dict[str, int]:
    """Clean up expired memories for an agent."""
    manager = await get_memory_manager(agent_id, session, repo)
    
    deleted = await manager.cleanup_expired()
    
    return {"deleted_count": deleted}


@router.get(
    "/tiers",
    summary="Get memory access by tier",
    description="Get information about memory access for each cognitive tier.",
)
async def get_memory_tiers() -> List[Dict[str, Any]]:
    """Get memory access configuration for each tier."""
    from src.cognitive.tiers import TIER_CONFIGS
    
    return [
        {
            "tier": tier.name,
            "memory_access": config.memory_access.value,
            "max_memory_tokens": config.max_tokens // 4,  # Approximate
            "description": _get_tier_memory_description(tier),
        }
        for tier, config in TIER_CONFIGS.items()
    ]


def _get_tier_memory_description(tier: CognitiveTier) -> str:
    """Get description of memory access for a tier."""
    descriptions = {
        CognitiveTier.REFLEX: "Working memory only - minimal context for fast responses",
        CognitiveTier.REACTIVE: "Working memory + recent short-term memories",
        CognitiveTier.DELIBERATE: "Working memory + indexed short-term memories by topic",
        CognitiveTier.ANALYTICAL: "Full access to all memory tiers including long-term",
        CognitiveTier.COMPREHENSIVE: "Full access to all memory tiers with maximum context",
    }
    return descriptions.get(tier, "Unknown tier")

