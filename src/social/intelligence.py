"""Social Intelligence module for externalization decisions.

This is the core of Phase 5 - the module that enables agents to make
intelligent decisions about when to speak based on social context,
expertise, and conversational dynamics.

Phase 5 of the Cognitive Agent Engine.
"""

import logging
from typing import List, Optional, Tuple

from src.agents.models import AgentProfile
from src.cognitive.mind import InternalMind
from src.social.context import (
    SocialContext,
    GroupType,
    ParticipantInfo,
    EnergyLevel,
    DiscussionPhase,
)
from src.social.intent import (
    ExternalizationIntent,
    ExternalizationDecision,
    ContributionType,
    ContributionTiming,
)
from src.social.models import Stimulus

logger = logging.getLogger(__name__)


class SocialIntelligence:
    """Evaluates social context to decide if/when to speak.
    
    This is what makes external orchestration unnecessary - agents
    can independently assess whether their contribution would be
    valuable given the current social context.
    
    The evaluation considers:
    - Self-awareness: What do I know? Have I said enough?
    - Social awareness: Who else is here? Should I defer?
    - Role appropriateness: What does my position suggest?
    - Group dynamics: Is there space for me to contribute?
    
    Attributes:
        agent: The agent profile with skills and social markers
        mind: The agent's internal mind (from Phase 4)
    """
    
    def __init__(self, agent: AgentProfile, mind: InternalMind):
        """Initialize social intelligence for an agent.
        
        Args:
            agent: The agent's profile
            mind: The agent's internal mind
        """
        self.agent = agent
        self.mind = mind
    
    def should_i_speak(
        self,
        stimulus: Stimulus,
        context: SocialContext,
    ) -> ExternalizationDecision:
        """Core social intelligence decision.
        
        Evaluates multiple factors to decide whether to externalize
        (speak/contribute) or remain silent.
        
        Args:
            stimulus: The incoming stimulus to respond to
            context: The current social context
            
        Returns:
            ExternalizationDecision with intent, confidence, and reasoning
        """
        factors = {}
        
        # 1. Am I directly addressed?
        if self._am_i_directly_addressed(stimulus):
            logger.debug(f"Agent {self.agent.name} directly addressed, must respond")
            return ExternalizationDecision.must_respond(
                reason="directly_addressed",
                contribution_type=ContributionType.RESPONSE.value,
                factors={"directly_addressed": True},
            )
        
        # 2. Calculate expertise relevance
        relevance = self._calculate_expertise_match(stimulus.topic)
        factors["expertise_relevance"] = relevance
        
        if relevance < 0.3:
            logger.debug(
                f"Agent {self.agent.name} has low relevance ({relevance:.2f}) "
                f"for topic '{stimulus.topic}'"
            )
            return ExternalizationDecision.passive_awareness(
                confidence=0.9,
                reason="not_my_area",
                factors=factors,
            )
        
        # 3. Check if I should defer to an expert
        should_defer, defer_to = self._should_defer_to_expert(stimulus.topic, context)
        factors["should_defer"] = should_defer
        factors["defer_to"] = defer_to
        
        if should_defer:
            logger.debug(
                f"Agent {self.agent.name} deferring to {defer_to} "
                f"on topic '{stimulus.topic}'"
            )
            return ExternalizationDecision.active_listen(
                confidence=0.7,
                reason=f"defer_to_expert:{defer_to}",
                timing=ContributionTiming.WHEN_ASKED.value,
                factors=factors,
            )
        
        # 4. Check conversational space
        has_space = self._is_there_conversational_space(context)
        factors["conversational_space"] = has_space
        
        if not has_space:
            logger.debug(
                f"Agent {self.agent.name} waiting for conversational space"
            )
            return ExternalizationDecision.active_listen(
                confidence=0.8,
                reason="no_space",
                timing=ContributionTiming.WAIT_FOR_OPENING.value,
                factors=factors,
            )
        
        # 5. Check if I've said enough
        said_enough = self._have_i_said_enough(context)
        factors["said_enough"] = said_enough
        
        if said_enough:
            # Unless my input is critical
            has_critical = self._do_i_have_critical_input(stimulus)
            factors["has_critical_input"] = has_critical
            
            if not has_critical:
                logger.debug(
                    f"Agent {self.agent.name} has said enough, listening"
                )
                return ExternalizationDecision.active_listen(
                    confidence=0.6,
                    reason="said_enough",
                    timing=ContributionTiming.WHEN_ASKED.value,
                    factors=factors,
                )
        
        # 6. Check role appropriateness
        role_suggests = self._what_does_role_suggest(context)
        factors["role_suggests"] = role_suggests
        
        if role_suggests == "mostly_listen":
            logger.debug(
                f"Agent {self.agent.name} role suggests listening"
            )
            return ExternalizationDecision.active_listen(
                confidence=0.7,
                reason="role_is_observer",
                timing=ContributionTiming.WHEN_ASKED.value,
                factors=factors,
            )
        
        # 7. Adjust for group size
        contribution_threshold = self._get_contribution_threshold(context.group_type)
        factors["contribution_threshold"] = contribution_threshold
        factors["group_type"] = context.group_type.value
        
        if relevance < contribution_threshold:
            logger.debug(
                f"Agent {self.agent.name} below threshold "
                f"({relevance:.2f} < {contribution_threshold:.2f}) for group type"
            )
            return ExternalizationDecision.may_contribute(
                confidence=relevance,
                reason="below_threshold_for_group_size",
                timing=ContributionTiming.WHEN_ASKED.value,
                contribution_type=self._determine_contribution_type(stimulus, context),
                factors=factors,
            )
        
        # 8. Passed all checks - should contribute
        contribution_type = self._determine_contribution_type(stimulus, context)
        factors["contribution_type"] = contribution_type
        
        intent = (
            ExternalizationIntent.SHOULD_CONTRIBUTE 
            if relevance > 0.6 
            else ExternalizationIntent.MAY_CONTRIBUTE
        )
        
        logger.debug(
            f"Agent {self.agent.name} deciding to contribute "
            f"(intent={intent.value}, relevance={relevance:.2f})"
        )
        
        if intent == ExternalizationIntent.SHOULD_CONTRIBUTE:
            return ExternalizationDecision.should_contribute(
                confidence=relevance,
                reason="have_valuable_input",
                contribution_type=contribution_type,
                factors=factors,
            )
        else:
            return ExternalizationDecision.may_contribute(
                confidence=relevance,
                reason="have_valuable_input",
                timing=ContributionTiming.NOW.value,
                contribution_type=contribution_type,
                factors=factors,
            )
    
    # ==========================================
    # SELF-AWARENESS METHODS
    # ==========================================
    
    def _am_i_directly_addressed(self, stimulus: Stimulus) -> bool:
        """Check if stimulus is directed at me.
        
        Args:
            stimulus: The incoming stimulus
            
        Returns:
            True if directly addressed
        """
        my_id = str(self.agent.agent_id)
        my_name = self.agent.name
        
        # Check explicit direction
        if stimulus.is_directed_at(my_id, my_name):
            return True
        
        # Check content for name mention
        if stimulus.mentions_agent(my_id, my_name):
            return True
        
        # Check if response is explicitly required
        if stimulus.requires_response and stimulus.is_directed:
            if stimulus.is_directed_at(my_id, my_name):
                return True
        
        return False
    
    def _calculate_expertise_match(self, topic: str) -> float:
        """Calculate how much expertise I have on this topic.
        
        Args:
            topic: The topic to evaluate
            
        Returns:
            Relevance score (0.0 to 1.0)
        """
        if not topic:
            return 0.5  # Unknown topic = medium relevance
        
        keywords = topic.lower().split()
        return self.agent.skills.get_relevance_score(keywords)
    
    def _have_i_said_enough(self, context: SocialContext) -> bool:
        """Check if I'm dominating the conversation.
        
        Args:
            context: The current social context
            
        Returns:
            True if I've contributed more than my fair share
        """
        my_id = str(self.agent.agent_id)
        my_contributions = context.speaking_distribution.get(my_id, 0)
        total_contributions = context.get_total_contributions()
        
        if total_contributions == 0:
            return False
        
        my_share = my_contributions / total_contributions
        fair_share = context.get_fair_share()
        
        # Role adjustment
        role_multiplier = {
            "facilitator": 2.0,
            "leader": 1.5,
            "expert": 1.3,
            "participant": 1.0,
            "junior": 0.8,
            "observer": 0.3,
        }.get(context.my_role, 1.0)
        
        expected_share = fair_share * role_multiplier
        
        # Said enough if > 1.5x expected share
        return my_share > expected_share * 1.5
    
    def _do_i_have_critical_input(self, stimulus: Stimulus) -> bool:
        """Check if I have critical input that must be shared.
        
        Args:
            stimulus: The current stimulus
            
        Returns:
            True if I have critical input
        """
        # Check if I have a high-confidence ready thought
        best = self.mind.get_best_contribution()
        if best and best.confidence > 0.8 and best.thought_type.value == "concern":
            return True
        
        # Check for critical insights in held insights
        for thought in self.mind.held_insights:
            if thought.confidence > 0.85 and thought.thought_type.value == "concern":
                return True
        
        return False
    
    # ==========================================
    # SOCIAL AWARENESS METHODS
    # ==========================================
    
    def _should_defer_to_expert(
        self,
        topic: str,
        context: SocialContext,
    ) -> Tuple[bool, Optional[str]]:
        """Check if someone more qualified is present and should speak first.
        
        Args:
            topic: The topic under discussion
            context: The current social context
            
        Returns:
            Tuple of (should_defer, name_of_expert_to_defer_to)
        """
        my_expertise = self._calculate_expertise_match(topic)
        
        # Extract topic keywords
        keywords = topic.lower().split() if topic else []
        
        for participant in context.participants:
            if participant.agent_id == str(self.agent.agent_id):
                continue
            
            # Estimate their expertise
            their_expertise = self._estimate_participant_expertise(
                participant, keywords
            )
            
            # If they're significantly more qualified and haven't spoken
            if their_expertise > my_expertise + 0.2:
                if not participant.has_spoken:
                    return True, participant.name
        
        return False, None
    
    def _estimate_participant_expertise(
        self,
        participant: ParticipantInfo,
        keywords: List[str],
    ) -> float:
        """Estimate another participant's expertise on keywords.
        
        Args:
            participant: The participant to evaluate
            keywords: Keywords to check expertise against
            
        Returns:
            Estimated expertise score (0.0 to 1.0)
        """
        if not participant.expertise_areas:
            return 0.5  # Unknown = assume moderate
        
        # Check overlap between their expertise and keywords
        expertise_lower = [e.lower() for e in participant.expertise_areas]
        
        matches = 0
        for keyword in keywords:
            for expertise in expertise_lower:
                if keyword in expertise or expertise in keyword:
                    matches += 1
                    break
        
        if not keywords:
            return 0.5
        
        # Base + matches contribution
        return min(1.0, matches / len(keywords) + 0.3)
    
    def _is_there_conversational_space(self, context: SocialContext) -> bool:
        """Check if there's room for me to speak.
        
        Args:
            context: The current social context
            
        Returns:
            True if speaking is appropriate
        """
        # Someone is currently speaking
        if context.current_speaker:
            if context.current_speaker != str(self.agent.agent_id):
                return False
        
        # Closing phase - only critical input
        if context.discussion_phase == DiscussionPhase.CLOSING.value:
            return False
        
        # Heated discussion - consider if helping or inflaming
        if context.energy_level == EnergyLevel.HEATED.value:
            # Only speak if I can calm things
            sm = self.agent.social_markers
            return sm.comfort_with_conflict >= 6
        
        return True
    
    def _what_does_role_suggest(self, context: SocialContext) -> str:
        """What behavior does my role suggest?
        
        Args:
            context: The current social context
            
        Returns:
            Suggested behavior: "contribute_actively", "contribute_selectively", 
            "mostly_listen", etc.
        """
        role_behaviors = {
            "facilitator": "enable_others",
            "expert": "contribute_in_domain",
            "participant": "contribute_when_relevant",
            "observer": "mostly_listen",
            "leader": "guide_and_decide",
            "junior": "learn_and_ask",
        }
        return role_behaviors.get(context.my_role, "assess_situation")
    
    def _get_contribution_threshold(self, group_type: GroupType) -> float:
        """Get threshold for contribution based on group size.
        
        Larger groups require higher expertise relevance to justify
        taking speaking time.
        
        Args:
            group_type: The type of group
            
        Returns:
            Minimum relevance threshold (0.0 to 1.0)
        """
        thresholds = {
            GroupType.SOLO: 0.0,       # Always contribute
            GroupType.PAIR: 0.3,       # Low threshold
            GroupType.SMALL_TEAM: 0.4,
            GroupType.MEETING: 0.5,
            GroupType.LARGE_GROUP: 0.7,
            GroupType.ARMY: 0.9,       # Only if critical
        }
        return thresholds.get(group_type, 0.5)
    
    def _determine_contribution_type(
        self,
        stimulus: Stimulus,
        context: SocialContext,
    ) -> str:
        """Determine what type of contribution to make.
        
        Args:
            stimulus: The current stimulus
            context: The current social context
            
        Returns:
            Contribution type string
        """
        sm = self.agent.social_markers
        
        # If I have high curiosity and there are gaps
        if sm.curiosity >= 7:
            return ContributionType.QUESTION.value
        
        # If I have high facilitation instinct
        if sm.facilitation_instinct >= 7 and context.my_role in ["facilitator", "leader"]:
            return ContributionType.FACILITATION.value
        
        # If I have high assertiveness and there's disagreement
        if sm.assertiveness >= 7 and sm.comfort_with_conflict >= 6:
            return ContributionType.CHALLENGE.value
        
        # Default to statement
        return ContributionType.STATEMENT.value
    
    def evaluate_and_decide(
        self,
        stimulus: Stimulus,
        context: SocialContext,
    ) -> ExternalizationDecision:
        """Convenience method that wraps should_i_speak.
        
        Args:
            stimulus: The incoming stimulus
            context: The current social context
            
        Returns:
            ExternalizationDecision
        """
        return self.should_i_speak(stimulus, context)
    
    def get_speaking_confidence_for_topic(self, topic: str) -> float:
        """Get confidence level for speaking on a specific topic.
        
        Args:
            topic: The topic to evaluate
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        return self._calculate_expertise_match(topic)

