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

### Example Responses

**Liveness Probe:**
```json
{
  "status": "healthy",
  "version": "0.1.0"
}
```

**Readiness Probe:**
```json
{
  "status": "ready",
  "checks": {
    "database": "ok",
    "redis": "ok"
  }
}
```

## Project Structure

```
cognitive-agent-engine/
├── src/
│   ├── api/                    # FastAPI application
│   │   ├── main.py             # Application entry point
│   │   ├── routes/             # API route definitions
│   │   ├── middleware/         # Request/response middleware
│   │   └── dependencies.py     # FastAPI dependencies
│   ├── core/                   # Core utilities
│   │   ├── config.py           # Configuration management
│   │   └── exceptions.py       # Custom exceptions
│   ├── agents/                 # Agent management (Phase 1)
│   ├── cognitive/              # Cognitive processing (Phase 3)
│   ├── social/                 # Social intelligence (Phase 5)
│   ├── memory/                 # Memory architecture (Phase 6)
│   └── infrastructure/         # Database, cache, external services
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
| `MAX_ACTIVE_AGENTS` | Maximum concurrent agents | 20 |

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_health.py
```

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

## Architecture

The Cognitive Agent Engine uses a layered architecture:

1. **API Layer** - FastAPI for HTTP/WebSocket handling
2. **Agent Runtime** - Actor-based agent lifecycle management
3. **Cognitive Services** - Tiered model routing and inference
4. **Persistence Layer** - PostgreSQL for state, Redis for caching

### Cognitive Tiers

| Tier | Purpose | Target Latency |
|------|---------|----------------|
| REFLEX | Immediate reactions | <200ms |
| REACTIVE | Quick assessments | <500ms |
| DELIBERATE | Considered responses | <2s |
| ANALYTICAL | Deep analysis | <5s |
| COMPREHENSIVE | Full exploration | <10s |

## License

MIT

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

