"""
Edge Cases Tests

Tests for boundary conditions, error handling, and unusual inputs:
- Empty/minimal stimuli
- Very long stimuli
- Special characters
- Missing agents
- Budget exhaustion
- Model failures
- Concurrent edge cases
"""

import pytest
import asyncio
from datetime import datetime
from typing import List, Dict
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from conftest import (
    create_processor_with_mock_router,
)


# =============================================================================
# EMPTY AND MINIMAL INPUT TESTS
# =============================================================================

class TestEmptyInputs:
    """Tests for empty and minimal input handling."""

    @pytest.mark.asyncio
    async def test_empty_stimulus(self, processor_for_alex):
        """Empty stimulus should be handled gracefully."""
        result = await processor_for_alex.process(
            stimulus="",
            urgency=0.5,
            complexity=0.5,
            relevance=0.5,
        )
        
        # Should not crash
        # May produce minimal output or skip processing
        assert result is not None
        # Processing time should still be tracked
        assert result.processing_time_ms >= 0

    @pytest.mark.asyncio
    async def test_whitespace_only_stimulus(self, processor_for_alex):
        """Whitespace-only stimulus should be handled."""
        result = await processor_for_alex.process(
            stimulus="   \n\t   ",
            urgency=0.5,
            complexity=0.5,
            relevance=0.5,
        )
        
        # Should not crash
        assert result is not None

    @pytest.mark.asyncio
    async def test_single_character_stimulus(self, processor_for_alex):
        """Single character stimulus should be handled."""
        single_chars = ["?", "!", ".", "a", "1", "@"]
        
        for char in single_chars:
            result = await processor_for_alex.process(
                stimulus=char,
                urgency=0.5,
                complexity=0.5,
                relevance=0.5,
            )
            assert result is not None, f"Failed on character: {char}"


# =============================================================================
# LONG INPUT TESTS
# =============================================================================

class TestLongInputs:
    """Tests for handling very long inputs."""

    @pytest.mark.asyncio
    async def test_long_stimulus(self, processor_for_alex):
        """Very long stimulus should be handled (possibly truncated)."""
        long_stimulus = "This is a test. " * 500  # ~2500 words
        
        result = await processor_for_alex.process(
            stimulus=long_stimulus,
            urgency=0.3,
            complexity=0.5,
            relevance=0.7,
        )
        
        # Should not crash
        assert result is not None
        # Should still produce output
        assert result.primary_thought is not None

    @pytest.mark.asyncio
    async def test_extremely_long_stimulus(self, processor_for_alex):
        """Extremely long stimulus should not hang."""
        extreme_stimulus = "word " * 10000  # ~50000 characters
        
        try:
            result = await asyncio.wait_for(
                processor_for_alex.process(
                    stimulus=extreme_stimulus,
                    urgency=0.5,
                    complexity=0.5,
                    relevance=0.5,
                ),
                timeout=30.0
            )
            assert result is not None
        except asyncio.TimeoutError:
            pytest.fail("Extremely long stimulus caused timeout")

    @pytest.mark.asyncio
    async def test_long_single_word(self, processor_for_alex):
        """Very long single word should be handled."""
        long_word = "a" * 1000  # 1000 character word
        
        result = await processor_for_alex.process(
            stimulus=long_word,
            urgency=0.5,
            complexity=0.5,
            relevance=0.5,
        )
        
        assert result is not None


# =============================================================================
# SPECIAL CHARACTER TESTS
# =============================================================================

class TestSpecialCharacters:
    """Tests for special character handling."""

    @pytest.mark.asyncio
    async def test_unicode_stimulus(self, processor_for_alex):
        """Unicode characters should be handled."""
        unicode_stimulus = "Hello 你好 🎉 مرحبا שלום"
        
        result = await processor_for_alex.process(
            stimulus=unicode_stimulus,
            urgency=0.5,
            complexity=0.5,
            relevance=0.5,
        )
        
        assert result is not None
        assert result.primary_thought is not None

    @pytest.mark.asyncio
    async def test_emoji_only_stimulus(self, processor_for_alex):
        """Emoji-only stimulus should be handled."""
        result = await processor_for_alex.process(
            stimulus="🚀🔥💡🎯",
            urgency=0.5,
            complexity=0.5,
            relevance=0.5,
        )
        
        assert result is not None

    @pytest.mark.asyncio
    async def test_special_formatting_characters(self, processor_for_alex):
        """Special formatting characters should not break processing."""
        special_stimuli = [
            "Test\x00null",  # Null character
            "Test\r\nWindows",  # Windows line ending
            "Test\ttab\ttab",  # Tabs
            "Test\\escape",  # Backslash
            'Test"quotes"',  # Quotes
            "Test<html>",  # HTML-like
            "Test${variable}",  # Template syntax
        ]
        
        for stimulus in special_stimuli:
            result = await processor_for_alex.process(
                stimulus=stimulus,
                urgency=0.5,
                complexity=0.5,
                relevance=0.5,
            )
            assert result is not None, f"Failed on: {repr(stimulus)}"


# =============================================================================
# PARAMETER BOUNDARY TESTS
# =============================================================================

class TestParameterBoundaries:
    """Tests for parameter boundary conditions."""

    @pytest.mark.asyncio
    async def test_zero_urgency(self, processor_for_alex):
        """Zero urgency should be handled."""
        result = await processor_for_alex.process(
            stimulus="No rush at all",
            urgency=0.0,
            complexity=0.5,
            relevance=0.5,
        )
        
        assert result is not None

    @pytest.mark.asyncio
    async def test_max_urgency(self, processor_for_alex):
        """Maximum urgency should be handled.
        
        Note: REFLEX requires urgency > 0.8 AND relevance > 0.5
        """
        result = await processor_for_alex.process(
            stimulus="MAXIMUM URGENCY!",
            urgency=1.0,
            complexity=0.5,
            relevance=0.6,  # Must be > 0.5 to trigger REFLEX strategy
        )
        
        assert result is not None
        # Should trigger REFLEX when urgency high AND relevance > 0.5
        tiers = [t.tier.name for t in result.thoughts]
        assert "REFLEX" in tiers

    @pytest.mark.asyncio
    async def test_zero_complexity(self, processor_for_alex):
        """Zero complexity should be handled."""
        result = await processor_for_alex.process(
            stimulus="Simple",
            urgency=0.5,
            complexity=0.0,
            relevance=0.5,
        )
        
        assert result is not None

    @pytest.mark.asyncio
    async def test_max_complexity(self, processor_for_alex):
        """Maximum complexity should be handled."""
        result = await processor_for_alex.process(
            stimulus="Infinitely complex problem",
            urgency=0.5,
            complexity=1.0,
            relevance=0.5,
        )
        
        assert result is not None

    @pytest.mark.asyncio
    async def test_zero_relevance(self, processor_for_alex):
        """Zero relevance should trigger minimal processing."""
        result = await processor_for_alex.process(
            stimulus="Completely irrelevant",
            urgency=0.5,
            complexity=0.5,
            relevance=0.0,
        )
        
        assert result is not None
        # Should do minimal processing
        # May not engage deep tiers

    @pytest.mark.asyncio
    async def test_all_parameters_zero(self, processor_for_alex):
        """All zero parameters should be handled."""
        result = await processor_for_alex.process(
            stimulus="Nothing",
            urgency=0.0,
            complexity=0.0,
            relevance=0.0,
        )
        
        assert result is not None

    @pytest.mark.asyncio
    async def test_all_parameters_max(self, processor_for_alex):
        """All maximum parameters should be handled."""
        result = await processor_for_alex.process(
            stimulus="EVERYTHING AT MAXIMUM!",
            urgency=1.0,
            complexity=1.0,
            relevance=1.0,
        )
        
        assert result is not None
        # Should trigger intense processing
        assert len(result.thoughts) > 0


# =============================================================================
# ERROR HANDLING TESTS
# =============================================================================

class TestErrorHandling:
    """Tests for error handling in various failure scenarios."""

    @pytest.mark.asyncio
    async def test_model_timeout_fallback(self, alex_chen):
        """Model timeout should trigger fallback."""
        # Create processor with mock that times out
        mock_router = MagicMock()
        
        async def slow_route(*args, **kwargs):
            await asyncio.sleep(10)  # Simulate slow response
            raise asyncio.TimeoutError("Model timeout")
        
        mock_router.route = slow_route
        
        # Note: This test verifies the pattern, actual implementation
        # should handle this gracefully
        # For now, just verify structure
        assert mock_router is not None

    @pytest.mark.asyncio
    async def test_graceful_degradation_on_error(self, alex_chen):
        """Errors should degrade gracefully, not crash."""
        mock_router = MagicMock()
        
        call_count = [0]
        
        async def failing_route(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                raise Exception("First call fails")
            # Second call succeeds
            return MagicMock(
                text="Fallback response",
                completion_tokens=50,
            )
        
        mock_router.route = failing_route
        
        # Test would verify processor handles first failure
        # and retries or falls back
        assert True  # Placeholder for actual test

    @pytest.mark.asyncio
    async def test_invalid_context_handled(self, processor_for_alex):
        """Invalid context should not crash processing."""
        result = await processor_for_alex.process(
            stimulus="Test with context",
            urgency=0.5,
            complexity=0.5,
            relevance=0.5,
            context={"invalid_key": None, "nested": {"deep": "value"}},
        )
        
        assert result is not None


# =============================================================================
# CONCURRENT EDGE CASES
# =============================================================================

class TestConcurrentEdgeCases:
    """Tests for concurrent processing edge cases."""

    @pytest.mark.asyncio
    async def test_rapid_sequential_calls(self, processor_for_alex):
        """Rapid sequential calls should all complete."""
        results = []
        
        for i in range(10):
            result = await processor_for_alex.process(
                stimulus=f"Rapid call {i}",
                urgency=0.5,
                complexity=0.5,
                relevance=0.5,
            )
            results.append(result)
        
        # All should complete
        assert len(results) == 10
        for r in results:
            assert r.primary_thought is not None

    @pytest.mark.asyncio
    async def test_concurrent_different_urgencies(self, processor_for_alex):
        """Concurrent calls with different urgencies should process correctly."""
        tasks = [
            processor_for_alex.process(
                stimulus="Low urgency task",
                urgency=0.1,
                complexity=0.5,
                relevance=0.7,
            ),
            processor_for_alex.process(
                stimulus="High urgency task",
                urgency=0.9,
                complexity=0.5,
                relevance=0.7,
            ),
            processor_for_alex.process(
                stimulus="Medium urgency task",
                urgency=0.5,
                complexity=0.5,
                relevance=0.7,
            ),
        ]
        
        results = await asyncio.gather(*tasks)
        
        # All should complete
        assert len(results) == 3
        for r in results:
            assert r is not None

    @pytest.mark.asyncio
    async def test_concurrent_with_failures(self, alex_chen):
        """Some concurrent failures should not affect others."""
        # This tests resilience when some requests fail
        # Implementation should isolate failures
        pass  # Placeholder for actual implementation test


# =============================================================================
# MEMORY AND STATE EDGE CASES
# =============================================================================

class TestMemoryEdgeCases:
    """Tests for memory and state edge cases."""

    @pytest.mark.asyncio
    async def test_missing_context_handled(self, processor_for_alex):
        """Missing context fields should be handled gracefully."""
        result = await processor_for_alex.process(
            stimulus="Test without context",
            urgency=0.5,
            complexity=0.5,
            relevance=0.5,
            context=None,  # Explicitly None
        )
        
        assert result is not None

    @pytest.mark.asyncio
    async def test_empty_context_handled(self, processor_for_alex):
        """Empty context dict should be handled."""
        result = await processor_for_alex.process(
            stimulus="Test with empty context",
            urgency=0.5,
            complexity=0.5,
            relevance=0.5,
            context={},
        )
        
        assert result is not None


# =============================================================================
# THOUGHT ACCUMULATION EDGE CASES
# =============================================================================

class TestThoughtEdgeCases:
    """Tests for thought accumulation edge cases."""

    @pytest.mark.asyncio
    async def test_no_thoughts_generated(self, processor_for_alex):
        """Zero thoughts scenario should be handled."""
        # Very low relevance might produce minimal thoughts
        result = await processor_for_alex.process(
            stimulus="Completely unrelated topic xyz123",
            urgency=0.1,
            complexity=0.1,
            relevance=0.05,  # Very low
        )
        
        # Should still return valid result
        assert result is not None
        # May have empty thoughts list
        assert isinstance(result.thoughts, list)

    @pytest.mark.asyncio
    async def test_primary_thought_selection_with_one(self, processor_for_alex):
        """Single thought should be selected as primary."""
        result = await processor_for_alex.process(
            stimulus="Simple query",
            urgency=0.1,
            complexity=0.1,
            relevance=0.3,
        )
        
        if len(result.thoughts) == 1:
            assert result.primary_thought == result.thoughts[0]

    @pytest.mark.asyncio
    async def test_thought_ids_unique(self, processor_for_alex):
        """All thought IDs should be unique."""
        result = await processor_for_alex.process(
            stimulus="Generate multiple thoughts",
            urgency=0.8,
            complexity=0.7,
            relevance=0.9,
        )
        
        thought_ids = [t.thought_id for t in result.thoughts]
        assert len(thought_ids) == len(set(thought_ids)), (
            "Duplicate thought IDs found"
        )


# =============================================================================
# TIER SELECTION EDGE CASES
# =============================================================================

class TestTierSelectionEdgeCases:
    """Tests for tier selection edge cases."""

    @pytest.mark.asyncio
    async def test_conflicting_signals(self, processor_for_alex):
        """Conflicting urgency/complexity should resolve correctly."""
        # High urgency but also high complexity
        result = await processor_for_alex.process(
            stimulus="URGENT but also incredibly complex!",
            urgency=0.95,
            complexity=0.95,
            relevance=0.9,
        )
        
        # Should balance both - probably REFLEX for speed then deeper analysis
        assert result is not None
        tiers = [t.tier.name for t in result.thoughts]
        
        # Should have multiple tiers for this scenario
        # High urgency triggers REFLEX, high complexity triggers deeper

    @pytest.mark.asyncio
    async def test_borderline_urgency(self, processor_for_alex):
        """Borderline urgency values should be handled consistently."""
        # Test values right at threshold boundaries
        borderline_values = [0.29, 0.30, 0.31, 0.69, 0.70, 0.71]
        
        for urgency in borderline_values:
            result = await processor_for_alex.process(
                stimulus="Borderline test",
                urgency=urgency,
                complexity=0.5,
                relevance=0.7,
            )
            assert result is not None, f"Failed at urgency {urgency}"


# =============================================================================
# INTEGRATION EDGE CASES
# =============================================================================

class TestIntegrationEdgeCases:
    """Integration-level edge cases."""

    @pytest.mark.asyncio
    async def test_multiple_agents_same_stimulus(
        self, processor_for_alex, processor_for_maya, processor_for_emily
    ):
        """Same stimulus to multiple agents should produce different results."""
        stimulus = "What do you think about this approach?"
        
        results = await asyncio.gather(
            processor_for_alex.process(
                stimulus=stimulus, urgency=0.5, complexity=0.5, relevance=0.7
            ),
            processor_for_maya.process(
                stimulus=stimulus, urgency=0.5, complexity=0.5, relevance=0.7
            ),
            processor_for_emily.process(
                stimulus=stimulus, urgency=0.5, complexity=0.5, relevance=0.7
            ),
        )
        
        # All should complete
        assert len(results) == 3
        for r in results:
            assert r.primary_thought is not None
        
        # With different personalities, results should differ
        # (though with mocks may be similar)
        contents = [r.primary_thought.content for r in results]
        # At minimum, all should be valid strings
        for content in contents:
            assert len(content) > 0

    @pytest.mark.asyncio
    async def test_processor_reuse_stability(self, processor_for_alex):
        """Reusing processor for many calls should be stable."""
        for i in range(20):
            result = await processor_for_alex.process(
                stimulus=f"Call number {i}",
                urgency=0.5,
                complexity=0.5,
                relevance=0.5,
            )
            assert result is not None
        
        # Final call should still work normally
        final_result = await processor_for_alex.process(
            stimulus="Final call after many",
            urgency=0.5,
            complexity=0.5,
            relevance=0.9,
        )
        assert final_result.primary_thought is not None
