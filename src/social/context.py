"""Social context models for understanding social situations.

This module provides models for representing and reasoning about social
contexts - the information an agent needs to make appropriate decisions
about when and how to participate in conversations.

Phase 5 of the Cognitive Agent Engine.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class GroupType(Enum):
    """Classification of group by size.
    
    Different group sizes require different social behaviors:
    - Smaller groups allow more frequent contributions
    - Larger groups require more selective participation
    """
    
    SOLO = "solo"           # 1 - Full engagement
    PAIR = "pair"           # 2 - Active collaboration
    SMALL_TEAM = "small_team"  # 3-6 - Role-based contribution
    MEETING = "meeting"     # 7-20 - Selective contribution
    LARGE_GROUP = "large_group"  # 21-100 - Highly selective
    ARMY = "army"           # 100+ - Respond only to direct address


class DiscussionPhase(Enum):
    """Phase of the current discussion."""
    
    OPENING = "opening"     # Initial framing
    EXPLORING = "exploring"  # Gathering perspectives
    DEBATING = "debating"   # Weighing options
    DECIDING = "deciding"   # Making choices
    CLOSING = "closing"     # Wrapping up


class EnergyLevel(Enum):
    """Energy level of the conversation."""
    
    HEATED = "heated"       # High tension/conflict
    ENGAGED = "engaged"     # Active participation
    NEUTRAL = "neutral"     # Normal flow
    FLAGGING = "flagging"   # Losing energy


class ConsensusLevel(Enum):
    """Level of consensus in the group."""
    
    ALIGNED = "aligned"     # Agreement reached
    DISCUSSING = "discussing"  # Still exploring
    DIVIDED = "divided"     # Clear disagreement
    CONFLICTED = "conflicted"  # Significant conflict


@dataclass
class ParticipantInfo:
    """Information about another participant in the conversation.
    
    Captures what an agent knows or can observe about another
    participant to inform social decisions.
    
    Attributes:
        agent_id: Unique identifier for the participant
        name: Display name
        role: Professional role (e.g., "engineer", "designer")
        expertise_areas: Known areas of expertise
        has_spoken: Whether they have contributed to this discussion
        contribution_count: Number of contributions made
        seems_engaged: Whether they appear to be actively engaged
        apparent_position: Their apparent stance on current topic
    """
    
    agent_id: str
    name: str
    role: str = "participant"
    expertise_areas: List[str] = field(default_factory=list)
    
    # Observed state
    has_spoken: bool = False
    contribution_count: int = 0
    seems_engaged: bool = True
    apparent_position: Optional[str] = None  # On current topic
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "role": self.role,
            "expertise_areas": self.expertise_areas,
            "has_spoken": self.has_spoken,
            "contribution_count": self.contribution_count,
            "seems_engaged": self.seems_engaged,
            "apparent_position": self.apparent_position,
        }


@dataclass
class SocialContext:
    """What the agent perceives about the current social situation.
    
    This is the primary input to social intelligence decisions,
    capturing everything relevant about the conversational context.
    
    Attributes:
        participants: List of other participants
        group_size: Total number of participants including self
        my_role: Agent's role in this context
        my_status_relative: Agent's status relative to others
        current_speaker: ID of whoever is currently speaking
        topic_under_discussion: Current topic being discussed
        discussion_phase: Phase of discussion
        expertise_present: Map of skills to agent IDs who have them
        expertise_gaps: Skills needed but not well-represented
        speaking_distribution: Map of agent_id to contribution count
        energy_level: Current energy of the conversation
        consensus_level: Level of agreement in the group
    """
    
    # Group composition
    participants: List[ParticipantInfo] = field(default_factory=list)
    group_size: int = 1
    
    # My position
    my_role: str = "participant"  # facilitator, expert, participant, observer, leader, junior
    my_status_relative: str = "peer"  # senior, peer, junior, outsider
    
    # Current dynamics
    current_speaker: Optional[str] = None
    topic_under_discussion: str = ""
    discussion_phase: str = DiscussionPhase.EXPLORING.value
    
    # Expertise map
    expertise_present: Dict[str, List[str]] = field(default_factory=dict)  # skill → agent_ids
    expertise_gaps: List[str] = field(default_factory=list)
    
    # Conversational state
    speaking_distribution: Dict[str, int] = field(default_factory=dict)  # agent_id → count
    energy_level: str = EnergyLevel.ENGAGED.value
    consensus_level: str = ConsensusLevel.DISCUSSING.value
    
    @property
    def group_type(self) -> GroupType:
        """Classify group by size.
        
        Returns:
            GroupType enum value based on current group size
        """
        if self.group_size <= 1:
            return GroupType.SOLO
        elif self.group_size == 2:
            return GroupType.PAIR
        elif self.group_size <= 6:
            return GroupType.SMALL_TEAM
        elif self.group_size <= 20:
            return GroupType.MEETING
        elif self.group_size <= 100:
            return GroupType.LARGE_GROUP
        else:
            return GroupType.ARMY
    
    def get_participant(self, agent_id: str) -> Optional[ParticipantInfo]:
        """Get participant by ID.
        
        Args:
            agent_id: The agent ID to look for
            
        Returns:
            ParticipantInfo if found, None otherwise
        """
        for participant in self.participants:
            if participant.agent_id == agent_id:
                return participant
        return None
    
    def update_speaker(self, agent_id: str) -> None:
        """Update current speaker and speaking distribution.
        
        Args:
            agent_id: ID of the agent who is now speaking
        """
        self.current_speaker = agent_id
        self.speaking_distribution[agent_id] = (
            self.speaking_distribution.get(agent_id, 0) + 1
        )
        
        # Update participant's speaking state
        participant = self.get_participant(agent_id)
        if participant:
            participant.has_spoken = True
            participant.contribution_count += 1
    
    def get_total_contributions(self) -> int:
        """Get total number of contributions across all participants.
        
        Returns:
            Sum of all contributions
        """
        return sum(self.speaking_distribution.values())
    
    def get_contribution_share(self, agent_id: str) -> float:
        """Calculate an agent's share of contributions.
        
        Args:
            agent_id: The agent to calculate share for
            
        Returns:
            Proportion of contributions (0.0 to 1.0)
        """
        total = self.get_total_contributions()
        if total == 0:
            return 0.0
        return self.speaking_distribution.get(agent_id, 0) / total
    
    def get_fair_share(self) -> float:
        """Calculate what a fair share of contributions would be.
        
        Returns:
            Expected proportion if contributions were equal
        """
        if self.group_size <= 0:
            return 0.0
        return 1.0 / self.group_size
    
    def get_participants_with_expertise(self, skill: str) -> List[str]:
        """Get agent IDs of participants with a given expertise.
        
        Args:
            skill: The skill to look for
            
        Returns:
            List of agent IDs with that expertise
        """
        skill_lower = skill.lower()
        for expertise, agent_ids in self.expertise_present.items():
            if skill_lower in expertise.lower() or expertise.lower() in skill_lower:
                return agent_ids
        return []
    
    def has_expert_for(self, topic: str) -> bool:
        """Check if there's an expert present for a topic.
        
        Args:
            topic: The topic to check expertise for
            
        Returns:
            True if at least one participant has relevant expertise
        """
        keywords = topic.lower().split()
        for keyword in keywords:
            if self.get_participants_with_expertise(keyword):
                return True
        return False
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "participants": [p.to_dict() for p in self.participants],
            "group_size": self.group_size,
            "group_type": self.group_type.value,
            "my_role": self.my_role,
            "my_status_relative": self.my_status_relative,
            "current_speaker": self.current_speaker,
            "topic_under_discussion": self.topic_under_discussion,
            "discussion_phase": self.discussion_phase,
            "expertise_present": self.expertise_present,
            "expertise_gaps": self.expertise_gaps,
            "speaking_distribution": self.speaking_distribution,
            "energy_level": self.energy_level,
            "consensus_level": self.consensus_level,
        }

