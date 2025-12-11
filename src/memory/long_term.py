"""Long-Term Memory - Tier 3 of the memory architecture.

PostgreSQL-backed permanent records of significant project experiences.
These are project chapters that capture lessons learned and outcomes.

Phase 6 of the Cognitive Agent Engine.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.memory.models import ProjectChapterDB


@dataclass
class ProjectChapter:
    """A chapter of project history.
    
    Represents a significant experience from a project that
    the agent has worked on.
    
    Attributes:
        chapter_id: Unique identifier
        agent_id: Agent this memory belongs to
        project_id: Project this chapter belongs to
        title: Chapter title
        summary: Detailed summary of the experience
        role_in_project: Agent's role in this project
        start_date: When the project/chapter started
        end_date: When the project/chapter ended (None if ongoing)
        outcome: Result (success, partial_success, failure, ongoing)
        significance: Importance score (0.0-1.0)
        lessons_learned: Key lessons from this experience
        collaborators: List of agent IDs who worked together
        created_at: When this record was created
    """
    
    chapter_id: UUID
    agent_id: UUID
    project_id: UUID
    title: str
    summary: str
    role_in_project: Optional[str]
    start_date: datetime
    end_date: Optional[datetime]
    outcome: Optional[str]
    significance: float
    lessons_learned: Optional[str]
    collaborators: Optional[List[str]]
    created_at: datetime
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "chapter_id": str(self.chapter_id),
            "agent_id": str(self.agent_id),
            "project_id": str(self.project_id),
            "title": self.title,
            "summary": self.summary,
            "role_in_project": self.role_in_project,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "outcome": self.outcome,
            "significance": self.significance,
            "lessons_learned": self.lessons_learned,
            "collaborators": self.collaborators,
            "created_at": self.created_at.isoformat(),
        }
    
    @property
    def is_ongoing(self) -> bool:
        """Check if this project chapter is still ongoing.
        
        Returns:
            True if ongoing (no end date or outcome is 'ongoing')
        """
        return self.end_date is None or self.outcome == "ongoing"
    
    @property
    def was_successful(self) -> bool:
        """Check if this project was successful.
        
        Returns:
            True if outcome is 'success' or 'partial_success'
        """
        return self.outcome in ("success", "partial_success")


class LongTermMemory:
    """Tier 3: Permanent records of significant experiences.
    
    PostgreSQL-backed, permanent storage for project chapters
    and significant career milestones.
    
    Attributes:
        session: Database session
        agent_id: Agent this memory belongs to
    """
    
    def __init__(self, session: AsyncSession, agent_id: UUID):
        """Initialize long-term memory.
        
        Args:
            session: Database session
            agent_id: Agent ID
        """
        self.session = session
        self.agent_id = agent_id
    
    async def add_chapter(
        self,
        project_id: UUID,
        title: str,
        summary: str,
        role: Optional[str] = None,
        start_date: Optional[datetime] = None,
        outcome: Optional[str] = None,
        significance: float = 0.5,
        lessons: Optional[str] = None,
        collaborators: Optional[List[str]] = None,
    ) -> ProjectChapter:
        """Add a project chapter.
        
        Args:
            project_id: Project ID
            title: Chapter title
            summary: Detailed summary
            role: Agent's role in the project
            start_date: When project started (default: now)
            outcome: Result (success, partial_success, failure, ongoing)
            significance: Importance score (0.0-1.0)
            lessons: Lessons learned
            collaborators: List of collaborator agent IDs
            
        Returns:
            Created ProjectChapter
        """
        db_entry = ProjectChapterDB(
            chapter_id=uuid4(),
            agent_id=self.agent_id,
            project_id=project_id,
            title=title,
            summary=summary,
            role_in_project=role,
            start_date=start_date or datetime.now(timezone.utc),
            outcome=outcome or "ongoing",
            significance=max(0.0, min(1.0, significance)),
            lessons_learned=lessons,
            collaborators=collaborators or [],
            created_at=datetime.now(timezone.utc),
        )
        
        self.session.add(db_entry)
        await self.session.commit()
        await self.session.refresh(db_entry)
        
        return self._to_model(db_entry)
    
    async def complete_chapter(
        self,
        chapter_id: UUID,
        outcome: str,
        lessons: Optional[str] = None,
        end_date: Optional[datetime] = None,
    ) -> Optional[ProjectChapter]:
        """Mark a chapter as complete.
        
        Args:
            chapter_id: Chapter to complete
            outcome: Final outcome (success, partial_success, failure)
            lessons: Lessons learned (updates existing)
            end_date: When completed (default: now)
            
        Returns:
            Updated ProjectChapter or None if not found
        """
        update_values = {
            "outcome": outcome,
            "end_date": end_date or datetime.now(timezone.utc),
        }
        
        if lessons:
            update_values["lessons_learned"] = lessons
        
        await self.session.execute(
            update(ProjectChapterDB)
            .where(
                ProjectChapterDB.chapter_id == chapter_id,
                ProjectChapterDB.agent_id == self.agent_id,
            )
            .values(**update_values)
        )
        await self.session.commit()
        
        return await self.get_by_id(chapter_id)
    
    async def search(
        self,
        topic: Optional[str] = None,
        outcome: Optional[str] = None,
        min_significance: float = 0.0,
        max_results: int = 5,
        max_tokens: int = 500,
    ) -> str:
        """Search long-term memories.
        
        Args:
            topic: Topic to search for in title/summary
            outcome: Filter by outcome
            min_significance: Minimum significance score
            max_results: Maximum entries to return
            max_tokens: Maximum tokens for formatted output
            
        Returns:
            Formatted memory string for prompt context
        """
        query = select(ProjectChapterDB).where(
            ProjectChapterDB.agent_id == self.agent_id,
            ProjectChapterDB.significance >= min_significance,
        )
        
        if topic:
            query = query.where(
                ProjectChapterDB.title.ilike(f"%{topic}%") |
                ProjectChapterDB.summary.ilike(f"%{topic}%")
            )
        
        if outcome:
            query = query.where(ProjectChapterDB.outcome == outcome)
        
        query = query.order_by(
            ProjectChapterDB.significance.desc(),
        ).limit(max_results)
        
        result = await self.session.execute(query)
        chapters = result.scalars().all()
        
        return self._format_chapters(chapters, max_tokens)
    
    async def search_chapters(
        self,
        topic: Optional[str] = None,
        outcome: Optional[str] = None,
        project_id: Optional[UUID] = None,
        min_significance: float = 0.0,
        max_results: int = 10,
    ) -> List[ProjectChapter]:
        """Search chapters and return as objects.
        
        Args:
            topic: Topic to search for
            outcome: Filter by outcome
            project_id: Filter by project
            min_significance: Minimum significance
            max_results: Maximum results
            
        Returns:
            List of ProjectChapter objects
        """
        query = select(ProjectChapterDB).where(
            ProjectChapterDB.agent_id == self.agent_id,
            ProjectChapterDB.significance >= min_significance,
        )
        
        if topic:
            query = query.where(
                ProjectChapterDB.title.ilike(f"%{topic}%") |
                ProjectChapterDB.summary.ilike(f"%{topic}%")
            )
        
        if outcome:
            query = query.where(ProjectChapterDB.outcome == outcome)
        
        if project_id:
            query = query.where(ProjectChapterDB.project_id == project_id)
        
        query = query.order_by(
            ProjectChapterDB.significance.desc(),
            ProjectChapterDB.start_date.desc(),
        ).limit(max_results)
        
        result = await self.session.execute(query)
        chapters = result.scalars().all()
        
        return [self._to_model(ch) for ch in chapters]
    
    async def get_by_id(self, chapter_id: UUID) -> Optional[ProjectChapter]:
        """Get a chapter by ID.
        
        Args:
            chapter_id: Chapter ID
            
        Returns:
            ProjectChapter or None
        """
        query = select(ProjectChapterDB).where(
            ProjectChapterDB.chapter_id == chapter_id,
            ProjectChapterDB.agent_id == self.agent_id,
        )
        
        result = await self.session.execute(query)
        chapter = result.scalar_one_or_none()
        
        return self._to_model(chapter) if chapter else None
    
    async def get_by_project(
        self,
        project_id: UUID,
        max_results: int = 10,
    ) -> List[ProjectChapter]:
        """Get all chapters for a project.
        
        Args:
            project_id: Project ID
            max_results: Maximum chapters to return
            
        Returns:
            List of ProjectChapter objects
        """
        query = select(ProjectChapterDB).where(
            ProjectChapterDB.agent_id == self.agent_id,
            ProjectChapterDB.project_id == project_id,
        ).order_by(
            ProjectChapterDB.start_date.desc(),
        ).limit(max_results)
        
        result = await self.session.execute(query)
        chapters = result.scalars().all()
        
        return [self._to_model(ch) for ch in chapters]
    
    async def get_successful_patterns(
        self,
        max_results: int = 5,
        max_tokens: int = 400,
    ) -> str:
        """Get lessons from successful projects.
        
        Args:
            max_results: Maximum chapters to include
            max_tokens: Maximum tokens for formatted output
            
        Returns:
            Formatted string of successful patterns
        """
        query = select(ProjectChapterDB).where(
            ProjectChapterDB.agent_id == self.agent_id,
            ProjectChapterDB.outcome.in_(["success", "partial_success"]),
            ProjectChapterDB.lessons_learned.isnot(None),
        ).order_by(
            ProjectChapterDB.significance.desc(),
        ).limit(max_results)
        
        result = await self.session.execute(query)
        chapters = result.scalars().all()
        
        return self._format_lessons(chapters, max_tokens)
    
    async def get_failure_warnings(
        self,
        max_results: int = 3,
        max_tokens: int = 300,
    ) -> str:
        """Get warnings from failed projects.
        
        Args:
            max_results: Maximum chapters to include
            max_tokens: Maximum tokens for formatted output
            
        Returns:
            Formatted string of failure warnings
        """
        query = select(ProjectChapterDB).where(
            ProjectChapterDB.agent_id == self.agent_id,
            ProjectChapterDB.outcome == "failure",
            ProjectChapterDB.lessons_learned.isnot(None),
        ).order_by(
            ProjectChapterDB.significance.desc(),
        ).limit(max_results)
        
        result = await self.session.execute(query)
        chapters = result.scalars().all()
        
        if not chapters:
            return ""
        
        lines = []
        char_count = 0
        max_chars = max_tokens * 4
        
        for chapter in chapters:
            warning = f"⚠️ {chapter.title}: {chapter.lessons_learned}"
            if char_count + len(warning) > max_chars:
                break
            lines.append(warning)
            char_count += len(warning) + 1
        
        return "\n".join(lines)
    
    def _to_model(self, db_entry: ProjectChapterDB) -> ProjectChapter:
        """Convert DB model to dataclass.
        
        Args:
            db_entry: Database entry
            
        Returns:
            ProjectChapter dataclass
        """
        return ProjectChapter(
            chapter_id=db_entry.chapter_id,
            agent_id=db_entry.agent_id,
            project_id=db_entry.project_id,
            title=db_entry.title,
            summary=db_entry.summary,
            role_in_project=db_entry.role_in_project,
            start_date=db_entry.start_date,
            end_date=db_entry.end_date,
            outcome=db_entry.outcome,
            significance=db_entry.significance,
            lessons_learned=db_entry.lessons_learned,
            collaborators=db_entry.collaborators,
            created_at=db_entry.created_at,
        )
    
    def _format_chapters(
        self,
        chapters: List[ProjectChapterDB],
        max_tokens: int,
    ) -> str:
        """Format chapters for prompt context.
        
        Args:
            chapters: Database entries
            max_tokens: Maximum tokens (chars / 4)
            
        Returns:
            Formatted string
        """
        if not chapters:
            return ""
        
        sections = []
        char_count = 0
        max_chars = max_tokens * 4
        
        for chapter in chapters:
            section = f"""Project: {chapter.title}
Role: {chapter.role_in_project or 'Contributor'}
Outcome: {chapter.outcome or 'ongoing'}
Lessons: {chapter.lessons_learned or 'None recorded'}""".strip()
            
            if char_count + len(section) > max_chars:
                break
            sections.append(section)
            char_count += len(section) + 2  # +2 for paragraph break
        
        return "\n\n".join(sections)
    
    def _format_lessons(
        self,
        chapters: List[ProjectChapterDB],
        max_tokens: int,
    ) -> str:
        """Format lessons learned for prompt context.
        
        Args:
            chapters: Database entries
            max_tokens: Maximum tokens
            
        Returns:
            Formatted string of lessons
        """
        if not chapters:
            return ""
        
        lines = []
        char_count = 0
        max_chars = max_tokens * 4
        
        for chapter in chapters:
            if chapter.lessons_learned:
                lesson = f"• {chapter.title}: {chapter.lessons_learned}"
                if char_count + len(lesson) > max_chars:
                    break
                lines.append(lesson)
                char_count += len(lesson) + 1
        
        return "\n".join(lines)

