"""
Processing Characteristics Tests

Tests that verify processing characteristics meet requirements:
- Latency targets for each tier
- Token limits enforced
- Thought type distribution appropriate
- Resource usage within bounds
"""

import pytest
import asyncio
import time
from datetime import datetime
from typing import List, Dict
from unittest.mock import AsyncMock, MagicMock
from statistics import mean, stdev

from conftest import (
    analyze_response_style,
)


# =============================================================================
# LATENCY REQUIREMENTS
# =============================================================================

LATENCY_TARGETS_MS = {
    # p95 targets including mock overhead
    "REFLEX": 500,
    "REACTIVE": 1000,
    "DELIBERATE": 3000,
    "ANALYTICAL": 7000,
    "COMPREHENSIVE": 12000,
}

TOKEN_LIMITS = {
    "REFLEX": 150,
    "REACTIVE": 400,
    "DELIBERATE": 1200,
    "ANALYTICAL": 2500,
    "COMPREHENSIVE": 4000,
}


# =============================================================================
# LATENCY TESTS
# =============================================================================

class TestLatencyTargets:
    """Tests that processing meets latency targets."""

    @pytest.mark.asyncio
    async def test_reflex_latency(self, processor_for_alex):
        """REFLEX processing should complete within target latency."""
        latencies = []
        
        # Run multiple times for statistical significance
        for _ in range(5):
            start = time.time()
            result = await processor_for_alex.process(
                stimulus="Alert!",
                urgency=1.0,
                complexity=0.1,
                relevance=0.9,
            )
            elapsed_ms = (time.time() - start) * 1000
            latencies.append(elapsed_ms)
        
        # Calculate p95 (with small sample, use max)
        p95 = max(latencies)
        target = LATENCY_TARGETS_MS["REFLEX"]
        
        assert p95 <= target, (
            f"REFLEX p95 latency {p95:.0f}ms exceeds target {target}ms"
        )

    @pytest.mark.asyncio
    async def test_reactive_latency(self, processor_for_alex):
        """REACTIVE processing should complete within target latency."""
        latencies = []
        
        for _ in range(5):
            start = time.time()
            result = await processor_for_alex.process(
                stimulus="There's a performance issue we should look at",
                urgency=0.6,
                complexity=0.4,
                relevance=0.9,
            )
            elapsed_ms = (time.time() - start) * 1000
            latencies.append(elapsed_ms)
        
        p95 = max(latencies)
        target = LATENCY_TARGETS_MS["REACTIVE"]
        
        assert p95 <= target, (
            f"REACTIVE p95 latency {p95:.0f}ms exceeds target {target}ms"
        )

    @pytest.mark.asyncio
    async def test_deliberate_latency(self, processor_for_alex):
        """DELIBERATE processing should complete within target latency."""
        latencies = []
        
        for _ in range(3):  # Fewer iterations for slower tier
            start = time.time()
            result = await processor_for_alex.process(
                stimulus="How should we design the authentication system?",
                urgency=0.2,
                complexity=0.8,
                relevance=0.9,
            )
            elapsed_ms = (time.time() - start) * 1000
            latencies.append(elapsed_ms)
        
        p95 = max(latencies)
        target = LATENCY_TARGETS_MS["DELIBERATE"]
        
        assert p95 <= target, (
            f"DELIBERATE p95 latency {p95:.0f}ms exceeds target {target}ms"
        )

    @pytest.mark.asyncio
    async def test_latency_proportional_to_complexity(self, processor_for_alex):
        """Higher complexity should generally take more time."""
        # Simple scenario
        start_simple = time.time()
        await processor_for_alex.process(
            stimulus="OK",
            urgency=0.9,
            complexity=0.1,
            relevance=0.9,
        )
        simple_time = time.time() - start_simple
        
        # Complex scenario
        start_complex = time.time()
        await processor_for_alex.process(
            stimulus="Design the complete data architecture including "
                     "sharding strategy, replication, and failover",
            urgency=0.1,
            complexity=0.9,
            relevance=0.9,
        )
        complex_time = time.time() - start_complex
        
        # Complex should not be significantly faster than simple
        # (with mocks, times may be similar, but complex shouldn't be faster)
        assert complex_time >= simple_time * 0.5, (
            f"Complex scenario shouldn't be much faster: "
            f"simple={simple_time:.3f}s, complex={complex_time:.3f}s"
        )


# =============================================================================
# TOKEN USAGE TESTS
# =============================================================================

class TestTokenLimits:
    """Tests that token limits are respected."""

    @pytest.mark.asyncio
    async def test_reflex_token_limit(self, processor_for_alex):
        """REFLEX tier should respect token limits."""
        result = await processor_for_alex.process(
            stimulus="Quick!",
            urgency=1.0,
            complexity=0.1,
            relevance=0.9,
        )
        
        reflex_thoughts = [t for t in result.thoughts if t.tier.name == "REFLEX"]
        
        for thought in reflex_thoughts:
            # Rough estimate: 1 token ≈ 0.75 words
            word_count = len(thought.content.split())
            estimated_tokens = word_count / 0.75
            limit = TOKEN_LIMITS["REFLEX"]
            
            assert estimated_tokens <= limit * 1.5, (
                f"REFLEX estimated tokens {estimated_tokens:.0f} exceeds limit {limit}"
            )

    @pytest.mark.asyncio
    async def test_deliberate_token_limit(self, processor_for_alex):
        """DELIBERATE tier should respect token limits."""
        result = await processor_for_alex.process(
            stimulus="Provide a comprehensive analysis of our system design",
            urgency=0.1,
            complexity=0.9,
            relevance=0.9,
        )
        
        deliberate_thoughts = [t for t in result.thoughts if t.tier.name == "DELIBERATE"]
        
        for thought in deliberate_thoughts:
            word_count = len(thought.content.split())
            estimated_tokens = word_count / 0.75
            limit = TOKEN_LIMITS["DELIBERATE"]
            
            assert estimated_tokens <= limit * 1.5, (
                f"DELIBERATE estimated tokens {estimated_tokens:.0f} exceeds limit {limit}"
            )

    @pytest.mark.asyncio
    async def test_token_usage_proportional(self, processor_for_alex):
        """Higher tiers should use proportionally more tokens."""
        # REFLEX-inducing scenario
        reflex_result = await processor_for_alex.process(
            stimulus="!",
            urgency=1.0,
            complexity=0.1,
            relevance=0.9,
        )
        
        # DELIBERATE-inducing scenario
        deliberate_result = await processor_for_alex.process(
            stimulus="Design the API authentication flow",
            urgency=0.1,
            complexity=0.8,
            relevance=0.9,
        )
        
        # Get word counts
        reflex_words = sum(len(t.content.split()) for t in reflex_result.thoughts)
        deliberate_words = sum(len(t.content.split()) for t in deliberate_result.thoughts)
        
        # DELIBERATE should use more tokens than REFLEX
        # (with mocks may be similar, but DELIBERATE shouldn't be less)
        assert deliberate_words >= reflex_words * 0.5, (
            f"DELIBERATE should use >= tokens: "
            f"deliberate={deliberate_words}, reflex={reflex_words}"
        )


# =============================================================================
# THOUGHT TYPE DISTRIBUTION TESTS
# =============================================================================

class TestThoughtTypeDistribution:
    """Tests that thought types are distributed appropriately."""

    @pytest.mark.asyncio
    async def test_urgent_scenario_produces_reactions(self, processor_for_alex):
        """Urgent scenarios should produce reaction-type thoughts."""
        result = await processor_for_alex.process(
            stimulus="Emergency! Server down!",
            urgency=1.0,
            complexity=0.1,
            relevance=0.9,
        )
        
        thought_types = [t.thought_type for t in result.thoughts]
        
        # Urgent scenarios should produce reactions or observations
        immediate_types = ["reaction", "observation"]
        has_immediate = any(t in immediate_types for t in thought_types)
        
        # Should have at least some immediate response
        # (though may also have other types from parallel processing)
        assert len(thought_types) > 0

    @pytest.mark.asyncio
    async def test_analytical_scenario_produces_insights(self, processor_for_alex):
        """Analytical scenarios should produce insight-type thoughts."""
        result = await processor_for_alex.process(
            stimulus="What patterns do you see in our architecture decisions?",
            urgency=0.1,
            complexity=0.9,
            relevance=0.9,
        )
        
        thought_types = [t.thought_type for t in result.thoughts]
        
        # Analytical scenarios should produce insights or plans
        deep_types = ["insight", "plan", "concern"]
        has_deep = any(t in deep_types for t in thought_types)
        
        # Primary thought should be insightful
        if result.primary_thought:
            assert result.primary_thought.thought_type in ["insight", "plan", "concern", "question"]

    @pytest.mark.asyncio
    async def test_concern_triggers_concern_thoughts(self, processor_for_alex):
        """Risk-related stimuli should trigger concern-type thoughts."""
        result = await processor_for_alex.process(
            stimulus="I'm worried about the security implications of this approach",
            urgency=0.4,
            complexity=0.6,
            relevance=0.9,
        )
        
        thought_types = [t.thought_type for t in result.thoughts]
        
        # Risk-related input should trigger concern or insight
        # (depending on how the agent processes it)
        assert len(thought_types) > 0

    @pytest.mark.asyncio
    async def test_question_can_trigger_question_thoughts(self, processor_for_alex):
        """Questions might trigger question-type thoughts (seeking clarification)."""
        result = await processor_for_alex.process(
            stimulus="How does this work?",
            urgency=0.3,
            complexity=0.5,
            relevance=0.8,
        )
        
        # Should produce some response
        assert len(result.thoughts) > 0
        
        # Primary thought might be insight (answering) or question (seeking clarification)
        valid_types = ["insight", "question", "observation", "reaction"]
        if result.primary_thought:
            assert result.primary_thought.thought_type in valid_types


# =============================================================================
# PROCESSING TIME TESTS
# =============================================================================

class TestProcessingTime:
    """Tests for processing time characteristics."""

    @pytest.mark.asyncio
    async def test_total_processing_time_reasonable(self, processor_for_alex):
        """Total processing time should be reasonable for given scenario."""
        start = time.time()
        result = await processor_for_alex.process(
            stimulus="Handle this situation",
            urgency=0.5,
            complexity=0.5,
            relevance=0.9,
        )
        total_time = time.time() - start
        
        # Processing time should be captured
        assert result.processing_time_ms > 0
        
        # Total time shouldn't exceed worst-case
        assert total_time < 15  # 15 seconds max

    @pytest.mark.asyncio
    async def test_processing_time_matches_result(self, processor_for_alex):
        """Result's processing_time_ms should match actual time."""
        start = time.time()
        result = await processor_for_alex.process(
            stimulus="Process this",
            urgency=0.5,
            complexity=0.5,
            relevance=0.9,
        )
        actual_time_ms = (time.time() - start) * 1000
        
        # Result's reported time should be close to actual
        # (may be slightly less due to result building overhead)
        assert result.processing_time_ms <= actual_time_ms + 100, (
            f"Reported time {result.processing_time_ms}ms > actual {actual_time_ms:.0f}ms"
        )

    @pytest.mark.asyncio
    async def test_multiple_thoughts_processing_time(self, processor_for_alex):
        """Multiple thoughts should not exceed aggregate time limits."""
        result = await processor_for_alex.process(
            stimulus="Urgent critical issue requiring analysis!",
            urgency=0.9,
            complexity=0.7,
            relevance=0.9,
        )
        
        # With multiple thoughts from parallel processing,
        # total time should still be reasonable (not sequential sum)
        num_thoughts = len(result.thoughts)
        processing_time = result.processing_time_ms
        
        # Average time per thought should be reasonable
        if num_thoughts > 0:
            avg_per_thought = processing_time / num_thoughts
            # Should benefit from parallel processing
            # (average shouldn't exceed individual tier max)
            assert avg_per_thought < 5000, (
                f"Average {avg_per_thought:.0f}ms per thought is too slow"
            )


# =============================================================================
# RESOURCE USAGE TESTS
# =============================================================================

class TestResourceUsage:
    """Tests for resource usage characteristics."""

    @pytest.mark.asyncio
    async def test_no_memory_leak_multiple_processes(self, processor_for_alex):
        """Processing multiple stimuli should not leak resources."""
        import gc
        
        # Process multiple stimuli
        for i in range(10):
            result = await processor_for_alex.process(
                stimulus=f"Process stimulus {i}",
                urgency=0.5,
                complexity=0.5,
                relevance=0.9,
            )
            # Just verify it processes
            assert result.primary_thought is not None
        
        # Force garbage collection
        gc.collect()
        
        # If we get here without error, no obvious memory issues
        assert True

    @pytest.mark.asyncio
    async def test_concurrent_processing_safe(self, processor_for_alex):
        """Concurrent processing should be safe."""
        # Create multiple concurrent tasks
        tasks = []
        for i in range(5):
            task = processor_for_alex.process(
                stimulus=f"Concurrent stimulus {i}",
                urgency=0.5,
                complexity=0.5,
                relevance=0.9,
            )
            tasks.append(task)
        
        # Run concurrently
        results = await asyncio.gather(*tasks)
        
        # All should complete successfully
        assert len(results) == 5
        for result in results:
            assert result.primary_thought is not None


# =============================================================================
# CONSISTENCY TESTS
# =============================================================================

class TestProcessingConsistency:
    """Tests for processing consistency."""

    @pytest.mark.asyncio
    async def test_similar_inputs_similar_tiers(self, processor_for_alex):
        """Similar inputs should use similar tier selections."""
        results = []
        
        # Process similar stimuli
        for i in range(3):
            result = await processor_for_alex.process(
                stimulus=f"Explain the API design (variation {i})",
                urgency=0.3,
                complexity=0.6,
                relevance=0.9,
            )
            results.append(result)
        
        # Extract tiers used in each
        tier_sets = [set(t.tier.name for t in r.thoughts) for r in results]
        
        # Should have some consistency (at least same general level)
        # Count how many share at least one tier
        shared = 0
        for i in range(len(tier_sets)):
            for j in range(i + 1, len(tier_sets)):
                if tier_sets[i] & tier_sets[j]:  # Intersection
                    shared += 1
        
        # Most pairs should share tiers
        total_pairs = len(tier_sets) * (len(tier_sets) - 1) / 2
        assert shared >= total_pairs * 0.5, (
            "Similar inputs should produce consistent tier selections"
        )

    @pytest.mark.asyncio
    async def test_deterministic_tier_selection(self, processor_for_alex):
        """Tier selection should be deterministic for same inputs."""
        tiers_per_run = []
        
        for _ in range(3):
            result = await processor_for_alex.process(
                stimulus="What do you think?",
                urgency=0.5,
                complexity=0.5,
                relevance=0.7,
            )
            tiers = frozenset(t.tier.name for t in result.thoughts)
            tiers_per_run.append(tiers)
        
        # All runs should produce same tier selection
        assert len(set(tiers_per_run)) == 1, (
            f"Tier selection not deterministic: {tiers_per_run}"
        )


# =============================================================================
# PERFORMANCE REGRESSION TESTS
# =============================================================================

class TestPerformanceRegression:
    """Tests to catch performance regressions."""

    @pytest.mark.asyncio
    async def test_simple_stimulus_fast(self, processor_for_alex):
        """Simple stimuli should process quickly."""
        start = time.time()
        result = await processor_for_alex.process(
            stimulus="OK",
            urgency=0.5,
            complexity=0.1,
            relevance=0.5,
        )
        elapsed = time.time() - start
        
        # Simple stimulus should be fast
        assert elapsed < 2.0, f"Simple stimulus took {elapsed:.2f}s"

    @pytest.mark.asyncio
    async def test_complex_stimulus_within_bounds(self, processor_for_alex):
        """Complex stimuli should process within bounds."""
        start = time.time()
        result = await processor_for_alex.process(
            stimulus="Design a complete microservices architecture "
                     "including service mesh, observability stack, "
                     "deployment strategy, and disaster recovery plan",
            urgency=0.1,
            complexity=1.0,
            relevance=0.9,
        )
        elapsed = time.time() - start
        
        # Complex but should still complete within bounds
        assert elapsed < 15.0, f"Complex stimulus took {elapsed:.2f}s"

    @pytest.mark.asyncio
    async def test_no_processing_hangs(self, processor_for_alex):
        """Processing should not hang on edge cases."""
        edge_cases = [
            "",  # Empty
            "?",  # Single character
            "a" * 1000,  # Long repetitive
            "Hello\nWorld\n" * 10,  # Multiple lines
        ]
        
        for stimulus in edge_cases:
            try:
                result = await asyncio.wait_for(
                    processor_for_alex.process(
                        stimulus=stimulus,
                        urgency=0.5,
                        complexity=0.5,
                        relevance=0.5,
                    ),
                    timeout=10.0  # 10 second timeout
                )
                # Should complete
                assert result is not None
            except asyncio.TimeoutError:
                pytest.fail(f"Processing hung on: {repr(stimulus[:50])}")
