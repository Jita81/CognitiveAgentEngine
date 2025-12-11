"""Cognitive processing API routes.

Includes:
- Phase 3: Tiered cognitive processing endpoints
- Phase 4: Internal Mind state endpoints
"""

from typing import Annotated, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from src.agents.repository import AgentRepository
from src.api.dependencies import AgentRepo
from src.cognitive import (
    CognitiveTier,
    CognitiveProcessor,
    CognitiveResult,
    InternalMind,
    ThoughtAccumulator,
    BackgroundProcessor,
    create_background_processor,
    get_all_tier_configs,
    get_tier_config,
)
from src.infrastructure.model_router import ModelRouter, create_router_with_mock_clients

router = APIRouter(prefix="/v1/cognitive", tags=["cognitive"])


# ==========================================
# Request/Response Models
# ==========================================


class ProcessRequest(BaseModel):
    """Request to process a stimulus through cognitive tiers."""

    stimulus: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="The stimulus text to process",
    )
    agent_id: UUID = Field(..., description="ID of the agent to process with")
    urgency: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="How urgent (affects speed vs depth)",
    )
    complexity: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="How complex (affects tier selection)",
    )
    relevance: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="How relevant to the agent",
    )
    purpose: str = Field(
        default="general_response",
        max_length=100,
        description="Purpose of this processing",
    )
    context: Optional[dict] = Field(
        None,
        description="Additional context for processing",
    )


class ProcessResponse(BaseModel):
    """Response from cognitive processing."""

    thoughts: list = Field(description="All thoughts produced")
    primary_thought: Optional[dict] = Field(description="Most significant thought")
    processing_time_ms: float = Field(description="Processing time in milliseconds")
    tiers_used: list = Field(description="Cognitive tiers invoked")
    thought_count: int = Field(description="Number of thoughts produced")
    agent_id: str = Field(description="Agent that processed")


class TierProcessRequest(BaseModel):
    """Request to process with a specific tier."""

    stimulus: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="The stimulus text to process",
    )
    agent_id: UUID = Field(..., description="ID of the agent to process with")
    tier: str = Field(
        ...,
        description="Cognitive tier to use (REFLEX, REACTIVE, DELIBERATE, ANALYTICAL, COMPREHENSIVE)",
    )
    purpose: str = Field(
        default="direct_tier",
        max_length=100,
        description="Purpose of this processing",
    )
    context: Optional[dict] = Field(
        None,
        description="Additional context",
    )


class ThoughtResponse(BaseModel):
    """Response containing a single thought."""

    thought_id: str
    tier: str
    content: str
    thought_type: str
    trigger: str
    confidence: float
    completeness: float


class TierInfoResponse(BaseModel):
    """Information about a cognitive tier."""

    tier: str
    max_tokens: int
    target_latency_ms: int
    memory_access: str
    context_depth: str
    can_interrupt: bool
    runs_parallel: bool
    max_context_tokens: int
    response_format: str


# ==========================================
# Global Model Router (singleton for demo)
# Using mock clients for testing
# ==========================================

_model_router: Optional[ModelRouter] = None


def get_model_router() -> ModelRouter:
    """Get or create the model router singleton."""
    global _model_router
    if _model_router is None:
        _model_router = create_router_with_mock_clients(hourly_budget=15.0)
    return _model_router


ModelRouterDep = Annotated[ModelRouter, Depends(get_model_router)]


# ==========================================
# Endpoints
# ==========================================


@router.post(
    "/process",
    response_model=ProcessResponse,
    summary="Process stimulus through cognitive tiers",
    description="Process a stimulus using the agent's cognitive system with automatic tier selection.",
)
async def process_stimulus(
    request: ProcessRequest,
    repo: AgentRepo,
    model_router: ModelRouterDep,
) -> ProcessResponse:
    """Process a stimulus through the cognitive system.
    
    The system automatically selects appropriate cognitive tiers based on:
    - urgency: Higher urgency → faster tiers (REFLEX, REACTIVE)
    - complexity: Higher complexity → deeper tiers (DELIBERATE, ANALYTICAL)
    - relevance: Lower relevance → minimal processing
    """
    # Get the agent
    agent = await repo.get(request.agent_id)
    if agent is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {request.agent_id} not found",
        )

    # Create processor
    processor = CognitiveProcessor(agent=agent, model_router=model_router)

    # Process stimulus
    result = await processor.process(
        stimulus=request.stimulus,
        urgency=request.urgency,
        complexity=request.complexity,
        relevance=request.relevance,
        purpose=request.purpose,
        context=request.context,
    )

    # Convert to response
    return ProcessResponse(
        thoughts=[t.to_dict() for t in result.thoughts],
        primary_thought=result.primary_thought.to_dict() if result.primary_thought else None,
        processing_time_ms=result.processing_time_ms,
        tiers_used=[t.name for t in result.tiers_used],
        thought_count=len(result.thoughts),
        agent_id=str(request.agent_id),
    )


@router.post(
    "/process/tier",
    response_model=ThoughtResponse,
    summary="Process with specific tier",
    description="Process a stimulus using a specific cognitive tier (bypasses strategy planning).",
)
async def process_with_tier(
    request: TierProcessRequest,
    repo: AgentRepo,
    model_router: ModelRouterDep,
) -> ThoughtResponse:
    """Process a stimulus with a specific cognitive tier.
    
    Useful for testing or when a specific tier is required.
    """
    # Validate tier
    try:
        tier = CognitiveTier[request.tier.upper()]
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid tier: {request.tier}. Must be one of: REFLEX, REACTIVE, DELIBERATE, ANALYTICAL, COMPREHENSIVE",
        )

    # Get the agent
    agent = await repo.get(request.agent_id)
    if agent is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {request.agent_id} not found",
        )

    # Create processor
    processor = CognitiveProcessor(agent=agent, model_router=model_router)

    # Process with specific tier
    thought = await processor.process_with_tier_override(
        stimulus=request.stimulus,
        tier=tier,
        purpose=request.purpose,
        context=request.context,
    )

    # Convert to response
    return ThoughtResponse(
        thought_id=str(thought.thought_id),
        tier=thought.tier.name,
        content=thought.content,
        thought_type=thought.thought_type.value,
        trigger=thought.trigger,
        confidence=thought.confidence,
        completeness=thought.completeness,
    )


@router.get(
    "/tiers",
    summary="Get tier configurations",
    description="Get configuration details for all cognitive tiers.",
)
async def get_tiers() -> dict:
    """Get all cognitive tier configurations."""
    return {
        "tiers": get_all_tier_configs(),
        "tier_count": len(CognitiveTier),
    }


@router.get(
    "/tiers/{tier_name}",
    response_model=TierInfoResponse,
    summary="Get tier info",
    description="Get configuration details for a specific cognitive tier.",
)
async def get_tier_info(tier_name: str) -> TierInfoResponse:
    """Get information about a specific cognitive tier."""
    try:
        tier = CognitiveTier[tier_name.upper()]
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tier not found: {tier_name}. Must be one of: REFLEX, REACTIVE, DELIBERATE, ANALYTICAL, COMPREHENSIVE",
        )

    config = get_tier_config(tier)
    return TierInfoResponse(**config.to_dict())


@router.get(
    "/status",
    summary="Get cognitive system status",
    description="Get status of the cognitive processing system.",
)
async def get_status(model_router: ModelRouterDep) -> dict:
    """Get current status of the cognitive processing system."""
    router_status = model_router.get_status()
    return {
        "status": "operational",
        "model_router": router_status.to_dict(),
        "tiers_available": [t.name for t in CognitiveTier],
    }


# ==========================================
# Phase 4: Internal Mind Endpoints
# ==========================================


# Store for agent minds (in-memory for MVP)
# In production, this would be managed by an AgentManager service
_agent_minds: Dict[str, InternalMind] = {}
_background_processors: Dict[str, BackgroundProcessor] = {}


def get_or_create_mind(agent_id: UUID) -> InternalMind:
    """Get or create an InternalMind for an agent."""
    agent_id_str = str(agent_id)
    if agent_id_str not in _agent_minds:
        _agent_minds[agent_id_str] = InternalMind(agent_id=agent_id_str)
    return _agent_minds[agent_id_str]


class MindStateResponse(BaseModel):
    """Response with mind state information."""

    agent_id: str
    active_thoughts: int
    streams: int
    streams_needing_synthesis: int
    held_insights: int
    ready_to_share: int
    background_tasks: int
    stream_topics: List[str]


class MindDetailedStateResponse(MindStateResponse):
    """Detailed mind state response with stream info."""

    streams_detail: List[dict]
    ready_thoughts: List[dict]


class ReadyThoughtResponse(BaseModel):
    """Response containing a thought ready to share."""

    thought_id: str
    tier: str
    content: str
    thought_type: str
    confidence: float
    completeness: float


class InvalidateRequest(BaseModel):
    """Request to invalidate thoughts about a topic."""

    topic: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Topic to invalidate thoughts about",
    )


class InvalidateResponse(BaseModel):
    """Response from thought invalidation."""

    topic: str
    thoughts_invalidated: int


class ObservationRequest(BaseModel):
    """Request to process an observation."""

    stimulus: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="The observation to process",
    )
    relevance: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="How relevant this observation is to the agent",
    )
    context: Optional[dict] = Field(
        None,
        description="Additional context",
    )


@router.get(
    "/mind/{agent_id}/state",
    response_model=MindStateResponse,
    summary="Get mind state",
    description="Get the current state of an agent's internal mind.",
)
async def get_mind_state(
    agent_id: UUID,
    repo: AgentRepo,
) -> MindStateResponse:
    """Get the current state of an agent's internal mind.
    
    Returns summary information about active thoughts, streams,
    held insights, and thoughts ready to share.
    """
    # Verify agent exists
    agent = await repo.get(agent_id)
    if agent is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found",
        )

    mind = get_or_create_mind(agent_id)
    state = mind.get_state()

    return MindStateResponse(**state)


@router.get(
    "/mind/{agent_id}/state/detailed",
    response_model=MindDetailedStateResponse,
    summary="Get detailed mind state",
    description="Get detailed state of an agent's internal mind including stream info.",
)
async def get_mind_detailed_state(
    agent_id: UUID,
    repo: AgentRepo,
) -> MindDetailedStateResponse:
    """Get detailed state of an agent's internal mind.
    
    Returns full information including stream details and ready thoughts.
    """
    # Verify agent exists
    agent = await repo.get(agent_id)
    if agent is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found",
        )

    mind = get_or_create_mind(agent_id)
    state = mind.get_detailed_state()

    return MindDetailedStateResponse(**state)


@router.get(
    "/mind/{agent_id}/ready-thoughts",
    summary="Get thoughts ready to share",
    description="Get thoughts that are ready to be externalized/shared.",
)
async def get_ready_thoughts(
    agent_id: UUID,
    repo: AgentRepo,
) -> dict:
    """Get thoughts ready to be shared.
    
    Returns list of thoughts marked ready for externalization.
    """
    # Verify agent exists
    agent = await repo.get(agent_id)
    if agent is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found",
        )

    mind = get_or_create_mind(agent_id)

    return {
        "agent_id": str(agent_id),
        "count": len(mind.ready_to_share),
        "thoughts": [
            {
                "thought_id": str(t.thought_id),
                "tier": t.tier.name,
                "content": t.content,
                "thought_type": t.thought_type.value,
                "confidence": t.confidence,
                "completeness": t.completeness,
            }
            for t in mind.ready_to_share
        ],
    }


@router.get(
    "/mind/{agent_id}/best-contribution",
    summary="Get best thought to share",
    description="Get the best thought to share right now, if any.",
)
async def get_best_contribution(
    agent_id: UUID,
    repo: AgentRepo,
) -> dict:
    """Get the best thought to share.
    
    Selects the best thought based on relevance, confidence, and completeness.
    """
    # Verify agent exists
    agent = await repo.get(agent_id)
    if agent is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found",
        )

    mind = get_or_create_mind(agent_id)
    best = mind.get_best_contribution()

    if best is None:
        return {
            "agent_id": str(agent_id),
            "has_contribution": False,
            "thought": None,
        }

    return {
        "agent_id": str(agent_id),
        "has_contribution": True,
        "thought": {
            "thought_id": str(best.thought_id),
            "tier": best.tier.name,
            "content": best.content,
            "thought_type": best.thought_type.value,
            "confidence": best.confidence,
            "completeness": best.completeness,
        },
    }


@router.post(
    "/mind/{agent_id}/invalidate",
    response_model=InvalidateResponse,
    summary="Invalidate thoughts about topic",
    description="Mark thoughts about a topic as no longer relevant.",
)
async def invalidate_thoughts(
    agent_id: UUID,
    request: InvalidateRequest,
    repo: AgentRepo,
) -> InvalidateResponse:
    """Invalidate thoughts about a topic.
    
    Use when new information supersedes previous thinking.
    """
    # Verify agent exists
    agent = await repo.get(agent_id)
    if agent is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found",
        )

    mind = get_or_create_mind(agent_id)
    count = mind.invalidate_thoughts_about(request.topic)

    return InvalidateResponse(
        topic=request.topic,
        thoughts_invalidated=count,
    )


@router.post(
    "/mind/{agent_id}/observe",
    summary="Process an observation",
    description="Process an observation with low cognitive effort, accumulating in the mind.",
)
async def process_observation(
    agent_id: UUID,
    request: ObservationRequest,
    repo: AgentRepo,
    model_router: ModelRouterDep,
) -> dict:
    """Process an observation into the agent's mind.
    
    Creates small thought bubbles that accumulate, enabling
    "listening" behavior where thoughts build up before speaking.
    """
    # Get the agent
    agent = await repo.get(agent_id)
    if agent is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found",
        )

    # Get or create mind and processor
    mind = get_or_create_mind(agent_id)
    processor = CognitiveProcessor(agent=agent, model_router=model_router)
    accumulator = ThoughtAccumulator(mind=mind, processor=processor)

    # Process the observation
    thought = await accumulator.process_observation(
        stimulus=request.stimulus,
        relevance=request.relevance,
        context=request.context,
    )

    if thought is None:
        return {
            "agent_id": str(agent_id),
            "processed": False,
            "thought": None,
            "accumulation": accumulator.get_accumulation_summary(),
        }

    return {
        "agent_id": str(agent_id),
        "processed": True,
        "thought": {
            "thought_id": str(thought.thought_id),
            "tier": thought.tier.name,
            "content": thought.content,
            "thought_type": thought.thought_type.value,
            "confidence": thought.confidence,
        },
        "accumulation": accumulator.get_accumulation_summary(),
    }


@router.post(
    "/mind/{agent_id}/externalize/{thought_id}",
    summary="Mark thought as externalized",
    description="Mark a thought as having been spoken/shared.",
)
async def externalize_thought(
    agent_id: UUID,
    thought_id: UUID,
    repo: AgentRepo,
) -> dict:
    """Mark a thought as externalized.
    
    Call this after the thought has been shared/spoken.
    """
    # Verify agent exists
    agent = await repo.get(agent_id)
    if agent is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found",
        )

    mind = get_or_create_mind(agent_id)
    
    # Check if thought exists
    thought_id_str = str(thought_id)
    if thought_id_str not in mind.active_thoughts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Thought {thought_id} not found in agent's mind",
        )

    mind.mark_externalized(thought_id)

    return {
        "agent_id": str(agent_id),
        "thought_id": str(thought_id),
        "externalized": True,
    }


@router.delete(
    "/mind/{agent_id}",
    summary="Clear agent's mind",
    description="Clear all state from the agent's internal mind.",
)
async def clear_mind(
    agent_id: UUID,
    repo: AgentRepo,
) -> dict:
    """Clear all state from the agent's mind.
    
    Use with caution - this removes all accumulated thoughts.
    """
    # Verify agent exists
    agent = await repo.get(agent_id)
    if agent is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found",
        )

    mind = get_or_create_mind(agent_id)
    mind.clear()

    return {
        "agent_id": str(agent_id),
        "cleared": True,
    }

