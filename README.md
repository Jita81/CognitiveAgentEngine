# Cognitive Agent Engine

AI agents with human-like social intelligence. Each agent possesses skills, personality, and emotional intelligence that enables them to think independently, know when to speak, and learn from experience.

## Overview

The Cognitive Agent Engine creates AI team members that can:

- **Think independently** - Process information and form thoughts without necessarily speaking
- **Know when to speak** - Understand context, read the room, and contribute when valuable
- **Know when to listen** - Recognize when others are more qualified or when silence is appropriate
- **Learn from experience** - Accumulate patterns of success and failure from projects
- **Scale naturally** - Operate effectively whether alone, in small teams, or in groups of thousands

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)

### Running with Docker (Recommended)

```bash
# Clone the repository
cd cognitive-agent-engine

# Start all services
docker-compose -f docker/docker-compose.yml up -d

# Check health
curl http://localhost:8000/health

# View logs
docker-compose -f docker/docker-compose.yml logs -f api
```

### Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Copy environment configuration
cp env.example .env

# Start PostgreSQL and Redis (using Docker)
docker-compose -f docker/docker-compose.yml up -d db redis

# Run database migrations
alembic upgrade head

# Start the API server
uvicorn src.api.main:app --reload

# Run tests
pytest
```

## API Endpoints

### Health Checks

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Liveness probe - returns healthy if service is running |
| `/health/ready` | GET | Readiness probe - checks database and Redis connectivity |

### Agent Management (Phase 1)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/agents` | POST | Create a new agent with profile |
| `/v1/agents/{id}` | GET | Get agent by ID |
| `/v1/agents` | GET | List agents with filtering |
| `/v1/agents/{id}` | PATCH | Update agent profile |
| `/v1/agents/{id}` | DELETE | Soft delete agent |

### Model Infrastructure (Phase 2)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/models/status` | GET | Get model router status and health |
| `/v1/models/generate` | POST | Generate text with specified tier |
| `/v1/models/tiers` | GET | Get cognitive tier configurations |
| `/v1/models/budget` | GET | Get current budget utilization |
| `/v1/models/health-check` | GET | Check health of all model endpoints |

### Cognitive Processing (Phase 3)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/cognitive/process` | POST | Process stimulus through cognitive tiers |
| `/v1/cognitive/process/tier` | POST | Process with a specific tier |
| `/v1/cognitive/tiers` | GET | Get all tier configurations |
| `/v1/cognitive/tiers/{name}` | GET | Get specific tier info |
| `/v1/cognitive/status` | GET | Get cognitive system status |

### Example: Cognitive Processing

**Request:**
```json
{
  "stimulus": "Should we refactor the authentication service?",
  "agent_id": "550e8400-e29b-41d4-a716-446655440000",
  "urgency": 0.5,
  "complexity": 0.7,
  "relevance": 0.8,
  "purpose": "architecture_decision"
}
```

**Response:**
```json
{
  "thoughts": [
    {
      "thought_id": "...",
      "tier": "DELIBERATE",
      "content": "Given my experience with distributed systems...",
      "thought_type": "insight",
      "confidence": 0.75,
      "completeness": 0.8
    }
  ],
  "primary_thought": { ... },
  "processing_time_ms": 1250.5,
  "tiers_used": ["REACTIVE", "DELIBERATE"],
  "thought_count": 2
}
```

## Project Structure

```
cognitive-agent-engine/
├── src/
│   ├── api/                    # FastAPI application
│   │   ├── main.py             # Application entry point
│   │   ├── routes/             # API route definitions
│   │   │   ├── health.py       # Health endpoints
│   │   │   ├── agents.py       # Agent CRUD endpoints
│   │   │   ├── models.py       # Model infrastructure endpoints
│   │   │   └── cognitive.py    # Cognitive processing endpoints
│   │   ├── middleware/         # Request/response middleware
│   │   └── dependencies.py     # FastAPI dependencies
│   ├── core/                   # Core utilities
│   │   ├── config.py           # Configuration management
│   │   └── exceptions.py       # Custom exceptions
│   ├── agents/                 # Agent management (Phase 1)
│   │   ├── models.py           # Pydantic models for profiles
│   │   ├── repository.py       # Database operations
│   │   └── formatter.py        # Profile formatting for prompts
│   ├── cognitive/              # Cognitive processing (Phase 3)
│   │   ├── tiers.py            # Tier configurations
│   │   ├── models.py           # Thought and CognitiveResult models
│   │   ├── prompts.py          # Tiered prompt builder
│   │   └── processor.py        # Main cognitive processor
│   ├── social/                 # Social intelligence (Phase 5)
│   ├── memory/                 # Memory architecture (Phase 6)
│   └── infrastructure/         # Database, cache, external services
│       ├── database.py         # SQLAlchemy async setup
│       ├── redis.py            # Redis client
│       ├── model_client.py     # vLLM client
│       ├── model_router.py     # Cognitive tier routing
│       ├── budget_manager.py   # Token budget tracking
│       └── metrics.py          # Prometheus metrics
├── migrations/                 # Alembic database migrations
├── tests/                      # Test suite
├── docker/                     # Docker configuration
└── pyproject.toml              # Python project configuration
```

## Configuration

Configuration is managed via environment variables. See `env.example` for all available options.

| Variable | Description | Default |
|----------|-------------|---------|
| `SERVICE_NAME` | Service name | cognitive-agent-engine |
| `ENVIRONMENT` | Environment (development/production) | development |
| `LOG_LEVEL` | Logging level | INFO |
| `DATABASE_URL` | PostgreSQL connection URL | postgresql+asyncpg://cae:cae@localhost:5432/cae |
| `REDIS_URL` | Redis connection URL | redis://localhost:6379 |
| `HOURLY_BUDGET_USD` | Maximum hourly model cost | 15.0 |
| `MAX_ACTIVE_AGENTS` | Maximum concurrent agents | 20 |

## Architecture

The Cognitive Agent Engine uses a layered architecture:

1. **API Layer** - FastAPI for HTTP/WebSocket handling
2. **Agent Runtime** - Actor-based agent lifecycle management
3. **Cognitive Services** - Tiered model routing and inference
4. **Persistence Layer** - PostgreSQL for state, Redis for caching

### Cognitive Tiers

The system implements 5 cognitive tiers with increasing depth and cost:

| Tier | Purpose | Max Tokens | Target Latency | Memory Access |
|------|---------|------------|----------------|---------------|
| REFLEX | Immediate reactions | 150 | <200ms | Cached |
| REACTIVE | Quick assessments | 400 | <500ms | Recent |
| DELIBERATE | Considered responses | 1200 | <2s | Indexed |
| ANALYTICAL | Deep analysis | 2500 | <5s | Full search |
| COMPREHENSIVE | Full exploration | 4000 | <10s | Full search |

### Strategy Planning

The cognitive processor automatically selects tiers based on stimulus characteristics:

- **High urgency + relevant**: REFLEX → parallel REACTIVE → DELIBERATE
- **Low urgency + complex**: DELIBERATE → ANALYTICAL
- **Low relevance**: REFLEX only (note for context)
- **Medium everything**: REACTIVE or DELIBERATE based on complexity

### Thought Model

Each cognitive process produces `Thought` objects with:
- **Content**: The actual thought text
- **Type**: insight, concern, question, observation, plan, reaction
- **Confidence**: 0-1 score based on tier and hedging language
- **Completeness**: 0-1 score based on token utilization

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_cognitive.py

# Run tests with verbose output
pytest -v
```

**Current Test Status:**
- 139 tests passing
- 80% code coverage

### Code Quality

```bash
# Format code
ruff format src tests

# Lint code
ruff check src tests

# Type checking
mypy src
```

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

## Build Progress

| Phase | Name | Status | Milestone |
|-------|------|--------|-----------|
| 0 | Foundation | Complete | Infrastructure ready |
| 1 | Agent Identity & Skills | Complete | Agents have profiles |
| 2 | Model Infrastructure | Complete | vLLM routing works |
| 3 | Cognitive Tiers | Complete | M1: Agent Responds |
| 4 | Internal Mind | Planned | M2: Agent Thinks |
| 5 | Social Intelligence | Planned | M3: Agent Knows When to Speak |
| 6 | Memory Architecture | Planned | M4: Agent Remembers |
| 7 | Multi-Agent Coordination | Planned | M5: Team Collaborates |
| 8 | Pattern Learning | Planned | M6: Team Learns |
| 9 | Production Hardening | Planned | Production ready |
| 10 | Integration & Validation | Planned | M7: All criteria met |

## License

MIT

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.
