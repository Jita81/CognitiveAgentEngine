"""Memory Manager - Orchestrates all memory tiers.

Provides tier-appropriate access to memory based on cognitive tier,
handles memory promotion, and coordinates between working, short-term,
and long-term memory.

Phase 6 of the Cognitive Agent Engine.
"""

import logging
from typing import Optional, List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.cognitive.tiers import CognitiveTier, TIER_CONFIGS
from src.memory.working import WorkingMemory, ConversationTurn
from src.memory.short_term import ShortTermMemory, ShortTermMemoryEntry
from src.memory.long_term import LongTermMemory, ProjectChapter

logger = logging.getLogger(__name__)


class MemoryManager:
    """Manages all memory tiers and provides tier-appropriate access.
    
    The MemoryManager is the primary interface for memory operations,
    routing requests to the appropriate tier based on the cognitive
    tier being used.
    
    Memory Access by Tier:
    - REFLEX: Working memory only (cached, ~50 tokens)
    - REACTIVE: Working + recent short-term (~150 tokens)
    - DELIBERATE: Working + indexed short-term (~300 tokens)
    - ANALYTICAL: All tiers (~500 tokens)
    - COMPREHENSIVE: All tiers (~800 tokens)
    
    Attributes:
        agent_id: Agent this manager belongs to
        working: Working memory instance
        short_term: Short-term memory instance
        long_term: Long-term memory instance
    """
    
    def __init__(
        self,
        agent_id: UUID,
        working: WorkingMemory,
        short_term: ShortTermMemory,
        long_term: LongTermMemory,
    ):
        """Initialize memory manager.
        
        Args:
            agent_id: Agent ID
            working: Working memory instance
            short_term: Short-term memory instance
            long_term: Long-term memory instance
        """
        self.agent_id = agent_id
        self.working = working
        self.short_term = short_term
        self.long_term = long_term
    
    async def get_context_for_tier(
        self,
        tier: CognitiveTier,
        topic: Optional[str] = None,
    ) -> str:
        """Get memory context appropriate for a cognitive tier.
        
        Each tier has access to different memory depths:
        - REFLEX: Only working memory (fastest)
        - REACTIVE: Working + recent short-term
        - DELIBERATE: Working + indexed short-term
        - ANALYTICAL/COMPREHENSIVE: All tiers
        
        Args:
            tier: Cognitive tier requesting memory
            topic: Optional topic to focus retrieval
            
        Returns:
            Formatted memory context string
        """
        config = TIER_CONFIGS[tier]
        memory_access = config.memory_access.value  # Get string value from enum
        
        if memory_access == "cached":
            # REFLEX: working memory only
            return self.working.get_for_reflex()
        
        elif memory_access == "recent":
            # REACTIVE: working + recent short-term
            working = self.working.get_for_reactive()
            recent = await self.short_term.get_recent(hours=1, max_tokens=100)
            
            if recent:
                return f"{working}\n\nRecent:\n{recent}"
            return working
        
        elif memory_access == "indexed":
            # DELIBERATE: working + indexed short-term
            working = self.working.get_for_deliberate(max_tokens=150)
            
            if topic:
                indexed = await self.short_term.query(
                    topic=topic,
                    max_results=5,
                    max_tokens=300,
                )
            else:
                # Fall back to recent if no topic
                indexed = await self.short_term.get_recent(hours=24, max_tokens=300)
            
            if indexed:
                return f"{working}\n\nRelevant memories:\n{indexed}"
            return working
        
        else:
            # ANALYTICAL/COMPREHENSIVE: full search
            return await self._get_full_context(topic)
    
    async def _get_full_context(self, topic: Optional[str] = None) -> str:
        """Get full memory context from all tiers.
        
        Used for ANALYTICAL and COMPREHENSIVE cognitive tiers.
        
        Args:
            topic: Optional topic to focus search
            
        Returns:
            Full memory context string
        """
        sections = []
        
        # Working memory
        working = self.working.get_for_deliberate(max_tokens=200)
        if working:
            sections.append(f"Working Memory:\n{working}")
        
        # Short-term memories
        if topic:
            short = await self.short_term.query(
                topic=topic,
                max_results=10,
                max_tokens=400,
            )
        else:
            short = await self.short_term.get_recent(hours=48, max_tokens=400)
        
        if short:
            sections.append(f"Recent Experience:\n{short}")
        
        # Long-term memories
        long = await self.long_term.search(
            topic=topic,
            max_results=5,
            max_tokens=400,
        )
        
        if long:
            sections.append(f"Long-term Memory:\n{long}")
        
        return "\n\n".join(sections)
    
    async def record_significant_event(
        self,
        content: str,
        memory_type: str,
        significance: float,
        topic: str,
        project_id: Optional[UUID] = None,
        related_agents: Optional[List[str]] = None,
    ) -> ShortTermMemoryEntry:
        """Record a significant event to short-term memory.
        
        Events with high significance may be later promoted to
        long-term memory.
        
        Args:
            content: Event description
            memory_type: Type (observation, decision, interaction, insight)
            significance: Importance score (0.0-1.0)
            topic: Topic/context of the event
            project_id: Optional related project
            related_agents: List of involved agent IDs
            
        Returns:
            Created ShortTermMemoryEntry
        """
        keywords = topic.split() if topic else []
        
        entry = await self.short_term.add(
            content=content,
            memory_type=memory_type,
            significance=significance,
            topic_keywords=keywords,
            project_id=project_id,
            related_agents=related_agents,
            confidence_at_time=str(self.working.confidence_level),
        )
        
        logger.debug(
            f"Recorded significant event for agent {self.agent_id}: "
            f"{memory_type} with significance {significance:.2f}"
        )
        
        return entry
    
    async def evaluate_promotion(
        self,
        memory_id: UUID,
        significance: float,
        relationship_delta: int = 0,
    ) -> bool:
        """Check if a memory should be promoted to long-term.
        
        Promotion criteria:
        - Significance >= 0.7
        - Significant relationship change (|delta| >= 1)
        
        Args:
            memory_id: Memory to evaluate
            significance: Memory's significance score
            relationship_delta: Change in relationship metrics
            
        Returns:
            True if memory should be promoted
        """
        # Promotion criteria
        if significance >= 0.7:
            logger.debug(f"Memory {memory_id} eligible for promotion (high significance)")
            return True
        
        if abs(relationship_delta) >= 1:
            logger.debug(f"Memory {memory_id} eligible for promotion (relationship change)")
            return True
        
        return False
    
    async def promote_memory(
        self,
        memory_id: UUID,
        project_id: UUID,
        title: str,
        lessons: Optional[str] = None,
    ) -> Optional[ProjectChapter]:
        """Promote a short-term memory to long-term.
        
        Creates a project chapter from the short-term memory
        and marks the original as promoted.
        
        Args:
            memory_id: Short-term memory to promote
            project_id: Project to associate with
            title: Title for the chapter
            lessons: Lessons learned (optional)
            
        Returns:
            Created ProjectChapter or None if memory not found
        """
        # Get the short-term memory
        entry = await self.short_term.get_by_id(memory_id)
        if not entry:
            logger.warning(f"Memory {memory_id} not found for promotion")
            return None
        
        # Create long-term chapter
        chapter = await self.long_term.add_chapter(
            project_id=project_id,
            title=title,
            summary=entry.content,
            significance=entry.significance,
            lessons=lessons,
        )
        
        # Mark as promoted
        await self.short_term.promote_to_long_term(memory_id, chapter.chapter_id)
        
        logger.info(
            f"Promoted memory {memory_id} to chapter {chapter.chapter_id}"
        )
        
        return chapter
    
    def add_conversation_turn(
        self,
        role: str,
        content: str,
        speaker_name: Optional[str] = None,
        speaker_id: Optional[str] = None,
    ) -> ConversationTurn:
        """Add a turn to working memory.
        
        Convenience method for adding conversation context.
        
        Args:
            role: Speaker role (user, assistant, system)
            content: Message content
            speaker_name: Optional display name
            speaker_id: Optional speaker ID
            
        Returns:
            Created ConversationTurn
        """
        return self.working.add_message(
            role=role,
            content=content,
            speaker_name=speaker_name,
            speaker_id=speaker_id,
        )
    
    def update_topic(self, topic: str) -> None:
        """Update the current topic in working memory.
        
        Args:
            topic: New current topic
        """
        self.working.set_topic(topic)
    
    def update_confidence(self, confidence: float) -> None:
        """Update agent's confidence level.
        
        Args:
            confidence: New confidence (0.0-1.0)
        """
        self.working.set_confidence(confidence)
    
    def update_mood(self, mood: str) -> None:
        """Update agent's current mood.
        
        Args:
            mood: New mood state
        """
        self.working.set_mood(mood)
    
    async def cleanup_expired(self) -> int:
        """Clean up expired short-term memories.
        
        Returns:
            Number of deleted entries
        """
        deleted = await self.short_term.delete_expired()
        if deleted > 0:
            logger.info(f"Cleaned up {deleted} expired memories for agent {self.agent_id}")
        return deleted
    
    def get_working_state(self) -> dict:
        """Get current working memory state.
        
        Returns:
            Working memory state dictionary
        """
        return self.working.get_state()
    
    def clear_working_memory(self) -> None:
        """Clear working memory.
        
        Used when starting a new session.
        """
        self.working.clear()
        logger.debug(f"Cleared working memory for agent {self.agent_id}")


async def create_memory_manager(
    session: AsyncSession,
    agent_id: UUID,
    max_working_turns: int = 20,
) -> MemoryManager:
    """Factory function to create a MemoryManager.
    
    Creates all memory tier instances and wires them together.
    
    Args:
        session: Database session
        agent_id: Agent ID
        max_working_turns: Maximum turns in working memory
        
    Returns:
        Configured MemoryManager
    """
    working = WorkingMemory(max_turns=max_working_turns)
    short_term = ShortTermMemory(session=session, agent_id=agent_id)
    long_term = LongTermMemory(session=session, agent_id=agent_id)
    
    return MemoryManager(
        agent_id=agent_id,
        working=working,
        short_term=short_term,
        long_term=long_term,
    )

