"""Tests for PokéAPI client."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
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
    # Create async mock that properly handles awaitable responses
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = sample_pokemon_response
    
    # Mock the _make_request method directly to avoid httpx complexity
    with patch.object(api_client, '_make_request', new_callable=AsyncMock) as mock_request:
        mock_request.return_value = sample_pokemon_response
        
        pokemon = await api_client.get_pokemon("pikachu")
        
        assert pokemon.name == "pikachu"
        assert pokemon.id == 25
        assert len(pokemon.types) == 1
        assert pokemon.types[0].type["name"] == "electric"
        mock_request.assert_called_once_with("pokemon/pikachu")


@pytest.mark.asyncio
async def test_get_pokemon_not_found(api_client):
    """Test Pokemon not found error."""
    # Mock _make_request to raise the appropriate exception
    with patch.object(api_client, '_make_request', new_callable=AsyncMock) as mock_request:
        mock_request.side_effect = PokemonNotFoundError("Pokemon not found")
        
        with pytest.raises(PokemonNotFoundError):
            await api_client.get_pokemon("nonexistent")


@pytest.mark.asyncio
async def test_get_pokemon_rate_limit(api_client):
    """Test rate limit error handling."""
    # Mock _make_request to raise rate limit exception
    with patch.object(api_client, '_make_request', new_callable=AsyncMock) as mock_request:
        mock_request.side_effect = PokemonAPIRateLimitError("Rate limit exceeded")
        
        with pytest.raises(PokemonAPIRateLimitError):
            await api_client.get_pokemon("pikachu")


@pytest.mark.asyncio
async def test_get_pokemon_timeout(api_client):
    """Test timeout error handling."""
    # Mock _make_request to raise timeout exception
    with patch.object(api_client, '_make_request', new_callable=AsyncMock) as mock_request:
        mock_request.side_effect = PokemonAPITimeoutError("Request timeout")
        
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
    
    # Mock _make_request directly
    with patch.object(api_client, '_make_request', new_callable=AsyncMock) as mock_request:
        mock_request.return_value = search_response
        
        result = await api_client.search_pokemon(limit=2)
        
        assert result.count == 1302
        assert len(result.results) == 2
        assert result.results[0]["name"] == "bulbasaur"
        mock_request.assert_called_once_with("pokemon?limit=2&offset=0")


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
    
    # Mock _make_request directly
    with patch.object(api_client, '_make_request', new_callable=AsyncMock) as mock_request:
        mock_request.return_value = type_response
        
        result = await api_client.get_type_info("electric")
        
        assert result["name"] == "electric"
        assert "damage_relations" in result
        mock_request.assert_called_once_with("type/electric")


@pytest.mark.asyncio
async def test_get_multiple_pokemon(api_client, sample_pokemon_response):
    """Test concurrent Pokemon retrieval."""
    # Mock get_pokemon method directly for cleaner testing
    with patch.object(api_client, 'get_pokemon', new_callable=AsyncMock) as mock_get_pokemon:
        # Create mock Pokemon objects
        from src.models.pokemon_models import Pokemon
        mock_pokemon = Pokemon(**sample_pokemon_response)
        mock_get_pokemon.return_value = mock_pokemon
        
        pokemon_list = await api_client.get_multiple_pokemon(["pikachu", "charizard"])
        
        assert len(pokemon_list) == 2
        for pokemon in pokemon_list:
            assert pokemon.name == "pikachu"  # Same response for both
        
        # Verify that get_pokemon was called for each Pokemon
        assert mock_get_pokemon.call_count == 2
