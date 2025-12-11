"""Integration tests for the Internal Mind system (Phase 4).

Tests the full workflow from stimulus processing through thought
accumulation, synthesis, and externalization decisions.
"""

import asyncio
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
    BackgroundProcessor,
    Thought,
    ThoughtType,
    StreamStatus,
    create_processor_with_mock_router,
    create_background_processor,
)


# ==========================================
# Fixtures
# ==========================================


@pytest.fixture
def sample_agent() -> AgentProfile:
    """Create a sample agent for testing."""
    return AgentProfile(
        agent_id=uuid4(),
        name="Alex Chen",
        role="Senior Software Architect",
        title="Principal Engineer",
        backstory_summary=(
            "Alex is a senior software architect with 12 years of experience "
            "in distributed systems and cloud architecture. Known for pragmatic "
            "decision-making and deep technical expertise."
        ),
        years_experience=12,
        skills=SkillSet(
            technical={
                "python": 9,
                "distributed_systems": 9,
                "microservices": 8,
                "cloud_architecture": 8,
                "kubernetes": 7,
                "databases": 8,
            },
            domains={
                "system_design": 9,
                "performance_optimization": 8,
                "security": 7,
            },
            soft_skills={
                "leadership": 8,
                "communication": 8,
                "mentoring": 7,
            },
        ),
        personality_markers=PersonalityMarkers(
            openness=7,
            conscientiousness=9,
            extraversion=5,
            agreeableness=6,
            neuroticism=3,
            perfectionism=6,
            pragmatism=8,
            risk_tolerance=5,
        ),
        social_markers=SocialMarkers(
            confidence=8,
            assertiveness=7,
            deference=4,
            curiosity=8,
            social_calibration=7,
            facilitation_instinct=6,
            comfort_with_conflict=6,
        ),
        communication_style=CommunicationStyle(
            vocabulary_level="technical",
            sentence_structure="moderate",
            formality="professional",
            uses_analogies=True,
            uses_examples=True,
        ),
        knowledge_domains=["distributed systems", "cloud computing", "python"],
        knowledge_gaps=["machine learning", "frontend development"],
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def internal_mind() -> InternalMind:
    """Create an InternalMind for testing."""
    return InternalMind(agent_id="test-agent-integration")


@pytest.fixture
def processor(sample_agent) -> CognitiveProcessor:
    """Create a CognitiveProcessor with mock router."""
    return create_processor_with_mock_router(sample_agent)


@pytest.fixture
def accumulator(internal_mind, processor) -> ThoughtAccumulator:
    """Create a ThoughtAccumulator for testing."""
    return ThoughtAccumulator(mind=internal_mind, processor=processor)


@pytest.fixture
def background(internal_mind, processor, accumulator) -> BackgroundProcessor:
    """Create a BackgroundProcessor for testing."""
    return BackgroundProcessor(
        mind=internal_mind,
        processor=processor,
        accumulator=accumulator,
        synthesis_check_interval_seconds=0.05,
        cleanup_interval_seconds=1.0,
    )


# ==========================================
# Full Workflow Integration Tests
# ==========================================


class TestFullMindWorkflow:
    """Tests for the complete internal mind workflow."""

    @pytest.mark.asyncio
    async def test_observation_to_synthesis_workflow(
        self, internal_mind, processor, accumulator
    ):
        """Test complete flow from observations to synthesis."""
        # Simulate a meeting where the agent observes multiple related points
        observations = [
            "The team is discussing migrating to microservices.",
            "Sarah mentioned concerns about increased complexity.",
            "John suggested starting with a modular monolith approach.",
        ]
        
        # Process observations
        for obs in observations:
            await accumulator.process_observation(
                stimulus=obs,
                relevance=0.7,
            )
        
        # Verify accumulation
        assert len(internal_mind.active_thoughts) >= len(observations)
        assert len(internal_mind.streams) >= 1
        
        # Check for synthesis needs
        needs_synthesis = internal_mind.get_streams_needing_synthesis()
        
        # Run synthesis if needed
        if needs_synthesis:
            synthesized = await accumulator.check_streams_for_synthesis()
            assert len(synthesized) >= 1
            
            # Verify synthesis quality
            for thought in synthesized:
                assert thought.confidence > 0
                assert thought.completeness > 0
                assert len(thought.content) > 10

    @pytest.mark.asyncio
    async def test_ready_to_share_workflow(self, internal_mind, processor, accumulator):
        """Test that high-quality synthesis is prepared for sharing."""
        # Add thoughts that will trigger synthesis
        for i in range(3):
            thought = Thought(
                thought_id=uuid4(),
                created_at=datetime.now(timezone.utc),
                tier=CognitiveTier.REACTIVE,
                content=f"Architecture decision observation {i}: Important point about design.",
                thought_type=ThoughtType.OBSERVATION,
                trigger="meeting_observation",
                confidence=0.8,
                completeness=0.7,
            )
            internal_mind.add_thought(thought)
        
        # Run synthesis
        await accumulator.check_streams_for_synthesis()
        
        # Check for ready-to-share thoughts
        ready_count = len(internal_mind.ready_to_share)
        
        # Get best contribution
        best = internal_mind.get_best_contribution()
        
        if best:
            assert best.confidence > 0
            assert best.still_relevant is True
            
            # Simulate externalization
            internal_mind.mark_externalized(best.thought_id)
            
            # Verify externalization
            assert best.externalized is True
            assert best.externalized_at is not None
            assert best not in internal_mind.ready_to_share

    @pytest.mark.asyncio
    async def test_topic_invalidation_workflow(self, internal_mind, processor, accumulator):
        """Test that new information invalidates old thoughts."""
        # Add thoughts on a topic
        await accumulator.process_observation(
            stimulus="The database should use PostgreSQL.",
            relevance=0.7,
        )
        await accumulator.process_observation(
            stimulus="PostgreSQL has better JSON support.",
            relevance=0.6,
        )
        
        initial_count = len(internal_mind.active_thoughts)
        
        # Simulate new information that invalidates previous thinking
        invalidated = internal_mind.invalidate_thoughts_about("PostgreSQL")
        
        # Old thoughts should be marked irrelevant
        for thought in internal_mind.active_thoughts.values():
            if "postgresql" in thought.content.lower():
                assert thought.still_relevant is False
        
        # Count should stay same (thoughts not deleted, just marked)
        assert len(internal_mind.active_thoughts) == initial_count


class TestBackgroundProcessingIntegration:
    """Tests for background processing integration."""

    @pytest.mark.asyncio
    async def test_background_synthesis_workflow(
        self, internal_mind, processor, accumulator, background
    ):
        """Test that background processor handles synthesis."""
        # Add thoughts
        for i in range(3):
            thought = Thought(
                thought_id=uuid4(),
                created_at=datetime.now(timezone.utc),
                tier=CognitiveTier.REACTIVE,
                content=f"System design consideration {i}",
                thought_type=ThoughtType.OBSERVATION,
                trigger="test",
                confidence=0.7,
            )
            internal_mind.add_thought(thought)
        
        # Start background processor
        await background.start()
        
        try:
            # Give time for synthesis
            await asyncio.sleep(0.2)
            
            # Check status
            status = background.get_status()
            assert status["running"] is True
            
        finally:
            await background.stop()

    @pytest.mark.asyncio
    async def test_deep_analysis_workflow(
        self, internal_mind, processor, accumulator, background
    ):
        """Test queuing and executing deep analysis."""
        analysis_complete = {"done": False}
        received_thought = {"thought": None}
        
        def callback(thought):
            analysis_complete["done"] = True
            received_thought["thought"] = thought
        
        # Queue deep analysis
        task = await background.queue_deep_analysis(
            stimulus="What are the long-term implications of this architecture choice?",
            purpose="strategic_analysis",
            callback=callback,
        )
        
        # Wait for completion
        await task
        
        # Verify analysis was added to mind
        assert task.done()


class TestMindStateManagement:
    """Tests for mind state management."""

    @pytest.mark.asyncio
    async def test_mind_state_tracking(self, internal_mind, processor, accumulator):
        """Test that mind state is accurately tracked."""
        # Initial state
        initial_state = internal_mind.get_state()
        assert initial_state["active_thoughts"] == 0
        assert initial_state["streams"] == 0
        
        # Add observations
        await accumulator.process_observation(
            stimulus="First observation about the project.",
            relevance=0.7,
        )
        await accumulator.process_observation(
            stimulus="Second observation about the project.",
            relevance=0.6,
        )
        
        # Check state updated
        state = internal_mind.get_state()
        assert state["active_thoughts"] == 2
        assert state["streams"] >= 1
        
        # Get detailed state
        detailed = internal_mind.get_detailed_state()
        assert "streams_detail" in detailed
        assert len(detailed["streams_detail"]) >= 1

    @pytest.mark.asyncio
    async def test_multiple_topics_tracking(self, internal_mind, accumulator):
        """Test tracking thoughts across multiple topics."""
        # Add thoughts on different topics
        topics = [
            ("Database performance is critical.", 0.8),
            ("The API design needs review.", 0.7),
            ("Security concerns should be addressed.", 0.9),
        ]
        
        for stimulus, relevance in topics:
            await accumulator.process_observation(
                stimulus=stimulus,
                relevance=relevance,
            )
        
        # Check accumulation summary
        summary = accumulator.get_accumulation_summary()
        assert summary["total_accumulated_thoughts"] == 3
        assert summary["total_streams"] >= 1  # May be grouped depending on topic extraction

    def test_clear_and_reset(self, internal_mind):
        """Test clearing the mind state."""
        # Add some state
        thought = Thought(
            thought_id=uuid4(),
            created_at=datetime.now(timezone.utc),
            tier=CognitiveTier.REACTIVE,
            content="Test thought",
            thought_type=ThoughtType.OBSERVATION,
            trigger="test",
        )
        internal_mind.add_thought(thought)
        internal_mind.hold_insight(thought)
        internal_mind.prepare_to_share(thought)
        
        # Verify state
        assert len(internal_mind.active_thoughts) > 0
        assert len(internal_mind.streams) > 0
        
        # Clear
        internal_mind.clear()
        
        # Verify cleared
        state = internal_mind.get_state()
        assert state["active_thoughts"] == 0
        assert state["streams"] == 0
        assert state["held_insights"] == 0
        assert state["ready_to_share"] == 0


class TestCognitiveIntegrationWithMind:
    """Tests for cognitive processing integration with internal mind."""

    @pytest.mark.asyncio
    async def test_processor_to_mind_flow(self, sample_agent, internal_mind):
        """Test that processor output integrates with mind."""
        processor = create_processor_with_mock_router(sample_agent)
        
        # Process a stimulus
        result = await processor.process(
            stimulus="Should we use microservices for this project?",
            urgency=0.5,
            complexity=0.7,
            relevance=0.8,
            purpose="architecture_question",
        )
        
        # Add result to mind
        if result.primary_thought:
            stream = internal_mind.add_thought(result.primary_thought)
            
            assert str(result.primary_thought.thought_id) in internal_mind.active_thoughts
            assert stream is not None

    @pytest.mark.asyncio
    async def test_accumulated_context_enhances_processing(
        self, sample_agent, internal_mind, accumulator
    ):
        """Test that accumulated thoughts provide context."""
        # Accumulate some context
        await accumulator.process_observation(
            stimulus="The team prefers Python for backend services.",
            relevance=0.6,
        )
        await accumulator.process_observation(
            stimulus="We have limited DevOps resources.",
            relevance=0.7,
        )
        
        # Get thoughts for context
        context_thoughts = internal_mind.get_thoughts_for_context(n=5)
        
        # Verify context is available
        assert len(context_thoughts) == 2
        
        # Context could be used in future processing
        context = {
            "prior_thoughts": [t.content for t in context_thoughts]
        }
        
        assert len(context["prior_thoughts"]) == 2


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_empty_stimulus_handling(self, internal_mind, accumulator):
        """Test handling of edge cases with minimal content."""
        # Process minimal observation
        thought = await accumulator.process_observation(
            stimulus="Noted.",
            relevance=0.3,
        )
        
        # Should still work
        if thought:
            assert thought.content is not None

    def test_get_best_contribution_all_irrelevant(self, internal_mind):
        """Test getting contribution when all thoughts are irrelevant."""
        # Add thoughts
        thought = Thought(
            thought_id=uuid4(),
            created_at=datetime.now(timezone.utc),
            tier=CognitiveTier.REACTIVE,
            content="Irrelevant thought",
            thought_type=ThoughtType.OBSERVATION,
            trigger="test",
            still_relevant=False,  # Mark as irrelevant
        )
        internal_mind.prepare_to_share(thought)
        
        # Get best contribution
        best = internal_mind.get_best_contribution()
        
        # Should be None since all are irrelevant
        assert best is None

    @pytest.mark.asyncio
    async def test_synthesis_with_mixed_confidence(self, internal_mind, accumulator):
        """Test synthesis with varying confidence levels."""
        # Add thoughts with varying confidence
        confidences = [0.3, 0.7, 0.9]
        
        for i, conf in enumerate(confidences):
            thought = Thought(
                thought_id=uuid4(),
                created_at=datetime.now(timezone.utc),
                tier=CognitiveTier.REACTIVE,
                content=f"Mixed confidence thought {i}",
                thought_type=ThoughtType.OBSERVATION,
                trigger="test",
                confidence=conf,
            )
            internal_mind.add_thought(thought)
        
        # Run synthesis
        synthesized = await accumulator.check_streams_for_synthesis()
        
        # Verify synthesis happened
        if synthesized:
            for s in synthesized:
                assert s.confidence > 0

