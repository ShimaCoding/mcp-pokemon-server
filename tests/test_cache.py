"""Tests for the Redis cache module."""

from unittest.mock import AsyncMock, patch

import pytest
from redis.exceptions import RedisError

from src.cache.decorators import cached
from src.cache.redis_cache import CacheMetrics, RedisCache


@pytest.fixture
def redis_cache() -> RedisCache:
    """Provide a RedisCache instance for testing."""
    cache = RedisCache(
        redis_url="redis://localhost:6379",
        db=0,
        password=None,
    )
    return cache


@pytest.fixture
def available_cache(redis_cache: RedisCache) -> RedisCache:
    """Provide a RedisCache with a mocked available Redis client."""
    mock_client = AsyncMock()
    redis_cache.client = mock_client
    redis_cache._available = True
    return redis_cache


class TestCacheMetrics:
    def test_initial_state(self) -> None:
        metrics = CacheMetrics()
        assert metrics.hits == 0
        assert metrics.misses == 0
        assert metrics.errors == 0

    def test_hit_rate_zero_with_no_ops(self) -> None:
        metrics = CacheMetrics()
        assert metrics.hit_rate() == 0.0

    def test_hit_rate_calculation(self) -> None:
        metrics = CacheMetrics()
        metrics.hits = 3
        metrics.misses = 1
        assert metrics.hit_rate() == 75.0

    def test_repr(self) -> None:
        metrics = CacheMetrics()
        metrics.hits = 1
        metrics.misses = 1
        assert "50.0%" in repr(metrics)


class TestRedisCacheInit:
    def test_default_initialization(self, redis_cache: RedisCache) -> None:
        assert redis_cache.redis_url == "redis://localhost:6379"
        assert redis_cache.db == 0
        assert redis_cache.password is None
        assert redis_cache.client is None
        assert redis_cache._available is False

    def test_with_password(self) -> None:
        cache = RedisCache(password="secret")
        assert cache.password == "secret"


class TestRedisCacheStart:
    async def test_start_success(self, redis_cache: RedisCache) -> None:
        mock_redis = AsyncMock()
        with patch(
            "src.cache.redis_cache.redis_async.from_url", return_value=mock_redis
        ):
            await redis_cache.start()
        assert redis_cache._available is True
        mock_redis.ping.assert_called_once()

    async def test_start_connection_error_graceful(
        self, redis_cache: RedisCache
    ) -> None:
        """If Redis is unavailable, cache starts without failing."""
        with patch(
            "src.cache.redis_cache.redis_async.from_url",
            side_effect=ConnectionError("Redis unavailable"),
        ):
            await redis_cache.start()  # Should not raise

        assert redis_cache._available is False

    async def test_start_ping_fails_graceful(self, redis_cache: RedisCache) -> None:
        """If ping fails, cache is unavailable but no exception."""
        mock_redis = AsyncMock()
        mock_redis.ping.side_effect = Exception("Ping failed")
        with patch(
            "src.cache.redis_cache.redis_async.from_url", return_value=mock_redis
        ):
            await redis_cache.start()

        assert redis_cache._available is False


class TestRedisCacheClose:
    async def test_close_success(self, available_cache: RedisCache) -> None:
        await available_cache.close()
        available_cache.client.close.assert_called_once()  # type: ignore[union-attr]
        assert available_cache._available is False

    async def test_close_no_client(self, redis_cache: RedisCache) -> None:
        """Close without client does not raise."""
        await redis_cache.close()  # Should not raise


class TestRedisCacheGet:
    async def test_get_hit(self, available_cache: RedisCache) -> None:
        available_cache.client.get.return_value = '{"name": "pikachu"}'  # type: ignore[union-attr]
        result = await available_cache.get("pokemon:pikachu")
        assert result == {"name": "pikachu"}
        assert available_cache.metrics.hits == 1
        assert available_cache.metrics.misses == 0

    async def test_get_miss(self, available_cache: RedisCache) -> None:
        available_cache.client.get.return_value = None  # type: ignore[union-attr]
        result = await available_cache.get("pokemon:pikachu")
        assert result is None
        assert available_cache.metrics.misses == 1
        assert available_cache.metrics.hits == 0

    async def test_get_unavailable_returns_none(self, redis_cache: RedisCache) -> None:
        result = await redis_cache.get("pokemon:pikachu")
        assert result is None

    async def test_get_redis_error_graceful(self, available_cache: RedisCache) -> None:
        available_cache.client.get.side_effect = RedisError("Redis error")  # type: ignore[union-attr]
        result = await available_cache.get("pokemon:pikachu")
        assert result is None
        assert available_cache.metrics.errors == 1


class TestRedisCacheSet:
    async def test_set_success(self, available_cache: RedisCache) -> None:
        available_cache.client.setex.return_value = True  # type: ignore[union-attr]
        result = await available_cache.set(
            "pokemon:pikachu", {"name": "pikachu"}, ttl=3600
        )
        assert result is True
        available_cache.client.setex.assert_called_once()  # type: ignore[union-attr]

    async def test_set_unavailable_returns_false(self, redis_cache: RedisCache) -> None:
        result = await redis_cache.set("key", {"data": "value"})
        assert result is False

    async def test_set_redis_error_returns_false(
        self, available_cache: RedisCache
    ) -> None:
        available_cache.client.setex.side_effect = RedisError("Write error")  # type: ignore[union-attr]
        result = await available_cache.set("key", {"data": "value"})
        assert result is False
        assert available_cache.metrics.errors == 1


class TestRedisCacheDelete:
    async def test_delete_existing_key(self, available_cache: RedisCache) -> None:
        available_cache.client.delete.return_value = 1  # type: ignore[union-attr]
        result = await available_cache.delete("pokemon:pikachu")
        assert result is True

    async def test_delete_missing_key(self, available_cache: RedisCache) -> None:
        available_cache.client.delete.return_value = 0  # type: ignore[union-attr]
        result = await available_cache.delete("pokemon:notexist")
        assert result is False

    async def test_delete_unavailable(self, redis_cache: RedisCache) -> None:
        result = await redis_cache.delete("key")
        assert result is False


class TestRedisCacheExists:
    async def test_exists_true(self, available_cache: RedisCache) -> None:
        available_cache.client.exists.return_value = 1  # type: ignore[union-attr]
        result = await available_cache.exists("pokemon:pikachu")
        assert result is True

    async def test_exists_false(self, available_cache: RedisCache) -> None:
        available_cache.client.exists.return_value = 0  # type: ignore[union-attr]
        result = await available_cache.exists("pokemon:notexist")
        assert result is False

    async def test_exists_unavailable(self, redis_cache: RedisCache) -> None:
        result = await redis_cache.exists("key")
        assert result is False


class TestCachedDecorator:
    async def test_decorator_caches_result(self) -> None:
        """Decorator stores result in cache on first call."""
        mock_cache = AsyncMock()
        mock_cache._available = True
        mock_cache.get.return_value = None  # Cache miss

        class FakeClient:
            @cached(ttl=60, key_prefix="test")
            async def fetch(self, name: str) -> dict:
                return {"name": name}

        client = FakeClient()

        with patch("src.cache.redis_cache._cache", mock_cache):
            result = await client.fetch("pikachu")

        assert result == {"name": "pikachu"}
        mock_cache.set.assert_called_once()

    async def test_decorator_returns_cached_value(self) -> None:
        """Decorator returns cached value without calling original function."""
        cached_data = {"name": "pikachu", "from_cache": True}
        mock_cache = AsyncMock()
        mock_cache._available = True
        mock_cache.get.return_value = cached_data

        call_count = 0

        class FakeClient:
            @cached(ttl=60, key_prefix="test")
            async def fetch(self, name: str) -> dict:
                nonlocal call_count
                call_count += 1
                return {"name": name, "from_cache": False}

        client = FakeClient()

        with patch("src.cache.redis_cache._cache", mock_cache):
            result = await client.fetch("pikachu")

        assert result == cached_data
        assert call_count == 0  # Original function NOT called

    async def test_decorator_fallback_when_cache_unavailable(self) -> None:
        """Decorator executes original function when cache is unavailable."""
        with patch("src.cache.redis_cache._cache", None):

            class FakeClient:
                @cached(ttl=60, key_prefix="test")
                async def fetch(self, name: str) -> dict:
                    return {"name": name}

            client = FakeClient()
            result = await client.fetch("pikachu")

        assert result == {"name": "pikachu"}

    async def test_decorator_key_generation(self) -> None:
        """Decorator generates expected cache key from prefix and args."""
        mock_cache = AsyncMock()
        mock_cache._available = True
        mock_cache.get.return_value = None

        class FakeClient:
            @cached(ttl=60, key_prefix="pokemon")
            async def fetch(self, identifier: str) -> dict:
                return {"id": identifier}

        client = FakeClient()

        with patch("src.cache.redis_cache._cache", mock_cache):
            await client.fetch("pikachu")

        # Key should be "pokemon:pikachu"
        mock_cache.get.assert_called_with("pokemon:pikachu")

    async def test_decorator_handles_pydantic_model(self) -> None:
        """Decorator serializes Pydantic models before caching."""
        from pydantic import BaseModel

        class PokemonModel(BaseModel):
            name: str
            id: int

        mock_cache = AsyncMock()
        mock_cache._available = True
        mock_cache.get.return_value = None

        class FakeClient:
            @cached(ttl=60, key_prefix="pokemon")
            async def fetch(self, name: str) -> PokemonModel:
                return PokemonModel(name=name, id=1)

        client = FakeClient()

        with patch("src.cache.redis_cache._cache", mock_cache):
            result = await client.fetch("pikachu")

        assert isinstance(result, PokemonModel)
        # Verify set was called with serialized dict
        call_args = mock_cache.set.call_args
        assert call_args[0][1] == {"name": "pikachu", "id": 1}
