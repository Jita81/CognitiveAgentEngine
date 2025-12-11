"""Internal Mind module for cognitive workspace management.

This module implements the agent's Internal Mind - a cognitive workspace where
thoughts exist independently of speaking. The mind accumulates thoughts into
streams, synthesizes related thoughts, and manages what's ready to share.

Phase 4 of the Cognitive Agent Engine.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable, Dict, List, Optional
from uuid import UUID, uuid4

from src.cognitive.models import Thought

logger = logging.getLogger(__name__)


class StreamStatus:
    """Status values for thought streams."""
    
    ACTIVE = "active"
    PAUSED = "paused"
    NEEDS_SYNTHESIS = "needs_synthesis"
    CONCLUDED = "concluded"
    ABANDONED = "abandoned"


@dataclass
class ThoughtStream:
    """A stream of related thoughts building toward something.
    
    Thought streams group related thoughts by topic, enabling the agent
    to accumulate observations and insights before synthesizing them
    into a coherent contribution.
    
    Attributes:
        stream_id: Unique identifier for this stream
        topic: The topic this stream is about
        thoughts: List of thoughts in this stream
        status: Current status of the stream
        created_at: When the stream was created
        synthesized_output: The synthesis result if synthesized
        ready_to_externalize: Whether synthesis is ready to share
    """
    
    stream_id: str
    topic: str
    thoughts: List[Thought] = field(default_factory=list)
    status: str = StreamStatus.ACTIVE
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    synthesized_output: Optional[Thought] = None
    ready_to_externalize: bool = False
    
    def add_thought(self, thought: Thought) -> None:
        """Add a thought to this stream.
        
        Args:
            thought: The thought to add
        """
        self.thoughts.append(thought)
        # Link to previous thoughts in stream
        if len(self.thoughts) > 1:
            prior_ids = [t.thought_id for t in self.thoughts[:-1]]
            # Update related_thought_ids (limited to last few)
            thought.related_thought_ids = list(prior_ids[-3:])
    
    def get_recent(self, n: int = 3) -> List[Thought]:
        """Get the most recent thoughts in this stream.
        
        Args:
            n: Number of thoughts to return
            
        Returns:
            List of most recent thoughts
        """
        return self.thoughts[-n:]
    
    @property
    def avg_confidence(self) -> float:
        """Calculate average confidence across all thoughts."""
        if not self.thoughts:
            return 0.0
        return sum(t.confidence for t in self.thoughts) / len(self.thoughts)
    
    @property
    def avg_completeness(self) -> float:
        """Calculate average completeness across all thoughts."""
        if not self.thoughts:
            return 0.0
        return sum(t.completeness for t in self.thoughts) / len(self.thoughts)
    
    @property
    def thought_count(self) -> int:
        """Get number of thoughts in stream."""
        return len(self.thoughts)
    
    @property
    def time_span_seconds(self) -> float:
        """Get time span from first to last thought in seconds."""
        if len(self.thoughts) < 2:
            return 0.0
        first = self.thoughts[0].created_at
        last = self.thoughts[-1].created_at
        return (last - first).total_seconds()
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
        return {
            "stream_id": self.stream_id,
            "topic": self.topic,
            "thought_count": self.thought_count,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "avg_confidence": self.avg_confidence,
            "avg_completeness": self.avg_completeness,
            "time_span_seconds": self.time_span_seconds,
            "ready_to_externalize": self.ready_to_externalize,
            "has_synthesis": self.synthesized_output is not None,
        }


class InternalMind:
    """The agent's cognitive workspace where thoughts exist.
    
    The Internal Mind is the central cognitive workspace for an agent.
    It manages:
    - Active thoughts that haven't been resolved
    - Thought streams grouping related thoughts by topic
    - Held insights (things known but not shared)
    - Thoughts ready to share when appropriate
    - Background processing tasks
    
    This enables agents to "think" continuously - thoughts exist
    whether they're spoken or not, and can accumulate and synthesize
    over time.
    
    Attributes:
        agent_id: ID of the agent this mind belongs to
        active_thoughts: Currently active thoughts by ID
        streams: Thought streams by stream ID
        held_insights: Insights held internally
        ready_to_share: Thoughts ready for externalization
        background_tasks: Background processing tasks
    """
    
    def __init__(self, agent_id: str):
        """Initialize the internal mind.
        
        Args:
            agent_id: ID of the agent this mind belongs to
        """
        self.agent_id = agent_id
        
        # Active thoughts not yet resolved
        self.active_thoughts: Dict[str, Thought] = {}
        
        # Thought streams (trains of thought by topic)
        self.streams: Dict[str, ThoughtStream] = {}
        
        # Held insights (things I know but haven't shared)
        self.held_insights: List[Thought] = []
        
        # Ready to share when appropriate
        self.ready_to_share: List[Thought] = []
        
        # Background tasks
        self.background_tasks: List[asyncio.Task] = []
        
        # Callback for when synthesis is needed (set by accumulator)
        self._synthesis_callback: Optional[Callable] = None
    
    def add_thought(self, thought: Thought) -> ThoughtStream:
        """Add a new thought to the mind.
        
        The thought is added to active_thoughts and associated with
        an appropriate stream (existing or new).
        
        Args:
            thought: The thought to add
            
        Returns:
            The ThoughtStream this thought was added to
        """
        # Store in active thoughts
        thought_id_str = str(thought.thought_id)
        self.active_thoughts[thought_id_str] = thought
        
        # Find or create related stream
        stream = self._find_or_create_stream(thought)
        stream.add_thought(thought)
        
        logger.debug(
            f"Added thought {thought_id_str[:8]} to stream '{stream.topic}' "
            f"(now {stream.thought_count} thoughts)"
        )
        
        # Check if stream should be synthesized
        if self._should_synthesize(stream):
            stream.status = StreamStatus.NEEDS_SYNTHESIS
            logger.debug(f"Stream '{stream.topic}' marked for synthesis")
        
        return stream
    
    def hold_insight(self, thought: Thought) -> None:
        """Hold an insight internally - don't share it now.
        
        The thought still exists and affects internal state,
        but is not queued for externalization.
        
        Args:
            thought: The thought to hold
        """
        thought.externalized = False
        if thought not in self.held_insights:
            self.held_insights.append(thought)
            logger.debug(f"Holding insight: {str(thought.thought_id)[:8]}")
    
    def prepare_to_share(self, thought: Thought) -> None:
        """Mark a thought as ready to share when appropriate.
        
        Args:
            thought: The thought to prepare for sharing
        """
        if thought not in self.ready_to_share:
            self.ready_to_share.append(thought)
            logger.debug(f"Prepared to share: {str(thought.thought_id)[:8]}")
    
    def get_best_contribution(self) -> Optional[Thought]:
        """Get the best thought to share right now.
        
        Selects from ready_to_share based on:
        - Still relevant
        - Highest completeness
        - Highest confidence
        
        Returns:
            The best thought to share, or None if nothing ready
        """
        if not self.ready_to_share:
            return None
        
        # Filter to still-relevant thoughts
        valid = [t for t in self.ready_to_share if t.still_relevant]
        if not valid:
            return None
        
        # Rank by completeness (primary) and confidence (secondary)
        ranked = sorted(
            valid,
            key=lambda t: (t.completeness, t.confidence),
            reverse=True
        )
        
        return ranked[0]
    
    def mark_externalized(self, thought_id: UUID) -> None:
        """Mark a thought as having been spoken/shared.
        
        Args:
            thought_id: ID of the thought that was externalized
        """
        thought_id_str = str(thought_id)
        
        if thought_id_str in self.active_thoughts:
            thought = self.active_thoughts[thought_id_str]
            thought.externalized = True
            thought.externalized_at = datetime.now(timezone.utc)
            logger.debug(f"Marked externalized: {thought_id_str[:8]}")
        
        # Remove from ready_to_share
        self.ready_to_share = [
            t for t in self.ready_to_share
            if str(t.thought_id) != thought_id_str
        ]
    
    def invalidate_thoughts_about(self, topic: str) -> int:
        """Mark thoughts about a topic as no longer relevant.
        
        Called when new information supersedes previous thinking.
        
        Args:
            topic: The topic to invalidate thoughts about
            
        Returns:
            Number of thoughts invalidated
        """
        count = 0
        
        for thought in self.active_thoughts.values():
            if self._thought_relates_to(thought, topic):
                thought.still_relevant = False
                count += 1
        
        # Also clear from ready_to_share
        original_count = len(self.ready_to_share)
        self.ready_to_share = [
            t for t in self.ready_to_share
            if not self._thought_relates_to(t, topic)
        ]
        count += original_count - len(self.ready_to_share)
        
        if count > 0:
            logger.debug(f"Invalidated {count} thoughts about '{topic}'")
        
        return count
    
    def get_thoughts_for_context(self, n: int = 5) -> List[Thought]:
        """Get recent thoughts for use as context in prompts.
        
        Args:
            n: Maximum number of thoughts to return
            
        Returns:
            List of recent thoughts, most recent first
        """
        recent = sorted(
            self.active_thoughts.values(),
            key=lambda t: t.created_at,
            reverse=True
        )[:n]
        return recent
    
    def get_stream_for_topic(self, topic: str) -> Optional[ThoughtStream]:
        """Find a stream matching the given topic.
        
        Args:
            topic: Topic to search for
            
        Returns:
            Matching ThoughtStream or None
        """
        topic_lower = topic.lower()
        for stream in self.streams.values():
            if topic_lower in stream.topic.lower():
                return stream
        return None
    
    def get_streams_needing_synthesis(self) -> List[ThoughtStream]:
        """Get all streams that need synthesis.
        
        Returns:
            List of streams with NEEDS_SYNTHESIS status
        """
        return [
            s for s in self.streams.values()
            if s.status == StreamStatus.NEEDS_SYNTHESIS
        ]
    
    def _find_or_create_stream(self, thought: Thought) -> ThoughtStream:
        """Find an existing stream or create a new one for a thought.
        
        Args:
            thought: The thought to find/create a stream for
            
        Returns:
            The appropriate ThoughtStream
        """
        # Extract topic from thought content
        topic = self._extract_topic(thought.content)
        
        # Look for existing stream with related topic
        for stream in self.streams.values():
            if stream.status in (StreamStatus.ACTIVE, StreamStatus.PAUSED):
                if self._topics_related(stream.topic, topic):
                    return stream
        
        # Create new stream
        stream = ThoughtStream(
            stream_id=self._generate_id(),
            topic=topic
        )
        self.streams[stream.stream_id] = stream
        logger.debug(f"Created new stream for topic: '{topic}'")
        
        return stream
    
    def _should_synthesize(self, stream: ThoughtStream) -> bool:
        """Determine if a stream should be synthesized.
        
        Synthesis triggers:
        - 3+ thoughts in stream
        - 2+ thoughts spanning >30 seconds with avg confidence >0.6
        
        Args:
            stream: The stream to check
            
        Returns:
            True if synthesis should be triggered
        """
        if stream.status != StreamStatus.ACTIVE:
            return False
        
        thought_count = stream.thought_count
        
        # Trigger at 3+ thoughts
        if thought_count >= 3:
            return True
        
        # Trigger at 2+ thoughts with time span and confidence
        if thought_count >= 2:
            time_span = stream.time_span_seconds
            if time_span > 30 and stream.avg_confidence > 0.6:
                return True
        
        return False
    
    def _extract_topic(self, content: str) -> str:
        """Extract a topic from thought content.
        
        Simple extraction using first few significant words.
        
        Args:
            content: The thought content
            
        Returns:
            Extracted topic string
        """
        # Remove common filler words
        stop_words = {
            "i", "the", "a", "an", "is", "are", "was", "were", "be", "been",
            "being", "have", "has", "had", "do", "does", "did", "will", "would",
            "could", "should", "may", "might", "must", "that", "this", "these",
            "those", "it", "its", "of", "to", "in", "for", "on", "with", "at",
            "by", "from", "as", "into", "through", "during", "before", "after",
            "and", "but", "or", "so", "if", "then", "else", "when", "there",
            "here", "all", "each", "every", "both", "few", "more", "most",
            "other", "some", "such", "no", "not", "only", "own", "same",
            "than", "too", "very", "just", "also", "now", "about", "think",
            "thinking", "thought", "seems", "like", "really", "actually",
        }
        
        words = content.lower().split()
        significant = [w for w in words if w not in stop_words and len(w) > 2]
        
        # Take first 3-5 significant words
        topic_words = significant[:5]
        if not topic_words:
            topic_words = words[:3]
        
        return " ".join(topic_words)
    
    def _topics_related(self, topic1: str, topic2: str) -> bool:
        """Check if two topics are related.
        
        Uses word overlap to determine relatedness.
        
        Args:
            topic1: First topic
            topic2: Second topic
            
        Returns:
            True if topics are related
        """
        words1 = set(topic1.lower().split())
        words2 = set(topic2.lower().split())
        overlap = words1 & words2
        
        # Consider related if at least 1 word overlaps
        return len(overlap) > 0
    
    def _thought_relates_to(self, thought: Thought, topic: str) -> bool:
        """Check if a thought relates to a topic.
        
        Args:
            thought: The thought to check
            topic: The topic to match against
            
        Returns:
            True if thought relates to topic
        """
        topic_lower = topic.lower()
        content_lower = thought.content.lower()
        
        # Check for direct topic mention
        if topic_lower in content_lower:
            return True
        
        # Check for word overlap
        topic_words = set(topic_lower.split())
        content_words = set(content_lower.split())
        overlap = topic_words & content_words
        
        return len(overlap) >= 2
    
    def _generate_id(self) -> str:
        """Generate a unique ID string."""
        return str(uuid4())
    
    def get_state(self) -> dict:
        """Get current mind state as dictionary.
        
        Returns:
            Dictionary with mind state information
        """
        active_tasks = [t for t in self.background_tasks if not t.done()]
        
        return {
            "agent_id": self.agent_id,
            "active_thoughts": len(self.active_thoughts),
            "streams": len(self.streams),
            "streams_needing_synthesis": len(self.get_streams_needing_synthesis()),
            "held_insights": len(self.held_insights),
            "ready_to_share": len(self.ready_to_share),
            "background_tasks": len(active_tasks),
            "stream_topics": [s.topic for s in self.streams.values()],
        }
    
    def get_detailed_state(self) -> dict:
        """Get detailed mind state including stream info.
        
        Returns:
            Detailed dictionary with full state information
        """
        state = self.get_state()
        state["streams_detail"] = [s.to_dict() for s in self.streams.values()]
        state["ready_thoughts"] = [
            {
                "thought_id": str(t.thought_id),
                "tier": t.tier.name,
                "confidence": t.confidence,
                "completeness": t.completeness,
            }
            for t in self.ready_to_share
        ]
        return state
    
    def cleanup_old_thoughts(self, max_age_minutes: int = 30) -> int:
        """Remove thoughts older than specified age.
        
        Args:
            max_age_minutes: Maximum age in minutes
            
        Returns:
            Number of thoughts removed
        """
        from datetime import timedelta
        
        threshold = datetime.now(timezone.utc) - timedelta(minutes=max_age_minutes)
        count = 0
        
        # Remove from active thoughts
        to_remove = [
            tid for tid, thought in self.active_thoughts.items()
            if thought.created_at < threshold and not thought.externalized
        ]
        for tid in to_remove:
            del self.active_thoughts[tid]
            count += 1
        
        # Clean up concluded streams
        concluded = [
            sid for sid, stream in self.streams.items()
            if stream.status == StreamStatus.CONCLUDED
        ]
        for sid in concluded:
            del self.streams[sid]
        
        # Clean up abandoned streams older than threshold
        abandoned = [
            sid for sid, stream in self.streams.items()
            if stream.created_at < threshold and stream.thought_count == 0
        ]
        for sid in abandoned:
            del self.streams[sid]
        
        if count > 0:
            logger.debug(f"Cleaned up {count} old thoughts")
        
        return count
    
    def clear(self) -> None:
        """Clear all state from the mind.
        
        Useful for testing or resetting an agent's cognitive state.
        """
        self.active_thoughts.clear()
        self.streams.clear()
        self.held_insights.clear()
        self.ready_to_share.clear()
        
        # Cancel background tasks
        for task in self.background_tasks:
            if not task.done():
                task.cancel()
        self.background_tasks.clear()
        
        logger.debug(f"Cleared mind for agent {self.agent_id}")

