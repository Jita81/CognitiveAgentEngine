"""Tests for Social Intelligence API endpoints.

Tests for the social API routes from Phase 5.

Note: Tests marked with @pytest.mark.db require a running database.
Run these tests when the database is available.
"""

import pytest
from uuid import uuid4
from datetime import datetime, timezone
import os

from fastapi.testclient import TestClient

from src.api.main import app
from src.agents.models import (
    AgentProfile,
    SkillSet,
    PersonalityMarkers,
    SocialMarkers,
    CommunicationStyle,
)

# Skip database tests if DATABASE_URL is not configured
DB_AVAILABLE = os.environ.get("DATABASE_URL") is not None

requires_db = pytest.mark.skipif(
    not DB_AVAILABLE,
    reason="Database not available (set DATABASE_URL to run DB tests)"
)


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def sample_agent_data():
    """Sample agent creation data."""
    return {
        "name": "TestAgent",
        "role": "Software Engineer",
        "backstory_summary": "A test agent with Python expertise for testing social intelligence features.",
        "skills": {
            "technical": {"python": 9, "testing": 8},
            "domains": {"backend": 8},
            "soft_skills": {"communication": 7},
        },
        "personality_markers": {
            "openness": 7,
            "conscientiousness": 8,
            "extraversion": 5,
            "agreeableness": 7,
            "neuroticism": 3,
        },
        "social_markers": {
            "confidence": 7,
            "assertiveness": 6,
            "deference": 4,
            "curiosity": 8,
            "social_calibration": 7,
            "status_sensitivity": 4,
            "facilitation_instinct": 6,
            "comfort_in_spotlight": 6,
            "comfort_with_conflict": 5,
        },
    }


class TestEvaluateEndpoint:
    """Tests for POST /v1/social/evaluate endpoint."""
    
    @requires_db
    @pytest.mark.asyncio
    async def test_evaluate_direct_address(self, client, sample_agent_data):
        """Test evaluate returns MUST_RESPOND for direct address."""
        # First create an agent
        response = client.post("/v1/agents", json=sample_agent_data)
        assert response.status_code == 201
        agent_id = response.json()["agent_id"]
        
        # Now evaluate with direct address
        eval_request = {
            "agent_id": agent_id,
            "stimulus": {
                "content": "What do you think about this approach?",
                "directed_at": [agent_id],
                "topic": "python design",
            },
            "context": {
                "participants": [],
                "group_size": 3,
                "my_role": "participant",
            },
        }
        
        response = client.post("/v1/social/evaluate", json=eval_request)
        
        assert response.status_code == 200
        data = response.json()
        assert data["intent"] == "must_respond"
        assert data["confidence"] == 1.0
        assert data["should_speak"] is True
        assert data["is_mandatory"] is True
    
    @requires_db
    @pytest.mark.asyncio
    async def test_evaluate_low_relevance(self, client, sample_agent_data):
        """Test evaluate returns PASSIVE_AWARENESS for low relevance."""
        # Create agent
        response = client.post("/v1/agents", json=sample_agent_data)
        agent_id = response.json()["agent_id"]
        
        # Evaluate with irrelevant topic
        eval_request = {
            "agent_id": agent_id,
            "stimulus": {
                "content": "Let's discuss our marketing strategy for Q4.",
                "topic": "marketing strategy branding",
            },
            "context": {
                "participants": [],
                "group_size": 5,
                "my_role": "participant",
            },
        }
        
        response = client.post("/v1/social/evaluate", json=eval_request)
        
        assert response.status_code == 200
        data = response.json()
        assert data["intent"] == "passive"
        assert data["should_speak"] is False
    
    @requires_db
    @pytest.mark.asyncio
    async def test_evaluate_high_relevance(self, client, sample_agent_data):
        """Test evaluate returns contribution intent for high relevance."""
        # Create agent
        response = client.post("/v1/agents", json=sample_agent_data)
        agent_id = response.json()["agent_id"]
        
        # Evaluate with relevant topic
        eval_request = {
            "agent_id": agent_id,
            "stimulus": {
                "content": "How should we structure the Python backend?",
                "topic": "python backend architecture",
            },
            "context": {
                "participants": [],
                "group_size": 3,
                "my_role": "participant",
            },
        }
        
        response = client.post("/v1/social/evaluate", json=eval_request)
        
        assert response.status_code == 200
        data = response.json()
        assert data["intent"] in ["should", "may"]
        assert data["should_speak"] is True
    
    @requires_db
    @pytest.mark.asyncio
    async def test_evaluate_agent_not_found(self, client):
        """Test evaluate with non-existent agent."""
        fake_id = str(uuid4())
        
        eval_request = {
            "agent_id": fake_id,
            "stimulus": {
                "content": "Test",
                "topic": "test",
            },
            "context": {
                "participants": [],
                "group_size": 1,
            },
        }
        
        response = client.post("/v1/social/evaluate", json=eval_request)
        
        assert response.status_code == 404


class TestBuildContextEndpoint:
    """Tests for POST /v1/social/context/from-meeting endpoint."""
    
    @requires_db
    @pytest.mark.asyncio
    async def test_build_context_from_meeting(self, client, sample_agent_data):
        """Test building context from meeting state."""
        # Create agent
        response = client.post("/v1/agents", json=sample_agent_data)
        agent_id = response.json()["agent_id"]
        
        # Build context
        build_request = {
            "agent_id": agent_id,
            "meeting_state": {
                "participants": [
                    {
                        "agent_id": "other-1",
                        "name": "Alice",
                        "role": "designer",
                        "expertise": ["ux", "ui"],
                    },
                    {
                        "agent_id": "other-2",
                        "name": "Bob",
                        "role": "pm",
                    },
                ],
                "current_topic": "sprint planning",
                "phase": "exploring",
                "energy": "engaged",
            },
        }
        
        response = client.post("/v1/social/context/from-meeting", json=build_request)
        
        assert response.status_code == 200
        data = response.json()
        assert data["group_size"] == 2
        assert data["topic_under_discussion"] == "sprint planning"
        assert data["discussion_phase"] == "exploring"
        assert data["energy_level"] == "engaged"
    
    @requires_db
    @pytest.mark.asyncio
    async def test_build_context_group_type(self, client, sample_agent_data):
        """Test that group type is correctly calculated."""
        # Create agent
        response = client.post("/v1/agents", json=sample_agent_data)
        agent_id = response.json()["agent_id"]
        
        # Build context with 7 participants (meeting size)
        build_request = {
            "agent_id": agent_id,
            "meeting_state": {
                "participants": [
                    {"agent_id": f"agent-{i}", "name": f"Person-{i}"}
                    for i in range(7)
                ],
            },
        }
        
        response = client.post("/v1/social/context/from-meeting", json=build_request)
        
        assert response.status_code == 200
        data = response.json()
        assert data["group_type"] == "meeting"


class TestSpeakingStatusEndpoint:
    """Tests for GET /v1/social/agents/{agent_id}/speaking-status endpoint."""
    
    @requires_db
    @pytest.mark.asyncio
    async def test_get_speaking_status(self, client, sample_agent_data):
        """Test getting agent's speaking status."""
        # Create agent
        response = client.post("/v1/agents", json=sample_agent_data)
        agent_id = response.json()["agent_id"]
        
        # Get speaking status
        response = client.get(f"/v1/social/agents/{agent_id}/speaking-status")
        
        assert response.status_code == 200
        data = response.json()
        assert data["agent_id"] == agent_id
        assert data["agent_name"] == "TestAgent"
        assert "ready_to_share_count" in data
        assert "held_insights_count" in data
        assert "active_thoughts_count" in data
        assert "has_critical_input" in data
    
    @requires_db
    @pytest.mark.asyncio
    async def test_speaking_status_agent_not_found(self, client):
        """Test speaking status with non-existent agent."""
        fake_id = str(uuid4())
        
        response = client.get(f"/v1/social/agents/{fake_id}/speaking-status")
        
        assert response.status_code == 404


class TestIntentsEndpoint:
    """Tests for GET /v1/social/intents endpoint."""
    
    @pytest.mark.asyncio
    async def test_get_intents(self, client):
        """Test getting all externalization intents."""
        response = client.get("/v1/social/intents")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have 5 intents
        assert len(data) == 5
        
        # Check structure
        intent_values = [item["value"] for item in data]
        assert "must_respond" in intent_values
        assert "should" in intent_values
        assert "may" in intent_values
        assert "listen" in intent_values
        assert "passive" in intent_values
        
        # Check each has required fields
        for item in data:
            assert "value" in item
            assert "name" in item
            assert "description" in item


class TestGroupTypesEndpoint:
    """Tests for GET /v1/social/group-types endpoint."""
    
    @pytest.mark.asyncio
    async def test_get_group_types(self, client):
        """Test getting all group types."""
        response = client.get("/v1/social/group-types")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have 6 group types
        assert len(data) == 6
        
        # Check structure
        group_values = [item["value"] for item in data]
        assert "solo" in group_values
        assert "pair" in group_values
        assert "small_team" in group_values
        assert "meeting" in group_values
        assert "large_group" in group_values
        assert "army" in group_values
        
        # Check thresholds
        for item in data:
            assert "contribution_threshold" in item
            assert "size_range" in item
            
            # Verify threshold increases with group size
            if item["value"] == "solo":
                assert item["contribution_threshold"] == 0.0
            elif item["value"] == "army":
                assert item["contribution_threshold"] == 0.9

