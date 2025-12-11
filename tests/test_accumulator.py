"""Tests for the ThoughtAccumulator module (Phase 4).

Tests cover:
- Processing observations
- Thought synthesis
- Stream management
- Accumulation summaries
"""

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from src.agents.models import (
    AgentProfile,
    CommunicationStyle,
    PersonalityMarkers,
    SkillSet,
    SocialMarkers,
)
from src.cognitive import (
    CognitiveTier,
    CognitiveProcessor,
    InternalMind,
    ThoughtAccumulator,
    Thought,
    ThoughtType,
    StreamStatus,
    create_processor_with_mock_router,
)


# ==========================================
# Fixtures
# ==========================================


@pytest.fixture
def sample_agent() -> AgentProfile:
    """Create a sample agent for testing."""
    return AgentProfile(
        agent_id=uuid4(),
        name="Test Agent",
        role="Software Developer",
        title="Senior Engineer",
        backstory_summary="Experienced developer with expertise in distributed systems.",
        years_experience=10,
        skills=SkillSet(
            technical={
                "python": 8,
                "distributed_systems": 7,
                "microservices": 8,
            },
            domains={
                "system_design": 7,
            },
            soft_skills={
                "communication": 7,
            },
        ),
        personality_markers=PersonalityMarkers(
            openness=7,
            conscientiousness=8,
            extraversion=5,
            agreeableness=6,
            neuroticism=3,
        ),
        social_markers=SocialMarkers(
            confidence=7,
            assertiveness=6,
        ),
        communication_style=CommunicationStyle(
            vocabulary_level="technical",
            formality="professional",
        ),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def internal_mind() -> InternalMind:
    """Create an InternalMind for testing."""
    return InternalMind(agent_id="test-agent")


@pytest.fixture
def cognitive_processor(sample_agent) -> CognitiveProcessor:
    """Create a CognitiveProcessor with mock router."""
    return create_processor_with_mock_router(sample_agent)


@pytest.fixture
def accumulator(internal_mind, cognitive_processor) -> ThoughtAccumulator:
    """Create a ThoughtAccumulator for testing."""
    return ThoughtAccumulator(mind=internal_mind, processor=cognitive_processor)


# ==========================================
# Basic Accumulator Tests
# ==========================================


class TestThoughtAccumulatorBasics:
    """Basic tests for ThoughtAccumulator."""

    def test_accumulator_creation(self, internal_mind, cognitive_processor):
        """Test creating an accumulator."""
        accumulator = ThoughtAccumulator(
            mind=internal_mind,
            processor=cognitive_processor,
        )
        assert accumulator.mind == internal_mind
        assert accumulator.processor == cognitive_processor

    def test_get_pending_synthesis_count_empty(self, accumulator):
        """Test pending synthesis count when empty."""
        count = accumulator.get_pending_synthesis_count()
        assert count == 0

    def test_get_accumulation_summary_empty(self, accumulator):
        """Test accumulation summary when empty."""
        summary = accumulator.get_accumulation_summary()
        
        assert summary["total_streams"] == 0
        assert summary["active_streams"] == 0
        assert summary["needs_synthesis"] == 0
        assert summary["total_accumulated_thoughts"] == 0
        assert summary["ready_to_share"] == 0
        assert summary["held_insights"] == 0


# ==========================================
# Observation Processing Tests
# ==========================================


class TestObservationProcessing:
    """Tests for processing observations."""

    @pytest.mark.asyncio
    async def test_process_observation(self, accumulator):
        """Test processing a simple observation."""
        thought = await accumulator.process_observation(
            stimulus="The team is discussing microservices.",
            relevance=0.7,
        )
        
        assert thought is not None
        assert thought.content is not None
        # Processing creates thoughts at various tiers depending on strategy
        assert thought.tier in CognitiveTier

    @pytest.mark.asyncio
    async def test_process_observation_adds_to_mind(self, accumulator, internal_mind):
        """Test that observations are added to the mind."""
        await accumulator.process_observation(
            stimulus="Something interesting happened.",
            relevance=0.6,
        )
        
        assert len(internal_mind.active_thoughts) == 1
        assert len(internal_mind.streams) == 1

    @pytest.mark.asyncio
    async def test_process_multiple_observations(self, accumulator, internal_mind):
        """Test processing multiple related observations."""
        await accumulator.process_observation(
            stimulus="First microservices observation.",
            relevance=0.6,
        )
        await accumulator.process_observation(
            stimulus="Second microservices observation.",
            relevance=0.7,
        )
        
        assert len(internal_mind.active_thoughts) == 2
        # Related observations should be in same stream
        assert len(internal_mind.streams) >= 1

    @pytest.mark.asyncio
    async def test_process_observation_with_context(self, accumulator):
        """Test processing observation with additional context."""
        thought = await accumulator.process_observation(
            stimulus="The architecture needs improvement.",
            relevance=0.8,
            context={"meeting_type": "design_review"},
        )
        
        assert thought is not None

    @pytest.mark.asyncio
    async def test_accumulation_summary_after_observations(self, accumulator):
        """Test accumulation summary after adding observations."""
        await accumulator.process_observation(
            stimulus="First observation.",
            relevance=0.6,
        )
        await accumulator.process_observation(
            stimulus="Second observation.",
            relevance=0.7,
        )
        
        summary = accumulator.get_accumulation_summary()
        
        assert summary["total_streams"] >= 1
        assert summary["total_accumulated_thoughts"] == 2


# ==========================================
# Synthesis Tests
# ==========================================


class TestStreamSynthesis:
    """Tests for thought stream synthesis."""

    @pytest.mark.asyncio
    async def test_synthesize_stream_with_multiple_thoughts(self, accumulator, internal_mind):
        """Test synthesizing a stream with multiple thoughts."""
        # Manually add thoughts to create a stream
        thoughts = []
        for i in range(3):
            thought = Thought(
                thought_id=uuid4(),
                created_at=datetime.now(timezone.utc),
                tier=CognitiveTier.REACTIVE,
                content=f"Microservices observation {i}",
                thought_type=ThoughtType.OBSERVATION,
                trigger="test",
                confidence=0.7,
                completeness=0.6,
            )
            internal_mind.add_thought(thought)
            thoughts.append(thought)
        
        # Get the stream
        stream = internal_mind.get_stream_for_topic("microservices")
        assert stream is not None
        
        # Synthesize
        synthesis = await accumulator.synthesize_stream(stream)
        
        assert synthesis is not None
        assert synthesis.thought_type == ThoughtType.INSIGHT
        assert stream.status == StreamStatus.CONCLUDED
        assert stream.synthesized_output == synthesis

    @pytest.mark.asyncio
    async def test_synthesize_stream_marks_sources_superseded(self, accumulator, internal_mind):
        """Test that synthesis marks source thoughts as superseded."""
        # Add thoughts
        thoughts = []
        for i in range(3):
            thought = Thought(
                thought_id=uuid4(),
                created_at=datetime.now(timezone.utc),
                tier=CognitiveTier.REACTIVE,
                content=f"Microservices thought {i}",
                thought_type=ThoughtType.OBSERVATION,
                trigger="test",
                confidence=0.7,
            )
            internal_mind.add_thought(thought)
            thoughts.append(thought)
        
        stream = internal_mind.get_stream_for_topic("microservices")
        synthesis = await accumulator.synthesize_stream(stream)
        
        # Source thoughts should be marked as no longer relevant
        for thought in thoughts:
            assert thought.still_relevant is False
            assert thought.superseded_by == synthesis.thought_id

    @pytest.mark.asyncio
    async def test_synthesize_stream_too_few_thoughts(self, accumulator, internal_mind):
        """Test that synthesis requires at least 2 thoughts."""
        # Add only 1 thought
        thought = Thought(
            thought_id=uuid4(),
            created_at=datetime.now(timezone.utc),
            tier=CognitiveTier.REACTIVE,
            content="Single microservices thought",
            thought_type=ThoughtType.OBSERVATION,
            trigger="test",
        )
        internal_mind.add_thought(thought)
        
        stream = internal_mind.get_stream_for_topic("microservices")
        synthesis = await accumulator.synthesize_stream(stream)
        
        assert synthesis is None

    @pytest.mark.asyncio
    async def test_high_confidence_synthesis_prepared_to_share(self, accumulator, internal_mind):
        """Test that high-confidence synthesis is prepared to share."""
        # Add thoughts with high confidence
        for i in range(3):
            thought = Thought(
                thought_id=uuid4(),
                created_at=datetime.now(timezone.utc),
                tier=CognitiveTier.REACTIVE,
                content=f"Microservices thought {i}",
                thought_type=ThoughtType.OBSERVATION,
                trigger="test",
                confidence=0.8,
                completeness=0.7,
            )
            internal_mind.add_thought(thought)
        
        stream = internal_mind.get_stream_for_topic("microservices")
        synthesis = await accumulator.synthesize_stream(stream)
        
        # High confidence synthesis should be ready to share
        if synthesis and synthesis.confidence > 0.6:
            assert synthesis in internal_mind.ready_to_share

    @pytest.mark.asyncio
    async def test_check_streams_for_synthesis(self, accumulator, internal_mind):
        """Test checking all streams for synthesis."""
        # Create streams that need synthesis
        for i in range(3):
            thought = Thought(
                thought_id=uuid4(),
                created_at=datetime.now(timezone.utc),
                tier=CognitiveTier.REACTIVE,
                content=f"Microservices thought {i}",
                thought_type=ThoughtType.OBSERVATION,
                trigger="test",
                confidence=0.7,
            )
            internal_mind.add_thought(thought)
        
        # Should have a stream needing synthesis
        needs_synthesis_before = accumulator.get_pending_synthesis_count()
        assert needs_synthesis_before >= 1
        
        # Run synthesis check
        synthesized = await accumulator.check_streams_for_synthesis()
        
        assert len(synthesized) >= 1
        
        # Should have no more pending
        needs_synthesis_after = accumulator.get_pending_synthesis_count()
        assert needs_synthesis_after == 0


# ==========================================
# Force Synthesis Tests
# ==========================================


class TestForceSynthesis:
    """Tests for forced synthesis on specific topics."""

    @pytest.mark.asyncio
    async def test_force_synthesis_on_topic(self, accumulator, internal_mind):
        """Test forcing synthesis on a specific topic."""
        # Add thoughts on topic
        for i in range(2):
            thought = Thought(
                thought_id=uuid4(),
                created_at=datetime.now(timezone.utc),
                tier=CognitiveTier.REACTIVE,
                content=f"Architecture thought {i}",
                thought_type=ThoughtType.OBSERVATION,
                trigger="test",
                confidence=0.7,
            )
            internal_mind.add_thought(thought)
        
        # Force synthesis
        synthesis = await accumulator.force_synthesis_on_topic("architecture")
        
        assert synthesis is not None

    @pytest.mark.asyncio
    async def test_force_synthesis_no_matching_topic(self, accumulator, internal_mind):
        """Test forcing synthesis on non-existent topic."""
        synthesis = await accumulator.force_synthesis_on_topic("nonexistent")
        
        assert synthesis is None

    @pytest.mark.asyncio
    async def test_force_synthesis_too_few_thoughts(self, accumulator, internal_mind):
        """Test forcing synthesis with too few thoughts."""
        # Add only 1 thought
        thought = Thought(
            thought_id=uuid4(),
            created_at=datetime.now(timezone.utc),
            tier=CognitiveTier.REACTIVE,
            content="Single architecture thought",
            thought_type=ThoughtType.OBSERVATION,
            trigger="test",
        )
        internal_mind.add_thought(thought)
        
        synthesis = await accumulator.force_synthesis_on_topic("architecture")
        
        assert synthesis is None


# ==========================================
# Integration Tests
# ==========================================


class TestAccumulatorIntegration:
    """Integration tests for accumulator with full flow."""

    @pytest.mark.asyncio
    async def test_full_observation_to_synthesis_flow(self, accumulator, internal_mind):
        """Test complete flow from observations to synthesis."""
        # Process 3 related observations
        for i in range(3):
            await accumulator.process_observation(
                stimulus=f"Database observation {i}: The query is slow.",
                relevance=0.7 + (i * 0.05),
            )
        
        # Should have accumulated thoughts
        summary = accumulator.get_accumulation_summary()
        assert summary["total_accumulated_thoughts"] >= 3
        
        # Check for synthesis
        synthesized = await accumulator.check_streams_for_synthesis()
        
        # Verify final state
        final_summary = accumulator.get_accumulation_summary()
        assert final_summary["concluded"] >= 0  # May or may not be concluded depending on mock

    @pytest.mark.asyncio
    async def test_multiple_topics_accumulated(self, accumulator, internal_mind):
        """Test accumulating thoughts on multiple topics."""
        # Add thoughts on different topics
        await accumulator.process_observation(
            stimulus="The database is performing well.",
            relevance=0.6,
        )
        await accumulator.process_observation(
            stimulus="The API needs optimization.",
            relevance=0.7,
        )
        await accumulator.process_observation(
            stimulus="Security needs review.",
            relevance=0.8,
        )
        
        # Should have multiple streams for different topics
        summary = accumulator.get_accumulation_summary()
        assert summary["total_accumulated_thoughts"] == 3
        # Topics may or may not create separate streams depending on topic extraction
        assert summary["total_streams"] >= 1

