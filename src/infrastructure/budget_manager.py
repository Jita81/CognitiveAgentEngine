"""Token budget manager for model inference cost control."""

import threading
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional

from src.infrastructure.model_client import ModelTier


# Cost estimates based on GPU costs / throughput
# These are estimates for self-hosted vLLM on cloud GPUs
COST_PER_1K_TOKENS: Dict[ModelTier, float] = {
    ModelTier.SMALL: 0.0002,  # T4: ~$0.40/hr, ~500 tok/s
    ModelTier.MEDIUM: 0.0012,  # A10G: ~$1.25/hr, ~300 tok/s
    ModelTier.LARGE: 0.0049,  # A100: ~$3.50/hr, ~200 tok/s
}

# Budget allocation by tier (percentages)
BUDGET_ALLOCATION: Dict[ModelTier, float] = {
    ModelTier.SMALL: 0.10,  # 10% - REFLEX tier
    ModelTier.MEDIUM: 0.25,  # 25% - REACTIVE tier
    ModelTier.LARGE: 0.50,  # 50% - DELIBERATE+ tiers
    # 15% reserved for infrastructure overhead
}

# Throttling thresholds by tier
THROTTLE_THRESHOLDS: Dict[ModelTier, float] = {
    ModelTier.SMALL: 0.95,  # Rarely throttle REFLEX
    ModelTier.MEDIUM: 0.85,  # Moderate throttling
    ModelTier.LARGE: 0.75,  # Earlier throttling for expensive tier
}


@dataclass
class TierBudgetStatus:
    """Status for a single tier's budget."""

    tier: ModelTier
    tokens_used: int
    cost_usd: float
    budget_usd: float
    utilization: float
    is_throttled: bool

    def to_dict(self) -> dict:
        """Convert to dictionary for API response."""
        return {
            "tier": self.tier.value,
            "tokens_used": self.tokens_used,
            "cost_usd": round(self.cost_usd, 4),
            "budget_usd": round(self.budget_usd, 2),
            "utilization": round(self.utilization, 3),
            "is_throttled": self.is_throttled,
        }


@dataclass
class BudgetStatus:
    """Overall budget status."""

    hour_start: datetime
    total_cost_usd: float
    hourly_budget_usd: float
    overall_utilization: float
    by_tier: Dict[ModelTier, TierBudgetStatus]
    top_agents: list  # List of (agent_id, tokens) tuples

    def to_dict(self) -> dict:
        """Convert to dictionary for API response."""
        return {
            "hour_start": self.hour_start.isoformat(),
            "total_cost_usd": round(self.total_cost_usd, 4),
            "hourly_budget_usd": self.hourly_budget_usd,
            "overall_utilization": round(self.overall_utilization, 3),
            "by_tier": {
                tier.value: status.to_dict() for tier, status in self.by_tier.items()
            },
            "top_agents": [
                {"agent_id": agent_id, "tokens": tokens}
                for agent_id, tokens in self.top_agents
            ],
        }


@dataclass
class TokenBudgetManager:
    """Manages token budget across model tiers.

    Thread-safe budget tracking with:
    - Hourly budget enforcement ($15/hour default)
    - Per-tier budget allocation
    - Per-agent usage tracking
    - Automatic hourly reset
    - Throttling recommendations
    """

    hourly_budget_usd: float = 15.0

    # Internal tracking (initialized in __post_init__)
    _hour_start: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    _tokens_by_tier: Dict[ModelTier, int] = field(
        default_factory=lambda: {tier: 0 for tier in ModelTier}
    )
    _tokens_by_agent: Dict[str, int] = field(default_factory=dict)
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def record_usage(self, tier: ModelTier, tokens: int, agent_id: str) -> None:
        """Record token usage for a request.

        Args:
            tier: The model tier used
            tokens: Number of tokens consumed
            agent_id: ID of the agent making the request
        """
        with self._lock:
            self._maybe_reset_hour()
            self._tokens_by_tier[tier] += tokens
            self._tokens_by_agent[agent_id] = (
                self._tokens_by_agent.get(agent_id, 0) + tokens
            )

    def should_throttle(self, tier: ModelTier) -> bool:
        """Check if a tier should be throttled.

        Args:
            tier: The model tier to check

        Returns:
            True if the tier has exceeded its throttle threshold
        """
        with self._lock:
            self._maybe_reset_hour()
            utilization = self._get_tier_utilization(tier)
            threshold = THROTTLE_THRESHOLDS.get(tier, 0.8)
            return utilization > threshold

    def recommend_downgrade(self, tier: ModelTier) -> Optional[ModelTier]:
        """Recommend a cheaper tier if budget is tight.

        Args:
            tier: The current tier being requested

        Returns:
            A lower tier to use, or None if no downgrade available/needed
        """
        downgrades = {
            ModelTier.LARGE: ModelTier.MEDIUM,
            ModelTier.MEDIUM: ModelTier.SMALL,
            ModelTier.SMALL: None,
        }

        downgrade = downgrades.get(tier)
        if downgrade and not self.should_throttle(downgrade):
            return downgrade
        return None

    def get_status(self) -> BudgetStatus:
        """Get current budget status.

        Returns:
            BudgetStatus with all tracking information
        """
        with self._lock:
            self._maybe_reset_hour()

            tier_statuses = {}
            for tier in ModelTier:
                tokens = self._tokens_by_tier[tier]
                cost = self._calculate_cost(tier, tokens)
                budget = self.hourly_budget_usd * BUDGET_ALLOCATION.get(tier, 0)
                utilization = cost / budget if budget > 0 else 0
                threshold = THROTTLE_THRESHOLDS.get(tier, 0.8)

                tier_statuses[tier] = TierBudgetStatus(
                    tier=tier,
                    tokens_used=tokens,
                    cost_usd=cost,
                    budget_usd=budget,
                    utilization=utilization,
                    is_throttled=utilization > threshold,
                )

            total_cost = sum(s.cost_usd for s in tier_statuses.values())

            # Get top agents by token usage
            sorted_agents = sorted(
                self._tokens_by_agent.items(), key=lambda x: x[1], reverse=True
            )
            top_agents = sorted_agents[:10]

            return BudgetStatus(
                hour_start=self._hour_start,
                total_cost_usd=total_cost,
                hourly_budget_usd=self.hourly_budget_usd,
                overall_utilization=(
                    total_cost / self.hourly_budget_usd
                    if self.hourly_budget_usd > 0
                    else 0
                ),
                by_tier=tier_statuses,
                top_agents=top_agents,
            )

    def get_agent_usage(self, agent_id: str) -> int:
        """Get token usage for a specific agent.

        Args:
            agent_id: The agent ID to look up

        Returns:
            Total tokens used by the agent this hour
        """
        with self._lock:
            self._maybe_reset_hour()
            return self._tokens_by_agent.get(agent_id, 0)

    def get_tier_tokens(self, tier: ModelTier) -> int:
        """Get token usage for a specific tier.

        Args:
            tier: The model tier to look up

        Returns:
            Total tokens used by the tier this hour
        """
        with self._lock:
            self._maybe_reset_hour()
            return self._tokens_by_tier.get(tier, 0)

    def reset(self) -> None:
        """Force reset of all counters."""
        with self._lock:
            self._hour_start = datetime.now(timezone.utc)
            self._tokens_by_tier = {tier: 0 for tier in ModelTier}
            self._tokens_by_agent = {}

    def _get_tier_utilization(self, tier: ModelTier) -> float:
        """Get utilization ratio for a tier (0-1+)."""
        tokens = self._tokens_by_tier.get(tier, 0)
        cost = self._calculate_cost(tier, tokens)
        budget = self.hourly_budget_usd * BUDGET_ALLOCATION.get(tier, 0)
        return cost / budget if budget > 0 else 0

    def _calculate_cost(self, tier: ModelTier, tokens: int) -> float:
        """Calculate cost for tokens at a tier."""
        cost_per_1k = COST_PER_1K_TOKENS.get(tier, 0)
        return tokens * cost_per_1k / 1000

    def _maybe_reset_hour(self) -> None:
        """Reset counters if hour has passed."""
        now = datetime.now(timezone.utc)
        if now - self._hour_start > timedelta(hours=1):
            self._hour_start = now
            self._tokens_by_tier = {tier: 0 for tier in ModelTier}
            self._tokens_by_agent = {}

    def __repr__(self) -> str:
        status = self.get_status()
        return (
            f"TokenBudgetManager("
            f"budget=${self.hourly_budget_usd}/hr, "
            f"used=${status.total_cost_usd:.4f}, "
            f"utilization={status.overall_utilization:.1%})"
        )
