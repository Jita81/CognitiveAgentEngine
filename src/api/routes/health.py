"""Health check endpoints."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_db_session
from src.infrastructure.redis import check_redis_health

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    """Response model for health check."""

    status: str
    version: str


class ReadinessCheck(BaseModel):
    """Individual readiness check result."""

    status: str


class ReadinessResponse(BaseModel):
    """Response model for readiness check."""

    status: str
    checks: dict[str, str]


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Liveness probe.

    Returns healthy if the service is running.
    Used by container orchestrators to check if the service is alive.
    """
    return HealthResponse(status="healthy", version="0.1.0")


@router.get("/health/ready", response_model=ReadinessResponse)
async def readiness_check(
    db: AsyncSession = Depends(get_db_session),
) -> ReadinessResponse:
    """Readiness probe.

    Checks all dependencies are available:
    - Database (PostgreSQL)
    - Cache (Redis)

    Used by container orchestrators to check if the service is ready to accept traffic.
    """
    checks: dict[str, str] = {}

    # Database check
    try:
        await db.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as e:
        checks["database"] = f"error: {str(e)}"

    # Redis check
    try:
        redis_ok = await check_redis_health()
        checks["redis"] = "ok" if redis_ok else "error: connection failed"
    except Exception as e:
        checks["redis"] = f"error: {str(e)}"

    # Determine overall status
    all_ok = all(v == "ok" for v in checks.values())

    return ReadinessResponse(
        status="ready" if all_ok else "not_ready",
        checks=checks,
    )

