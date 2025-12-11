"""Tests for the Internal Mind module (Phase 4).

Tests cover:
- ThoughtStream creation and management
- InternalMind thought management
- Stream synthesis triggering
- Thought invalidation
- Ready-to-share queue management
- Cleanup of old thoughts
"""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from src.cognitive import (
    CognitiveTier,
    Thought,
    ThoughtType,
    InternalMind,
    ThoughtStream,
    StreamStatus,
)


# ==========================================
# Fixtures
# ==========================================


@pytest.fixture
def sample_thought() -> Thought:
    """Create a sample thought for testing."""
    return Thought(
        thought_id=uuid4(),
        created_at=datetime.now(timezone.utc),
        tier=CognitiveTier.REACTIVE,
        content="This is a test thought about microservices.",
        thought_type=ThoughtType.OBSERVATION,
        trigger="test",
        confidence=0.7,
        completeness=0.6,
    )


@pytest.fixture
def sample_thought_2() -> Thought:
    """Create a second sample thought for testing."""
    return Thought(
        thought_id=uuid4(),
        created_at=datetime.now(timezone.utc),
        tier=CognitiveTier.REACTIVE,
        content="Another thought about microservices architecture.",
        thought_type=ThoughtType.INSIGHT,
        trigger="test",
        confidence=0.8,
        completeness=0.7,
    )


@pytest.fixture
def sample_thought_3() -> Thought:
    """Create a third sample thought for testing."""
    return Thought(
        thought_id=uuid4(),
        created_at=datetime.now(timezone.utc),
        tier=CognitiveTier.DELIBERATE,
        content="Microservices can be complex for small teams.",
        thought_type=ThoughtType.CONCERN,
        trigger="test",
        confidence=0.9,
        completeness=0.85,
    )


@pytest.fixture
def internal_mind() -> InternalMind:
    """Create an InternalMind for testing."""
    return InternalMind(agent_id="test-agent-123")


# ==========================================
# ThoughtStream Tests
# ==========================================


class TestThoughtStream:
    """Tests for ThoughtStream class."""

    def test_stream_creation(self):
        """Test creating a thought stream."""
        stream = ThoughtStream(
            stream_id="stream-1",
            topic="microservices",
        )
        assert stream.stream_id == "stream-1"
        assert stream.topic == "microservices"
        assert stream.status == StreamStatus.ACTIVE
        assert len(stream.thoughts) == 0
        assert stream.synthesized_output is None
        assert stream.ready_to_externalize is False

    def test_add_thought(self, sample_thought):
        """Test adding thoughts to a stream."""
        stream = ThoughtStream(
            stream_id="stream-1",
            topic="microservices",
        )
        stream.add_thought(sample_thought)
        
        assert stream.thought_count == 1
        assert stream.thoughts[0] == sample_thought

    def test_add_multiple_thoughts_links_related(self, sample_thought, sample_thought_2):
        """Test that adding multiple thoughts creates relationships."""
        stream = ThoughtStream(
            stream_id="stream-1",
            topic="microservices",
        )
        stream.add_thought(sample_thought)
        stream.add_thought(sample_thought_2)
        
        assert stream.thought_count == 2
        # Second thought should reference the first
        assert sample_thought.thought_id in sample_thought_2.related_thought_ids

    def test_get_recent(self, sample_thought, sample_thought_2, sample_thought_3):
        """Test getting recent thoughts."""
        stream = ThoughtStream(
            stream_id="stream-1",
            topic="microservices",
        )
        stream.add_thought(sample_thought)
        stream.add_thought(sample_thought_2)
        stream.add_thought(sample_thought_3)
        
        recent = stream.get_recent(2)
        assert len(recent) == 2
        assert recent[0] == sample_thought_2
        assert recent[1] == sample_thought_3

    def test_avg_confidence(self, sample_thought, sample_thought_2):
        """Test average confidence calculation."""
        stream = ThoughtStream(
            stream_id="stream-1",
            topic="microservices",
        )
        stream.add_thought(sample_thought)  # 0.7
        stream.add_thought(sample_thought_2)  # 0.8
        
        assert stream.avg_confidence == pytest.approx(0.75)

    def test_avg_completeness(self, sample_thought, sample_thought_2):
        """Test average completeness calculation."""
        stream = ThoughtStream(
            stream_id="stream-1",
            topic="microservices",
        )
        stream.add_thought(sample_thought)  # 0.6
        stream.add_thought(sample_thought_2)  # 0.7
        
        assert stream.avg_completeness == pytest.approx(0.65)

    def test_time_span(self):
        """Test time span calculation."""
        stream = ThoughtStream(
            stream_id="stream-1",
            topic="microservices",
        )
        
        # Add thoughts with different timestamps
        thought1 = Thought(
            thought_id=uuid4(),
            created_at=datetime.now(timezone.utc) - timedelta(seconds=60),
            tier=CognitiveTier.REACTIVE,
            content="First thought",
            thought_type=ThoughtType.OBSERVATION,
            trigger="test",
        )
        thought2 = Thought(
            thought_id=uuid4(),
            created_at=datetime.now(timezone.utc),
            tier=CognitiveTier.REACTIVE,
            content="Second thought",
            thought_type=ThoughtType.OBSERVATION,
            trigger="test",
        )
        
        stream.add_thought(thought1)
        stream.add_thought(thought2)
        
        # Time span should be approximately 60 seconds
        assert stream.time_span_seconds >= 59
        assert stream.time_span_seconds <= 61

    def test_to_dict(self, sample_thought):
        """Test stream to_dict method."""
        stream = ThoughtStream(
            stream_id="stream-1",
            topic="microservices",
        )
        stream.add_thought(sample_thought)
        
        d = stream.to_dict()
        assert d["stream_id"] == "stream-1"
        assert d["topic"] == "microservices"
        assert d["thought_count"] == 1
        assert d["status"] == StreamStatus.ACTIVE
        assert "created_at" in d


# ==========================================
# InternalMind Tests
# ==========================================


class TestInternalMind:
    """Tests for InternalMind class."""

    def test_mind_creation(self, internal_mind):
        """Test creating an internal mind."""
        assert internal_mind.agent_id == "test-agent-123"
        assert len(internal_mind.active_thoughts) == 0
        assert len(internal_mind.streams) == 0
        assert len(internal_mind.held_insights) == 0
        assert len(internal_mind.ready_to_share) == 0

    def test_add_thought(self, internal_mind, sample_thought):
        """Test adding a thought to the mind."""
        stream = internal_mind.add_thought(sample_thought)
        
        assert str(sample_thought.thought_id) in internal_mind.active_thoughts
        assert len(internal_mind.streams) == 1
        assert stream.thought_count == 1

    def test_add_thought_creates_stream(self, internal_mind, sample_thought):
        """Test that adding a thought creates a stream."""
        stream = internal_mind.add_thought(sample_thought)
        
        assert stream.topic is not None
        assert stream.stream_id in internal_mind.streams

    def test_related_thoughts_same_stream(self, internal_mind):
        """Test that related thoughts are added to the same stream."""
        # Create two thoughts with clearly overlapping topics
        thought1 = Thought(
            thought_id=uuid4(),
            created_at=datetime.now(timezone.utc),
            tier=CognitiveTier.REACTIVE,
            content="The database performance is slow.",
            thought_type=ThoughtType.OBSERVATION,
            trigger="test",
            confidence=0.7,
        )
        thought2 = Thought(
            thought_id=uuid4(),
            created_at=datetime.now(timezone.utc),
            tier=CognitiveTier.REACTIVE,
            content="Database queries need optimization.",
            thought_type=ThoughtType.INSIGHT,
            trigger="test",
            confidence=0.8,
        )
        
        stream1 = internal_mind.add_thought(thought1)
        stream2 = internal_mind.add_thought(thought2)
        
        # Both thoughts about database should be in same stream
        assert stream1.stream_id == stream2.stream_id
        assert stream1.thought_count == 2

    def test_unrelated_thoughts_different_streams(self, internal_mind, sample_thought):
        """Test that unrelated thoughts create different streams."""
        # Add microservices thought
        stream1 = internal_mind.add_thought(sample_thought)
        
        # Add unrelated thought
        unrelated = Thought(
            thought_id=uuid4(),
            created_at=datetime.now(timezone.utc),
            tier=CognitiveTier.REACTIVE,
            content="Testing is important for quality.",
            thought_type=ThoughtType.OBSERVATION,
            trigger="test",
        )
        stream2 = internal_mind.add_thought(unrelated)
        
        assert stream1.stream_id != stream2.stream_id
        assert len(internal_mind.streams) == 2

    def test_hold_insight(self, internal_mind, sample_thought):
        """Test holding an insight."""
        internal_mind.hold_insight(sample_thought)
        
        assert sample_thought in internal_mind.held_insights
        assert sample_thought.externalized is False

    def test_prepare_to_share(self, internal_mind, sample_thought):
        """Test preparing a thought to share."""
        internal_mind.prepare_to_share(sample_thought)
        
        assert sample_thought in internal_mind.ready_to_share

    def test_prepare_to_share_no_duplicates(self, internal_mind, sample_thought):
        """Test that prepare_to_share doesn't add duplicates."""
        internal_mind.prepare_to_share(sample_thought)
        internal_mind.prepare_to_share(sample_thought)
        
        assert internal_mind.ready_to_share.count(sample_thought) == 1

    def test_get_best_contribution(self, internal_mind, sample_thought, sample_thought_2, sample_thought_3):
        """Test getting the best contribution."""
        # Add thoughts with varying quality
        internal_mind.prepare_to_share(sample_thought)  # 0.6 completeness, 0.7 confidence
        internal_mind.prepare_to_share(sample_thought_2)  # 0.7 completeness, 0.8 confidence
        internal_mind.prepare_to_share(sample_thought_3)  # 0.85 completeness, 0.9 confidence
        
        best = internal_mind.get_best_contribution()
        
        # Should select thought_3 with highest completeness/confidence
        assert best == sample_thought_3

    def test_get_best_contribution_filters_irrelevant(self, internal_mind, sample_thought, sample_thought_2):
        """Test that get_best_contribution filters out irrelevant thoughts."""
        internal_mind.prepare_to_share(sample_thought)
        internal_mind.prepare_to_share(sample_thought_2)
        
        # Mark one as irrelevant
        sample_thought_2.still_relevant = False
        
        best = internal_mind.get_best_contribution()
        assert best == sample_thought

    def test_get_best_contribution_empty(self, internal_mind):
        """Test get_best_contribution with no ready thoughts."""
        best = internal_mind.get_best_contribution()
        assert best is None

    def test_mark_externalized(self, internal_mind, sample_thought):
        """Test marking a thought as externalized."""
        internal_mind.add_thought(sample_thought)
        internal_mind.prepare_to_share(sample_thought)
        
        internal_mind.mark_externalized(sample_thought.thought_id)
        
        assert sample_thought.externalized is True
        assert sample_thought.externalized_at is not None
        assert sample_thought not in internal_mind.ready_to_share

    def test_invalidate_thoughts_about(self, internal_mind, sample_thought, sample_thought_2):
        """Test invalidating thoughts about a topic."""
        internal_mind.add_thought(sample_thought)
        internal_mind.add_thought(sample_thought_2)
        internal_mind.prepare_to_share(sample_thought)
        internal_mind.prepare_to_share(sample_thought_2)
        
        count = internal_mind.invalidate_thoughts_about("microservices")
        
        # Both thoughts should be invalidated
        assert sample_thought.still_relevant is False
        assert sample_thought_2.still_relevant is False
        assert count >= 2  # May include duplicates from ready_to_share

    def test_get_thoughts_for_context(self, internal_mind, sample_thought, sample_thought_2, sample_thought_3):
        """Test getting recent thoughts for context."""
        internal_mind.add_thought(sample_thought)
        internal_mind.add_thought(sample_thought_2)
        internal_mind.add_thought(sample_thought_3)
        
        recent = internal_mind.get_thoughts_for_context(n=2)
        
        assert len(recent) == 2
        # Should be most recent first
        assert recent[0].created_at >= recent[1].created_at

    def test_get_stream_for_topic(self, internal_mind, sample_thought):
        """Test finding a stream by topic."""
        internal_mind.add_thought(sample_thought)
        
        stream = internal_mind.get_stream_for_topic("microservices")
        assert stream is not None
        
        # Should not find unrelated topic
        no_stream = internal_mind.get_stream_for_topic("frontend")
        assert no_stream is None

    def test_get_streams_needing_synthesis(self, internal_mind):
        """Test getting streams that need synthesis."""
        # Add enough thoughts to trigger synthesis
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
        
        needs_synthesis = internal_mind.get_streams_needing_synthesis()
        assert len(needs_synthesis) == 1
        assert needs_synthesis[0].status == StreamStatus.NEEDS_SYNTHESIS

    def test_get_state(self, internal_mind, sample_thought, sample_thought_2):
        """Test getting mind state."""
        internal_mind.add_thought(sample_thought)
        internal_mind.add_thought(sample_thought_2)
        internal_mind.hold_insight(sample_thought)
        
        state = internal_mind.get_state()
        
        assert state["agent_id"] == "test-agent-123"
        assert state["active_thoughts"] == 2
        assert state["streams"] >= 1
        assert state["held_insights"] == 1
        assert "stream_topics" in state

    def test_get_detailed_state(self, internal_mind, sample_thought):
        """Test getting detailed mind state."""
        internal_mind.add_thought(sample_thought)
        internal_mind.prepare_to_share(sample_thought)
        
        state = internal_mind.get_detailed_state()
        
        assert "streams_detail" in state
        assert "ready_thoughts" in state
        assert len(state["ready_thoughts"]) == 1

    def test_cleanup_old_thoughts(self, internal_mind):
        """Test cleaning up old thoughts."""
        # Add old thought
        old_thought = Thought(
            thought_id=uuid4(),
            created_at=datetime.now(timezone.utc) - timedelta(minutes=60),
            tier=CognitiveTier.REACTIVE,
            content="Old thought",
            thought_type=ThoughtType.OBSERVATION,
            trigger="test",
        )
        
        # Add recent thought
        recent_thought = Thought(
            thought_id=uuid4(),
            created_at=datetime.now(timezone.utc),
            tier=CognitiveTier.REACTIVE,
            content="Recent thought",
            thought_type=ThoughtType.OBSERVATION,
            trigger="test",
        )
        
        internal_mind.add_thought(old_thought)
        internal_mind.add_thought(recent_thought)
        
        assert len(internal_mind.active_thoughts) == 2
        
        # Cleanup with 30 minute threshold
        cleaned = internal_mind.cleanup_old_thoughts(max_age_minutes=30)
        
        assert cleaned == 1
        assert str(old_thought.thought_id) not in internal_mind.active_thoughts
        assert str(recent_thought.thought_id) in internal_mind.active_thoughts

    def test_cleanup_preserves_externalized(self, internal_mind):
        """Test that cleanup preserves externalized thoughts even if old."""
        old_externalized = Thought(
            thought_id=uuid4(),
            created_at=datetime.now(timezone.utc) - timedelta(minutes=60),
            tier=CognitiveTier.REACTIVE,
            content="Old externalized thought",
            thought_type=ThoughtType.OBSERVATION,
            trigger="test",
            externalized=True,
        )
        
        internal_mind.add_thought(old_externalized)
        cleaned = internal_mind.cleanup_old_thoughts(max_age_minutes=30)
        
        # Should not clean up externalized thought
        assert cleaned == 0
        assert str(old_externalized.thought_id) in internal_mind.active_thoughts

    def test_clear(self, internal_mind, sample_thought, sample_thought_2):
        """Test clearing the mind."""
        internal_mind.add_thought(sample_thought)
        internal_mind.add_thought(sample_thought_2)
        internal_mind.hold_insight(sample_thought)
        internal_mind.prepare_to_share(sample_thought_2)
        
        internal_mind.clear()
        
        assert len(internal_mind.active_thoughts) == 0
        assert len(internal_mind.streams) == 0
        assert len(internal_mind.held_insights) == 0
        assert len(internal_mind.ready_to_share) == 0


# ==========================================
# Synthesis Trigger Tests
# ==========================================


class TestSynthesisTrigger:
    """Tests for synthesis trigger conditions."""

    def test_synthesis_triggers_at_3_thoughts(self, internal_mind):
        """Test that synthesis triggers at 3+ thoughts."""
        # Add 2 thoughts - should not trigger
        for i in range(2):
            thought = Thought(
                thought_id=uuid4(),
                created_at=datetime.now(timezone.utc),
                tier=CognitiveTier.REACTIVE,
                content=f"Microservices thought {i}",
                thought_type=ThoughtType.OBSERVATION,
                trigger="test",
            )
            stream = internal_mind.add_thought(thought)
        
        assert stream.status == StreamStatus.ACTIVE
        
        # Add 3rd thought - should trigger
        thought3 = Thought(
            thought_id=uuid4(),
            created_at=datetime.now(timezone.utc),
            tier=CognitiveTier.REACTIVE,
            content="Microservices thought 3",
            thought_type=ThoughtType.OBSERVATION,
            trigger="test",
        )
        stream = internal_mind.add_thought(thought3)
        
        assert stream.status == StreamStatus.NEEDS_SYNTHESIS

    def test_synthesis_triggers_with_time_and_confidence(self, internal_mind):
        """Test that synthesis triggers at 2 thoughts with time span and confidence."""
        # Add 2 thoughts with time span and high confidence
        thought1 = Thought(
            thought_id=uuid4(),
            created_at=datetime.now(timezone.utc) - timedelta(seconds=45),
            tier=CognitiveTier.REACTIVE,
            content="Microservices thought 1",
            thought_type=ThoughtType.OBSERVATION,
            trigger="test",
            confidence=0.8,
        )
        thought2 = Thought(
            thought_id=uuid4(),
            created_at=datetime.now(timezone.utc),
            tier=CognitiveTier.REACTIVE,
            content="Microservices thought 2",
            thought_type=ThoughtType.OBSERVATION,
            trigger="test",
            confidence=0.7,
        )
        
        internal_mind.add_thought(thought1)
        stream = internal_mind.add_thought(thought2)
        
        # Should trigger due to time span > 30s and avg confidence > 0.6
        assert stream.status == StreamStatus.NEEDS_SYNTHESIS

    def test_no_synthesis_low_confidence(self, internal_mind):
        """Test that synthesis doesn't trigger with low confidence."""
        thought1 = Thought(
            thought_id=uuid4(),
            created_at=datetime.now(timezone.utc) - timedelta(seconds=45),
            tier=CognitiveTier.REACTIVE,
            content="Microservices thought 1",
            thought_type=ThoughtType.OBSERVATION,
            trigger="test",
            confidence=0.4,  # Low confidence
        )
        thought2 = Thought(
            thought_id=uuid4(),
            created_at=datetime.now(timezone.utc),
            tier=CognitiveTier.REACTIVE,
            content="Microservices thought 2",
            thought_type=ThoughtType.OBSERVATION,
            trigger="test",
            confidence=0.5,  # Low confidence
        )
        
        internal_mind.add_thought(thought1)
        stream = internal_mind.add_thought(thought2)
        
        # Average confidence 0.45 < 0.6, should not trigger
        assert stream.status == StreamStatus.ACTIVE

