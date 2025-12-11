"""Tests for agent API endpoints and models."""

from datetime import datetime
from uuid import uuid4

import pytest
from httpx import AsyncClient

from src.agents.models import (
    AgentProfile,
    AgentProfileCreate,
    CommunicationStyle,
    PersonalityMarkers,
    SkillSet,
    SocialMarkers,
)
from src.agents.formatter import ProfileFormatter


# =============================================================================
# Sample Agent Data
# =============================================================================

SAMPLE_AGENT_DATA = {
    "name": "Alex Chen",
    "role": "Senior Backend Developer",
    "title": "Principal Consultant",
    "backstory_summary": "10 years building distributed systems at scale. Led teams of 5-15 engineers. Specializes in Python and Go backends. Known for pragmatic architecture decisions.",
    "years_experience": 10,
    "skills": {
        "technical": {"python": 9, "go": 7, "system_design": 8, "postgresql": 8},
        "domains": {"fintech": 7, "enterprise": 6},
        "soft_skills": {"communication": 7, "mentoring": 7},
    },
    "personality_markers": {
        "openness": 7,
        "conscientiousness": 8,
        "extraversion": 5,
        "agreeableness": 6,
        "neuroticism": 3,
        "perfectionism": 6,
        "pragmatism": 8,
        "risk_tolerance": 5,
    },
    "social_markers": {
        "confidence": 7,
        "assertiveness": 6,
        "deference": 4,
        "curiosity": 7,
        "social_calibration": 7,
        "status_sensitivity": 5,
        "facilitation_instinct": 5,
        "comfort_in_spotlight": 4,
        "comfort_with_conflict": 6,
    },
    "communication_style": {
        "vocabulary_level": "technical",
        "sentence_structure": "moderate",
        "formality": "professional",
        "uses_analogies": True,
        "uses_examples": True,
        "asks_clarifying_questions": True,
        "verbal_tics": [],
    },
    "knowledge_domains": ["fintech", "ecommerce", "enterprise"],
    "knowledge_gaps": ["frontend", "mobile", "ml_ops"],
}


def get_minimal_agent_data():
    """Get minimal valid agent data."""
    return {
        "name": "Test Agent",
        "role": "Developer",
        "backstory_summary": "A test agent with minimal configuration for testing purposes. Has basic development skills.",
    }


# =============================================================================
# Model Tests
# =============================================================================


class TestSkillSetModel:
    """Tests for SkillSet model validation."""

    def test_valid_skills(self):
        """Valid skills should pass validation."""
        skills = SkillSet(
            technical={"python": 9, "go": 7},
            domains={"fintech": 5},
            soft_skills={"communication": 8},
        )
        assert skills.technical["python"] == 9

    def test_skill_over_10_raises_error(self):
        """Skills over 10 should raise validation error."""
        with pytest.raises(ValueError, match="must be 0-10"):
            SkillSet(technical={"python": 11})

    def test_skill_negative_raises_error(self):
        """Negative skills should raise validation error."""
        with pytest.raises(ValueError, match="must be 0-10"):
            SkillSet(technical={"python": -1})

    def test_get_top_skills(self):
        """get_top_skills should return highest rated skills."""
        skills = SkillSet(
            technical={"python": 9, "java": 5},
            domains={"fintech": 7},
            soft_skills={"leadership": 8},
        )
        top = skills.get_top_skills(3)
        assert len(top) == 3
        assert top[0] == ("python", 9)
        assert top[1] == ("leadership", 8)
        assert top[2] == ("fintech", 7)

    def test_get_relevance_score(self):
        """get_relevance_score should calculate relevance based on keywords."""
        skills = SkillSet(
            technical={"python": 10, "golang": 5},
            domains={"fintech": 8},
        )
        # "python" matches exactly
        score = skills.get_relevance_score(["python"])
        assert score == 1.0  # 10 / (1 * 10)

        # Python matches (10), rust doesn't match (0)
        # score = 10 / (2 * 10) = 0.5
        score = skills.get_relevance_score(["python", "rust"])
        assert score == 0.5

        # No match
        score = skills.get_relevance_score(["rust"])
        assert score == 0.0
        
        # Empty keywords
        score = skills.get_relevance_score([])
        assert score == 0.0
        
        # Multiple matches
        score = skills.get_relevance_score(["python", "golang"])
        assert score == 0.75  # (10 + 5) / (2 * 10)


class TestPersonalityMarkersModel:
    """Tests for PersonalityMarkers model validation."""

    def test_valid_markers(self):
        """Valid markers should pass validation."""
        markers = PersonalityMarkers(openness=7, conscientiousness=8)
        assert markers.openness == 7

    def test_marker_over_10_raises_error(self):
        """Markers over 10 should raise validation error."""
        with pytest.raises(ValueError):
            PersonalityMarkers(openness=11)

    def test_marker_negative_raises_error(self):
        """Negative markers should raise validation error."""
        with pytest.raises(ValueError):
            PersonalityMarkers(neuroticism=-1)

    def test_default_values(self):
        """Default values should be 5."""
        markers = PersonalityMarkers()
        assert markers.openness == 5
        assert markers.conscientiousness == 5


class TestSocialMarkersModel:
    """Tests for SocialMarkers model validation."""

    def test_valid_markers(self):
        """Valid markers should pass validation."""
        markers = SocialMarkers(confidence=8, assertiveness=6)
        assert markers.confidence == 8

    def test_all_markers_validated(self):
        """All markers should be validated for range."""
        with pytest.raises(ValueError):
            SocialMarkers(comfort_with_conflict=15)


class TestCommunicationStyleModel:
    """Tests for CommunicationStyle model validation."""

    def test_valid_style(self):
        """Valid style should pass validation."""
        style = CommunicationStyle(
            vocabulary_level="technical",
            formality="professional",
        )
        assert style.vocabulary_level == "technical"

    def test_invalid_vocabulary_level(self):
        """Invalid vocabulary level should raise error."""
        with pytest.raises(ValueError, match="vocabulary_level"):
            CommunicationStyle(vocabulary_level="expert")

    def test_invalid_formality(self):
        """Invalid formality should raise error."""
        with pytest.raises(ValueError, match="formality"):
            CommunicationStyle(formality="strict")


class TestAgentProfileCreateModel:
    """Tests for AgentProfileCreate model validation."""

    def test_valid_profile(self):
        """Valid profile should pass validation."""
        profile = AgentProfileCreate(**SAMPLE_AGENT_DATA)
        assert profile.name == "Alex Chen"

    def test_name_too_long(self):
        """Name over 100 chars should raise error."""
        data = get_minimal_agent_data()
        data["name"] = "A" * 101
        with pytest.raises(ValueError):
            AgentProfileCreate(**data)

    def test_backstory_too_short(self):
        """Backstory under 50 chars should raise error."""
        data = get_minimal_agent_data()
        data["backstory_summary"] = "Too short"
        with pytest.raises(ValueError):
            AgentProfileCreate(**data)

    def test_years_experience_over_50(self):
        """Years over 50 should raise error."""
        data = get_minimal_agent_data()
        data["years_experience"] = 51
        with pytest.raises(ValueError):
            AgentProfileCreate(**data)


# =============================================================================
# Formatter Tests
# =============================================================================


class TestProfileFormatter:
    """Tests for ProfileFormatter."""

    @pytest.fixture
    def sample_profile(self) -> AgentProfile:
        """Create a sample profile for testing."""
        now = datetime.utcnow()
        return AgentProfile(
            agent_id=uuid4(),
            name="Alex Chen",
            role="Senior Backend Developer",
            title="Principal Consultant",
            backstory_summary="10 years building distributed systems.",
            years_experience=10,
            skills=SkillSet(
                technical={"python": 9, "system_design": 8},
                domains={"fintech": 7},
                soft_skills={"communication": 7},
            ),
            personality_markers=PersonalityMarkers(
                openness=7,
                conscientiousness=8,
                pragmatism=8,
            ),
            social_markers=SocialMarkers(
                confidence=8,
                deference=3,
                curiosity=8,
                facilitation_instinct=7,
            ),
            communication_style=CommunicationStyle(
                vocabulary_level="technical",
                formality="professional",
            ),
            knowledge_domains=["fintech", "enterprise"],
            knowledge_gaps=["frontend"],
            created_at=now,
            updated_at=now,
        )

    def test_format_identity_minimal(self, sample_profile):
        """Minimal format should be concise."""
        result = ProfileFormatter.format_identity_minimal(sample_profile)
        assert "Alex Chen" in result
        assert "Senior Backend Developer" in result
        # Should be short
        assert len(result) < 100

    def test_format_identity_brief(self, sample_profile):
        """Brief format should include top skills."""
        result = ProfileFormatter.format_identity_brief(sample_profile)
        assert "Alex Chen" in result
        assert "python" in result.lower()
        assert "10 years" in result

    def test_format_identity_full(self, sample_profile):
        """Full format should include comprehensive info."""
        result = ProfileFormatter.format_identity_full(sample_profile)
        assert "IDENTITY:" in result
        assert "SKILLS & EXPERTISE:" in result
        assert "COMMUNICATION STYLE:" in result
        assert "technical" in result.lower()

    def test_format_social_context(self, sample_profile):
        """Social context should describe traits."""
        result = ProfileFormatter.format_social_context(sample_profile)
        # High confidence
        assert "confident" in result.lower()
        # High curiosity
        assert "question" in result.lower()

    def test_format_for_tier_reflex(self, sample_profile):
        """REFLEX tier should use minimal format."""
        result = ProfileFormatter.format_for_tier(sample_profile, "reflex")
        assert len(result) < 100

    def test_format_for_tier_deliberate(self, sample_profile):
        """DELIBERATE tier should use full format."""
        result = ProfileFormatter.format_for_tier(
            sample_profile, "deliberate", include_social=True
        )
        assert "IDENTITY:" in result
        assert "SOCIAL STYLE:" in result


# =============================================================================
# API Endpoint Tests
# =============================================================================


@pytest.mark.asyncio
async def test_create_agent_valid(client: AsyncClient):
    """Create agent with valid data should return 201."""
    response = await client.post("/v1/agents", json=SAMPLE_AGENT_DATA)
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Alex Chen"
    assert data["role"] == "Senior Backend Developer"
    assert "agent_id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_create_agent_minimal(client: AsyncClient):
    """Create agent with minimal data should succeed."""
    response = await client.post("/v1/agents", json=get_minimal_agent_data())
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Agent"


@pytest.mark.asyncio
async def test_create_agent_invalid_skill_over_10(client: AsyncClient):
    """Create agent with skill > 10 should return 422."""
    data = get_minimal_agent_data()
    data["skills"] = {"technical": {"python": 11}}
    
    response = await client.post("/v1/agents", json=data)
    
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_agent_invalid_skill_negative(client: AsyncClient):
    """Create agent with negative skill should return 422."""
    data = get_minimal_agent_data()
    data["skills"] = {"technical": {"python": -1}}
    
    response = await client.post("/v1/agents", json=data)
    
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_agent_missing_required_field(client: AsyncClient):
    """Create agent missing required field should return 422."""
    data = {"name": "Test"}  # Missing role and backstory
    
    response = await client.post("/v1/agents", json=data)
    
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_agent_exists(client: AsyncClient):
    """Get existing agent should return 200."""
    # Create agent first
    create_response = await client.post("/v1/agents", json=get_minimal_agent_data())
    agent_id = create_response.json()["agent_id"]
    
    # Get agent
    response = await client.get(f"/v1/agents/{agent_id}")
    
    assert response.status_code == 200
    assert response.json()["agent_id"] == agent_id


@pytest.mark.asyncio
async def test_get_agent_not_found(client: AsyncClient):
    """Get non-existent agent should return 404."""
    fake_id = uuid4()
    response = await client.get(f"/v1/agents/{fake_id}")
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_agents_empty(client: AsyncClient):
    """List agents when none exist should return empty list."""
    response = await client.get("/v1/agents")
    
    assert response.status_code == 200
    data = response.json()
    assert "agents" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_list_agents_with_results(client: AsyncClient):
    """List agents should return created agents."""
    # Create an agent
    await client.post("/v1/agents", json=get_minimal_agent_data())
    
    response = await client.get("/v1/agents")
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert len(data["agents"]) >= 1


@pytest.mark.asyncio
async def test_list_agents_with_role_filter(client: AsyncClient):
    """List agents with role filter should filter results."""
    # Create agents with different roles
    data1 = get_minimal_agent_data()
    data1["role"] = "Backend Developer"
    await client.post("/v1/agents", json=data1)
    
    data2 = get_minimal_agent_data()
    data2["name"] = "Agent 2"
    data2["role"] = "Frontend Developer"
    await client.post("/v1/agents", json=data2)
    
    # Filter by role
    response = await client.get("/v1/agents?role=Backend")
    
    assert response.status_code == 200
    data = response.json()
    for agent in data["agents"]:
        assert "backend" in agent["role"].lower()


@pytest.mark.asyncio
async def test_update_agent_name(client: AsyncClient):
    """Update agent name should succeed."""
    # Create agent
    create_response = await client.post("/v1/agents", json=get_minimal_agent_data())
    agent_id = create_response.json()["agent_id"]
    
    # Update name
    response = await client.patch(f"/v1/agents/{agent_id}", json={"name": "Updated Name"})
    
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Name"


@pytest.mark.asyncio
async def test_update_agent_not_found(client: AsyncClient):
    """Update non-existent agent should return 404."""
    fake_id = uuid4()
    response = await client.patch(f"/v1/agents/{fake_id}", json={"name": "Test"})
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_agent(client: AsyncClient):
    """Delete agent should return 204."""
    # Create agent
    create_response = await client.post("/v1/agents", json=get_minimal_agent_data())
    agent_id = create_response.json()["agent_id"]
    
    # Delete agent
    response = await client.delete(f"/v1/agents/{agent_id}")
    
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_get_deleted_agent_returns_404(client: AsyncClient):
    """Get deleted agent should return 404."""
    # Create agent
    create_response = await client.post("/v1/agents", json=get_minimal_agent_data())
    agent_id = create_response.json()["agent_id"]
    
    # Delete agent
    await client.delete(f"/v1/agents/{agent_id}")
    
    # Try to get deleted agent
    response = await client.get(f"/v1/agents/{agent_id}")
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_agent_not_found(client: AsyncClient):
    """Delete non-existent agent should return 404."""
    fake_id = uuid4()
    response = await client.delete(f"/v1/agents/{fake_id}")
    
    assert response.status_code == 404
