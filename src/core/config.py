"""Configuration management using Pydantic settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ==========================================================================
    # Service Configuration
    # ==========================================================================
    service_name: str = "cognitive-agent-engine"
    environment: str = "development"
    log_level: str = "INFO"

    # ==========================================================================
    # Database Configuration
    # ==========================================================================
    database_url: str = "postgresql+asyncpg://cae:cae@localhost:5432/cae"
    database_pool_size: int = 20

    # ==========================================================================
    # Redis Configuration
    # ==========================================================================
    redis_url: str = "redis://localhost:6379"

    # ==========================================================================
    # Model Endpoints (Phase 2)
    # ==========================================================================
    vllm_small_url: str = ""
    vllm_medium_url: str = ""
    vllm_large_url: str = ""

    # ==========================================================================
    # Budget Configuration (Phase 2)
    # ==========================================================================
    hourly_budget_usd: float = 15.0
    budget_alert_threshold: float = 0.8

    # ==========================================================================
    # Agent Configuration
    # ==========================================================================
    max_active_agents: int = 20
    agent_memory_limit_mb: int = 100

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == "production"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

