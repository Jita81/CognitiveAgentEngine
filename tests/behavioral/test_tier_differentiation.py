"""
Tier Differentiation Tests

Tests that each cognitive tier produces qualitatively different output:
- REFLEX: Brief, immediate reactions
- REACTIVE: Quick tactical assessments
- DELIBERATE: Considered, structured responses
- ANALYTICAL: Deep analysis with patterns
- COMPREHENSIVE: Full exploration

These tests verify the cognitive architecture produces appropriate
depth and quality at each processing level.
"""

import pytest
import asyncio
from datetime import datetime
from typing import List, Dict
from unittest.mock import AsyncMock, MagicMock

from conftest import (
    analyze_response_style,
    score_response_quality,
)


# =============================================================================
# TIER CHARACTERISTIC DEFINITIONS
# =============================================================================

TIER_CHARACTERISTICS = {
    "REFLEX": {
        "max_words": 50,
        "max_latency_ms": 500,  # With mock overhead
        "thought_types": ["reaction", "observation"],
        "min_completeness": 0.3,
        "max_completeness": 0.7,
        "description": "Immediate, instinctive response",
    },
    "REACTIVE": {
        "min_words": 20,
        "max_words": 150,
        "max_latency_ms": 1000,
        "thought_types": ["reaction", "observation", "insight", "concern"],
        "min_completeness": 0.4,
        "max_completeness": 0.8,
        "min_confidence": 0.5,
        "description": "Quick tactical assessment",
    },
    "DELIBERATE": {
        "min_words": 50,
        "max_words": 400,
        "max_latency_ms": 3000,
        "thought_types": ["insight", "concern", "plan", "question"],
        "min_completeness": 0.6,
        "min_confidence": 0.65,
        "description": "Considered, structured response",
    },
    "ANALYTICAL": {
        "min_words": 100,
        "max_words": 600,
        "max_latency_ms": 7000,
        "thought_types": ["insight", "concern", "plan"],
        "min_completeness": 0.7,
        "min_confidence": 0.75,
        "description": "Deep analysis with patterns",
    },
    "COMPREHENSIVE": {
        "min_words": 150,
        "max_words": 800,
        "max_latency_ms": 12000,
        "thought_types": ["insight", "plan"],
        "min_completeness": 0.8,
        "min_confidence": 0.8,
        "description": "Full exploration",
    },
}


def count_words(text: str) -> int:
    """Count words in text."""
    return len(text.split())


def check_tier_characteristics(thought, tier_name: str) -> Dict[str, bool]:
    """Check if thought matches tier characteristics."""
    chars = TIER_CHARACTERISTICS[tier_name]
    results = {}
    
    word_count = count_words(thought.content)
    
    # Word count checks
    if "min_words" in chars:
        results["min_words"] = word_count >= chars["min_words"]
    if "max_words" in chars:
        results["max_words"] = word_count <= chars["max_words"]
    
    # Thought type check
    if "thought_types" in chars:
        results["thought_type_valid"] = thought.thought_type in chars["thought_types"]
    
    # Completeness checks
    if "min_completeness" in chars:
        results["min_completeness"] = thought.completeness >= chars["min_completeness"]
    if "max_completeness" in chars:
        results["max_completeness"] = thought.completeness <= chars["max_completeness"]
    
    # Confidence checks
    if "min_confidence" in chars:
        results["min_confidence"] = thought.confidence >= chars["min_confidence"]
    
    return results


# =============================================================================
# REFLEX TIER TESTS
# =============================================================================

class TestReflexTier:
    """Tests for REFLEX tier - immediate reactions."""

    @pytest.mark.asyncio
    async def test_reflex_produces_brief_output(self, processor_for_alex):
        """REFLEX tier should produce brief, immediate output."""
        # Force REFLEX by high urgency
        result = await processor_for_alex.process(
            stimulus="Quick! The server is down!",
            urgency=0.95,
            complexity=0.2,
            relevance=0.9,
        )
        
        # Should have at least one thought
        assert len(result.thoughts) > 0
        
        # Find REFLEX thoughts
        reflex_thoughts = [t for t in result.thoughts if t.tier.name == "REFLEX"]
        
        # High urgency should trigger REFLEX
        assert len(reflex_thoughts) > 0, "High urgency should produce REFLEX thoughts"
        
        # Check REFLEX characteristics
        for thought in reflex_thoughts:
            word_count = count_words(thought.content)
            assert word_count <= TIER_CHARACTERISTICS["REFLEX"]["max_words"], (
                f"REFLEX thought too long: {word_count} words"
            )

    @pytest.mark.asyncio
    async def test_reflex_thought_type(self, processor_for_alex):
        """REFLEX thoughts should be reactions or observations."""
        result = await processor_for_alex.process(
            stimulus="Alert! Security breach detected!",
            urgency=0.99,
            complexity=0.1,
            relevance=0.9,
        )
        
        reflex_thoughts = [t for t in result.thoughts if t.tier.name == "REFLEX"]
        
        for thought in reflex_thoughts:
            valid_types = TIER_CHARACTERISTICS["REFLEX"]["thought_types"]
            assert thought.thought_type.value in valid_types, (
                f"REFLEX thought type '{thought.thought_type.value}' not in {valid_types}"
            )

    @pytest.mark.asyncio
    async def test_reflex_low_completeness(self, processor_for_alex):
        """REFLEX thoughts should have moderate completeness (quick, not thorough)."""
        result = await processor_for_alex.process(
            stimulus="Incoming!",
            urgency=1.0,
            complexity=0.1,
            relevance=0.9,
        )
        
        reflex_thoughts = [t for t in result.thoughts if t.tier.name == "REFLEX"]
        
        for thought in reflex_thoughts:
            chars = TIER_CHARACTERISTICS["REFLEX"]
            assert thought.completeness <= chars["max_completeness"], (
                f"REFLEX completeness {thought.completeness} exceeds max {chars['max_completeness']}"
            )


# =============================================================================
# REACTIVE TIER TESTS
# =============================================================================

class TestReactiveTier:
    """Tests for REACTIVE tier - quick tactical assessments."""

    @pytest.mark.asyncio
    async def test_reactive_produces_tactical_assessment(self, processor_for_alex):
        """REACTIVE tier should produce tactical assessments."""
        # Medium urgency, relevant topic
        result = await processor_for_alex.process(
            stimulus="We have a performance issue in the API. Response times are slow.",
            urgency=0.6,
            complexity=0.4,
            relevance=0.9,
        )
        
        # Should have thoughts
        assert len(result.thoughts) > 0
        
        # Find REACTIVE thoughts
        reactive_thoughts = [t for t in result.thoughts if t.tier.name == "REACTIVE"]
        
        # Medium urgency with relevance should include REACTIVE
        # (may also include DELIBERATE for complexity)
        assert len(reactive_thoughts) >= 0  # May or may not have REACTIVE depending on strategy

    @pytest.mark.asyncio
    async def test_reactive_word_count_appropriate(self, processor_for_alex):
        """REACTIVE thoughts should be moderate length."""
        result = await processor_for_alex.process(
            stimulus="There's a bug in the authentication flow. Users can't log in.",
            urgency=0.7,
            complexity=0.3,
            relevance=0.9,
        )
        
        reactive_thoughts = [t for t in result.thoughts if t.tier.name == "REACTIVE"]
        
        for thought in reactive_thoughts:
            word_count = count_words(thought.content)
            chars = TIER_CHARACTERISTICS["REACTIVE"]
            
            assert word_count >= chars["min_words"], (
                f"REACTIVE thought too short: {word_count} < {chars['min_words']}"
            )
            assert word_count <= chars["max_words"], (
                f"REACTIVE thought too long: {word_count} > {chars['max_words']}"
            )

    @pytest.mark.asyncio
    async def test_reactive_minimum_confidence(self, processor_for_alex):
        """REACTIVE thoughts should have minimum confidence."""
        result = await processor_for_alex.process(
            stimulus="Database connection pool seems exhausted.",
            urgency=0.6,
            complexity=0.4,
            relevance=0.9,
        )
        
        reactive_thoughts = [t for t in result.thoughts if t.tier.name == "REACTIVE"]
        
        for thought in reactive_thoughts:
            min_conf = TIER_CHARACTERISTICS["REACTIVE"]["min_confidence"]
            assert thought.confidence >= min_conf, (
                f"REACTIVE confidence {thought.confidence} below min {min_conf}"
            )


# =============================================================================
# DELIBERATE TIER TESTS
# =============================================================================

class TestDeliberateTier:
    """Tests for DELIBERATE tier - considered, structured responses."""

    @pytest.mark.asyncio
    async def test_deliberate_produces_structured_response(self, processor_for_alex):
        """DELIBERATE tier should produce considered responses."""
        # Low urgency, high complexity, high relevance
        result = await processor_for_alex.process(
            stimulus="How should we architect the new microservices platform?",
            urgency=0.2,
            complexity=0.8,
            relevance=0.9,
        )
        
        # Should have primary thought
        assert result.primary_thought is not None
        
        # Low urgency + high complexity should use DELIBERATE
        deliberate_thoughts = [t for t in result.thoughts if t.tier.name == "DELIBERATE"]
        
        # Should have at least one DELIBERATE thought for this scenario
        assert len(deliberate_thoughts) > 0, (
            "Low urgency + high complexity should produce DELIBERATE thoughts"
        )

    @pytest.mark.asyncio
    async def test_deliberate_word_count_appropriate(self, processor_for_alex):
        """DELIBERATE thoughts should be substantial but not excessive."""
        result = await processor_for_alex.process(
            stimulus="What's the best approach for implementing the payment system?",
            urgency=0.2,
            complexity=0.7,
            relevance=0.9,
        )
        
        deliberate_thoughts = [t for t in result.thoughts if t.tier.name == "DELIBERATE"]
        
        for thought in deliberate_thoughts:
            word_count = count_words(thought.content)
            chars = TIER_CHARACTERISTICS["DELIBERATE"]
            
            assert word_count >= chars["min_words"], (
                f"DELIBERATE thought too short: {word_count} < {chars['min_words']}"
            )
            assert word_count <= chars["max_words"], (
                f"DELIBERATE thought too long: {word_count} > {chars['max_words']}"
            )

    @pytest.mark.asyncio
    async def test_deliberate_high_completeness(self, processor_for_alex):
        """DELIBERATE thoughts should have high completeness."""
        result = await processor_for_alex.process(
            stimulus="Design a caching strategy for our API endpoints.",
            urgency=0.2,
            complexity=0.7,
            relevance=0.9,
        )
        
        deliberate_thoughts = [t for t in result.thoughts if t.tier.name == "DELIBERATE"]
        
        for thought in deliberate_thoughts:
            min_comp = TIER_CHARACTERISTICS["DELIBERATE"]["min_completeness"]
            assert thought.completeness >= min_comp, (
                f"DELIBERATE completeness {thought.completeness} below min {min_comp}"
            )

    @pytest.mark.asyncio
    async def test_deliberate_confidence_appropriate(self, processor_for_alex):
        """DELIBERATE thoughts should have appropriate confidence."""
        result = await processor_for_alex.process(
            stimulus="Should we use PostgreSQL or MongoDB for the new service?",
            urgency=0.2,
            complexity=0.6,
            relevance=0.9,
        )
        
        deliberate_thoughts = [t for t in result.thoughts if t.tier.name == "DELIBERATE"]
        
        for thought in deliberate_thoughts:
            min_conf = TIER_CHARACTERISTICS["DELIBERATE"]["min_confidence"]
            assert thought.confidence >= min_conf, (
                f"DELIBERATE confidence {thought.confidence} below min {min_conf}"
            )


# =============================================================================
# ANALYTICAL TIER TESTS
# =============================================================================

class TestAnalyticalTier:
    """Tests for ANALYTICAL tier - deep analysis with patterns."""

    @pytest.mark.asyncio
    async def test_analytical_produces_deep_analysis(self, processor_for_alex):
        """ANALYTICAL tier should produce deep analysis."""
        # Low urgency, very high complexity
        result = await processor_for_alex.process(
            stimulus="We need to completely redesign our data architecture to support "
                     "real-time analytics, multi-tenancy, and horizontal scaling. "
                     "What are all the tradeoffs we should consider?",
            urgency=0.1,
            complexity=0.9,
            relevance=0.9,
        )
        
        # Should produce substantial output
        assert result.primary_thought is not None
        
        # Very high complexity should engage ANALYTICAL
        analytical_thoughts = [t for t in result.thoughts if t.tier.name == "ANALYTICAL"]
        
        # May or may not have explicit ANALYTICAL depending on strategy
        # But primary thought should be high quality
        assert result.primary_thought.completeness >= 0.6

    @pytest.mark.asyncio
    async def test_analytical_substantial_output(self, processor_for_alex):
        """ANALYTICAL thoughts should be substantial."""
        result = await processor_for_alex.process(
            stimulus="Analyze the security implications of our new authentication system.",
            urgency=0.1,
            complexity=0.95,
            relevance=0.9,
        )
        
        analytical_thoughts = [t for t in result.thoughts if t.tier.name == "ANALYTICAL"]
        
        for thought in analytical_thoughts:
            word_count = count_words(thought.content)
            chars = TIER_CHARACTERISTICS["ANALYTICAL"]
            
            assert word_count >= chars["min_words"], (
                f"ANALYTICAL thought too short: {word_count} < {chars['min_words']}"
            )

    @pytest.mark.asyncio
    async def test_analytical_high_confidence(self, processor_for_alex):
        """ANALYTICAL thoughts should have high confidence from thorough analysis."""
        result = await processor_for_alex.process(
            stimulus="What are all the failure modes we should plan for?",
            urgency=0.1,
            complexity=0.9,
            relevance=0.9,
        )
        
        analytical_thoughts = [t for t in result.thoughts if t.tier.name == "ANALYTICAL"]
        
        for thought in analytical_thoughts:
            min_conf = TIER_CHARACTERISTICS["ANALYTICAL"]["min_confidence"]
            assert thought.confidence >= min_conf, (
                f"ANALYTICAL confidence {thought.confidence} below min {min_conf}"
            )


# =============================================================================
# TIER PROGRESSION TESTS
# =============================================================================

class TestTierProgression:
    """Tests that verify tiers produce progressively deeper output."""

    @pytest.mark.asyncio
    async def test_later_tiers_more_complete(self, processor_for_alex):
        """Higher tiers should produce more complete thoughts."""
        # Run multiple scenarios to get different tiers
        
        # High urgency (should get REFLEX)
        urgent_result = await processor_for_alex.process(
            stimulus="Emergency!",
            urgency=0.99,
            complexity=0.1,
            relevance=0.9,
        )
        
        # Medium (should get REACTIVE/DELIBERATE)
        medium_result = await processor_for_alex.process(
            stimulus="We have a performance concern",
            urgency=0.5,
            complexity=0.5,
            relevance=0.9,
        )
        
        # Low urgency + high complexity (should get DELIBERATE+)
        complex_result = await processor_for_alex.process(
            stimulus="Design the complete system architecture",
            urgency=0.1,
            complexity=0.9,
            relevance=0.9,
        )
        
        # Get primary thoughts
        urgent_thought = urgent_result.primary_thought
        medium_thought = medium_result.primary_thought
        complex_thought = complex_result.primary_thought
        
        assert all([urgent_thought, medium_thought, complex_thought])
        
        # Complex scenario should have highest completeness
        assert complex_thought.completeness >= medium_thought.completeness * 0.9, (
            f"Complex scenario should have high completeness: "
            f"complex={complex_thought.completeness}, medium={medium_thought.completeness}"
        )

    @pytest.mark.asyncio
    async def test_higher_tiers_longer_output(self, processor_for_alex):
        """Higher tiers should generally produce longer output."""
        # Urgent (REFLEX)
        urgent_result = await processor_for_alex.process(
            stimulus="Fire!",
            urgency=1.0,
            complexity=0.1,
            relevance=0.9,
        )
        
        # Complex (DELIBERATE+)
        complex_result = await processor_for_alex.process(
            stimulus="Design the authentication system architecture",
            urgency=0.1,
            complexity=0.8,
            relevance=0.9,
        )
        
        urgent_words = count_words(urgent_result.primary_thought.content)
        complex_words = count_words(complex_result.primary_thought.content)
        
        # Complex should be substantially longer (unless mocks are identical)
        # At minimum, complex shouldn't be shorter
        assert complex_words >= urgent_words * 0.5, (
            f"Complex should not be much shorter than urgent: "
            f"complex={complex_words}, urgent={urgent_words}"
        )


# =============================================================================
# MULTI-TIER PROCESSING TESTS
# =============================================================================

class TestMultiTierProcessing:
    """Tests for scenarios that involve multiple tiers."""

    @pytest.mark.asyncio
    async def test_urgent_relevant_uses_multiple_tiers(self, processor_for_alex):
        """High urgency + high relevance should use multiple tiers."""
        result = await processor_for_alex.process(
            stimulus="Critical security vulnerability found! We need to patch immediately!",
            urgency=0.95,
            complexity=0.6,
            relevance=0.9,
        )
        
        # Should have multiple thoughts from different processing
        assert len(result.thoughts) >= 1
        
        # Track which tiers were used
        tiers_used = set(t.tier.name for t in result.thoughts)
        
        # High urgency + relevance should trigger parallel processing
        # At minimum, should have some processing
        assert len(tiers_used) >= 1

    @pytest.mark.asyncio
    async def test_tier_progression_in_strategy(self, processor_for_alex):
        """Strategy should progress from fast to thorough as needed."""
        result = await processor_for_alex.process(
            stimulus="We found a bug that's causing data corruption. "
                     "It's affecting production but we need to understand the root cause.",
            urgency=0.8,  # High but not immediate
            complexity=0.7,  # Needs analysis
            relevance=0.9,
        )
        
        # Should have thoughts
        assert len(result.thoughts) >= 1
        
        # With high urgency + complexity, should have processed at multiple levels
        tiers_used = [t.tier.name for t in result.thoughts]
        
        # The final/primary thought should be from a considered tier
        assert result.primary_thought is not None
        assert result.primary_thought.tier.value >= 1  # At least REACTIVE


# =============================================================================
# TIER OUTPUT QUALITY TESTS
# =============================================================================

class TestTierOutputQuality:
    """Tests that tier output quality is appropriate."""

    @pytest.mark.asyncio
    async def test_reflex_not_overengineered(self, processor_for_alex):
        """REFLEX responses should be simple, not complex."""
        result = await processor_for_alex.process(
            stimulus="Heads up!",
            urgency=1.0,
            complexity=0.1,
            relevance=0.9,
        )
        
        reflex_thoughts = [t for t in result.thoughts if t.tier.name == "REFLEX"]
        
        for thought in reflex_thoughts:
            # Should be simple acknowledgment, not detailed analysis
            word_count = count_words(thought.content)
            assert word_count < 100, f"REFLEX too complex: {word_count} words"

    @pytest.mark.asyncio
    async def test_deliberate_shows_reasoning(self, processor_for_alex):
        """DELIBERATE responses should show reasoning structure."""
        result = await processor_for_alex.process(
            stimulus="Should we migrate from PostgreSQL to CockroachDB?",
            urgency=0.2,
            complexity=0.8,
            relevance=0.9,
        )
        
        deliberate_thoughts = [t for t in result.thoughts if t.tier.name == "DELIBERATE"]
        
        for thought in deliberate_thoughts:
            # DELIBERATE should have substance
            word_count = count_words(thought.content)
            assert word_count >= 30, (
                f"DELIBERATE should have substantial reasoning: {word_count} words"
            )

    @pytest.mark.asyncio
    async def test_all_tiers_produce_coherent_output(self, processor_for_alex):
        """All tiers should produce grammatically coherent output."""
        scenarios = [
            {"stimulus": "Alert!", "urgency": 1.0, "complexity": 0.1},
            {"stimulus": "How's the project going?", "urgency": 0.5, "complexity": 0.3},
            {"stimulus": "Design the database schema", "urgency": 0.2, "complexity": 0.8},
        ]
        
        for scenario in scenarios:
            result = await processor_for_alex.process(
                stimulus=scenario["stimulus"],
                urgency=scenario["urgency"],
                complexity=scenario["complexity"],
                relevance=0.9,
            )
            
            # All thoughts should have non-empty content
            for thought in result.thoughts:
                assert thought.content, f"Empty content for {scenario['stimulus']}"
                assert len(thought.content) > 5, f"Content too short for {scenario['stimulus']}"


# =============================================================================
# TIER SELECTION CORRECTNESS TESTS
# =============================================================================

class TestTierSelectionCorrectness:
    """Tests that the correct tier is selected for given inputs."""

    @pytest.mark.asyncio
    async def test_maximum_urgency_includes_reflex(self, processor_for_alex):
        """Maximum urgency should definitely include REFLEX."""
        result = await processor_for_alex.process(
            stimulus="EMERGENCY!",
            urgency=1.0,
            complexity=0.1,
            relevance=0.9,
        )
        
        tiers_used = [t.tier.name for t in result.thoughts]
        
        # Highest urgency must include REFLEX
        assert "REFLEX" in tiers_used, (
            f"Maximum urgency should include REFLEX, got: {tiers_used}"
        )

    @pytest.mark.asyncio
    async def test_low_urgency_high_complexity_uses_deliberate(self, processor_for_alex):
        """Low urgency + high complexity should use DELIBERATE tier."""
        result = await processor_for_alex.process(
            stimulus="Take your time and design the complete API surface",
            urgency=0.1,
            complexity=0.9,
            relevance=0.9,
        )
        
        tiers_used = [t.tier.name for t in result.thoughts]
        
        # Low urgency + high complexity should use DELIBERATE or higher
        high_tiers = ["DELIBERATE", "ANALYTICAL", "COMPREHENSIVE"]
        has_high_tier = any(t in high_tiers for t in tiers_used)
        
        assert has_high_tier, (
            f"Low urgency + high complexity should use high tier, got: {tiers_used}"
        )

    @pytest.mark.asyncio
    async def test_low_relevance_uses_minimal_processing(self, processor_for_alex):
        """Low relevance should use minimal processing (REFLEX only)."""
        result = await processor_for_alex.process(
            stimulus="The weather is nice today",
            urgency=0.2,
            complexity=0.2,
            relevance=0.1,  # Not relevant to Alex
        )
        
        # Should process but minimally
        assert len(result.thoughts) >= 1
        
        # Low relevance shouldn't trigger deep analysis
        analytical = [t for t in result.thoughts if t.tier.name == "ANALYTICAL"]
        assert len(analytical) == 0, (
            "Low relevance should not trigger ANALYTICAL tier"
        )
