"""Model router for cognitive tier-based inference routing."""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Optional

from src.cognitive.tiers import CognitiveTier, TIER_CONFIGS
from src.infrastructure.budget_manager import TokenBudgetManager
from src.infrastructure.model_client import (
    InferenceRequest,
    InferenceResponse,
    ModelClient,
    ModelClientProtocol,
    ModelTier,
)

logger = logging.getLogger(__name__)


@dataclass
class CognitiveTierConfig:
    """Configuration for a cognitive tier (router-specific).
    
    Maps cognitive tiers to model tiers with timeout settings.
    """

    tier: CognitiveTier
    max_tokens: int
    timeout_ms: int
    model_tier: ModelTier

    @property
    def timeout_seconds(self) -> float:
        """Get timeout in seconds."""
        return self.timeout_ms / 1000


# Cognitive tier to model tier mappings
COGNITIVE_TIER_CONFIGS: Dict[CognitiveTier, CognitiveTierConfig] = {
    CognitiveTier.REFLEX: CognitiveTierConfig(
        tier=CognitiveTier.REFLEX,
        max_tokens=150,
        timeout_ms=500,
        model_tier=ModelTier.SMALL,
    ),
    CognitiveTier.REACTIVE: CognitiveTierConfig(
        tier=CognitiveTier.REACTIVE,
        max_tokens=400,
        timeout_ms=1000,
        model_tier=ModelTier.MEDIUM,
    ),
    CognitiveTier.DELIBERATE: CognitiveTierConfig(
        tier=CognitiveTier.DELIBERATE,
        max_tokens=1200,
        timeout_ms=3000,
        model_tier=ModelTier.LARGE,
    ),
    CognitiveTier.ANALYTICAL: CognitiveTierConfig(
        tier=CognitiveTier.ANALYTICAL,
        max_tokens=2500,
        timeout_ms=7000,
        model_tier=ModelTier.LARGE,
    ),
    CognitiveTier.COMPREHENSIVE: CognitiveTierConfig(
        tier=CognitiveTier.COMPREHENSIVE,
        max_tokens=4000,
        timeout_ms=12000,
        model_tier=ModelTier.LARGE,
    ),
}


@dataclass
class RouterStatus:
    """Status of the model router."""

    health: Dict[str, bool]
    budget: dict
    last_health_check: Optional[datetime]
    active_requests: int

    def to_dict(self) -> dict:
        """Convert to dictionary for API response."""
        return {
            "health": self.health,
            "budget": self.budget,
            "last_health_check": (
                self.last_health_check.isoformat() if self.last_health_check else None
            ),
            "active_requests": self.active_requests,
        }


@dataclass
class RoutingDecision:
    """Record of a routing decision for debugging/metrics."""

    cognitive_tier: CognitiveTier
    target_model_tier: ModelTier
    actual_model_tier: ModelTier
    was_downgraded: bool
    downgrade_reason: Optional[str]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class ModelRouter:
    """Routes inference requests to appropriate model tier.

    Features:
    - Cognitive tier to model tier mapping
    - Budget-aware tier downgrade
    - Health-aware fallback routing
    - Timeout handling
    - Request tracking
    """

    def __init__(
        self,
        clients: Dict[ModelTier, ModelClientProtocol],
        budget_manager: TokenBudgetManager,
    ):
        """Initialize the router.

        Args:
            clients: Dictionary mapping ModelTier to client instances
            budget_manager: Budget manager for tracking and throttling
        """
        self.clients = clients
        self.budget_manager = budget_manager

        # Health status tracking
        self._health_status: Dict[ModelTier, bool] = {tier: True for tier in ModelTier}
        self._last_health_check: Optional[datetime] = None

        # Active request tracking
        self._active_requests: int = 0

        # Routing history (for debugging)
        self._routing_history: list[RoutingDecision] = []
        self._max_history: int = 100

    async def route(
        self,
        cognitive_tier: CognitiveTier,
        request: InferenceRequest,
        agent_id: str,
    ) -> InferenceResponse:
        """Route request to appropriate model tier.

        Args:
            cognitive_tier: The cognitive tier for processing
            request: The inference request
            agent_id: ID of the requesting agent

        Returns:
            InferenceResponse from the selected model

        Raises:
            RuntimeError: If no model is available
        """
        self._active_requests += 1
        try:
            # Get tier configuration
            tier_config = COGNITIVE_TIER_CONFIGS[cognitive_tier]
            target_tier = tier_config.model_tier

            # Determine actual tier (may be downgraded)
            actual_tier, downgrade_reason = self._select_tier(target_tier)

            # Record routing decision
            decision = RoutingDecision(
                cognitive_tier=cognitive_tier,
                target_model_tier=target_tier,
                actual_model_tier=actual_tier,
                was_downgraded=actual_tier != target_tier,
                downgrade_reason=downgrade_reason,
            )
            self._record_decision(decision)

            if downgrade_reason:
                logger.info(
                    f"Routing {cognitive_tier.name}: {target_tier.value} -> "
                    f"{actual_tier.value} ({downgrade_reason})"
                )

            # Get client and enforce token limit
            client = self.clients[actual_tier]
            request.max_tokens = min(request.max_tokens, tier_config.max_tokens)

            # Execute with timeout
            try:
                response = await asyncio.wait_for(
                    client.generate(request),
                    timeout=tier_config.timeout_seconds,
                )

                # Record usage
                self.budget_manager.record_usage(
                    actual_tier, response.total_tokens, agent_id
                )

                return response

            except asyncio.TimeoutError:
                logger.warning(f"Timeout on {actual_tier.value}, trying fallback")
                return await self._handle_timeout(
                    cognitive_tier, request, agent_id, actual_tier
                )

        except Exception as e:
            logger.error(f"Error in route(): {e}")
            # Mark tier as unhealthy
            if "actual_tier" in locals():
                self._health_status[actual_tier] = False
            raise

        finally:
            self._active_requests -= 1

    def _select_tier(self, target_tier: ModelTier) -> tuple[ModelTier, Optional[str]]:
        """Select the actual tier to use, considering budget and health.

        Args:
            target_tier: The desired model tier

        Returns:
            Tuple of (actual_tier, downgrade_reason or None)
        """
        # Check budget throttling
        if self.budget_manager.should_throttle(target_tier):
            downgrade = self.budget_manager.recommend_downgrade(target_tier)
            if downgrade:
                return downgrade, "budget_throttle"

        # Check health
        if not self._health_status[target_tier]:
            fallback = self._get_fallback(target_tier)
            if fallback:
                return fallback, "unhealthy"
            # No fallback available, try anyway
            logger.warning(f"No healthy fallback for {target_tier.value}")

        return target_tier, None

    def _get_fallback(self, tier: ModelTier) -> Optional[ModelTier]:
        """Get a fallback tier if available.

        Args:
            tier: The tier that needs a fallback

        Returns:
            A healthy lower tier, or None
        """
        fallbacks = {
            ModelTier.LARGE: ModelTier.MEDIUM,
            ModelTier.MEDIUM: ModelTier.SMALL,
            ModelTier.SMALL: None,
        }

        fallback = fallbacks.get(tier)
        if fallback and self._health_status.get(fallback, False):
            return fallback
        return None

    async def _handle_timeout(
        self,
        cognitive_tier: CognitiveTier,
        request: InferenceRequest,
        agent_id: str,
        failed_tier: ModelTier,
    ) -> InferenceResponse:
        """Handle timeout by trying fallback tier.

        Args:
            cognitive_tier: Original cognitive tier
            request: The inference request
            agent_id: ID of the requesting agent
            failed_tier: The tier that timed out

        Returns:
            InferenceResponse from fallback tier

        Raises:
            RuntimeError: If no fallback available
        """
        fallback = self._get_fallback(failed_tier)

        if fallback:
            client = self.clients[fallback]
            response = await client.generate(request)
            self.budget_manager.record_usage(fallback, response.total_tokens, agent_id)
            return response

        raise RuntimeError(
            f"No available model for {cognitive_tier.name} after timeout"
        )

    async def check_health(self) -> Dict[ModelTier, bool]:
        """Check health of all model endpoints.

        Returns:
            Dictionary mapping tier to health status
        """
        results = {}
        for tier, client in self.clients.items():
            try:
                is_healthy = await client.health_check()
                results[tier] = is_healthy
                self._health_status[tier] = is_healthy
            except Exception as e:
                logger.error(f"Health check failed for {tier.value}: {e}")
                results[tier] = False
                self._health_status[tier] = False

        self._last_health_check = datetime.now(timezone.utc)
        return results

    def get_status(self) -> RouterStatus:
        """Get current router status.

        Returns:
            RouterStatus with health, budget, and metrics
        """
        return RouterStatus(
            health={tier.value: healthy for tier, healthy in self._health_status.items()},
            budget=self.budget_manager.get_status().to_dict(),
            last_health_check=self._last_health_check,
            active_requests=self._active_requests,
        )

    def get_tier_config(self, cognitive_tier: CognitiveTier) -> CognitiveTierConfig:
        """Get configuration for a cognitive tier.

        Args:
            cognitive_tier: The tier to get config for

        Returns:
            CognitiveTierConfig for the tier
        """
        return COGNITIVE_TIER_CONFIGS[cognitive_tier]

    def set_tier_health(self, tier: ModelTier, healthy: bool) -> None:
        """Manually set tier health status (for testing).

        Args:
            tier: The tier to set
            healthy: Health status
        """
        self._health_status[tier] = healthy

    def _record_decision(self, decision: RoutingDecision) -> None:
        """Record a routing decision for history."""
        self._routing_history.append(decision)
        if len(self._routing_history) > self._max_history:
            self._routing_history.pop(0)

    def get_routing_history(self, limit: int = 10) -> list[RoutingDecision]:
        """Get recent routing decisions.

        Args:
            limit: Maximum number of decisions to return

        Returns:
            List of recent RoutingDecision objects
        """
        return self._routing_history[-limit:]

    async def close(self) -> None:
        """Close all client connections."""
        for client in self.clients.values():
            await client.close()

    def __repr__(self) -> str:
        healthy_count = sum(1 for h in self._health_status.values() if h)
        total_count = len(self._health_status)
        return (
            f"ModelRouter(healthy={healthy_count}/{total_count}, "
            f"active_requests={self._active_requests})"
        )


def create_router_with_mock_clients(
    hourly_budget: float = 15.0,
) -> ModelRouter:
    """Create a router with mock clients for testing.

    Args:
        hourly_budget: Hourly budget in USD

    Returns:
        ModelRouter configured with mock clients
    """
    from src.infrastructure.model_client_mock import create_mock_clients

    clients = create_mock_clients()
    budget_manager = TokenBudgetManager(hourly_budget_usd=hourly_budget)

    return ModelRouter(clients=clients, budget_manager=budget_manager)
