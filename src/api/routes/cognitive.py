"""Cognitive processing API routes."""

from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from src.agents.repository import AgentRepository
from src.api.dependencies import AgentRepo
from src.cognitive import (
    CognitiveTier,
    CognitiveProcessor,
    CognitiveResult,
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

