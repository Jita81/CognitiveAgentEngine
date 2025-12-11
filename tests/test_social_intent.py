"""Tests for externalization intent models.

Tests for ExternalizationIntent and ExternalizationDecision from Phase 5.
"""

import pytest

from src.social.intent import (
    ExternalizationIntent,
    ExternalizationDecision,
    ContributionType,
    ContributionTiming,
)


class TestExternalizationIntent:
    """Tests for ExternalizationIntent enum."""
    
    def test_intent_values(self):
        """Test all intent values exist."""
        assert ExternalizationIntent.MUST_RESPOND.value == "must_respond"
        assert ExternalizationIntent.SHOULD_CONTRIBUTE.value == "should"
        assert ExternalizationIntent.MAY_CONTRIBUTE.value == "may"
        assert ExternalizationIntent.ACTIVE_LISTEN.value == "listen"
        assert ExternalizationIntent.PASSIVE_AWARENESS.value == "passive"
    
    def test_intent_count(self):
        """Test we have exactly 5 intents."""
        assert len(ExternalizationIntent) == 5


class TestContributionType:
    """Tests for ContributionType enum."""
    
    def test_contribution_types(self):
        """Test all contribution types exist."""
        assert ContributionType.RESPONSE.value == "response"
        assert ContributionType.STATEMENT.value == "statement"
        assert ContributionType.QUESTION.value == "question"
        assert ContributionType.FACILITATION.value == "facilitation"
        assert ContributionType.CHALLENGE.value == "challenge"
        assert ContributionType.SUPPORT.value == "support"


class TestContributionTiming:
    """Tests for ContributionTiming enum."""
    
    def test_timing_values(self):
        """Test all timing values exist."""
        assert ContributionTiming.NOW.value == "now"
        assert ContributionTiming.WAIT_FOR_OPENING.value == "wait_for_opening"
        assert ContributionTiming.WHEN_ASKED.value == "when_asked"
        assert ContributionTiming.END_OF_DISCUSSION.value == "end_of_discussion"


class TestExternalizationDecision:
    """Tests for ExternalizationDecision dataclass."""
    
    def test_create_decision(self):
        """Test creating a basic decision."""
        decision = ExternalizationDecision(
            intent=ExternalizationIntent.SHOULD_CONTRIBUTE,
            confidence=0.8,
            reason="have_valuable_input",
        )
        
        assert decision.intent == ExternalizationIntent.SHOULD_CONTRIBUTE
        assert decision.confidence == 0.8
        assert decision.reason == "have_valuable_input"
        assert decision.contribution_type is None
        assert decision.timing == ContributionTiming.NOW.value
        assert decision.factors == {}
    
    def test_should_speak_must_respond(self):
        """Test should_speak property for MUST_RESPOND."""
        decision = ExternalizationDecision(
            intent=ExternalizationIntent.MUST_RESPOND,
            confidence=1.0,
            reason="directly_addressed",
        )
        
        assert decision.should_speak is True
        assert decision.is_mandatory is True
        assert decision.is_optional is False
    
    def test_should_speak_should_contribute(self):
        """Test should_speak property for SHOULD_CONTRIBUTE."""
        decision = ExternalizationDecision(
            intent=ExternalizationIntent.SHOULD_CONTRIBUTE,
            confidence=0.7,
            reason="expertise_needed",
        )
        
        assert decision.should_speak is True
        assert decision.is_mandatory is False
    
    def test_should_speak_may_contribute(self):
        """Test should_speak property for MAY_CONTRIBUTE."""
        decision = ExternalizationDecision(
            intent=ExternalizationIntent.MAY_CONTRIBUTE,
            confidence=0.5,
            reason="have_value_to_add",
        )
        
        assert decision.should_speak is True
        assert decision.is_optional is True
    
    def test_should_speak_active_listen(self):
        """Test should_speak property for ACTIVE_LISTEN."""
        decision = ExternalizationDecision(
            intent=ExternalizationIntent.ACTIVE_LISTEN,
            confidence=0.6,
            reason="defer_to_expert",
        )
        
        assert decision.should_speak is False
    
    def test_should_speak_passive_awareness(self):
        """Test should_speak property for PASSIVE_AWARENESS."""
        decision = ExternalizationDecision(
            intent=ExternalizationIntent.PASSIVE_AWARENESS,
            confidence=0.9,
            reason="not_relevant",
        )
        
        assert decision.should_speak is False
    
    def test_should_wait_now(self):
        """Test should_wait property for NOW timing."""
        decision = ExternalizationDecision(
            intent=ExternalizationIntent.SHOULD_CONTRIBUTE,
            confidence=0.8,
            reason="test",
            timing=ContributionTiming.NOW.value,
        )
        
        assert decision.should_wait is False
    
    def test_should_wait_deferred(self):
        """Test should_wait property for non-NOW timing."""
        decision = ExternalizationDecision(
            intent=ExternalizationIntent.MAY_CONTRIBUTE,
            confidence=0.5,
            reason="test",
            timing=ContributionTiming.WAIT_FOR_OPENING.value,
        )
        
        assert decision.should_wait is True
    
    def test_to_dict(self):
        """Test converting decision to dictionary."""
        decision = ExternalizationDecision(
            intent=ExternalizationIntent.SHOULD_CONTRIBUTE,
            confidence=0.75,
            reason="expertise_match",
            contribution_type=ContributionType.STATEMENT.value,
            timing=ContributionTiming.NOW.value,
            factors={"expertise_relevance": 0.8},
        )
        
        d = decision.to_dict()
        
        assert d["intent"] == "should"
        assert d["confidence"] == 0.75
        assert d["reason"] == "expertise_match"
        assert d["contribution_type"] == "statement"
        assert d["timing"] == "now"
        assert d["should_speak"] is True
        assert d["is_mandatory"] is False
        assert d["factors"]["expertise_relevance"] == 0.8


class TestDecisionFactories:
    """Tests for ExternalizationDecision factory methods."""
    
    def test_must_respond_factory(self):
        """Test must_respond factory method."""
        decision = ExternalizationDecision.must_respond(
            reason="name_mentioned",
            contribution_type=ContributionType.RESPONSE.value,
        )
        
        assert decision.intent == ExternalizationIntent.MUST_RESPOND
        assert decision.confidence == 1.0
        assert decision.reason == "name_mentioned"
        assert decision.contribution_type == "response"
        assert decision.timing == "now"
        assert decision.should_speak is True
    
    def test_must_respond_factory_defaults(self):
        """Test must_respond factory with defaults."""
        decision = ExternalizationDecision.must_respond()
        
        assert decision.intent == ExternalizationIntent.MUST_RESPOND
        assert decision.confidence == 1.0
        assert decision.reason == "directly_addressed"
        assert decision.contribution_type == "response"
        assert decision.factors["directly_addressed"] is True
    
    def test_should_contribute_factory(self):
        """Test should_contribute factory method."""
        decision = ExternalizationDecision.should_contribute(
            confidence=0.85,
            reason="expertise_needed",
            contribution_type=ContributionType.STATEMENT.value,
            factors={"expertise": 0.9},
        )
        
        assert decision.intent == ExternalizationIntent.SHOULD_CONTRIBUTE
        assert decision.confidence == 0.85
        assert decision.reason == "expertise_needed"
        assert decision.contribution_type == "statement"
        assert decision.timing == "now"
        assert decision.factors["expertise"] == 0.9
    
    def test_may_contribute_factory(self):
        """Test may_contribute factory method."""
        decision = ExternalizationDecision.may_contribute(
            confidence=0.5,
            reason="have_insight",
            timing=ContributionTiming.WAIT_FOR_OPENING.value,
        )
        
        assert decision.intent == ExternalizationIntent.MAY_CONTRIBUTE
        assert decision.confidence == 0.5
        assert decision.reason == "have_insight"
        assert decision.timing == "wait_for_opening"
    
    def test_active_listen_factory(self):
        """Test active_listen factory method."""
        decision = ExternalizationDecision.active_listen(
            confidence=0.7,
            reason="defer_to_expert:Bob",
            factors={"defer_to": "Bob"},
        )
        
        assert decision.intent == ExternalizationIntent.ACTIVE_LISTEN
        assert decision.confidence == 0.7
        assert decision.reason == "defer_to_expert:Bob"
        assert decision.contribution_type is None
        assert decision.timing == "when_asked"
        assert decision.factors["defer_to"] == "Bob"
    
    def test_passive_awareness_factory(self):
        """Test passive_awareness factory method."""
        decision = ExternalizationDecision.passive_awareness(
            confidence=0.95,
            reason="not_my_domain",
        )
        
        assert decision.intent == ExternalizationIntent.PASSIVE_AWARENESS
        assert decision.confidence == 0.95
        assert decision.reason == "not_my_domain"
        assert decision.contribution_type is None
        assert decision.should_speak is False
    
    def test_passive_awareness_factory_defaults(self):
        """Test passive_awareness factory with defaults."""
        decision = ExternalizationDecision.passive_awareness()
        
        assert decision.confidence == 0.9
        assert decision.reason == "not_relevant"

