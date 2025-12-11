"""Tests for Memory Manager.

Tests for the MemoryManager class that orchestrates all memory tiers
with tier-appropriate access.

Note: These tests use mocked database operations since they focus
on the manager's logic, not database integration.
"""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from src.cognitive.tiers import CognitiveTier
from src.memory.working import WorkingMemory
from src.memory.short_term import ShortTermMemory, ShortTermMemoryEntry
from src.memory.long_term import LongTermMemory, ProjectChapter
from src.memory.manager import MemoryManager


@pytest.fixture
def agent_id():
    """Create test agent ID."""
    return uuid4()


@pytest.fixture
def working_memory():
    """Create working memory instance."""
    return WorkingMemory()


@pytest.fixture
def mock_short_term(agent_id):
    """Create mocked short-term memory."""
    mock = MagicMock(spec=ShortTermMemory)
    mock.agent_id = agent_id
    return mock


@pytest.fixture
def mock_long_term(agent_id):
    """Create mocked long-term memory."""
    mock = MagicMock(spec=LongTermMemory)
    mock.agent_id = agent_id
    return mock


@pytest.fixture
def memory_manager(agent_id, working_memory, mock_short_term, mock_long_term):
    """Create memory manager with mocked dependencies."""
    return MemoryManager(
        agent_id=agent_id,
        working=working_memory,
        short_term=mock_short_term,
        long_term=mock_long_term,
    )


class TestMemoryManagerBasics:
    """Tests for basic MemoryManager functionality."""
    
    def test_create_manager(self, memory_manager, agent_id):
        """Test creating memory manager."""
        assert memory_manager.agent_id == agent_id
        assert memory_manager.working is not None
        assert memory_manager.short_term is not None
        assert memory_manager.long_term is not None
    
    def test_add_conversation_turn(self, memory_manager):
        """Test adding conversation turn."""
        turn = memory_manager.add_conversation_turn(
            role="user",
            content="Hello, world!",
            speaker_name="Alice",
        )
        
        assert turn.role == "user"
        assert turn.content == "Hello, world!"
        assert memory_manager.working.get_turn_count() == 1
    
    def test_update_topic(self, memory_manager):
        """Test updating topic."""
        memory_manager.update_topic("API design")
        
        assert memory_manager.working.current_topic == "API design"
    
    def test_update_confidence(self, memory_manager):
        """Test updating confidence."""
        memory_manager.update_confidence(0.85)
        
        assert memory_manager.working.confidence_level == 0.85
    
    def test_update_mood(self, memory_manager):
        """Test updating mood."""
        memory_manager.update_mood("focused")
        
        assert memory_manager.working.current_mood == "focused"
    
    def test_get_working_state(self, memory_manager):
        """Test getting working memory state."""
        memory_manager.add_conversation_turn("user", "Test message")
        memory_manager.update_topic("testing")
        
        state = memory_manager.get_working_state()
        
        assert state["turn_count"] == 1
        assert state["current_topic"] == "testing"
    
    def test_clear_working_memory(self, memory_manager):
        """Test clearing working memory."""
        memory_manager.add_conversation_turn("user", "Test")
        memory_manager.update_topic("something")
        
        memory_manager.clear_working_memory()
        
        assert memory_manager.working.get_turn_count() == 0
        assert memory_manager.working.current_topic == ""


class TestTierAppropriateAccess:
    """Tests for tier-appropriate memory access."""
    
    @pytest.mark.asyncio
    async def test_reflex_tier_access(self, memory_manager):
        """Test REFLEX tier gets only working memory."""
        memory_manager.update_topic("quick question")
        memory_manager.update_mood("alert")
        
        context = await memory_manager.get_context_for_tier(CognitiveTier.REFLEX)
        
        # Should only include minimal working memory
        assert "quick question" in context
        assert "alert" in context
        
        # Short-term shouldn't be queried
        memory_manager.short_term.get_recent.assert_not_called()
        memory_manager.short_term.query.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_reactive_tier_access(self, memory_manager):
        """Test REACTIVE tier gets working + recent short-term."""
        memory_manager.add_conversation_turn("user", "Recent conversation")
        memory_manager.short_term.get_recent = AsyncMock(return_value="Recent memory")
        
        context = await memory_manager.get_context_for_tier(CognitiveTier.REACTIVE)
        
        # Should query recent short-term
        memory_manager.short_term.get_recent.assert_called_once()
        assert "Recent memory" in context or "Recent" in context
    
    @pytest.mark.asyncio
    async def test_deliberate_tier_access_with_topic(self, memory_manager):
        """Test DELIBERATE tier gets working + indexed short-term."""
        memory_manager.short_term.query = AsyncMock(return_value="Indexed memories")
        
        context = await memory_manager.get_context_for_tier(
            CognitiveTier.DELIBERATE,
            topic="architecture",
        )
        
        # Should query by topic
        memory_manager.short_term.query.assert_called_once()
        call_kwargs = memory_manager.short_term.query.call_args
        assert "architecture" in str(call_kwargs)
    
    @pytest.mark.asyncio
    async def test_deliberate_tier_access_no_topic(self, memory_manager):
        """Test DELIBERATE tier falls back to recent when no topic."""
        memory_manager.short_term.get_recent = AsyncMock(return_value="Recent items")
        
        context = await memory_manager.get_context_for_tier(
            CognitiveTier.DELIBERATE,
            topic=None,
        )
        
        # Should fall back to get_recent
        memory_manager.short_term.get_recent.assert_called()
    
    @pytest.mark.asyncio
    async def test_analytical_tier_access(self, memory_manager):
        """Test ANALYTICAL tier gets all memory tiers."""
        memory_manager.short_term.query = AsyncMock(return_value="Short-term data")
        memory_manager.long_term.search = AsyncMock(return_value="Long-term data")
        
        context = await memory_manager.get_context_for_tier(
            CognitiveTier.ANALYTICAL,
            topic="deep analysis",
        )
        
        # Should query all tiers
        memory_manager.short_term.query.assert_called_once()
        memory_manager.long_term.search.assert_called_once()
        
        assert "Short-term" in context or "Long-term" in context
    
    @pytest.mark.asyncio
    async def test_comprehensive_tier_access(self, memory_manager):
        """Test COMPREHENSIVE tier gets maximum context."""
        memory_manager.short_term.query = AsyncMock(return_value="Full short-term")
        memory_manager.long_term.search = AsyncMock(return_value="Full long-term")
        
        context = await memory_manager.get_context_for_tier(
            CognitiveTier.COMPREHENSIVE,
            topic="full exploration",
        )
        
        # Should query all tiers
        memory_manager.short_term.query.assert_called_once()
        memory_manager.long_term.search.assert_called_once()


class TestRecordSignificantEvent:
    """Tests for recording significant events."""
    
    @pytest.mark.asyncio
    async def test_record_event(self, memory_manager, agent_id):
        """Test recording a significant event."""
        entry = ShortTermMemoryEntry(
            memory_id=uuid4(),
            agent_id=agent_id,
            memory_type="decision",
            content="Decided to use PostgreSQL",
            significance=0.8,
            topic_keywords=["database", "postgresql"],
            created_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        )
        memory_manager.short_term.add = AsyncMock(return_value=entry)
        
        result = await memory_manager.record_significant_event(
            content="Decided to use PostgreSQL",
            memory_type="decision",
            significance=0.8,
            topic="database selection",
        )
        
        memory_manager.short_term.add.assert_called_once()
        assert result.content == "Decided to use PostgreSQL"
    
    @pytest.mark.asyncio
    async def test_record_event_with_project(self, memory_manager, agent_id):
        """Test recording event with project context."""
        project_id = uuid4()
        entry = ShortTermMemoryEntry(
            memory_id=uuid4(),
            agent_id=agent_id,
            memory_type="interaction",
            content="Collaboration with team",
            significance=0.6,
            topic_keywords=["team"],
            created_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
            project_id=project_id,
            related_agents=["agent-2", "agent-3"],
        )
        memory_manager.short_term.add = AsyncMock(return_value=entry)
        
        result = await memory_manager.record_significant_event(
            content="Collaboration with team",
            memory_type="interaction",
            significance=0.6,
            topic="team work",
            project_id=project_id,
            related_agents=["agent-2", "agent-3"],
        )
        
        call_kwargs = memory_manager.short_term.add.call_args
        assert str(project_id) in str(call_kwargs)


class TestMemoryPromotion:
    """Tests for memory promotion logic."""
    
    @pytest.mark.asyncio
    async def test_evaluate_promotion_high_significance(self, memory_manager):
        """Test promotion with high significance."""
        memory_id = uuid4()
        
        should_promote = await memory_manager.evaluate_promotion(
            memory_id=memory_id,
            significance=0.8,  # >= 0.7 threshold
        )
        
        assert should_promote is True
    
    @pytest.mark.asyncio
    async def test_evaluate_promotion_low_significance(self, memory_manager):
        """Test no promotion with low significance."""
        memory_id = uuid4()
        
        should_promote = await memory_manager.evaluate_promotion(
            memory_id=memory_id,
            significance=0.5,  # < 0.7 threshold
        )
        
        assert should_promote is False
    
    @pytest.mark.asyncio
    async def test_evaluate_promotion_relationship_delta(self, memory_manager):
        """Test promotion based on relationship change."""
        memory_id = uuid4()
        
        should_promote = await memory_manager.evaluate_promotion(
            memory_id=memory_id,
            significance=0.3,  # Low significance
            relationship_delta=2,  # High relationship change
        )
        
        assert should_promote is True
    
    @pytest.mark.asyncio
    async def test_promote_memory(self, memory_manager, agent_id):
        """Test promoting memory to long-term."""
        memory_id = uuid4()
        project_id = uuid4()
        chapter_id = uuid4()
        
        # Mock the short-term memory entry
        entry = ShortTermMemoryEntry(
            memory_id=memory_id,
            agent_id=agent_id,
            memory_type="decision",
            content="Important decision content",
            significance=0.9,
            topic_keywords=["important"],
            created_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        )
        memory_manager.short_term.get_by_id = AsyncMock(return_value=entry)
        
        # Mock the chapter creation
        chapter = ProjectChapter(
            chapter_id=chapter_id,
            agent_id=agent_id,
            project_id=project_id,
            title="Important Decision",
            summary="Important decision content",
            role_in_project=None,
            start_date=datetime.now(timezone.utc),
            end_date=None,
            outcome="ongoing",
            significance=0.9,
            lessons_learned=None,
            collaborators=None,
            created_at=datetime.now(timezone.utc),
        )
        memory_manager.long_term.add_chapter = AsyncMock(return_value=chapter)
        memory_manager.short_term.promote_to_long_term = AsyncMock()
        
        result = await memory_manager.promote_memory(
            memory_id=memory_id,
            project_id=project_id,
            title="Important Decision",
        )
        
        assert result is not None
        assert result.title == "Important Decision"
        memory_manager.short_term.promote_to_long_term.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_promote_memory_not_found(self, memory_manager):
        """Test promotion when memory not found."""
        memory_manager.short_term.get_by_id = AsyncMock(return_value=None)
        
        result = await memory_manager.promote_memory(
            memory_id=uuid4(),
            project_id=uuid4(),
            title="Missing Memory",
        )
        
        assert result is None


class TestCleanup:
    """Tests for memory cleanup."""
    
    @pytest.mark.asyncio
    async def test_cleanup_expired(self, memory_manager):
        """Test cleaning up expired memories."""
        memory_manager.short_term.delete_expired = AsyncMock(return_value=5)
        
        deleted = await memory_manager.cleanup_expired()
        
        assert deleted == 5
        memory_manager.short_term.delete_expired.assert_called_once()


class TestDataclassModels:
    """Tests for the dataclass models."""
    
    def test_short_term_memory_entry_to_dict(self):
        """Test ShortTermMemoryEntry to_dict."""
        agent_id = uuid4()
        entry = ShortTermMemoryEntry(
            memory_id=uuid4(),
            agent_id=agent_id,
            memory_type="observation",
            content="Test content",
            significance=0.5,
            topic_keywords=["test"],
            created_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        )
        
        d = entry.to_dict()
        
        assert d["memory_type"] == "observation"
        assert d["content"] == "Test content"
        assert d["significance"] == 0.5
    
    def test_short_term_memory_entry_is_expired(self):
        """Test ShortTermMemoryEntry is_expired check."""
        agent_id = uuid4()
        
        # Not expired
        entry = ShortTermMemoryEntry(
            memory_id=uuid4(),
            agent_id=agent_id,
            memory_type="test",
            content="Test",
            significance=0.5,
            topic_keywords=[],
            created_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + timedelta(days=1),
        )
        assert entry.is_expired() is False
        
        # Expired
        expired_entry = ShortTermMemoryEntry(
            memory_id=uuid4(),
            agent_id=agent_id,
            memory_type="test",
            content="Test",
            significance=0.5,
            topic_keywords=[],
            created_at=datetime.now(timezone.utc) - timedelta(days=10),
            expires_at=datetime.now(timezone.utc) - timedelta(days=1),
        )
        assert expired_entry.is_expired() is True
    
    def test_project_chapter_to_dict(self):
        """Test ProjectChapter to_dict."""
        agent_id = uuid4()
        project_id = uuid4()
        
        chapter = ProjectChapter(
            chapter_id=uuid4(),
            agent_id=agent_id,
            project_id=project_id,
            title="API Design",
            summary="Designed REST API for user service",
            role_in_project="Lead Developer",
            start_date=datetime.now(timezone.utc),
            end_date=None,
            outcome="success",
            significance=0.8,
            lessons_learned="Start with API design early",
            collaborators=["agent-2"],
            created_at=datetime.now(timezone.utc),
        )
        
        d = chapter.to_dict()
        
        assert d["title"] == "API Design"
        assert d["outcome"] == "success"
        assert d["significance"] == 0.8
    
    def test_project_chapter_is_ongoing(self):
        """Test ProjectChapter is_ongoing property."""
        agent_id = uuid4()
        project_id = uuid4()
        
        # Ongoing (no end date)
        ongoing = ProjectChapter(
            chapter_id=uuid4(),
            agent_id=agent_id,
            project_id=project_id,
            title="Current Project",
            summary="Working on it",
            role_in_project=None,
            start_date=datetime.now(timezone.utc),
            end_date=None,
            outcome="ongoing",
            significance=0.5,
            lessons_learned=None,
            collaborators=None,
            created_at=datetime.now(timezone.utc),
        )
        assert ongoing.is_ongoing is True
        
        # Completed
        completed = ProjectChapter(
            chapter_id=uuid4(),
            agent_id=agent_id,
            project_id=project_id,
            title="Done Project",
            summary="Finished",
            role_in_project=None,
            start_date=datetime.now(timezone.utc) - timedelta(days=30),
            end_date=datetime.now(timezone.utc),
            outcome="success",
            significance=0.8,
            lessons_learned=None,
            collaborators=None,
            created_at=datetime.now(timezone.utc),
        )
        assert completed.is_ongoing is False
    
    def test_project_chapter_was_successful(self):
        """Test ProjectChapter was_successful property."""
        agent_id = uuid4()
        project_id = uuid4()
        
        base_chapter = {
            "chapter_id": uuid4(),
            "agent_id": agent_id,
            "project_id": project_id,
            "title": "Test",
            "summary": "Test",
            "role_in_project": None,
            "start_date": datetime.now(timezone.utc),
            "end_date": None,
            "significance": 0.5,
            "lessons_learned": None,
            "collaborators": None,
            "created_at": datetime.now(timezone.utc),
        }
        
        success = ProjectChapter(**{**base_chapter, "outcome": "success"})
        assert success.was_successful is True
        
        partial = ProjectChapter(**{**base_chapter, "outcome": "partial_success"})
        assert partial.was_successful is True
        
        failure = ProjectChapter(**{**base_chapter, "outcome": "failure"})
        assert failure.was_successful is False

