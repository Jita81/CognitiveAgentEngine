"""Behavioral test fixtures and helpers for M1 validation.

These fixtures support testing agent behavior (not just code correctness).
"""

import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional
from uuid import uuid4

import pytest
import pytest_asyncio

from src.agents.models import (
    AgentProfile,
    CommunicationStyle,
    PersonalityMarkers,
    SkillSet,
    SocialMarkers,
)
from src.cognitive import (
    CognitiveTier,
    CognitiveProcessor,
    CognitiveResult,
    Thought,
    create_processor_with_mock_router,
)


# ==========================================
# Test Data Loading
# ==========================================


def load_test_stimuli() -> Dict:
    """Load test stimuli from JSON file."""
    data_path = Path(__file__).parent.parent / "data" / "sample_stimuli.json"
    if data_path.exists():
        with open(data_path) as f:
            return json.load(f)
    # Fallback default stimuli
    return {
        "high_urgency": [
            "ALERT: The production server is down!",
            "Critical security vulnerability detected!",
        ],
        "low_urgency": [
            "Should we migrate to microservices?",
            "What testing strategy should we adopt?",
        ],
        "low_relevance": [
            "What's for lunch today?",
            "Nice weather we're having.",
        ],
    }


# ==========================================
# Agent Profile Factories
# ==========================================


def create_alex_chen() -> AgentProfile:
    """Create Alex Chen - Senior Backend Developer.
    
    High technical skills, confident, pragmatic.
    """
    return AgentProfile(
        agent_id=uuid4(),
        name="Alex Chen",
        role="Senior Backend Developer",
        title="Principal Consultant",
        backstory_summary=(
            "10 years building distributed systems at scale. Led teams of 5-15 engineers. "
            "Specializes in Python and Go backends. Known for pragmatic architecture decisions."
        ),
        years_experience=10,
        skills=SkillSet(
            technical={"python": 9, "go": 7, "system_design": 8, "postgresql": 8, "kubernetes": 6},
            domains={"fintech": 7, "enterprise": 6, "ecommerce": 5},
            soft_skills={"communication": 7, "mentoring": 8, "leadership": 6},
        ),
        personality_markers=PersonalityMarkers(
            openness=7, conscientiousness=8, extraversion=5,
            agreeableness=6, neuroticism=3, perfectionism=6,
            pragmatism=8, risk_tolerance=5,
        ),
        social_markers=SocialMarkers(
            confidence=7, assertiveness=6, deference=4, curiosity=7,
            social_calibration=7, status_sensitivity=5, facilitation_instinct=6,
            comfort_in_spotlight=5, comfort_with_conflict=6,
        ),
        communication_style=CommunicationStyle(
            vocabulary_level="technical", sentence_structure="moderate",
            formality="professional", uses_analogies=True, uses_examples=True,
            asks_clarifying_questions=True,
        ),
        knowledge_domains=["distributed_systems", "api_design", "database_optimization"],
        knowledge_gaps=["frontend", "mobile", "ml_ops"],
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


def create_maya_patel() -> AgentProfile:
    """Create Maya Patel - UX Designer.
    
    Design expertise, empathetic, creative.
    """
    return AgentProfile(
        agent_id=uuid4(),
        name="Maya Patel",
        role="Senior UX Designer",
        title="Design Lead",
        backstory_summary=(
            "8 years crafting user experiences for consumer and enterprise products. "
            "Strong advocate for accessibility and inclusive design."
        ),
        years_experience=8,
        skills=SkillSet(
            technical={"figma": 9, "prototyping": 8, "css": 6, "user_research": 8},
            domains={"consumer_apps": 8, "enterprise_software": 6, "accessibility": 7},
            soft_skills={"empathy": 9, "presentation": 7, "collaboration": 8},
        ),
        personality_markers=PersonalityMarkers(
            openness=9, conscientiousness=7, extraversion=6,
            agreeableness=8, neuroticism=4, perfectionism=7,
            pragmatism=6, risk_tolerance=6,
        ),
        social_markers=SocialMarkers(
            confidence=6, assertiveness=5, deference=6, curiosity=8,
            social_calibration=8, status_sensitivity=4, facilitation_instinct=7,
            comfort_in_spotlight=6, comfort_with_conflict=4,
        ),
        communication_style=CommunicationStyle(
            vocabulary_level="moderate", sentence_structure="elaborate",
            formality="casual", uses_analogies=True, uses_examples=True,
            asks_clarifying_questions=True,
        ),
        knowledge_domains=["design_systems", "user_psychology", "accessibility"],
        knowledge_gaps=["backend", "devops", "data_engineering"],
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


def create_emily_rodriguez() -> AgentProfile:
    """Create Emily Rodriguez - Junior Developer.
    
    Lower confidence, curious, deferential.
    """
    return AgentProfile(
        agent_id=uuid4(),
        name="Emily Rodriguez",
        role="Junior Developer",
        title="Software Engineer I",
        backstory_summary=(
            "1 year of professional experience after bootcamp. Eager learner with strong "
            "fundamentals. Works primarily on frontend but interested in full-stack."
        ),
        years_experience=1,
        skills=SkillSet(
            technical={"javascript": 6, "react": 5, "html_css": 6, "git": 5},
            domains={"web_development": 5},
            soft_skills={"learning": 8, "collaboration": 7, "documentation": 5},
        ),
        personality_markers=PersonalityMarkers(
            openness=8, conscientiousness=7, extraversion=6,
            agreeableness=8, neuroticism=5, perfectionism=4,
            pragmatism=5, risk_tolerance=5,
        ),
        social_markers=SocialMarkers(
            confidence=4, assertiveness=3, deference=8, curiosity=9,
            social_calibration=6, status_sensitivity=7, facilitation_instinct=3,
            comfort_in_spotlight=3, comfort_with_conflict=2,
        ),
        communication_style=CommunicationStyle(
            vocabulary_level="simple", sentence_structure="moderate",
            formality="casual", uses_analogies=False, uses_examples=True,
            asks_clarifying_questions=True,
        ),
        knowledge_domains=["react", "javascript_basics"],
        knowledge_gaps=["backend", "databases", "system_design", "devops"],
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


def create_david_kim() -> AgentProfile:
    """Create David Kim - Tech Lead.
    
    Experienced, facilitative, high leadership skills.
    """
    return AgentProfile(
        agent_id=uuid4(),
        name="David Kim",
        role="Tech Lead",
        title="Engineering Manager",
        backstory_summary=(
            "12 years of engineering experience, 4 years in leadership. Balances hands-on "
            "coding with team management. Strong believer in servant leadership."
        ),
        years_experience=12,
        skills=SkillSet(
            technical={"java": 8, "system_design": 9, "code_review": 9, "architecture": 8},
            domains={"enterprise": 8, "fintech": 7, "healthcare": 5},
            soft_skills={"leadership": 8, "mentoring": 9, "conflict_resolution": 7, "hiring": 7},
        ),
        personality_markers=PersonalityMarkers(
            openness=6, conscientiousness=8, extraversion=6,
            agreeableness=7, neuroticism=3, perfectionism=6,
            pragmatism=7, risk_tolerance=5,
        ),
        social_markers=SocialMarkers(
            confidence=8, assertiveness=6, deference=5, curiosity=6,
            social_calibration=8, status_sensitivity=5, facilitation_instinct=9,
            comfort_in_spotlight=6, comfort_with_conflict=7,
        ),
        communication_style=CommunicationStyle(
            vocabulary_level="moderate", sentence_structure="moderate",
            formality="professional", uses_analogies=True, uses_examples=True,
            asks_clarifying_questions=True,
        ),
        knowledge_domains=["team_leadership", "architecture", "agile"],
        knowledge_gaps=["ml", "frontend_frameworks", "mobile"],
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


# ==========================================
# Analysis Helpers
# ==========================================


def count_hedging_words(text: str) -> int:
    """Count hedging/uncertainty words in text."""
    hedging_words = [
        "maybe", "perhaps", "possibly", "might", "could be",
        "i think", "i believe", "not sure", "uncertain",
        "probably", "seems like", "appears to",
    ]
    text_lower = text.lower()
    return sum(1 for word in hedging_words if word in text_lower)


def count_technical_terms(text: str) -> int:
    """Count technical terms in text."""
    technical_terms = [
        "api", "database", "server", "client", "architecture",
        "microservice", "monolith", "cache", "queue", "endpoint",
        "authentication", "authorization", "latency", "throughput",
        "scalability", "distributed", "kubernetes", "docker",
        "postgresql", "redis", "mongodb", "sql", "nosql",
    ]
    text_lower = text.lower()
    return sum(1 for term in technical_terms if term in text_lower)


def analyze_response_style(thought: Thought) -> Dict:
    """Analyze the style characteristics of a response."""
    content = thought.content
    words = content.split()
    
    return {
        "word_count": len(words),
        "sentence_count": content.count('.') + content.count('!') + content.count('?'),
        "question_count": content.count('?'),
        "hedging_count": count_hedging_words(content),
        "technical_count": count_technical_terms(content),
        "has_structure": any(marker in content for marker in ['1.', '2.', '-', '•', 'First', 'Second']),
        "confidence": thought.confidence,
        "completeness": thought.completeness,
        "thought_type": thought.thought_type.value,
    }


def compare_responses(response_a: CognitiveResult, response_b: CognitiveResult) -> Dict:
    """Compare two cognitive results for statistical differences."""
    if not response_a.primary_thought or not response_b.primary_thought:
        return {"error": "Missing primary thought"}
    
    analysis_a = analyze_response_style(response_a.primary_thought)
    analysis_b = analyze_response_style(response_b.primary_thought)
    
    return {
        "word_count_diff": analysis_a["word_count"] - analysis_b["word_count"],
        "confidence_diff": analysis_a["confidence"] - analysis_b["confidence"],
        "hedging_diff": analysis_a["hedging_count"] - analysis_b["hedging_count"],
        "technical_diff": analysis_a["technical_count"] - analysis_b["technical_count"],
        "a_analysis": analysis_a,
        "b_analysis": analysis_b,
    }


# ==========================================
# Tier Validation Helpers
# ==========================================


def validate_tier_selection(
    urgency: float,
    complexity: float,
    relevance: float,
    result: CognitiveResult,
) -> Dict:
    """Validate that tier selection matches expected strategy."""
    validation = {
        "valid": True,
        "issues": [],
        "urgency": urgency,
        "complexity": complexity,
        "relevance": relevance,
        "tiers_used": [t.name for t in result.tiers_used],
    }
    
    # High urgency + relevant should use REFLEX first
    if urgency > 0.8 and relevance > 0.5:
        if CognitiveTier.REFLEX not in result.tiers_used:
            validation["valid"] = False
            validation["issues"].append("High urgency should use REFLEX")
        if result.thoughts and result.thoughts[0].tier != CognitiveTier.REFLEX:
            validation["valid"] = False
            validation["issues"].append("REFLEX should fire first on high urgency")
    
    # Low urgency + high complexity should skip REFLEX
    if urgency < 0.3 and complexity > 0.7 and relevance > 0.5:
        if CognitiveTier.REFLEX in result.tiers_used:
            validation["issues"].append("Low urgency should skip REFLEX (warning)")
        if CognitiveTier.DELIBERATE not in result.tiers_used:
            validation["valid"] = False
            validation["issues"].append("Complex low-urgency needs DELIBERATE")
    
    # Low relevance should only use REFLEX
    if relevance < 0.3:
        if len(result.tiers_used) > 1:
            validation["issues"].append("Low relevance should minimize tiers (warning)")
    
    return validation


def expected_tier_for_params(urgency: float, complexity: float, relevance: float) -> List[CognitiveTier]:
    """Return expected tiers based on strategy matrix."""
    # From requirements:
    # High urgency + High relevance -> REFLEX → Parallel REACTIVE → Background DELIBERATE
    # High urgency + Low relevance -> REFLEX only
    # Low urgency + High relevance + High complexity -> DELIBERATE → ANALYTICAL
    # Low urgency + High relevance + Low complexity -> REACTIVE → DELIBERATE
    # Low urgency + Low relevance -> REFLEX only
    
    if urgency > 0.8 and relevance > 0.5:
        tiers = [CognitiveTier.REFLEX, CognitiveTier.REACTIVE]
        if complexity > 0.5:
            tiers.append(CognitiveTier.DELIBERATE)
        return tiers
    
    if urgency > 0.8 and relevance <= 0.5:
        return [CognitiveTier.REFLEX]
    
    if urgency < 0.3 and relevance > 0.5:
        if complexity > 0.7:
            return [CognitiveTier.DELIBERATE, CognitiveTier.ANALYTICAL]
        else:
            return [CognitiveTier.DELIBERATE]
    
    if relevance < 0.3:
        return [CognitiveTier.REFLEX]
    
    # Medium everything
    if complexity < 0.5:
        return [CognitiveTier.REACTIVE]
    else:
        return [CognitiveTier.DELIBERATE]


# ==========================================
# Quality Scoring
# ==========================================


def score_response_quality(
    thought: Thought,
    agent: AgentProfile,
    urgency: float,
    complexity: float,
    relevance: float,
) -> Dict:
    """Score the quality of a response on multiple dimensions."""
    scores = {}
    
    # 1. Length appropriateness for tier
    word_count = len(thought.content.split())
    expected_ranges = {
        CognitiveTier.REFLEX: (5, 50),
        CognitiveTier.REACTIVE: (20, 150),
        CognitiveTier.DELIBERATE: (50, 400),
        CognitiveTier.ANALYTICAL: (100, 600),
        CognitiveTier.COMPREHENSIVE: (150, 800),
    }
    min_len, max_len = expected_ranges[thought.tier]
    scores["length_appropriate"] = min_len <= word_count <= max_len
    scores["word_count"] = word_count
    scores["expected_range"] = (min_len, max_len)
    
    # 2. Confidence calibration
    expected_min_confidence = {
        CognitiveTier.REFLEX: 0.4,
        CognitiveTier.REACTIVE: 0.5,
        CognitiveTier.DELIBERATE: 0.65,
        CognitiveTier.ANALYTICAL: 0.75,
        CognitiveTier.COMPREHENSIVE: 0.8,
    }
    scores["confidence_calibrated"] = thought.confidence >= expected_min_confidence[thought.tier]
    
    # 3. Thought type appropriateness
    if thought.tier == CognitiveTier.REFLEX:
        scores["type_appropriate"] = thought.thought_type.value in ["reaction", "observation"]
    else:
        scores["type_appropriate"] = True  # More types are valid for higher tiers
    
    # 4. Overall score
    scores["overall"] = sum([
        scores["length_appropriate"],
        scores["confidence_calibrated"],
        scores["type_appropriate"],
    ]) / 3.0
    
    return scores


# ==========================================
# Pytest Fixtures
# ==========================================


@pytest.fixture
def alex_chen() -> AgentProfile:
    """Senior Backend Developer - high technical skills."""
    return create_alex_chen()


@pytest.fixture
def maya_patel() -> AgentProfile:
    """UX Designer - design expertise."""
    return create_maya_patel()


@pytest.fixture
def emily_rodriguez() -> AgentProfile:
    """Junior Developer - lower confidence."""
    return create_emily_rodriguez()


@pytest.fixture
def david_kim() -> AgentProfile:
    """Tech Lead - facilitative, experienced."""
    return create_david_kim()


@pytest.fixture
def processor_for_alex(alex_chen) -> CognitiveProcessor:
    """Create processor with mock router for Alex Chen."""
    return create_processor_with_mock_router(alex_chen)


@pytest.fixture
def processor_for_maya(maya_patel) -> CognitiveProcessor:
    """Create processor with mock router for Maya Patel."""
    return create_processor_with_mock_router(maya_patel)


@pytest.fixture
def processor_for_emily(emily_rodriguez) -> CognitiveProcessor:
    """Create processor with mock router for Emily Rodriguez."""
    return create_processor_with_mock_router(emily_rodriguez)


@pytest.fixture
def test_stimuli() -> Dict:
    """Load test stimuli."""
    return load_test_stimuli()
