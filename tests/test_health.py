"""Tests for health check endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test the liveness probe endpoint."""
    response = await client.get("/health")
    
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "0.1.0"


@pytest.mark.asyncio
async def test_health_check_response_format(client: AsyncClient):
    """Test that health check returns correct format."""
    response = await client.get("/health")
    
    assert response.status_code == 200
    
    data = response.json()
    assert "status" in data
    assert "version" in data
    assert isinstance(data["status"], str)
    assert isinstance(data["version"], str)


@pytest.mark.asyncio
async def test_readiness_check_database_only(client: AsyncClient):
    """Test the readiness probe with database check.
    
    Note: This test uses SQLite which doesn't have Redis,
    so we only check database connectivity.
    """
    response = await client.get("/health/ready")
    
    assert response.status_code == 200
    
    data = response.json()
    assert "status" in data
    assert "checks" in data
    assert "database" in data["checks"]
    
    # Database should be ok with our test SQLite setup
    assert data["checks"]["database"] == "ok"


@pytest.mark.asyncio
async def test_readiness_response_structure(client: AsyncClient):
    """Test that readiness check returns correct structure."""
    response = await client.get("/health/ready")
    
    assert response.status_code == 200
    
    data = response.json()
    
    # Check top-level structure
    assert "status" in data
    assert "checks" in data
    
    # Status should be either "ready" or "not_ready"
    assert data["status"] in ["ready", "not_ready"]
    
    # Checks should be a dict
    assert isinstance(data["checks"], dict)


class TestHealthEndpointContract:
    """Test the contract of health endpoints."""

    @pytest.mark.asyncio
    async def test_health_is_idempotent(self, client: AsyncClient):
        """Health check should be idempotent."""
        response1 = await client.get("/health")
        response2 = await client.get("/health")
        
        assert response1.status_code == response2.status_code
        assert response1.json() == response2.json()

    @pytest.mark.asyncio
    async def test_health_allows_get_only(self, client: AsyncClient):
        """Health check should only allow GET requests."""
        # GET should work
        get_response = await client.get("/health")
        assert get_response.status_code == 200
        
        # POST should fail
        post_response = await client.post("/health")
        assert post_response.status_code == 405

    @pytest.mark.asyncio
    async def test_readiness_allows_get_only(self, client: AsyncClient):
        """Readiness check should only allow GET requests."""
        # GET should work
        get_response = await client.get("/health/ready")
        assert get_response.status_code == 200
        
        # POST should fail
        post_response = await client.post("/health/ready")
        assert post_response.status_code == 405

