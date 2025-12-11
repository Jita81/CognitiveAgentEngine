"""Async client for vLLM inference endpoints."""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Protocol

import httpx


class ModelTier(Enum):
    """Model tier classification based on size and capability."""

    SMALL = "small"  # Qwen2.5-3B - Fast, for REFLEX tier
    MEDIUM = "medium"  # Qwen2.5-7B - Balanced, for REACTIVE tier
    LARGE = "large"  # Qwen2.5-14B - Powerful, for DELIBERATE+ tiers


@dataclass
class ModelConfig:
    """Configuration for a model endpoint."""

    tier: ModelTier
    url: str
    model_name: str
    max_tokens: int
    typical_latency_ms: int
    cost_per_1k_tokens: float

    # Connection settings
    timeout_seconds: float = 30.0
    max_connections: int = 10


# Default model configurations
DEFAULT_MODEL_CONFIGS = {
    ModelTier.SMALL: ModelConfig(
        tier=ModelTier.SMALL,
        url="http://localhost:8001",
        model_name="Qwen/Qwen2.5-3B-Instruct",
        max_tokens=2048,
        typical_latency_ms=200,
        cost_per_1k_tokens=0.0002,
    ),
    ModelTier.MEDIUM: ModelConfig(
        tier=ModelTier.MEDIUM,
        url="http://localhost:8002",
        model_name="Qwen/Qwen2.5-7B-Instruct",
        max_tokens=4096,
        typical_latency_ms=500,
        cost_per_1k_tokens=0.0012,
    ),
    ModelTier.LARGE: ModelConfig(
        tier=ModelTier.LARGE,
        url="http://localhost:8003",
        model_name="Qwen/Qwen2.5-14B-Instruct",
        max_tokens=8192,
        typical_latency_ms=2000,
        cost_per_1k_tokens=0.0049,
    ),
}


@dataclass
class InferenceRequest:
    """Request for model inference."""

    prompt: str
    max_tokens: int = 256
    temperature: float = 0.7
    top_p: float = 0.95
    stop: Optional[List[str]] = None

    def to_vllm_payload(self, model_name: str) -> dict:
        """Convert to vLLM API payload."""
        return {
            "model": model_name,
            "prompt": self.prompt,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "stop": self.stop or [],
        }


@dataclass
class InferenceResponse:
    """Response from model inference."""

    text: str
    model_used: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    latency_ms: float
    tier_used: ModelTier

    @property
    def tokens_per_second(self) -> float:
        """Calculate tokens per second."""
        if self.latency_ms <= 0:
            return 0.0
        return (self.completion_tokens / self.latency_ms) * 1000


class ModelClientProtocol(Protocol):
    """Protocol for model clients (real and mock)."""

    async def generate(self, request: InferenceRequest) -> InferenceResponse:
        """Generate completion from model."""
        ...

    async def health_check(self) -> bool:
        """Check if model endpoint is healthy."""
        ...

    async def close(self) -> None:
        """Close client connections."""
        ...


class ModelClient:
    """Async client for vLLM inference endpoints."""

    def __init__(self, config: ModelConfig):
        self.config = config
        self._client: Optional[httpx.AsyncClient] = None

    @property
    def client(self) -> httpx.AsyncClient:
        """Lazy initialization of HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.config.timeout_seconds),
                limits=httpx.Limits(max_connections=self.config.max_connections),
            )
        return self._client

    async def generate(self, request: InferenceRequest) -> InferenceResponse:
        """Generate completion from model.

        Args:
            request: The inference request

        Returns:
            InferenceResponse with generated text and metadata

        Raises:
            httpx.HTTPStatusError: If the request fails
            httpx.TimeoutException: If the request times out
        """
        start_time = time.time()

        # Ensure max_tokens doesn't exceed model limit
        effective_max_tokens = min(request.max_tokens, self.config.max_tokens)
        request.max_tokens = effective_max_tokens

        payload = request.to_vllm_payload(self.config.model_name)

        response = await self.client.post(
            f"{self.config.url}/v1/completions",
            json=payload,
        )
        response.raise_for_status()

        result = response.json()
        latency_ms = (time.time() - start_time) * 1000

        # Extract response data
        choice = result["choices"][0]
        usage = result.get("usage", {})

        return InferenceResponse(
            text=choice["text"],
            model_used=self.config.model_name,
            prompt_tokens=usage.get("prompt_tokens", 0),
            completion_tokens=usage.get("completion_tokens", 0),
            total_tokens=usage.get("total_tokens", 0),
            latency_ms=latency_ms,
            tier_used=self.config.tier,
        )

    async def health_check(self) -> bool:
        """Check if model endpoint is healthy.

        Returns:
            True if endpoint responds successfully, False otherwise
        """
        try:
            response = await self.client.get(
                f"{self.config.url}/health",
                timeout=5.0,
            )
            return response.status_code == 200
        except Exception:
            return False

    async def get_model_info(self) -> Optional[dict]:
        """Get model information from endpoint.

        Returns:
            Model info dict or None if unavailable
        """
        try:
            response = await self.client.get(f"{self.config.url}/v1/models")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception:
            return None

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    def __repr__(self) -> str:
        return f"ModelClient(tier={self.config.tier.value}, url={self.config.url})"
