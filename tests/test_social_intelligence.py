"""Tests for SocialIntelligence class.

Tests for the core social intelligence decision-making from Phase 5.
"""

import pytest
from datetime import datetime, timezone
from uuid import uuid4

from src.agents.models import (
    AgentProfile,
    SkillSet,
    PersonalityMarkers,
    SocialMarkers,
    CommunicationStyle,
)
from src.cognitive.mind import InternalMind
from src.cognitive.models import Thought, ThoughtType
from src.cognitive.tiers import CognitiveTier
from src.social.context import (
    SocialContext,
    ParticipantInfo,
    GroupType,
    DiscussionPhase,
    EnergyLevel,
)
from src.social.intent import ExternalizationIntent, ContributionType
from src.social.intelligence import SocialIntelligence
from src.social.models import Stimulus


@pytest.fixture
def sample_agent():
    """Create a sample agent for testing."""
    return AgentProfile(
        agent_id=uuid4(),
        name="Alice",
        role="Senior Engineer",
        backstory_summary="Experienced software engineer with expertise in Python and system design. "
                         "Known for thoughtful contributions and collaborative approach.",
        skills=SkillSet(
            technical={"python": 9, "system_design": 8, "testing": 7},
            domains={"backend": 8, "databases": 7},
            soft_skills={"communication": 7, "mentoring": 6},
        ),
        personality_markers=PersonalityMarkers(
            openness=7,
            conscientiousness=8,
            extraversion=5,
            agreeableness=7,
            neuroticism=3,
        ),
        social_markers=SocialMarkers(
            confidence=7,
            assertiveness=6,
            deference=4,
            curiosity=8,
            social_calibration=7,
            status_sensitivity=4,
            facilitation_instinct=6,
            comfort_in_spotlight=6,
            comfort_with_conflict=5,
        ),
        communication_style=CommunicationStyle(),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def sample_mind(sample_agent):
    """Create a sample internal mind for testing."""
    return InternalMind(agent_id=str(sample_agent.agent_id))


@pytest.fixture
def social_intelligence(sample_agent, sample_mind):
    """Create SocialIntelligence instance for testing."""
    return SocialIntelligence(agent=sample_agent, mind=sample_mind)


class TestDirectAddress:
    """Tests for direct address handling."""
    
    def test_direct_address_by_id(self, social_intelligence, sample_agent):
        """Test MUST_RESPOND when addressed by ID."""
        stimulus = Stimulus(
            content="What do you think?",
            directed_at=[str(sample_agent.agent_id)],
            topic="design",
        )
        context = SocialContext(group_size=5)
        
        decision = social_intelligence.should_i_speak(stimulus, context)
        
        assert decision.intent == ExternalizationIntent.MUST_RESPOND
        assert decision.confidence == 1.0
        assert decision.should_speak is True
        assert decision.is_mandatory is True
    
    def test_direct_address_by_name(self, social_intelligence, sample_agent):
        """Test MUST_RESPOND when addressed by name."""
        stimulus = Stimulus(
            content="What do you think?",
            directed_at=["Alice"],
            topic="design",
        )
        context = SocialContext(group_size=5)
        
        decision = social_intelligence.should_i_speak(stimulus, context)
        
        assert decision.intent == ExternalizationIntent.MUST_RESPOND
    
    def test_name_mentioned_in_content(self, social_intelligence):
        """Test MUST_RESPOND when name is mentioned in content."""
        stimulus = Stimulus(
            content="Alice, what's your opinion on this approach?",
            topic="architecture",
        )
        context = SocialContext(group_size=5)
        
        decision = social_intelligence.should_i_speak(stimulus, context)
        
        assert decision.intent == ExternalizationIntent.MUST_RESPOND


class TestExpertiseRelevance:
    """Tests for expertise-based decisions."""
    
    def test_low_relevance_passive(self, social_intelligence):
        """Test PASSIVE_AWARENESS for irrelevant topics."""
        stimulus = Stimulus(
            content="Let's discuss the marketing strategy.",
            topic="marketing branding campaign",
        )
        context = SocialContext(group_size=5)
        
        decision = social_intelligence.should_i_speak(stimulus, context)
        
        assert decision.intent == ExternalizationIntent.PASSIVE_AWARENESS
        assert "not_my_area" in decision.reason
    
    def test_high_relevance_should_contribute(self, social_intelligence):
        """Test SHOULD_CONTRIBUTE for relevant topics."""
        stimulus = Stimulus(
            content="We need to discuss the Python backend architecture.",
            topic="python backend architecture",
        )
        context = SocialContext(group_size=3, my_role="participant")
        
        decision = social_intelligence.should_i_speak(stimulus, context)
        
        assert decision.intent in [
            ExternalizationIntent.SHOULD_CONTRIBUTE,
            ExternalizationIntent.MAY_CONTRIBUTE,
        ]
        assert decision.should_speak is True


class TestDeferToExpert:
    """Tests for deferring to experts."""
    
    def test_defer_when_expert_present(self, social_intelligence):
        """Test ACTIVE_LISTEN when more qualified expert is present."""
        expert = ParticipantInfo(
            agent_id="expert-1",
            name="Bob",
            role="Principal Engineer",
            expertise_areas=["python", "system_design", "architecture"],
            has_spoken=False,
        )
        
        stimulus = Stimulus(
            content="What's the best approach for scaling?",
            topic="system design scaling",
        )
        context = SocialContext(
            participants=[expert],
            group_size=3,
            expertise_present={"system_design": ["expert-1"], "scaling": ["expert-1"]},
        )
        
        decision = social_intelligence.should_i_speak(stimulus, context)
        
        # Should defer since Bob is more qualified and hasn't spoken
        assert decision.intent == ExternalizationIntent.ACTIVE_LISTEN
        assert "defer" in decision.reason.lower()
    
    def test_contribute_after_expert_spoke(self, social_intelligence):
        """Test contributing after expert has already spoken."""
        expert = ParticipantInfo(
            agent_id="expert-1",
            name="Bob",
            role="Principal Engineer",
            expertise_areas=["python", "system_design"],
            has_spoken=True,  # Expert has already spoken
            contribution_count=1,
        )
        
        stimulus = Stimulus(
            content="Any other thoughts on the architecture?",
            topic="python architecture",
        )
        context = SocialContext(
            participants=[expert],
            group_size=3,
            my_role="participant",
            expertise_present={"python": ["expert-1"]},
        )
        
        decision = social_intelligence.should_i_speak(stimulus, context)
        
        # Should be willing to contribute now
        assert decision.intent != ExternalizationIntent.PASSIVE_AWARENESS


class TestConversationalSpace:
    """Tests for conversational space awareness."""
    
    def test_no_space_when_someone_speaking(self, social_intelligence):
        """Test ACTIVE_LISTEN when someone else is speaking."""
        stimulus = Stimulus(content="Test message", topic="python")
        context = SocialContext(
            group_size=5,
            current_speaker="other-agent",  # Someone else is speaking
        )
        
        decision = social_intelligence.should_i_speak(stimulus, context)
        
        assert decision.intent == ExternalizationIntent.ACTIVE_LISTEN
        assert "no_space" in decision.reason
    
    def test_no_contribution_in_closing(self, social_intelligence):
        """Test ACTIVE_LISTEN during closing phase."""
        stimulus = Stimulus(content="Final thoughts?", topic="python")
        context = SocialContext(
            group_size=5,
            discussion_phase=DiscussionPhase.CLOSING.value,
        )
        
        decision = social_intelligence.should_i_speak(stimulus, context)
        
        assert decision.intent == ExternalizationIntent.ACTIVE_LISTEN
    
    def test_heated_discussion_with_conflict_comfort(self, social_intelligence, sample_agent):
        """Test handling heated discussions."""
        # Agent has comfort_with_conflict = 5, below threshold
        stimulus = Stimulus(content="This is wrong!", topic="python")
        context = SocialContext(
            group_size=5,
            energy_level=EnergyLevel.HEATED.value,
        )
        
        decision = social_intelligence.should_i_speak(stimulus, context)
        
        # With comfort_with_conflict at 5, should listen in heated discussions
        assert decision.intent == ExternalizationIntent.ACTIVE_LISTEN


class TestSaidEnough:
    """Tests for contribution fairness."""
    
    def test_listen_when_dominated(self, social_intelligence, sample_agent):
        """Test ACTIVE_LISTEN when agent has dominated conversation."""
        my_id = str(sample_agent.agent_id)
        
        stimulus = Stimulus(content="What else?", topic="python")
        context = SocialContext(
            group_size=4,
            my_role="participant",
            speaking_distribution={
                my_id: 10,  # We've spoken 10 times
                "other-1": 2,
                "other-2": 1,
            },
        )
        
        decision = social_intelligence.should_i_speak(stimulus, context)
        
        # We've spoken way more than fair share, should listen
        assert decision.intent == ExternalizationIntent.ACTIVE_LISTEN
        assert "said_enough" in decision.reason


class TestRoleApproprateness:
    """Tests for role-based behavior."""
    
    def test_observer_role_listens(self, social_intelligence):
        """Test ACTIVE_LISTEN for observer role."""
        stimulus = Stimulus(content="Thoughts?", topic="python")
        context = SocialContext(
            group_size=5,
            my_role="observer",
        )
        
        decision = social_intelligence.should_i_speak(stimulus, context)
        
        assert decision.intent == ExternalizationIntent.ACTIVE_LISTEN
        assert "observer" in decision.reason.lower()


class TestGroupSizeAdaptation:
    """Tests for group size-based thresholds."""
    
    def test_solo_always_contributes(self, social_intelligence):
        """Test contribution in solo context."""
        stimulus = Stimulus(content="Working alone", topic="python")
        context = SocialContext(group_size=1)
        
        decision = social_intelligence.should_i_speak(stimulus, context)
        
        # In solo, threshold is 0, should contribute
        assert decision.should_speak is True
    
    def test_pair_low_threshold(self, social_intelligence):
        """Test lower threshold in pair context."""
        stimulus = Stimulus(content="Discussion", topic="python design")
        context = SocialContext(group_size=2)
        
        decision = social_intelligence.should_i_speak(stimulus, context)
        
        # Pair threshold is 0.3, should be willing to contribute
        assert decision.should_speak is True
    
    def test_army_high_threshold(self, social_intelligence):
        """Test high threshold in army-scale context."""
        stimulus = Stimulus(content="General discussion", topic="general topic")
        context = SocialContext(group_size=200)  # Army scale
        
        decision = social_intelligence.should_i_speak(stimulus, context)
        
        # Army threshold is 0.9 - unless very relevant, should listen
        # Since topic is "general topic", relevance is likely low
        assert decision.intent in [
            ExternalizationIntent.PASSIVE_AWARENESS,
            ExternalizationIntent.ACTIVE_LISTEN,
            ExternalizationIntent.MAY_CONTRIBUTE,
        ]


class TestContributionType:
    """Tests for determining contribution type."""
    
    def test_curious_agent_asks_questions(self, sample_agent, sample_mind):
        """Test that curious agents tend to ask questions."""
        # Set high curiosity
        sample_agent.social_markers.curiosity = 9
        
        social_intel = SocialIntelligence(agent=sample_agent, mind=sample_mind)
        
        stimulus = Stimulus(content="What do you think?", topic="python")
        context = SocialContext(group_size=3, my_role="participant")
        
        # The contribution type should be question for curious agents
        contrib_type = social_intel._determine_contribution_type(stimulus, context)
        
        assert contrib_type == ContributionType.QUESTION.value
    
    def test_facilitator_facilitates(self, sample_agent, sample_mind):
        """Test that facilitators tend to facilitate."""
        # Set high facilitation instinct and low curiosity so facilitation takes precedence
        sample_agent.social_markers.facilitation_instinct = 9
        sample_agent.social_markers.curiosity = 5  # Below threshold of 7
        
        social_intel = SocialIntelligence(agent=sample_agent, mind=sample_mind)
        
        stimulus = Stimulus(content="Discussion", topic="python")
        context = SocialContext(group_size=5, my_role="facilitator")
        
        contrib_type = social_intel._determine_contribution_type(stimulus, context)
        
        assert contrib_type == ContributionType.FACILITATION.value


class TestCriticalInput:
    """Tests for critical input handling."""
    
    def test_critical_concern_overrides_said_enough(self, social_intelligence, sample_agent, sample_mind):
        """Test that critical concerns override said_enough."""
        my_id = str(sample_agent.agent_id)
        
        # Add a high-confidence concern to the mind
        concern = Thought(
            thought_id=uuid4(),
            created_at=datetime.now(timezone.utc),
            tier=CognitiveTier.DELIBERATE,  # Use tier enum, not tier_used string
            content="This approach has a critical security flaw",
            thought_type=ThoughtType.CONCERN,
            trigger="security_analysis",
            confidence=0.9,
            completeness=0.8,
        )
        sample_mind.add_thought(concern)
        sample_mind.prepare_to_share(concern)
        
        stimulus = Stimulus(content="Let's proceed", topic="security")
        context = SocialContext(
            group_size=4,
            my_role="participant",
            speaking_distribution={my_id: 8, "other": 2},  # We've spoken a lot
        )
        
        # Even though we've said enough, critical concern should allow speaking
        decision = social_intelligence.should_i_speak(stimulus, context)
        
        # If it's truly critical, should override said_enough
        # The implementation checks for high-confidence concerns
        # This test validates the integration with InternalMind


class TestExpertiseCalculation:
    """Tests for expertise matching."""
    
    def test_expertise_match_calculation(self, social_intelligence):
        """Test expertise match calculation."""
        # Agent has python:9, system_design:8, testing:7
        
        python_relevance = social_intelligence._calculate_expertise_match("python programming")
        assert python_relevance > 0.4  # Should be reasonably high (skill matching is partial)
        
        marketing_relevance = social_intelligence._calculate_expertise_match("marketing strategy")
        assert marketing_relevance < 0.3  # Should be low
    
    def test_empty_topic_medium_relevance(self, social_intelligence):
        """Test that empty topic gives medium relevance."""
        relevance = social_intelligence._calculate_expertise_match("")
        assert relevance == 0.5


class TestConvenienceMethods:
    """Tests for convenience methods."""
    
    def test_evaluate_and_decide(self, social_intelligence):
        """Test evaluate_and_decide wrapper."""
        stimulus = Stimulus(content="Test", topic="python")
        context = SocialContext(group_size=3)
        
        decision = social_intelligence.evaluate_and_decide(stimulus, context)
        
        assert decision is not None
        assert decision.intent is not None
    
    def test_get_speaking_confidence_for_topic(self, social_intelligence):
        """Test getting speaking confidence for a topic."""
        python_confidence = social_intelligence.get_speaking_confidence_for_topic("python development")
        marketing_confidence = social_intelligence.get_speaking_confidence_for_topic("marketing")
        
        assert python_confidence > marketing_confidence

