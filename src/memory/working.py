"""Working Memory - Tier 1 of the memory architecture.

Active cognitive workspace for in-process, session-only memory.
This is the fastest memory tier with minimal latency.

Phase 6 of the Cognitive Agent Engine.
"""

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional


@dataclass
class ConversationTurn:
    """A single turn in conversation.
    
    Attributes:
        role: The role of the speaker (user, assistant, system)
        content: The actual message content
        timestamp: When this turn occurred
        speaker_name: Optional display name of the speaker
        speaker_id: Optional ID of the speaker (agent or user)
    """
    
    role: str  # user, assistant, system
    content: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    speaker_name: Optional[str] = None
    speaker_id: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "speaker_name": self.speaker_name,
            "speaker_id": self.speaker_id,
        }
    
    def format_for_prompt(self, max_content_length: int = 200) -> str:
        """Format turn for inclusion in prompts.
        
        Args:
            max_content_length: Maximum characters to include from content
            
        Returns:
            Formatted string representation
        """
        name = self.speaker_name or self.role
        content = self.content[:max_content_length]
        if len(self.content) > max_content_length:
            content += "..."
        return f"{name}: {content}"


class WorkingMemory:
    """Tier 1: Active cognitive workspace.
    
    In-process, session-only, fastest access. Used for:
    - Current conversation context
    - Active thoughts and thought streams
    - Immediate emotional/confidence state
    
    Attributes:
        max_turns: Maximum conversation turns to retain
        conversation: Ring buffer of conversation turns
        current_topic: Currently discussed topic
        current_mood: Agent's current mood state
        confidence_level: Current confidence level (0.0-1.0)
    """
    
    DEFAULT_MAX_TURNS = 20
    DEFAULT_CACHE_TTL_SECONDS = 60
    
    def __init__(self, max_turns: int = DEFAULT_MAX_TURNS):
        """Initialize working memory.
        
        Args:
            max_turns: Maximum conversation turns to retain
        """
        self.max_turns = max_turns
        self.conversation: deque[ConversationTurn] = deque(maxlen=max_turns)
        
        # Current state
        self.current_topic: str = ""
        self.current_mood: str = "neutral"
        self.confidence_level: float = 0.7
        
        # Quick-access cache for repeated queries
        self._cache: Dict[str, str] = {}
        self._cache_ttl: Dict[str, datetime] = {}
    
    def add_turn(self, turn: ConversationTurn) -> None:
        """Add a conversation turn.
        
        Args:
            turn: The conversation turn to add
        """
        self.conversation.append(turn)
        self._invalidate_cache()
    
    def add_message(
        self,
        role: str,
        content: str,
        speaker_name: Optional[str] = None,
        speaker_id: Optional[str] = None,
    ) -> ConversationTurn:
        """Convenience method to add a message.
        
        Args:
            role: Role of the speaker
            content: Message content
            speaker_name: Optional speaker display name
            speaker_id: Optional speaker ID
            
        Returns:
            The created ConversationTurn
        """
        turn = ConversationTurn(
            role=role,
            content=content,
            timestamp=datetime.now(timezone.utc),
            speaker_name=speaker_name,
            speaker_id=speaker_id,
        )
        self.add_turn(turn)
        return turn
    
    def get_for_reflex(self) -> str:
        """Get minimal context for REFLEX tier (~50 tokens).
        
        Returns only the essential state for fast responses.
        
        Returns:
            Minimal context string
        """
        return f"Topic: {self.current_topic}\nMood: {self.current_mood}"
    
    def get_for_reactive(self, max_tokens: int = 150) -> str:
        """Get recent context for REACTIVE tier.
        
        Includes recent conversation turns.
        
        Args:
            max_tokens: Approximate maximum tokens (chars / 4)
            
        Returns:
            Recent context string
        """
        max_chars = max_tokens * 4  # Rough char-to-token estimate
        
        recent = list(self.conversation)[-5:]
        lines = [turn.format_for_prompt(max_content_length=100) for turn in recent]
        
        result = "\n".join(lines)
        if len(result) > max_chars:
            result = result[:max_chars] + "..."
        
        return result
    
    def get_for_deliberate(self, max_tokens: int = 300) -> str:
        """Get fuller context for DELIBERATE tier.
        
        Includes more conversation history and current state.
        
        Args:
            max_tokens: Approximate maximum tokens
            
        Returns:
            Fuller context string
        """
        max_chars = max_tokens * 4
        
        # Include more turns
        recent = list(self.conversation)[-10:]
        lines = [turn.format_for_prompt(max_content_length=150) for turn in recent]
        
        conversation_context = "\n".join(lines)
        
        # Add state info
        state_info = f"\nCurrent topic: {self.current_topic}\nMood: {self.current_mood}\nConfidence: {self.confidence_level:.1f}"
        
        result = conversation_context + state_info
        if len(result) > max_chars:
            result = result[:max_chars] + "..."
        
        return result
    
    def get_recent_turns(self, n: int = 10) -> List[ConversationTurn]:
        """Get last N conversation turns.
        
        Args:
            n: Number of turns to retrieve
            
        Returns:
            List of recent ConversationTurn objects
        """
        return list(self.conversation)[-n:]
    
    def get_all_turns(self) -> List[ConversationTurn]:
        """Get all conversation turns.
        
        Returns:
            List of all ConversationTurn objects
        """
        return list(self.conversation)
    
    def get_turn_count(self) -> int:
        """Get number of turns in memory.
        
        Returns:
            Number of conversation turns
        """
        return len(self.conversation)
    
    def set_topic(self, topic: str) -> None:
        """Update current topic.
        
        Args:
            topic: The new current topic
        """
        self.current_topic = topic
        self._invalidate_cache()
    
    def set_mood(self, mood: str) -> None:
        """Update current mood.
        
        Args:
            mood: The new mood state
        """
        self.current_mood = mood
    
    def set_confidence(self, confidence: float) -> None:
        """Update confidence level.
        
        Args:
            confidence: Confidence level (0.0-1.0)
        """
        self.confidence_level = max(0.0, min(1.0, confidence))
    
    def get_cached(self, key: str) -> Optional[str]:
        """Get a cached value if not expired.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        if key in self._cache:
            if datetime.now(timezone.utc) < self._cache_ttl.get(key, datetime.min.replace(tzinfo=timezone.utc)):
                return self._cache[key]
            else:
                # Expired - remove
                del self._cache[key]
                del self._cache_ttl[key]
        return None
    
    def set_cached(
        self,
        key: str,
        value: str,
        ttl_seconds: int = DEFAULT_CACHE_TTL_SECONDS,
    ) -> None:
        """Cache a value with TTL.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Time-to-live in seconds
        """
        self._cache[key] = value
        self._cache_ttl[key] = datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)
    
    def _invalidate_cache(self) -> None:
        """Clear cache on new input."""
        self._cache.clear()
        self._cache_ttl.clear()
    
    def clear(self) -> None:
        """Clear all working memory."""
        self.conversation.clear()
        self.current_topic = ""
        self.current_mood = "neutral"
        self.confidence_level = 0.7
        self._invalidate_cache()
    
    def get_state(self) -> dict:
        """Get current working memory state.
        
        Returns:
            Dictionary with current state
        """
        return {
            "turn_count": len(self.conversation),
            "max_turns": self.max_turns,
            "current_topic": self.current_topic,
            "current_mood": self.current_mood,
            "confidence_level": self.confidence_level,
            "cache_size": len(self._cache),
        }
    
    def to_dict(self) -> dict:
        """Convert to full dictionary representation.
        
        Returns:
            Dictionary with all data
        """
        return {
            "turns": [turn.to_dict() for turn in self.conversation],
            "current_topic": self.current_topic,
            "current_mood": self.current_mood,
            "confidence_level": self.confidence_level,
            "max_turns": self.max_turns,
        }
    
    def extract_keywords_from_recent(self, n_turns: int = 5) -> List[str]:
        """Extract potential topic keywords from recent turns.
        
        Simple extraction for memory queries.
        
        Args:
            n_turns: Number of recent turns to analyze
            
        Returns:
            List of extracted keywords
        """
        # Simple approach: split on whitespace and filter
        stop_words = {
            "the", "a", "an", "is", "are", "was", "were", "be", "been",
            "being", "have", "has", "had", "do", "does", "did", "will",
            "would", "could", "should", "may", "might", "must", "shall",
            "can", "need", "to", "of", "in", "for", "on", "with", "at",
            "by", "from", "as", "into", "through", "during", "before",
            "after", "above", "below", "between", "under", "again",
            "further", "then", "once", "here", "there", "when", "where",
            "why", "how", "all", "each", "few", "more", "most", "other",
            "some", "such", "no", "nor", "not", "only", "own", "same",
            "so", "than", "too", "very", "just", "and", "but", "if", "or",
            "because", "until", "while", "about", "against", "this",
            "that", "these", "those", "it", "its", "i", "you", "we",
            "they", "he", "she", "my", "your", "our", "their", "his", "her",
        }
        
        keywords = []
        recent = self.get_recent_turns(n_turns)
        
        for turn in recent:
            words = turn.content.lower().split()
            for word in words:
                cleaned = word.strip(".,!?;:\"'()[]{}").lower()
                if len(cleaned) > 2 and cleaned not in stop_words:
                    if cleaned not in keywords:
                        keywords.append(cleaned)
        
        return keywords[:20]  # Limit to 20 keywords

