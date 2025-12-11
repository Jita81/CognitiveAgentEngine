"""Cognitive processing module (Phases 3 & 4).

This module provides tiered cognitive processing capabilities:
- 5 cognitive tiers (REFLEX → COMPREHENSIVE)
- Strategy planning based on stimulus characteristics
- Parallel and sequential tier execution
- Thought model with confidence and completeness metrics

Phase 4 adds Internal Mind capabilities:
- InternalMind: Cognitive workspace where thoughts exist
- ThoughtStream: Groups of related thoughts
- ThoughtAccumulator: Accumulates and synthesizes thoughts
- BackgroundProcessor: Async background cognitive tasks
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
# Phase 4: Internal Mind
from src.cognitive.mind import (
    InternalMind,
    ThoughtStream,
    StreamStatus,
)
from src.cognitive.accumulator import ThoughtAccumulator
from src.cognitive.background import (
    BackgroundProcessor,
    create_background_processor,
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
    # Phase 4: Internal Mind
    "InternalMind",
    "ThoughtStream",
    "StreamStatus",
    "ThoughtAccumulator",
    "BackgroundProcessor",
    "create_background_processor",
]
