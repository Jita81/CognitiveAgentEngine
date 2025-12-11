"""Social models for stimulus representation.

This module provides models for representing incoming stimuli
that agents need to evaluate for social response decisions.

Phase 5 of the Cognitive Agent Engine.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional


@dataclass
class Stimulus:
    """Input stimulus for social intelligence evaluation.
    
    Represents any incoming message, event, or communication that
    an agent might need to respond to.
    
    Attributes:
        content: The actual text/content of the stimulus
        source_id: ID of the agent/entity that produced this stimulus
        source_name: Display name of the source
        directed_at: List of agent IDs this is directed at (None = broadcast)
        topic: Extracted or labeled topic of the stimulus
        timestamp: When this stimulus occurred
        priority: How urgent/important this stimulus is (0.0-1.0)
        requires_response: Whether a response is explicitly expected
    """
    
    content: str
    source_id: Optional[str] = None
    source_name: Optional[str] = None
    directed_at: Optional[List[str]] = None  # None = broadcast to all
    topic: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    priority: float = 0.5
    requires_response: bool = False
    
    @property
    def is_broadcast(self) -> bool:
        """Check if this stimulus is broadcast to all participants.
        
        Returns:
            True if directed_at is None or empty
        """
        return self.directed_at is None or len(self.directed_at) == 0
    
    @property
    def is_directed(self) -> bool:
        """Check if this stimulus is directed at specific agents.
        
        Returns:
            True if directed_at contains one or more agent IDs
        """
        return self.directed_at is not None and len(self.directed_at) > 0
    
    def is_directed_at(self, agent_id: str, agent_name: Optional[str] = None) -> bool:
        """Check if this stimulus is directed at a specific agent.
        
        Args:
            agent_id: The agent ID to check
            agent_name: Optional agent name to also check
            
        Returns:
            True if stimulus is directed at this agent
        """
        if self.directed_at is None:
            return False
        
        # Check direct ID match
        if agent_id in self.directed_at:
            return True
        
        # Check name match if provided
        if agent_name:
            name_lower = agent_name.lower()
            for target in self.directed_at:
                if target.lower() == name_lower:
                    return True
        
        return False
    
    def mentions_agent(self, agent_id: str, agent_name: str) -> bool:
        """Check if the content mentions a specific agent.
        
        Args:
            agent_id: The agent ID to check for
            agent_name: The agent name to check for
            
        Returns:
            True if agent is mentioned in content
        """
        content_lower = self.content.lower()
        name_lower = agent_name.lower()
        
        # Check for name mention
        if name_lower in content_lower:
            return True
        
        # Check for @mention pattern
        if f"@{name_lower}" in content_lower:
            return True
        
        return False
    
    def extract_keywords(self) -> List[str]:
        """Extract keywords from the stimulus content.
        
        Simple keyword extraction for topic matching.
        
        Returns:
            List of lowercase keywords
        """
        # Simple approach: split on whitespace and filter
        words = self.content.lower().split()
        # Filter out very short words and common stop words
        stop_words = {
            "the", "a", "an", "is", "are", "was", "were", "be", "been",
            "being", "have", "has", "had", "do", "does", "did", "will",
            "would", "could", "should", "may", "might", "must", "shall",
            "can", "need", "dare", "ought", "used", "to", "of", "in",
            "for", "on", "with", "at", "by", "from", "as", "into",
            "through", "during", "before", "after", "above", "below",
            "between", "under", "again", "further", "then", "once",
            "here", "there", "when", "where", "why", "how", "all",
            "each", "few", "more", "most", "other", "some", "such",
            "no", "nor", "not", "only", "own", "same", "so", "than",
            "too", "very", "just", "and", "but", "if", "or", "because",
            "until", "while", "about", "against", "this", "that",
            "these", "those", "it", "its", "i", "you", "we", "they",
            "he", "she", "my", "your", "our", "their", "his", "her",
        }
        
        keywords = [
            word.strip(".,!?;:\"'()[]{}") 
            for word in words 
            if len(word) > 2 and word.lower() not in stop_words
        ]
        
        return keywords
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "content": self.content,
            "source_id": self.source_id,
            "source_name": self.source_name,
            "directed_at": self.directed_at,
            "topic": self.topic,
            "timestamp": self.timestamp.isoformat(),
            "priority": self.priority,
            "requires_response": self.requires_response,
            "is_broadcast": self.is_broadcast,
            "is_directed": self.is_directed,
        }
    
    @classmethod
    def from_message(
        cls,
        content: str,
        source_id: Optional[str] = None,
        source_name: Optional[str] = None,
        topic: Optional[str] = None,
    ) -> "Stimulus":
        """Create a stimulus from a simple message.
        
        Args:
            content: The message content
            source_id: ID of message sender
            source_name: Name of message sender
            topic: Optional topic override
            
        Returns:
            New Stimulus instance
        """
        stimulus = cls(
            content=content,
            source_id=source_id,
            source_name=source_name,
            topic=topic or "",
        )
        
        # Auto-extract topic if not provided
        if not topic:
            keywords = stimulus.extract_keywords()
            if keywords:
                stimulus.topic = " ".join(keywords[:5])  # First 5 keywords
        
        return stimulus
    
    @classmethod
    def direct_question(
        cls,
        content: str,
        directed_at: List[str],
        source_id: Optional[str] = None,
        source_name: Optional[str] = None,
        topic: str = "",
    ) -> "Stimulus":
        """Create a stimulus representing a direct question.
        
        Args:
            content: The question content
            directed_at: List of agent IDs being asked
            source_id: ID of questioner
            source_name: Name of questioner
            topic: Topic of the question
            
        Returns:
            New Stimulus instance marked as requiring response
        """
        return cls(
            content=content,
            source_id=source_id,
            source_name=source_name,
            directed_at=directed_at,
            topic=topic,
            requires_response=True,
            priority=0.8,
        )

