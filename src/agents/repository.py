"""Agent repository for database operations."""

import json
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.agents.models import (
    AgentProfile,
    AgentProfileCreate,
    AgentProfileUpdate,
    CommunicationStyle,
    PersonalityMarkers,
    SkillSet,
    SocialMarkers,
)
from src.infrastructure.database import AgentProfileDB


def _serialize_json(value: dict | list) -> dict | list | str:
    """Serialize value for storage (handles SQLite text columns)."""
    return value  # SQLAlchemy handles JSONB natively


def _deserialize_json(value: dict | list | str) -> dict | list:
    """Deserialize value from storage (handles SQLite text columns)."""
    if isinstance(value, str):
        return json.loads(value)
    return value


class AgentRepository:
    """Database operations for agents."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, profile: AgentProfileCreate) -> AgentProfile:
        """Create a new agent."""
        db_agent = AgentProfileDB(
            name=profile.name,
            role=profile.role,
            title=profile.title,
            backstory_summary=profile.backstory_summary,
            years_experience=profile.years_experience,
            skills=profile.skills.model_dump(),
            personality_markers=profile.personality_markers.model_dump(),
            social_markers=profile.social_markers.model_dump(),
            communication_style=profile.communication_style.model_dump(),
            knowledge_domains=profile.knowledge_domains,
            knowledge_gaps=profile.knowledge_gaps,
        )

        self.session.add(db_agent)
        await self.session.commit()
        await self.session.refresh(db_agent)

        return self._to_model(db_agent)

    async def get(self, agent_id: UUID) -> Optional[AgentProfile]:
        """Get agent by ID."""
        result = await self.session.execute(
            select(AgentProfileDB)
            .where(AgentProfileDB.agent_id == agent_id)
            .where(AgentProfileDB.deleted_at.is_(None))
        )
        db_agent = result.scalar_one_or_none()

        if db_agent is None:
            return None

        return self._to_model(db_agent)

    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        role: Optional[str] = None,
    ) -> tuple[List[AgentProfile], int]:
        """List agents with optional filtering.
        
        Returns a tuple of (agents, total_count).
        """
        # Base query for filtering
        base_query = select(AgentProfileDB).where(AgentProfileDB.deleted_at.is_(None))

        if role:
            base_query = base_query.where(AgentProfileDB.role.ilike(f"%{role}%"))

        # Get total count
        count_query = select(func.count()).select_from(base_query.subquery())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar() or 0

        # Get paginated results
        query = base_query.offset(skip).limit(limit).order_by(AgentProfileDB.created_at.desc())
        result = await self.session.execute(query)

        agents = [self._to_model(db_agent) for db_agent in result.scalars()]
        return agents, total

    async def update(
        self,
        agent_id: UUID,
        updates: AgentProfileUpdate,
    ) -> Optional[AgentProfile]:
        """Update agent profile."""
        # Get existing agent first
        existing = await self.get(agent_id)
        if existing is None:
            return None

        # Build update dict, excluding None values
        update_data = updates.model_dump(exclude_unset=True)
        
        # Convert nested models to dicts for JSONB columns
        if "skills" in update_data and update_data["skills"] is not None:
            update_data["skills"] = updates.skills.model_dump()
        if "personality_markers" in update_data and update_data["personality_markers"] is not None:
            update_data["personality_markers"] = updates.personality_markers.model_dump()
        if "social_markers" in update_data and update_data["social_markers"] is not None:
            update_data["social_markers"] = updates.social_markers.model_dump()
        if "communication_style" in update_data and update_data["communication_style"] is not None:
            update_data["communication_style"] = updates.communication_style.model_dump()

        update_data["updated_at"] = datetime.utcnow()

        await self.session.execute(
            update(AgentProfileDB)
            .where(AgentProfileDB.agent_id == agent_id)
            .where(AgentProfileDB.deleted_at.is_(None))
            .values(**update_data)
        )
        await self.session.commit()

        return await self.get(agent_id)

    async def delete(self, agent_id: UUID) -> bool:
        """Soft delete agent."""
        result = await self.session.execute(
            update(AgentProfileDB)
            .where(AgentProfileDB.agent_id == agent_id)
            .where(AgentProfileDB.deleted_at.is_(None))
            .values(deleted_at=datetime.utcnow())
        )
        await self.session.commit()

        return result.rowcount > 0

    def _to_model(self, db_agent: AgentProfileDB) -> AgentProfile:
        """Convert DB model to Pydantic model."""
        # Handle potential JSON string from SQLite
        skills_data = _deserialize_json(db_agent.skills)
        personality_data = _deserialize_json(db_agent.personality_markers)
        social_data = _deserialize_json(db_agent.social_markers)
        comm_data = _deserialize_json(db_agent.communication_style)
        domains = _deserialize_json(db_agent.knowledge_domains) if db_agent.knowledge_domains else []
        gaps = _deserialize_json(db_agent.knowledge_gaps) if db_agent.knowledge_gaps else []

        return AgentProfile(
            agent_id=db_agent.agent_id,
            name=db_agent.name,
            role=db_agent.role,
            title=db_agent.title,
            backstory_summary=db_agent.backstory_summary,
            years_experience=db_agent.years_experience,
            skills=SkillSet(**skills_data),
            personality_markers=PersonalityMarkers(**personality_data),
            social_markers=SocialMarkers(**social_data),
            communication_style=CommunicationStyle(**comm_data),
            knowledge_domains=domains,
            knowledge_gaps=gaps,
            created_at=db_agent.created_at,
            updated_at=db_agent.updated_at,
        )
