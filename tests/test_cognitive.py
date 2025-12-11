"""Comprehensive tests for the cognitive processing system (Phase 3).

Tests cover:
- Tier configurations
- Thought and CognitiveResult models
- TieredPromptBuilder
- CognitiveProcessor with strategy planning
- Parallel execution
- API endpoints
"""

import asyncio
from datetime import datetime, timezone
from uuid import uuid4

import pytest

from src.agents.models import (
    AgentProfile,
    AgentProfileCreate,
    CommunicationStyle,
    PersonalityMarkers,
    SkillSet,
    SocialMarkers,
)
from src.cognitive import (
    CognitiveTier,
    CognitiveProcessor,
    CognitiveResult,
    ContextDepth,
    MemoryAccess,
    ProcessingStrategy,
    ResponseFormat,
    TierConfig,
    Thought,
    ThoughtType,
    TieredPromptBuilder,
    TIER_CONFIGS,
    create_processor_with_mock_router,
    get_all_tier_configs,
    get_tier_config,
)


# ==========================================
# Fixtures
# ==========================================


@pytest.fixture
def sample_agent_profile() -> AgentProfile:
    """Create a sample agent profile for testing."""
    return AgentProfile(
        agent_id=uuid4(),
        name="Dr. Sarah Chen",
        role="Senior Software Architect",
        title="Principal Engineer",
        backstory_summary=(
            "Dr. Sarah Chen is a senior software architect with 15 years of experience "
            "in distributed systems and cloud architecture. She specializes in designing "
            "scalable microservices and has led teams at multiple Fortune 500 companies."
        ),
        years_experience=15,
        skills=SkillSet(
            technical={
                "python": 9,
                "distributed_systems": 9,
                "cloud_architecture": 8,
                "kubernetes": 7,
                "databases": 8,
            },
            domains={
                "system_design": 9,
                "performance_optimization": 8,
                "security": 7,
            },
            soft_skills={
                "leadership": 8,
                "communication": 8,
                "mentoring": 7,
            },
        ),
        personality_markers=PersonalityMarkers(
            openness=8,
            conscientiousness=9,
            extraversion=6,
            agreeableness=7,
            neuroticism=3,
            perfectionism=7,
            pragmatism=8,
            risk_tolerance=6,
        ),
        social_markers=SocialMarkers(
            confidence=8,
            assertiveness=7,
            deference=5,
            curiosity=9,
            social_calibration=8,
            status_sensitivity=4,
            facilitation_instinct=7,
            comfort_in_spotlight=6,
            comfort_with_conflict=7,
        ),
        communication_style=CommunicationStyle(
            vocabulary_level="technical",
            sentence_structure="moderate",
            formality="professional",
            uses_analogies=True,
            uses_examples=True,
            asks_clarifying_questions=True,
        ),
        knowledge_domains=["distributed systems", "cloud computing", "python"],
        knowledge_gaps=["machine learning", "frontend development"],
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def prompt_builder() -> TieredPromptBuilder:
    """Create a prompt builder instance."""
    return TieredPromptBuilder()


# ==========================================
# Tier Configuration Tests
# ==========================================


class TestTierConfiguration:
    """Tests for cognitive tier configuration."""

    def test_all_tiers_defined(self):
        """Test that all 5 cognitive tiers are defined."""
        assert len(CognitiveTier) == 5
        assert CognitiveTier.REFLEX.value == 0
        assert CognitiveTier.REACTIVE.value == 1
        assert CognitiveTier.DELIBERATE.value == 2
        assert CognitiveTier.ANALYTICAL.value == 3
        assert CognitiveTier.COMPREHENSIVE.value == 4

    def test_all_tiers_have_config(self):
        """Test that every tier has a configuration."""
        for tier in CognitiveTier:
            assert tier in TIER_CONFIGS
            config = TIER_CONFIGS[tier]
            assert isinstance(config, TierConfig)

    def test_reflex_config(self):
        """Test REFLEX tier configuration matches spec."""
        config = get_tier_config(CognitiveTier.REFLEX)
        assert config.max_tokens == 150
        assert config.target_latency_ms == 200
        assert config.memory_access == MemoryAccess.CACHED
        assert config.context_depth == ContextDepth.MINIMAL
        assert config.runs_parallel is True
        assert config.can_interrupt is False
        assert config.response_format == ResponseFormat.BRIEF

    def test_reactive_config(self):
        """Test REACTIVE tier configuration matches spec."""
        config = get_tier_config(CognitiveTier.REACTIVE)
        assert config.max_tokens == 400
        assert config.target_latency_ms == 500
        assert config.memory_access == MemoryAccess.RECENT
        assert config.context_depth == ContextDepth.SHALLOW
        assert config.runs_parallel is True

    def test_deliberate_config(self):
        """Test DELIBERATE tier configuration matches spec."""
        config = get_tier_config(CognitiveTier.DELIBERATE)
        assert config.max_tokens == 1200
        assert config.target_latency_ms == 2000
        assert config.memory_access == MemoryAccess.INDEXED
        assert config.context_depth == ContextDepth.STANDARD
        assert config.runs_parallel is False

    def test_analytical_config(self):
        """Test ANALYTICAL tier configuration matches spec."""
        config = get_tier_config(CognitiveTier.ANALYTICAL)
        assert config.max_tokens == 2500
        assert config.target_latency_ms == 5000
        assert config.memory_access == MemoryAccess.FULL_SEARCH
        assert config.context_depth == ContextDepth.DEEP
        assert config.runs_parallel is False

    def test_comprehensive_config(self):
        """Test COMPREHENSIVE tier configuration matches spec."""
        config = get_tier_config(CognitiveTier.COMPREHENSIVE)
        assert config.max_tokens == 4000
        assert config.target_latency_ms == 10000
        assert config.memory_access == MemoryAccess.FULL_SEARCH
        assert config.context_depth == ContextDepth.FULL
        assert config.runs_parallel is False

    def test_token_limits_increase_with_tier(self):
        """Test that token limits increase with tier level."""
        prev_tokens = 0
        for tier in CognitiveTier:
            config = get_tier_config(tier)
            assert config.max_tokens > prev_tokens
            prev_tokens = config.max_tokens

    def test_get_all_tier_configs(self):
        """Test getting all tier configs as dictionaries."""
        configs = get_all_tier_configs()
        assert len(configs) == 5
        assert "REFLEX" in configs
        assert "COMPREHENSIVE" in configs
        assert configs["REFLEX"]["max_tokens"] == 150

    def test_tier_config_to_dict(self):
        """Test TierConfig to_dict method."""
        config = get_tier_config(CognitiveTier.REFLEX)
        d = config.to_dict()
        assert d["tier"] == "REFLEX"
        assert d["max_tokens"] == 150
        assert d["memory_access"] == "cached"
        assert d["context_depth"] == "minimal"


# ==========================================
# Thought Model Tests
# ==========================================


class TestThoughtModel:
    """Tests for the Thought model."""

    def test_thought_creation(self):
        """Test creating a Thought."""
        thought = Thought(
            tier=CognitiveTier.REACTIVE,
            content="This is an interesting observation.",
            thought_type=ThoughtType.OBSERVATION,
            trigger="test",
            confidence=0.7,
            completeness=0.8,
        )
        assert thought.tier == CognitiveTier.REACTIVE
        assert thought.content == "This is an interesting observation."
        assert thought.thought_type == ThoughtType.OBSERVATION
        assert thought.confidence == 0.7
        assert thought.completeness == 0.8
        assert thought.externalized is False
        assert thought.still_relevant is True

    def test_thought_id_generated(self):
        """Test that thought_id is automatically generated."""
        thought = Thought(
            tier=CognitiveTier.REFLEX,
            content="Quick reaction",
            thought_type=ThoughtType.REACTION,
            trigger="test",
        )
        assert thought.thought_id is not None

    def test_thought_created_at_generated(self):
        """Test that created_at is automatically generated."""
        thought = Thought(
            tier=CognitiveTier.REFLEX,
            content="Quick reaction",
            thought_type=ThoughtType.REACTION,
            trigger="test",
        )
        assert thought.created_at is not None
        assert thought.created_at <= datetime.now(timezone.utc)

    def test_thought_to_dict(self):
        """Test Thought to_dict method."""
        thought = Thought(
            tier=CognitiveTier.DELIBERATE,
            content="This needs careful consideration.",
            thought_type=ThoughtType.INSIGHT,
            trigger="analysis",
            confidence=0.8,
            completeness=0.9,
        )
        d = thought.to_dict()
        assert d["tier"] == "DELIBERATE"
        assert d["thought_type"] == "insight"
        assert d["confidence"] == 0.8
        assert d["completeness"] == 0.9

    def test_all_thought_types(self):
        """Test all thought types are accessible."""
        assert ThoughtType.INSIGHT.value == "insight"
        assert ThoughtType.CONCERN.value == "concern"
        assert ThoughtType.QUESTION.value == "question"
        assert ThoughtType.OBSERVATION.value == "observation"
        assert ThoughtType.PLAN.value == "plan"
        assert ThoughtType.REACTION.value == "reaction"

    def test_thought_confidence_bounds(self):
        """Test thought confidence must be 0-1."""
        with pytest.raises(ValueError):
            Thought(
                tier=CognitiveTier.REFLEX,
                content="Test",
                thought_type=ThoughtType.REACTION,
                trigger="test",
                confidence=1.5,  # Invalid
            )

    def test_thought_completeness_bounds(self):
        """Test thought completeness must be 0-1."""
        with pytest.raises(ValueError):
            Thought(
                tier=CognitiveTier.REFLEX,
                content="Test",
                thought_type=ThoughtType.REACTION,
                trigger="test",
                completeness=-0.1,  # Invalid
            )


# ==========================================
# CognitiveResult Tests
# ==========================================


class TestCognitiveResult:
    """Tests for the CognitiveResult model."""

    def test_cognitive_result_creation(self):
        """Test creating a CognitiveResult."""
        thoughts = [
            Thought(
                tier=CognitiveTier.REFLEX,
                content="Quick thought",
                thought_type=ThoughtType.REACTION,
                trigger="test",
                confidence=0.5,
            ),
            Thought(
                tier=CognitiveTier.REACTIVE,
                content="More considered thought",
                thought_type=ThoughtType.INSIGHT,
                trigger="test",
                confidence=0.7,
            ),
        ]
        result = CognitiveResult(
            thoughts=thoughts,
            primary_thought=thoughts[1],
            processing_time_ms=150.5,
            tiers_used=[CognitiveTier.REFLEX, CognitiveTier.REACTIVE],
        )
        assert len(result.thoughts) == 2
        assert result.primary_thought == thoughts[1]
        assert result.processing_time_ms == 150.5
        assert len(result.tiers_used) == 2

    def test_cognitive_result_thought_count(self):
        """Test thought_count property."""
        thoughts = [
            Thought(
                tier=CognitiveTier.REFLEX,
                content="T1",
                thought_type=ThoughtType.REACTION,
                trigger="test",
            ),
            Thought(
                tier=CognitiveTier.REFLEX,
                content="T2",
                thought_type=ThoughtType.REACTION,
                trigger="test",
            ),
            Thought(
                tier=CognitiveTier.REACTIVE,
                content="T3",
                thought_type=ThoughtType.INSIGHT,
                trigger="test",
            ),
        ]
        result = CognitiveResult(thoughts=thoughts)
        assert result.thought_count == 3

    def test_cognitive_result_avg_confidence(self):
        """Test avg_confidence property."""
        thoughts = [
            Thought(
                tier=CognitiveTier.REFLEX,
                content="T1",
                thought_type=ThoughtType.REACTION,
                trigger="test",
                confidence=0.5,
            ),
            Thought(
                tier=CognitiveTier.REACTIVE,
                content="T2",
                thought_type=ThoughtType.INSIGHT,
                trigger="test",
                confidence=0.7,
            ),
        ]
        result = CognitiveResult(thoughts=thoughts)
        assert result.avg_confidence == pytest.approx(0.6)

    def test_cognitive_result_highest_tier(self):
        """Test highest_tier_used property."""
        result = CognitiveResult(
            tiers_used=[CognitiveTier.REFLEX, CognitiveTier.DELIBERATE, CognitiveTier.REACTIVE]
        )
        assert result.highest_tier_used == CognitiveTier.DELIBERATE

    def test_cognitive_result_to_dict(self):
        """Test CognitiveResult to_dict method."""
        result = CognitiveResult(
            thoughts=[],
            processing_time_ms=100.0,
            tiers_used=[CognitiveTier.REFLEX],
            agent_id=uuid4(),
        )
        d = result.to_dict()
        assert d["processing_time_ms"] == 100.0
        assert d["tiers_used"] == ["REFLEX"]
        assert d["thought_count"] == 0


# ==========================================
# TieredPromptBuilder Tests
# ==========================================


class TestTieredPromptBuilder:
    """Tests for the TieredPromptBuilder."""

    def test_reflex_prompt_minimal(self, sample_agent_profile, prompt_builder):
        """Test REFLEX prompt is minimal."""
        prompt = prompt_builder.build(
            tier=CognitiveTier.REFLEX,
            agent=sample_agent_profile,
            stimulus="What do you think?",
            purpose="test",
        )
        assert "Dr. Sarah Chen" in prompt
        assert "Senior Software Architect" in prompt
        assert "STIMULUS" in prompt
        assert "IMMEDIATE REACTION" in prompt
        # Should not contain full backstory
        assert "Fortune 500" not in prompt

    def test_reactive_prompt_brief(self, sample_agent_profile, prompt_builder):
        """Test REACTIVE prompt is brief but more detailed."""
        prompt = prompt_builder.build(
            tier=CognitiveTier.REACTIVE,
            agent=sample_agent_profile,
            stimulus="Should we refactor this service?",
            purpose="assessment",
            context={"recent_turns": "Alice: The service is getting slow."},
        )
        assert "Dr. Sarah Chen" in prompt
        assert "Key skills:" in prompt
        assert "SITUATION:" in prompt
        assert "PURPOSE: assessment" in prompt
        assert "quick assessment" in prompt
        assert "RECENT CONTEXT:" in prompt

    def test_deliberate_prompt_full(self, sample_agent_profile, prompt_builder):
        """Test DELIBERATE prompt includes full identity."""
        prompt = prompt_builder.build(
            tier=CognitiveTier.DELIBERATE,
            agent=sample_agent_profile,
            stimulus="Design a new microservices architecture.",
            purpose="design",
            context={"relevant_memory": "Previously worked on similar project."},
        )
        assert "IDENTITY:" in prompt
        assert "SKILLS & EXPERTISE:" in prompt
        assert "COMMUNICATION STYLE:" in prompt
        assert "YOUR SOCIAL STYLE:" in prompt
        assert "RELEVANT MEMORY:" in prompt
        assert "considered thoughts" in prompt

    def test_analytical_prompt_structured(self, sample_agent_profile, prompt_builder):
        """Test ANALYTICAL prompt has analysis structure."""
        prompt = prompt_builder.build(
            tier=CognitiveTier.ANALYTICAL,
            agent=sample_agent_profile,
            stimulus="Evaluate the risks of this migration.",
            purpose="risk_analysis",
            context={
                "relevant_memory": "Past migration experience.",
                "patterns": "Common migration pitfalls.",
            },
        )
        assert "RELEVANT EXPERIENCE:" in prompt
        assert "PATTERNS YOU'VE LEARNED:" in prompt
        assert "thorough analysis" in prompt
        assert "What's really going on here?" in prompt
        assert "risks/opportunities" in prompt

    def test_comprehensive_prompt_maximum(self, sample_agent_profile, prompt_builder):
        """Test COMPREHENSIVE prompt includes everything."""
        prompt = prompt_builder.build(
            tier=CognitiveTier.COMPREHENSIVE,
            agent=sample_agent_profile,
            stimulus="Plan the entire system redesign.",
            purpose="strategic_planning",
            context={
                "relevant_memory": "Experience",
                "patterns": "Patterns",
                "relationships": "Team dynamics",
                "project_history": "Past projects",
            },
        )
        assert "YOUR SOCIAL STYLE:" in prompt
        assert "YOUR THINKING STYLE:" in prompt
        assert "PROJECT HISTORY:" in prompt
        assert "comprehensive analysis" in prompt
        assert "Who else should be involved" in prompt

    def test_all_tiers_include_agent_identity(self, sample_agent_profile, prompt_builder):
        """Test that all tiers include some form of agent identity."""
        for tier in CognitiveTier:
            prompt = prompt_builder.build(
                tier=tier,
                agent=sample_agent_profile,
                stimulus="Test stimulus",
                purpose="test",
            )
            assert "Dr. Sarah Chen" in prompt

    def test_prior_thoughts_included(self, sample_agent_profile, prompt_builder):
        """Test that prior thoughts are included in DELIBERATE+ tiers."""
        prior_thoughts = ["First observation", "Second analysis"]
        formatted = TieredPromptBuilder.format_prior_thoughts(prior_thoughts)
        assert "- First observation" in formatted
        assert "- Second analysis" in formatted

    def test_context_truncation(self, prompt_builder):
        """Test context truncation utility."""
        long_content = "x" * 1000
        truncated = prompt_builder.truncate_context(long_content, max_chars=100)
        assert len(truncated) == 100
        assert truncated.endswith("...[truncated]")


# ==========================================
# CognitiveProcessor Tests
# ==========================================


class TestCognitiveProcessor:
    """Tests for the CognitiveProcessor."""

    @pytest.mark.asyncio
    async def test_processor_creation(self, sample_agent_profile):
        """Test creating a CognitiveProcessor."""
        processor = create_processor_with_mock_router(sample_agent_profile)
        assert processor.agent == sample_agent_profile
        assert processor.router is not None

    @pytest.mark.asyncio
    async def test_high_urgency_strategy(self, sample_agent_profile):
        """Test strategy planning for high urgency + relevant stimulus."""
        processor = create_processor_with_mock_router(sample_agent_profile)
        strategy = processor._plan_strategy(
            urgency=0.9,  # High
            complexity=0.6,  # Medium-high
            relevance=0.7,  # Relevant
        )
        # Should start with REFLEX
        assert strategy.steps[0]["tier"] == CognitiveTier.REFLEX
        # Should have parallel REACTIVE
        assert any(
            s["tier"] == CognitiveTier.REACTIVE and s.get("parallel")
            for s in strategy.steps
        )
        # With complexity > 0.5, should include DELIBERATE
        assert any(s["tier"] == CognitiveTier.DELIBERATE for s in strategy.steps)

    @pytest.mark.asyncio
    async def test_low_urgency_strategy(self, sample_agent_profile):
        """Test strategy for low urgency + high complexity."""
        processor = create_processor_with_mock_router(sample_agent_profile)
        strategy = processor._plan_strategy(
            urgency=0.2,  # Low
            complexity=0.8,  # High
            relevance=0.6,  # Relevant
        )
        # Should go straight to DELIBERATE
        assert strategy.steps[0]["tier"] == CognitiveTier.DELIBERATE
        # With high complexity, should include ANALYTICAL
        assert any(s["tier"] == CognitiveTier.ANALYTICAL for s in strategy.steps)

    @pytest.mark.asyncio
    async def test_low_relevance_strategy(self, sample_agent_profile):
        """Test strategy for low relevance stimulus."""
        processor = create_processor_with_mock_router(sample_agent_profile)
        strategy = processor._plan_strategy(
            urgency=0.5,
            complexity=0.5,
            relevance=0.2,  # Low
        )
        # Should only use REFLEX
        assert len(strategy.steps) == 1
        assert strategy.steps[0]["tier"] == CognitiveTier.REFLEX

    @pytest.mark.asyncio
    async def test_medium_complexity_low_strategy(self, sample_agent_profile):
        """Test strategy for medium urgency + low complexity."""
        processor = create_processor_with_mock_router(sample_agent_profile)
        strategy = processor._plan_strategy(
            urgency=0.5,  # Medium
            complexity=0.3,  # Low
            relevance=0.6,  # Relevant
        )
        # Should use REACTIVE
        assert strategy.steps[0]["tier"] == CognitiveTier.REACTIVE

    @pytest.mark.asyncio
    async def test_medium_complexity_high_strategy(self, sample_agent_profile):
        """Test strategy for medium urgency + high complexity."""
        processor = create_processor_with_mock_router(sample_agent_profile)
        strategy = processor._plan_strategy(
            urgency=0.5,  # Medium
            complexity=0.7,  # High
            relevance=0.6,  # Relevant
        )
        # Should use DELIBERATE
        assert strategy.steps[0]["tier"] == CognitiveTier.DELIBERATE

    @pytest.mark.asyncio
    async def test_process_produces_thoughts(self, sample_agent_profile):
        """Test that processing produces thoughts."""
        processor = create_processor_with_mock_router(sample_agent_profile)
        result = await processor.process(
            stimulus="What do you think about microservices?",
            urgency=0.5,
            complexity=0.5,
            relevance=0.7,
        )
        assert result.thought_count > 0
        assert result.primary_thought is not None
        assert result.processing_time_ms > 0

    @pytest.mark.asyncio
    async def test_process_with_tier_override(self, sample_agent_profile):
        """Test processing with specific tier."""
        processor = create_processor_with_mock_router(sample_agent_profile)
        thought = await processor.process_with_tier_override(
            stimulus="Quick question",
            tier=CognitiveTier.REFLEX,
            purpose="test",
        )
        assert thought.tier == CognitiveTier.REFLEX
        assert thought.content is not None

    @pytest.mark.asyncio
    async def test_parallel_execution(self, sample_agent_profile):
        """Test parallel execution produces multiple thoughts."""
        processor = create_processor_with_mock_router(sample_agent_profile)
        result = await processor.process(
            stimulus="Urgent critical decision needed!",
            urgency=0.95,  # Very high urgency triggers parallel
            complexity=0.3,
            relevance=0.8,
        )
        # Should have multiple thoughts from parallel REACTIVE
        reactive_thoughts = [t for t in result.thoughts if t.tier == CognitiveTier.REACTIVE]
        # High urgency should trigger parallel REACTIVE
        assert len(reactive_thoughts) >= 1

    @pytest.mark.asyncio
    async def test_thought_type_inference_concern(self, sample_agent_profile):
        """Test thought type inference for concerns."""
        processor = create_processor_with_mock_router(sample_agent_profile)
        thought_type = processor._infer_thought_type(
            purpose="analysis",
            content="I'm concerned about the risk of data loss.",
        )
        assert thought_type == ThoughtType.CONCERN

    @pytest.mark.asyncio
    async def test_thought_type_inference_question(self, sample_agent_profile):
        """Test thought type inference for questions."""
        processor = create_processor_with_mock_router(sample_agent_profile)
        thought_type = processor._infer_thought_type(
            purpose="analysis",
            content="What if we tried a different approach?",
        )
        assert thought_type == ThoughtType.QUESTION

    @pytest.mark.asyncio
    async def test_thought_type_inference_reaction(self, sample_agent_profile):
        """Test thought type inference for reactions."""
        processor = create_processor_with_mock_router(sample_agent_profile)
        thought_type = processor._infer_thought_type(
            purpose="immediate_response",
            content="That's interesting!",
        )
        assert thought_type == ThoughtType.REACTION

    @pytest.mark.asyncio
    async def test_thought_type_inference_plan(self, sample_agent_profile):
        """Test thought type inference for plans."""
        processor = create_processor_with_mock_router(sample_agent_profile)
        thought_type = processor._infer_thought_type(
            purpose="analysis",
            content="We should consider implementing caching first.",
        )
        assert thought_type == ThoughtType.PLAN

    @pytest.mark.asyncio
    async def test_confidence_estimation_by_tier(self, sample_agent_profile):
        """Test that confidence increases with tier level."""
        processor = create_processor_with_mock_router(sample_agent_profile)
        
        # Mock response with no hedging
        class MockResponse:
            text = "A clear and confident statement."
            completion_tokens = 50
        
        reflex_conf = processor._estimate_confidence(CognitiveTier.REFLEX, MockResponse())
        deliberate_conf = processor._estimate_confidence(CognitiveTier.DELIBERATE, MockResponse())
        analytical_conf = processor._estimate_confidence(CognitiveTier.ANALYTICAL, MockResponse())
        
        assert reflex_conf < deliberate_conf < analytical_conf

    @pytest.mark.asyncio
    async def test_confidence_reduced_by_hedging(self, sample_agent_profile):
        """Test that hedging language reduces confidence."""
        processor = create_processor_with_mock_router(sample_agent_profile)
        
        class ConfidentResponse:
            text = "This is definitely the right approach."
            completion_tokens = 50
        
        class HedgingResponse:
            text = "Maybe possibly perhaps this might be an approach."
            completion_tokens = 50
        
        confident_score = processor._estimate_confidence(CognitiveTier.REACTIVE, ConfidentResponse())
        hedging_score = processor._estimate_confidence(CognitiveTier.REACTIVE, HedgingResponse())
        
        assert hedging_score < confident_score

    @pytest.mark.asyncio
    async def test_completeness_estimation(self, sample_agent_profile):
        """Test completeness estimation based on token utilization."""
        processor = create_processor_with_mock_router(sample_agent_profile)
        
        class LowUtilResponse:
            completion_tokens = 20  # Low utilization of 150 max
        
        class HighUtilResponse:
            completion_tokens = 130  # High utilization of 150 max
        
        low_completeness = processor._estimate_completeness(CognitiveTier.REFLEX, LowUtilResponse())
        high_completeness = processor._estimate_completeness(CognitiveTier.REFLEX, HighUtilResponse())
        
        assert low_completeness < high_completeness

    @pytest.mark.asyncio
    async def test_primary_thought_selection(self, sample_agent_profile):
        """Test primary thought selection favors higher tier and confidence."""
        processor = create_processor_with_mock_router(sample_agent_profile)
        
        thoughts = [
            Thought(
                tier=CognitiveTier.REFLEX,
                content="Quick",
                thought_type=ThoughtType.REACTION,
                trigger="test",
                confidence=0.5,
                completeness=0.5,
            ),
            Thought(
                tier=CognitiveTier.DELIBERATE,
                content="Considered",
                thought_type=ThoughtType.INSIGHT,
                trigger="test",
                confidence=0.8,
                completeness=0.9,
            ),
            Thought(
                tier=CognitiveTier.REACTIVE,
                content="Medium",
                thought_type=ThoughtType.OBSERVATION,
                trigger="test",
                confidence=0.6,
                completeness=0.7,
            ),
        ]
        
        primary = processor._select_primary_thought(thoughts)
        assert primary.tier == CognitiveTier.DELIBERATE

    @pytest.mark.asyncio
    async def test_process_records_tiers_used(self, sample_agent_profile):
        """Test that process records which tiers were used."""
        processor = create_processor_with_mock_router(sample_agent_profile)
        result = await processor.process(
            stimulus="Test stimulus",
            urgency=0.5,
            complexity=0.5,
            relevance=0.6,
        )
        assert len(result.tiers_used) > 0
        assert all(isinstance(t, CognitiveTier) for t in result.tiers_used)

    @pytest.mark.asyncio
    async def test_process_sets_agent_id(self, sample_agent_profile):
        """Test that process sets the agent_id."""
        processor = create_processor_with_mock_router(sample_agent_profile)
        result = await processor.process(
            stimulus="Test",
            urgency=0.5,
            complexity=0.5,
            relevance=0.5,
        )
        assert result.agent_id == sample_agent_profile.agent_id


# ==========================================
# ProcessingStrategy Tests
# ==========================================


class TestProcessingStrategy:
    """Tests for ProcessingStrategy model."""

    def test_strategy_creation(self):
        """Test creating a strategy."""
        steps = [
            {"tier": CognitiveTier.REFLEX, "purpose": "immediate", "parallel": False},
            {"tier": CognitiveTier.REACTIVE, "purpose": "assess", "parallel": True, "count": 2},
        ]
        strategy = ProcessingStrategy(steps=steps)
        assert strategy.step_count == 2

    def test_strategy_has_parallel_steps(self):
        """Test has_parallel_steps property."""
        parallel_strategy = ProcessingStrategy(
            steps=[{"tier": CognitiveTier.REACTIVE, "parallel": True}]
        )
        sequential_strategy = ProcessingStrategy(
            steps=[{"tier": CognitiveTier.DELIBERATE, "parallel": False}]
        )
        assert parallel_strategy.has_parallel_steps is True
        assert sequential_strategy.has_parallel_steps is False

    def test_strategy_total_invocations(self):
        """Test total_tier_invocations property."""
        strategy = ProcessingStrategy(
            steps=[
                {"tier": CognitiveTier.REFLEX, "count": 1},
                {"tier": CognitiveTier.REACTIVE, "count": 3},
                {"tier": CognitiveTier.DELIBERATE},  # Default count = 1
            ]
        )
        assert strategy.total_tier_invocations == 5


# ==========================================
# Integration Tests
# ==========================================


class TestCognitiveIntegration:
    """Integration tests for the cognitive system."""

    @pytest.mark.asyncio
    async def test_full_processing_flow(self, sample_agent_profile):
        """Test complete processing flow from stimulus to result."""
        processor = create_processor_with_mock_router(sample_agent_profile)
        
        result = await processor.process(
            stimulus="We need to decide on the database architecture for our new service.",
            urgency=0.4,
            complexity=0.7,
            relevance=0.8,
            purpose="architecture_decision",
            context={"recent_turns": "Team discussed options yesterday."},
        )
        
        # Verify result structure
        assert isinstance(result, CognitiveResult)
        assert result.thought_count > 0
        assert result.primary_thought is not None
        assert result.processing_time_ms > 0
        assert len(result.tiers_used) > 0
        
        # Verify thoughts
        for thought in result.thoughts:
            assert isinstance(thought, Thought)
            assert thought.content
            assert thought.thought_type in ThoughtType
            assert 0 <= thought.confidence <= 1
            assert 0 <= thought.completeness <= 1

    @pytest.mark.asyncio
    async def test_budget_tracking_integration(self, sample_agent_profile):
        """Test that processing tracks budget through model router."""
        processor = create_processor_with_mock_router(sample_agent_profile, hourly_budget=15.0)
        
        # Process a stimulus
        await processor.process(
            stimulus="Test",
            urgency=0.5,
            complexity=0.5,
            relevance=0.6,
        )
        
        # Check budget was tracked
        status = processor.router.get_status()
        assert status.budget is not None

    @pytest.mark.asyncio
    async def test_multiple_sequential_processes(self, sample_agent_profile):
        """Test multiple sequential processing calls."""
        processor = create_processor_with_mock_router(sample_agent_profile)
        
        results = []
        for i in range(3):
            result = await processor.process(
                stimulus=f"Stimulus {i}",
                urgency=0.5,
                complexity=0.5,
                relevance=0.6,
            )
            results.append(result)
        
        assert len(results) == 3
        assert all(r.thought_count > 0 for r in results)

