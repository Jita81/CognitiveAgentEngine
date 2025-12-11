"""Add memory tables for Phase 6.

Revision ID: 20241211_000000
Revises: 20241202_000000
Create Date: 2024-12-11

Creates:
- short_term_memories table (Tier 2)
- project_chapters table (Tier 3)
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "20241211_000000"
down_revision: Union[str, None] = "20241202_000000"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create memory tables."""
    
    # Create short_term_memories table
    op.create_table(
        "short_term_memories",
        sa.Column("memory_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "agent_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("agent_profiles.agent_id", ondelete="CASCADE"),
            nullable=False,
        ),
        # Content
        sa.Column("memory_type", sa.String(50), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("significance", sa.Float, nullable=False),
        # Context
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("related_agents", postgresql.JSONB, nullable=True),
        sa.Column("topic_keywords", postgresql.JSONB, nullable=True),
        # Emotional context
        sa.Column("confidence_at_time", sa.String(20), nullable=True),
        # Lifecycle
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("promoted_to", postgresql.UUID(as_uuid=True), nullable=True),
        # Constraints
        sa.CheckConstraint(
            "significance >= 0 AND significance <= 1",
            name="check_stm_significance",
        ),
    )
    
    # Create indexes for short_term_memories
    op.create_index("idx_stm_agent", "short_term_memories", ["agent_id"])
    op.create_index("idx_stm_expires", "short_term_memories", ["expires_at"])
    op.create_index("idx_stm_project", "short_term_memories", ["project_id"])
    op.create_index(
        "idx_stm_significance",
        "short_term_memories",
        [sa.text("significance DESC")],
    )
    op.create_index(
        "idx_stm_created",
        "short_term_memories",
        [sa.text("created_at DESC")],
    )
    
    # Create project_chapters table
    op.create_table(
        "project_chapters",
        sa.Column("chapter_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "agent_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("agent_profiles.agent_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        # Content
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("summary", sa.Text, nullable=False),
        sa.Column("role_in_project", sa.String(100), nullable=True),
        # Timeline
        sa.Column("start_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_date", sa.DateTime(timezone=True), nullable=True),
        # Outcome
        sa.Column("outcome", sa.String(50), nullable=True),
        sa.Column("significance", sa.Float, nullable=False),
        sa.Column("lessons_learned", sa.Text, nullable=True),
        # Participants
        sa.Column("collaborators", postgresql.JSONB, nullable=True),
        # Metadata
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        # Constraints
        sa.CheckConstraint(
            "significance >= 0 AND significance <= 1",
            name="check_chapter_significance",
        ),
    )
    
    # Create indexes for project_chapters
    op.create_index("idx_chapters_agent", "project_chapters", ["agent_id"])
    op.create_index("idx_chapters_project", "project_chapters", ["project_id"])
    op.create_index("idx_chapters_outcome", "project_chapters", ["outcome"])
    op.create_index(
        "idx_chapters_significance",
        "project_chapters",
        [sa.text("significance DESC")],
    )


def downgrade() -> None:
    """Drop memory tables."""
    
    # Drop indexes first
    op.drop_index("idx_chapters_significance", table_name="project_chapters")
    op.drop_index("idx_chapters_outcome", table_name="project_chapters")
    op.drop_index("idx_chapters_project", table_name="project_chapters")
    op.drop_index("idx_chapters_agent", table_name="project_chapters")
    
    op.drop_index("idx_stm_created", table_name="short_term_memories")
    op.drop_index("idx_stm_significance", table_name="short_term_memories")
    op.drop_index("idx_stm_project", table_name="short_term_memories")
    op.drop_index("idx_stm_expires", table_name="short_term_memories")
    op.drop_index("idx_stm_agent", table_name="short_term_memories")
    
    # Drop tables
    op.drop_table("project_chapters")
    op.drop_table("short_term_memories")

