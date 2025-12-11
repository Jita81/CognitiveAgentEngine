"""Social Context Builder for constructing social context from various sources.

This module provides builders that can construct SocialContext objects
from different input formats like meeting state dictionaries.

Phase 5 of the Cognitive Agent Engine.
"""

from typing import Any, Dict, List, Optional

from src.social.context import (
    SocialContext,
    ParticipantInfo,
    EnergyLevel,
    DiscussionPhase,
    ConsensusLevel,
)


class SocialContextBuilder:
    """Builds SocialContext objects from various input sources.
    
    Provides factory methods for constructing properly configured
    SocialContext instances from meeting states, conversation data,
    and other sources.
    """
    
    @staticmethod
    def from_meeting_state(
        meeting_state: Dict[str, Any],
        my_agent_id: str,
    ) -> SocialContext:
        """Build SocialContext from a meeting state dictionary.
        
        Args:
            meeting_state: Dictionary containing meeting information
            my_agent_id: ID of the agent this context is for
            
        Returns:
            Configured SocialContext instance
        """
        # Build participant list
        participants = []
        for p in meeting_state.get("participants", []):
            participants.append(ParticipantInfo(
                agent_id=p.get("agent_id", ""),
                name=p.get("name", "Unknown"),
                role=p.get("role", "participant"),
                expertise_areas=p.get("expertise", []),
                has_spoken=p.get("has_spoken", False),
                contribution_count=p.get("contribution_count", 0),
                seems_engaged=p.get("seems_engaged", True),
                apparent_position=p.get("apparent_position"),
            ))
        
        # Build expertise map
        expertise_present: Dict[str, List[str]] = {}
        for p in participants:
            for skill in p.expertise_areas:
                skill_lower = skill.lower()
                if skill_lower not in expertise_present:
                    expertise_present[skill_lower] = []
                expertise_present[skill_lower].append(p.agent_id)
        
        # Determine my role and status
        my_role = "participant"
        my_status = "peer"
        for p in meeting_state.get("participants", []):
            if p.get("agent_id") == my_agent_id:
                my_role = p.get("meeting_role", p.get("role", "participant"))
                my_status = p.get("status", "peer")
                break
        
        # Get speaking distribution
        speaking_distribution = meeting_state.get("speaking_distribution", {})
        
        # Calculate group size
        group_size = len(participants)
        if group_size == 0:
            # Include self even if not in participant list
            group_size = 1
        
        return SocialContext(
            participants=participants,
            group_size=group_size,
            my_role=my_role,
            my_status_relative=my_status,
            current_speaker=meeting_state.get("current_speaker"),
            topic_under_discussion=meeting_state.get("current_topic", ""),
            discussion_phase=meeting_state.get("phase", DiscussionPhase.EXPLORING.value),
            expertise_present=expertise_present,
            expertise_gaps=meeting_state.get("expertise_gaps", []),
            speaking_distribution=speaking_distribution,
            energy_level=meeting_state.get("energy", EnergyLevel.ENGAGED.value),
            consensus_level=meeting_state.get("consensus", ConsensusLevel.DISCUSSING.value),
        )
    
    @staticmethod
    def from_conversation(
        messages: List[Dict[str, Any]],
        participants: List[Dict[str, Any]],
        my_agent_id: str,
        topic: str = "",
    ) -> SocialContext:
        """Build SocialContext from conversation messages.
        
        Args:
            messages: List of message dictionaries with 'sender_id' and 'content'
            participants: List of participant info dictionaries
            my_agent_id: ID of the agent this context is for
            topic: Current topic of discussion
            
        Returns:
            Configured SocialContext instance
        """
        # Build participant list
        participant_objs = []
        speaking_distribution: Dict[str, int] = {}
        
        for p in participants:
            agent_id = p.get("agent_id", "")
            participant_objs.append(ParticipantInfo(
                agent_id=agent_id,
                name=p.get("name", "Unknown"),
                role=p.get("role", "participant"),
                expertise_areas=p.get("expertise", []),
                seems_engaged=True,
            ))
            speaking_distribution[agent_id] = 0
        
        # Count contributions from messages
        for msg in messages:
            sender_id = msg.get("sender_id", "")
            if sender_id:
                speaking_distribution[sender_id] = speaking_distribution.get(sender_id, 0) + 1
        
        # Update participant speaking state
        for participant in participant_objs:
            count = speaking_distribution.get(participant.agent_id, 0)
            participant.contribution_count = count
            participant.has_spoken = count > 0
        
        # Build expertise map
        expertise_present: Dict[str, List[str]] = {}
        for p in participant_objs:
            for skill in p.expertise_areas:
                skill_lower = skill.lower()
                if skill_lower not in expertise_present:
                    expertise_present[skill_lower] = []
                expertise_present[skill_lower].append(p.agent_id)
        
        # Find my role
        my_role = "participant"
        my_status = "peer"
        for p in participants:
            if p.get("agent_id") == my_agent_id:
                my_role = p.get("role", "participant")
                my_status = p.get("status", "peer")
                break
        
        # Get current speaker from last message
        current_speaker = None
        if messages:
            current_speaker = messages[-1].get("sender_id")
        
        return SocialContext(
            participants=participant_objs,
            group_size=len(participant_objs) if participant_objs else 1,
            my_role=my_role,
            my_status_relative=my_status,
            current_speaker=current_speaker,
            topic_under_discussion=topic,
            discussion_phase=DiscussionPhase.EXPLORING.value,
            expertise_present=expertise_present,
            speaking_distribution=speaking_distribution,
            energy_level=EnergyLevel.ENGAGED.value,
            consensus_level=ConsensusLevel.DISCUSSING.value,
        )
    
    @staticmethod
    def solo_context(my_agent_id: str) -> SocialContext:
        """Create a solo context (agent working alone).
        
        Args:
            my_agent_id: ID of the agent
            
        Returns:
            SocialContext for solo work
        """
        return SocialContext(
            participants=[],
            group_size=1,
            my_role="participant",
            my_status_relative="peer",
            current_speaker=None,
            topic_under_discussion="",
            discussion_phase=DiscussionPhase.EXPLORING.value,
        )
    
    @staticmethod
    def pair_context(
        my_agent_id: str,
        partner: ParticipantInfo,
        topic: str = "",
    ) -> SocialContext:
        """Create a pair context (two agents in conversation).
        
        Args:
            my_agent_id: ID of the agent
            partner: Info about the conversation partner
            topic: Current topic
            
        Returns:
            SocialContext for pair conversation
        """
        expertise_present: Dict[str, List[str]] = {}
        for skill in partner.expertise_areas:
            skill_lower = skill.lower()
            expertise_present[skill_lower] = [partner.agent_id]
        
        return SocialContext(
            participants=[partner],
            group_size=2,
            my_role="participant",
            my_status_relative="peer",
            current_speaker=None,
            topic_under_discussion=topic,
            discussion_phase=DiscussionPhase.EXPLORING.value,
            expertise_present=expertise_present,
        )
    
    @staticmethod
    def meeting_context(
        my_agent_id: str,
        participants: List[ParticipantInfo],
        my_role: str = "participant",
        topic: str = "",
        phase: str = DiscussionPhase.EXPLORING.value,
    ) -> SocialContext:
        """Create a meeting context with multiple participants.
        
        Args:
            my_agent_id: ID of the agent
            participants: List of other participants
            my_role: Agent's role in this meeting
            topic: Current topic
            phase: Discussion phase
            
        Returns:
            SocialContext for meeting
        """
        # Build expertise map
        expertise_present: Dict[str, List[str]] = {}
        for p in participants:
            for skill in p.expertise_areas:
                skill_lower = skill.lower()
                if skill_lower not in expertise_present:
                    expertise_present[skill_lower] = []
                expertise_present[skill_lower].append(p.agent_id)
        
        # Initialize speaking distribution
        speaking_distribution: Dict[str, int] = {
            p.agent_id: p.contribution_count 
            for p in participants
        }
        
        return SocialContext(
            participants=participants,
            group_size=len(participants) + 1,  # Include self
            my_role=my_role,
            my_status_relative="peer",
            current_speaker=None,
            topic_under_discussion=topic,
            discussion_phase=phase,
            expertise_present=expertise_present,
            speaking_distribution=speaking_distribution,
        )


def create_participant(
    agent_id: str,
    name: str,
    role: str = "participant",
    expertise: Optional[List[str]] = None,
    has_spoken: bool = False,
    contribution_count: int = 0,
) -> ParticipantInfo:
    """Helper function to create a ParticipantInfo instance.
    
    Args:
        agent_id: Unique identifier
        name: Display name
        role: Role in the meeting
        expertise: List of expertise areas
        has_spoken: Whether they've contributed
        contribution_count: Number of contributions
        
    Returns:
        ParticipantInfo instance
    """
    return ParticipantInfo(
        agent_id=agent_id,
        name=name,
        role=role,
        expertise_areas=expertise or [],
        has_spoken=has_spoken,
        contribution_count=contribution_count,
    )

