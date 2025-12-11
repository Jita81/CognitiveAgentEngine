"""Cognitive tier configuration and definitions.

This module defines the 5-tier cognitive processing system:
- REFLEX: Immediate reactions (~150 tokens, <200ms)
- REACTIVE: Quick assessments (~400 tokens, <500ms)
- DELIBERATE: Considered responses (~1200 tokens, <2s)
- ANALYTICAL: Deep analysis (~2500 tokens, <5s)
- COMPREHENSIVE: Maximum depth (~4000 tokens, <10s)
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict


class CognitiveTier(Enum):
    """Cognitive processing tiers with increasing depth and cost.
    
    Each tier represents a different level of cognitive engagement:
    - Lower tiers are faster but shallower
    - Higher tiers are slower but more thorough
    """

    REFLEX = 0  # Immediate reactions
    REACTIVE = 1  # Quick assessments
    DELIBERATE = 2  # Considered responses
    ANALYTICAL = 3  # Deep analysis
    COMPREHENSIVE = 4  # Maximum depth


class MemoryAccess(Enum):
    """Memory access levels for cognitive tiers."""

    CACHED = "cached"  # In-memory cache only (fastest)
    RECENT = "recent"  # Recent conversation + cache
    INDEXED = "indexed"  # Keyword-indexed search
    FULL_SEARCH = "full_search"  # Full memory search


class ContextDepth(Enum):
    """Context depth levels for prompts."""

    MINIMAL = "minimal"  # Identity only
    SHALLOW = "shallow"  # Identity + brief context
    STANDARD = "standard"  # Full identity + memory
    DEEP = "deep"  # Full context + patterns
    FULL = "full"  # Maximum context


class ResponseFormat(Enum):
    """Expected response format for each tier."""

    BRIEF = "brief"  # 1-2 sentences
    MODERATE = "moderate"  # A paragraph
    THOROUGH = "thorough"  # Multiple paragraphs with structure


@dataclass(frozen=True)
class TierConfig:
    """Full configuration for a cognitive tier.
    
    Attributes:
        tier: The cognitive tier this config is for
        max_tokens: Maximum tokens for response
        target_latency_ms: Target latency in milliseconds
        memory_access: Level of memory access permitted
        context_depth: Depth of context to include in prompts
        can_interrupt: Whether this tier can be interrupted by higher priority
        runs_parallel: Whether multiple instances can run in parallel
        max_context_tokens: Maximum tokens for context in prompt
        response_format: Expected format of response
    """

    tier: CognitiveTier
    max_tokens: int
    target_latency_ms: int
    memory_access: MemoryAccess
    context_depth: ContextDepth
    can_interrupt: bool
    runs_parallel: bool
    max_context_tokens: int
    response_format: ResponseFormat

    @property
    def timeout_seconds(self) -> float:
        """Get timeout in seconds (slightly longer than target latency)."""
        # Give 50% more time than target for timeout
        return (self.target_latency_ms * 1.5) / 1000

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
        return {
            "tier": self.tier.name,
            "max_tokens": self.max_tokens,
            "target_latency_ms": self.target_latency_ms,
            "memory_access": self.memory_access.value,
            "context_depth": self.context_depth.value,
            "can_interrupt": self.can_interrupt,
            "runs_parallel": self.runs_parallel,
            "max_context_tokens": self.max_context_tokens,
            "response_format": self.response_format.value,
        }


# Tier configurations matching the build plan specifications
TIER_CONFIGS: Dict[CognitiveTier, TierConfig] = {
    CognitiveTier.REFLEX: TierConfig(
        tier=CognitiveTier.REFLEX,
        max_tokens=150,
        target_latency_ms=200,
        memory_access=MemoryAccess.CACHED,
        context_depth=ContextDepth.MINIMAL,
        can_interrupt=False,
        runs_parallel=True,
        max_context_tokens=100,
        response_format=ResponseFormat.BRIEF,
    ),
    CognitiveTier.REACTIVE: TierConfig(
        tier=CognitiveTier.REACTIVE,
        max_tokens=400,
        target_latency_ms=500,
        memory_access=MemoryAccess.RECENT,
        context_depth=ContextDepth.SHALLOW,
        can_interrupt=True,
        runs_parallel=True,
        max_context_tokens=300,
        response_format=ResponseFormat.BRIEF,
    ),
    CognitiveTier.DELIBERATE: TierConfig(
        tier=CognitiveTier.DELIBERATE,
        max_tokens=1200,
        target_latency_ms=2000,
        memory_access=MemoryAccess.INDEXED,
        context_depth=ContextDepth.STANDARD,
        can_interrupt=True,
        runs_parallel=False,
        max_context_tokens=600,
        response_format=ResponseFormat.MODERATE,
    ),
    CognitiveTier.ANALYTICAL: TierConfig(
        tier=CognitiveTier.ANALYTICAL,
        max_tokens=2500,
        target_latency_ms=5000,
        memory_access=MemoryAccess.FULL_SEARCH,
        context_depth=ContextDepth.DEEP,
        can_interrupt=True,
        runs_parallel=False,
        max_context_tokens=1000,
        response_format=ResponseFormat.THOROUGH,
    ),
    CognitiveTier.COMPREHENSIVE: TierConfig(
        tier=CognitiveTier.COMPREHENSIVE,
        max_tokens=4000,
        target_latency_ms=10000,
        memory_access=MemoryAccess.FULL_SEARCH,
        context_depth=ContextDepth.FULL,
        can_interrupt=True,
        runs_parallel=False,
        max_context_tokens=1500,
        response_format=ResponseFormat.THOROUGH,
    ),
}


def get_tier_config(tier: CognitiveTier) -> TierConfig:
    """Get configuration for a cognitive tier.
    
    Args:
        tier: The cognitive tier
        
    Returns:
        TierConfig for the specified tier
    """
    return TIER_CONFIGS[tier]


def get_all_tier_configs() -> Dict[str, dict]:
    """Get all tier configurations as dictionaries.
    
    Returns:
        Dictionary mapping tier names to their configurations
    """
    return {tier.name: config.to_dict() for tier, config in TIER_CONFIGS.items()}

