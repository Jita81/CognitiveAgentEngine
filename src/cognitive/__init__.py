"""Cognitive processing module (Phase 3).

This module provides tiered cognitive processing capabilities:
- 5 cognitive tiers (REFLEX → COMPREHENSIVE)
- Strategy planning based on stimulus characteristics
- Parallel and sequential tier execution
- Thought model with confidence and completeness metrics
"""

from src.cognitive.models import (
    CognitiveResult,
    ProcessingStrategy,
    StimulusInput,
    Thought,
    ThoughtType,
)
from src.cognitive.processor import CognitiveProcessor, create_processor_with_mock_router
from src.cognitive.prompts import TieredPromptBuilder
from src.cognitive.tiers import (
    CognitiveTier,
    ContextDepth,
    MemoryAccess,
    ResponseFormat,
    TierConfig,
    TIER_CONFIGS,
    get_tier_config,
    get_all_tier_configs,
)

__all__ = [
    # Tiers
    "CognitiveTier",
    "ContextDepth",
    "MemoryAccess",
    "ResponseFormat",
    "TierConfig",
    "TIER_CONFIGS",
    "get_tier_config",
    "get_all_tier_configs",
    # Models
    "Thought",
    "ThoughtType",
    "CognitiveResult",
    "ProcessingStrategy",
    "StimulusInput",
    # Processor
    "CognitiveProcessor",
    "create_processor_with_mock_router",
    # Prompts
    "TieredPromptBuilder",
]
