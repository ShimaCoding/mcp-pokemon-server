"""Tests for PokéAPI client."""

import pytest
from unittest.mock import AsyncMock, patch
import httpx

from src.clients.pokeapi_client import (
    PokemonAPIClient,
    PokemonNotFoundError,
    PokemonAPITimeoutError,
    PokemonAPIRateLimitError,
)


@pytest.fixture
def api_client():
    """Create a test API client."""
    return PokemonAPIClient(base_url="https://pokeapi.co/api/v2/", timeout=30)


@pytest.fixture
def sample_pokemon_response():
    """Sample Pokemon API response."""
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
            }
        ],
        "sprites": {
            "front_default": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/25.png"
        }
    }


@pytest.mark.asyncio
async def test_pokemon_client_context_manager():
    """Test client context manager usage."""
    client = PokemonAPIClient()
    
    async with client:
        assert client.client is not None
    
    assert client.client is None


@pytest.mark.asyncio
async def test_get_pokemon_success(api_client, sample_pokemon_response):
    """Test successful Pokemon retrieval."""
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json.return_value = sample_pokemon_response
    
    with patch.object(api_client, 'client') as mock_client:
        mock_client.get.return_value = mock_response
        
        pokemon = await api_client.get_pokemon("pikachu")
        
        assert pokemon.name == "pikachu"
        assert pokemon.id == 25
        assert len(pokemon.types) == 1
        assert pokemon.types[0].type["name"] == "electric"


@pytest.mark.asyncio
async def test_get_pokemon_not_found(api_client):
    """Test Pokemon not found error."""
    mock_response = AsyncMock()
    mock_response.status_code = 404
    
    with patch.object(api_client, 'client') as mock_client:
        mock_client.get.return_value = mock_response
        
        with pytest.raises(PokemonNotFoundError):
            await api_client.get_pokemon("nonexistent")


@pytest.mark.asyncio
async def test_get_pokemon_rate_limit(api_client):
    """Test rate limit error handling."""
    mock_response = AsyncMock()
    mock_response.status_code = 429
    
    with patch.object(api_client, 'client') as mock_client:
        mock_client.get.return_value = mock_response
        
        with pytest.raises(PokemonAPIRateLimitError):
            await api_client.get_pokemon("pikachu")


@pytest.mark.asyncio
async def test_get_pokemon_timeout(api_client):
    """Test timeout error handling."""
    with patch.object(api_client, 'client') as mock_client:
        mock_client.get.side_effect = httpx.TimeoutException("Timeout")
        
        with pytest.raises(PokemonAPITimeoutError):
            await api_client.get_pokemon("pikachu")


@pytest.mark.asyncio
async def test_search_pokemon(api_client):
    """Test Pokemon search."""
    search_response = {
        "count": 1302,
        "results": [
            {"name": "bulbasaur", "url": "https://pokeapi.co/api/v2/pokemon/1/"},
            {"name": "ivysaur", "url": "https://pokeapi.co/api/v2/pokemon/2/"},
        ]
    }
    
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json.return_value = search_response
    
    with patch.object(api_client, 'client') as mock_client:
        mock_client.get.return_value = mock_response
        
        result = await api_client.search_pokemon(limit=2)
        
        assert result.count == 1302
        assert len(result.results) == 2
        assert result.results[0]["name"] == "bulbasaur"


@pytest.mark.asyncio
async def test_get_type_info(api_client):
    """Test type information retrieval."""
    type_response = {
        "id": 13,
        "name": "electric",
        "damage_relations": {
            "double_damage_to": [
                {"name": "water"},
                {"name": "flying"}
            ],
            "half_damage_to": [
                {"name": "electric"},
                {"name": "grass"}
            ],
            "no_damage_to": [
                {"name": "ground"}
            ]
        }
    }
    
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json.return_value = type_response
    
    with patch.object(api_client, 'client') as mock_client:
        mock_client.get.return_value = mock_response
        
        result = await api_client.get_type_info("electric")
        
        assert result["name"] == "electric"
        assert "damage_relations" in result


@pytest.mark.asyncio
async def test_get_multiple_pokemon(api_client, sample_pokemon_response):
    """Test concurrent Pokemon retrieval."""
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json.return_value = sample_pokemon_response
    
    with patch.object(api_client, 'client') as mock_client:
        mock_client.get.return_value = mock_response
        
        pokemon_list = await api_client.get_multiple_pokemon(["pikachu", "charizard"])
        
        assert len(pokemon_list) == 2
        for pokemon in pokemon_list:
            assert pokemon.name == "pikachu"  # Same response for both
