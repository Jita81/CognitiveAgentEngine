"""Externalization intent models for social intelligence decisions.

This module defines the possible outcomes of a social intelligence
evaluation - whether an agent should speak, listen, or remain passive.

Phase 5 of the Cognitive Agent Engine.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional


class ExternalizationIntent(Enum):
    """The agent's decision about whether/how to contribute.
    
    These intents form a spectrum from mandatory response to passive awareness:
    - MUST_RESPOND: No choice, must answer (directly addressed)
    - SHOULD_CONTRIBUTE: Strong reason to contribute (expertise needed)
    - MAY_CONTRIBUTE: Optional contribution (have value to add)
    - ACTIVE_LISTEN: Engaged but not contributing (learning/deferring)
    - PASSIVE_AWARENESS: Background monitoring (not relevant)
    """
    
    MUST_RESPOND = "must_respond"       # Directly addressed, must answer
    SHOULD_CONTRIBUTE = "should"        # My expertise is specifically needed
    MAY_CONTRIBUTE = "may"              # I have value to add
    ACTIVE_LISTEN = "listen"            # Learning, not contributing
    PASSIVE_AWARENESS = "passive"       # Background noise


class ContributionType(Enum):
    """Type of contribution the agent plans to make."""
    
    RESPONSE = "response"           # Answering a direct question
    STATEMENT = "statement"         # Making a point
    QUESTION = "question"           # Asking for clarification
    FACILITATION = "facilitation"   # Helping the discussion flow
    CHALLENGE = "challenge"         # Respectful disagreement
    SUPPORT = "support"             # Building on someone's point


class ContributionTiming(Enum):
    """When the agent should make their contribution."""
    
    NOW = "now"                     # Speak immediately
    WAIT_FOR_OPENING = "wait_for_opening"  # Wait for a pause
    WHEN_ASKED = "when_asked"       # Only if directly asked
    END_OF_DISCUSSION = "end_of_discussion"  # Save for wrap-up


@dataclass
class ExternalizationDecision:
    """Full externalization decision with reasoning.
    
    This is the output of the social intelligence evaluation,
    capturing not just whether to speak but why and how.
    
    Attributes:
        intent: The decision type (MUST_RESPOND, SHOULD_CONTRIBUTE, etc.)
        confidence: How confident the agent is in this decision (0.0-1.0)
        reason: Human-readable explanation for the decision
        contribution_type: If speaking, what type of contribution
        timing: When to make the contribution
        factors: Debug info about factors considered
    """
    
    intent: ExternalizationIntent
    confidence: float
    reason: str
    
    # If speaking
    contribution_type: Optional[str] = None  # statement, question, facilitation
    timing: str = ContributionTiming.NOW.value
    
    # For debugging/learning
    factors: Dict[str, any] = field(default_factory=dict)
    
    @property
    def should_speak(self) -> bool:
        """Check if this decision indicates the agent should speak.
        
        Returns:
            True if intent indicates speaking (MUST_RESPOND, SHOULD, MAY)
        """
        return self.intent in (
            ExternalizationIntent.MUST_RESPOND,
            ExternalizationIntent.SHOULD_CONTRIBUTE,
            ExternalizationIntent.MAY_CONTRIBUTE,
        )
    
    @property
    def is_mandatory(self) -> bool:
        """Check if this decision requires a response.
        
        Returns:
            True only for MUST_RESPOND intent
        """
        return self.intent == ExternalizationIntent.MUST_RESPOND
    
    @property
    def is_optional(self) -> bool:
        """Check if contribution is optional.
        
        Returns:
            True for MAY_CONTRIBUTE intent
        """
        return self.intent == ExternalizationIntent.MAY_CONTRIBUTE
    
    @property
    def should_wait(self) -> bool:
        """Check if agent should wait before speaking.
        
        Returns:
            True if timing is not NOW
        """
        return self.timing != ContributionTiming.NOW.value
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "intent": self.intent.value,
            "confidence": self.confidence,
            "reason": self.reason,
            "contribution_type": self.contribution_type,
            "timing": self.timing,
            "should_speak": self.should_speak,
            "is_mandatory": self.is_mandatory,
            "factors": self.factors,
        }
    
    @classmethod
    def must_respond(
        cls,
        reason: str = "directly_addressed",
        contribution_type: str = ContributionType.RESPONSE.value,
        factors: Optional[Dict] = None,
    ) -> "ExternalizationDecision":
        """Factory for MUST_RESPOND decisions.
        
        Args:
            reason: Why the response is mandatory
            contribution_type: Type of contribution to make
            factors: Debug factors
            
        Returns:
            ExternalizationDecision with MUST_RESPOND intent
        """
        return cls(
            intent=ExternalizationIntent.MUST_RESPOND,
            confidence=1.0,
            reason=reason,
            contribution_type=contribution_type,
            timing=ContributionTiming.NOW.value,
            factors=factors or {"directly_addressed": True},
        )
    
    @classmethod
    def should_contribute(
        cls,
        confidence: float,
        reason: str,
        contribution_type: str = ContributionType.STATEMENT.value,
        factors: Optional[Dict] = None,
    ) -> "ExternalizationDecision":
        """Factory for SHOULD_CONTRIBUTE decisions.
        
        Args:
            confidence: Confidence level (0.0-1.0)
            reason: Why contribution is recommended
            contribution_type: Type of contribution to make
            factors: Debug factors
            
        Returns:
            ExternalizationDecision with SHOULD_CONTRIBUTE intent
        """
        return cls(
            intent=ExternalizationIntent.SHOULD_CONTRIBUTE,
            confidence=confidence,
            reason=reason,
            contribution_type=contribution_type,
            timing=ContributionTiming.NOW.value,
            factors=factors or {},
        )
    
    @classmethod
    def may_contribute(
        cls,
        confidence: float,
        reason: str,
        timing: str = ContributionTiming.WAIT_FOR_OPENING.value,
        contribution_type: str = ContributionType.STATEMENT.value,
        factors: Optional[Dict] = None,
    ) -> "ExternalizationDecision":
        """Factory for MAY_CONTRIBUTE decisions.
        
        Args:
            confidence: Confidence level (0.0-1.0)
            reason: Why contribution might be valuable
            timing: When to make the contribution
            contribution_type: Type of contribution to make
            factors: Debug factors
            
        Returns:
            ExternalizationDecision with MAY_CONTRIBUTE intent
        """
        return cls(
            intent=ExternalizationIntent.MAY_CONTRIBUTE,
            confidence=confidence,
            reason=reason,
            contribution_type=contribution_type,
            timing=timing,
            factors=factors or {},
        )
    
    @classmethod
    def active_listen(
        cls,
        confidence: float,
        reason: str,
        timing: str = ContributionTiming.WHEN_ASKED.value,
        factors: Optional[Dict] = None,
    ) -> "ExternalizationDecision":
        """Factory for ACTIVE_LISTEN decisions.
        
        Args:
            confidence: Confidence level (0.0-1.0)
            reason: Why active listening is appropriate
            timing: When might speak if asked
            factors: Debug factors
            
        Returns:
            ExternalizationDecision with ACTIVE_LISTEN intent
        """
        return cls(
            intent=ExternalizationIntent.ACTIVE_LISTEN,
            confidence=confidence,
            reason=reason,
            contribution_type=None,
            timing=timing,
            factors=factors or {},
        )
    
    @classmethod
    def passive_awareness(
        cls,
        confidence: float = 0.9,
        reason: str = "not_relevant",
        factors: Optional[Dict] = None,
    ) -> "ExternalizationDecision":
        """Factory for PASSIVE_AWARENESS decisions.
        
        Args:
            confidence: Confidence level (0.0-1.0)
            reason: Why passive mode is appropriate
            factors: Debug factors
            
        Returns:
            ExternalizationDecision with PASSIVE_AWARENESS intent
        """
        return cls(
            intent=ExternalizationIntent.PASSIVE_AWARENESS,
            confidence=confidence,
            reason=reason,
            contribution_type=None,
            timing=ContributionTiming.WHEN_ASKED.value,
            factors=factors or {},
        )

