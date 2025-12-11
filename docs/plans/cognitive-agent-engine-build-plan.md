# Cognitive Agent Engine - Build Plan

**Version:** 1.0  
**Date:** December 2, 2024  
**Reference:** CAE-MVP-001 Requirements Document  
**Target Duration:** 12 weeks

---

## Table of Contents

1. [Build Philosophy](#1-build-philosophy)
2. [Phase Overview](#2-phase-overview)
3. [Phase 0: Foundation](#3-phase-0-foundation)
4. [Phase 1: Agent Identity & Skills](#4-phase-1-agent-identity--skills)
5. [Phase 2: Model Infrastructure](#5-phase-2-model-infrastructure)
6. [Phase 3: Cognitive Tiers](#6-phase-3-cognitive-tiers)
7. [Phase 4: Internal Mind](#7-phase-4-internal-mind)
8. [Phase 5: Social Intelligence](#8-phase-5-social-intelligence)
9. [Phase 6: Memory Architecture](#9-phase-6-memory-architecture)
10. [Phase 7: Multi-Agent Coordination](#10-phase-7-multi-agent-coordination)
11. [Phase 8: Pattern Learning](#11-phase-8-pattern-learning)
12. [Phase 9: Production Hardening](#12-phase-9-production-hardening)
13. [Phase 10: Integration & Validation](#13-phase-10-integration--validation)
14. [Quality Gates](#14-quality-gates)
15. [Risk Mitigation](#15-risk-mitigation)
16. [Resource Requirements](#16-resource-requirements)

---

## 1. Build Philosophy

### 1.1 Core Principle: Cognition First

Each phase adds a layer of cognitive capability:

```
Phase 1:  "Who am I?"           → Identity & Skills
Phase 2:  "How do I think?"     → Model Infrastructure
Phase 3:  "How fast/deep?"      → Cognitive Tiers
Phase 4:  "What am I thinking?" → Internal Mind
Phase 5:  "Should I speak?"     → Social Intelligence
Phase 6:  "What do I remember?" → Memory Architecture
Phase 7:  "Who else is here?"   → Multi-Agent
Phase 8:  "What have I learned?"→ Pattern Learning
Phase 9:  "Am I reliable?"      → Production Hardening
Phase 10: "Does it all work?"   → Integration
```

### 1.2 Build Principles

| Principle | Description |
|-----------|-------------|
| **Vertical Slices** | Each phase delivers working functionality |
| **Test First** | Tests written before implementation |
| **Budget Aware** | Cost tracking from Phase 2 onward |
| **Fail Fast** | Validate assumptions early |
| **Incremental Complexity** | Simple working → sophisticated working |

### 1.3 Key Constraints

- **Budget**: $15/hour maximum infrastructure cost
- **Agents**: 20 concurrent agents target
- **Latency**: REFLEX <200ms, REACTIVE <500ms, DELIBERATE <2s
- **Models**: Self-hosted Qwen2.5 via vLLM

---

## 2. Phase Overview

### 2.1 Timeline

```
Week:  1    2    3    4    5    6    7    8    9    10   11   12
      ├────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┤
P0    ████                                                         Foundation
P1    ░░░░████                                                     Identity
P2         ████████                                                Models
P3              ░░░░████████                                       Cognitive
P4                        ████████                                 Mind
P5                             ░░░░████████                        Social
P6                                       ████████                  Memory
P7                                            ░░░░████             Multi-Agent
P8                                                 ████████        Patterns
P9                                                      ░░░░████   Hardening
P10                                                          ████  Integration

████ = Primary work
░░░░ = Overlap/parallel work
```

### 2.2 Phase Summary

| Phase | Name | Duration | Key Deliverable | Dependencies |
|-------|------|----------|-----------------|--------------|
| 0 | Foundation | 4 days | Project skeleton, DB, health checks | None |
| 1 | Identity & Skills | 5 days | Agent profiles, CRUD API | Phase 0 |
| 2 | Model Infrastructure | 8 days | vLLM serving, model router | Phase 0 |
| 3 | Cognitive Tiers | 7 days | Tiered processing, parallel execution | Phase 1, 2 |
| 4 | Internal Mind | 7 days | Thought model, streams, accumulation | Phase 3 |
| 5 | Social Intelligence | 8 days | Externalization decisions, room reading | Phase 4 |
| 6 | Memory Architecture | 7 days | 4-tier memory, promotion logic | Phase 4 |
| 7 | Multi-Agent | 5 days | Meeting support, 20 agent coordination | Phase 5, 6 |
| 8 | Pattern Learning | 7 days | Pattern extraction, outcome learning | Phase 6 |
| 9 | Production Hardening | 5 days | Safety, resilience, monitoring | Phase 7, 8 |
| 10 | Integration | 5 days | E2E testing, load testing, validation | All |

**Total: ~68 days (~12 weeks with buffer)**

### 2.3 Milestone Gates

| Milestone | Phase | Validation |
|-----------|-------|------------|
| **M1: Agent Responds** | Phase 3 | Single agent processes stimulus → response |
| **M2: Agent Thinks** | Phase 4 | Agent has internal thoughts, may not speak |
| **M3: Agent Knows When to Speak** | Phase 5 | Social intelligence working |
| **M4: Agent Remembers** | Phase 6 | Memory tiers functional |
| **M5: Team Collaborates** | Phase 7 | 20 agents in meeting |
| **M6: Team Learns** | Phase 8 | Patterns extracted from outcomes |
| **M7: Production Ready** | Phase 10 | All acceptance criteria met |

---

## 3. Phase 0: Foundation

### 3.1 Overview

| Attribute | Value |
|-----------|-------|
| **Duration** | 4 days |
| **Goal** | Infrastructure foundation for all subsequent work |
| **Team** | 1 developer |
| **Dependencies** | None |

### 3.2 Objectives

1. Project structure and tooling
2. Database schema and migrations
3. Basic API framework
4. Health and readiness endpoints
5. Docker development environment
6. CI pipeline foundation

### 3.3 Deliverables

#### D0.1: Project Structure

```
cognitive-agent-engine/
├── src/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── health.py
│   │   │   └── agents.py
│   │   ├── middleware/
│   │   │   ├── __init__.py
│   │   │   └── auth.py
│   │   └── dependencies.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py            # Settings management
│   │   └── exceptions.py
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── models.py            # Pydantic models
│   │   └── repository.py        # Database operations
│   ├── cognitive/               # Placeholder for Phase 3
│   │   └── __init__.py
│   ├── social/                  # Placeholder for Phase 5
│   │   └── __init__.py
│   ├── memory/                  # Placeholder for Phase 6
│   │   └── __init__.py
│   └── infrastructure/
│       ├── __init__.py
│       ├── database.py          # SQLAlchemy setup
│       └── redis.py             # Redis client
├── migrations/
│   └── versions/
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_health.py
│   └── test_agents.py
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── pyproject.toml
├── alembic.ini
└── README.md
```

#### D0.2: Database Schema (Initial)

```sql
-- migrations/versions/001_initial.py

-- Agent profiles table
CREATE TABLE agent_profiles (
    agent_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    role VARCHAR(100) NOT NULL,
    title VARCHAR(100),
    backstory_summary TEXT NOT NULL,
    years_experience INT,
    skills JSONB NOT NULL DEFAULT '{}',
    personality_markers JSONB NOT NULL DEFAULT '{}',
    social_markers JSONB NOT NULL DEFAULT '{}',
    communication_style JSONB NOT NULL DEFAULT '{}',
    knowledge_domains JSONB DEFAULT '[]',
    knowledge_gaps JSONB DEFAULT '[]',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP
);

CREATE INDEX idx_agent_profiles_name ON agent_profiles(name) WHERE deleted_at IS NULL;
CREATE INDEX idx_agent_profiles_role ON agent_profiles(role) WHERE deleted_at IS NULL;
CREATE INDEX idx_agent_profiles_deleted ON agent_profiles(deleted_at);
```

#### D0.3: Health Endpoints

```python
# src/api/routes/health.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(tags=["health"])

@router.get("/health")
async def health_check():
    """Liveness probe."""
    return {"status": "healthy", "version": "0.1.0"}

@router.get("/health/ready")
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """Readiness probe - checks dependencies."""
    checks = {}
    
    # Database check
    try:
        await db.execute("SELECT 1")
        checks["database"] = "ok"
    except Exception as e:
        checks["database"] = f"error: {str(e)}"
    
    # Redis check (when available)
    # checks["redis"] = await check_redis()
    
    all_ok = all(v == "ok" for v in checks.values())
    
    return {
        "status": "ready" if all_ok else "not_ready",
        "checks": checks
    }
```

#### D0.4: Docker Compose (Development)

```yaml
# docker/docker-compose.yml
version: '3.8'

services:
  api:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://cae:cae@db:5432/cae
      - REDIS_URL=redis://redis:6379
      - ENVIRONMENT=development
    volumes:
      - ../src:/app/src
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    command: uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: cae
      POSTGRES_USER: cae
      POSTGRES_PASSWORD: cae
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U cae"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

#### D0.5: Configuration Management

```python
# src/core/config.py

from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Service
    service_name: str = "cognitive-agent-engine"
    environment: str = "development"
    log_level: str = "INFO"
    
    # Database
    database_url: str
    database_pool_size: int = 20
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # Model endpoints (Phase 2)
    vllm_small_url: str = ""
    vllm_medium_url: str = ""
    vllm_large_url: str = ""
    
    # Budget (Phase 2)
    hourly_budget_usd: float = 15.0
    budget_alert_threshold: float = 0.8
    
    # Agents
    max_active_agents: int = 20
    agent_memory_limit_mb: int = 100
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

### 3.4 Test Criteria

| Test | Expected Result |
|------|-----------------|
| `docker-compose up` | All services start |
| `GET /health` | Returns `{"status": "healthy"}` |
| `GET /health/ready` | Returns ready with all checks ok |
| Database migration | Schema created successfully |
| pytest runs | All tests pass |

### 3.5 Definition of Done

- [ ] Project structure created
- [ ] pyproject.toml with all dependencies
- [ ] Docker Compose brings up API + DB + Redis
- [ ] Health endpoints respond correctly
- [ ] Database migrations run successfully
- [ ] CI pipeline runs tests
- [ ] README with setup instructions
- [ ] All tests pass

---

## 4. Phase 1: Agent Identity & Skills

### 4.1 Overview

| Attribute | Value |
|-----------|-------|
| **Duration** | 5 days |
| **Goal** | Agents have persistent identity, skills, and personality |
| **Team** | 1 developer |
| **Dependencies** | Phase 0 |

### 4.2 Objectives

1. Complete agent profile model
2. CRUD API for agents
3. Skills and personality validation
4. Agent repository pattern
5. Profile serialization for prompts

### 4.3 Deliverables

#### D1.1: Agent Profile Models

```python
# src/agents/models.py

from pydantic import BaseModel, Field, field_validator
from typing import Dict, List, Optional
from datetime import datetime
from uuid import UUID
from enum import Enum

class CommunicationStyle(BaseModel):
    """How the agent communicates."""
    vocabulary_level: str = Field(
        default="moderate",
        pattern="^(simple|moderate|technical|academic)$"
    )
    sentence_structure: str = Field(
        default="moderate",
        pattern="^(terse|moderate|elaborate)$"
    )
    formality: str = Field(
        default="professional",
        pattern="^(casual|professional|formal)$"
    )
    uses_analogies: bool = True
    uses_examples: bool = True
    asks_clarifying_questions: bool = True
    verbal_tics: List[str] = Field(default_factory=list)

class SkillSet(BaseModel):
    """Agent's skills with validation."""
    
    # All skills are 0-10
    technical: Dict[str, int] = Field(default_factory=dict)
    domains: Dict[str, int] = Field(default_factory=dict)
    soft_skills: Dict[str, int] = Field(default_factory=dict)
    
    @field_validator('technical', 'domains', 'soft_skills')
    @classmethod
    def validate_skill_range(cls, v):
        for skill, level in v.items():
            if not 0 <= level <= 10:
                raise ValueError(f"Skill {skill} must be 0-10, got {level}")
        return v
    
    def get_top_skills(self, n: int = 5) -> List[tuple]:
        """Get top N skills across all categories."""
        all_skills = {**self.technical, **self.domains, **self.soft_skills}
        sorted_skills = sorted(all_skills.items(), key=lambda x: -x[1])
        return sorted_skills[:n]
    
    def get_relevance_score(self, keywords: List[str]) -> float:
        """Calculate relevance to keywords."""
        all_skills = {**self.technical, **self.domains, **self.soft_skills}
        
        matched = []
        for keyword in keywords:
            kw_lower = keyword.lower().replace(" ", "_")
            for skill, level in all_skills.items():
                if kw_lower in skill or skill in kw_lower:
                    matched.append(level)
        
        if not matched:
            return 0.0
        return sum(matched) / (len(matched) * 10)

class PersonalityMarkers(BaseModel):
    """Core personality traits (0-10)."""
    
    # Big Five
    openness: int = Field(default=5, ge=0, le=10)
    conscientiousness: int = Field(default=5, ge=0, le=10)
    extraversion: int = Field(default=5, ge=0, le=10)
    agreeableness: int = Field(default=5, ge=0, le=10)
    neuroticism: int = Field(default=5, ge=0, le=10)
    
    # Professional
    perfectionism: int = Field(default=5, ge=0, le=10)
    pragmatism: int = Field(default=5, ge=0, le=10)
    risk_tolerance: int = Field(default=5, ge=0, le=10)

class SocialMarkers(BaseModel):
    """Social behavior traits (0-10)."""
    
    confidence: int = Field(default=5, ge=0, le=10)
    assertiveness: int = Field(default=5, ge=0, le=10)
    deference: int = Field(default=5, ge=0, le=10)
    curiosity: int = Field(default=5, ge=0, le=10)
    social_calibration: int = Field(default=5, ge=0, le=10)
    status_sensitivity: int = Field(default=5, ge=0, le=10)
    facilitation_instinct: int = Field(default=5, ge=0, le=10)
    comfort_in_spotlight: int = Field(default=5, ge=0, le=10)
    comfort_with_conflict: int = Field(default=5, ge=0, le=10)

class AgentProfileCreate(BaseModel):
    """Request model for creating an agent."""
    
    name: str = Field(..., min_length=1, max_length=100)
    role: str = Field(..., min_length=1, max_length=100)
    title: Optional[str] = Field(None, max_length=100)
    backstory_summary: str = Field(..., min_length=50, max_length=1000)
    years_experience: Optional[int] = Field(None, ge=0, le=50)
    
    skills: SkillSet = Field(default_factory=SkillSet)
    personality_markers: PersonalityMarkers = Field(default_factory=PersonalityMarkers)
    social_markers: SocialMarkers = Field(default_factory=SocialMarkers)
    communication_style: CommunicationStyle = Field(default_factory=CommunicationStyle)
    
    knowledge_domains: List[str] = Field(default_factory=list)
    knowledge_gaps: List[str] = Field(default_factory=list)

class AgentProfile(AgentProfileCreate):
    """Full agent profile with ID and timestamps."""
    
    agent_id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
```

#### D1.2: Agent Repository

```python
# src/agents/repository.py

from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime

from src.agents.models import AgentProfile, AgentProfileCreate
from src.infrastructure.database import AgentProfileDB

class AgentRepository:
    """Database operations for agents."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, profile: AgentProfileCreate) -> AgentProfile:
        """Create a new agent."""
        db_agent = AgentProfileDB(
            name=profile.name,
            role=profile.role,
            title=profile.title,
            backstory_summary=profile.backstory_summary,
            years_experience=profile.years_experience,
            skills=profile.skills.model_dump(),
            personality_markers=profile.personality_markers.model_dump(),
            social_markers=profile.social_markers.model_dump(),
            communication_style=profile.communication_style.model_dump(),
            knowledge_domains=profile.knowledge_domains,
            knowledge_gaps=profile.knowledge_gaps,
        )
        
        self.session.add(db_agent)
        await self.session.commit()
        await self.session.refresh(db_agent)
        
        return self._to_model(db_agent)
    
    async def get(self, agent_id: UUID) -> Optional[AgentProfile]:
        """Get agent by ID."""
        result = await self.session.execute(
            select(AgentProfileDB)
            .where(AgentProfileDB.agent_id == agent_id)
            .where(AgentProfileDB.deleted_at.is_(None))
        )
        db_agent = result.scalar_one_or_none()
        
        if db_agent is None:
            return None
        
        return self._to_model(db_agent)
    
    async def list(
        self, 
        skip: int = 0, 
        limit: int = 100,
        role: Optional[str] = None
    ) -> List[AgentProfile]:
        """List agents with optional filtering."""
        query = select(AgentProfileDB).where(AgentProfileDB.deleted_at.is_(None))
        
        if role:
            query = query.where(AgentProfileDB.role.ilike(f"%{role}%"))
        
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        
        return [self._to_model(db_agent) for db_agent in result.scalars()]
    
    async def update(
        self, 
        agent_id: UUID, 
        updates: dict
    ) -> Optional[AgentProfile]:
        """Update agent profile."""
        updates["updated_at"] = datetime.utcnow()
        
        await self.session.execute(
            update(AgentProfileDB)
            .where(AgentProfileDB.agent_id == agent_id)
            .where(AgentProfileDB.deleted_at.is_(None))
            .values(**updates)
        )
        await self.session.commit()
        
        return await self.get(agent_id)
    
    async def delete(self, agent_id: UUID) -> bool:
        """Soft delete agent."""
        result = await self.session.execute(
            update(AgentProfileDB)
            .where(AgentProfileDB.agent_id == agent_id)
            .where(AgentProfileDB.deleted_at.is_(None))
            .values(deleted_at=datetime.utcnow())
        )
        await self.session.commit()
        
        return result.rowcount > 0
    
    def _to_model(self, db_agent: AgentProfileDB) -> AgentProfile:
        """Convert DB model to Pydantic model."""
        return AgentProfile(
            agent_id=db_agent.agent_id,
            name=db_agent.name,
            role=db_agent.role,
            title=db_agent.title,
            backstory_summary=db_agent.backstory_summary,
            years_experience=db_agent.years_experience,
            skills=SkillSet(**db_agent.skills),
            personality_markers=PersonalityMarkers(**db_agent.personality_markers),
            social_markers=SocialMarkers(**db_agent.social_markers),
            communication_style=CommunicationStyle(**db_agent.communication_style),
            knowledge_domains=db_agent.knowledge_domains,
            knowledge_gaps=db_agent.knowledge_gaps,
            created_at=db_agent.created_at,
            updated_at=db_agent.updated_at,
        )
```

#### D1.3: Agent API Routes

```python
# src/api/routes/agents.py

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from uuid import UUID

from src.agents.models import AgentProfile, AgentProfileCreate
from src.agents.repository import AgentRepository
from src.api.dependencies import get_agent_repository

router = APIRouter(prefix="/v1/agents", tags=["agents"])

@router.post("", response_model=AgentProfile, status_code=status.HTTP_201_CREATED)
async def create_agent(
    profile: AgentProfileCreate,
    repo: AgentRepository = Depends(get_agent_repository)
):
    """Create a new agent."""
    return await repo.create(profile)

@router.get("/{agent_id}", response_model=AgentProfile)
async def get_agent(
    agent_id: UUID,
    repo: AgentRepository = Depends(get_agent_repository)
):
    """Get agent by ID."""
    agent = await repo.get(agent_id)
    if agent is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found"
        )
    return agent

@router.get("", response_model=List[AgentProfile])
async def list_agents(
    skip: int = 0,
    limit: int = 100,
    role: Optional[str] = None,
    repo: AgentRepository = Depends(get_agent_repository)
):
    """List agents with optional filtering."""
    return await repo.list(skip=skip, limit=limit, role=role)

@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(
    agent_id: UUID,
    repo: AgentRepository = Depends(get_agent_repository)
):
    """Delete agent (soft delete)."""
    deleted = await repo.delete(agent_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found"
        )
```

#### D1.4: Profile Formatter for Prompts

```python
# src/agents/formatter.py

from src.agents.models import AgentProfile

class ProfileFormatter:
    """Format agent profiles for LLM prompts."""
    
    @staticmethod
    def format_identity_minimal(profile: AgentProfile) -> str:
        """Minimal identity for REFLEX tier."""
        return f"You are {profile.name}, a {profile.role}."
    
    @staticmethod
    def format_identity_brief(profile: AgentProfile) -> str:
        """Brief identity for REACTIVE tier."""
        top_skills = profile.skills.get_top_skills(3)
        skills_str = ", ".join([s[0] for s in top_skills])
        
        return f"""You are {profile.name}, a {profile.role}.
Key skills: {skills_str}"""
    
    @staticmethod
    def format_identity_full(profile: AgentProfile) -> str:
        """Full identity for DELIBERATE+ tiers."""
        top_skills = profile.skills.get_top_skills(5)
        skills_str = "\n".join([f"- {s[0]}: {s[1]}/10" for s in top_skills])
        
        return f"""IDENTITY:
You are {profile.name}, a {profile.role}.
{profile.backstory_summary}

SKILLS & EXPERTISE:
{skills_str}

COMMUNICATION STYLE:
- Vocabulary: {profile.communication_style.vocabulary_level}
- Formality: {profile.communication_style.formality}
- Structure: {profile.communication_style.sentence_structure}"""
    
    @staticmethod
    def format_social_context(profile: AgentProfile) -> str:
        """Format social traits for context."""
        sm = profile.social_markers
        
        traits = []
        if sm.confidence >= 7:
            traits.append("You express your views confidently")
        elif sm.confidence <= 3:
            traits.append("You tend to hedge your opinions")
        
        if sm.deference >= 7:
            traits.append("You readily defer to others' expertise")
        elif sm.deference <= 3:
            traits.append("You stand firm on your positions")
        
        if sm.curiosity >= 7:
            traits.append("You ask probing questions")
        
        if sm.facilitation_instinct >= 7:
            traits.append("You help draw out others' perspectives")
        
        return "\n".join([f"- {t}" for t in traits])
```

### 4.4 Test Criteria

| Test | Expected Result |
|------|-----------------|
| Create agent with valid profile | Returns 201, agent created |
| Create agent with invalid skills (>10) | Returns 422, validation error |
| Get existing agent | Returns agent profile |
| Get non-existent agent | Returns 404 |
| List agents | Returns array of profiles |
| Delete agent | Returns 204, agent soft deleted |
| Get deleted agent | Returns 404 |
| Skills relevance scoring | Correct relevance for keywords |
| Profile formatting | Correct output for each tier |

### 4.5 Definition of Done

- [ ] All agent CRUD endpoints working
- [ ] Skill validation (0-10 range) enforced
- [ ] Personality markers validated
- [ ] Social markers validated
- [ ] Profile formatter for all tiers
- [ ] 10+ test agents created successfully
- [ ] Unit tests at 80%+ coverage
- [ ] API documentation auto-generated

---

## 5. Phase 2: Model Infrastructure

### 5.1 Overview

| Attribute | Value |
|-----------|-------|
| **Duration** | 8 days |
| **Goal** | Self-hosted LLM serving with tiered routing |
| **Team** | 1-2 developers |
| **Dependencies** | Phase 0 |

### 5.2 Objectives

1. vLLM deployment for 3 model tiers
2. Model router with tier selection
3. Budget tracking and throttling
4. Fallback mechanisms
5. Latency monitoring

### 5.3 Deliverables

#### D2.1: vLLM Docker Configuration

```yaml
# docker/docker-compose.models.yml
version: '3.8'

services:
  vllm-small:
    image: vllm/vllm-openai:latest
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES=0
      - VLLM_ATTENTION_BACKEND=FLASH_ATTN
    command: >
      --model Qwen/Qwen2.5-3B-Instruct
      --dtype float16
      --max-model-len 2048
      --gpu-memory-utilization 0.90
      --max-num-batched-tokens 4096
      --max-num-seqs 32
      --enable-prefix-caching
      --port 8001
    ports:
      - "8001:8001"
    volumes:
      - model_cache:/root/.cache/huggingface
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              device_ids: ['0']
              capabilities: [gpu]
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  vllm-medium:
    image: vllm/vllm-openai:latest
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES=1
      - VLLM_ATTENTION_BACKEND=FLASH_ATTN
    command: >
      --model Qwen/Qwen2.5-7B-Instruct
      --dtype float16
      --max-model-len 4096
      --gpu-memory-utilization 0.90
      --max-num-batched-tokens 8192
      --max-num-seqs 24
      --enable-prefix-caching
      --port 8002
    ports:
      - "8002:8002"
    volumes:
      - model_cache:/root/.cache/huggingface
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              device_ids: ['1']
              capabilities: [gpu]
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8002/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  vllm-large:
    image: vllm/vllm-openai:latest
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES=2
      - VLLM_ATTENTION_BACKEND=FLASH_ATTN
    command: >
      --model Qwen/Qwen2.5-14B-Instruct
      --dtype float16
      --max-model-len 8192
      --gpu-memory-utilization 0.90
      --max-num-batched-tokens 16384
      --max-num-seqs 16
      --enable-prefix-caching
      --port 8003
    ports:
      - "8003:8003"
    volumes:
      - model_cache:/root/.cache/huggingface
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              device_ids: ['2']
              capabilities: [gpu]
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8003/health"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  model_cache:
```

#### D2.2: Model Client

```python
# src/infrastructure/model_client.py

from dataclasses import dataclass
from typing import Optional
from enum import Enum
import httpx
import time
import asyncio

class ModelTier(Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"

@dataclass
class ModelConfig:
    tier: ModelTier
    url: str
    model_name: str
    max_tokens: int
    typical_latency_ms: int
    cost_per_1k_tokens: float

@dataclass
class InferenceRequest:
    prompt: str
    max_tokens: int
    temperature: float = 0.7
    stop: Optional[list] = None

@dataclass
class InferenceResponse:
    text: str
    model_used: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    latency_ms: float

class ModelClient:
    """Client for vLLM inference endpoints."""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def generate(self, request: InferenceRequest) -> InferenceResponse:
        """Generate completion from model."""
        start = time.time()
        
        payload = {
            "model": self.config.model_name,
            "prompt": request.prompt,
            "max_tokens": min(request.max_tokens, self.config.max_tokens),
            "temperature": request.temperature,
            "stop": request.stop or [],
        }
        
        response = await self.client.post(
            f"{self.config.url}/v1/completions",
            json=payload
        )
        response.raise_for_status()
        
        result = response.json()
        latency_ms = (time.time() - start) * 1000
        
        return InferenceResponse(
            text=result["choices"][0]["text"],
            model_used=self.config.model_name,
            prompt_tokens=result["usage"]["prompt_tokens"],
            completion_tokens=result["usage"]["completion_tokens"],
            total_tokens=result["usage"]["total_tokens"],
            latency_ms=latency_ms
        )
    
    async def health_check(self) -> bool:
        """Check if model endpoint is healthy."""
        try:
            response = await self.client.get(f"{self.config.url}/health")
            return response.status_code == 200
        except Exception:
            return False
    
    async def close(self):
        await self.client.aclose()
```

#### D2.3: Model Router

```python
# src/infrastructure/model_router.py

from typing import Dict, Optional
from enum import Enum
import asyncio
import logging

from src.infrastructure.model_client import (
    ModelClient, ModelConfig, ModelTier, 
    InferenceRequest, InferenceResponse
)
from src.infrastructure.budget_manager import TokenBudgetManager

logger = logging.getLogger(__name__)

class CognitiveTier(Enum):
    REFLEX = 0
    REACTIVE = 1
    DELIBERATE = 2
    ANALYTICAL = 3
    COMPREHENSIVE = 4

# Mapping from cognitive tier to model tier
COGNITIVE_TO_MODEL = {
    CognitiveTier.REFLEX: ModelTier.SMALL,
    CognitiveTier.REACTIVE: ModelTier.MEDIUM,
    CognitiveTier.DELIBERATE: ModelTier.LARGE,
    CognitiveTier.ANALYTICAL: ModelTier.LARGE,
    CognitiveTier.COMPREHENSIVE: ModelTier.LARGE,
}

# Tier configurations
TIER_CONFIGS = {
    CognitiveTier.REFLEX: {"max_tokens": 150, "timeout_ms": 500},
    CognitiveTier.REACTIVE: {"max_tokens": 400, "timeout_ms": 1000},
    CognitiveTier.DELIBERATE: {"max_tokens": 1200, "timeout_ms": 3000},
    CognitiveTier.ANALYTICAL: {"max_tokens": 2500, "timeout_ms": 7000},
    CognitiveTier.COMPREHENSIVE: {"max_tokens": 4000, "timeout_ms": 12000},
}

class ModelRouter:
    """Routes inference requests to appropriate model tier."""
    
    def __init__(
        self,
        clients: Dict[ModelTier, ModelClient],
        budget_manager: TokenBudgetManager
    ):
        self.clients = clients
        self.budget_manager = budget_manager
        self._health_status: Dict[ModelTier, bool] = {
            tier: True for tier in ModelTier
        }
    
    async def route(
        self,
        cognitive_tier: CognitiveTier,
        request: InferenceRequest,
        agent_id: str
    ) -> InferenceResponse:
        """Route request to appropriate model."""
        
        # Determine target model tier
        model_tier = COGNITIVE_TO_MODEL[cognitive_tier]
        tier_config = TIER_CONFIGS[cognitive_tier]
        
        # Check budget and potentially downgrade
        if self.budget_manager.should_throttle(model_tier):
            downgrade = self.budget_manager.recommend_downgrade(model_tier)
            if downgrade:
                logger.info(f"Budget throttle: {model_tier} -> {downgrade}")
                model_tier = downgrade
        
        # Check health and potentially use fallback
        if not self._health_status[model_tier]:
            fallback = self._get_fallback(model_tier)
            if fallback:
                logger.info(f"Health fallback: {model_tier} -> {fallback}")
                model_tier = fallback
        
        # Get client and make request
        client = self.clients[model_tier]
        
        # Enforce max tokens for tier
        request.max_tokens = min(request.max_tokens, tier_config["max_tokens"])
        
        try:
            timeout = tier_config["timeout_ms"] / 1000
            response = await asyncio.wait_for(
                client.generate(request),
                timeout=timeout
            )
            
            # Record usage
            self.budget_manager.record_usage(
                model_tier,
                response.total_tokens,
                agent_id
            )
            
            return response
            
        except asyncio.TimeoutError:
            logger.warning(f"Timeout on {model_tier}, trying fallback")
            return await self._handle_timeout(cognitive_tier, request, agent_id)
        
        except Exception as e:
            logger.error(f"Error on {model_tier}: {e}")
            self._health_status[model_tier] = False
            return await self._handle_error(cognitive_tier, request, agent_id, e)
    
    def _get_fallback(self, tier: ModelTier) -> Optional[ModelTier]:
        """Get fallback tier."""
        fallbacks = {
            ModelTier.LARGE: ModelTier.MEDIUM,
            ModelTier.MEDIUM: ModelTier.SMALL,
            ModelTier.SMALL: None,
        }
        
        fallback = fallbacks[tier]
        if fallback and self._health_status[fallback]:
            return fallback
        return None
    
    async def _handle_timeout(
        self,
        cognitive_tier: CognitiveTier,
        request: InferenceRequest,
        agent_id: str
    ) -> InferenceResponse:
        """Handle timeout by trying fallback."""
        model_tier = COGNITIVE_TO_MODEL[cognitive_tier]
        fallback = self._get_fallback(model_tier)
        
        if fallback:
            client = self.clients[fallback]
            response = await client.generate(request)
            self.budget_manager.record_usage(fallback, response.total_tokens, agent_id)
            return response
        
        # No fallback available - return error response
        raise RuntimeError(f"No available model for {cognitive_tier}")
    
    async def _handle_error(
        self,
        cognitive_tier: CognitiveTier,
        request: InferenceRequest,
        agent_id: str,
        error: Exception
    ) -> InferenceResponse:
        """Handle error by trying fallback."""
        return await self._handle_timeout(cognitive_tier, request, agent_id)
    
    async def check_health(self):
        """Update health status for all models."""
        for tier, client in self.clients.items():
            self._health_status[tier] = await client.health_check()
    
    def get_status(self) -> Dict:
        """Get router status."""
        return {
            "health": {t.value: h for t, h in self._health_status.items()},
            "budget": self.budget_manager.get_status()
        }
```

#### D2.4: Budget Manager

```python
# src/infrastructure/budget_manager.py

from dataclasses import dataclass, field
from typing import Dict, Optional
from enum import Enum
from datetime import datetime, timedelta
import threading

from src.infrastructure.model_client import ModelTier

# Cost estimates based on GPU costs / throughput
COST_PER_1K_TOKENS = {
    ModelTier.SMALL: 0.0002,   # T4: ~$0.40/hr, ~500 tok/s
    ModelTier.MEDIUM: 0.0012,  # A10G: ~$1.25/hr, ~300 tok/s
    ModelTier.LARGE: 0.0049,   # A100: ~$3.50/hr, ~200 tok/s
}

# Budget allocation by tier
BUDGET_ALLOCATION = {
    ModelTier.SMALL: 0.10,   # 10%
    ModelTier.MEDIUM: 0.25,  # 25%
    ModelTier.LARGE: 0.50,   # 50%
    # 15% reserved for infrastructure
}

@dataclass
class TokenBudgetManager:
    """Manages token budget across model tiers."""
    
    hourly_budget_usd: float = 15.0
    
    # Tracking
    _hour_start: datetime = field(default_factory=datetime.utcnow)
    _tokens_by_tier: Dict[ModelTier, int] = field(
        default_factory=lambda: {t: 0 for t in ModelTier}
    )
    _tokens_by_agent: Dict[str, int] = field(default_factory=dict)
    _lock: threading.Lock = field(default_factory=threading.Lock)
    
    def record_usage(self, tier: ModelTier, tokens: int, agent_id: str):
        """Record token usage."""
        with self._lock:
            self._maybe_reset_hour()
            self._tokens_by_tier[tier] += tokens
            self._tokens_by_agent[agent_id] = \
                self._tokens_by_agent.get(agent_id, 0) + tokens
    
    def should_throttle(self, tier: ModelTier) -> bool:
        """Check if tier should be throttled."""
        with self._lock:
            self._maybe_reset_hour()
            utilization = self._get_tier_utilization(tier)
            
            thresholds = {
                ModelTier.SMALL: 0.95,   # Rarely throttle REFLEX
                ModelTier.MEDIUM: 0.85,
                ModelTier.LARGE: 0.75,   # Throttle earlier for expensive tier
            }
            
            return utilization > thresholds[tier]
    
    def recommend_downgrade(self, tier: ModelTier) -> Optional[ModelTier]:
        """Recommend a cheaper tier if budget is tight."""
        downgrades = {
            ModelTier.LARGE: ModelTier.MEDIUM,
            ModelTier.MEDIUM: ModelTier.SMALL,
            ModelTier.SMALL: None,
        }
        
        downgrade = downgrades[tier]
        if downgrade and not self.should_throttle(downgrade):
            return downgrade
        return None
    
    def get_status(self) -> Dict:
        """Get current budget status."""
        with self._lock:
            self._maybe_reset_hour()
            
            tier_status = {}
            for tier in ModelTier:
                tokens = self._tokens_by_tier[tier]
                cost = tokens * COST_PER_1K_TOKENS[tier] / 1000
                budget = self.hourly_budget_usd * BUDGET_ALLOCATION[tier]
                utilization = cost / budget if budget > 0 else 0
                
                tier_status[tier.value] = {
                    "tokens": tokens,
                    "cost_usd": round(cost, 4),
                    "budget_usd": round(budget, 2),
                    "utilization": round(utilization, 3),
                    "throttled": utilization > 0.8
                }
            
            total_cost = sum(s["cost_usd"] for s in tier_status.values())
            
            return {
                "hour_start": self._hour_start.isoformat(),
                "total_cost_usd": round(total_cost, 4),
                "hourly_budget_usd": self.hourly_budget_usd,
                "overall_utilization": round(total_cost / self.hourly_budget_usd, 3),
                "by_tier": tier_status
            }
    
    def _get_tier_utilization(self, tier: ModelTier) -> float:
        """Get utilization for a tier."""
        tokens = self._tokens_by_tier[tier]
        cost = tokens * COST_PER_1K_TOKENS[tier] / 1000
        budget = self.hourly_budget_usd * BUDGET_ALLOCATION[tier]
        return cost / budget if budget > 0 else 0
    
    def _maybe_reset_hour(self):
        """Reset counters if hour has passed."""
        now = datetime.utcnow()
        if now - self._hour_start > timedelta(hours=1):
            self._hour_start = now
            self._tokens_by_tier = {t: 0 for t in ModelTier}
            self._tokens_by_agent = {}
```

#### D2.5: Metrics Collection

```python
# src/infrastructure/metrics.py

from prometheus_client import Counter, Histogram, Gauge

# Model metrics
model_requests = Counter(
    'cae_model_requests_total',
    'Total model requests',
    ['tier', 'status']
)

model_tokens = Counter(
    'cae_model_tokens_total',
    'Total tokens consumed',
    ['tier', 'type']  # type: prompt, completion
)

model_latency = Histogram(
    'cae_model_latency_seconds',
    'Model inference latency',
    ['tier'],
    buckets=[0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0]
)

# Budget metrics
budget_utilization = Gauge(
    'cae_budget_utilization',
    'Budget utilization (0-1)',
    ['tier']
)

hourly_cost = Gauge(
    'cae_hourly_cost_usd',
    'Estimated cost this hour'
)

throttle_events = Counter(
    'cae_throttle_events_total',
    'Throttle events',
    ['tier']
)
```

### 5.4 Test Criteria

| Test | Expected Result |
|------|-----------------|
| vLLM health check | All 3 endpoints respond |
| Small model inference | <200ms latency, correct output |
| Medium model inference | <500ms latency, correct output |
| Large model inference | <2s latency, correct output |
| Budget tracking | Tokens counted correctly |
| Throttling trigger | Throttle at 80%+ utilization |
| Tier downgrade | Large → Medium when throttled |
| Fallback on error | Routes to next available tier |
| Health monitoring | Detects unhealthy endpoint |

### 5.5 Definition of Done

- [ ] All 3 vLLM instances running
- [ ] Model router directing to correct tier
- [ ] Budget tracking per tier and agent
- [ ] Throttling working at thresholds
- [ ] Fallback on timeout/error
- [ ] Health checks detecting issues
- [ ] Prometheus metrics exposed
- [ ] <$15/hour verified in testing
- [ ] Unit tests at 80%+ coverage

---

## 6. Phase 3: Cognitive Tiers

### 6.1 Overview

| Attribute | Value |
|-----------|-------|
| **Duration** | 7 days |
| **Goal** | Tiered cognitive processing with parallel execution |
| **Team** | 1-2 developers |
| **Dependencies** | Phase 1, Phase 2 |

### 6.2 Objectives

1. Cognitive tier definitions and config
2. Tier-appropriate prompt building
3. Parallel processing for urgent stimuli
4. Cognitive dispatcher logic
5. Response quality by tier

### 6.3 Deliverables

#### D3.1: Cognitive Tier Configuration

```python
# src/cognitive/tiers.py

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

class CognitiveTier(Enum):
    REFLEX = 0
    REACTIVE = 1
    DELIBERATE = 2
    ANALYTICAL = 3
    COMPREHENSIVE = 4

@dataclass
class TierConfig:
    """Configuration for a cognitive tier."""
    
    tier: CognitiveTier
    max_tokens: int
    target_latency_ms: int
    memory_access: str  # cached, recent, indexed, full_search
    context_depth: str  # minimal, shallow, standard, deep, full
    can_interrupt: bool
    runs_parallel: bool
    
    # Prompt constraints
    max_context_tokens: int
    response_format: str  # brief, moderate, thorough

TIER_CONFIGS = {
    CognitiveTier.REFLEX: TierConfig(
        tier=CognitiveTier.REFLEX,
        max_tokens=150,
        target_latency_ms=200,
        memory_access="cached",
        context_depth="minimal",
        can_interrupt=False,
        runs_parallel=True,
        max_context_tokens=100,
        response_format="brief"
    ),
    CognitiveTier.REACTIVE: TierConfig(
        tier=CognitiveTier.REACTIVE,
        max_tokens=400,
        target_latency_ms=500,
        memory_access="recent",
        context_depth="shallow",
        can_interrupt=True,
        runs_parallel=True,
        max_context_tokens=300,
        response_format="brief"
    ),
    CognitiveTier.DELIBERATE: TierConfig(
        tier=CognitiveTier.DELIBERATE,
        max_tokens=1200,
        target_latency_ms=2000,
        memory_access="indexed",
        context_depth="standard",
        can_interrupt=True,
        runs_parallel=False,
        max_context_tokens=600,
        response_format="moderate"
    ),
    CognitiveTier.ANALYTICAL: TierConfig(
        tier=CognitiveTier.ANALYTICAL,
        max_tokens=2500,
        target_latency_ms=5000,
        memory_access="full_search",
        context_depth="deep",
        can_interrupt=True,
        runs_parallel=False,
        max_context_tokens=1000,
        response_format="thorough"
    ),
    CognitiveTier.COMPREHENSIVE: TierConfig(
        tier=CognitiveTier.COMPREHENSIVE,
        max_tokens=4000,
        target_latency_ms=10000,
        memory_access="full_search",
        context_depth="full",
        can_interrupt=True,
        runs_parallel=False,
        max_context_tokens=1500,
        response_format="thorough"
    ),
}
```

#### D3.2: Tiered Prompt Builder

```python
# src/cognitive/prompts.py

from src.agents.models import AgentProfile
from src.agents.formatter import ProfileFormatter
from src.cognitive.tiers import CognitiveTier, TIER_CONFIGS

class TieredPromptBuilder:
    """Builds prompts appropriate for each cognitive tier."""
    
    def build(
        self,
        tier: CognitiveTier,
        agent: AgentProfile,
        stimulus: str,
        purpose: str,
        context: dict = None
    ) -> str:
        """Build prompt for specified tier."""
        
        config = TIER_CONFIGS[tier]
        
        if tier == CognitiveTier.REFLEX:
            return self._build_reflex(agent, stimulus)
        elif tier == CognitiveTier.REACTIVE:
            return self._build_reactive(agent, stimulus, purpose, context)
        elif tier == CognitiveTier.DELIBERATE:
            return self._build_deliberate(agent, stimulus, purpose, context)
        elif tier == CognitiveTier.ANALYTICAL:
            return self._build_analytical(agent, stimulus, purpose, context)
        else:
            return self._build_comprehensive(agent, stimulus, purpose, context)
    
    def _build_reflex(self, agent: AgentProfile, stimulus: str) -> str:
        """Minimal context, maximum speed."""
        identity = ProfileFormatter.format_identity_minimal(agent)
        
        return f"""{identity}

STIMULUS: {stimulus}

IMMEDIATE REACTION (one brief thought):"""
    
    def _build_reactive(
        self,
        agent: AgentProfile,
        stimulus: str,
        purpose: str,
        context: dict
    ) -> str:
        """Quick but slightly more considered."""
        identity = ProfileFormatter.format_identity_brief(agent)
        
        recent_context = ""
        if context and context.get("recent_turns"):
            recent_context = f"\nRECENT CONTEXT:\n{context['recent_turns']}"
        
        return f"""{identity}{recent_context}

SITUATION: {stimulus}

PURPOSE: {purpose}

Your quick assessment (2-3 sentences):"""
    
    def _build_deliberate(
        self,
        agent: AgentProfile,
        stimulus: str,
        purpose: str,
        context: dict
    ) -> str:
        """Full considered response."""
        identity = ProfileFormatter.format_identity_full(agent)
        social = ProfileFormatter.format_social_context(agent)
        
        memory_context = ""
        if context and context.get("relevant_memory"):
            memory_context = f"\nRELEVANT MEMORY:\n{context['relevant_memory']}"
        
        prior_thoughts = ""
        if context and context.get("prior_thoughts"):
            prior_thoughts = f"\nYOUR THINKING SO FAR:\n{context['prior_thoughts']}"
        
        return f"""{identity}

YOUR SOCIAL STYLE:
{social}
{memory_context}{prior_thoughts}

SITUATION:
{stimulus}

PURPOSE: {purpose}

Provide your considered thoughts:"""
    
    def _build_analytical(
        self,
        agent: AgentProfile,
        stimulus: str,
        purpose: str,
        context: dict
    ) -> str:
        """Deep analysis with full context."""
        identity = ProfileFormatter.format_identity_full(agent)
        
        # Full context sections
        sections = [identity]
        
        if context:
            if context.get("relevant_memory"):
                sections.append(f"RELEVANT EXPERIENCE:\n{context['relevant_memory']}")
            if context.get("patterns"):
                sections.append(f"PATTERNS YOU'VE LEARNED:\n{context['patterns']}")
            if context.get("relationships"):
                sections.append(f"RELATIONSHIP CONTEXT:\n{context['relationships']}")
            if context.get("prior_thoughts"):
                sections.append(f"YOUR THINKING PROCESS:\n{context['prior_thoughts']}")
        
        sections.append(f"SITUATION:\n{stimulus}")
        sections.append(f"PURPOSE: {purpose}")
        sections.append("""Provide thorough analysis:
1. What's really going on here?
2. What do I know that's relevant?
3. What patterns apply?
4. What are the risks/opportunities?
5. What's my considered position?""")
        
        return "\n\n".join(sections)
    
    def _build_comprehensive(
        self,
        agent: AgentProfile,
        stimulus: str,
        purpose: str,
        context: dict
    ) -> str:
        """Maximum context and depth."""
        # Similar to analytical but with even more context
        return self._build_analytical(agent, stimulus, purpose, context)
```

#### D3.3: Cognitive Processor

```python
# src/cognitive/processor.py

from dataclasses import dataclass
from typing import List, Optional, Dict
from datetime import datetime
import asyncio
import logging

from src.agents.models import AgentProfile
from src.cognitive.tiers import CognitiveTier, TIER_CONFIGS
from src.cognitive.prompts import TieredPromptBuilder
from src.infrastructure.model_router import ModelRouter, InferenceRequest

logger = logging.getLogger(__name__)

@dataclass
class Thought:
    """A single unit of cognition."""
    
    thought_id: str
    created_at: datetime
    tier: CognitiveTier
    content: str
    thought_type: str  # insight, concern, question, observation, plan, reaction
    trigger: str
    confidence: float
    completeness: float
    
    # Lifecycle
    externalized: bool = False
    still_relevant: bool = True

@dataclass 
class CognitiveResult:
    """Result of cognitive processing."""
    
    thoughts: List[Thought]
    primary_thought: Optional[Thought]
    processing_time_ms: float
    tiers_used: List[CognitiveTier]

class CognitiveProcessor:
    """Processes stimuli through cognitive tiers."""
    
    def __init__(
        self,
        agent: AgentProfile,
        model_router: ModelRouter
    ):
        self.agent = agent
        self.router = model_router
        self.prompt_builder = TieredPromptBuilder()
    
    async def process(
        self,
        stimulus: str,
        urgency: float,
        complexity: float,
        relevance: float,
        context: dict = None
    ) -> CognitiveResult:
        """Process stimulus with appropriate cognitive depth."""
        
        start_time = datetime.utcnow()
        
        # Plan cognitive strategy
        strategy = self._plan_strategy(urgency, complexity, relevance)
        
        # Execute strategy
        thoughts = []
        
        for process in strategy:
            if process["parallel"]:
                # Run parallel processes
                parallel_tasks = [
                    self._run_tier(
                        process["tier"],
                        stimulus,
                        process["purpose"],
                        context,
                        prior_thoughts=thoughts
                    )
                    for _ in range(process.get("count", 1))
                ]
                results = await asyncio.gather(*parallel_tasks)
                thoughts.extend(results)
            else:
                # Run sequential
                thought = await self._run_tier(
                    process["tier"],
                    stimulus,
                    process["purpose"],
                    context,
                    prior_thoughts=thoughts
                )
                thoughts.append(thought)
        
        # Determine primary thought
        primary = self._select_primary_thought(thoughts)
        
        elapsed = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        return CognitiveResult(
            thoughts=thoughts,
            primary_thought=primary,
            processing_time_ms=elapsed,
            tiers_used=list(set(t.tier for t in thoughts))
        )
    
    def _plan_strategy(
        self,
        urgency: float,
        complexity: float,
        relevance: float
    ) -> List[dict]:
        """Plan cognitive processing strategy."""
        
        processes = []
        
        # High urgency + relevant: REFLEX first, then parallel REACTIVE
        if urgency > 0.8 and relevance > 0.5:
            processes.append({
                "tier": CognitiveTier.REFLEX,
                "purpose": "immediate_response",
                "parallel": False
            })
            processes.append({
                "tier": CognitiveTier.REACTIVE,
                "purpose": "tactical_assessment",
                "parallel": True,
                "count": 2  # tactical + strategic
            })
            if complexity > 0.5:
                processes.append({
                    "tier": CognitiveTier.DELIBERATE,
                    "purpose": "deeper_analysis",
                    "parallel": False
                })
        
        # Low urgency + relevant: go straight to DELIBERATE
        elif urgency < 0.3 and relevance > 0.5:
            processes.append({
                "tier": CognitiveTier.DELIBERATE,
                "purpose": "considered_response",
                "parallel": False
            })
            if complexity > 0.7:
                processes.append({
                    "tier": CognitiveTier.ANALYTICAL,
                    "purpose": "thorough_analysis",
                    "parallel": False
                })
        
        # Low relevance: just note it
        elif relevance < 0.3:
            processes.append({
                "tier": CognitiveTier.REFLEX,
                "purpose": "note_for_context",
                "parallel": False
            })
        
        # Medium everything: proportional response
        else:
            tier = CognitiveTier.REACTIVE if complexity < 0.5 else CognitiveTier.DELIBERATE
            processes.append({
                "tier": tier,
                "purpose": "proportional_response",
                "parallel": False
            })
        
        return processes
    
    async def _run_tier(
        self,
        tier: CognitiveTier,
        stimulus: str,
        purpose: str,
        context: dict,
        prior_thoughts: List[Thought]
    ) -> Thought:
        """Run a single cognitive tier."""
        
        # Add prior thoughts to context
        if prior_thoughts and context is None:
            context = {}
        if prior_thoughts:
            context["prior_thoughts"] = "\n".join([
                f"- {t.content}" for t in prior_thoughts[-3:]
            ])
        
        # Build prompt
        prompt = self.prompt_builder.build(
            tier=tier,
            agent=self.agent,
            stimulus=stimulus,
            purpose=purpose,
            context=context
        )
        
        # Get tier config
        config = TIER_CONFIGS[tier]
        
        # Make inference request
        request = InferenceRequest(
            prompt=prompt,
            max_tokens=config.max_tokens,
            temperature=0.7
        )
        
        response = await self.router.route(
            cognitive_tier=tier,
            request=request,
            agent_id=str(self.agent.agent_id)
        )
        
        # Create thought
        return Thought(
            thought_id=self._generate_id(),
            created_at=datetime.utcnow(),
            tier=tier,
            content=response.text.strip(),
            thought_type=self._infer_thought_type(purpose, response.text),
            trigger=purpose,
            confidence=self._estimate_confidence(tier, response),
            completeness=self._estimate_completeness(tier, response)
        )
    
    def _select_primary_thought(self, thoughts: List[Thought]) -> Optional[Thought]:
        """Select the primary thought from results."""
        if not thoughts:
            return None
        
        # Prefer higher tier, higher confidence, higher completeness
        return max(
            thoughts,
            key=lambda t: (
                t.tier.value * 0.4 +
                t.confidence * 0.3 +
                t.completeness * 0.3
            )
        )
    
    def _infer_thought_type(self, purpose: str, content: str) -> str:
        """Infer thought type from purpose and content."""
        content_lower = content.lower()
        
        if "concern" in content_lower or "risk" in content_lower or "worry" in content_lower:
            return "concern"
        if "?" in content:
            return "question"
        if purpose == "immediate_response":
            return "reaction"
        if "should" in content_lower or "could" in content_lower:
            return "plan"
        
        return "insight"
    
    def _estimate_confidence(self, tier: CognitiveTier, response) -> float:
        """Estimate confidence based on tier and response."""
        # Higher tiers = more considered = higher base confidence
        base = {
            CognitiveTier.REFLEX: 0.5,
            CognitiveTier.REACTIVE: 0.6,
            CognitiveTier.DELIBERATE: 0.75,
            CognitiveTier.ANALYTICAL: 0.85,
            CognitiveTier.COMPREHENSIVE: 0.9
        }[tier]
        
        # Adjust based on response characteristics
        # (In practice, could parse hedging language, etc.)
        return base
    
    def _estimate_completeness(self, tier: CognitiveTier, response) -> float:
        """Estimate how complete the thought is."""
        # Based on whether response used available tokens
        config = TIER_CONFIGS[tier]
        utilization = response.completion_tokens / config.max_tokens
        
        # High utilization = probably complete
        # Low utilization might mean truncated OR concise
        if utilization > 0.8:
            return 0.9
        elif utilization > 0.5:
            return 0.7
        else:
            return 0.5
    
    def _generate_id(self) -> str:
        import uuid
        return str(uuid.uuid4())
```

### 6.4 Test Criteria

| Test | Expected Result |
|------|-----------------|
| High urgency stimulus | REFLEX executes first, parallel REACTIVE follows |
| Low urgency + high complexity | DELIBERATE + ANALYTICAL executed |
| Low relevance stimulus | Only REFLEX tier used |
| Tier latency targets | Each tier within target (p95) |
| Thought quality | Higher tiers produce more detailed thoughts |
| Prior thoughts in context | Later tiers reference earlier thoughts |
| Budget tracking | All tiers counted correctly |

### 6.5 Definition of Done

- [ ] All 5 cognitive tiers implemented
- [ ] Strategy planning based on urgency/complexity/relevance
- [ ] Parallel processing for urgent stimuli
- [ ] Tiered prompt building working
- [ ] Latency targets met (p95)
- [ ] Thought model with confidence/completeness
- [ ] Integration with model router
- [ ] Unit tests at 80%+ coverage

**MILESTONE M1: Agent Responds** ✓

---

## 7. Phase 4: Internal Mind

### 7.1 Overview

| Attribute | Value |
|-----------|-------|
| **Duration** | 7 days |
| **Goal** | Agents have internal thoughts that exist independently of speaking |
| **Team** | 1 developer |
| **Dependencies** | Phase 3 |

### 7.2 Objectives

1. Internal mind model
2. Thought streams and accumulation
3. Thought synthesis
4. Thought invalidation
5. Background processing

### 7.3 Deliverables

#### D4.1: Internal Mind Model

```python
# src/cognitive/mind.py

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
from collections import deque
import asyncio

from src.cognitive.processor import Thought

@dataclass
class ThoughtStream:
    """A stream of related thoughts building toward something."""
    
    stream_id: str
    topic: str
    thoughts: List[Thought] = field(default_factory=list)
    status: str = "active"  # active, paused, concluded, abandoned
    
    # Synthesis result
    synthesized_output: Optional[Thought] = None
    ready_to_externalize: bool = False
    
    def add_thought(self, thought: Thought):
        """Add thought to stream."""
        self.thoughts.append(thought)
        thought.related_thoughts = [t.thought_id for t in self.thoughts[:-1]]
    
    def get_recent(self, n: int = 3) -> List[Thought]:
        """Get most recent thoughts."""
        return self.thoughts[-n:]
    
    @property
    def avg_confidence(self) -> float:
        if not self.thoughts:
            return 0.0
        return sum(t.confidence for t in self.thoughts) / len(self.thoughts)

class InternalMind:
    """The agent's cognitive workspace where thoughts exist."""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        
        # Active thoughts not yet resolved
        self.active_thoughts: Dict[str, Thought] = {}
        
        # Thought streams (trains of thought by topic)
        self.streams: Dict[str, ThoughtStream] = {}
        
        # Held insights (things I know but haven't shared)
        self.held_insights: List[Thought] = []
        
        # Ready to share when appropriate
        self.ready_to_share: List[Thought] = []
        
        # Background tasks
        self.background_tasks: List[asyncio.Task] = []
    
    def add_thought(self, thought: Thought):
        """Add a new thought to the mind."""
        self.active_thoughts[thought.thought_id] = thought
        
        # Find or create related stream
        stream = self._find_or_create_stream(thought)
        stream.add_thought(thought)
        
        # Check if stream should be synthesized
        if self._should_synthesize(stream):
            # Queue synthesis (don't block)
            task = asyncio.create_task(self._synthesize_stream(stream))
            self.background_tasks.append(task)
    
    def hold_insight(self, thought: Thought):
        """
        Hold an insight internally - don't share it now.
        The thought still exists and affects internal state.
        """
        thought.externalized = False
        self.held_insights.append(thought)
    
    def prepare_to_share(self, thought: Thought):
        """Mark thought as ready to share when appropriate."""
        if thought not in self.ready_to_share:
            self.ready_to_share.append(thought)
    
    def get_best_contribution(self) -> Optional[Thought]:
        """Get the best thought to share right now."""
        if not self.ready_to_share:
            return None
        
        # Filter to still-relevant thoughts
        valid = [t for t in self.ready_to_share if t.still_relevant]
        if not valid:
            return None
        
        # Rank by relevance, completeness, confidence
        ranked = sorted(
            valid,
            key=lambda t: (t.completeness, t.confidence),
            reverse=True
        )
        
        return ranked[0]
    
    def mark_externalized(self, thought_id: str):
        """Mark thought as having been spoken."""
        if thought_id in self.active_thoughts:
            self.active_thoughts[thought_id].externalized = True
        
        # Remove from ready_to_share
        self.ready_to_share = [
            t for t in self.ready_to_share 
            if t.thought_id != thought_id
        ]
    
    def invalidate_thoughts_about(self, topic: str):
        """
        Mark thoughts about a topic as no longer relevant.
        Called when new information supersedes previous thinking.
        """
        for thought in self.active_thoughts.values():
            if self._thought_relates_to(thought, topic):
                thought.still_relevant = False
        
        # Also clear from ready_to_share
        self.ready_to_share = [
            t for t in self.ready_to_share
            if not self._thought_relates_to(t, topic)
        ]
    
    def get_thoughts_for_context(self, n: int = 5) -> List[Thought]:
        """Get recent thoughts for context in prompts."""
        recent = sorted(
            self.active_thoughts.values(),
            key=lambda t: t.created_at,
            reverse=True
        )[:n]
        return recent
    
    def get_stream_for_topic(self, topic: str) -> Optional[ThoughtStream]:
        """Find stream matching topic."""
        topic_lower = topic.lower()
        for stream_id, stream in self.streams.items():
            if topic_lower in stream.topic.lower():
                return stream
        return None
    
    def _find_or_create_stream(self, thought: Thought) -> ThoughtStream:
        """Find existing stream or create new one."""
        # Simple topic extraction from thought content
        topic = self._extract_topic(thought.content)
        
        # Look for existing stream
        for stream in self.streams.values():
            if self._topics_related(stream.topic, topic):
                return stream
        
        # Create new stream
        stream = ThoughtStream(
            stream_id=self._generate_id(),
            topic=topic
        )
        self.streams[stream.stream_id] = stream
        return stream
    
    def _should_synthesize(self, stream: ThoughtStream) -> bool:
        """Determine if stream should be synthesized."""
        if len(stream.thoughts) < 2:
            return False
        
        # Synthesize if 3+ thoughts, or 2+ thoughts spanning time
        thought_count = len(stream.thoughts)
        if thought_count >= 3:
            return True
        
        if thought_count >= 2:
            time_span = (
                stream.thoughts[-1].created_at - 
                stream.thoughts[0].created_at
            ).seconds
            if time_span > 30 and stream.avg_confidence > 0.6:
                return True
        
        return False
    
    async def _synthesize_stream(self, stream: ThoughtStream):
        """Synthesize thoughts in stream into unified contribution."""
        # This will be called via cognitive processor
        # For now, just mark as needing synthesis
        stream.status = "needs_synthesis"
    
    def _extract_topic(self, content: str) -> str:
        """Extract topic from thought content."""
        # Simple: use first few words
        words = content.split()[:5]
        return " ".join(words)
    
    def _topics_related(self, topic1: str, topic2: str) -> bool:
        """Check if topics are related."""
        words1 = set(topic1.lower().split())
        words2 = set(topic2.lower().split())
        overlap = words1 & words2
        return len(overlap) > 0
    
    def _thought_relates_to(self, thought: Thought, topic: str) -> bool:
        """Check if thought relates to topic."""
        return topic.lower() in thought.content.lower()
    
    def _generate_id(self) -> str:
        import uuid
        return str(uuid.uuid4())
    
    def get_state(self) -> dict:
        """Get current mind state."""
        return {
            "active_thoughts": len(self.active_thoughts),
            "streams": len(self.streams),
            "held_insights": len(self.held_insights),
            "ready_to_share": len(self.ready_to_share),
            "background_tasks": len([t for t in self.background_tasks if not t.done()])
        }
```

#### D4.2: Thought Accumulator

```python
# src/cognitive/accumulator.py

from typing import List, Optional
from datetime import datetime
import asyncio

from src.cognitive.mind import InternalMind, ThoughtStream
from src.cognitive.processor import Thought, CognitiveProcessor
from src.cognitive.tiers import CognitiveTier

class ThoughtAccumulator:
    """
    Accumulates thoughts from stimuli and manages synthesis.
    Enables "listening" behavior where thoughts build up before speaking.
    """
    
    def __init__(
        self,
        mind: InternalMind,
        processor: CognitiveProcessor
    ):
        self.mind = mind
        self.processor = processor
    
    async def process_observation(
        self,
        stimulus: str,
        relevance: float
    ) -> Thought:
        """
        Process an observation (e.g., someone speaking in a meeting).
        Creates small thought bubbles that accumulate.
        """
        # Low-effort observation thought
        result = await self.processor.process(
            stimulus=stimulus,
            urgency=0.2,  # Not urgent
            complexity=0.3,  # Simple observation
            relevance=relevance,
            context=None
        )
        
        if result.primary_thought:
            self.mind.add_thought(result.primary_thought)
        
        return result.primary_thought
    
    async def synthesize_stream(
        self,
        stream: ThoughtStream
    ) -> Optional[Thought]:
        """
        Synthesize accumulated thoughts into coherent contribution.
        Called when stream has enough thoughts.
        """
        if len(stream.thoughts) < 2:
            return None
        
        # Format thoughts for synthesis prompt
        thoughts_text = "\n".join([
            f"- {t.content} (confidence: {t.confidence:.1f})"
            for t in stream.thoughts
        ])
        
        synthesis_stimulus = f"""
I've been thinking about {stream.topic}.

My observations and thoughts:
{thoughts_text}

Synthesize these into ONE clear, coherent point.
"""
        
        result = await self.processor.process(
            stimulus=synthesis_stimulus,
            urgency=0.3,
            complexity=0.6,
            relevance=0.8,  # Synthesis is always relevant to me
            context={"prior_thoughts": thoughts_text}
        )
        
        if result.primary_thought:
            # Mark as synthesized
            result.primary_thought.thought_type = "synthesis"
            
            # Add to stream
            stream.synthesized_output = result.primary_thought
            stream.ready_to_externalize = True
            
            # Prepare to share if confidence is high
            if result.primary_thought.confidence > 0.6:
                self.mind.prepare_to_share(result.primary_thought)
            
            # Mark source thoughts as synthesized
            for thought in stream.thoughts:
                thought.still_relevant = False  # Superseded by synthesis
        
        return result.primary_thought
    
    async def check_streams_for_synthesis(self):
        """Check all streams and synthesize if ready."""
        for stream in self.mind.streams.values():
            if stream.status == "needs_synthesis":
                await self.synthesize_stream(stream)
                stream.status = "concluded"
    
    def get_pending_synthesis_count(self) -> int:
        """Count streams needing synthesis."""
        return sum(
            1 for s in self.mind.streams.values()
            if s.status == "needs_synthesis"
        )
```

#### D4.3: Background Processor

```python
# src/cognitive/background.py

import asyncio
from typing import Optional
from datetime import datetime, timedelta

from src.cognitive.mind import InternalMind
from src.cognitive.accumulator import ThoughtAccumulator
from src.cognitive.processor import CognitiveProcessor, Thought

class BackgroundProcessor:
    """
    Handles background cognitive tasks that run while agent is "listening".
    Enables deeper processing without blocking responses.
    """
    
    def __init__(
        self,
        mind: InternalMind,
        processor: CognitiveProcessor,
        accumulator: ThoughtAccumulator
    ):
        self.mind = mind
        self.processor = processor
        self.accumulator = accumulator
        
        self._running = False
        self._task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start background processing loop."""
        self._running = True
        self._task = asyncio.create_task(self._process_loop())
    
    async def stop(self):
        """Stop background processing."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
    
    async def _process_loop(self):
        """Main background processing loop."""
        while self._running:
            try:
                # Check for streams needing synthesis
                await self.accumulator.check_streams_for_synthesis()
                
                # Clean up old thoughts
                self._cleanup_old_thoughts()
                
                # Wait before next cycle
                await asyncio.sleep(1.0)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                # Log but don't crash
                import logging
                logging.error(f"Background processor error: {e}")
                await asyncio.sleep(5.0)
    
    def _cleanup_old_thoughts(self):
        """Remove thoughts older than threshold."""
        threshold = datetime.utcnow() - timedelta(minutes=30)
        
        # Remove from active thoughts
        to_remove = [
            tid for tid, thought in self.mind.active_thoughts.items()
            if thought.created_at < threshold and not thought.externalized
        ]
        for tid in to_remove:
            del self.mind.active_thoughts[tid]
        
        # Clean up concluded streams
        concluded = [
            sid for sid, stream in self.mind.streams.items()
            if stream.status == "concluded"
        ]
        for sid in concluded:
            del self.mind.streams[sid]
    
    async def queue_deep_analysis(
        self,
        stimulus: str,
        purpose: str,
        callback: callable = None
    ):
        """
        Queue a deep analysis task to run in background.
        Results can refine ongoing behavior.
        """
        async def _run_analysis():
            result = await self.processor.process(
                stimulus=stimulus,
                urgency=0.1,  # Not urgent
                complexity=0.9,  # Deep analysis
                relevance=0.7,
                context=None
            )
            
            if result.primary_thought:
                self.mind.add_thought(result.primary_thought)
                
                if callback:
                    await callback(result.primary_thought)
        
        task = asyncio.create_task(_run_analysis())
        self.mind.background_tasks.append(task)
```

### 7.4 Test Criteria

| Test | Expected Result |
|------|-----------------|
| Add thought to mind | Thought stored in active_thoughts |
| Thought stream creation | Related thoughts grouped |
| Stream synthesis trigger | Triggers at 3+ thoughts |
| Synthesis quality | Synthesized thought coherent |
| Thought invalidation | Old thoughts marked irrelevant |
| Ready to share queue | Only valid thoughts returned |
| Background cleanup | Old thoughts removed |
| Multiple streams | Different topics create different streams |

### 7.5 Definition of Done

- [ ] Internal mind model implemented
- [ ] Thought streams accumulate related thoughts
- [ ] Synthesis triggers at threshold
- [ ] Background processor running
- [ ] Thought invalidation working
- [ ] Ready-to-share queue managed
- [ ] Cleanup of old thoughts
- [ ] Unit tests at 80%+ coverage

**MILESTONE M2: Agent Thinks** ✓

---

## 8. Phase 5: Social Intelligence

### 8.1 Overview

| Attribute | Value |
|-----------|-------|
| **Duration** | 8 days |
| **Goal** | Agents decide when to speak based on social context |
| **Team** | 1-2 developers |
| **Dependencies** | Phase 4 |

### 8.2 Objectives

1. Social context model
2. Externalization intent classification
3. Self-awareness evaluation
4. Social awareness evaluation
5. Group size adaptation

### 8.3 Deliverables

#### D5.1: Social Context Model

```python
# src/social/context.py

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum

class GroupType(Enum):
    SOLO = "solo"
    PAIR = "pair"
    SMALL_TEAM = "small_team"
    MEETING = "meeting"
    LARGE_GROUP = "large_group"
    ARMY = "army"

@dataclass
class ParticipantInfo:
    """Information about another participant."""
    
    agent_id: str
    name: str
    role: str
    expertise_areas: List[str]
    
    # Observed state
    has_spoken: bool = False
    contribution_count: int = 0
    seems_engaged: bool = True
    apparent_position: Optional[str] = None  # On current topic

@dataclass
class SocialContext:
    """What the agent perceives about the current social situation."""
    
    # Group composition
    participants: List[ParticipantInfo] = field(default_factory=list)
    group_size: int = 1
    
    # My position
    my_role: str = "participant"  # facilitator, expert, participant, observer, leader, junior
    my_status_relative: str = "peer"  # senior, peer, junior, outsider
    
    # Current dynamics
    current_speaker: Optional[str] = None
    topic_under_discussion: str = ""
    discussion_phase: str = "exploring"  # opening, exploring, debating, deciding, closing
    
    # Expertise in room
    expertise_present: Dict[str, List[str]] = field(default_factory=dict)  # skill → agent_ids
    expertise_gaps: List[str] = field(default_factory=list)
    
    # Conversational state
    speaking_distribution: Dict[str, int] = field(default_factory=dict)  # agent_id → count
    energy_level: str = "engaged"  # heated, engaged, neutral, flagging
    consensus_level: str = "discussing"  # aligned, discussing, divided, conflicted
    
    @property
    def group_type(self) -> GroupType:
        """Classify group by size."""
        if self.group_size <= 1:
            return GroupType.SOLO
        elif self.group_size == 2:
            return GroupType.PAIR
        elif self.group_size <= 6:
            return GroupType.SMALL_TEAM
        elif self.group_size <= 20:
            return GroupType.MEETING
        elif self.group_size <= 100:
            return GroupType.LARGE_GROUP
        else:
            return GroupType.ARMY
    
    def get_participant(self, agent_id: str) -> Optional[ParticipantInfo]:
        """Get participant by ID."""
        for p in self.participants:
            if p.agent_id == agent_id:
                return p
        return None
    
    def update_speaker(self, agent_id: str):
        """Update current speaker and distribution."""
        self.current_speaker = agent_id
        self.speaking_distribution[agent_id] = \
            self.speaking_distribution.get(agent_id, 0) + 1
        
        participant = self.get_participant(agent_id)
        if participant:
            participant.has_spoken = True
            participant.contribution_count += 1
```

#### D5.2: Externalization Intent

```python
# src/social/intent.py

from dataclasses import dataclass
from enum import Enum
from typing import Optional

class ExternalizationIntent(Enum):
    """The agent's decision about whether to contribute."""
    
    MUST_RESPOND = "must_respond"       # Directly addressed
    SHOULD_CONTRIBUTE = "should"        # My expertise needed
    MAY_CONTRIBUTE = "may"              # I have value to add
    ACTIVE_LISTEN = "listen"            # Learning, not contributing
    PASSIVE_AWARENESS = "passive"       # Background noise

@dataclass
class ExternalizationDecision:
    """Full externalization decision with reasoning."""
    
    intent: ExternalizationIntent
    confidence: float
    reason: str
    
    # If speaking
    contribution_type: Optional[str] = None  # statement, question, facilitation
    timing: str = "now"  # now, wait_for_opening, when_asked
    
    # For debugging/learning
    factors: dict = None
```

#### D5.3: Social Intelligence Module

```python
# src/social/intelligence.py

from typing import Optional, List
from dataclasses import dataclass

from src.agents.models import AgentProfile
from src.social.context import SocialContext, GroupType, ParticipantInfo
from src.social.intent import ExternalizationIntent, ExternalizationDecision
from src.cognitive.mind import InternalMind

@dataclass
class Stimulus:
    """Input stimulus for evaluation."""
    
    content: str
    source_id: Optional[str] = None
    source_name: Optional[str] = None
    directed_at: Optional[List[str]] = None  # None = broadcast, list = specific agents
    topic: str = ""

class SocialIntelligence:
    """
    Evaluates social context to decide if/when to speak.
    This is what makes orchestration unnecessary.
    """
    
    def __init__(self, agent: AgentProfile, mind: InternalMind):
        self.agent = agent
        self.mind = mind
    
    def should_i_speak(
        self,
        stimulus: Stimulus,
        context: SocialContext
    ) -> ExternalizationDecision:
        """
        Core social intelligence decision.
        Evaluates multiple factors to decide whether to externalize.
        """
        
        factors = {}
        
        # 1. Am I directly addressed?
        if self._am_i_directly_addressed(stimulus):
            return ExternalizationDecision(
                intent=ExternalizationIntent.MUST_RESPOND,
                confidence=1.0,
                reason="directly_addressed",
                contribution_type="response",
                factors={"directly_addressed": True}
            )
        
        # 2. Calculate expertise relevance
        relevance = self._calculate_expertise_match(stimulus.topic)
        factors["expertise_relevance"] = relevance
        
        if relevance < 0.3:
            return ExternalizationDecision(
                intent=ExternalizationIntent.PASSIVE_AWARENESS,
                confidence=0.9,
                reason="not_my_area",
                factors=factors
            )
        
        # 3. Check if I should defer
        should_defer, defer_to = self._should_defer_to_expert(stimulus.topic, context)
        factors["should_defer"] = should_defer
        factors["defer_to"] = defer_to
        
        if should_defer:
            return ExternalizationDecision(
                intent=ExternalizationIntent.ACTIVE_LISTEN,
                confidence=0.7,
                reason=f"defer_to_expert:{defer_to}",
                factors=factors
            )
        
        # 4. Check conversational space
        has_space = self._is_there_conversational_space(context)
        factors["conversational_space"] = has_space
        
        if not has_space:
            return ExternalizationDecision(
                intent=ExternalizationIntent.ACTIVE_LISTEN,
                confidence=0.8,
                reason="no_space",
                timing="wait_for_opening",
                factors=factors
            )
        
        # 5. Check if I've said enough
        said_enough = self._have_i_said_enough(context)
        factors["said_enough"] = said_enough
        
        if said_enough:
            # Unless my input is critical
            has_critical = self._do_i_have_critical_input(stimulus)
            factors["has_critical_input"] = has_critical
            
            if not has_critical:
                return ExternalizationDecision(
                    intent=ExternalizationIntent.ACTIVE_LISTEN,
                    confidence=0.6,
                    reason="said_enough",
                    factors=factors
                )
        
        # 6. Check role appropriateness
        role_suggests = self._what_does_role_suggest(context)
        factors["role_suggests"] = role_suggests
        
        if role_suggests == "mostly_listen":
            return ExternalizationDecision(
                intent=ExternalizationIntent.ACTIVE_LISTEN,
                confidence=0.7,
                reason="role_is_observer",
                factors=factors
            )
        
        # 7. Adjust for group size
        contribution_threshold = self._get_contribution_threshold(context.group_type)
        factors["contribution_threshold"] = contribution_threshold
        
        if relevance < contribution_threshold:
            return ExternalizationDecision(
                intent=ExternalizationIntent.MAY_CONTRIBUTE,
                confidence=relevance,
                reason="below_threshold_for_group_size",
                timing="when_asked",
                factors=factors
            )
        
        # 8. Passed all checks - should contribute
        contribution_type = self._determine_contribution_type(stimulus, context)
        
        return ExternalizationDecision(
            intent=ExternalizationIntent.SHOULD_CONTRIBUTE if relevance > 0.6 
                   else ExternalizationIntent.MAY_CONTRIBUTE,
            confidence=relevance,
            contribution_type=contribution_type,
            reason="have_valuable_input",
            factors=factors
        )
    
    # ==========================================
    # SELF-AWARENESS METHODS
    # ==========================================
    
    def _am_i_directly_addressed(self, stimulus: Stimulus) -> bool:
        """Check if stimulus is directed at me."""
        if stimulus.directed_at is None:
            return False
        
        my_id = str(self.agent.agent_id)
        my_name = self.agent.name.lower()
        
        for target in stimulus.directed_at:
            if target == my_id or target.lower() == my_name:
                return True
        
        # Check content for name mention
        if my_name in stimulus.content.lower():
            return True
        
        return False
    
    def _calculate_expertise_match(self, topic: str) -> float:
        """How much expertise do I have on this topic?"""
        if not topic:
            return 0.5  # Unknown topic = medium relevance
        
        keywords = topic.lower().split()
        return self.agent.skills.get_relevance_score(keywords)
    
    def _have_i_said_enough(self, context: SocialContext) -> bool:
        """Check if I'm dominating the conversation."""
        my_id = str(self.agent.agent_id)
        my_contributions = context.speaking_distribution.get(my_id, 0)
        total_contributions = sum(context.speaking_distribution.values())
        
        if total_contributions == 0:
            return False
        
        my_share = my_contributions / total_contributions
        fair_share = 1.0 / max(context.group_size, 1)
        
        # Role adjustment
        role_multiplier = {
            "facilitator": 2.0,
            "leader": 1.5,
            "expert": 1.3,
            "participant": 1.0,
            "junior": 0.8,
            "observer": 0.3
        }.get(context.my_role, 1.0)
        
        expected_share = fair_share * role_multiplier
        
        return my_share > expected_share * 1.5
    
    def _do_i_have_critical_input(self, stimulus: Stimulus) -> bool:
        """Check if I have critical input that must be shared."""
        # Check if I have a high-confidence ready thought
        best = self.mind.get_best_contribution()
        if best and best.confidence > 0.8 and best.thought_type == "concern":
            return True
        return False
    
    # ==========================================
    # SOCIAL AWARENESS METHODS
    # ==========================================
    
    def _should_defer_to_expert(
        self,
        topic: str,
        context: SocialContext
    ) -> tuple[bool, Optional[str]]:
        """Check if someone more qualified is present."""
        my_expertise = self._calculate_expertise_match(topic)
        
        # Extract topic keywords
        keywords = topic.lower().split() if topic else []
        
        for participant in context.participants:
            if participant.agent_id == str(self.agent.agent_id):
                continue
            
            # Estimate their expertise
            their_expertise = self._estimate_participant_expertise(
                participant, keywords
            )
            
            # If they're significantly more qualified and haven't spoken
            if their_expertise > my_expertise + 0.2:
                if not participant.has_spoken:
                    return True, participant.name
        
        return False, None
    
    def _estimate_participant_expertise(
        self,
        participant: ParticipantInfo,
        keywords: List[str]
    ) -> float:
        """Estimate another participant's expertise."""
        if not participant.expertise_areas:
            return 0.5
        
        # Check overlap between their expertise and keywords
        expertise_lower = [e.lower() for e in participant.expertise_areas]
        
        matches = 0
        for keyword in keywords:
            for expertise in expertise_lower:
                if keyword in expertise or expertise in keyword:
                    matches += 1
                    break
        
        if not keywords:
            return 0.5
        
        return min(1.0, matches / len(keywords) + 0.3)  # Base + matches
    
    def _is_there_conversational_space(self, context: SocialContext) -> bool:
        """Check if there's room for me to speak."""
        # Someone is currently speaking
        if context.current_speaker and \
           context.current_speaker != str(self.agent.agent_id):
            return False
        
        # Closing phase - only critical input
        if context.discussion_phase == "closing":
            return False
        
        # Heated discussion - consider if helping or inflaming
        if context.energy_level == "heated":
            # Only speak if I can calm things
            sm = self.agent.social_markers
            return sm.comfort_with_conflict >= 6
        
        return True
    
    def _what_does_role_suggest(self, context: SocialContext) -> str:
        """What behavior does my role suggest?"""
        role_behaviors = {
            "facilitator": "enable_others",
            "expert": "contribute_in_domain",
            "participant": "contribute_when_relevant",
            "observer": "mostly_listen",
            "leader": "guide_and_decide",
            "junior": "learn_and_ask",
        }
        return role_behaviors.get(context.my_role, "assess_situation")
    
    def _get_contribution_threshold(self, group_type: GroupType) -> float:
        """Get threshold for contribution based on group size."""
        thresholds = {
            GroupType.SOLO: 0.0,      # Always contribute
            GroupType.PAIR: 0.3,      # Low threshold
            GroupType.SMALL_TEAM: 0.4,
            GroupType.MEETING: 0.5,
            GroupType.LARGE_GROUP: 0.7,
            GroupType.ARMY: 0.9,      # Only if critical
        }
        return thresholds[group_type]
    
    def _determine_contribution_type(
        self,
        stimulus: Stimulus,
        context: SocialContext
    ) -> str:
        """Determine what type of contribution to make."""
        sm = self.agent.social_markers
        
        # If I have high curiosity and there are gaps
        if sm.curiosity >= 7:
            return "question"
        
        # If I have high facilitation instinct
        if sm.facilitation_instinct >= 7 and context.my_role in ["facilitator", "leader"]:
            return "facilitation"
        
        # Default to statement
        return "statement"
```

#### D5.4: Social Context Builder

```python
# src/social/builder.py

from typing import List, Dict, Optional
from src.social.context import SocialContext, ParticipantInfo

class SocialContextBuilder:
    """Builds social context from meeting/conversation state."""
    
    @staticmethod
    def from_meeting_state(
        meeting_state: dict,
        my_agent_id: str
    ) -> SocialContext:
        """Build context from meeting state."""
        
        participants = []
        for p in meeting_state.get("participants", []):
            participants.append(ParticipantInfo(
                agent_id=p["agent_id"],
                name=p["name"],
                role=p.get("role", "participant"),
                expertise_areas=p.get("expertise", []),
                has_spoken=p.get("has_spoken", False),
                contribution_count=p.get("contribution_count", 0)
            ))
        
        # Build expertise map
        expertise_present = {}
        for p in participants:
            for skill in p.expertise_areas:
                if skill not in expertise_present:
                    expertise_present[skill] = []
                expertise_present[skill].append(p.agent_id)
        
        # Determine my role
        my_role = "participant"
        my_status = "peer"
        for p in meeting_state.get("participants", []):
            if p["agent_id"] == my_agent_id:
                my_role = p.get("meeting_role", "participant")
                my_status = p.get("status", "peer")
                break
        
        return SocialContext(
            participants=participants,
            group_size=len(participants),
            my_role=my_role,
            my_status_relative=my_status,
            current_speaker=meeting_state.get("current_speaker"),
            topic_under_discussion=meeting_state.get("current_topic", ""),
            discussion_phase=meeting_state.get("phase", "exploring"),
            expertise_present=expertise_present,
            speaking_distribution=meeting_state.get("speaking_distribution", {}),
            energy_level=meeting_state.get("energy", "engaged"),
            consensus_level=meeting_state.get("consensus", "discussing")
        )
```

### 8.4 Test Criteria

| Test | Expected Result |
|------|-----------------|
| Direct address | Returns MUST_RESPOND |
| Low relevance topic | Returns PASSIVE_AWARENESS |
| Expert present, hasn't spoken | Returns ACTIVE_LISTEN with defer reason |
| No conversational space | Returns ACTIVE_LISTEN with timing |
| Said enough already | Returns ACTIVE_LISTEN unless critical |
| Observer role | Returns ACTIVE_LISTEN |
| High expertise + space | Returns SHOULD_CONTRIBUTE |
| Group size adaptation | Higher threshold for larger groups |
| Solo context | Always contributes |

### 8.5 Definition of Done

- [ ] Social context model implemented
- [ ] All 5 externalization intents working
- [ ] Self-awareness factors evaluated
- [ ] Social awareness factors evaluated
- [ ] Group size adaptation working
- [ ] Role-based behavior implemented
- [ ] Integration with internal mind
- [ ] Unit tests at 80%+ coverage

**MILESTONE M3: Agent Knows When to Speak** ✓

---

## 9. Phase 6: Memory Architecture

### 9.1 Overview

| Attribute | Value |
|-----------|-------|
| **Duration** | 7 days |
| **Goal** | 4-tier memory with cognitive tier-appropriate access |
| **Team** | 1 developer |
| **Dependencies** | Phase 4 |

### 9.2 Objectives

1. Working memory (in-process)
2. Short-term memory (Redis + PostgreSQL)
3. Long-term memory (PostgreSQL)
4. Pattern library (PostgreSQL)
5. Memory promotion logic
6. Tier-appropriate retrieval

### 9.3 Deliverables

#### D6.1: Working Memory

```python
# src/memory/working.py

from dataclasses import dataclass, field
from typing import List, Optional, Dict
from collections import deque
from datetime import datetime

@dataclass
class ConversationTurn:
    """A single turn in conversation."""
    role: str  # user, assistant, system
    content: str
    timestamp: datetime
    speaker_name: Optional[str] = None

class WorkingMemory:
    """
    Tier 1: Active cognitive workspace.
    In-process, session-only, fastest access.
    """
    
    def __init__(self, max_turns: int = 20):
        self.conversation: deque[ConversationTurn] = deque(maxlen=max_turns)
        self.current_topic: str = ""
        self.current_mood: str = "neutral"
        self.confidence_level: float = 0.7
        
        # Quick-access cache for repeated queries
        self._cache: Dict[str, str] = {}
        self._cache_ttl: Dict[str, datetime] = {}
    
    def add_turn(self, turn: ConversationTurn):
        """Add conversation turn."""
        self.conversation.append(turn)
        self._invalidate_cache()
    
    def get_for_reflex(self) -> str:
        """Minimal context for REFLEX tier (~50 tokens)."""
        return f"Topic: {self.current_topic}\nMood: {self.current_mood}"
    
    def get_for_reactive(self, max_tokens: int = 150) -> str:
        """Recent context for REACTIVE tier."""
        recent = list(self.conversation)[-5:]
        lines = [f"{t.speaker_name or t.role}: {t.content[:100]}" for t in recent]
        return "\n".join(lines)[:max_tokens * 4]  # Rough char estimate
    
    def get_recent_turns(self, n: int = 10) -> List[ConversationTurn]:
        """Get last N turns."""
        return list(self.conversation)[-n:]
    
    def get_cached(self, key: str) -> Optional[str]:
        """Get cached value if not expired."""
        if key in self._cache:
            if datetime.utcnow() < self._cache_ttl.get(key, datetime.min):
                return self._cache[key]
        return None
    
    def set_cached(self, key: str, value: str, ttl_seconds: int = 60):
        """Cache a value."""
        self._cache[key] = value
        self._cache_ttl[key] = datetime.utcnow() + timedelta(seconds=ttl_seconds)
    
    def _invalidate_cache(self):
        """Clear cache on new input."""
        self._cache.clear()
        self._cache_ttl.clear()
```

#### D6.2: Short-Term Memory

```python
# src/memory/short_term.py

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime, timedelta
from uuid import UUID
import json

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

@dataclass
class ShortTermMemoryEntry:
    """A short-term memory entry."""
    
    memory_id: UUID
    agent_id: UUID
    memory_type: str  # observation, decision, interaction, insight
    content: str
    significance: float
    topic_keywords: List[str]
    created_at: datetime
    expires_at: datetime
    
    # Optional context
    project_id: Optional[UUID] = None
    related_agents: Optional[List[str]] = None

class ShortTermMemory:
    """
    Tier 2: Recent significant events.
    PostgreSQL-backed, 7-day TTL, indexed by topic.
    """
    
    DEFAULT_TTL_DAYS = 7
    MAX_ENTRIES = 100
    
    def __init__(self, session: AsyncSession, agent_id: UUID):
        self.session = session
        self.agent_id = agent_id
    
    async def add(
        self,
        content: str,
        memory_type: str,
        significance: float,
        topic_keywords: List[str],
        project_id: UUID = None
    ) -> ShortTermMemoryEntry:
        """Add memory entry."""
        
        # Check if at capacity
        count = await self._count_entries()
        if count >= self.MAX_ENTRIES:
            await self._evict_oldest()
        
        expires_at = datetime.utcnow() + timedelta(days=self.DEFAULT_TTL_DAYS)
        
        entry = ShortTermMemoryDB(
            agent_id=self.agent_id,
            memory_type=memory_type,
            content=content,
            significance=significance,
            topic_keywords=topic_keywords,
            project_id=project_id,
            expires_at=expires_at
        )
        
        self.session.add(entry)
        await self.session.commit()
        
        return self._to_model(entry)
    
    async def query(
        self,
        topic: str = None,
        keywords: List[str] = None,
        max_results: int = 10,
        max_tokens: int = 300
    ) -> str:
        """Query memories by topic/keywords."""
        
        query = select(ShortTermMemoryDB).where(
            ShortTermMemoryDB.agent_id == self.agent_id,
            ShortTermMemoryDB.expires_at > datetime.utcnow()
        )
        
        if keywords:
            # Filter by keyword overlap
            query = query.where(
                ShortTermMemoryDB.topic_keywords.overlap(keywords)
            )
        
        query = query.order_by(
            ShortTermMemoryDB.significance.desc(),
            ShortTermMemoryDB.created_at.desc()
        ).limit(max_results)
        
        result = await self.session.execute(query)
        entries = result.scalars().all()
        
        return self._format_entries(entries, max_tokens)
    
    async def get_recent(
        self,
        hours: int = 24,
        max_tokens: int = 200
    ) -> str:
        """Get recent memories."""
        
        since = datetime.utcnow() - timedelta(hours=hours)
        
        query = select(ShortTermMemoryDB).where(
            ShortTermMemoryDB.agent_id == self.agent_id,
            ShortTermMemoryDB.created_at > since,
            ShortTermMemoryDB.expires_at > datetime.utcnow()
        ).order_by(
            ShortTermMemoryDB.created_at.desc()
        ).limit(10)
        
        result = await self.session.execute(query)
        entries = result.scalars().all()
        
        return self._format_entries(entries, max_tokens)
    
    async def promote_to_long_term(
        self,
        memory_id: UUID,
        long_term_ref: UUID
    ):
        """Mark memory as promoted to long-term."""
        await self.session.execute(
            update(ShortTermMemoryDB)
            .where(ShortTermMemoryDB.memory_id == memory_id)
            .values(promoted_to=long_term_ref)
        )
        await self.session.commit()
    
    def _format_entries(
        self,
        entries: List,
        max_tokens: int
    ) -> str:
        """Format entries for prompt context."""
        lines = []
        char_count = 0
        max_chars = max_tokens * 4
        
        for entry in entries:
            line = f"[{entry.memory_type}] {entry.content}"
            if char_count + len(line) > max_chars:
                break
            lines.append(line)
            char_count += len(line)
        
        return "\n".join(lines)
```

#### D6.3: Long-Term Memory

```python
# src/memory/long_term.py

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
from uuid import UUID

@dataclass
class ProjectChapter:
    """A chapter of project history."""
    
    chapter_id: UUID
    agent_id: UUID
    project_id: UUID
    
    title: str
    summary: str
    role_in_project: str
    
    start_date: datetime
    end_date: Optional[datetime]
    
    outcome: str  # success, partial_success, failure, ongoing
    significance: float
    lessons_learned: str
    
    collaborators: List[str]

class LongTermMemory:
    """
    Tier 3: Permanent records of significant experiences.
    PostgreSQL-backed, permanent storage.
    """
    
    def __init__(self, session: AsyncSession, agent_id: UUID):
        self.session = session
        self.agent_id = agent_id
    
    async def add_chapter(
        self,
        project_id: UUID,
        title: str,
        summary: str,
        role: str,
        outcome: str,
        significance: float,
        lessons: str,
        collaborators: List[str] = None
    ) -> ProjectChapter:
        """Add a project chapter."""
        
        chapter = ProjectChapterDB(
            agent_id=self.agent_id,
            project_id=project_id,
            title=title,
            summary=summary,
            role_in_project=role,
            outcome=outcome,
            significance=significance,
            lessons_learned=lessons,
            collaborators=collaborators or [],
            start_date=datetime.utcnow()
        )
        
        self.session.add(chapter)
        await self.session.commit()
        
        return self._to_model(chapter)
    
    async def search(
        self,
        topic: str = None,
        outcome: str = None,
        max_results: int = 5,
        max_tokens: int = 500
    ) -> str:
        """Search long-term memories."""
        
        query = select(ProjectChapterDB).where(
            ProjectChapterDB.agent_id == self.agent_id
        )
        
        if topic:
            query = query.where(
                ProjectChapterDB.title.ilike(f"%{topic}%") |
                ProjectChapterDB.summary.ilike(f"%{topic}%")
            )
        
        if outcome:
            query = query.where(ProjectChapterDB.outcome == outcome)
        
        query = query.order_by(
            ProjectChapterDB.significance.desc()
        ).limit(max_results)
        
        result = await self.session.execute(query)
        chapters = result.scalars().all()
        
        return self._format_chapters(chapters, max_tokens)
    
    def _format_chapters(
        self,
        chapters: List,
        max_tokens: int
    ) -> str:
        """Format chapters for prompt context."""
        sections = []
        char_count = 0
        max_chars = max_tokens * 4
        
        for chapter in chapters:
            section = f"""
Project: {chapter.title}
Role: {chapter.role_in_project}
Outcome: {chapter.outcome}
Lessons: {chapter.lessons_learned}
""".strip()
            
            if char_count + len(section) > max_chars:
                break
            sections.append(section)
            char_count += len(section)
        
        return "\n\n".join(sections)
```

#### D6.4: Memory Manager

```python
# src/memory/manager.py

from typing import Optional
from uuid import UUID

from src.memory.working import WorkingMemory
from src.memory.short_term import ShortTermMemory
from src.memory.long_term import LongTermMemory
from src.cognitive.tiers import CognitiveTier, TIER_CONFIGS

class MemoryManager:
    """
    Manages all memory tiers and provides tier-appropriate access.
    """
    
    def __init__(
        self,
        agent_id: UUID,
        working: WorkingMemory,
        short_term: ShortTermMemory,
        long_term: LongTermMemory
    ):
        self.agent_id = agent_id
        self.working = working
        self.short_term = short_term
        self.long_term = long_term
    
    async def get_context_for_tier(
        self,
        tier: CognitiveTier,
        topic: str = None
    ) -> str:
        """Get memory context appropriate for cognitive tier."""
        
        config = TIER_CONFIGS[tier]
        
        if config.memory_access == "cached":
            # REFLEX: working memory only
            return self.working.get_for_reflex()
        
        elif config.memory_access == "recent":
            # REACTIVE: working + recent short-term
            working = self.working.get_for_reactive()
            recent = await self.short_term.get_recent(hours=1, max_tokens=100)
            return f"{working}\n\nRecent:\n{recent}"
        
        elif config.memory_access == "indexed":
            # DELIBERATE: working + indexed short-term
            working = self.working.get_for_reactive(max_tokens=150)
            
            keywords = topic.split() if topic else []
            indexed = await self.short_term.query(
                keywords=keywords,
                max_results=5,
                max_tokens=300
            )
            
            return f"{working}\n\nRelevant memories:\n{indexed}"
        
        else:
            # ANALYTICAL/COMPREHENSIVE: full search
            working = self.working.get_for_reactive(max_tokens=200)
            
            keywords = topic.split() if topic else []
            short = await self.short_term.query(
                keywords=keywords,
                max_results=10,
                max_tokens=400
            )
            
            long = await self.long_term.search(
                topic=topic,
                max_results=5,
                max_tokens=400
            )
            
            return f"""Working Memory:
{working}

Recent Experience:
{short}

Long-term Memory:
{long}"""
    
    async def record_significant_event(
        self,
        content: str,
        memory_type: str,
        significance: float,
        topic: str,
        project_id: UUID = None
    ):
        """Record a significant event to short-term memory."""
        
        keywords = topic.split() if topic else []
        
        await self.short_term.add(
            content=content,
            memory_type=memory_type,
            significance=significance,
            topic_keywords=keywords,
            project_id=project_id
        )
    
    async def evaluate_promotion(
        self,
        memory_id: UUID,
        significance: float,
        relationship_delta: int = 0
    ) -> bool:
        """Check if memory should be promoted to long-term."""
        
        # Promotion criteria
        if significance >= 0.7:
            return True
        if abs(relationship_delta) >= 1:
            return True
        
        return False
```

### 9.4 Test Criteria

| Test | Expected Result |
|------|-----------------|
| Working memory add/get | Turns stored and retrieved |
| REFLEX memory access | Only working memory |
| REACTIVE memory access | Working + recent |
| DELIBERATE memory access | Working + indexed |
| ANALYTICAL memory access | All tiers |
| Short-term query by keyword | Matching entries returned |
| Short-term expiry | Expired entries not returned |
| Long-term search | Chapters found by topic |
| Memory promotion | Significant events promoted |

### 9.5 Definition of Done

- [ ] Working memory implemented
- [ ] Short-term memory with PostgreSQL
- [ ] Long-term memory with chapters
- [ ] Tier-appropriate retrieval working
- [ ] Memory promotion logic
- [ ] Expiry handling
- [ ] Unit tests at 80%+ coverage

**MILESTONE M4: Agent Remembers** ✓

---

## 10. Phase 7: Multi-Agent Coordination

### 10.1 Overview

| Attribute | Value |
|-----------|-------|
| **Duration** | 5 days |
| **Goal** | 20 agents collaborating in meetings |
| **Team** | 1-2 developers |
| **Dependencies** | Phase 5, Phase 6 |

### 10.2 Objectives

1. Agent manager with lazy loading
2. Meeting state management
3. Stimulus broadcast
4. Response collection
5. Actor model for concurrency

### 10.3 Key Deliverables

- Agent lifecycle manager (load, unload, LRU)
- Meeting service (join, leave, broadcast)
- Actor-per-agent pattern
- Concurrent stimulus processing
- Response aggregation

### 10.4 Test Criteria

| Test | Expected Result |
|------|-----------------|
| Load 20 agents | All loaded successfully |
| Broadcast stimulus | All agents receive |
| Collect responses | Responses aggregated |
| LRU eviction | Oldest agent evicted at capacity |
| Concurrent processing | No race conditions |

**MILESTONE M5: Team Collaborates** ✓

---

## 11. Phase 8: Pattern Learning

### 11.1 Overview

| Attribute | Value |
|-----------|-------|
| **Duration** | 7 days |
| **Goal** | Agents learn from project outcomes |
| **Team** | 1 developer |
| **Dependencies** | Phase 6 |

### 11.2 Objectives

1. Pattern library model
2. Outcome recording
3. Pattern extraction
4. Confidence updating
5. Pattern retrieval for context

### 11.3 Key Deliverables

- Pattern database schema
- Outcome recording API
- Pattern extraction logic
- Confidence update on outcomes
- Pattern query for prompts

### 11.4 Test Criteria

| Test | Expected Result |
|------|-----------------|
| Record outcome | Outcome stored |
| Extract pattern | Pattern created from outcome |
| Success updates confidence | Confidence increases |
| Failure updates confidence | Confidence decreases |
| Query patterns | Relevant patterns returned |

**MILESTONE M6: Team Learns** ✓

---

## 12. Phase 9: Production Hardening

### 12.1 Overview

| Attribute | Value |
|-----------|-------|
| **Duration** | 5 days |
| **Goal** | Production-ready safety and resilience |
| **Team** | 1 developer |
| **Dependencies** | Phase 7, Phase 8 |

### 12.2 Objectives

1. Input sanitization
2. Output filtering
3. Circuit breaker for models
4. Rate limiting
5. Comprehensive monitoring

### 12.3 Key Deliverables

- Input sanitization middleware
- Output filter pipeline
- Circuit breaker implementation
- Rate limiter per agent/tier
- Prometheus metrics
- Grafana dashboards

---

## 13. Phase 10: Integration & Validation

### 13.1 Overview

| Attribute | Value |
|-----------|-------|
| **Duration** | 5 days |
| **Goal** | Validate complete system meets requirements |
| **Team** | 1-2 developers |
| **Dependencies** | All previous phases |

### 13.2 Objectives

1. End-to-end integration tests
2. Load testing (20 agents)
3. Budget validation (<$15/hour)
4. Social intelligence validation
5. Documentation completion

### 13.3 Test Scenarios

1. **Full Meeting Simulation**: 20 agents, 1-hour meeting, all participating
2. **Scale Test**: 100 stimuli/minute sustained
3. **Budget Test**: Track actual cost over 1 hour
4. **Social Appropriateness**: Human evaluation of decisions
5. **Cognitive Quality**: Human evaluation of thoughts

### 13.4 Acceptance Criteria

| Criteria | Target | Test Method |
|----------|--------|-------------|
| Concurrent agents | 20 | Load test |
| REFLEX latency | <200ms p95 | Load test |
| REACTIVE latency | <500ms p95 | Load test |
| DELIBERATE latency | <2s p95 | Load test |
| Hourly cost | <$15 | 1-hour test |
| Social appropriateness | >85% | Human eval |
| Thought quality | >90% | Human eval |

**MILESTONE M7: Production Ready** ✓

---

## 14. Quality Gates

### Gate Criteria (Apply to Each Phase)

| Category | Requirement |
|----------|-------------|
| **Code Quality** | Test coverage ≥80%, no critical linting errors |
| **Performance** | No regression from previous phase |
| **Functionality** | All defined tests pass |
| **Documentation** | README updated, API docs current |
| **Review** | Code review approved |

### Phase Gate Checklist

```markdown
## Phase N Gate Checklist

- [ ] All deliverables completed
- [ ] All test criteria met
- [ ] Test coverage ≥80%
- [ ] No critical bugs
- [ ] Performance targets met
- [ ] Documentation updated
- [ ] Code review approved
- [ ] Demo completed
```

---

## 15. Risk Mitigation

| Phase | Risk | Mitigation |
|-------|------|------------|
| 2 | Model quality insufficient | Test multiple Qwen variants |
| 2 | GPU availability | Multi-cloud strategy |
| 3 | Latency targets missed | Aggressive prompt optimization |
| 4 | Thought accumulation overhead | Background processing |
| 5 | Social decisions inappropriate | Extensive human evaluation |
| 6 | Memory retrieval slow | Index optimization |
| 7 | Race conditions | Actor model |
| 8 | Pattern extraction unreliable | Manual curation option |
| 9 | Safety bypass | Multiple filter layers |
| 10 | Integration failures | Feature flags |

---

## 16. Resource Requirements

### 16.1 Team

| Role | Phase 0-4 | Phase 5-7 | Phase 8-10 |
|------|-----------|-----------|------------|
| Backend Developer | 1 | 1-2 | 1 |
| DevOps | 0.25 | 0.5 | 0.5 |
| QA | 0 | 0.5 | 1 |

### 16.2 Infrastructure (Development)

| Component | Specification | Cost/Hour |
|-----------|---------------|-----------|
| T4 GPU | 16GB | $0.40 |
| A10G GPU | 24GB | $1.25 |
| A100 GPU | 40GB | $3.50 |
| App Server | 4 vCPU, 16GB | $0.20 |
| PostgreSQL | Managed | $0.15 |
| Redis | Managed | $0.10 |
| **Total** | | **~$5.60/hr** |

### 16.3 Development Environment

- Local: Docker Compose with CPU inference (slow but free)
- Testing: Cloud GPUs on-demand
- CI/CD: GitHub Actions with cloud GPU runners

---

## Document Approval

- [ ] Product Owner: _________________ Date: _______
- [ ] Technical Lead: _________________ Date: _______
- [ ] Architect: _________________ Date: _______

---

**End of Build Plan**

**Version**: 1.0
**Total Duration**: ~12 weeks
