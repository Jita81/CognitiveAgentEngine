"""Tests for model infrastructure (Phase 2)."""

import pytest
from httpx import AsyncClient

from src.infrastructure.budget_manager import (
    BUDGET_ALLOCATION,
    COST_PER_1K_TOKENS,
    THROTTLE_THRESHOLDS,
    TokenBudgetManager,
)
from src.infrastructure.model_client import (
    DEFAULT_MODEL_CONFIGS,
    InferenceRequest,
    InferenceResponse,
    ModelClient,
    ModelConfig,
    ModelTier,
)
from src.infrastructure.model_client_mock import MockConfig, MockModelClient
from src.infrastructure.model_router import (
    COGNITIVE_TIER_CONFIGS,
    CognitiveTier,
    ModelRouter,
    create_router_with_mock_clients,
)


# =============================================================================
# Model Client Tests
# =============================================================================


class TestModelTier:
    """Tests for ModelTier enum."""

    def test_tier_values(self):
        """All tier values should be defined."""
        assert ModelTier.SMALL.value == "small"
        assert ModelTier.MEDIUM.value == "medium"
        assert ModelTier.LARGE.value == "large"

    def test_tier_count(self):
        """Should have exactly 3 tiers."""
        assert len(ModelTier) == 3


class TestModelConfig:
    """Tests for ModelConfig."""

    def test_default_configs_exist(self):
        """Default configs should exist for all tiers."""
        for tier in ModelTier:
            assert tier in DEFAULT_MODEL_CONFIGS
            config = DEFAULT_MODEL_CONFIGS[tier]
            assert config.tier == tier
            assert config.url
            assert config.model_name
            assert config.max_tokens > 0

    def test_cost_increases_with_tier(self):
        """Cost should increase with tier size."""
        small_cost = DEFAULT_MODEL_CONFIGS[ModelTier.SMALL].cost_per_1k_tokens
        medium_cost = DEFAULT_MODEL_CONFIGS[ModelTier.MEDIUM].cost_per_1k_tokens
        large_cost = DEFAULT_MODEL_CONFIGS[ModelTier.LARGE].cost_per_1k_tokens

        assert small_cost < medium_cost < large_cost


class TestInferenceRequest:
    """Tests for InferenceRequest."""

    def test_default_values(self):
        """Request should have sensible defaults."""
        request = InferenceRequest(prompt="test")
        assert request.max_tokens == 256
        assert request.temperature == 0.7
        assert request.top_p == 0.95
        assert request.stop is None

    def test_to_vllm_payload(self):
        """Should convert to vLLM API format."""
        request = InferenceRequest(
            prompt="Hello world",
            max_tokens=100,
            temperature=0.5,
        )
        payload = request.to_vllm_payload("test-model")

        assert payload["model"] == "test-model"
        assert payload["prompt"] == "Hello world"
        assert payload["max_tokens"] == 100
        assert payload["temperature"] == 0.5


class TestMockModelClient:
    """Tests for MockModelClient."""

    @pytest.fixture
    def mock_client(self) -> MockModelClient:
        """Create a mock client for testing."""
        config = DEFAULT_MODEL_CONFIGS[ModelTier.SMALL]
        return MockModelClient(config=config)

    @pytest.mark.asyncio
    async def test_generate_returns_response(self, mock_client):
        """Generate should return an InferenceResponse."""
        request = InferenceRequest(prompt="Test prompt")
        response = await mock_client.generate(request)

        assert isinstance(response, InferenceResponse)
        assert response.text
        assert response.model_used == mock_client.config.model_name
        assert response.tier_used == ModelTier.SMALL
        assert response.total_tokens > 0
        assert response.latency_ms > 0

    @pytest.mark.asyncio
    async def test_health_check_default_healthy(self, mock_client):
        """Health check should return True by default."""
        assert await mock_client.health_check() is True

    @pytest.mark.asyncio
    async def test_health_check_unhealthy(self, mock_client):
        """Health check should return False when set unhealthy."""
        mock_client.set_healthy(False)
        assert await mock_client.health_check() is False

    @pytest.mark.asyncio
    async def test_call_history_tracked(self, mock_client):
        """Calls should be tracked in history."""
        assert mock_client.get_call_count() == 0

        request = InferenceRequest(prompt="Test")
        await mock_client.generate(request)

        assert mock_client.get_call_count() == 1
        assert mock_client.get_last_request() == request

    @pytest.mark.asyncio
    async def test_token_tracking(self, mock_client):
        """Tokens should be tracked."""
        assert mock_client.get_total_tokens() == 0

        request = InferenceRequest(prompt="Test prompt")
        await mock_client.generate(request)

        assert mock_client.get_total_tokens() > 0

    @pytest.mark.asyncio
    async def test_failure_injection(self, mock_client):
        """Should fail when failure_rate is 1.0."""
        mock_client.set_failure_rate(1.0)
        request = InferenceRequest(prompt="Test")

        with pytest.raises(RuntimeError, match="Simulated failure"):
            await mock_client.generate(request)


# =============================================================================
# Budget Manager Tests
# =============================================================================


class TestTokenBudgetManager:
    """Tests for TokenBudgetManager."""

    @pytest.fixture
    def budget_manager(self) -> TokenBudgetManager:
        """Create a budget manager for testing."""
        return TokenBudgetManager(hourly_budget_usd=15.0)

    def test_initial_state(self, budget_manager):
        """Initial state should have zero usage."""
        status = budget_manager.get_status()
        assert status.total_cost_usd == 0
        assert status.overall_utilization == 0

    def test_record_usage(self, budget_manager):
        """Recording usage should update tracking."""
        budget_manager.record_usage(ModelTier.SMALL, 1000, "agent-1")

        assert budget_manager.get_tier_tokens(ModelTier.SMALL) == 1000
        assert budget_manager.get_agent_usage("agent-1") == 1000

    def test_multiple_agents_tracked(self, budget_manager):
        """Multiple agents should be tracked separately."""
        budget_manager.record_usage(ModelTier.SMALL, 500, "agent-1")
        budget_manager.record_usage(ModelTier.MEDIUM, 300, "agent-2")

        assert budget_manager.get_agent_usage("agent-1") == 500
        assert budget_manager.get_agent_usage("agent-2") == 300

    def test_throttle_at_threshold(self, budget_manager):
        """Should throttle when utilization exceeds threshold."""
        # Calculate tokens needed to exceed threshold
        budget = budget_manager.hourly_budget_usd * BUDGET_ALLOCATION[ModelTier.LARGE]
        cost_per_token = COST_PER_1K_TOKENS[ModelTier.LARGE] / 1000
        threshold = THROTTLE_THRESHOLDS[ModelTier.LARGE]

        # Tokens to exceed threshold
        tokens_needed = int((budget * threshold / cost_per_token) + 1000)

        budget_manager.record_usage(ModelTier.LARGE, tokens_needed, "agent-1")

        assert budget_manager.should_throttle(ModelTier.LARGE) is True

    def test_no_throttle_below_threshold(self, budget_manager):
        """Should not throttle below threshold."""
        # Small usage should not trigger throttle
        budget_manager.record_usage(ModelTier.SMALL, 100, "agent-1")

        assert budget_manager.should_throttle(ModelTier.SMALL) is False

    def test_recommend_downgrade(self, budget_manager):
        """Should recommend downgrade when throttled."""
        # Force large tier to throttle
        budget = budget_manager.hourly_budget_usd * BUDGET_ALLOCATION[ModelTier.LARGE]
        cost_per_token = COST_PER_1K_TOKENS[ModelTier.LARGE] / 1000
        tokens_needed = int((budget * 0.8 / cost_per_token) + 1000)

        budget_manager.record_usage(ModelTier.LARGE, tokens_needed, "agent-1")

        downgrade = budget_manager.recommend_downgrade(ModelTier.LARGE)
        assert downgrade == ModelTier.MEDIUM

    def test_no_downgrade_from_small(self, budget_manager):
        """Small tier should not have a downgrade option."""
        downgrade = budget_manager.recommend_downgrade(ModelTier.SMALL)
        assert downgrade is None

    def test_reset_clears_counters(self, budget_manager):
        """Reset should clear all counters."""
        budget_manager.record_usage(ModelTier.SMALL, 1000, "agent-1")
        budget_manager.reset()

        assert budget_manager.get_tier_tokens(ModelTier.SMALL) == 0
        assert budget_manager.get_agent_usage("agent-1") == 0

    def test_status_includes_all_tiers(self, budget_manager):
        """Status should include all tiers."""
        status = budget_manager.get_status()

        for tier in ModelTier:
            assert tier in status.by_tier


# =============================================================================
# Model Router Tests
# =============================================================================


class TestCognitiveTier:
    """Tests for CognitiveTier enum."""

    def test_tier_order(self):
        """Tiers should have correct ordering."""
        assert CognitiveTier.REFLEX.value < CognitiveTier.REACTIVE.value
        assert CognitiveTier.REACTIVE.value < CognitiveTier.DELIBERATE.value
        assert CognitiveTier.DELIBERATE.value < CognitiveTier.ANALYTICAL.value
        assert CognitiveTier.ANALYTICAL.value < CognitiveTier.COMPREHENSIVE.value

    def test_configs_exist(self):
        """All tiers should have configurations."""
        for tier in CognitiveTier:
            assert tier in COGNITIVE_TIER_CONFIGS
            config = COGNITIVE_TIER_CONFIGS[tier]
            assert config.max_tokens > 0
            assert config.timeout_ms > 0


class TestModelRouter:
    """Tests for ModelRouter."""

    @pytest.fixture
    def router(self) -> ModelRouter:
        """Create a router with mock clients."""
        return create_router_with_mock_clients()

    @pytest.mark.asyncio
    async def test_route_reflex_uses_small(self, router):
        """REFLEX tier should use SMALL model."""
        request = InferenceRequest(prompt="Quick test")
        response = await router.route(CognitiveTier.REFLEX, request, "agent-1")

        assert response.tier_used == ModelTier.SMALL

    @pytest.mark.asyncio
    async def test_route_reactive_uses_medium(self, router):
        """REACTIVE tier should use MEDIUM model."""
        request = InferenceRequest(prompt="Test prompt")
        response = await router.route(CognitiveTier.REACTIVE, request, "agent-1")

        assert response.tier_used == ModelTier.MEDIUM

    @pytest.mark.asyncio
    async def test_route_deliberate_uses_large(self, router):
        """DELIBERATE tier should use LARGE model."""
        request = InferenceRequest(prompt="Complex analysis needed")
        response = await router.route(CognitiveTier.DELIBERATE, request, "agent-1")

        assert response.tier_used == ModelTier.LARGE

    @pytest.mark.asyncio
    async def test_route_enforces_max_tokens(self, router):
        """Router should enforce tier max tokens."""
        tier_config = COGNITIVE_TIER_CONFIGS[CognitiveTier.REFLEX]

        # Request more tokens than tier allows
        request = InferenceRequest(prompt="Test", max_tokens=10000)
        await router.route(CognitiveTier.REFLEX, request, "agent-1")

        # Request should have been capped
        assert request.max_tokens == tier_config.max_tokens

    @pytest.mark.asyncio
    async def test_fallback_on_unhealthy(self, router):
        """Should fall back when tier is unhealthy."""
        # Mark large tier as unhealthy
        router.set_tier_health(ModelTier.LARGE, False)

        request = InferenceRequest(prompt="Test")
        response = await router.route(CognitiveTier.DELIBERATE, request, "agent-1")

        # Should have fallen back to MEDIUM
        assert response.tier_used == ModelTier.MEDIUM

    @pytest.mark.asyncio
    async def test_health_check(self, router):
        """Health check should return status for all tiers."""
        results = await router.check_health()

        assert ModelTier.SMALL in results
        assert ModelTier.MEDIUM in results
        assert ModelTier.LARGE in results

    def test_get_status(self, router):
        """Status should include health and budget."""
        status = router.get_status()

        assert "small" in status.health
        assert "medium" in status.health
        assert "large" in status.health
        assert status.budget is not None

    @pytest.mark.asyncio
    async def test_usage_recorded(self, router):
        """Usage should be recorded in budget manager."""
        request = InferenceRequest(prompt="Test prompt")
        await router.route(CognitiveTier.REFLEX, request, "agent-1")

        usage = router.budget_manager.get_agent_usage("agent-1")
        assert usage > 0

    @pytest.mark.asyncio
    async def test_routing_history(self, router):
        """Routing decisions should be recorded."""
        request = InferenceRequest(prompt="Test")
        await router.route(CognitiveTier.REFLEX, request, "agent-1")

        history = router.get_routing_history(limit=1)
        assert len(history) == 1
        assert history[0].cognitive_tier == CognitiveTier.REFLEX


# =============================================================================
# API Endpoint Tests
# =============================================================================


@pytest.mark.asyncio
async def test_models_status_endpoint(client: AsyncClient):
    """GET /v1/models/status should return router status."""
    response = await client.get("/v1/models/status")

    assert response.status_code == 200
    data = response.json()
    assert "health" in data
    assert "budget" in data
    assert "active_requests" in data


@pytest.mark.asyncio
async def test_models_tiers_endpoint(client: AsyncClient):
    """GET /v1/models/tiers should return tier configurations."""
    response = await client.get("/v1/models/tiers")

    assert response.status_code == 200
    data = response.json()
    assert "tiers" in data
    assert "reflex" in data["tiers"]
    assert "deliberate" in data["tiers"]


@pytest.mark.asyncio
async def test_models_generate_endpoint(client: AsyncClient):
    """POST /v1/models/generate should generate text."""
    response = await client.post(
        "/v1/models/generate",
        json={
            "prompt": "Hello, world!",
            "cognitive_tier": "reflex",
            "max_tokens": 50,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "text" in data
    assert "tier_used" in data
    assert "latency_ms" in data


@pytest.mark.asyncio
async def test_models_generate_invalid_tier(client: AsyncClient):
    """POST /v1/models/generate with invalid tier should fail."""
    response = await client.post(
        "/v1/models/generate",
        json={
            "prompt": "Test",
            "cognitive_tier": "invalid_tier",
        },
    )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_models_budget_endpoint(client: AsyncClient):
    """GET /v1/models/budget should return budget status."""
    response = await client.get("/v1/models/budget")

    assert response.status_code == 200
    data = response.json()
    assert "hourly_budget_usd" in data
    assert "by_tier" in data


@pytest.mark.asyncio
async def test_models_health_check_endpoint(client: AsyncClient):
    """POST /v1/models/health-check should trigger health check."""
    response = await client.post("/v1/models/health-check")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert "health" in data

