"""Caching decorators for the Pokemon MCP Server.

Usage:
    from src.cache.decorators import cached

    @cached(ttl=3600, key_prefix="pokemon")
    async def get_pokemon(self, identifier: str) -> Pokemon:
        ...
"""

import functools
from collections.abc import Callable
from typing import Any, TypeVar

from ..config.logging import get_logger

logger = get_logger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


def cached(ttl: int = 3600, key_prefix: str = "cache") -> Callable[[F], F]:
    """Decorator to cache async function results in Redis.

    Provides graceful degradation: if Redis is unavailable,
    the function executes normally without caching.

    Args:
        ttl: Time to live in seconds (default: 3600)
        key_prefix: Prefix for cache keys (default: "cache")

    Returns:
        Decorated function with caching behavior

    Example:
        @cached(ttl=86400, key_prefix="type")
        async def get_type_info(self, type_name: str) -> dict:
            ...
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Get current global cache instance (sync, returns None if not initialized)
            from .redis_cache import get_redis_cache

            cache = get_redis_cache()

            # Build cache key: skip 'self' if this is a method call
            cache_args = args[1:] if args else args
            key_parts = [str(a) for a in cache_args] + [
                f"{k}={v}" for k, v in sorted(kwargs.items())
            ]
            key = f"{key_prefix}:{':'.join(key_parts)}" if key_parts else key_prefix

            # Attempt cache lookup
            if cache is not None and cache._available:
                cached_value = await cache.get(key)
                if cached_value is not None:
                    logger.info("[CACHE HIT]", key=key)
                    return cached_value

            # Cache miss or unavailable — execute original function
            result = await func(*args, **kwargs)

            # Attempt to store in cache (best-effort)
            if cache is not None and cache._available and result is not None:
                # Serialize Pydantic models or plain dicts
                if hasattr(result, "model_dump"):
                    serializable = result.model_dump()
                elif isinstance(result, list):
                    serializable = [
                        item.model_dump() if hasattr(item, "model_dump") else item
                        for item in result
                    ]
                else:
                    serializable = result

                await cache.set(key, serializable, ttl=ttl)
                logger.info("[CACHE SET]", key=key, ttl=ttl)

            return result

        return wrapper  # type: ignore[return-value]

    return decorator
