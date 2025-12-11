"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.api.routes import agents, health
from src.core.config import get_settings
from src.core.exceptions import CAEException
from src.infrastructure.database import close_db, init_db
from src.infrastructure.redis import close_redis, get_redis

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager.

    Handles startup and shutdown events.
    """
    settings = get_settings()
    logger.info(f"Starting {settings.service_name} in {settings.environment} mode")

    # Startup
    try:
        # Initialize database (creates tables if they don't exist in dev mode)
        if settings.is_development:
            await init_db()
            logger.info("Database initialized")

        # Initialize Redis connection
        await get_redis()
        logger.info("Redis connection established")

        logger.info("Application startup complete")
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down application")
    await close_redis()
    await close_db()
    logger.info("Application shutdown complete")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="Cognitive Agent Engine",
        description="AI agents with human-like social intelligence",
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/docs" if settings.is_development else None,
        redoc_url="/redoc" if settings.is_development else None,
    )

    # Register exception handlers
    register_exception_handlers(app)

    # Register routes
    app.include_router(health.router)
    app.include_router(agents.router)

    return app


def register_exception_handlers(app: FastAPI) -> None:
    """Register custom exception handlers."""

    @app.exception_handler(CAEException)
    async def cae_exception_handler(request: Request, exc: CAEException) -> JSONResponse:
        """Handle CAE custom exceptions."""
        return JSONResponse(
            status_code=get_status_code(exc.code),
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details,
                },
                "timestamp": datetime.utcnow().isoformat(),
                "path": str(request.url),
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Handle unexpected exceptions."""
        logger.exception(f"Unhandled exception: {exc}")
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred",
                    "details": {},
                },
                "timestamp": datetime.utcnow().isoformat(),
                "path": str(request.url),
            },
        )


def get_status_code(error_code: str) -> int:
    """Map error codes to HTTP status codes."""
    status_map: dict[str, int] = {
        "AGENT_NOT_FOUND": 404,
        "AGENT_LIMIT_EXCEEDED": 429,
        "BUDGET_EXCEEDED": 429,
        "MODEL_UNAVAILABLE": 503,
        "VALIDATION_ERROR": 422,
        "DATABASE_ERROR": 500,
        "INTERNAL_ERROR": 500,
    }
    return status_map.get(error_code, 500)


# Create the application instance
app = create_app()

