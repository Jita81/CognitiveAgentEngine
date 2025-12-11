"""Cognitive processor for tiered stimulus processing.

This module contains the main CognitiveProcessor class that:
- Plans processing strategies based on stimulus characteristics
- Executes cognitive tiers (parallel or sequential)
- Creates and manages Thought objects
- Integrates with the model router for inference
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from src.agents.models import AgentProfile
from src.cognitive.models import (
    CognitiveResult,
    ProcessingStrategy,
    Thought,
    ThoughtType,
)
from src.cognitive.prompts import TieredPromptBuilder
from src.cognitive.tiers import CognitiveTier, TIER_CONFIGS
from src.infrastructure.model_client import InferenceRequest, InferenceResponse
from src.infrastructure.model_router import ModelRouter

logger = logging.getLogger(__name__)


class CognitiveProcessor:
    """Processes stimuli through cognitive tiers.
    
    This is the core processing engine that transforms stimuli into
    Thoughts through tiered cognitive processing.
    
    Features:
    - Strategy planning based on urgency/complexity/relevance
    - Parallel execution for REFLEX and REACTIVE tiers
    - Sequential execution with prior thought context for higher tiers
    - Integration with model router for budget-aware inference
    """

    def __init__(
        self,
        agent: AgentProfile,
        model_router: ModelRouter,
    ):
        """Initialize the cognitive processor.
        
        Args:
            agent: The agent profile to process as
            model_router: Router for model inference
        """
        self.agent = agent
        self.router = model_router
        self.prompt_builder = TieredPromptBuilder()

    async def process(
        self,
        stimulus: str,
        urgency: float,
        complexity: float,
        relevance: float,
        purpose: str = "general_response",
        context: Optional[Dict] = None,
    ) -> CognitiveResult:
        """Process stimulus with appropriate cognitive depth.
        
        Args:
            stimulus: The stimulus text to process
            urgency: How urgent (0-1, affects speed vs depth)
            complexity: How complex (0-1, affects tier selection)
            relevance: How relevant to agent (0-1, affects engagement)
            purpose: Purpose of this processing
            context: Optional additional context
            
        Returns:
            CognitiveResult with all produced thoughts
        """
        start_time = datetime.now(timezone.utc)
        stimulus_id = uuid4()

        # Plan cognitive strategy
        strategy = self._plan_strategy(urgency, complexity, relevance)
        logger.debug(
            f"Planned strategy with {strategy.step_count} steps for "
            f"urgency={urgency:.2f}, complexity={complexity:.2f}, relevance={relevance:.2f}"
        )

        # Execute strategy
        thoughts: List[Thought] = []

        for step in strategy.steps:
            tier = step["tier"]
            step_purpose = step["purpose"]
            is_parallel = step.get("parallel", False)
            count = step.get("count", 1)

            if is_parallel and count > 1:
                # Run parallel processes
                parallel_tasks = [
                    self._run_tier(
                        tier=tier,
                        stimulus=stimulus,
                        purpose=f"{step_purpose}_{i}",
                        context=context,
                        prior_thoughts=thoughts,
                    )
                    for i in range(count)
                ]
                results = await asyncio.gather(*parallel_tasks, return_exceptions=True)
                
                for result in results:
                    if isinstance(result, Thought):
                        thoughts.append(result)
                    elif isinstance(result, Exception):
                        logger.error(f"Parallel tier execution failed: {result}")
            else:
                # Run sequential
                try:
                    thought = await self._run_tier(
                        tier=tier,
                        stimulus=stimulus,
                        purpose=step_purpose,
                        context=context,
                        prior_thoughts=thoughts,
                    )
                    thoughts.append(thought)
                except Exception as e:
                    logger.error(f"Sequential tier execution failed: {e}")

        # Determine primary thought
        primary = self._select_primary_thought(thoughts)

        # Calculate processing time
        elapsed_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000

        return CognitiveResult(
            thoughts=thoughts,
            primary_thought=primary,
            processing_time_ms=elapsed_ms,
            tiers_used=list(set(t.tier for t in thoughts)),
            agent_id=self.agent.agent_id,
            stimulus_id=stimulus_id,
        )

    def _plan_strategy(
        self,
        urgency: float,
        complexity: float,
        relevance: float,
    ) -> ProcessingStrategy:
        """Plan cognitive processing strategy based on stimulus characteristics.
        
        Strategy selection matrix:
        - High urgency + relevant: REFLEX first, then parallel REACTIVE
        - Low urgency + relevant: go straight to DELIBERATE
        - Low relevance: just note it with REFLEX
        - Medium everything: proportional response
        
        Args:
            urgency: How urgent (0-1)
            complexity: How complex (0-1)
            relevance: How relevant (0-1)
            
        Returns:
            ProcessingStrategy with planned steps
        """
        steps: List[Dict] = []

        # High urgency + relevant: REFLEX first, then parallel REACTIVE
        if urgency > 0.8 and relevance > 0.5:
            steps.append({
                "tier": CognitiveTier.REFLEX,
                "purpose": "immediate_response",
                "parallel": False,
            })
            steps.append({
                "tier": CognitiveTier.REACTIVE,
                "purpose": "tactical_assessment",
                "parallel": True,
                "count": 2,  # Tactical + strategic perspectives
            })
            if complexity > 0.5:
                steps.append({
                    "tier": CognitiveTier.DELIBERATE,
                    "purpose": "deeper_analysis",
                    "parallel": False,
                })

        # Low urgency + relevant: go straight to DELIBERATE
        elif urgency < 0.3 and relevance > 0.5:
            steps.append({
                "tier": CognitiveTier.DELIBERATE,
                "purpose": "considered_response",
                "parallel": False,
            })
            if complexity > 0.7:
                steps.append({
                    "tier": CognitiveTier.ANALYTICAL,
                    "purpose": "thorough_analysis",
                    "parallel": False,
                })

        # Low relevance: just note it
        elif relevance < 0.3:
            steps.append({
                "tier": CognitiveTier.REFLEX,
                "purpose": "note_for_context",
                "parallel": False,
            })

        # Medium everything: proportional response
        else:
            if complexity < 0.5:
                tier = CognitiveTier.REACTIVE
            else:
                tier = CognitiveTier.DELIBERATE
            
            steps.append({
                "tier": tier,
                "purpose": "proportional_response",
                "parallel": False,
            })

        return ProcessingStrategy(steps=steps)

    async def _run_tier(
        self,
        tier: CognitiveTier,
        stimulus: str,
        purpose: str,
        context: Optional[Dict],
        prior_thoughts: List[Thought],
    ) -> Thought:
        """Run a single cognitive tier.
        
        Args:
            tier: The cognitive tier to run
            stimulus: The stimulus to process
            purpose: Purpose of this tier execution
            context: Additional context
            prior_thoughts: Thoughts from prior tier executions
            
        Returns:
            Thought produced by this tier
        """
        # Build context with prior thoughts
        effective_context = dict(context) if context else {}
        if prior_thoughts:
            effective_context["prior_thoughts"] = TieredPromptBuilder.format_prior_thoughts(
                [t.content for t in prior_thoughts[-3:]]
            )

        # Build prompt
        prompt = self.prompt_builder.build(
            tier=tier,
            agent=self.agent,
            stimulus=stimulus,
            purpose=purpose,
            context=effective_context,
        )

        # Get tier config
        config = TIER_CONFIGS[tier]

        # Make inference request
        request = InferenceRequest(
            prompt=prompt,
            max_tokens=config.max_tokens,
            temperature=0.7,
        )

        # Route through model router (handles budget, fallback, etc.)
        response = await self.router.route(
            cognitive_tier=tier,
            request=request,
            agent_id=str(self.agent.agent_id),
        )

        # Create thought from response
        return Thought(
            thought_id=uuid4(),
            created_at=datetime.now(timezone.utc),
            tier=tier,
            content=response.text.strip(),
            thought_type=self._infer_thought_type(purpose, response.text),
            trigger=purpose,
            confidence=self._estimate_confidence(tier, response),
            completeness=self._estimate_completeness(tier, response),
            related_thought_ids=[t.thought_id for t in prior_thoughts[-2:]],
        )

    def _select_primary_thought(
        self,
        thoughts: List[Thought],
    ) -> Optional[Thought]:
        """Select the primary (most significant) thought from results.
        
        Selection criteria:
        - Higher tier = more considered
        - Higher confidence = more certain
        - Higher completeness = more developed
        
        Args:
            thoughts: All thoughts to select from
            
        Returns:
            The primary thought, or None if no thoughts
        """
        if not thoughts:
            return None

        # Score each thought: tier weight (40%) + confidence (30%) + completeness (30%)
        def score(t: Thought) -> float:
            return (
                t.tier.value * 0.4 +
                t.confidence * 0.3 +
                t.completeness * 0.3
            )

        return max(thoughts, key=score)

    def _infer_thought_type(
        self,
        purpose: str,
        content: str,
    ) -> ThoughtType:
        """Infer thought type from purpose and content.
        
        Args:
            purpose: The purpose that triggered this thought
            content: The thought content
            
        Returns:
            Inferred ThoughtType
        """
        content_lower = content.lower()

        # Check content for type indicators
        if any(word in content_lower for word in ["concern", "risk", "worry", "careful", "danger"]):
            return ThoughtType.CONCERN
        if "?" in content:
            return ThoughtType.QUESTION
        if purpose == "immediate_response":
            return ThoughtType.REACTION
        if any(word in content_lower for word in ["should", "could", "plan", "next", "recommend"]):
            return ThoughtType.PLAN
        if any(word in content_lower for word in ["notice", "observe", "see", "note"]):
            return ThoughtType.OBSERVATION

        return ThoughtType.INSIGHT

    def _estimate_confidence(
        self,
        tier: CognitiveTier,
        response: InferenceResponse,
    ) -> float:
        """Estimate confidence based on tier and response characteristics.
        
        Higher tiers produce more considered thoughts with higher base confidence.
        
        Args:
            tier: The tier that produced this thought
            response: The model response
            
        Returns:
            Confidence score (0-1)
        """
        # Base confidence by tier
        base_confidence = {
            CognitiveTier.REFLEX: 0.5,
            CognitiveTier.REACTIVE: 0.6,
            CognitiveTier.DELIBERATE: 0.75,
            CognitiveTier.ANALYTICAL: 0.85,
            CognitiveTier.COMPREHENSIVE: 0.9,
        }[tier]

        # Could adjust based on hedging language, but keep simple for now
        # E.g., "I think", "maybe", "perhaps" could reduce confidence
        hedging_words = ["maybe", "perhaps", "might", "possibly", "uncertain"]
        content_lower = response.text.lower()
        hedging_count = sum(1 for word in hedging_words if word in content_lower)
        
        # Reduce confidence slightly for hedging (max -0.15)
        hedging_penalty = min(hedging_count * 0.05, 0.15)
        
        return max(0.3, base_confidence - hedging_penalty)

    def _estimate_completeness(
        self,
        tier: CognitiveTier,
        response: InferenceResponse,
    ) -> float:
        """Estimate how complete/developed the thought is.
        
        Based on token utilization relative to tier budget.
        
        Args:
            tier: The tier that produced this thought
            response: The model response
            
        Returns:
            Completeness score (0-1)
        """
        config = TIER_CONFIGS[tier]
        
        # Avoid division by zero
        if config.max_tokens == 0:
            return 0.5
            
        utilization = response.completion_tokens / config.max_tokens

        # High utilization = probably complete thought
        # Low utilization = either truncated OR concise (hard to tell)
        if utilization > 0.8:
            return 0.9
        elif utilization > 0.5:
            return 0.7
        elif utilization > 0.2:
            return 0.5
        else:
            return 0.4

    async def process_with_tier_override(
        self,
        stimulus: str,
        tier: CognitiveTier,
        purpose: str = "direct_tier",
        context: Optional[Dict] = None,
    ) -> Thought:
        """Process stimulus with a specific tier (bypassing strategy planning).
        
        Useful for testing or when a specific tier is required.
        
        Args:
            stimulus: The stimulus to process
            tier: The specific tier to use
            purpose: Purpose of processing
            context: Optional context
            
        Returns:
            Single Thought from the specified tier
        """
        return await self._run_tier(
            tier=tier,
            stimulus=stimulus,
            purpose=purpose,
            context=context,
            prior_thoughts=[],
        )


def create_processor_with_mock_router(
    agent: AgentProfile,
    hourly_budget: float = 15.0,
) -> CognitiveProcessor:
    """Create a processor with mock model router for testing.
    
    Args:
        agent: The agent profile to use
        hourly_budget: Budget for token usage
        
    Returns:
        CognitiveProcessor with mock infrastructure
    """
    from src.infrastructure.model_router import create_router_with_mock_clients

    router = create_router_with_mock_clients(hourly_budget=hourly_budget)
    return CognitiveProcessor(agent=agent, model_router=router)

