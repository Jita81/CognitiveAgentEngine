"""Ollama client for local LLM inference (macOS compatible).

This provides a drop-in replacement for the vLLM client that works with
Ollama running locally on macOS (Apple Silicon supported).
"""

import time
from dataclasses import dataclass
from typing import Dict, Optional

import httpx

from src.infrastructure.model_client import (
    InferenceRequest,
    InferenceResponse,
    ModelClientProtocol,
    ModelTier,
)


@dataclass
class OllamaModelConfig:
    """Configuration for an Ollama model."""

    tier: ModelTier
    model_name: str
    url: str = "http://localhost:11434"
    max_tokens: int = 2048
    typical_latency_ms: int = 500
    cost_per_1k_tokens: float = 0.0  # Local model, no cost


# Default Ollama model configurations
# Maps each tier to a specific Ollama model
DEFAULT_OLLAMA_CONFIGS = {
    ModelTier.SMALL: OllamaModelConfig(
        tier=ModelTier.SMALL,
        model_name="qwen2.5:3b",
        max_tokens=1024,
        typical_latency_ms=200,
    ),
    ModelTier.MEDIUM: OllamaModelConfig(
        tier=ModelTier.MEDIUM,
        model_name="qwen2.5:7b",
        max_tokens=2048,
        typical_latency_ms=500,
    ),
    ModelTier.LARGE: OllamaModelConfig(
        tier=ModelTier.LARGE,
        model_name="qwen2.5:14b",
        max_tokens=4096,
        typical_latency_ms=1500,
    ),
}


class OllamaClient:
    """Async client for Ollama inference."""

    def __init__(
        self,
        config: OllamaModelConfig,
        fallback_model: Optional[str] = None,
    ):
        """Initialize Ollama client.

        Args:
            config: Configuration for this client
            fallback_model: Alternative model to use if primary isn't available
        """
        self.config = config
        self.fallback_model = fallback_model or "llama3.2"
        self._client: Optional[httpx.AsyncClient] = None
        self._available_model: Optional[str] = None

    @property
    def client(self) -> httpx.AsyncClient:
        """Lazy initialization of HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(60.0),  # Ollama can be slow on first load
            )
        return self._client

    async def _check_model_available(self, model_name: str) -> bool:
        """Check if a model is available in Ollama."""
        try:
            response = await self.client.get(f"{self.config.url}/api/tags")
            if response.status_code == 200:
                data = response.json()
                models = [m["name"] for m in data.get("models", [])]
                # Check for exact match or base model match
                return any(
                    model_name in m or m.startswith(model_name.split(":")[0])
                    for m in models
                )
        except Exception:
            pass
        return False

    async def _get_model_to_use(self) -> str:
        """Determine which model to use, checking availability."""
        if self._available_model:
            return self._available_model

        # Try primary model first
        if await self._check_model_available(self.config.model_name):
            self._available_model = self.config.model_name
            return self._available_model

        # Try fallback
        if await self._check_model_available(self.fallback_model):
            self._available_model = self.fallback_model
            return self._available_model

        # Default to whatever we have
        self._available_model = self.fallback_model
        return self._available_model

    async def generate(self, request: InferenceRequest) -> InferenceResponse:
        """Generate completion from Ollama.

        Args:
            request: The inference request

        Returns:
            InferenceResponse with generated text and metadata
        """
        start_time = time.time()

        model_to_use = await self._get_model_to_use()

        # Build the prompt - Ollama's generate endpoint expects raw text
        payload = {
            "model": model_to_use,
            "prompt": request.prompt,
            "stream": False,
            "options": {
                "num_predict": min(request.max_tokens, self.config.max_tokens),
                "temperature": request.temperature,
                "top_p": request.top_p,
            },
        }

        if request.stop:
            payload["options"]["stop"] = request.stop

        response = await self.client.post(
            f"{self.config.url}/api/generate",
            json=payload,
        )
        response.raise_for_status()

        result = response.json()
        latency_ms = (time.time() - start_time) * 1000

        # Extract token counts from Ollama response
        prompt_tokens = result.get("prompt_eval_count", 0)
        completion_tokens = result.get("eval_count", 0)

        return InferenceResponse(
            text=result.get("response", ""),
            model_used=model_to_use,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            latency_ms=latency_ms,
            tier_used=self.config.tier,
        )

    async def health_check(self) -> bool:
        """Check if Ollama is running and responsive."""
        try:
            response = await self.client.get(
                f"{self.config.url}/api/tags",
                timeout=5.0,
            )
            return response.status_code == 200
        except Exception:
            return False

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    def __repr__(self) -> str:
        return f"OllamaClient(tier={self.config.tier.value}, model={self.config.model_name})"


def create_ollama_clients(
    available_models: Optional[Dict[ModelTier, str]] = None,
    base_url: str = "http://localhost:11434",
) -> Dict[ModelTier, OllamaClient]:
    """Create Ollama clients for all model tiers.

    Args:
        available_models: Optional dict mapping tiers to specific model names
        base_url: Ollama API base URL

    Returns:
        Dictionary mapping ModelTier to OllamaClient
    """
    clients = {}

    for tier, default_config in DEFAULT_OLLAMA_CONFIGS.items():
        # Use provided model name or default
        model_name = (
            available_models.get(tier, default_config.model_name)
            if available_models
            else default_config.model_name
        )

        config = OllamaModelConfig(
            tier=tier,
            model_name=model_name,
            url=base_url,
            max_tokens=default_config.max_tokens,
            typical_latency_ms=default_config.typical_latency_ms,
        )

        clients[tier] = OllamaClient(config)

    return clients


def create_single_model_clients(
    model_name: str = "llama3.2",
    base_url: str = "http://localhost:11434",
) -> Dict[ModelTier, OllamaClient]:
    """Create clients that all use the same model (for testing).

    This is useful when you only have one model available locally.

    Args:
        model_name: The Ollama model to use for all tiers
        base_url: Ollama API base URL

    Returns:
        Dictionary mapping ModelTier to OllamaClient
    """
    return create_ollama_clients(
        available_models={
            ModelTier.SMALL: model_name,
            ModelTier.MEDIUM: model_name,
            ModelTier.LARGE: model_name,
        },
        base_url=base_url,
    )

