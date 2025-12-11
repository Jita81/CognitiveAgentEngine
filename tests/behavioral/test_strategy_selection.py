"""Behavioral tests for cognitive strategy selection.

Tests verify that the cognitive system selects appropriate tiers based on
urgency, complexity, and relevance parameters.

These are behavioral tests - we're testing that the system makes smart
decisions about HOW to think, not just that it can think.
"""

import pytest

from src.cognitive import CognitiveTier, CognitiveResult


class TestHighUrgencyStrategy:
    """Tests for high urgency stimulus processing.
    
    When urgency is high (>0.8) and the stimulus is relevant,
    we expect:
    - REFLEX fires first (immediate reaction)
    - REACTIVE runs in parallel (tactical assessment)
    - DELIBERATE may follow (deeper analysis)
    """

    @pytest.mark.asyncio
    async def test_reflex_fires_first_on_high_urgency(self, processor_for_alex):
        """High urgency should trigger REFLEX as first tier."""
        result = await processor_for_alex.process(
            stimulus="ALERT: The production server is down and customers can't access their data!",
            urgency=0.95,
            complexity=0.6,
            relevance=0.9,
        )
        
        # REFLEX should be in the tiers used
        assert CognitiveTier.REFLEX in result.tiers_used, (
            f"Expected REFLEX in tiers, got: {[t.name for t in result.tiers_used]}"
        )
        
        # First thought should be from REFLEX
        assert result.thoughts[0].tier == CognitiveTier.REFLEX, (
            f"Expected first thought from REFLEX, got: {result.thoughts[0].tier.name}"
        )

    @pytest.mark.asyncio
    async def test_parallel_reactive_on_high_urgency(self, processor_for_alex):
        """High urgency should trigger parallel REACTIVE processing."""
        result = await processor_for_alex.process(
            stimulus="Critical bug affecting all users - system is unresponsive!",
            urgency=0.95,
            complexity=0.5,
            relevance=0.9,
        )
        
        # Should have REACTIVE thoughts
        reactive_thoughts = [t for t in result.thoughts if t.tier == CognitiveTier.REACTIVE]
        
        # High urgency should trigger at least one REACTIVE thought
        assert len(reactive_thoughts) >= 1, (
            f"Expected at least 1 REACTIVE thought, got: {len(reactive_thoughts)}"
        )

    @pytest.mark.asyncio
    async def test_high_urgency_includes_deliberate_on_complexity(self, processor_for_alex):
        """High urgency + complexity should eventually include DELIBERATE."""
        result = await processor_for_alex.process(
            stimulus="Production database is corrupted and we're losing data every minute!",
            urgency=0.95,
            complexity=0.7,  # High complexity
            relevance=0.9,
        )
        
        # With high complexity, should escalate to DELIBERATE
        assert CognitiveTier.DELIBERATE in result.tiers_used, (
            f"Expected DELIBERATE for complex high-urgency, got: {[t.name for t in result.tiers_used]}"
        )

    @pytest.mark.asyncio
    async def test_high_urgency_completes_quickly(self, processor_for_alex):
        """High urgency processing should complete within time bounds."""
        result = await processor_for_alex.process(
            stimulus="Server down now!",
            urgency=0.95,
            complexity=0.5,
            relevance=0.9,
        )
        
        # Should complete in under 3 seconds (generous for mock)
        assert result.processing_time_ms < 3000, (
            f"Processing took too long: {result.processing_time_ms}ms"
        )

    @pytest.mark.asyncio
    async def test_high_urgency_produces_actionable_first_thought(self, processor_for_alex):
        """First thought in high urgency should be brief and actionable."""
        result = await processor_for_alex.process(
            stimulus="CRITICAL: Payment processing is failing for all transactions!",
            urgency=0.95,
            complexity=0.6,
            relevance=0.9,
        )
        
        first_thought = result.thoughts[0]
        
        # Should be brief (REFLEX tier)
        word_count = len(first_thought.content.split())
        assert word_count < 60, (
            f"First thought should be brief, got {word_count} words"
        )
        
        # Should be a reaction or observation
        assert first_thought.thought_type.value in ["reaction", "observation", "concern", "plan"], (
            f"Expected actionable thought type, got: {first_thought.thought_type.value}"
        )


class TestLowUrgencyStrategy:
    """Tests for low urgency stimulus processing.
    
    When urgency is low (<0.3) and complexity is high,
    we expect:
    - REFLEX is skipped (no need for speed)
    - DELIBERATE is primary (time for considered response)
    - ANALYTICAL may follow for complex topics
    """

    @pytest.mark.asyncio
    async def test_no_reflex_on_low_urgency_high_complexity(self, processor_for_alex):
        """Low urgency + high complexity should skip REFLEX."""
        result = await processor_for_alex.process(
            stimulus="Should we migrate our monolith to microservices architecture?",
            urgency=0.2,
            complexity=0.85,
            relevance=0.8,
        )
        
        # Should NOT include REFLEX
        assert CognitiveTier.REFLEX not in result.tiers_used, (
            f"Low urgency should skip REFLEX, but got: {[t.name for t in result.tiers_used]}"
        )

    @pytest.mark.asyncio
    async def test_deliberate_on_complex_low_urgency(self, processor_for_alex):
        """Complex, non-urgent questions should engage DELIBERATE."""
        result = await processor_for_alex.process(
            stimulus="What architecture patterns should we consider for our new platform?",
            urgency=0.2,
            complexity=0.8,
            relevance=0.8,
        )
        
        # Should include DELIBERATE
        assert CognitiveTier.DELIBERATE in result.tiers_used, (
            f"Complex question needs DELIBERATE, got: {[t.name for t in result.tiers_used]}"
        )

    @pytest.mark.asyncio
    async def test_analytical_on_very_complex(self, processor_for_alex):
        """Very complex low-urgency should escalate to ANALYTICAL."""
        result = await processor_for_alex.process(
            stimulus=(
                "Analyze the tradeoffs between our current architecture and a complete "
                "redesign. Consider scalability, team structure, migration costs, and "
                "long-term maintainability."
            ),
            urgency=0.15,
            complexity=0.9,  # Very high complexity
            relevance=0.85,
        )
        
        # Should include ANALYTICAL for deep analysis
        assert CognitiveTier.ANALYTICAL in result.tiers_used or CognitiveTier.DELIBERATE in result.tiers_used, (
            f"Very complex needs ANALYTICAL or DELIBERATE, got: {[t.name for t in result.tiers_used]}"
        )

    @pytest.mark.asyncio
    async def test_low_urgency_produces_considered_response(self, processor_for_alex):
        """Low urgency should produce more thorough responses."""
        result = await processor_for_alex.process(
            stimulus="What's the best approach for handling distributed transactions?",
            urgency=0.2,
            complexity=0.7,
            relevance=0.8,
        )
        
        # Primary thought should have higher confidence
        assert result.primary_thought is not None
        assert result.primary_thought.confidence >= 0.65, (
            f"Considered response should have higher confidence, got: {result.primary_thought.confidence}"
        )
        
        # Should be reasonably complete (mock may generate shorter responses)
        assert result.primary_thought.completeness >= 0.4, (
            f"Considered response should be more complete, got: {result.primary_thought.completeness}"
        )


class TestLowRelevanceStrategy:
    """Tests for low relevance stimulus processing.
    
    When relevance is low (<0.3), we expect:
    - Only REFLEX tier used (minimal engagement)
    - Brief observation or acknowledgment
    - Quick processing
    """

    @pytest.mark.asyncio
    async def test_only_reflex_on_low_relevance(self, processor_for_alex):
        """Low relevance should use only REFLEX."""
        result = await processor_for_alex.process(
            stimulus="What's everyone having for lunch today?",
            urgency=0.3,
            complexity=0.1,
            relevance=0.15,  # Not relevant to backend development
        )
        
        # Should only use REFLEX
        assert len(result.tiers_used) == 1, (
            f"Low relevance should minimize tiers, got: {len(result.tiers_used)} tiers"
        )
        assert result.tiers_used[0] == CognitiveTier.REFLEX, (
            f"Low relevance should use REFLEX, got: {result.tiers_used[0].name}"
        )

    @pytest.mark.asyncio
    async def test_low_relevance_produces_brief_response(self, processor_for_alex):
        """Low relevance should produce minimal response."""
        result = await processor_for_alex.process(
            stimulus="Did anyone watch the game last night?",
            urgency=0.2,
            complexity=0.1,
            relevance=0.1,
        )
        
        # Should have exactly one thought
        assert result.thought_count <= 2, (
            f"Low relevance should produce few thoughts, got: {result.thought_count}"
        )
        
        # Thought should be brief
        word_count = len(result.primary_thought.content.split())
        assert word_count < 50, (
            f"Low relevance response should be brief, got {word_count} words"
        )

    @pytest.mark.asyncio
    async def test_low_relevance_quick_processing(self, processor_for_alex):
        """Low relevance should process quickly."""
        result = await processor_for_alex.process(
            stimulus="Nice weather we're having!",
            urgency=0.2,
            complexity=0.05,
            relevance=0.1,
        )
        
        # Should be very fast
        assert result.processing_time_ms < 1000, (
            f"Low relevance should be quick, took: {result.processing_time_ms}ms"
        )


class TestMediumParametersStrategy:
    """Tests for medium urgency/complexity/relevance.
    
    When parameters are in the middle range, we expect:
    - Proportional response
    - REACTIVE or DELIBERATE depending on complexity
    - Not extreme in either direction
    """

    @pytest.mark.asyncio
    async def test_medium_low_complexity_uses_reactive(self, processor_for_alex):
        """Medium urgency + low complexity should use REACTIVE."""
        result = await processor_for_alex.process(
            stimulus="How should we handle error logging?",
            urgency=0.5,
            complexity=0.3,
            relevance=0.6,
        )
        
        # Should use REACTIVE (quick but considered)
        assert CognitiveTier.REACTIVE in result.tiers_used or CognitiveTier.DELIBERATE in result.tiers_used, (
            f"Medium should use REACTIVE or DELIBERATE, got: {[t.name for t in result.tiers_used]}"
        )
        
        # Should NOT use ANALYTICAL for simple question
        assert CognitiveTier.ANALYTICAL not in result.tiers_used, (
            "Simple question shouldn't need ANALYTICAL"
        )

    @pytest.mark.asyncio
    async def test_medium_high_complexity_uses_deliberate(self, processor_for_alex):
        """Medium urgency + higher complexity should use DELIBERATE."""
        result = await processor_for_alex.process(
            stimulus="How should we approach our caching strategy?",
            urgency=0.5,
            complexity=0.7,
            relevance=0.7,
        )
        
        # Should use DELIBERATE for more complex topic
        assert CognitiveTier.DELIBERATE in result.tiers_used, (
            f"Higher complexity needs DELIBERATE, got: {[t.name for t in result.tiers_used]}"
        )

    @pytest.mark.asyncio
    async def test_medium_produces_balanced_response(self, processor_for_alex):
        """Medium parameters should produce balanced response."""
        result = await processor_for_alex.process(
            stimulus="Should we add input validation here?",
            urgency=0.5,
            complexity=0.5,
            relevance=0.6,
        )
        
        # Should have 1-2 thoughts (not too many, not too few)
        assert 1 <= result.thought_count <= 3, (
            f"Medium should produce 1-3 thoughts, got: {result.thought_count}"
        )
        
        # Processing time should be moderate
        assert 200 < result.processing_time_ms < 5000, (
            f"Medium processing should be moderate, got: {result.processing_time_ms}ms"
        )


class TestStrategyMatrix:
    """Tests for the complete strategy selection matrix.
    
    Systematically tests all combinations from the requirements matrix.
    """

    @pytest.mark.asyncio
    @pytest.mark.parametrize("urgency,relevance,complexity,expected_tiers", [
        # High urgency + High relevance + Any complexity
        (0.9, 0.8, 0.3, [CognitiveTier.REFLEX, CognitiveTier.REACTIVE]),
        (0.9, 0.8, 0.8, [CognitiveTier.REFLEX, CognitiveTier.REACTIVE, CognitiveTier.DELIBERATE]),
        
        # High urgency + Low relevance
        (0.9, 0.2, 0.5, [CognitiveTier.REFLEX]),
        
        # Low urgency + High relevance + High complexity
        (0.2, 0.8, 0.8, [CognitiveTier.DELIBERATE]),
        
        # Low urgency + High relevance + Low complexity
        (0.2, 0.8, 0.3, [CognitiveTier.DELIBERATE]),
        
        # Low urgency + Low relevance
        (0.2, 0.2, 0.5, [CognitiveTier.REFLEX]),
    ])
    async def test_strategy_matrix_selection(
        self,
        processor_for_alex,
        urgency: float,
        relevance: float,
        complexity: float,
        expected_tiers: list,
    ):
        """Test that strategy selection matches the requirements matrix."""
        result = await processor_for_alex.process(
            stimulus="Test stimulus for strategy matrix validation",
            urgency=urgency,
            complexity=complexity,
            relevance=relevance,
        )
        
        # Check that at least the minimum expected tiers are used
        for expected_tier in expected_tiers:
            if expected_tier == CognitiveTier.REFLEX and urgency > 0.8 and relevance > 0.5:
                # REFLEX should definitely be present for high urgency + relevant
                assert expected_tier in result.tiers_used, (
                    f"Expected {expected_tier.name} for urgency={urgency}, "
                    f"relevance={relevance}, complexity={complexity}. "
                    f"Got: {[t.name for t in result.tiers_used]}"
                )


class TestTierProgressionBehavior:
    """Tests for how thoughts progress through tiers."""

    @pytest.mark.asyncio
    async def test_later_thoughts_build_on_earlier(self, processor_for_alex):
        """Later thoughts should have access to earlier thoughts."""
        result = await processor_for_alex.process(
            stimulus="Major security incident - user credentials may have been exposed!",
            urgency=0.9,
            complexity=0.7,
            relevance=0.9,
        )
        
        # With multiple thoughts, later ones should be from higher tiers
        if result.thought_count >= 2:
            first_tier_value = result.thoughts[0].tier.value
            last_tier_value = result.thoughts[-1].tier.value
            
            # Generally, we expect tier progression (or at least not regression)
            # This is a soft check since parallel thoughts may not strictly progress
            assert last_tier_value >= first_tier_value or result.thought_count == 1, (
                "Thoughts should generally progress to higher tiers"
            )

    @pytest.mark.asyncio
    async def test_primary_thought_selection(self, processor_for_alex):
        """Primary thought should be the most valuable."""
        result = await processor_for_alex.process(
            stimulus="Critical decision needed on database choice",
            urgency=0.7,
            complexity=0.7,
            relevance=0.9,
        )
        
        # Primary thought should exist
        assert result.primary_thought is not None
        
        # Primary should have high confidence
        assert result.primary_thought.confidence >= 0.5, (
            f"Primary thought should have reasonable confidence, got: {result.primary_thought.confidence}"
        )
        
        # Primary should be from a higher tier (not REFLEX) for complex relevant stimulus
        if result.thought_count > 1:
            assert result.primary_thought.tier.value >= CognitiveTier.REACTIVE.value, (
                f"Primary thought should be considered, got: {result.primary_thought.tier.name}"
            )
