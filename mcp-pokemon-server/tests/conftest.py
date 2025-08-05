"""Pytest configuration and fixtures for MCP Pokemon Server tests."""

import asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest
from pytest_mock import MockerFixture

from src.config.settings import Settings


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_settings() -> Settings:
    """Provide test settings."""
    return Settings(
        server_host="localhost",
        server_port=8000,
        pokeapi_base_url="https://pokeapi.co/api/v2",
        redis_url="redis://localhost:6379",
        log_level="DEBUG",
        debug=True,
        development_mode=True,
        cache_ttl=60,  # Shorter TTL for tests
    )


@pytest.fixture
async def mock_httpx_client() -> AsyncGenerator[AsyncMock, None]:
    """Provide a mocked httpx client."""
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    yield mock_client


@pytest.fixture
def mock_redis_client(mocker: MockerFixture) -> MagicMock:
    """Provide a mocked Redis client."""
    mock_redis = MagicMock()
    mocker.patch("redis.Redis", return_value=mock_redis)
    return mock_redis


@pytest.fixture
def sample_pokemon_data() -> dict:
    """Provide sample Pokemon data for testing."""
    return {
        "id": 25,
        "name": "pikachu",
        "height": 4,
        "weight": 60,
        "base_experience": 112,
        "types": [
            {
                "slot": 1,
                "type": {
                    "name": "electric",
                    "url": "https://pokeapi.co/api/v2/type/13/"
                }
            }
        ],
        "stats": [
            {
                "base_stat": 35,
                "effort": 0,
                "stat": {
                    "name": "hp",
                    "url": "https://pokeapi.co/api/v2/stat/1/"
                }
            },
            {
                "base_stat": 55,
                "effort": 0,
                "stat": {
                    "name": "attack",
                    "url": "https://pokeapi.co/api/v2/stat/2/"
                }
            },
            {
                "base_stat": 40,
                "effort": 0,
                "stat": {
                    "name": "defense",
                    "url": "https://pokeapi.co/api/v2/stat/3/"
                }
            },
            {
                "base_stat": 50,
                "effort": 0,
                "stat": {
                    "name": "special-attack",
                    "url": "https://pokeapi.co/api/v2/stat/4/"
                }
            },
            {
                "base_stat": 50,
                "effort": 0,
                "stat": {
                    "name": "special-defense",
                    "url": "https://pokeapi.co/api/v2/stat/5/"
                }
            },
            {
                "base_stat": 90,
                "effort": 2,
                "stat": {
                    "name": "speed",
                    "url": "https://pokeapi.co/api/v2/stat/6/"
                }
            }
        ],
        "abilities": [
            {
                "ability": {
                    "name": "static",
                    "url": "https://pokeapi.co/api/v2/ability/9/"
                },
                "is_hidden": False,
                "slot": 1
            },
            {
                "ability": {
                    "name": "lightning-rod",
                    "url": "https://pokeapi.co/api/v2/ability/31/"
                },
                "is_hidden": True,
                "slot": 3
            }
        ],
        "sprites": {
            "front_default": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/25.png",
            "front_shiny": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/shiny/25.png"
        }
    }
