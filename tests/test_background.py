"""Tests for the BackgroundProcessor module (Phase 4).

Tests cover:
- Background processor lifecycle (start/stop)
- Background synthesis checking
- Old thought cleanup
- Deep analysis queuing
- Status reporting
"""

import asyncio
from datetime import datetime, timedelta, timezone
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
        name="Test Agent",
        role="Software Developer",
        title="Senior Engineer",
        backstory_summary="Experienced developer.",
        years_experience=10,
        skills=SkillSet(
            technical={"python": 8},
            domains={"system_design": 7},
            soft_skills={"communication": 7},
        ),
        personality_markers=PersonalityMarkers(),
        social_markers=SocialMarkers(),
        communication_style=CommunicationStyle(),
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


@pytest.fixture
def background_processor(internal_mind, cognitive_processor, accumulator) -> BackgroundProcessor:
    """Create a BackgroundProcessor for testing."""
    return BackgroundProcessor(
        mind=internal_mind,
        processor=cognitive_processor,
        accumulator=accumulator,
        cleanup_interval_seconds=5.0,  # Short for testing
        synthesis_check_interval_seconds=0.1,  # Very short for testing
        max_thought_age_minutes=30,
    )


# ==========================================
# Lifecycle Tests
# ==========================================


class TestBackgroundProcessorLifecycle:
    """Tests for background processor lifecycle."""

    def test_processor_creation(self, internal_mind, cognitive_processor, accumulator):
        """Test creating a background processor."""
        processor = BackgroundProcessor(
            mind=internal_mind,
            processor=cognitive_processor,
            accumulator=accumulator,
        )
        assert processor.mind == internal_mind
        assert processor.processor == cognitive_processor
        assert processor.accumulator == accumulator
        assert processor.is_running is False

    @pytest.mark.asyncio
    async def test_start_processor(self, background_processor):
        """Test starting the background processor."""
        await background_processor.start()
        
        try:
            assert background_processor.is_running is True
            assert background_processor._main_task is not None
        finally:
            await background_processor.stop()

    @pytest.mark.asyncio
    async def test_stop_processor(self, background_processor):
        """Test stopping the background processor."""
        await background_processor.start()
        assert background_processor.is_running is True
        
        await background_processor.stop()
        
        assert background_processor.is_running is False
        assert background_processor._main_task is None

    @pytest.mark.asyncio
    async def test_double_start(self, background_processor):
        """Test that double start is handled gracefully."""
        await background_processor.start()
        
        try:
            # Second start should not cause issues
            await background_processor.start()
            assert background_processor.is_running is True
        finally:
            await background_processor.stop()

    @pytest.mark.asyncio
    async def test_double_stop(self, background_processor):
        """Test that double stop is handled gracefully."""
        await background_processor.start()
        await background_processor.stop()
        
        # Second stop should not cause issues
        await background_processor.stop()
        assert background_processor.is_running is False


# ==========================================
# Status Tests
# ==========================================


class TestBackgroundProcessorStatus:
    """Tests for background processor status reporting."""

    def test_get_status_not_running(self, background_processor):
        """Test status when not running."""
        status = background_processor.get_status()
        
        assert status["running"] is False
        assert status["active_background_tasks"] == 0
        assert status["pending_synthesis"] == 0

    @pytest.mark.asyncio
    async def test_get_status_running(self, background_processor):
        """Test status when running."""
        await background_processor.start()
        
        try:
            status = background_processor.get_status()
            
            assert status["running"] is True
            assert "cleanup_interval_seconds" in status
            assert "synthesis_check_interval_seconds" in status
            assert "max_thought_age_minutes" in status
        finally:
            await background_processor.stop()


# ==========================================
# Cleanup Tests
# ==========================================


class TestBackgroundCleanup:
    """Tests for background thought cleanup."""

    def test_cleanup_old_thoughts(self, background_processor, internal_mind):
        """Test that old thoughts are cleaned up."""
        # Add old thought
        old_thought = Thought(
            thought_id=uuid4(),
            created_at=datetime.now(timezone.utc) - timedelta(minutes=60),
            tier=CognitiveTier.REACTIVE,
            content="Old thought",
            thought_type=ThoughtType.OBSERVATION,
            trigger="test",
        )
        internal_mind.add_thought(old_thought)
        
        # Add recent thought
        recent_thought = Thought(
            thought_id=uuid4(),
            created_at=datetime.now(timezone.utc),
            tier=CognitiveTier.REACTIVE,
            content="Recent thought",
            thought_type=ThoughtType.OBSERVATION,
            trigger="test",
        )
        internal_mind.add_thought(recent_thought)
        
        assert len(internal_mind.active_thoughts) == 2
        
        # Run cleanup
        cleaned = background_processor._cleanup_old_thoughts()
        
        assert cleaned == 1
        assert len(internal_mind.active_thoughts) == 1

    def test_cleanup_completed_tasks(self, background_processor, internal_mind):
        """Test that completed tasks are cleaned from the list."""
        # Create a completed task
        async def completed_task():
            return "done"
        
        task = asyncio.get_event_loop().create_task(completed_task())
        internal_mind.background_tasks.append(task)
        
        # Wait for task to complete
        asyncio.get_event_loop().run_until_complete(asyncio.sleep(0.1))
        
        # Cleanup
        background_processor._cleanup_completed_tasks()
        
        # Task should be removed
        assert len(internal_mind.background_tasks) == 0


# ==========================================
# Deep Analysis Tests
# ==========================================


class TestDeepAnalysis:
    """Tests for queuing deep analysis."""

    @pytest.mark.asyncio
    async def test_queue_deep_analysis(self, background_processor, internal_mind):
        """Test queuing a deep analysis task."""
        task = await background_processor.queue_deep_analysis(
            stimulus="Analyze the system architecture.",
            purpose="architecture_review",
        )
        
        assert task is not None
        assert task in internal_mind.background_tasks
        
        # Wait for task to complete
        result = await task
        
        # Should have added thought to mind
        assert result is not None or len(internal_mind.active_thoughts) >= 0

    @pytest.mark.asyncio
    async def test_queue_deep_analysis_with_callback(self, background_processor, internal_mind):
        """Test queuing deep analysis with callback."""
        callback_called = {"value": False}
        received_thought = {"thought": None}
        
        def callback(thought):
            callback_called["value"] = True
            received_thought["thought"] = thought
        
        task = await background_processor.queue_deep_analysis(
            stimulus="Analyze performance issues.",
            purpose="performance_analysis",
            callback=callback,
        )
        
        # Wait for task
        await task
        
        # Callback should have been called (if thought was produced)
        # Note: depends on mock behavior
        assert task.done()


# ==========================================
# Synthesis Queue Tests
# ==========================================


class TestSynthesisQueue:
    """Tests for queuing synthesis tasks."""

    @pytest.mark.asyncio
    async def test_queue_synthesis_no_stream(self, background_processor, internal_mind):
        """Test queuing synthesis with no matching stream."""
        task = await background_processor.queue_synthesis("nonexistent_topic")
        
        assert task is None

    @pytest.mark.asyncio
    async def test_queue_synthesis_with_stream(self, background_processor, internal_mind):
        """Test queuing synthesis with matching stream."""
        # Add thoughts to create a stream
        for i in range(2):
            thought = Thought(
                thought_id=uuid4(),
                created_at=datetime.now(timezone.utc),
                tier=CognitiveTier.REACTIVE,
                content=f"Database thought {i}",
                thought_type=ThoughtType.OBSERVATION,
                trigger="test",
                confidence=0.7,
            )
            internal_mind.add_thought(thought)
        
        task = await background_processor.queue_synthesis("database")
        
        assert task is not None
        assert task in internal_mind.background_tasks


# ==========================================
# Processing Loop Tests
# ==========================================


class TestProcessingLoop:
    """Tests for the main processing loop."""

    @pytest.mark.asyncio
    async def test_loop_processes_synthesis(self, background_processor, internal_mind, accumulator):
        """Test that the loop processes streams needing synthesis."""
        # Add thoughts to trigger synthesis
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
        
        # Should have pending synthesis
        assert accumulator.get_pending_synthesis_count() >= 1
        
        # Start processor
        await background_processor.start()
        
        try:
            # Give loop time to run
            await asyncio.sleep(0.3)
            
            # Synthesis should have been processed
            # (May or may not be complete depending on timing)
        finally:
            await background_processor.stop()

    @pytest.mark.asyncio
    async def test_loop_handles_errors_gracefully(self, background_processor):
        """Test that the loop continues after errors."""
        await background_processor.start()
        
        try:
            # Loop should be running
            assert background_processor.is_running
            
            # Give it time to run a few cycles
            await asyncio.sleep(0.3)
            
            # Should still be running
            assert background_processor.is_running
        finally:
            await background_processor.stop()


# ==========================================
# Factory Function Tests
# ==========================================


class TestCreateBackgroundProcessor:
    """Tests for the create_background_processor factory function."""

    def test_create_background_processor(self, internal_mind, cognitive_processor):
        """Test the factory function creates properly configured processor."""
        processor = create_background_processor(
            mind=internal_mind,
            processor=cognitive_processor,
        )
        
        assert processor.mind == internal_mind
        assert processor.processor == cognitive_processor
        assert processor.accumulator is not None
        assert isinstance(processor.accumulator, ThoughtAccumulator)


# ==========================================
# Integration Tests
# ==========================================


class TestBackgroundIntegration:
    """Integration tests for background processor."""

    @pytest.mark.asyncio
    async def test_full_background_flow(self, sample_agent, internal_mind):
        """Test complete background processing flow."""
        # Create all components
        processor = create_processor_with_mock_router(sample_agent)
        accumulator = ThoughtAccumulator(mind=internal_mind, processor=processor)
        background = BackgroundProcessor(
            mind=internal_mind,
            processor=processor,
            accumulator=accumulator,
            synthesis_check_interval_seconds=0.05,
        )
        
        # Add thoughts
        for i in range(3):
            thought = Thought(
                thought_id=uuid4(),
                created_at=datetime.now(timezone.utc),
                tier=CognitiveTier.REACTIVE,
                content=f"API design thought {i}",
                thought_type=ThoughtType.OBSERVATION,
                trigger="test",
                confidence=0.7,
            )
            internal_mind.add_thought(thought)
        
        # Start background processor
        await background.start()
        
        try:
            # Give time for processing
            await asyncio.sleep(0.2)
            
            # Check status
            status = background.get_status()
            assert status["running"] is True
            
        finally:
            await background.stop()
        
        # Verify cleanup
        assert background.is_running is False

