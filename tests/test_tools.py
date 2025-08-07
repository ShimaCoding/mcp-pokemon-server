"""Tests for Pokemon tools."""

from unittest.mock import AsyncMock, patch

import pytest

from src.clients.pokeapi_client import PokemonNotFoundError
from src.models.pokemon_models import (
    Pokemon,
    PokemonAbility,
    PokemonSprites,
    PokemonStat,
    PokemonType,
)
from src.tools.pokemon_tools import (
    analyze_pokemon_stats,
    get_pokemon_info,
    get_type_effectiveness,
    search_pokemon,
)


@pytest.fixture
def sample_pokemon():
    """Sample Pokemon data for testing."""
    return Pokemon(
        id=25,
        name="pikachu",
        height=4,
        weight=60,
        base_experience=112,
        types=[
            PokemonType(
                slot=1,
                type={"name": "electric", "url": "https://pokeapi.co/api/v2/type/13/"},
            )
        ],
        stats=[
            PokemonStat(
                base_stat=35,
                effort=0,
                stat={"name": "hp", "url": "https://pokeapi.co/api/v2/stat/1/"},
            ),
            PokemonStat(
                base_stat=55,
                effort=0,
                stat={"name": "attack", "url": "https://pokeapi.co/api/v2/stat/2/"},
            ),
            PokemonStat(
                base_stat=90,
                effort=2,
                stat={"name": "speed", "url": "https://pokeapi.co/api/v2/stat/6/"},
            ),
        ],
        abilities=[
            PokemonAbility(
                ability={
                    "name": "static",
                    "url": "https://pokeapi.co/api/v2/ability/9/",
                },
                is_hidden=False,
                slot=1,
            )
        ],
        sprites=PokemonSprites(
            front_default="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/25.png"
        ),
    )


@pytest.mark.asyncio
async def test_get_pokemon_info_success(sample_pokemon):
    """Test successful Pokemon info retrieval."""
    with patch("src.tools.pokemon_tools.get_pokemon_client") as mock_client:
        mock_api_client = AsyncMock()
        mock_api_client.get_pokemon.return_value = sample_pokemon
        mock_client.return_value = mock_api_client

        result = await get_pokemon_info("pikachu")

        assert not result.is_error
        assert len(result.content) == 1
        assert "Pikachu" in result.content[0]["text"]
        assert "#25" in result.content[0]["text"]
        assert "electric" in result.content[0]["text"]


@pytest.mark.asyncio
async def test_get_pokemon_info_not_found():
    """Test Pokemon not found error."""
    with patch("src.tools.pokemon_tools.get_pokemon_client") as mock_client:
        mock_api_client = AsyncMock()
        mock_api_client.get_pokemon.side_effect = PokemonNotFoundError("Not found")
        mock_client.return_value = mock_api_client

        result = await get_pokemon_info("nonexistent")

        assert result.is_error
        assert "not found" in result.content[0]["text"].lower()


@pytest.mark.asyncio
async def test_search_pokemon():
    """Test Pokemon search functionality."""
    search_result = {
        "count": 1302,
        "results": [
            {"name": "bulbasaur", "url": "https://pokeapi.co/api/v2/pokemon/1/"},
            {"name": "ivysaur", "url": "https://pokeapi.co/api/v2/pokemon/2/"},
        ],
    }

    with patch("src.tools.pokemon_tools.get_pokemon_client") as mock_client:
        mock_api_client = AsyncMock()
        mock_api_client.search_pokemon.return_value = type(
            "SearchResult", (), search_result
        )
        mock_client.return_value = mock_api_client

        result = await search_pokemon(limit=2)

        assert not result.is_error
        assert "1302" in result.content[0]["text"]
        assert "Bulbasaur" in result.content[0]["text"]


@pytest.mark.asyncio
async def test_get_type_effectiveness():
    """Test type effectiveness retrieval."""
    type_data = {
        "damage_relations": {
            "double_damage_to": [{"name": "water"}, {"name": "flying"}],
            "half_damage_to": [{"name": "electric"}, {"name": "grass"}],
            "no_damage_to": [{"name": "ground"}],
        }
    }

    with patch("src.tools.pokemon_tools.get_pokemon_client") as mock_client:
        mock_api_client = AsyncMock()
        mock_api_client.get_type_info.return_value = type_data
        mock_client.return_value = mock_api_client

        result = await get_type_effectiveness("electric")

        assert not result.is_error
        assert "Electric Type Effectiveness" in result.content[0]["text"]
        assert "Water" in result.content[0]["text"]
        assert "Ground" in result.content[0]["text"]


@pytest.mark.asyncio
async def test_analyze_pokemon_stats(sample_pokemon):
    """Test Pokemon stats analysis."""
    with patch("src.tools.pokemon_tools.get_pokemon_client") as mock_client:
        mock_api_client = AsyncMock()
        mock_api_client.get_pokemon.return_value = sample_pokemon
        mock_client.return_value = mock_api_client

        result = await analyze_pokemon_stats("pikachu")

        assert not result.is_error
        assert "Pikachu Stats Analysis" in result.content[0]["text"]
        assert "Total Base Stats:" in result.content[0]["text"]
        assert "Speed" in result.content[0]["text"]  # Should be highest stat


@pytest.mark.asyncio
async def test_tool_error_handling():
    """Test generic error handling in tools."""
    with patch("src.tools.pokemon_tools.get_pokemon_client") as mock_client:
        mock_api_client = AsyncMock()
        mock_api_client.get_pokemon.side_effect = Exception("API Error")
        mock_client.return_value = mock_api_client

        result = await get_pokemon_info("test")

        assert result.is_error
        assert "Error retrieving Pokemon information" in result.content[0]["text"]
