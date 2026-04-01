"""Cache module for Pokemon MCP Server."""

from .decorators import cached
from .redis_cache import (
    RedisCache,
    close_redis_cache,
    get_redis_cache,
    init_redis_cache,
)

__all__ = [
    "RedisCache",
    "get_redis_cache",
    "init_redis_cache",
    "close_redis_cache",
    "cached",
]
