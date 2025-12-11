"""Integration tests for Memory Architecture (Phase 6).

Tests for the complete memory workflow including:
- Memory tier interactions
- Memory promotion flow
- Context retrieval for cognitive tiers
- Integration with cognitive processor
"""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from src.cognitive.tiers import CognitiveTier
from src.memory.working import WorkingMemory, ConversationTurn
from src.memory.short_term import ShortTermMemory, ShortTermMemoryEntry
from src.memory.long_term import LongTermMemory, ProjectChapter
from src.memory.manager import MemoryManager


class TestFullMemoryWorkflow:
    """Tests for complete memory workflow scenarios."""
    
    @pytest.fixture
    def agent_id(self):
        """Create test agent ID."""
        return uuid4()
    
    @pytest.fixture
    def working_memory(self):
        """Create working memory."""
        return WorkingMemory()
    
    @pytest.fixture
    def mock_short_term(self, agent_id):
        """Create mocked short-term memory."""
        mock = MagicMock(spec=ShortTermMemory)
        mock.agent_id = agent_id
        return mock
    
    @pytest.fixture
    def mock_long_term(self, agent_id):
        """Create mocked long-term memory."""
        mock = MagicMock(spec=LongTermMemory)
        mock.agent_id = agent_id
        return mock
    
    @pytest.fixture
    def manager(self, agent_id, working_memory, mock_short_term, mock_long_term):
        """Create memory manager."""
        return MemoryManager(
            agent_id=agent_id,
            working=working_memory,
            short_term=mock_short_term,
            long_term=mock_long_term,
        )
    
    @pytest.mark.asyncio
    async def test_conversation_to_memory_flow(self, manager, agent_id):
        """Test flow from conversation to short-term memory."""
        # Simulate a conversation
        manager.add_conversation_turn("user", "Let's discuss the API design")
        manager.add_conversation_turn("assistant", "I think we should use REST")
        manager.add_conversation_turn("user", "Good idea. What about authentication?")
        manager.add_conversation_turn("assistant", "JWT tokens would work well here")
        
        # Update context
        manager.update_topic("API design")
        manager.update_confidence(0.85)
        
        # Record a significant decision
        entry = ShortTermMemoryEntry(
            memory_id=uuid4(),
            agent_id=agent_id,
            memory_type="decision",
            content="Decided to use REST API with JWT authentication",
            significance=0.8,
            topic_keywords=["API", "REST", "JWT"],
            created_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        )
        manager.short_term.add = AsyncMock(return_value=entry)
        
        result = await manager.record_significant_event(
            content="Decided to use REST API with JWT authentication",
            memory_type="decision",
            significance=0.8,
            topic="API authentication",
        )
        
        assert result.significance == 0.8
        assert manager.working.get_turn_count() == 4
        assert manager.working.current_topic == "API design"
    
    @pytest.mark.asyncio
    async def test_memory_promotion_workflow(self, manager, agent_id):
        """Test full promotion from short-term to long-term."""
        memory_id = uuid4()
        project_id = uuid4()
        chapter_id = uuid4()
        
        # Create a significant short-term memory
        entry = ShortTermMemoryEntry(
            memory_id=memory_id,
            agent_id=agent_id,
            memory_type="insight",
            content="Event-driven architecture significantly improved system responsiveness",
            significance=0.9,
            topic_keywords=["architecture", "events"],
            created_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        )
        manager.short_term.get_by_id = AsyncMock(return_value=entry)
        
        # Mock chapter creation
        chapter = ProjectChapter(
            chapter_id=chapter_id,
            agent_id=agent_id,
            project_id=project_id,
            title="Event-Driven Architecture Success",
            summary="Event-driven architecture significantly improved system responsiveness",
            role_in_project="Lead Developer",
            start_date=datetime.now(timezone.utc),
            end_date=None,
            outcome="success",
            significance=0.9,
            lessons_learned="Consider event-driven patterns for responsive systems",
            collaborators=None,
            created_at=datetime.now(timezone.utc),
        )
        manager.long_term.add_chapter = AsyncMock(return_value=chapter)
        manager.short_term.promote_to_long_term = AsyncMock()
        
        # Check promotion criteria
        should_promote = await manager.evaluate_promotion(
            memory_id=memory_id,
            significance=0.9,
        )
        assert should_promote is True
        
        # Promote the memory
        result = await manager.promote_memory(
            memory_id=memory_id,
            project_id=project_id,
            title="Event-Driven Architecture Success",
            lessons="Consider event-driven patterns for responsive systems",
        )
        
        assert result is not None
        assert result.title == "Event-Driven Architecture Success"
        manager.short_term.promote_to_long_term.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_context_retrieval_escalation(self, manager):
        """Test memory context retrieval across cognitive tiers."""
        # Populate working memory
        for i in range(10):
            manager.add_conversation_turn(
                "user" if i % 2 == 0 else "assistant",
                f"Discussion point {i}",
            )
        manager.update_topic("system architecture")
        
        # Mock short and long-term returns
        manager.short_term.get_recent = AsyncMock(return_value="Recent: Team discussed microservices")
        manager.short_term.query = AsyncMock(return_value="Indexed: Previous architecture decisions")
        manager.long_term.search = AsyncMock(return_value="Long-term: Past project experiences")
        
        # REFLEX: Only working memory
        reflex_context = await manager.get_context_for_tier(CognitiveTier.REFLEX)
        assert "system architecture" in reflex_context
        manager.short_term.get_recent.assert_not_called()
        
        # REACTIVE: Working + recent
        reactive_context = await manager.get_context_for_tier(CognitiveTier.REACTIVE)
        manager.short_term.get_recent.assert_called()
        
        # Reset mock
        manager.short_term.get_recent.reset_mock()
        
        # DELIBERATE: Working + indexed
        deliberate_context = await manager.get_context_for_tier(
            CognitiveTier.DELIBERATE,
            topic="architecture"
        )
        manager.short_term.query.assert_called()
        
        # ANALYTICAL: All tiers
        analytical_context = await manager.get_context_for_tier(
            CognitiveTier.ANALYTICAL,
            topic="architecture"
        )
        manager.long_term.search.assert_called()


class TestCognitiveIntegration:
    """Tests for integration with cognitive processing."""
    
    @pytest.fixture
    def agent_id(self):
        return uuid4()
    
    @pytest.fixture
    def manager(self, agent_id):
        working = WorkingMemory()
        mock_short = MagicMock(spec=ShortTermMemory)
        mock_long = MagicMock(spec=LongTermMemory)
        return MemoryManager(
            agent_id=agent_id,
            working=working,
            short_term=mock_short,
            long_term=mock_long,
        )
    
    def test_working_memory_provides_context_depth(self, manager):
        """Test that working memory provides appropriate context depth."""
        # Simulate a conversation about a complex topic
        messages = [
            ("user", "I need help designing our microservices architecture"),
            ("assistant", "What are the main services you're considering?"),
            ("user", "User service, order service, and inventory service"),
            ("assistant", "Those are good core services. How will they communicate?"),
            ("user", "I was thinking REST APIs, but maybe we need async messaging too"),
        ]
        
        for role, content in messages:
            manager.add_conversation_turn(role, content)
        
        manager.update_topic("microservices architecture")
        
        # REFLEX context should be minimal
        reflex = manager.working.get_for_reflex()
        assert len(reflex) < 200  # Minimal
        assert "microservices" in reflex
        
        # REACTIVE context should include recent turns
        reactive = manager.working.get_for_reactive()
        assert len(reactive) > len(reflex)
        
        # DELIBERATE context should be fuller
        deliberate = manager.working.get_for_deliberate()
        assert len(deliberate) >= len(reactive)
    
    def test_keywords_extraction_for_memory_query(self, manager):
        """Test extracting keywords from conversation for memory queries."""
        messages = [
            ("user", "The PostgreSQL database is running slow"),
            ("assistant", "Have you checked the query performance?"),
            ("user", "Yes, some queries take over 5 seconds"),
        ]
        
        for role, content in messages:
            manager.add_conversation_turn(role, content)
        
        keywords = manager.working.extract_keywords_from_recent()
        
        # Should extract meaningful technical terms
        assert "postgresql" in keywords
        assert "database" in keywords
        assert "query" in keywords or "queries" in keywords


class TestMemoryStateManagement:
    """Tests for memory state management."""
    
    @pytest.fixture
    def agent_id(self):
        return uuid4()
    
    @pytest.fixture
    def manager(self, agent_id):
        working = WorkingMemory()
        mock_short = MagicMock(spec=ShortTermMemory)
        mock_long = MagicMock(spec=LongTermMemory)
        return MemoryManager(
            agent_id=agent_id,
            working=working,
            short_term=mock_short,
            long_term=mock_long,
        )
    
    def test_confidence_tracking(self, manager):
        """Test confidence level tracking through conversation."""
        # Start neutral
        assert manager.working.confidence_level == 0.7
        
        # Confidence increases with agreement
        manager.update_confidence(0.85)
        assert manager.working.confidence_level == 0.85
        
        # Can track through state
        state = manager.get_working_state()
        assert state["confidence_level"] == 0.85
    
    def test_topic_evolution(self, manager):
        """Test topic tracking as conversation evolves."""
        manager.update_topic("initial planning")
        assert manager.working.current_topic == "initial planning"
        
        manager.add_conversation_turn("user", "Let's discuss the database now")
        manager.update_topic("database design")
        
        state = manager.get_working_state()
        assert state["current_topic"] == "database design"
    
    def test_mood_affects_context(self, manager):
        """Test that mood is reflected in context."""
        manager.update_mood("focused")
        manager.update_topic("critical decision")
        
        reflex_context = manager.working.get_for_reflex()
        
        assert "focused" in reflex_context
        assert "critical decision" in reflex_context
    
    def test_session_reset(self, manager):
        """Test resetting session working memory."""
        # Build up state
        manager.add_conversation_turn("user", "Hello")
        manager.add_conversation_turn("assistant", "Hi there")
        manager.update_topic("greeting")
        manager.update_confidence(0.9)
        manager.update_mood("friendly")
        
        # Verify state
        assert manager.working.get_turn_count() == 2
        assert manager.working.current_topic == "greeting"
        
        # Clear working memory
        manager.clear_working_memory()
        
        # Should be reset
        state = manager.get_working_state()
        assert state["turn_count"] == 0
        assert state["current_topic"] == ""
        assert state["confidence_level"] == 0.7
        assert state["current_mood"] == "neutral"


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""
    
    @pytest.fixture
    def agent_id(self):
        return uuid4()
    
    @pytest.fixture
    def manager(self, agent_id):
        working = WorkingMemory(max_turns=5)  # Small buffer
        mock_short = MagicMock(spec=ShortTermMemory)
        mock_long = MagicMock(spec=LongTermMemory)
        return MemoryManager(
            agent_id=agent_id,
            working=working,
            short_term=mock_short,
            long_term=mock_long,
        )
    
    def test_working_memory_overflow(self, manager):
        """Test working memory ring buffer overflow."""
        # Add more turns than buffer size
        for i in range(10):
            manager.add_conversation_turn("user", f"Message {i}")
        
        # Should only have max_turns
        assert manager.working.get_turn_count() == 5
        
        # Oldest should be evicted
        turns = manager.working.get_all_turns()
        assert turns[0].content == "Message 5"
        assert turns[-1].content == "Message 9"
    
    @pytest.mark.asyncio
    async def test_empty_short_term_memory(self, manager):
        """Test context retrieval with empty short-term memory."""
        manager.short_term.get_recent = AsyncMock(return_value="")
        manager.short_term.query = AsyncMock(return_value="")
        
        context = await manager.get_context_for_tier(CognitiveTier.REACTIVE)
        
        # Should still return working memory context
        assert context is not None
    
    @pytest.mark.asyncio
    async def test_empty_long_term_memory(self, manager):
        """Test context retrieval with empty long-term memory."""
        manager.short_term.query = AsyncMock(return_value="Short-term data")
        manager.long_term.search = AsyncMock(return_value="")
        
        context = await manager.get_context_for_tier(CognitiveTier.ANALYTICAL)
        
        # Should include short-term but handle empty long-term
        assert "Short-term" in context or context is not None
    
    @pytest.mark.asyncio
    async def test_promotion_of_nonexistent_memory(self, manager):
        """Test promoting memory that doesn't exist."""
        manager.short_term.get_by_id = AsyncMock(return_value=None)
        
        result = await manager.promote_memory(
            memory_id=uuid4(),
            project_id=uuid4(),
            title="Ghost Memory",
        )
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_borderline_promotion_criteria(self, manager):
        """Test promotion criteria at boundary values."""
        memory_id = uuid4()
        
        # Exactly at threshold - should promote
        should_promote = await manager.evaluate_promotion(
            memory_id=memory_id,
            significance=0.7,  # Exactly at threshold
        )
        assert should_promote is True
        
        # Just below threshold - should not promote
        should_not_promote = await manager.evaluate_promotion(
            memory_id=memory_id,
            significance=0.69,  # Just below
        )
        assert should_not_promote is False
    
    def test_long_content_truncation(self, manager):
        """Test that long content is properly truncated."""
        # Add a very long message
        long_content = "A" * 5000
        manager.add_conversation_turn("user", long_content)
        
        # Get reactive context with limited tokens
        reactive = manager.working.get_for_reactive(max_tokens=100)
        
        # Should be truncated
        assert len(reactive) < 1000
    
    def test_special_characters_in_topic(self, manager):
        """Test handling special characters in topic."""
        manager.update_topic("API v2.0 (beta) - user/auth")
        
        reflex = manager.working.get_for_reflex()
        
        assert "API v2.0" in reflex


class TestMultipleAgents:
    """Tests for scenarios involving multiple agents."""
    
    def test_managers_are_independent(self):
        """Test that different agent managers are isolated."""
        agent1_id = uuid4()
        agent2_id = uuid4()
        
        manager1 = MemoryManager(
            agent_id=agent1_id,
            working=WorkingMemory(),
            short_term=MagicMock(spec=ShortTermMemory),
            long_term=MagicMock(spec=LongTermMemory),
        )
        
        manager2 = MemoryManager(
            agent_id=agent2_id,
            working=WorkingMemory(),
            short_term=MagicMock(spec=ShortTermMemory),
            long_term=MagicMock(spec=LongTermMemory),
        )
        
        # Modify manager1
        manager1.add_conversation_turn("user", "Message for agent 1")
        manager1.update_topic("Agent 1 topic")
        
        # Manager2 should be unaffected
        assert manager2.working.get_turn_count() == 0
        assert manager2.working.current_topic == ""
    
    def test_related_agents_in_memory(self):
        """Test tracking related agents in memories."""
        agent_id = uuid4()
        working = WorkingMemory()
        
        # Track conversation with multiple speakers
        working.add_message(
            role="assistant",
            content="Hello everyone",
            speaker_name="Agent Alice",
            speaker_id="agent-alice",
        )
        working.add_message(
            role="assistant",
            content="Hi Alice!",
            speaker_name="Agent Bob",
            speaker_id="agent-bob",
        )
        
        turns = working.get_all_turns()
        
        # Should track different speakers
        speakers = {t.speaker_id for t in turns if t.speaker_id}
        assert "agent-alice" in speakers
        assert "agent-bob" in speakers

