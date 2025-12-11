"""Tests for SocialContextBuilder.

Tests for building social context from various sources.
"""

import pytest

from src.social.context import (
    SocialContext,
    ParticipantInfo,
    GroupType,
    DiscussionPhase,
    EnergyLevel,
)
from src.social.builder import SocialContextBuilder, create_participant


class TestFromMeetingState:
    """Tests for building context from meeting state."""
    
    def test_basic_meeting_state(self):
        """Test building from basic meeting state."""
        meeting_state = {
            "participants": [
                {
                    "agent_id": "agent-1",
                    "name": "Alice",
                    "role": "engineer",
                    "expertise": ["python", "testing"],
                    "has_spoken": True,
                    "contribution_count": 2,
                },
                {
                    "agent_id": "agent-2",
                    "name": "Bob",
                    "role": "designer",
                    "expertise": ["ui", "ux"],
                    "has_spoken": False,
                    "contribution_count": 0,
                },
            ],
            "current_speaker": "agent-1",
            "current_topic": "architecture",
            "phase": "exploring",
            "speaking_distribution": {"agent-1": 2},
            "energy": "engaged",
            "consensus": "discussing",
        }
        
        context = SocialContextBuilder.from_meeting_state(
            meeting_state=meeting_state,
            my_agent_id="agent-1",
        )
        
        assert context.group_size == 2
        assert context.group_type == GroupType.PAIR
        assert context.current_speaker == "agent-1"
        assert context.topic_under_discussion == "architecture"
        assert context.discussion_phase == "exploring"
        assert len(context.participants) == 2
        assert context.energy_level == "engaged"
    
    def test_expertise_map_building(self):
        """Test that expertise map is built correctly."""
        meeting_state = {
            "participants": [
                {
                    "agent_id": "agent-1",
                    "name": "Alice",
                    "expertise": ["Python", "Testing"],
                },
                {
                    "agent_id": "agent-2",
                    "name": "Bob",
                    "expertise": ["Python", "Design"],
                },
            ],
        }
        
        context = SocialContextBuilder.from_meeting_state(
            meeting_state=meeting_state,
            my_agent_id="agent-1",
        )
        
        # Python should map to both agents (lowercase)
        assert "python" in context.expertise_present
        assert "agent-1" in context.expertise_present["python"]
        assert "agent-2" in context.expertise_present["python"]
    
    def test_my_role_extraction(self):
        """Test that my role is correctly extracted."""
        meeting_state = {
            "participants": [
                {
                    "agent_id": "agent-1",
                    "name": "Alice",
                    "meeting_role": "facilitator",
                    "status": "senior",
                },
                {
                    "agent_id": "agent-2",
                    "name": "Bob",
                    "meeting_role": "participant",
                },
            ],
        }
        
        context = SocialContextBuilder.from_meeting_state(
            meeting_state=meeting_state,
            my_agent_id="agent-1",
        )
        
        assert context.my_role == "facilitator"
        assert context.my_status_relative == "senior"
    
    def test_empty_meeting_state(self):
        """Test handling empty meeting state."""
        meeting_state = {}
        
        context = SocialContextBuilder.from_meeting_state(
            meeting_state=meeting_state,
            my_agent_id="agent-1",
        )
        
        # Should create valid context with defaults
        assert context.group_size == 1
        assert context.participants == []
        assert context.discussion_phase == DiscussionPhase.EXPLORING.value


class TestFromConversation:
    """Tests for building context from conversation."""
    
    def test_basic_conversation(self):
        """Test building from conversation messages."""
        messages = [
            {"sender_id": "agent-1", "content": "Hello"},
            {"sender_id": "agent-2", "content": "Hi there"},
            {"sender_id": "agent-1", "content": "Let's discuss"},
        ]
        
        participants = [
            {"agent_id": "agent-1", "name": "Alice", "expertise": ["python"]},
            {"agent_id": "agent-2", "name": "Bob", "expertise": ["design"]},
        ]
        
        context = SocialContextBuilder.from_conversation(
            messages=messages,
            participants=participants,
            my_agent_id="agent-1",
            topic="project planning",
        )
        
        assert context.group_size == 2
        assert context.topic_under_discussion == "project planning"
        
        # Check speaking distribution
        assert context.speaking_distribution["agent-1"] == 2
        assert context.speaking_distribution["agent-2"] == 1
        
        # Check has_spoken
        alice = context.get_participant("agent-1")
        assert alice.has_spoken is True
        assert alice.contribution_count == 2
    
    def test_conversation_expertise_map(self):
        """Test expertise map from conversation participants."""
        messages = []
        participants = [
            {"agent_id": "a1", "name": "A", "expertise": ["ml", "python"]},
            {"agent_id": "a2", "name": "B", "expertise": ["ml", "data"]},
        ]
        
        context = SocialContextBuilder.from_conversation(
            messages=messages,
            participants=participants,
            my_agent_id="a1",
        )
        
        assert "ml" in context.expertise_present
        assert len(context.expertise_present["ml"]) == 2
    
    def test_current_speaker_from_last_message(self):
        """Test that current speaker is set from last message."""
        messages = [
            {"sender_id": "agent-1", "content": "First"},
            {"sender_id": "agent-2", "content": "Last message"},
        ]
        participants = [
            {"agent_id": "agent-1", "name": "A"},
            {"agent_id": "agent-2", "name": "B"},
        ]
        
        context = SocialContextBuilder.from_conversation(
            messages=messages,
            participants=participants,
            my_agent_id="agent-1",
        )
        
        assert context.current_speaker == "agent-2"


class TestSoloContext:
    """Tests for solo context builder."""
    
    def test_solo_context(self):
        """Test creating solo context."""
        context = SocialContextBuilder.solo_context(my_agent_id="agent-1")
        
        assert context.group_size == 1
        assert context.group_type == GroupType.SOLO
        assert context.participants == []
        assert context.my_role == "participant"


class TestPairContext:
    """Tests for pair context builder."""
    
    def test_pair_context(self):
        """Test creating pair context."""
        partner = ParticipantInfo(
            agent_id="partner-1",
            name="Bob",
            role="engineer",
            expertise_areas=["java", "databases"],
        )
        
        context = SocialContextBuilder.pair_context(
            my_agent_id="agent-1",
            partner=partner,
            topic="code review",
        )
        
        assert context.group_size == 2
        assert context.group_type == GroupType.PAIR
        assert len(context.participants) == 1
        assert context.participants[0].name == "Bob"
        assert context.topic_under_discussion == "code review"
    
    def test_pair_expertise_map(self):
        """Test expertise map in pair context."""
        partner = ParticipantInfo(
            agent_id="partner-1",
            name="Bob",
            expertise_areas=["Python", "Testing"],
        )
        
        context = SocialContextBuilder.pair_context(
            my_agent_id="agent-1",
            partner=partner,
        )
        
        assert "python" in context.expertise_present
        assert "partner-1" in context.expertise_present["python"]


class TestMeetingContext:
    """Tests for meeting context builder."""
    
    def test_meeting_context(self):
        """Test creating meeting context."""
        participants = [
            ParticipantInfo(agent_id="a1", name="Alice", expertise_areas=["python"]),
            ParticipantInfo(agent_id="a2", name="Bob", expertise_areas=["design"]),
            ParticipantInfo(agent_id="a3", name="Carol", expertise_areas=["testing"]),
        ]
        
        context = SocialContextBuilder.meeting_context(
            my_agent_id="me",
            participants=participants,
            my_role="facilitator",
            topic="sprint planning",
            phase=DiscussionPhase.EXPLORING.value,
        )
        
        assert context.group_size == 4  # 3 participants + me
        assert context.group_type == GroupType.SMALL_TEAM
        assert context.my_role == "facilitator"
        assert context.topic_under_discussion == "sprint planning"
    
    def test_meeting_with_contributions(self):
        """Test meeting context with existing contributions."""
        participants = [
            ParticipantInfo(
                agent_id="a1",
                name="Alice",
                contribution_count=3,
            ),
            ParticipantInfo(
                agent_id="a2",
                name="Bob",
                contribution_count=1,
            ),
        ]
        
        context = SocialContextBuilder.meeting_context(
            my_agent_id="me",
            participants=participants,
        )
        
        assert context.speaking_distribution["a1"] == 3
        assert context.speaking_distribution["a2"] == 1


class TestCreateParticipantHelper:
    """Tests for create_participant helper function."""
    
    def test_create_minimal_participant(self):
        """Test creating participant with minimal args."""
        participant = create_participant(
            agent_id="agent-1",
            name="Alice",
        )
        
        assert participant.agent_id == "agent-1"
        assert participant.name == "Alice"
        assert participant.role == "participant"
        assert participant.expertise_areas == []
        assert participant.has_spoken is False
    
    def test_create_full_participant(self):
        """Test creating participant with all args."""
        participant = create_participant(
            agent_id="agent-1",
            name="Alice",
            role="expert",
            expertise=["python", "ml"],
            has_spoken=True,
            contribution_count=5,
        )
        
        assert participant.role == "expert"
        assert participant.expertise_areas == ["python", "ml"]
        assert participant.has_spoken is True
        assert participant.contribution_count == 5

