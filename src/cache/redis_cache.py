"""Redis cache client with async support and graceful degradation."""

import json
from typing import Any

import redis.asyncio as redis_async
from redis.asyncio import Redis
from redis.exceptions import RedisError

from ..config.logging import get_logger
from ..config.settings import Settings, get_settings

logger = get_logger(__name__)

# Global cache instance — managed by server lifespan
_cache: "RedisCache | None" = None


class CacheMetrics:
    """Cache hit/miss metrics."""

    def __init__(self) -> None:
        self.hits: int = 0
        self.misses: int = 0
        self.errors: int = 0

    def hit_rate(self) -> float:
        """Calculate cache hit rate as percentage."""
        total = self.hits + self.misses
        return (self.hits / total * 100) if total > 0 else 0.0

    def __repr__(self) -> str:
        return (
            f"CacheMetrics(hits={self.hits}, misses={self.misses}, "
            f"errors={self.errors}, hit_rate={self.hit_rate():.1f}%)"
        )


class RedisCache:
    """Async Redis cache client with graceful degradation."""

    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        db: int = 0,
        password: str | None = None,
    ) -> None:
        """Initialize Redis cache.

        Args:
            redis_url: Redis connection URL
            db: Redis database number
            password: Redis password (optional)
        """
        self.redis_url = redis_url
        self.db = db
        self.password = password
        self.client: Redis[str] | None = None
        self.metrics = CacheMetrics()
        self._available = False

    async def start(self) -> None:
        """Start Redis connection."""
        try:
            if self.password:
                connection_url = self.redis_url
                if "://" in connection_url and "@" not in connection_url:
                    protocol, rest = connection_url.split("://", 1)
                    connection_url = f"{protocol}://:{self.password}@{rest}"
            else:
                connection_url = self.redis_url

            self.client = redis_async.from_url(
                connection_url,
                db=self.db,
                decode_responses=True,
                socket_connect_timeout=5,
            )

            # Test connection
            await self.client.ping()
            self._available = True
            logger.info("[REDIS] Connected", redis_url=self.redis_url, db=self.db)
        except (RedisError, Exception) as e:
            self._available = False
            logger.warning(
                "[REDIS] Unavailable — skipping cache",
                error=str(e),
                redis_url=self.redis_url,
            )

    async def close(self) -> None:
        """Close Redis connection."""
        if self.client:
            try:
                await self.client.close()
                self._available = False
                logger.info("[REDIS] Closed")
            except Exception as e:
                logger.error("Error closing Redis connection", error=str(e))

    async def get(self, key: str) -> Any:
        """Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found or error occurred
        """
        if not self._available or not self.client:
            return None

        try:
            value = await self.client.get(key)
            if value:
                self.metrics.hits += 1
                logger.debug("Cache HIT", key=key)
                return json.loads(value)
            else:
                self.metrics.misses += 1
                logger.debug("Cache MISS", key=key)
                return None
        except (RedisError, json.JSONDecodeError) as e:
            self.metrics.errors += 1
            logger.warning("Cache GET error", key=key, error=str(e))
            return None

    async def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        """Set value in cache.

        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            ttl: Time to live in seconds

        Returns:
            True if successful, False otherwise
        """
        if not self._available or not self.client:
            return False

        try:
            serialized = json.dumps(value)
            await self.client.setex(key, ttl or 3600, serialized)  # Default TTL: 1 hour
            logger.debug("Cache SET", key=key, ttl=ttl)
            return True
        except (RedisError, json.JSONDecodeError) as e:
            self.metrics.errors += 1
            logger.warning("Cache SET error", key=key, error=str(e))
            return False

    async def delete(self, key: str) -> bool:
        """Delete value from cache.

        Args:
            key: Cache key

        Returns:
            True if deleted, False otherwise
        """
        if not self._available or not self.client:
            return False

        try:
            result = await self.client.delete(key)
            logger.debug("Cache DELETE", key=key, deleted=result > 0)
            return result > 0
        except (RedisError, Exception) as e:
            self.metrics.errors += 1
            logger.warning("Cache DELETE error", key=key, error=str(e))
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache.

        Args:
            key: Cache key

        Returns:
            True if exists, False otherwise
        """
        if not self._available or not self.client:
            return False

        try:
            result = await self.client.exists(key)
            return result > 0
        except (RedisError, Exception) as e:
            logger.warning("Cache EXISTS error", key=key, error=str(e))
            return False

    async def flush(self) -> bool:
        """Flush all keys from cache (DEVELOPMENT ONLY).

        Returns:
            True if successful, False otherwise
        """
        if not self._available or not self.client:
            return False

        try:
            await self.client.flushdb()
            logger.info("Cache flushed")
            return True
        except (RedisError, Exception) as e:
            logger.warning("Cache FLUSH error", error=str(e))
            return False


def get_redis_cache() -> "RedisCache | None":
    """Return the global RedisCache instance, or None if not initialized."""
    return _cache


async def init_redis_cache(settings: Settings | None = None) -> RedisCache:
    """Create, connect, and register the global cache. Called at server startup.

    Args:
        settings: Settings object (optional, defaults to project settings)

    Returns:
        Connected RedisCache instance
    """
    global _cache

    s = settings or get_settings()
    _cache = RedisCache(
        redis_url=s.redis_url,
        db=s.redis_db,
        password=s.redis_password,
    )
    if s.redis_enabled:
        await _cache.start()

    return _cache


async def close_redis_cache() -> None:
    """Disconnect and unregister the global cache. Called at server shutdown."""
    global _cache
    if _cache:
        await _cache.close()
        _cache = None
