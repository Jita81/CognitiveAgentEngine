"""Memory Architecture module (Phase 6).

This module provides a 4-tier memory system matching human memory patterns:

- **Tier 1: Working Memory** - In-process, session-only, fastest access
- **Tier 2: Short-Term Memory** - PostgreSQL-backed, 7-day TTL
- **Tier 3: Long-Term Memory** - PostgreSQL-backed, permanent storage
- **Tier 4: Pattern Library** - Learned patterns (Phase 8)

Each cognitive tier has access to different memory depths:
- REFLEX: Working memory only
- REACTIVE: Working + recent short-term
- DELIBERATE: Working + indexed short-term  
- ANALYTICAL: All tiers
- COMPREHENSIVE: All tiers + patterns

Example usage:
    from src.memory import (
        MemoryManager,
        WorkingMemory,
        ShortTermMemory,
        LongTermMemory,
        create_memory_manager,
    )
    
    # Create memory manager for an agent
    manager = await create_memory_manager(session, agent_id)
    
    # Get context appropriate for cognitive tier
    context = await manager.get_context_for_tier(CognitiveTier.DELIBERATE, topic="API design")
    
    # Record a significant event
    await manager.record_significant_event(
        content="Decided to use event sourcing for state management",
        memory_type="decision",
        significance=0.8,
        topic="architecture",
    )
"""

# Working Memory (Tier 1)
from src.memory.working import (
    WorkingMemory,
    ConversationTurn,
)

# Short-Term Memory (Tier 2)
from src.memory.short_term import (
    ShortTermMemory,
    ShortTermMemoryEntry,
)

# Long-Term Memory (Tier 3)
from src.memory.long_term import (
    LongTermMemory,
    ProjectChapter,
)

# Database Models
from src.memory.models import (
    ShortTermMemoryDB,
    ProjectChapterDB,
    DEFAULT_SHORT_TERM_TTL_DAYS,
    get_default_expiry,
)

# Memory Manager
from src.memory.manager import (
    MemoryManager,
    create_memory_manager,
)

__all__ = [
    # Working Memory (Tier 1)
    "WorkingMemory",
    "ConversationTurn",
    # Short-Term Memory (Tier 2)
    "ShortTermMemory",
    "ShortTermMemoryEntry",
    # Long-Term Memory (Tier 3)
    "LongTermMemory",
    "ProjectChapter",
    # Database Models
    "ShortTermMemoryDB",
    "ProjectChapterDB",
    "DEFAULT_SHORT_TERM_TTL_DAYS",
    "get_default_expiry",
    # Memory Manager
    "MemoryManager",
    "create_memory_manager",
]
