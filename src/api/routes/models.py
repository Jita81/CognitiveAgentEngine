"""Model infrastructure API routes."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from src.infrastructure.model_client import InferenceRequest, ModelTier
from src.infrastructure.model_router import CognitiveTier, ModelRouter

router = APIRouter(prefix="/v1/models", tags=["models"])


# =============================================================================
# Pydantic Models for API
# =============================================================================


class GenerateRequest(BaseModel):
    """Request model for text generation."""

    prompt: str = Field(..., min_length=1, description="The prompt to generate from")
    cognitive_tier: str = Field(
        default="reactive",
        description="Cognitive tier: reflex, reactive, deliberate, analytical, comprehensive",
    )
    max_tokens: int = Field(default=256, ge=1, le=4096, description="Maximum tokens to generate")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Sampling temperature")
    agent_id: str = Field(default="default", description="Agent ID for tracking")


class GenerateResponse(BaseModel):
    """Response model for text generation."""

    text: str
    model_used: str
    tier_used: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    latency_ms: float


class TierStatusResponse(BaseModel):
    """Status for a single tier."""

    tier: str
    tokens_used: int
    cost_usd: float
    budget_usd: float
    utilization: float
    is_throttled: bool


class BudgetStatusResponse(BaseModel):
    """Budget status response."""

    hour_start: str
    total_cost_usd: float
    hourly_budget_usd: float
    overall_utilization: float
    by_tier: dict


class RouterStatusResponse(BaseModel):
    """Full router status response."""

    health: dict
    budget: BudgetStatusResponse
    last_health_check: Optional[str]
    active_requests: int


# =============================================================================
# Router Instance Management
# =============================================================================

# Global router instance (initialized on first request or startup)
_router_instance: Optional[ModelRouter] = None


def get_model_router() -> ModelRouter:
    """Get or create the model router instance.

    For testing, this uses mock clients. In production, configure
    with actual vLLM endpoints.
    """
    global _router_instance
    if _router_instance is None:
        from src.infrastructure.model_router import create_router_with_mock_clients

        _router_instance = create_router_with_mock_clients()
    return _router_instance


def set_model_router(router: ModelRouter) -> None:
    """Set the model router instance (for testing/configuration)."""
    global _router_instance
    _router_instance = router


# =============================================================================
# API Endpoints
# =============================================================================


@router.get(
    "/status",
    response_model=RouterStatusResponse,
    summary="Get model infrastructure status",
    description="Returns health status of all model tiers, budget utilization, and active requests.",
)
async def get_status(
    router: ModelRouter = Depends(get_model_router),
) -> RouterStatusResponse:
    """Get current model infrastructure status."""
    status = router.get_status()
    return RouterStatusResponse(
        health=status.health,
        budget=BudgetStatusResponse(**status.budget),
        last_health_check=(
            status.last_health_check.isoformat() if status.last_health_check else None
        ),
        active_requests=status.active_requests,
    )


@router.post(
    "/health-check",
    summary="Trigger health check",
    description="Triggers a health check of all model endpoints and returns results.",
)
async def trigger_health_check(
    router: ModelRouter = Depends(get_model_router),
) -> dict:
    """Trigger health check of all model endpoints."""
    results = await router.check_health()
    return {
        "status": "completed",
        "health": {tier.value: healthy for tier, healthy in results.items()},
    }


@router.post(
    "/generate",
    response_model=GenerateResponse,
    summary="Generate text (for testing)",
    description="Generate text using the model infrastructure. Primarily for testing.",
)
async def generate(
    request: GenerateRequest,
    router: ModelRouter = Depends(get_model_router),
) -> GenerateResponse:
    """Generate text using model infrastructure.

    This endpoint is primarily for testing the model infrastructure.
    In production, cognitive processing goes through the agent system.
    """
    # Parse cognitive tier
    try:
        cognitive_tier = CognitiveTier[request.cognitive_tier.upper()]
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid cognitive_tier: {request.cognitive_tier}. "
            f"Must be one of: {[t.name.lower() for t in CognitiveTier]}",
        )

    # Create inference request
    inference_request = InferenceRequest(
        prompt=request.prompt,
        max_tokens=request.max_tokens,
        temperature=request.temperature,
    )

    try:
        # Route request
        response = await router.route(
            cognitive_tier=cognitive_tier,
            request=inference_request,
            agent_id=request.agent_id,
        )

        return GenerateResponse(
            text=response.text,
            model_used=response.model_used,
            tier_used=response.tier_used.value,
            prompt_tokens=response.prompt_tokens,
            completion_tokens=response.completion_tokens,
            total_tokens=response.total_tokens,
            latency_ms=response.latency_ms,
        )

    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
        )


@router.get(
    "/tiers",
    summary="Get cognitive tier configurations",
    description="Returns configuration for all cognitive tiers including token limits and timeouts.",
)
async def get_tier_configs() -> dict:
    """Get cognitive tier configurations."""
    from src.infrastructure.model_router import COGNITIVE_TIER_CONFIGS

    return {
        "tiers": {
            tier.name.lower(): {
                "max_tokens": config.max_tokens,
                "timeout_ms": config.timeout_ms,
                "model_tier": config.model_tier.value,
            }
            for tier, config in COGNITIVE_TIER_CONFIGS.items()
        }
    }


@router.get(
    "/budget",
    summary="Get detailed budget status",
    description="Returns detailed budget information including per-agent usage.",
)
async def get_budget_status(
    router: ModelRouter = Depends(get_model_router),
) -> dict:
    """Get detailed budget status."""
    return router.budget_manager.get_status().to_dict()


@router.post(
    "/budget/reset",
    summary="Reset budget counters",
    description="Force reset of all budget counters. Use with caution.",
)
async def reset_budget(
    router: ModelRouter = Depends(get_model_router),
) -> dict:
    """Reset budget counters."""
    router.budget_manager.reset()
    return {"status": "reset", "message": "Budget counters have been reset"}

