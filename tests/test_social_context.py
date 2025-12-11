"""Tests for social context models.

Tests for SocialContext, ParticipantInfo, and GroupType from Phase 5.
"""

import pytest

from src.social.context import (
    GroupType,
    DiscussionPhase,
    EnergyLevel,
    ConsensusLevel,
    ParticipantInfo,
    SocialContext,
)


class TestGroupType:
    """Tests for GroupType enum."""
    
    def test_group_type_values(self):
        """Test all group type values exist."""
        assert GroupType.SOLO.value == "solo"
        assert GroupType.PAIR.value == "pair"
        assert GroupType.SMALL_TEAM.value == "small_team"
        assert GroupType.MEETING.value == "meeting"
        assert GroupType.LARGE_GROUP.value == "large_group"
        assert GroupType.ARMY.value == "army"
    
    def test_group_type_count(self):
        """Test we have exactly 6 group types."""
        assert len(GroupType) == 6


class TestParticipantInfo:
    """Tests for ParticipantInfo dataclass."""
    
    def test_create_minimal_participant(self):
        """Test creating participant with minimal info."""
        participant = ParticipantInfo(
            agent_id="agent-1",
            name="Alice",
        )
        
        assert participant.agent_id == "agent-1"
        assert participant.name == "Alice"
        assert participant.role == "participant"
        assert participant.expertise_areas == []
        assert participant.has_spoken is False
        assert participant.contribution_count == 0
        assert participant.seems_engaged is True
        assert participant.apparent_position is None
    
    def test_create_full_participant(self):
        """Test creating participant with all fields."""
        participant = ParticipantInfo(
            agent_id="agent-2",
            name="Bob",
            role="expert",
            expertise_areas=["python", "machine learning"],
            has_spoken=True,
            contribution_count=3,
            seems_engaged=True,
            apparent_position="supports the proposal",
        )
        
        assert participant.agent_id == "agent-2"
        assert participant.name == "Bob"
        assert participant.role == "expert"
        assert participant.expertise_areas == ["python", "machine learning"]
        assert participant.has_spoken is True
        assert participant.contribution_count == 3
        assert participant.apparent_position == "supports the proposal"
    
    def test_participant_to_dict(self):
        """Test converting participant to dictionary."""
        participant = ParticipantInfo(
            agent_id="agent-1",
            name="Alice",
            role="expert",
            expertise_areas=["design"],
        )
        
        d = participant.to_dict()
        
        assert d["agent_id"] == "agent-1"
        assert d["name"] == "Alice"
        assert d["role"] == "expert"
        assert d["expertise_areas"] == ["design"]
        assert d["has_spoken"] is False


class TestSocialContext:
    """Tests for SocialContext dataclass."""
    
    def test_create_default_context(self):
        """Test creating context with defaults."""
        context = SocialContext()
        
        assert context.participants == []
        assert context.group_size == 1
        assert context.my_role == "participant"
        assert context.my_status_relative == "peer"
        assert context.current_speaker is None
        assert context.topic_under_discussion == ""
        assert context.discussion_phase == DiscussionPhase.EXPLORING.value
        assert context.expertise_present == {}
        assert context.expertise_gaps == []
        assert context.speaking_distribution == {}
        assert context.energy_level == EnergyLevel.ENGAGED.value
        assert context.consensus_level == ConsensusLevel.DISCUSSING.value
    
    def test_group_type_solo(self):
        """Test group type classification for solo."""
        context = SocialContext(group_size=1)
        assert context.group_type == GroupType.SOLO
    
    def test_group_type_pair(self):
        """Test group type classification for pair."""
        context = SocialContext(group_size=2)
        assert context.group_type == GroupType.PAIR
    
    def test_group_type_small_team(self):
        """Test group type classification for small team."""
        for size in [3, 4, 5, 6]:
            context = SocialContext(group_size=size)
            assert context.group_type == GroupType.SMALL_TEAM, f"Failed for size {size}"
    
    def test_group_type_meeting(self):
        """Test group type classification for meeting."""
        for size in [7, 10, 15, 20]:
            context = SocialContext(group_size=size)
            assert context.group_type == GroupType.MEETING, f"Failed for size {size}"
    
    def test_group_type_large_group(self):
        """Test group type classification for large group."""
        for size in [21, 50, 75, 100]:
            context = SocialContext(group_size=size)
            assert context.group_type == GroupType.LARGE_GROUP, f"Failed for size {size}"
    
    def test_group_type_army(self):
        """Test group type classification for army scale."""
        for size in [101, 500, 1000]:
            context = SocialContext(group_size=size)
            assert context.group_type == GroupType.ARMY, f"Failed for size {size}"
    
    def test_get_participant_found(self):
        """Test finding a participant by ID."""
        participant = ParticipantInfo(agent_id="agent-1", name="Alice")
        context = SocialContext(participants=[participant])
        
        found = context.get_participant("agent-1")
        
        assert found is not None
        assert found.name == "Alice"
    
    def test_get_participant_not_found(self):
        """Test looking for non-existent participant."""
        context = SocialContext(participants=[])
        
        found = context.get_participant("unknown")
        
        assert found is None
    
    def test_update_speaker(self):
        """Test updating the current speaker."""
        participant = ParticipantInfo(agent_id="agent-1", name="Alice")
        context = SocialContext(
            participants=[participant],
            group_size=2,
        )
        
        context.update_speaker("agent-1")
        
        assert context.current_speaker == "agent-1"
        assert context.speaking_distribution["agent-1"] == 1
        assert participant.has_spoken is True
        assert participant.contribution_count == 1
    
    def test_update_speaker_multiple_times(self):
        """Test updating speaker multiple times."""
        participant = ParticipantInfo(agent_id="agent-1", name="Alice")
        context = SocialContext(participants=[participant])
        
        context.update_speaker("agent-1")
        context.update_speaker("agent-1")
        context.update_speaker("agent-1")
        
        assert context.speaking_distribution["agent-1"] == 3
        assert participant.contribution_count == 3
    
    def test_get_total_contributions(self):
        """Test getting total contributions."""
        context = SocialContext(
            speaking_distribution={"agent-1": 3, "agent-2": 5, "agent-3": 2}
        )
        
        total = context.get_total_contributions()
        
        assert total == 10
    
    def test_get_total_contributions_empty(self):
        """Test getting total with no contributions."""
        context = SocialContext()
        
        total = context.get_total_contributions()
        
        assert total == 0
    
    def test_get_contribution_share(self):
        """Test calculating contribution share."""
        context = SocialContext(
            speaking_distribution={"agent-1": 5, "agent-2": 5}
        )
        
        share = context.get_contribution_share("agent-1")
        
        assert share == 0.5
    
    def test_get_contribution_share_zero_total(self):
        """Test contribution share with no contributions."""
        context = SocialContext()
        
        share = context.get_contribution_share("agent-1")
        
        assert share == 0.0
    
    def test_get_fair_share(self):
        """Test calculating fair share."""
        context = SocialContext(group_size=4)
        
        fair_share = context.get_fair_share()
        
        assert fair_share == 0.25
    
    def test_get_participants_with_expertise(self):
        """Test finding participants with expertise."""
        context = SocialContext(
            expertise_present={
                "python": ["agent-1", "agent-2"],
                "machine learning": ["agent-2", "agent-3"],
            }
        )
        
        python_experts = context.get_participants_with_expertise("python")
        
        assert python_experts == ["agent-1", "agent-2"]
    
    def test_get_participants_with_expertise_partial_match(self):
        """Test finding participants with partial expertise match."""
        context = SocialContext(
            expertise_present={
                "machine learning": ["agent-1"],
                "deep learning": ["agent-2"],
            }
        )
        
        # "learning" should match both
        learning_experts = context.get_participants_with_expertise("learning")
        
        assert len(learning_experts) > 0
    
    def test_has_expert_for_topic(self):
        """Test checking for topic experts."""
        context = SocialContext(
            expertise_present={
                "python": ["agent-1"],
                "javascript": ["agent-2"],
            }
        )
        
        assert context.has_expert_for("python programming") is True
        assert context.has_expert_for("rust programming") is False
    
    def test_context_to_dict(self):
        """Test converting context to dictionary."""
        participant = ParticipantInfo(agent_id="agent-1", name="Alice")
        context = SocialContext(
            participants=[participant],
            group_size=2,
            my_role="expert",
            topic_under_discussion="architecture",
        )
        
        d = context.to_dict()
        
        assert d["group_size"] == 2
        assert d["group_type"] == "pair"
        assert d["my_role"] == "expert"
        assert d["topic_under_discussion"] == "architecture"
        assert len(d["participants"]) == 1


class TestEnums:
    """Tests for supporting enums."""
    
    def test_discussion_phases(self):
        """Test all discussion phases exist."""
        assert DiscussionPhase.OPENING.value == "opening"
        assert DiscussionPhase.EXPLORING.value == "exploring"
        assert DiscussionPhase.DEBATING.value == "debating"
        assert DiscussionPhase.DECIDING.value == "deciding"
        assert DiscussionPhase.CLOSING.value == "closing"
    
    def test_energy_levels(self):
        """Test all energy levels exist."""
        assert EnergyLevel.HEATED.value == "heated"
        assert EnergyLevel.ENGAGED.value == "engaged"
        assert EnergyLevel.NEUTRAL.value == "neutral"
        assert EnergyLevel.FLAGGING.value == "flagging"
    
    def test_consensus_levels(self):
        """Test all consensus levels exist."""
        assert ConsensusLevel.ALIGNED.value == "aligned"
        assert ConsensusLevel.DISCUSSING.value == "discussing"
        assert ConsensusLevel.DIVIDED.value == "divided"
        assert ConsensusLevel.CONFLICTED.value == "conflicted"

