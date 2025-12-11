"""Initial agent_profiles table.

Revision ID: 001_initial
Revises: 
Create Date: 2024-12-02 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create agent_profiles table
    op.create_table(
        "agent_profiles",
        sa.Column(
            "agent_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        # Identity
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("role", sa.String(100), nullable=False),
        sa.Column("title", sa.String(100), nullable=True),
        sa.Column("backstory_summary", sa.Text(), nullable=False),
        sa.Column("years_experience", sa.Integer(), nullable=True),
        # Skills and personality (JSONB for flexibility)
        sa.Column(
            "skills",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "personality_markers",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "social_markers",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "communication_style",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="{}",
        ),
        # Knowledge
        sa.Column(
            "knowledge_domains",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            server_default="[]",
        ),
        sa.Column(
            "knowledge_gaps",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            server_default="[]",
        ),
        # Timestamps
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
    )

    # Create indexes
    op.create_index(
        "idx_agent_profiles_name",
        "agent_profiles",
        ["name"],
        postgresql_where=sa.text("deleted_at IS NULL"),
    )
    op.create_index(
        "idx_agent_profiles_role",
        "agent_profiles",
        ["role"],
        postgresql_where=sa.text("deleted_at IS NULL"),
    )
    op.create_index(
        "idx_agent_profiles_deleted",
        "agent_profiles",
        ["deleted_at"],
    )


def downgrade() -> None:
    # Drop indexes
    op.drop_index("idx_agent_profiles_deleted", table_name="agent_profiles")
    op.drop_index("idx_agent_profiles_role", table_name="agent_profiles")
    op.drop_index("idx_agent_profiles_name", table_name="agent_profiles")

    # Drop table
    op.drop_table("agent_profiles")

