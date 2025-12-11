"""Tiered prompt builder for cognitive processing.

This module builds prompts appropriate for each cognitive tier,
incorporating agent identity, context, and memory at appropriate depths.
"""

from typing import Dict, List, Optional

from src.agents.formatter import ProfileFormatter
from src.agents.models import AgentProfile
from src.cognitive.tiers import CognitiveTier, ContextDepth, TIER_CONFIGS


class TieredPromptBuilder:
    """Builds prompts appropriate for each cognitive tier.
    
    Each tier gets a different level of context and identity information,
    optimized for the tier's token budget and purpose.
    """

    def build(
        self,
        tier: CognitiveTier,
        agent: AgentProfile,
        stimulus: str,
        purpose: str,
        context: Optional[Dict] = None,
    ) -> str:
        """Build prompt for specified cognitive tier.
        
        Args:
            tier: The cognitive tier to build for
            agent: The agent profile to use
            stimulus: The stimulus text to process
            purpose: The purpose of this processing
            context: Optional additional context dict
            
        Returns:
            Formatted prompt string appropriate for the tier
        """
        if tier == CognitiveTier.REFLEX:
            return self._build_reflex(agent, stimulus)
        elif tier == CognitiveTier.REACTIVE:
            return self._build_reactive(agent, stimulus, purpose, context)
        elif tier == CognitiveTier.DELIBERATE:
            return self._build_deliberate(agent, stimulus, purpose, context)
        elif tier == CognitiveTier.ANALYTICAL:
            return self._build_analytical(agent, stimulus, purpose, context)
        else:  # COMPREHENSIVE
            return self._build_comprehensive(agent, stimulus, purpose, context)

    def _build_reflex(
        self,
        agent: AgentProfile,
        stimulus: str,
    ) -> str:
        """Build minimal prompt for REFLEX tier.
        
        Optimized for speed: minimal context, immediate reaction.
        Target: ~100 context tokens, ~150 response tokens.
        """
        identity = ProfileFormatter.format_identity_minimal(agent)

        return f"""{identity}

STIMULUS: {stimulus}

IMMEDIATE REACTION (one brief thought):"""

    def _build_reactive(
        self,
        agent: AgentProfile,
        stimulus: str,
        purpose: str,
        context: Optional[Dict],
    ) -> str:
        """Build quick assessment prompt for REACTIVE tier.
        
        Quick but more considered than REFLEX.
        Target: ~300 context tokens, ~400 response tokens.
        """
        identity = ProfileFormatter.format_identity_brief(agent)

        # Add recent context if available
        recent_context = ""
        if context and context.get("recent_turns"):
            recent_context = f"\nRECENT CONTEXT:\n{context['recent_turns']}"

        return f"""{identity}{recent_context}

SITUATION: {stimulus}

PURPOSE: {purpose}

Your quick assessment (2-3 sentences):"""

    def _build_deliberate(
        self,
        agent: AgentProfile,
        stimulus: str,
        purpose: str,
        context: Optional[Dict],
    ) -> str:
        """Build considered response prompt for DELIBERATE tier.
        
        Full identity, social context, and memory access.
        Target: ~600 context tokens, ~1200 response tokens.
        """
        identity = ProfileFormatter.format_identity_full(agent)
        social = ProfileFormatter.format_social_context(agent)

        # Build context sections
        memory_context = ""
        if context and context.get("relevant_memory"):
            memory_context = f"\nRELEVANT MEMORY:\n{context['relevant_memory']}"

        prior_thoughts = ""
        if context and context.get("prior_thoughts"):
            prior_thoughts = f"\nYOUR THINKING SO FAR:\n{context['prior_thoughts']}"

        return f"""{identity}

YOUR SOCIAL STYLE:
{social}
{memory_context}{prior_thoughts}

SITUATION:
{stimulus}

PURPOSE: {purpose}

Provide your considered thoughts:"""

    def _build_analytical(
        self,
        agent: AgentProfile,
        stimulus: str,
        purpose: str,
        context: Optional[Dict],
    ) -> str:
        """Build deep analysis prompt for ANALYTICAL tier.
        
        Full context with structured analysis framework.
        Target: ~1000 context tokens, ~2500 response tokens.
        """
        identity = ProfileFormatter.format_identity_full(agent)
        
        # Build comprehensive context sections
        sections = [identity]

        if context:
            if context.get("relevant_memory"):
                sections.append(f"RELEVANT EXPERIENCE:\n{context['relevant_memory']}")
            if context.get("patterns"):
                sections.append(f"PATTERNS YOU'VE LEARNED:\n{context['patterns']}")
            if context.get("relationships"):
                sections.append(f"RELATIONSHIP CONTEXT:\n{context['relationships']}")
            if context.get("prior_thoughts"):
                sections.append(f"YOUR THINKING PROCESS:\n{context['prior_thoughts']}")

        sections.append(f"SITUATION:\n{stimulus}")
        sections.append(f"PURPOSE: {purpose}")
        sections.append("""Provide thorough analysis:
1. What's really going on here?
2. What do I know that's relevant?
3. What patterns apply?
4. What are the risks/opportunities?
5. What's my considered position?""")

        return "\n\n".join(sections)

    def _build_comprehensive(
        self,
        agent: AgentProfile,
        stimulus: str,
        purpose: str,
        context: Optional[Dict],
    ) -> str:
        """Build maximum depth prompt for COMPREHENSIVE tier.
        
        Maximum context and depth, including personality.
        Target: ~1500 context tokens, ~4000 response tokens.
        """
        identity = ProfileFormatter.format_identity_full(agent)
        social = ProfileFormatter.format_social_context(agent)
        personality = ProfileFormatter.format_personality_context(agent)
        
        # Build all context sections
        sections = [identity]
        
        sections.append(f"YOUR SOCIAL STYLE:\n{social}")
        sections.append(f"YOUR THINKING STYLE:\n{personality}")

        if context:
            if context.get("relevant_memory"):
                sections.append(f"RELEVANT EXPERIENCE:\n{context['relevant_memory']}")
            if context.get("patterns"):
                sections.append(f"PATTERNS YOU'VE LEARNED:\n{context['patterns']}")
            if context.get("relationships"):
                sections.append(f"RELATIONSHIP CONTEXT:\n{context['relationships']}")
            if context.get("prior_thoughts"):
                sections.append(f"YOUR THINKING PROCESS:\n{context['prior_thoughts']}")
            if context.get("project_history"):
                sections.append(f"PROJECT HISTORY:\n{context['project_history']}")

        sections.append(f"SITUATION:\n{stimulus}")
        sections.append(f"PURPOSE: {purpose}")
        sections.append("""Provide comprehensive analysis:
1. What's really going on here? Consider multiple perspectives.
2. What do I know that's relevant? Draw from all my experience.
3. What patterns apply? Think about similar situations I've encountered.
4. What are the risks and opportunities? Be thorough.
5. Who else should be involved and why?
6. What's my considered position? Support with reasoning.
7. What would I recommend as next steps?""")

        return "\n\n".join(sections)

    def get_prompt_estimate(
        self,
        tier: CognitiveTier,
        context_size: int = 0,
    ) -> Dict[str, int]:
        """Estimate prompt sizes for a tier.
        
        Args:
            tier: The cognitive tier
            context_size: Size of context in approximate tokens
            
        Returns:
            Dictionary with estimated token counts
        """
        config = TIER_CONFIGS[tier]
        
        # Base prompt overhead estimates
        base_sizes = {
            CognitiveTier.REFLEX: 30,
            CognitiveTier.REACTIVE: 80,
            CognitiveTier.DELIBERATE: 200,
            CognitiveTier.ANALYTICAL: 350,
            CognitiveTier.COMPREHENSIVE: 500,
        }
        
        base = base_sizes[tier]
        total_context = min(base + context_size, config.max_context_tokens)
        
        return {
            "base_tokens": base,
            "context_tokens": context_size,
            "total_context_tokens": total_context,
            "max_response_tokens": config.max_tokens,
            "tier": tier.name,
        }

    @staticmethod
    def truncate_context(
        content: str,
        max_chars: int,
        suffix: str = "...[truncated]",
    ) -> str:
        """Truncate content to fit within character limit.
        
        Args:
            content: Content to truncate
            max_chars: Maximum characters
            suffix: Suffix to add if truncated
            
        Returns:
            Truncated content
        """
        if len(content) <= max_chars:
            return content
        return content[: max_chars - len(suffix)] + suffix

    @staticmethod
    def format_prior_thoughts(thoughts: List[str], max_count: int = 3) -> str:
        """Format prior thoughts for inclusion in context.
        
        Args:
            thoughts: List of thought content strings
            max_count: Maximum number to include
            
        Returns:
            Formatted string of prior thoughts
        """
        if not thoughts:
            return ""
        
        recent = thoughts[-max_count:]
        return "\n".join([f"- {t}" for t in recent])

