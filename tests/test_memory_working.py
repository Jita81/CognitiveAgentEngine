"""Tests for Working Memory (Tier 1).

Tests for in-process conversation buffer and cache.
"""

import pytest
from datetime import datetime, timedelta, timezone

from src.memory.working import WorkingMemory, ConversationTurn


class TestConversationTurn:
    """Tests for ConversationTurn dataclass."""
    
    def test_create_turn(self):
        """Test creating a conversation turn."""
        turn = ConversationTurn(
            role="user",
            content="Hello, how are you?",
        )
        
        assert turn.role == "user"
        assert turn.content == "Hello, how are you?"
        assert turn.timestamp is not None
        assert turn.speaker_name is None
    
    def test_create_turn_with_speaker(self):
        """Test creating turn with speaker info."""
        turn = ConversationTurn(
            role="assistant",
            content="I'm doing well!",
            speaker_name="Alice",
            speaker_id="agent-1",
        )
        
        assert turn.speaker_name == "Alice"
        assert turn.speaker_id == "agent-1"
    
    def test_to_dict(self):
        """Test converting turn to dictionary."""
        turn = ConversationTurn(
            role="user",
            content="Test message",
            speaker_name="Bob",
        )
        
        d = turn.to_dict()
        
        assert d["role"] == "user"
        assert d["content"] == "Test message"
        assert d["speaker_name"] == "Bob"
        assert "timestamp" in d
    
    def test_format_for_prompt(self):
        """Test formatting turn for prompt."""
        turn = ConversationTurn(
            role="user",
            content="This is a test message",
            speaker_name="Bob",
        )
        
        formatted = turn.format_for_prompt()
        
        assert "Bob:" in formatted
        assert "This is a test message" in formatted
    
    def test_format_for_prompt_truncation(self):
        """Test that long content is truncated."""
        turn = ConversationTurn(
            role="user",
            content="A" * 500,  # Long content
        )
        
        formatted = turn.format_for_prompt(max_content_length=100)
        
        assert len(formatted) < 200  # Should be truncated
        assert "..." in formatted


class TestWorkingMemory:
    """Tests for WorkingMemory class."""
    
    def test_create_working_memory(self):
        """Test creating working memory."""
        wm = WorkingMemory(max_turns=10)
        
        assert wm.max_turns == 10
        assert wm.current_topic == ""
        assert wm.current_mood == "neutral"
        assert wm.confidence_level == 0.7
    
    def test_add_turn(self):
        """Test adding a conversation turn."""
        wm = WorkingMemory()
        
        turn = ConversationTurn(role="user", content="Hello")
        wm.add_turn(turn)
        
        assert wm.get_turn_count() == 1
        assert wm.get_all_turns()[0].content == "Hello"
    
    def test_add_message(self):
        """Test convenience method for adding messages."""
        wm = WorkingMemory()
        
        turn = wm.add_message(
            role="assistant",
            content="Hi there!",
            speaker_name="Agent",
        )
        
        assert wm.get_turn_count() == 1
        assert turn.speaker_name == "Agent"
    
    def test_ring_buffer_overflow(self):
        """Test that oldest turns are evicted at capacity."""
        wm = WorkingMemory(max_turns=5)
        
        # Add 7 turns
        for i in range(7):
            wm.add_message(role="user", content=f"Message {i}")
        
        # Should only have 5 turns
        assert wm.get_turn_count() == 5
        
        # Should have messages 2-6 (0 and 1 evicted)
        turns = wm.get_all_turns()
        assert turns[0].content == "Message 2"
        assert turns[-1].content == "Message 6"
    
    def test_get_recent_turns(self):
        """Test getting recent turns."""
        wm = WorkingMemory()
        
        for i in range(10):
            wm.add_message(role="user", content=f"Message {i}")
        
        recent = wm.get_recent_turns(3)
        
        assert len(recent) == 3
        assert recent[0].content == "Message 7"
        assert recent[-1].content == "Message 9"
    
    def test_get_for_reflex(self):
        """Test minimal context for REFLEX tier."""
        wm = WorkingMemory()
        wm.set_topic("API design")
        wm.set_mood("focused")
        
        context = wm.get_for_reflex()
        
        assert "API design" in context
        assert "focused" in context
    
    def test_get_for_reactive(self):
        """Test recent context for REACTIVE tier."""
        wm = WorkingMemory()
        
        for i in range(10):
            wm.add_message(
                role="user" if i % 2 == 0 else "assistant",
                content=f"Message {i}",
                speaker_name=f"Speaker {i}",
            )
        
        context = wm.get_for_reactive()
        
        # Should include recent messages
        assert "Message 9" in context or "Speaker 9" in context
    
    def test_get_for_deliberate(self):
        """Test fuller context for DELIBERATE tier."""
        wm = WorkingMemory()
        wm.set_topic("architecture")
        wm.set_confidence(0.8)
        
        for i in range(5):
            wm.add_message(role="user", content=f"Design point {i}")
        
        context = wm.get_for_deliberate()
        
        # Should include conversation and state
        assert "architecture" in context
        assert "0.8" in context
    
    def test_set_topic(self):
        """Test setting current topic."""
        wm = WorkingMemory()
        
        wm.set_topic("database design")
        
        assert wm.current_topic == "database design"
    
    def test_set_mood(self):
        """Test setting current mood."""
        wm = WorkingMemory()
        
        wm.set_mood("curious")
        
        assert wm.current_mood == "curious"
    
    def test_set_confidence(self):
        """Test setting confidence level."""
        wm = WorkingMemory()
        
        wm.set_confidence(0.9)
        assert wm.confidence_level == 0.9
        
        # Should clamp to valid range
        wm.set_confidence(1.5)
        assert wm.confidence_level == 1.0
        
        wm.set_confidence(-0.5)
        assert wm.confidence_level == 0.0
    
    def test_cache_set_and_get(self):
        """Test caching values."""
        wm = WorkingMemory()
        
        wm.set_cached("key1", "value1", ttl_seconds=60)
        
        result = wm.get_cached("key1")
        assert result == "value1"
    
    def test_cache_expiry(self):
        """Test that cache expires."""
        wm = WorkingMemory()
        
        # Set with 0 second TTL (immediate expiry)
        wm.set_cached("key1", "value1", ttl_seconds=0)
        
        # Manually set expiry in the past
        wm._cache_ttl["key1"] = datetime.now(timezone.utc) - timedelta(seconds=1)
        
        result = wm.get_cached("key1")
        assert result is None
    
    def test_cache_invalidation_on_turn(self):
        """Test that cache is invalidated on new turn."""
        wm = WorkingMemory()
        
        wm.set_cached("key1", "value1")
        assert wm.get_cached("key1") == "value1"
        
        wm.add_message(role="user", content="New message")
        
        assert wm.get_cached("key1") is None
    
    def test_clear(self):
        """Test clearing working memory."""
        wm = WorkingMemory()
        
        wm.add_message(role="user", content="Test")
        wm.set_topic("topic")
        wm.set_mood("happy")
        wm.set_confidence(0.9)
        wm.set_cached("key", "value")
        
        wm.clear()
        
        assert wm.get_turn_count() == 0
        assert wm.current_topic == ""
        assert wm.current_mood == "neutral"
        assert wm.confidence_level == 0.7
        assert wm.get_cached("key") is None
    
    def test_get_state(self):
        """Test getting working memory state."""
        wm = WorkingMemory(max_turns=15)
        wm.set_topic("testing")
        
        for i in range(5):
            wm.add_message(role="user", content=f"Msg {i}")
        
        state = wm.get_state()
        
        assert state["turn_count"] == 5
        assert state["max_turns"] == 15
        assert state["current_topic"] == "testing"
    
    def test_to_dict(self):
        """Test converting to full dictionary."""
        wm = WorkingMemory()
        wm.add_message(role="user", content="Hello")
        wm.set_topic("greeting")
        
        d = wm.to_dict()
        
        assert len(d["turns"]) == 1
        assert d["current_topic"] == "greeting"
        assert "max_turns" in d
    
    def test_extract_keywords_from_recent(self):
        """Test extracting keywords from recent turns."""
        wm = WorkingMemory()
        
        wm.add_message(role="user", content="We need to discuss the database schema design")
        wm.add_message(role="assistant", content="I think PostgreSQL would be a good choice")
        
        keywords = wm.extract_keywords_from_recent()
        
        # Should extract meaningful words
        assert "database" in keywords
        assert "postgresql" in keywords
        
        # Should not include stop words
        assert "the" not in keywords
        assert "to" not in keywords

