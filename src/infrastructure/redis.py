"""Async Redis client setup."""

from typing import Optional

import redis.asyncio as redis
from redis.asyncio import Redis

from src.core.config import get_settings

# Global Redis client (initialized lazily)
_redis_client: Optional[Redis] = None


async def get_redis() -> Redis:
    """Get or create the Redis client."""
    global _redis_client
    if _redis_client is None:
        settings = get_settings()
        _redis_client = redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
    return _redis_client


async def close_redis() -> None:
    """Close Redis connection."""
    global _redis_client
    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None


async def check_redis_health() -> bool:
    """Check if Redis is healthy."""
    try:
        client = await get_redis()
        await client.ping()
        return True
    except Exception:
        return False

