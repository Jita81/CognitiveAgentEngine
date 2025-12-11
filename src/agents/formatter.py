"""Profile formatter for LLM prompts."""

from src.agents.models import AgentProfile


class ProfileFormatter:
    """Format agent profiles for LLM prompts at different cognitive tiers."""

    @staticmethod
    def format_identity_minimal(profile: AgentProfile) -> str:
        """Minimal identity for REFLEX tier (~50 tokens).
        
        Used for immediate reactions where full context isn't needed.
        """
        return f"You are {profile.name}, a {profile.role}."

    @staticmethod
    def format_identity_brief(profile: AgentProfile) -> str:
        """Brief identity for REACTIVE tier (~150 tokens).
        
        Used for quick assessments and tactical decisions.
        """
        top_skills = profile.skills.get_top_skills(3)
        skills_str = ", ".join([s[0].replace("_", " ") for s in top_skills])

        lines = [
            f"You are {profile.name}, a {profile.role}.",
            f"Key skills: {skills_str}.",
        ]

        if profile.years_experience:
            lines.append(f"Experience: {profile.years_experience} years.")

        return "\n".join(lines)

    @staticmethod
    def format_identity_full(profile: AgentProfile) -> str:
        """Full identity for DELIBERATE+ tiers (~400 tokens).
        
        Used for considered responses, synthesis, and complex analysis.
        """
        top_skills = profile.skills.get_top_skills(5)
        skills_str = "\n".join([f"- {s[0].replace('_', ' ')}: {s[1]}/10" for s in top_skills])

        # Build identity section
        identity_parts = [f"You are {profile.name}, a {profile.role}."]
        if profile.title:
            identity_parts[0] = f"You are {profile.name}, {profile.title}, a {profile.role}."

        lines = [
            "IDENTITY:",
            identity_parts[0],
            "",
            f"{profile.backstory_summary}",
            "",
            "SKILLS & EXPERTISE:",
            skills_str,
        ]

        # Add knowledge domains if present
        if profile.knowledge_domains:
            domains = ", ".join(profile.knowledge_domains)
            lines.extend(["", f"Domain expertise: {domains}"])

        # Add communication style
        comm = profile.communication_style
        lines.extend([
            "",
            "COMMUNICATION STYLE:",
            f"- Vocabulary: {comm.vocabulary_level}",
            f"- Formality: {comm.formality}",
            f"- Structure: {comm.sentence_structure}",
        ])

        return "\n".join(lines)

    @staticmethod
    def format_social_context(profile: AgentProfile) -> str:
        """Format social traits for context in prompts.
        
        Used to inform the agent's social behavior in group settings.
        """
        sm = profile.social_markers
        traits = []

        # Confidence
        if sm.confidence >= 7:
            traits.append("You express your views confidently")
        elif sm.confidence <= 3:
            traits.append("You tend to hedge your opinions")

        # Deference
        if sm.deference >= 7:
            traits.append("You readily defer to others' expertise")
        elif sm.deference <= 3:
            traits.append("You stand firm on your positions")

        # Curiosity
        if sm.curiosity >= 7:
            traits.append("You ask probing questions to understand deeply")

        # Facilitation
        if sm.facilitation_instinct >= 7:
            traits.append("You help draw out others' perspectives")

        # Assertiveness
        if sm.assertiveness >= 7:
            traits.append("You advocate strongly for your ideas")
        elif sm.assertiveness <= 3:
            traits.append("You prefer to suggest rather than assert")

        # Conflict comfort
        if sm.comfort_with_conflict >= 7:
            traits.append("You're comfortable engaging in constructive disagreement")
        elif sm.comfort_with_conflict <= 3:
            traits.append("You prefer to find common ground over confrontation")

        # Spotlight comfort
        if sm.comfort_in_spotlight <= 3:
            traits.append("You prefer not to be the center of attention")

        if not traits:
            return "You have a balanced social style."

        return "\n".join([f"- {t}" for t in traits])

    @staticmethod
    def format_personality_context(profile: AgentProfile) -> str:
        """Format personality traits for context in prompts.
        
        Used to inform the agent's thinking style and approach.
        """
        pm = profile.personality_markers
        traits = []

        # Openness
        if pm.openness >= 7:
            traits.append("You're open to novel ideas and unconventional approaches")
        elif pm.openness <= 3:
            traits.append("You prefer proven approaches over experimental ones")

        # Conscientiousness
        if pm.conscientiousness >= 7:
            traits.append("You're detail-oriented and thorough")
        elif pm.conscientiousness <= 3:
            traits.append("You focus on the big picture over details")

        # Pragmatism vs perfectionism
        if pm.pragmatism >= 7:
            traits.append("You favor practical solutions over ideal ones")
        elif pm.perfectionism >= 7:
            traits.append("You strive for excellence and high standards")

        # Risk tolerance
        if pm.risk_tolerance >= 7:
            traits.append("You're comfortable with uncertainty and calculated risks")
        elif pm.risk_tolerance <= 3:
            traits.append("You prefer certainty and well-tested approaches")

        if not traits:
            return "You have a balanced thinking style."

        return "\n".join([f"- {t}" for t in traits])

    @classmethod
    def format_for_tier(
        cls,
        profile: AgentProfile,
        tier: str,
        include_social: bool = False,
        include_personality: bool = False,
    ) -> str:
        """Format profile for a specific cognitive tier.
        
        Args:
            profile: The agent profile to format
            tier: One of "reflex", "reactive", "deliberate", "analytical", "comprehensive"
            include_social: Whether to include social context
            include_personality: Whether to include personality context
        
        Returns:
            Formatted profile string appropriate for the tier
        """
        tier_lower = tier.lower()

        if tier_lower == "reflex":
            return cls.format_identity_minimal(profile)

        elif tier_lower == "reactive":
            return cls.format_identity_brief(profile)

        else:
            # DELIBERATE, ANALYTICAL, COMPREHENSIVE
            parts = [cls.format_identity_full(profile)]

            if include_social:
                social = cls.format_social_context(profile)
                if social:
                    parts.extend(["", "YOUR SOCIAL STYLE:", social])

            if include_personality:
                personality = cls.format_personality_context(profile)
                if personality:
                    parts.extend(["", "YOUR THINKING STYLE:", personality])

            return "\n".join(parts)

