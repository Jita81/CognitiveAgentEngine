"""Social Intelligence API routes.

Phase 5: Social intelligence endpoints for evaluating when agents should speak.
"""

from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from src.agents.repository import AgentRepository
from src.api.dependencies import AgentRepo
from src.cognitive import InternalMind
from src.social.context import SocialContext, ParticipantInfo, GroupType
from src.social.intent import ExternalizationIntent, ExternalizationDecision
from src.social.intelligence import SocialIntelligence
from src.social.models import Stimulus
from src.social.builder import SocialContextBuilder, create_participant

router = APIRouter(prefix="/v1/social", tags=["social"])


# ==========================================
# Request/Response Models
# ==========================================


class ParticipantInput(BaseModel):
    """Input model for participant information."""
    
    agent_id: str = Field(..., description="Unique identifier for the participant")
    name: str = Field(..., description="Display name")
    role: str = Field(default="participant", description="Role in the meeting")
    expertise: List[str] = Field(default_factory=list, description="Areas of expertise")
    has_spoken: bool = Field(default=False, description="Whether they've contributed")
    contribution_count: int = Field(default=0, description="Number of contributions")
    seems_engaged: bool = Field(default=True, description="Whether they appear engaged")
    apparent_position: Optional[str] = Field(None, description="Their stance on current topic")


class StimulusInput(BaseModel):
    """Input model for stimulus."""
    
    content: str = Field(..., min_length=1, description="The stimulus content")
    source_id: Optional[str] = Field(None, description="ID of the source agent")
    source_name: Optional[str] = Field(None, description="Name of the source")
    directed_at: Optional[List[str]] = Field(None, description="Agent IDs this is directed at")
    topic: str = Field(default="", description="Topic of the stimulus")
    priority: float = Field(default=0.5, ge=0.0, le=1.0, description="Priority level")
    requires_response: bool = Field(default=False, description="Whether response is required")


class SocialContextInput(BaseModel):
    """Input model for social context."""
    
    participants: List[ParticipantInput] = Field(default_factory=list)
    group_size: int = Field(default=1, ge=1, description="Total group size")
    my_role: str = Field(default="participant", description="Agent's role")
    my_status_relative: str = Field(default="peer", description="Agent's relative status")
    current_speaker: Optional[str] = Field(None, description="Current speaker ID")
    topic_under_discussion: str = Field(default="", description="Current topic")
    discussion_phase: str = Field(default="exploring", description="Phase of discussion")
    speaking_distribution: Dict[str, int] = Field(default_factory=dict)
    energy_level: str = Field(default="engaged", description="Conversation energy")
    consensus_level: str = Field(default="discussing", description="Level of agreement")


class EvaluateRequest(BaseModel):
    """Request to evaluate whether an agent should speak."""
    
    agent_id: UUID = Field(..., description="ID of the agent to evaluate")
    stimulus: StimulusInput = Field(..., description="The incoming stimulus")
    context: SocialContextInput = Field(..., description="The social context")


class EvaluateResponse(BaseModel):
    """Response from social intelligence evaluation."""
    
    intent: str = Field(description="The externalization intent")
    confidence: float = Field(description="Confidence in the decision")
    reason: str = Field(description="Reason for the decision")
    should_speak: bool = Field(description="Whether the agent should speak")
    is_mandatory: bool = Field(description="Whether response is mandatory")
    contribution_type: Optional[str] = Field(description="Type of contribution if speaking")
    timing: str = Field(description="When to contribute")
    factors: Dict[str, Any] = Field(description="Factors considered in decision")


class MeetingStateInput(BaseModel):
    """Input model for meeting state."""
    
    participants: List[Dict[str, Any]] = Field(default_factory=list)
    current_speaker: Optional[str] = Field(None)
    current_topic: str = Field(default="")
    phase: str = Field(default="exploring")
    speaking_distribution: Dict[str, int] = Field(default_factory=dict)
    energy: str = Field(default="engaged")
    consensus: str = Field(default="discussing")
    expertise_gaps: List[str] = Field(default_factory=list)


class BuildContextRequest(BaseModel):
    """Request to build social context from meeting state."""
    
    agent_id: UUID = Field(..., description="ID of the agent")
    meeting_state: MeetingStateInput = Field(..., description="Meeting state data")


class SocialContextResponse(BaseModel):
    """Response containing built social context."""
    
    group_size: int
    group_type: str
    my_role: str
    my_status_relative: str
    current_speaker: Optional[str]
    topic_under_discussion: str
    discussion_phase: str
    participant_count: int
    energy_level: str
    consensus_level: str


class SpeakingStatusResponse(BaseModel):
    """Response for agent's speaking status."""
    
    agent_id: str
    agent_name: str
    ready_to_share_count: int
    held_insights_count: int
    active_thoughts_count: int
    has_critical_input: bool
    best_contribution_confidence: Optional[float]


# ==========================================
# In-memory storage for agent minds (simplified)
# In production, these would be managed by AgentManager
# ==========================================


_agent_minds: Dict[UUID, InternalMind] = {}


def get_agent_mind(agent_id: UUID) -> InternalMind:
    """Get or create an agent's InternalMind."""
    if agent_id not in _agent_minds:
        _agent_minds[agent_id] = InternalMind(agent_id=str(agent_id))
    return _agent_minds[agent_id]


# ==========================================
# API Endpoints
# ==========================================


@router.post(
    "/evaluate",
    response_model=EvaluateResponse,
    summary="Evaluate whether agent should speak",
    description="Use social intelligence to determine if an agent should contribute to a conversation.",
)
async def evaluate_should_speak(
    request: EvaluateRequest,
    repo: AgentRepository = Depends(AgentRepo),
) -> EvaluateResponse:
    """Evaluate whether an agent should speak based on stimulus and context."""
    
    # Get agent profile
    agent = await repo.get(request.agent_id)
    if agent is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {request.agent_id} not found",
        )
    
    # Get or create agent's mind
    mind = get_agent_mind(request.agent_id)
    
    # Build stimulus
    stimulus = Stimulus(
        content=request.stimulus.content,
        source_id=request.stimulus.source_id,
        source_name=request.stimulus.source_name,
        directed_at=request.stimulus.directed_at,
        topic=request.stimulus.topic,
        priority=request.stimulus.priority,
        requires_response=request.stimulus.requires_response,
    )
    
    # Build social context
    participants = [
        ParticipantInfo(
            agent_id=p.agent_id,
            name=p.name,
            role=p.role,
            expertise_areas=p.expertise,
            has_spoken=p.has_spoken,
            contribution_count=p.contribution_count,
            seems_engaged=p.seems_engaged,
            apparent_position=p.apparent_position,
        )
        for p in request.context.participants
    ]
    
    context = SocialContext(
        participants=participants,
        group_size=request.context.group_size,
        my_role=request.context.my_role,
        my_status_relative=request.context.my_status_relative,
        current_speaker=request.context.current_speaker,
        topic_under_discussion=request.context.topic_under_discussion,
        discussion_phase=request.context.discussion_phase,
        speaking_distribution=request.context.speaking_distribution,
        energy_level=request.context.energy_level,
        consensus_level=request.context.consensus_level,
    )
    
    # Create social intelligence and evaluate
    social_intelligence = SocialIntelligence(agent=agent, mind=mind)
    decision = social_intelligence.should_i_speak(stimulus, context)
    
    return EvaluateResponse(
        intent=decision.intent.value,
        confidence=decision.confidence,
        reason=decision.reason,
        should_speak=decision.should_speak,
        is_mandatory=decision.is_mandatory,
        contribution_type=decision.contribution_type,
        timing=decision.timing,
        factors=decision.factors,
    )


@router.post(
    "/context/from-meeting",
    response_model=SocialContextResponse,
    summary="Build context from meeting state",
    description="Build a social context from meeting state data.",
)
async def build_context_from_meeting(
    request: BuildContextRequest,
    repo: AgentRepository = Depends(AgentRepo),
) -> SocialContextResponse:
    """Build social context from meeting state."""
    
    # Verify agent exists
    agent = await repo.get(request.agent_id)
    if agent is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {request.agent_id} not found",
        )
    
    # Convert meeting state to dict
    meeting_state = {
        "participants": [dict(p) for p in request.meeting_state.participants],
        "current_speaker": request.meeting_state.current_speaker,
        "current_topic": request.meeting_state.current_topic,
        "phase": request.meeting_state.phase,
        "speaking_distribution": request.meeting_state.speaking_distribution,
        "energy": request.meeting_state.energy,
        "consensus": request.meeting_state.consensus,
        "expertise_gaps": request.meeting_state.expertise_gaps,
    }
    
    # Build context
    context = SocialContextBuilder.from_meeting_state(
        meeting_state=meeting_state,
        my_agent_id=str(request.agent_id),
    )
    
    return SocialContextResponse(
        group_size=context.group_size,
        group_type=context.group_type.value,
        my_role=context.my_role,
        my_status_relative=context.my_status_relative,
        current_speaker=context.current_speaker,
        topic_under_discussion=context.topic_under_discussion,
        discussion_phase=context.discussion_phase,
        participant_count=len(context.participants),
        energy_level=context.energy_level,
        consensus_level=context.consensus_level,
    )


@router.get(
    "/agents/{agent_id}/speaking-status",
    response_model=SpeakingStatusResponse,
    summary="Get agent's speaking status",
    description="Get information about an agent's readiness to speak.",
)
async def get_agent_speaking_status(
    agent_id: UUID,
    repo: AgentRepository = Depends(AgentRepo),
) -> SpeakingStatusResponse:
    """Get agent's current speaking status."""
    
    # Get agent profile
    agent = await repo.get(agent_id)
    if agent is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found",
        )
    
    # Get agent's mind
    mind = get_agent_mind(agent_id)
    
    # Get best contribution
    best = mind.get_best_contribution()
    best_confidence = best.confidence if best else None
    
    # Check for critical input
    has_critical = False
    for thought in mind.held_insights:
        if thought.confidence > 0.85 and thought.thought_type.value == "concern":
            has_critical = True
            break
    
    if best and best.confidence > 0.8 and best.thought_type.value == "concern":
        has_critical = True
    
    return SpeakingStatusResponse(
        agent_id=str(agent_id),
        agent_name=agent.name,
        ready_to_share_count=len(mind.ready_to_share),
        held_insights_count=len(mind.held_insights),
        active_thoughts_count=len(mind.active_thoughts),
        has_critical_input=has_critical,
        best_contribution_confidence=best_confidence,
    )


@router.get(
    "/intents",
    summary="Get all externalization intents",
    description="List all possible externalization intent types.",
)
async def get_externalization_intents() -> List[Dict[str, str]]:
    """Get all externalization intent types."""
    return [
        {
            "value": intent.value,
            "name": intent.name,
            "description": _get_intent_description(intent),
        }
        for intent in ExternalizationIntent
    ]


@router.get(
    "/group-types",
    summary="Get all group types",
    description="List all group type classifications with their thresholds.",
)
async def get_group_types() -> List[Dict[str, Any]]:
    """Get all group type classifications."""
    thresholds = {
        GroupType.SOLO: 0.0,
        GroupType.PAIR: 0.3,
        GroupType.SMALL_TEAM: 0.4,
        GroupType.MEETING: 0.5,
        GroupType.LARGE_GROUP: 0.7,
        GroupType.ARMY: 0.9,
    }
    
    size_ranges = {
        GroupType.SOLO: "1",
        GroupType.PAIR: "2",
        GroupType.SMALL_TEAM: "3-6",
        GroupType.MEETING: "7-20",
        GroupType.LARGE_GROUP: "21-100",
        GroupType.ARMY: "100+",
    }
    
    return [
        {
            "value": gt.value,
            "name": gt.name,
            "size_range": size_ranges[gt],
            "contribution_threshold": thresholds[gt],
        }
        for gt in GroupType
    ]


def _get_intent_description(intent: ExternalizationIntent) -> str:
    """Get description for an externalization intent."""
    descriptions = {
        ExternalizationIntent.MUST_RESPOND: "Directly addressed, must answer",
        ExternalizationIntent.SHOULD_CONTRIBUTE: "Expertise is specifically needed",
        ExternalizationIntent.MAY_CONTRIBUTE: "Have value to add but optional",
        ExternalizationIntent.ACTIVE_LISTEN: "Learning, not contributing",
        ExternalizationIntent.PASSIVE_AWARENESS: "Background noise, not relevant",
    }
    return descriptions.get(intent, "Unknown intent")

