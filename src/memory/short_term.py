"""Short-Term Memory - Tier 2 of the memory architecture.

PostgreSQL-backed recent significant events with 7-day TTL.
Used for observations, decisions, interactions, and insights
that are important but not permanent.

Phase 6 of the Cognitive Agent Engine.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.memory.models import ShortTermMemoryDB, get_default_expiry


@dataclass
class ShortTermMemoryEntry:
    """A short-term memory entry.
    
    Attributes:
        memory_id: Unique identifier
        agent_id: Agent this memory belongs to
        memory_type: Type of memory (observation, decision, interaction, insight)
        content: The actual memory content
        significance: Importance score (0.0-1.0)
        topic_keywords: Keywords for searching
        created_at: When created
        expires_at: When this memory expires
        project_id: Optional related project
        related_agents: List of agent IDs involved
        confidence_at_time: Agent's confidence when memory was created
        promoted_to: Long-term memory ID if promoted
    """
    
    memory_id: UUID
    agent_id: UUID
    memory_type: str
    content: str
    significance: float
    topic_keywords: List[str]
    created_at: datetime
    expires_at: datetime
    project_id: Optional[UUID] = None
    related_agents: Optional[List[str]] = None
    confidence_at_time: Optional[str] = None
    promoted_to: Optional[UUID] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "memory_id": str(self.memory_id),
            "agent_id": str(self.agent_id),
            "memory_type": self.memory_type,
            "content": self.content,
            "significance": self.significance,
            "topic_keywords": self.topic_keywords,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "project_id": str(self.project_id) if self.project_id else None,
            "related_agents": self.related_agents,
            "confidence_at_time": self.confidence_at_time,
            "promoted_to": str(self.promoted_to) if self.promoted_to else None,
        }
    
    def is_expired(self) -> bool:
        """Check if this memory has expired.
        
        Returns:
            True if expired
        """
        return datetime.now(timezone.utc) > self.expires_at


class ShortTermMemory:
    """Tier 2: Recent significant events.
    
    PostgreSQL-backed, 7-day TTL, indexed by topic.
    
    Attributes:
        session: Database session
        agent_id: Agent this memory belongs to
    """
    
    DEFAULT_TTL_DAYS = 7
    MAX_ENTRIES = 100
    
    def __init__(self, session: AsyncSession, agent_id: UUID):
        """Initialize short-term memory.
        
        Args:
            session: Database session
            agent_id: Agent ID
        """
        self.session = session
        self.agent_id = agent_id
    
    async def add(
        self,
        content: str,
        memory_type: str,
        significance: float,
        topic_keywords: Optional[List[str]] = None,
        project_id: Optional[UUID] = None,
        related_agents: Optional[List[str]] = None,
        confidence_at_time: Optional[str] = None,
        ttl_days: Optional[int] = None,
    ) -> ShortTermMemoryEntry:
        """Add a memory entry.
        
        Args:
            content: Memory content
            memory_type: Type (observation, decision, interaction, insight)
            significance: Importance score (0.0-1.0)
            topic_keywords: Keywords for searching
            project_id: Optional related project ID
            related_agents: List of related agent IDs
            confidence_at_time: Agent's confidence level
            ttl_days: Custom TTL (default: 7 days)
            
        Returns:
            Created ShortTermMemoryEntry
        """
        # Ensure not at capacity
        count = await self._count_entries()
        if count >= self.MAX_ENTRIES:
            await self._evict_oldest()
        
        # Calculate expiry
        ttl = ttl_days or self.DEFAULT_TTL_DAYS
        expires_at = datetime.now(timezone.utc) + timedelta(days=ttl)
        
        # Create DB entry
        db_entry = ShortTermMemoryDB(
            memory_id=uuid4(),
            agent_id=self.agent_id,
            memory_type=memory_type,
            content=content,
            significance=max(0.0, min(1.0, significance)),
            topic_keywords=topic_keywords or [],
            project_id=project_id,
            related_agents=related_agents,
            confidence_at_time=confidence_at_time,
            created_at=datetime.now(timezone.utc),
            expires_at=expires_at,
        )
        
        self.session.add(db_entry)
        await self.session.commit()
        await self.session.refresh(db_entry)
        
        return self._to_model(db_entry)
    
    async def query(
        self,
        topic: Optional[str] = None,
        keywords: Optional[List[str]] = None,
        memory_type: Optional[str] = None,
        project_id: Optional[UUID] = None,
        min_significance: float = 0.0,
        max_results: int = 10,
        max_tokens: int = 300,
    ) -> str:
        """Query memories by topic/keywords.
        
        Args:
            topic: Topic to search for
            keywords: Keywords to match
            memory_type: Filter by memory type
            project_id: Filter by project
            min_significance: Minimum significance score
            max_results: Maximum entries to return
            max_tokens: Maximum tokens for formatted output
            
        Returns:
            Formatted memory string for prompt context
        """
        query = select(ShortTermMemoryDB).where(
            ShortTermMemoryDB.agent_id == self.agent_id,
            ShortTermMemoryDB.expires_at > datetime.now(timezone.utc),
            ShortTermMemoryDB.significance >= min_significance,
        )
        
        if memory_type:
            query = query.where(ShortTermMemoryDB.memory_type == memory_type)
        
        if project_id:
            query = query.where(ShortTermMemoryDB.project_id == project_id)
        
        # Note: For keyword matching, using simple ILIKE for now
        # Future: Use GIN index on JSONB for better performance
        if topic:
            query = query.where(
                ShortTermMemoryDB.content.ilike(f"%{topic}%")
            )
        
        query = query.order_by(
            ShortTermMemoryDB.significance.desc(),
            ShortTermMemoryDB.created_at.desc(),
        ).limit(max_results)
        
        result = await self.session.execute(query)
        entries = result.scalars().all()
        
        return self._format_entries(entries, max_tokens)
    
    async def query_entries(
        self,
        keywords: Optional[List[str]] = None,
        memory_type: Optional[str] = None,
        min_significance: float = 0.0,
        max_results: int = 10,
    ) -> List[ShortTermMemoryEntry]:
        """Query memories and return as entry objects.
        
        Args:
            keywords: Keywords to match in content
            memory_type: Filter by memory type
            min_significance: Minimum significance score
            max_results: Maximum entries to return
            
        Returns:
            List of ShortTermMemoryEntry objects
        """
        query = select(ShortTermMemoryDB).where(
            ShortTermMemoryDB.agent_id == self.agent_id,
            ShortTermMemoryDB.expires_at > datetime.now(timezone.utc),
            ShortTermMemoryDB.significance >= min_significance,
        )
        
        if memory_type:
            query = query.where(ShortTermMemoryDB.memory_type == memory_type)
        
        query = query.order_by(
            ShortTermMemoryDB.significance.desc(),
            ShortTermMemoryDB.created_at.desc(),
        ).limit(max_results)
        
        result = await self.session.execute(query)
        entries = result.scalars().all()
        
        return [self._to_model(entry) for entry in entries]
    
    async def get_recent(
        self,
        hours: int = 24,
        max_tokens: int = 200,
    ) -> str:
        """Get recent memories.
        
        Args:
            hours: Look back period in hours
            max_tokens: Maximum tokens for formatted output
            
        Returns:
            Formatted memory string for prompt context
        """
        since = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        query = select(ShortTermMemoryDB).where(
            ShortTermMemoryDB.agent_id == self.agent_id,
            ShortTermMemoryDB.created_at > since,
            ShortTermMemoryDB.expires_at > datetime.now(timezone.utc),
        ).order_by(
            ShortTermMemoryDB.created_at.desc(),
        ).limit(10)
        
        result = await self.session.execute(query)
        entries = result.scalars().all()
        
        return self._format_entries(entries, max_tokens)
    
    async def get_by_id(self, memory_id: UUID) -> Optional[ShortTermMemoryEntry]:
        """Get a memory by ID.
        
        Args:
            memory_id: Memory ID to fetch
            
        Returns:
            ShortTermMemoryEntry or None
        """
        query = select(ShortTermMemoryDB).where(
            ShortTermMemoryDB.memory_id == memory_id,
            ShortTermMemoryDB.agent_id == self.agent_id,
        )
        
        result = await self.session.execute(query)
        entry = result.scalar_one_or_none()
        
        return self._to_model(entry) if entry else None
    
    async def promote_to_long_term(
        self,
        memory_id: UUID,
        long_term_ref: UUID,
    ) -> None:
        """Mark a memory as promoted to long-term.
        
        Args:
            memory_id: Memory to mark
            long_term_ref: ID of the long-term memory entry
        """
        await self.session.execute(
            update(ShortTermMemoryDB)
            .where(
                ShortTermMemoryDB.memory_id == memory_id,
                ShortTermMemoryDB.agent_id == self.agent_id,
            )
            .values(promoted_to=long_term_ref)
        )
        await self.session.commit()
    
    async def delete_expired(self) -> int:
        """Delete all expired memories.
        
        Returns:
            Number of deleted entries
        """
        result = await self.session.execute(
            delete(ShortTermMemoryDB).where(
                ShortTermMemoryDB.agent_id == self.agent_id,
                ShortTermMemoryDB.expires_at <= datetime.now(timezone.utc),
            )
        )
        await self.session.commit()
        return result.rowcount
    
    async def _count_entries(self) -> int:
        """Count current entries.
        
        Returns:
            Number of entries
        """
        result = await self.session.execute(
            select(func.count()).select_from(ShortTermMemoryDB).where(
                ShortTermMemoryDB.agent_id == self.agent_id,
                ShortTermMemoryDB.expires_at > datetime.now(timezone.utc),
            )
        )
        return result.scalar() or 0
    
    async def _evict_oldest(self, count: int = 1) -> int:
        """Evict oldest entries.
        
        Args:
            count: Number of entries to evict
            
        Returns:
            Number of evicted entries
        """
        # Find oldest entries
        subquery = (
            select(ShortTermMemoryDB.memory_id)
            .where(ShortTermMemoryDB.agent_id == self.agent_id)
            .order_by(ShortTermMemoryDB.created_at.asc())
            .limit(count)
        )
        
        result = await self.session.execute(
            delete(ShortTermMemoryDB).where(
                ShortTermMemoryDB.memory_id.in_(subquery)
            )
        )
        await self.session.commit()
        return result.rowcount
    
    def _to_model(self, db_entry: ShortTermMemoryDB) -> ShortTermMemoryEntry:
        """Convert DB model to dataclass.
        
        Args:
            db_entry: Database entry
            
        Returns:
            ShortTermMemoryEntry dataclass
        """
        return ShortTermMemoryEntry(
            memory_id=db_entry.memory_id,
            agent_id=db_entry.agent_id,
            memory_type=db_entry.memory_type,
            content=db_entry.content,
            significance=db_entry.significance,
            topic_keywords=db_entry.topic_keywords or [],
            created_at=db_entry.created_at,
            expires_at=db_entry.expires_at,
            project_id=db_entry.project_id,
            related_agents=db_entry.related_agents,
            confidence_at_time=db_entry.confidence_at_time,
            promoted_to=db_entry.promoted_to,
        )
    
    def _format_entries(
        self,
        entries: List[ShortTermMemoryDB],
        max_tokens: int,
    ) -> str:
        """Format entries for prompt context.
        
        Args:
            entries: Database entries
            max_tokens: Maximum tokens (chars / 4)
            
        Returns:
            Formatted string
        """
        if not entries:
            return ""
        
        lines = []
        char_count = 0
        max_chars = max_tokens * 4
        
        for entry in entries:
            line = f"[{entry.memory_type}] {entry.content}"
            if char_count + len(line) > max_chars:
                break
            lines.append(line)
            char_count += len(line) + 1  # +1 for newline
        
        return "\n".join(lines)

