"""Mock model client for testing without GPUs."""

import asyncio
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from src.infrastructure.model_client import (
    InferenceRequest,
    InferenceResponse,
    ModelConfig,
    ModelTier,
)


@dataclass
class MockConfig:
    """Configuration for mock behavior."""

    # Simulated latency range (min, max) in ms
    latency_range: tuple[int, int] = (50, 200)

    # Probability of simulated failure (0-1)
    failure_rate: float = 0.0

    # Whether endpoint appears healthy
    is_healthy: bool = True

    # Tokens per word estimate (for usage simulation)
    tokens_per_word: float = 1.3


@dataclass
class MockModelClient:
    """Mock client for testing without actual vLLM endpoints.

    Simulates model inference with configurable behavior:
    - Latency simulation based on tier
    - Deterministic or random responses
    - Controllable error injection
    - Usage tracking
    """

    config: ModelConfig
    mock_config: MockConfig = field(default_factory=MockConfig)

    # Track calls for testing
    _call_history: List[InferenceRequest] = field(default_factory=list)
    _total_tokens: int = 0

    # Response templates by tier
    RESPONSE_TEMPLATES = {
        ModelTier.SMALL: [
            "I understand. Let me help with that.",
            "Here's a quick thought on this matter.",
            "Based on my understanding, the answer is straightforward.",
        ],
        ModelTier.MEDIUM: [
            "This is an interesting question that requires some consideration. "
            "Let me break it down for you step by step.",
            "I've analyzed this carefully. Here's what I think is most relevant "
            "to your situation.",
            "There are several factors to consider here. Let me walk you through "
            "the key points.",
        ],
        ModelTier.LARGE: [
            "This is a complex topic that warrants thorough analysis. "
            "Let me provide a comprehensive breakdown of the key considerations, "
            "potential approaches, and my recommended path forward. "
            "First, we need to understand the underlying context...",
            "Thank you for this thoughtful question. I'll provide a detailed response "
            "that covers the theoretical foundations, practical implications, "
            "and actionable recommendations. Let's start with the fundamentals...",
            "This requires careful consideration of multiple factors. "
            "I'll structure my response to address the immediate concerns, "
            "broader implications, and strategic recommendations. "
            "Beginning with the core issue...",
        ],
    }

    async def generate(self, request: InferenceRequest) -> InferenceResponse:
        """Simulate model inference.

        Args:
            request: The inference request

        Returns:
            Simulated InferenceResponse

        Raises:
            RuntimeError: If failure_rate triggers simulated error
        """
        # Record call
        self._call_history.append(request)

        # Simulate latency based on tier
        latency_ms = self._simulate_latency()
        await asyncio.sleep(latency_ms / 1000)

        # Check for simulated failure
        if self.mock_config.failure_rate > 0:
            if random.random() < self.mock_config.failure_rate:
                raise RuntimeError(f"Simulated failure for {self.config.tier.value}")

        # Generate response
        response_text = self._generate_response(request)

        # Calculate tokens (approximate)
        prompt_tokens = self._estimate_tokens(request.prompt)
        completion_tokens = self._estimate_tokens(response_text)
        total_tokens = prompt_tokens + completion_tokens

        self._total_tokens += total_tokens

        return InferenceResponse(
            text=response_text,
            model_used=self.config.model_name,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            latency_ms=latency_ms,
            tier_used=self.config.tier,
        )

    async def health_check(self) -> bool:
        """Return configured health status."""
        # Small delay to simulate network
        await asyncio.sleep(0.01)
        return self.mock_config.is_healthy

    async def close(self) -> None:
        """No-op for mock client."""
        pass

    def _simulate_latency(self) -> float:
        """Simulate latency based on tier and config."""
        # Base latency from config
        min_lat, max_lat = self.mock_config.latency_range

        # Scale by tier (larger = slower)
        tier_multipliers = {
            ModelTier.SMALL: 1.0,
            ModelTier.MEDIUM: 2.0,
            ModelTier.LARGE: 4.0,
        }
        multiplier = tier_multipliers.get(self.config.tier, 1.0)

        base_latency = random.uniform(min_lat, max_lat)
        return base_latency * multiplier

    def _generate_response(self, request: InferenceRequest) -> str:
        """Generate a mock response based on tier."""
        templates = self.RESPONSE_TEMPLATES.get(
            self.config.tier, self.RESPONSE_TEMPLATES[ModelTier.MEDIUM]
        )
        response = random.choice(templates)

        # Truncate to max_tokens (rough approximation)
        words = response.split()
        max_words = int(request.max_tokens / self.mock_config.tokens_per_word)
        if len(words) > max_words:
            response = " ".join(words[:max_words]) + "..."

        return response

    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count from text."""
        words = len(text.split())
        return int(words * self.mock_config.tokens_per_word)

    # Test helper methods

    def get_call_count(self) -> int:
        """Get total number of generate() calls."""
        return len(self._call_history)

    def get_last_request(self) -> Optional[InferenceRequest]:
        """Get the most recent request."""
        if self._call_history:
            return self._call_history[-1]
        return None

    def get_total_tokens(self) -> int:
        """Get total tokens generated."""
        return self._total_tokens

    def reset_history(self) -> None:
        """Reset call history and counters."""
        self._call_history.clear()
        self._total_tokens = 0

    def set_healthy(self, healthy: bool) -> None:
        """Set health status for testing."""
        self.mock_config.is_healthy = healthy

    def set_failure_rate(self, rate: float) -> None:
        """Set failure rate for testing (0-1)."""
        self.mock_config.failure_rate = max(0.0, min(1.0, rate))

    def __repr__(self) -> str:
        return f"MockModelClient(tier={self.config.tier.value}, healthy={self.mock_config.is_healthy})"


def create_mock_clients() -> Dict[ModelTier, MockModelClient]:
    """Create mock clients for all tiers.

    Returns:
        Dictionary mapping ModelTier to MockModelClient
    """
    from src.infrastructure.model_client import DEFAULT_MODEL_CONFIGS

    return {
        tier: MockModelClient(config=config)
        for tier, config in DEFAULT_MODEL_CONFIGS.items()
    }
