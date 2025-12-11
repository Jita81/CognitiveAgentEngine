"""Database models for memory architecture.

SQLAlchemy models for short-term and long-term memory storage.

Phase 6 of the Cognitive Agent Engine.
"""

from datetime import datetime, timedelta, timezone
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    CheckConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database import Base


class ShortTermMemoryDB(Base):
    """Database model for short-term memory entries.
    
    Tier 2: Recent significant events with 7-day TTL.
    """
    
    __tablename__ = "short_term_memories"
    
    # Primary key
    memory_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    
    # Foreign key to agent
    agent_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("agent_profiles.agent_id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Content
    memory_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )  # observation, decision, interaction, insight
    
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    
    significance: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    
    # Context
    project_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=True,
    )
    
    related_agents: Mapped[Optional[list]] = mapped_column(
        JSONB,
        nullable=True,
    )  # Array of agent IDs involved
    
    topic_keywords: Mapped[Optional[list]] = mapped_column(
        JSONB,
        nullable=True,
    )  # For querying
    
    # Emotional context
    confidence_at_time: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )
    
    # Lifecycle
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    
    promoted_to: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=True,
    )  # Reference to long-term memory if promoted
    
    # Table constraints and indexes
    __table_args__ = (
        CheckConstraint(
            "significance >= 0 AND significance <= 1",
            name="check_stm_significance",
        ),
        Index("idx_stm_agent", agent_id),
        Index("idx_stm_expires", expires_at),
        Index("idx_stm_project", project_id),
        Index("idx_stm_significance", significance.desc()),
        Index("idx_stm_created", created_at.desc()),
    )


class ProjectChapterDB(Base):
    """Database model for long-term memory (project chapters).
    
    Tier 3: Permanent records of significant project experiences.
    """
    
    __tablename__ = "project_chapters"
    
    # Primary key
    chapter_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    
    # Foreign key to agent
    agent_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("agent_profiles.agent_id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Project reference
    project_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=False,
    )
    
    # Content
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    
    summary: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    
    role_in_project: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )
    
    # Timeline
    start_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    
    end_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    
    # Outcome
    outcome: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )  # success, partial_success, failure, ongoing
    
    significance: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    
    lessons_learned: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    
    # Participants
    collaborators: Mapped[Optional[list]] = mapped_column(
        JSONB,
        nullable=True,
    )  # Array of agent IDs
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    
    # Table constraints and indexes
    __table_args__ = (
        CheckConstraint(
            "significance >= 0 AND significance <= 1",
            name="check_chapter_significance",
        ),
        Index("idx_chapters_agent", agent_id),
        Index("idx_chapters_project", project_id),
        Index("idx_chapters_outcome", outcome),
        Index("idx_chapters_significance", significance.desc()),
    )


# Constants for default TTL
DEFAULT_SHORT_TERM_TTL_DAYS = 7


def get_default_expiry() -> datetime:
    """Get default expiry time for short-term memories.
    
    Returns:
        Expiry datetime (7 days from now)
    """
    return datetime.now(timezone.utc) + timedelta(days=DEFAULT_SHORT_TERM_TTL_DAYS)

