"""Agent profile Pydantic models with validation."""

from datetime import datetime
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator


class CommunicationStyle(BaseModel):
    """How the agent communicates."""

    vocabulary_level: str = Field(
        default="moderate",
        description="Language complexity level",
    )
    sentence_structure: str = Field(
        default="moderate",
        description="Sentence complexity",
    )
    formality: str = Field(
        default="professional",
        description="Communication formality",
    )
    uses_analogies: bool = Field(default=True)
    uses_examples: bool = Field(default=True)
    asks_clarifying_questions: bool = Field(default=True)
    summarizes_frequently: bool = Field(default=False)
    verbal_tics: List[str] = Field(default_factory=list)

    @field_validator("vocabulary_level")
    @classmethod
    def validate_vocabulary_level(cls, v: str) -> str:
        valid = {"simple", "moderate", "technical", "academic"}
        if v not in valid:
            raise ValueError(f"vocabulary_level must be one of {valid}")
        return v

    @field_validator("sentence_structure")
    @classmethod
    def validate_sentence_structure(cls, v: str) -> str:
        valid = {"terse", "moderate", "elaborate"}
        if v not in valid:
            raise ValueError(f"sentence_structure must be one of {valid}")
        return v

    @field_validator("formality")
    @classmethod
    def validate_formality(cls, v: str) -> str:
        valid = {"casual", "professional", "formal"}
        if v not in valid:
            raise ValueError(f"formality must be one of {valid}")
        return v


class SkillSet(BaseModel):
    """Agent's skills with validation."""

    # All skills are 0-10
    technical: Dict[str, int] = Field(default_factory=dict)
    domains: Dict[str, int] = Field(default_factory=dict)
    soft_skills: Dict[str, int] = Field(default_factory=dict)

    @field_validator("technical", "domains", "soft_skills", mode="before")
    @classmethod
    def validate_skill_range(cls, v: Dict[str, int]) -> Dict[str, int]:
        if not isinstance(v, dict):
            return v
        for skill, level in v.items():
            if not isinstance(level, int):
                raise ValueError(f"Skill level for '{skill}' must be an integer")
            if not 0 <= level <= 10:
                raise ValueError(f"Skill '{skill}' must be 0-10, got {level}")
        return v

    def get_top_skills(self, n: int = 5) -> List[Tuple[str, int]]:
        """Get top N skills across all categories."""
        all_skills = {**self.technical, **self.domains, **self.soft_skills}
        sorted_skills = sorted(all_skills.items(), key=lambda x: -x[1])
        return sorted_skills[:n]

    def get_relevance_score(self, keywords: List[str]) -> float:
        """Calculate relevance to keywords based on skill overlap."""
        if not keywords:
            return 0.0

        all_skills = {**self.technical, **self.domains, **self.soft_skills}

        matched = []
        for keyword in keywords:
            kw_lower = keyword.lower().replace(" ", "_").replace("-", "_")
            for skill, level in all_skills.items():
                skill_lower = skill.lower()
                if kw_lower in skill_lower or skill_lower in kw_lower:
                    matched.append(level)
                    break

        if not matched:
            return 0.0
        return sum(matched) / (len(keywords) * 10)

    def get_all_skills(self) -> Dict[str, int]:
        """Get all skills as a flat dictionary."""
        return {**self.technical, **self.domains, **self.soft_skills}


class PersonalityMarkers(BaseModel):
    """Core personality traits (0-10 scale)."""

    # Big Five
    openness: int = Field(default=5, ge=0, le=10, description="Openness to new ideas")
    conscientiousness: int = Field(default=5, ge=0, le=10, description="Attention to detail")
    extraversion: int = Field(default=5, ge=0, le=10, description="Energy from social interaction")
    agreeableness: int = Field(default=5, ge=0, le=10, description="Cooperative vs competitive")
    neuroticism: int = Field(default=5, ge=0, le=10, description="Emotional stability (lower = stable)")

    # Professional traits
    perfectionism: int = Field(default=5, ge=0, le=10, description="Standards for work quality")
    pragmatism: int = Field(default=5, ge=0, le=10, description="Practical vs idealistic")
    risk_tolerance: int = Field(default=5, ge=0, le=10, description="Comfort with uncertainty")


class SocialMarkers(BaseModel):
    """Social behavior traits (0-10 scale)."""

    confidence: int = Field(default=5, ge=0, le=10, description="How readily shares views")
    assertiveness: int = Field(default=5, ge=0, le=10, description="How strongly pushes position")
    deference: int = Field(default=5, ge=0, le=10, description="How much yields to others")
    curiosity: int = Field(default=5, ge=0, le=10, description="How much asks questions")
    social_calibration: int = Field(default=5, ge=0, le=10, description="How well reads rooms")
    status_sensitivity: int = Field(default=5, ge=0, le=10, description="How much hierarchy affects behavior")
    facilitation_instinct: int = Field(default=5, ge=0, le=10, description="Tendency to help others contribute")
    comfort_in_spotlight: int = Field(default=5, ge=0, le=10, description="Comfort speaking to groups")
    comfort_with_conflict: int = Field(default=5, ge=0, le=10, description="Willingness to disagree")


class AgentProfileCreate(BaseModel):
    """Request model for creating an agent."""

    name: str = Field(..., min_length=1, max_length=100, description="Agent name")
    role: str = Field(..., min_length=1, max_length=100, description="Professional role")
    title: Optional[str] = Field(None, max_length=100, description="Professional title")
    backstory_summary: str = Field(
        ...,
        min_length=50,
        max_length=1000,
        description="Background summary (50-1000 chars)",
    )
    years_experience: Optional[int] = Field(
        None,
        ge=0,
        le=50,
        description="Years of experience (0-50)",
    )

    skills: SkillSet = Field(default_factory=SkillSet)
    personality_markers: PersonalityMarkers = Field(default_factory=PersonalityMarkers)
    social_markers: SocialMarkers = Field(default_factory=SocialMarkers)
    communication_style: CommunicationStyle = Field(default_factory=CommunicationStyle)

    knowledge_domains: List[str] = Field(default_factory=list)
    knowledge_gaps: List[str] = Field(default_factory=list)


class AgentProfileUpdate(BaseModel):
    """Request model for updating an agent (all fields optional)."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    role: Optional[str] = Field(None, min_length=1, max_length=100)
    title: Optional[str] = Field(None, max_length=100)
    backstory_summary: Optional[str] = Field(None, min_length=50, max_length=1000)
    years_experience: Optional[int] = Field(None, ge=0, le=50)

    skills: Optional[SkillSet] = None
    personality_markers: Optional[PersonalityMarkers] = None
    social_markers: Optional[SocialMarkers] = None
    communication_style: Optional[CommunicationStyle] = None

    knowledge_domains: Optional[List[str]] = None
    knowledge_gaps: Optional[List[str]] = None

    @model_validator(mode="after")
    def check_at_least_one_field(self) -> "AgentProfileUpdate":
        """Ensure at least one field is provided for update."""
        values = self.model_dump(exclude_unset=True)
        if not values:
            raise ValueError("At least one field must be provided for update")
        return self


class AgentProfile(BaseModel):
    """Full agent profile with ID and timestamps."""

    agent_id: UUID
    name: str
    role: str
    title: Optional[str] = None
    backstory_summary: str
    years_experience: Optional[int] = None

    skills: SkillSet
    personality_markers: PersonalityMarkers
    social_markers: SocialMarkers
    communication_style: CommunicationStyle

    knowledge_domains: List[str] = Field(default_factory=list)
    knowledge_gaps: List[str] = Field(default_factory=list)

    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AgentProfileList(BaseModel):
    """Response model for listing agents."""

    agents: List[AgentProfile]
    total: int
    skip: int
    limit: int
