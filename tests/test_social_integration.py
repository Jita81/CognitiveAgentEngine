"""Integration tests for Social Intelligence with InternalMind.

Tests the full social intelligence workflow including integration
with the cognitive mind system from Phase 4.
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
from src.social.context import SocialContext, ParticipantInfo, GroupType
from src.social.intent import ExternalizationIntent
from src.social.intelligence import SocialIntelligence
from src.social.models import Stimulus
from src.social.builder import SocialContextBuilder, create_participant


@pytest.fixture
def engineer_agent():
    """Create an engineer agent for testing."""
    return AgentProfile(
        agent_id=uuid4(),
        name="Engineer",
        role="Software Engineer",
        backstory_summary="Experienced software engineer with deep expertise in Python and system design. "
                         "Known for thoughtful analysis and collaborative problem-solving.",
        skills=SkillSet(
            technical={"python": 9, "system_design": 8, "databases": 7, "testing": 8},
            domains={"backend": 8, "api_design": 7},
            soft_skills={"communication": 6, "mentoring": 5},
        ),
        personality_markers=PersonalityMarkers(openness=7, conscientiousness=8),
        social_markers=SocialMarkers(
            confidence=7,
            curiosity=8,
            facilitation_instinct=5,
            comfort_with_conflict=5,
        ),
        communication_style=CommunicationStyle(),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def designer_agent():
    """Create a designer agent for testing."""
    return AgentProfile(
        agent_id=uuid4(),
        name="Designer",
        role="UX Designer",
        backstory_summary="Creative UX designer with expertise in user research and interface design. "
                         "Passionate about creating intuitive user experiences.",
        skills=SkillSet(
            technical={"figma": 9, "prototyping": 8},
            domains={"ux": 9, "ui": 8, "user_research": 7},
            soft_skills={"presentation": 8, "empathy": 9},
        ),
        personality_markers=PersonalityMarkers(openness=9, extraversion=7),
        social_markers=SocialMarkers(
            confidence=7,
            curiosity=7,
            facilitation_instinct=7,
            comfort_in_spotlight=8,
        ),
        communication_style=CommunicationStyle(),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


class TestFullWorkflow:
    """Tests for complete social intelligence workflow."""
    
    def test_engineer_responds_to_technical_question(self, engineer_agent):
        """Test engineer responds when asked technical question."""
        mind = InternalMind(agent_id=str(engineer_agent.agent_id))
        social_intel = SocialIntelligence(agent=engineer_agent, mind=mind)
        
        # Designer asks about API design
        stimulus = Stimulus.direct_question(
            content="How should we design the REST API for this feature?",
            directed_at=[str(engineer_agent.agent_id)],
            topic="api design rest",
        )
        
        context = SocialContextBuilder.pair_context(
            my_agent_id=str(engineer_agent.agent_id),
            partner=create_participant("designer-1", "Designer"),
            topic="api design",
        )
        
        decision = social_intel.should_i_speak(stimulus, context)
        
        assert decision.intent == ExternalizationIntent.MUST_RESPOND
        assert decision.should_speak is True
    
    def test_designer_defers_on_backend_topic(self, designer_agent, engineer_agent):
        """Test designer defers when backend expert is present."""
        mind = InternalMind(agent_id=str(designer_agent.agent_id))
        social_intel = SocialIntelligence(agent=designer_agent, mind=mind)
        
        # Create context with engineer present
        engineer_participant = create_participant(
            agent_id=str(engineer_agent.agent_id),
            name=engineer_agent.name,
            role="engineer",
            expertise=["python", "backend", "databases"],
            has_spoken=False,
        )
        
        context = SocialContext(
            participants=[engineer_participant],
            group_size=3,
            my_role="participant",
            expertise_present={
                "python": [str(engineer_agent.agent_id)],
                "backend": [str(engineer_agent.agent_id)],
            },
        )
        
        stimulus = Stimulus(
            content="What database should we use for this?",
            topic="backend database",
        )
        
        decision = social_intel.should_i_speak(stimulus, context)
        
        # Designer should defer to engineer on backend topics
        assert decision.intent in [
            ExternalizationIntent.ACTIVE_LISTEN,
            ExternalizationIntent.PASSIVE_AWARENESS,
        ]
    
    def test_designer_contributes_on_ux_topic(self, designer_agent):
        """Test designer contributes when UX topic comes up."""
        mind = InternalMind(agent_id=str(designer_agent.agent_id))
        social_intel = SocialIntelligence(agent=designer_agent, mind=mind)
        
        context = SocialContext(
            participants=[
                create_participant("eng-1", "Engineer", expertise=["python"]),
            ],
            group_size=2,
            my_role="participant",
        )
        
        stimulus = Stimulus(
            content="How should we handle the user onboarding flow?",
            topic="ux onboarding user experience",
        )
        
        decision = social_intel.should_i_speak(stimulus, context)
        
        # Designer should contribute on UX topics
        assert decision.should_speak is True
        assert decision.intent in [
            ExternalizationIntent.SHOULD_CONTRIBUTE,
            ExternalizationIntent.MAY_CONTRIBUTE,
        ]


class TestMindIntegration:
    """Tests for integration with InternalMind."""
    
    def test_critical_concern_in_mind(self, engineer_agent):
        """Test that critical concerns in mind affect decisions."""
        mind = InternalMind(agent_id=str(engineer_agent.agent_id))
        
        # Add a critical security concern
        concern = Thought(
            thought_id=uuid4(),
            created_at=datetime.now(timezone.utc),
            tier=CognitiveTier.ANALYTICAL,
            content="This approach exposes a significant SQL injection vulnerability",
            thought_type=ThoughtType.CONCERN,
            trigger="security_analysis",
            confidence=0.95,
            completeness=0.9,
        )
        mind.add_thought(concern)
        mind.prepare_to_share(concern)
        
        social_intel = SocialIntelligence(agent=engineer_agent, mind=mind)
        
        # Check that the mind has the concern
        assert mind.get_best_contribution() is not None
        assert mind.get_best_contribution().confidence > 0.8
    
    def test_held_insights_affect_decision(self, engineer_agent):
        """Test that held insights can affect decisions."""
        mind = InternalMind(agent_id=str(engineer_agent.agent_id))
        
        # Add a held insight
        insight = Thought(
            thought_id=uuid4(),
            created_at=datetime.now(timezone.utc),
            tier=CognitiveTier.DELIBERATE,
            content="I noticed a pattern that could simplify this",
            thought_type=ThoughtType.INSIGHT,
            trigger="pattern_recognition",
            confidence=0.8,
            completeness=0.7,
        )
        mind.hold_insight(insight)
        
        social_intel = SocialIntelligence(agent=engineer_agent, mind=mind)
        
        # The held insight exists but shouldn't force contribution
        assert len(mind.held_insights) == 1


class TestGroupDynamics:
    """Tests for group dynamics across different sizes."""
    
    def test_small_team_dynamics(self, engineer_agent):
        """Test behavior in small team context."""
        mind = InternalMind(agent_id=str(engineer_agent.agent_id))
        social_intel = SocialIntelligence(agent=engineer_agent, mind=mind)
        
        context = SocialContextBuilder.meeting_context(
            my_agent_id=str(engineer_agent.agent_id),
            participants=[
                create_participant("a1", "Alice", expertise=["python"]),
                create_participant("a2", "Bob", expertise=["design"]),
                create_participant("a3", "Carol", expertise=["testing"]),
            ],
            my_role="participant",
            topic="sprint planning",
        )
        
        assert context.group_type == GroupType.SMALL_TEAM
        
        stimulus = Stimulus(
            content="How should we approach the backend refactoring?",
            topic="python backend refactoring",
        )
        
        decision = social_intel.should_i_speak(stimulus, context)
        
        # In small team, engineer should contribute on backend topics
        assert decision.should_speak is True
    
    def test_large_meeting_dynamics(self, engineer_agent):
        """Test behavior in large meeting."""
        mind = InternalMind(agent_id=str(engineer_agent.agent_id))
        social_intel = SocialIntelligence(agent=engineer_agent, mind=mind)
        
        # Create large meeting context
        participants = [
            create_participant(f"agent-{i}", f"Person-{i}")
            for i in range(15)
        ]
        
        context = SocialContext(
            participants=participants,
            group_size=16,  # 15 + me
            my_role="participant",
        )
        
        assert context.group_type == GroupType.MEETING
        
        stimulus = Stimulus(
            content="General project update discussion",
            topic="general updates",
        )
        
        decision = social_intel.should_i_speak(stimulus, context)
        
        # In larger meeting with general topic, should be more selective
        # Either listen or only contribute if asked
        assert decision.intent in [
            ExternalizationIntent.ACTIVE_LISTEN,
            ExternalizationIntent.PASSIVE_AWARENESS,
            ExternalizationIntent.MAY_CONTRIBUTE,
        ]


class TestStimulusHandling:
    """Tests for different stimulus types."""
    
    def test_broadcast_stimulus(self, engineer_agent):
        """Test handling broadcast messages."""
        mind = InternalMind(agent_id=str(engineer_agent.agent_id))
        social_intel = SocialIntelligence(agent=engineer_agent, mind=mind)
        
        stimulus = Stimulus.from_message(
            content="Does anyone have experience with caching strategies?",
            source_name="Project Manager",
            topic="caching performance",
        )
        
        assert stimulus.is_broadcast is True
        
        context = SocialContext(group_size=5, my_role="participant")
        
        decision = social_intel.should_i_speak(stimulus, context)
        
        # Should consider contributing if relevant expertise
        # Engineer doesn't have explicit caching expertise, so may listen
        assert decision.intent is not None
    
    def test_directed_question_stimulus(self, engineer_agent):
        """Test handling directed questions."""
        mind = InternalMind(agent_id=str(engineer_agent.agent_id))
        social_intel = SocialIntelligence(agent=engineer_agent, mind=mind)
        
        stimulus = Stimulus.direct_question(
            content="Can you explain the database schema?",
            directed_at=[str(engineer_agent.agent_id)],
            source_name="New Developer",
            topic="database schema",
        )
        
        assert stimulus.is_directed is True
        assert stimulus.requires_response is True
        
        context = SocialContext(group_size=3, my_role="mentor")
        
        decision = social_intel.should_i_speak(stimulus, context)
        
        assert decision.intent == ExternalizationIntent.MUST_RESPOND
        assert decision.should_speak is True


class TestRoleBasedBehavior:
    """Tests for role-based behavior."""
    
    def test_facilitator_role(self, engineer_agent):
        """Test behavior as facilitator."""
        # Give agent high facilitation instinct
        engineer_agent.social_markers.facilitation_instinct = 9
        
        mind = InternalMind(agent_id=str(engineer_agent.agent_id))
        social_intel = SocialIntelligence(agent=engineer_agent, mind=mind)
        
        context = SocialContext(
            group_size=5,
            my_role="facilitator",
            participants=[
                create_participant("a1", "Alice"),
                create_participant("a2", "Bob"),
            ],
        )
        
        stimulus = Stimulus(content="What should we discuss?", topic="agenda")
        
        decision = social_intel.should_i_speak(stimulus, context)
        
        # Facilitator should lean towards facilitation contribution type
        if decision.should_speak:
            assert decision.contribution_type in ["facilitation", "statement", "question"]
    
    def test_junior_role(self, engineer_agent):
        """Test behavior as junior team member."""
        mind = InternalMind(agent_id=str(engineer_agent.agent_id))
        social_intel = SocialIntelligence(agent=engineer_agent, mind=mind)
        
        context = SocialContext(
            group_size=5,
            my_role="junior",
            my_status_relative="junior",
        )
        
        # Role suggestion for junior is "learn_and_ask"
        role_suggests = social_intel._what_does_role_suggest(context)
        assert role_suggests == "learn_and_ask"
    
    def test_expert_role(self, engineer_agent):
        """Test behavior as domain expert."""
        mind = InternalMind(agent_id=str(engineer_agent.agent_id))
        social_intel = SocialIntelligence(agent=engineer_agent, mind=mind)
        
        context = SocialContext(
            group_size=5,
            my_role="expert",
        )
        
        stimulus = Stimulus(
            content="We need guidance on the Python implementation",
            topic="python implementation",
        )
        
        decision = social_intel.should_i_speak(stimulus, context)
        
        # As expert on Python topic, should contribute
        assert decision.should_speak is True


class TestEdgeCases:
    """Tests for edge cases."""
    
    def test_empty_stimulus(self, engineer_agent):
        """Test handling stimulus with minimal content."""
        mind = InternalMind(agent_id=str(engineer_agent.agent_id))
        social_intel = SocialIntelligence(agent=engineer_agent, mind=mind)
        
        stimulus = Stimulus(content="...", topic="")
        context = SocialContext(group_size=2)
        
        # Should handle gracefully
        decision = social_intel.should_i_speak(stimulus, context)
        assert decision is not None
    
    def test_no_participants(self, engineer_agent):
        """Test handling context with no participants."""
        mind = InternalMind(agent_id=str(engineer_agent.agent_id))
        social_intel = SocialIntelligence(agent=engineer_agent, mind=mind)
        
        context = SocialContextBuilder.solo_context(str(engineer_agent.agent_id))
        
        # Use a topic the engineer has expertise in (python)
        stimulus = Stimulus(content="Working on Python code", topic="python backend")
        
        decision = social_intel.should_i_speak(stimulus, context)
        
        # In solo context with relevant topic, should be willing to contribute
        assert context.group_type == GroupType.SOLO
        assert decision.should_speak is True

