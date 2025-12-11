"""Cognitive processing models.

This module defines the core data models for cognitive processing:
- Thought: A single unit of cognition with type, confidence, completeness
- CognitiveResult: The result of processing a stimulus through cognitive tiers
- StimulusInput: Input model for cognitive processing requests
"""

from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator

from src.cognitive.tiers import CognitiveTier


class ThoughtType(Enum):
    """Types of thoughts an agent can have."""

    INSIGHT = "insight"  # A realization or understanding
    CONCERN = "concern"  # A worry or risk identification
    QUESTION = "question"  # Something to ask or clarify
    OBSERVATION = "observation"  # Noticing something
    PLAN = "plan"  # An intention or course of action
    REACTION = "reaction"  # An immediate response


class Thought(BaseModel):
    """A single unit of cognition.
    
    Represents one discrete thought produced by cognitive processing,
    with metadata about its quality and lifecycle.
    """

    thought_id: UUID = Field(default_factory=uuid4, description="Unique thought identifier")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When the thought was created",
    )
    tier: CognitiveTier = Field(..., description="Cognitive tier that produced this thought")
    content: str = Field(..., min_length=1, description="The thought content")
    thought_type: ThoughtType = Field(..., description="Classification of the thought")
    trigger: str = Field(..., description="What triggered this thought (purpose)")
    
    # Quality metrics (0.0 to 1.0)
    confidence: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="How confident the agent is in this thought",
    )
    completeness: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="How complete/developed this thought is",
    )
    
    # Lifecycle tracking
    externalized: bool = Field(
        default=False,
        description="Whether this thought has been spoken/shared",
    )
    externalized_at: Optional[datetime] = Field(
        default=None,
        description="When this thought was externalized (if ever)",
    )
    still_relevant: bool = Field(
        default=True,
        description="Whether this thought is still relevant",
    )
    superseded_by: Optional[UUID] = Field(
        default=None,
        description="ID of thought that superseded this one (e.g., synthesis)",
    )
    
    # Optional references
    related_thought_ids: List[UUID] = Field(
        default_factory=list,
        description="IDs of related thoughts",
    )

    model_config = {"from_attributes": True}

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
        return {
            "thought_id": str(self.thought_id),
            "created_at": self.created_at.isoformat(),
            "tier": self.tier.name,
            "content": self.content,
            "thought_type": self.thought_type.value,
            "trigger": self.trigger,
            "confidence": self.confidence,
            "completeness": self.completeness,
            "externalized": self.externalized,
            "externalized_at": self.externalized_at.isoformat() if self.externalized_at else None,
            "still_relevant": self.still_relevant,
            "superseded_by": str(self.superseded_by) if self.superseded_by else None,
            "related_thought_ids": [str(tid) for tid in self.related_thought_ids],
        }


class CognitiveResult(BaseModel):
    """Result of cognitive processing.
    
    Contains all thoughts produced from processing a stimulus,
    along with metadata about the processing itself.
    """

    thoughts: List[Thought] = Field(
        default_factory=list,
        description="All thoughts produced during processing",
    )
    primary_thought: Optional[Thought] = Field(
        None,
        description="The most significant thought from processing",
    )
    processing_time_ms: float = Field(
        default=0.0,
        ge=0.0,
        description="Total processing time in milliseconds",
    )
    tiers_used: List[CognitiveTier] = Field(
        default_factory=list,
        description="Cognitive tiers that were invoked",
    )
    
    # Additional metadata
    agent_id: Optional[UUID] = Field(None, description="ID of the agent that processed")
    stimulus_id: Optional[UUID] = Field(None, description="ID of the stimulus processed")

    model_config = {"from_attributes": True}

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
        return {
            "thoughts": [t.to_dict() for t in self.thoughts],
            "primary_thought": self.primary_thought.to_dict() if self.primary_thought else None,
            "processing_time_ms": self.processing_time_ms,
            "tiers_used": [t.name for t in self.tiers_used],
            "agent_id": str(self.agent_id) if self.agent_id else None,
            "stimulus_id": str(self.stimulus_id) if self.stimulus_id else None,
            "thought_count": len(self.thoughts),
        }

    @property
    def thought_count(self) -> int:
        """Get number of thoughts produced."""
        return len(self.thoughts)

    @property
    def avg_confidence(self) -> float:
        """Get average confidence across all thoughts."""
        if not self.thoughts:
            return 0.0
        return sum(t.confidence for t in self.thoughts) / len(self.thoughts)

    @property
    def highest_tier_used(self) -> Optional[CognitiveTier]:
        """Get the highest cognitive tier that was used."""
        if not self.tiers_used:
            return None
        return max(self.tiers_used, key=lambda t: t.value)


class StimulusInput(BaseModel):
    """Input model for cognitive processing requests.
    
    Contains the stimulus to process and parameters that determine
    how it should be processed.
    """

    stimulus: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="The stimulus text to process",
    )
    agent_id: UUID = Field(..., description="ID of the agent to process with")
    
    # Processing parameters (0.0 to 1.0)
    urgency: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="How urgent is this stimulus (affects tier selection)",
    )
    complexity: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="How complex is this stimulus (affects depth)",
    )
    relevance: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="How relevant is this to the agent (affects engagement)",
    )
    
    # Optional context
    purpose: str = Field(
        default="general_response",
        description="Purpose of processing this stimulus",
    )
    context: Optional[dict] = Field(
        None,
        description="Additional context for processing",
    )

    model_config = {"from_attributes": True}


class ProcessingStrategy(BaseModel):
    """A planned cognitive processing strategy.
    
    Describes which tiers to use and in what order,
    based on the stimulus characteristics.
    """

    steps: List[dict] = Field(
        default_factory=list,
        description="Processing steps to execute",
    )
    
    # Each step has:
    # - tier: CognitiveTier
    # - purpose: str
    # - parallel: bool
    # - count: int (for parallel execution)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "steps": self.steps,
            "step_count": len(self.steps),
            "has_parallel": any(s.get("parallel", False) for s in self.steps),
        }

    @property
    def step_count(self) -> int:
        """Get number of steps in strategy."""
        return len(self.steps)

    @property
    def has_parallel_steps(self) -> bool:
        """Check if strategy has any parallel steps."""
        return any(s.get("parallel", False) for s in self.steps)

    @property
    def total_tier_invocations(self) -> int:
        """Get total number of tier invocations."""
        return sum(s.get("count", 1) for s in self.steps)

