"""Social Intelligence module (Phase 5).

This module provides social intelligence capabilities that enable agents
to make human-like decisions about when to speak. Key components:

- SocialContext: Models for understanding social situations
- ExternalizationIntent: Decision types for externalization
- SocialIntelligence: Core decision-making class
- SocialContextBuilder: Build context from various sources
- Stimulus: Input stimulus representation

Example usage:
    from src.social import (
        SocialIntelligence,
        SocialContext,
        Stimulus,
        ExternalizationIntent,
    )
    
    # Create social intelligence for an agent
    social_intel = SocialIntelligence(agent=agent, mind=mind)
    
    # Evaluate whether to speak
    stimulus = Stimulus(content="What do you think about this design?")
    context = SocialContext(group_size=5, my_role="expert")
    
    decision = social_intel.should_i_speak(stimulus, context)
    if decision.should_speak:
        print(f"Contributing: {decision.contribution_type}")
"""

# Context models
from src.social.context import (
    GroupType,
    DiscussionPhase,
    EnergyLevel,
    ConsensusLevel,
    ParticipantInfo,
    SocialContext,
)

# Intent models
from src.social.intent import (
    ExternalizationIntent,
    ExternalizationDecision,
    ContributionType,
    ContributionTiming,
)

# Stimulus model
from src.social.models import Stimulus

# Core intelligence
from src.social.intelligence import SocialIntelligence

# Builder utilities
from src.social.builder import (
    SocialContextBuilder,
    create_participant,
)

__all__ = [
    # Context
    "GroupType",
    "DiscussionPhase",
    "EnergyLevel",
    "ConsensusLevel",
    "ParticipantInfo",
    "SocialContext",
    # Intent
    "ExternalizationIntent",
    "ExternalizationDecision",
    "ContributionType",
    "ContributionTiming",
    # Stimulus
    "Stimulus",
    # Intelligence
    "SocialIntelligence",
    # Builder
    "SocialContextBuilder",
    "create_participant",
]
