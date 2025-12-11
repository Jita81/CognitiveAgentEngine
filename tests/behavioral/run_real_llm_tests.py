#!/usr/bin/env python3
"""Test the Cognitive Agent Engine with a real LLM via Ollama.

This script runs a subset of behavioral tests using Ollama instead of mocks.

NOTE: This is a standalone script, not a pytest test module.
Run with: python tests/behavioral/run_real_llm_tests.py
"""

import asyncio
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4

import httpx

from src.agents.models import (
    AgentProfile,
    CommunicationStyle,
    PersonalityMarkers,
    SocialMarkers,
    SkillSet,
)
from src.cognitive import CognitiveTier
from src.cognitive.models import Thought, ThoughtType, CognitiveResult
from src.cognitive.prompts import TieredPromptBuilder
from src.cognitive.tiers import TIER_CONFIGS


# ============================================================================
# Simplified Ollama Client (direct, no router overhead)
# ============================================================================

class SimpleOllamaClient:
    """Simple async client for Ollama - bypasses router timeouts for testing."""

    def __init__(self, model_name: str = "qwen2.5:3b", base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url
        self._client: Optional[httpx.AsyncClient] = None

    async def _ensure_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=httpx.Timeout(120.0))  # Long timeout
        return self._client

    async def generate(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7,
    ) -> Dict:
        """Generate completion from Ollama."""
        client = await self._ensure_client()

        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature,
            },
        }

        response = await client.post(f"{self.base_url}/api/generate", json=payload)
        response.raise_for_status()
        return response.json()

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None


# ============================================================================
# Test Agent Profiles
# ============================================================================

def create_backend_expert() -> AgentProfile:
    """Create Marcus - a senior backend expert."""
    return AgentProfile(
        agent_id=uuid4(),
        name="Marcus",
        role="Senior Backend Engineer",
        title="Principal Engineer",
        backstory_summary=(
            "Marcus has 10 years of backend development experience, specializing in "
            "distributed systems and database optimization. He led the migration of a "
            "major e-commerce platform to microservices and is passionate about clean "
            "architecture and performance tuning."
        ),
        years_experience=10,
        personality_markers=PersonalityMarkers(
            openness=7,
            conscientiousness=9,
            extraversion=4,
            agreeableness=6,
            neuroticism=2,
            perfectionism=8,
            pragmatism=7,
            risk_tolerance=4,
        ),
        social_markers=SocialMarkers(
            confidence=8,
            assertiveness=7,
            deference=3,
            curiosity=6,
            social_calibration=6,
            status_sensitivity=4,
            facilitation_instinct=5,
            comfort_in_spotlight=5,
            comfort_with_conflict=7,
        ),
        communication_style=CommunicationStyle(
            vocabulary_level="technical",
            sentence_structure="moderate",
            formality="professional",
            uses_analogies=True,
            uses_examples=True,
            asks_clarifying_questions=True,
            summarizes_frequently=False,
            verbal_tics=["let me think about that", "the thing is"],
        ),
        skills=SkillSet(
            technical={"python": 9, "postgresql": 10, "redis": 8, "docker": 8},
            domains={"database_design": 10, "api_architecture": 9, "distributed_systems": 8},
            soft_skills={"code_review": 8, "mentoring": 7},
        ),
        knowledge_domains=["databases", "api_design", "performance_optimization", "python"],
        knowledge_gaps=["frontend", "mobile_development"],
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


def create_frontend_designer() -> AgentProfile:
    """Create Maya - a creative frontend designer."""
    return AgentProfile(
        agent_id=uuid4(),
        name="Maya",
        role="Senior Frontend Designer",
        title="Lead UX Designer",
        backstory_summary=(
            "Maya has 8 years designing beautiful and accessible user interfaces. "
            "She's passionate about creating delightful user experiences and has won "
            "multiple design awards. She believes great design should be invisible - "
            "users should just feel that things work."
        ),
        years_experience=8,
        personality_markers=PersonalityMarkers(
            openness=10,
            conscientiousness=7,
            extraversion=8,
            agreeableness=8,
            neuroticism=3,
            perfectionism=8,
            pragmatism=5,
            risk_tolerance=7,
        ),
        social_markers=SocialMarkers(
            confidence=7,
            assertiveness=6,
            deference=5,
            curiosity=9,
            social_calibration=8,
            status_sensitivity=3,
            facilitation_instinct=7,
            comfort_in_spotlight=7,
            comfort_with_conflict=5,
        ),
        communication_style=CommunicationStyle(
            vocabulary_level="moderate",
            sentence_structure="elaborate",
            formality="casual",
            uses_analogies=True,
            uses_examples=True,
            asks_clarifying_questions=True,
            summarizes_frequently=True,
            verbal_tics=["you know", "I feel like"],
        ),
        skills=SkillSet(
            technical={"css": 9, "react": 8, "figma": 10, "accessibility": 8},
            domains={"ui_design": 10, "user_experience": 9, "design_systems": 8},
            soft_skills={"user_research": 8, "presentation": 9},
        ),
        knowledge_domains=["ui_design", "user_experience", "accessibility", "design_systems"],
        knowledge_gaps=["backend", "databases", "devops"],
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


# ============================================================================
# Simple Cognitive Processor (for testing)
# ============================================================================

class SimpleCognitiveProcessor:
    """Simplified cognitive processor for testing with real LLM."""

    def __init__(self, agent: AgentProfile, ollama_client: SimpleOllamaClient):
        self.agent = agent
        self.client = ollama_client
        self.prompt_builder = TieredPromptBuilder()

    async def process(
        self,
        stimulus: str,
        tier: CognitiveTier,
        purpose: str = "response",
    ) -> Thought:
        """Process stimulus with specified tier."""
        config = TIER_CONFIGS[tier]

        # Build prompt
        prompt = self.prompt_builder.build(
            tier=tier,
            agent=self.agent,
            stimulus=stimulus,
            purpose=purpose,
            context={},
        )

        # Generate response
        result = await self.client.generate(
            prompt=prompt,
            max_tokens=config.max_tokens,
            temperature=0.7,
        )

        content = result.get("response", "")
        completion_tokens = result.get("eval_count", 0)

        # Estimate confidence
        hedging_words = ["maybe", "perhaps", "might", "possibly", "uncertain"]
        hedging_count = sum(1 for word in hedging_words if word in content.lower())
        base_confidence = {
            CognitiveTier.REFLEX: 0.5,
            CognitiveTier.REACTIVE: 0.6,
            CognitiveTier.DELIBERATE: 0.75,
            CognitiveTier.ANALYTICAL: 0.85,
            CognitiveTier.COMPREHENSIVE: 0.9,
        }[tier]
        confidence = max(0.3, base_confidence - min(hedging_count * 0.05, 0.15))

        # Estimate completeness
        utilization = completion_tokens / config.max_tokens if config.max_tokens > 0 else 0.5
        if utilization > 0.8:
            completeness = 0.9
        elif utilization > 0.5:
            completeness = 0.7
        elif utilization > 0.2:
            completeness = 0.5
        else:
            completeness = 0.4

        return Thought(
            thought_id=uuid4(),
            tier=tier,
            content=content.strip(),
            thought_type=self._infer_thought_type(content, purpose),
            trigger=purpose,
            confidence=confidence,
            completeness=completeness,
        )

    def _infer_thought_type(self, content: str, purpose: str) -> ThoughtType:
        """Infer thought type from content."""
        content_lower = content.lower()
        if any(word in content_lower for word in ["concern", "risk", "worry", "careful"]):
            return ThoughtType.CONCERN
        if "?" in content:
            return ThoughtType.QUESTION
        if purpose == "immediate_response":
            return ThoughtType.REACTION
        if any(word in content_lower for word in ["should", "could", "plan", "recommend"]):
            return ThoughtType.PLAN
        return ThoughtType.INSIGHT


# ============================================================================
# Test Cases
# ============================================================================

@dataclass
class LLMTestResult:
    """Result of a single LLM test case (renamed to avoid pytest collection)."""
    name: str
    passed: bool
    duration_ms: float
    details: str
    error: Optional[str] = None


async def test_basic_response(processor: SimpleCognitiveProcessor) -> LLMTestResult:
    """Test basic stimulus response."""
    start = time.time()
    try:
        thought = await processor.process(
            stimulus="Hello! How are you today?",
            tier=CognitiveTier.REACTIVE,
            purpose="greeting",
        )
        duration = (time.time() - start) * 1000

        passed = len(thought.content) > 10
        details = (
            f"Response: {thought.content[:150]}...\n"
            f"Confidence: {thought.confidence:.2f}\n"
            f"Completeness: {thought.completeness:.2f}\n"
            f"Latency: {duration:.0f}ms"
        )
        return LLMTestResult("Basic Response", passed, duration, details)
    except Exception as e:
        return LLMTestResult("Basic Response", False, (time.time() - start) * 1000, "", str(e))


async def test_reflex_is_brief(processor: SimpleCognitiveProcessor) -> LLMTestResult:
    """Test that REFLEX tier produces brief responses."""
    start = time.time()
    try:
        thought = await processor.process(
            stimulus="URGENT: Server alert!",
            tier=CognitiveTier.REFLEX,
            purpose="immediate_response",
        )
        duration = (time.time() - start) * 1000

        word_count = len(thought.content.split())
        # REFLEX should be concise (< 50 words typically)
        passed = 5 < word_count < 100
        details = (
            f"Word count: {word_count}\n"
            f"Response: {thought.content[:100]}...\n"
            f"Latency: {duration:.0f}ms"
        )
        return LLMTestResult("REFLEX is Brief", passed, duration, details)
    except Exception as e:
        return LLMTestResult("REFLEX is Brief", False, (time.time() - start) * 1000, "", str(e))


async def test_deliberate_is_thorough(processor: SimpleCognitiveProcessor) -> LLMTestResult:
    """Test that DELIBERATE tier produces thorough responses."""
    start = time.time()
    try:
        thought = await processor.process(
            stimulus="What are the tradeoffs between SQL and NoSQL databases?",
            tier=CognitiveTier.DELIBERATE,
            purpose="analysis",
        )
        duration = (time.time() - start) * 1000

        word_count = len(thought.content.split())
        # DELIBERATE should be more thorough (> 50 words typically)
        passed = word_count > 30
        details = (
            f"Word count: {word_count}\n"
            f"Response preview: {thought.content[:200]}...\n"
            f"Confidence: {thought.confidence:.2f}\n"
            f"Latency: {duration:.0f}ms"
        )
        return LLMTestResult("DELIBERATE is Thorough", passed, duration, details)
    except Exception as e:
        return LLMTestResult("DELIBERATE is Thorough", False, (time.time() - start) * 1000, "", str(e))


async def test_expert_domain_response(processor: SimpleCognitiveProcessor) -> LLMTestResult:
    """Test expert responds well to domain questions."""
    start = time.time()
    try:
        # Marcus is a database expert
        thought = await processor.process(
            stimulus="How would you optimize a slow PostgreSQL query with multiple joins?",
            tier=CognitiveTier.DELIBERATE,
            purpose="technical_advice",
        )
        duration = (time.time() - start) * 1000

        # Check for technical content
        technical_terms = ["index", "query", "join", "explain", "table", "column", "performance"]
        has_technical = any(term in thought.content.lower() for term in technical_terms)

        passed = has_technical and thought.confidence >= 0.6
        details = (
            f"Has technical content: {has_technical}\n"
            f"Confidence: {thought.confidence:.2f}\n"
            f"Response preview: {thought.content[:200]}...\n"
            f"Latency: {duration:.0f}ms"
        )
        return LLMTestResult("Expert Domain Response", passed, duration, details)
    except Exception as e:
        return LLMTestResult("Expert Domain Response", False, (time.time() - start) * 1000, "", str(e))


async def test_different_agents_differ(
    marcus_processor: SimpleCognitiveProcessor,
    maya_processor: SimpleCognitiveProcessor,
) -> LLMTestResult:
    """Test that different agents produce different responses."""
    start = time.time()
    try:
        stimulus = "What do you think makes a good user interface?"

        marcus_thought = await marcus_processor.process(
            stimulus=stimulus,
            tier=CognitiveTier.REACTIVE,
            purpose="opinion",
        )
        maya_thought = await maya_processor.process(
            stimulus=stimulus,
            tier=CognitiveTier.REACTIVE,
            purpose="opinion",
        )
        duration = (time.time() - start) * 1000

        # Responses should be different
        different = marcus_thought.content != maya_thought.content

        # Maya (designer) might mention design terms more
        design_terms = ["design", "user", "visual", "experience", "interface", "aesthetic"]
        marcus_design_count = sum(1 for t in design_terms if t in marcus_thought.content.lower())
        maya_design_count = sum(1 for t in design_terms if t in maya_thought.content.lower())

        passed = different
        details = (
            f"Responses different: {different}\n"
            f"Marcus design terms: {marcus_design_count}\n"
            f"Maya design terms: {maya_design_count}\n"
            f"Marcus: {marcus_thought.content[:100]}...\n"
            f"Maya: {maya_thought.content[:100]}...\n"
            f"Latency: {duration:.0f}ms"
        )
        return LLMTestResult("Different Agents Differ", passed, duration, details)
    except Exception as e:
        return LLMTestResult("Different Agents Differ", False, (time.time() - start) * 1000, "", str(e))


async def test_tier_depth_varies(processor: SimpleCognitiveProcessor) -> LLMTestResult:
    """Test that different tiers produce different depth of response."""
    start = time.time()
    try:
        stimulus = "What is REST API?"

        reflex_thought = await processor.process(
            stimulus=stimulus,
            tier=CognitiveTier.REFLEX,
            purpose="quick_answer",
        )
        deliberate_thought = await processor.process(
            stimulus=stimulus,
            tier=CognitiveTier.DELIBERATE,
            purpose="detailed_answer",
        )
        duration = (time.time() - start) * 1000

        reflex_len = len(reflex_thought.content)
        deliberate_len = len(deliberate_thought.content)
        deliberate_longer = deliberate_len > reflex_len

        passed = deliberate_longer
        details = (
            f"REFLEX length: {reflex_len} chars\n"
            f"DELIBERATE length: {deliberate_len} chars\n"
            f"DELIBERATE is longer: {deliberate_longer}\n"
            f"REFLEX: {reflex_thought.content[:80]}...\n"
            f"DELIBERATE: {deliberate_thought.content[:80]}...\n"
            f"Latency: {duration:.0f}ms"
        )
        return LLMTestResult("Tier Depth Varies", passed, duration, details)
    except Exception as e:
        return LLMTestResult("Tier Depth Varies", False, (time.time() - start) * 1000, "", str(e))


# ============================================================================
# Main Test Runner
# ============================================================================

async def run_all_tests(model_name: str = "qwen2.5:3b"):
    """Run all behavioral tests with real LLM."""

    print("=" * 70)
    print("COGNITIVE AGENT ENGINE - REAL LLM TEST SUITE")
    print(f"Using model: {model_name}")
    print("=" * 70)
    print()

    # Check Ollama connection
    print("Checking Ollama connection...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:11434/api/tags", timeout=5.0)
            if response.status_code != 200:
                print("ERROR: Ollama is not responding")
                return False
            models = [m["name"] for m in response.json().get("models", [])]
            print(f"Available models: {', '.join(models)}")
            if not any(model_name in m for m in models):
                print(f"WARNING: {model_name} not found")
    except Exception as e:
        print(f"ERROR: Cannot connect to Ollama: {e}")
        return False

    print()

    # Create shared Ollama client
    ollama = SimpleOllamaClient(model_name=model_name)

    # Warm up the model (first request is slow)
    print("Warming up model (first request may be slow)...")
    try:
        warmup_start = time.time()
        warmup = await ollama.generate("Hello", max_tokens=10)
        warmup_time = time.time() - warmup_start
        print(f"Model ready ({warmup_time:.1f}s warmup)")
    except Exception as e:
        print(f"ERROR: Failed to warm up model: {e}")
        await ollama.close()
        return False

    print()

    # Create processors
    marcus = create_backend_expert()
    maya = create_frontend_designer()

    marcus_processor = SimpleCognitiveProcessor(marcus, ollama)
    maya_processor = SimpleCognitiveProcessor(maya, ollama)

    # Run tests
    results: List[LLMTestResult] = []

    print("-" * 70)
    print("RUNNING TESTS...")
    print("-" * 70)
    print()

    tests = [
        ("1. Basic Response", lambda: test_basic_response(marcus_processor)),
        ("2. REFLEX is Brief", lambda: test_reflex_is_brief(marcus_processor)),
        ("3. DELIBERATE is Thorough", lambda: test_deliberate_is_thorough(marcus_processor)),
        ("4. Expert Domain Response", lambda: test_expert_domain_response(marcus_processor)),
        ("5. Different Agents Differ", lambda: test_different_agents_differ(marcus_processor, maya_processor)),
        ("6. Tier Depth Varies", lambda: test_tier_depth_varies(marcus_processor)),
    ]

    for name, test_fn in tests:
        print(f"{name}...")
        result = await test_fn()
        results.append(result)
        status = "✓ PASSED" if result.passed else "✗ FAILED"
        print(f"   {status} ({result.duration_ms:.0f}ms)")
        if result.error:
            print(f"   Error: {result.error[:100]}")
        print()

    # Summary
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for r in results if r.passed)
    total = len(results)
    total_time = sum(r.duration_ms for r in results)

    print(f"Passed: {passed}/{total} ({100*passed/total:.0f}%)")
    print(f"Total time: {total_time/1000:.2f}s")
    print()

    # Detailed results
    print("-" * 70)
    print("DETAILED RESULTS")
    print("-" * 70)
    for result in results:
        status = "✓ PASSED" if result.passed else "✗ FAILED"
        print(f"\n{status}: {result.name}")
        print(f"Duration: {result.duration_ms:.0f}ms")
        if result.details:
            print(f"Details:\n{result.details}")
        if result.error:
            print(f"Error: {result.error}")

    # Cleanup
    await ollama.close()

    return passed == total


if __name__ == "__main__":
    import sys

    model = sys.argv[1] if len(sys.argv) > 1 else "qwen2.5:3b"
    success = asyncio.run(run_all_tests(model))
    sys.exit(0 if success else 1)
