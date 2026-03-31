"""Tests for Pokemon tools."""

from unittest.mock import AsyncMock, patch

import pytest

from src.clients.pokeapi_client import PokemonNotFoundError
from src.models.pokemon_models import (
    Pokemon,
    PokemonAbility,
    PokemonSpecies,
    PokemonSprites,
    PokemonStat,
    PokemonType,
)
from src.tools.pokemon_tools import (
    analyze_pokemon_stats,
    get_pokedex_entry,
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


# ---------------------------------------------------------------------------
# get_pokedex_entry tests
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_pokemon_with_species():
    """Pikachu Pokemon model with species URL populated."""
    return Pokemon(
        id=25,
        name="pikachu",
        height=4,
        weight=60,
        base_experience=112,
        species={
            "name": "pikachu",
            "url": "https://pokeapi.co/api/v2/pokemon-species/25/",
        },
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


SAMPLE_EVOLUTION_CHAIN = {
    "id": 10,
    "chain": {
        "is_baby": True,
        "species": {
            "name": "pichu",
            "url": "https://pokeapi.co/api/v2/pokemon-species/172/",
        },
        "evolution_details": [],
        "evolves_to": [
            {
                "is_baby": False,
                "species": {
                    "name": "pikachu",
                    "url": "https://pokeapi.co/api/v2/pokemon-species/25/",
                },
                "evolution_details": [
                    {
                        "trigger": {"name": "level-up", "url": ""},
                        "min_happiness": 220,
                        "gender": None,
                        "held_item": None,
                        "item": None,
                        "known_move": None,
                        "known_move_type": None,
                        "location": None,
                        "min_affection": None,
                        "min_beauty": None,
                        "min_level": None,
                        "needs_overworld_rain": False,
                        "relative_physical_stats": None,
                        "time_of_day": "",
                        "turn_upside_down": False,
                    }
                ],
                "evolves_to": [
                    {
                        "is_baby": False,
                        "species": {
                            "name": "raichu",
                            "url": "https://pokeapi.co/api/v2/pokemon-species/26/",
                        },
                        "evolution_details": [
                            {
                                "trigger": {"name": "use-item", "url": ""},
                                "item": {"name": "thunder-stone", "url": ""},
                                "gender": None,
                                "held_item": None,
                                "known_move": None,
                                "known_move_type": None,
                                "location": None,
                                "min_affection": None,
                                "min_beauty": None,
                                "min_happiness": None,
                                "min_level": None,
                                "needs_overworld_rain": False,
                                "relative_physical_stats": None,
                                "time_of_day": "",
                                "turn_upside_down": False,
                            }
                        ],
                        "evolves_to": [],
                    }
                ],
            }
        ],
    },
}


@pytest.fixture
def sample_species():
    """Pikachu PokemonSpecies model."""
    return PokemonSpecies(
        id=25,
        name="pikachu",
        color={"name": "yellow", "url": "https://pokeapi.co/api/v2/pokemon-color/10/"},
        generation={
            "name": "generation-i",
            "url": "https://pokeapi.co/api/v2/generation/1/",
        },
        habitat={
            "name": "forest",
            "url": "https://pokeapi.co/api/v2/pokemon-habitat/4/",
        },
        is_legendary=False,
        is_mythical=False,
        capture_rate=190,
        genera=[
            {"genus": "Ratón eléctrico", "language": {"name": "es", "url": ""}},
            {"genus": "Mouse Pokémon", "language": {"name": "en", "url": ""}},
        ],
        gender_rate=4,
        base_happiness=70,
        growth_rate={"name": "medium", "url": ""},
        egg_groups=[{"name": "field", "url": ""}, {"name": "fairy", "url": ""}],
        shape={"name": "quadruped", "url": ""},
        evolution_chain={"url": "https://pokeapi.co/api/v2/evolution-chain/10/"},
        flavor_text_entries=[
            {
                "flavor_text": "Cuando varios de estos POKEMON se juntan, su electricidad puede provocar tormentas.",
                "language": {
                    "name": "es",
                    "url": "https://pokeapi.co/api/v2/language/7/",
                },
                "version": {"name": "x", "url": ""},
            },
            {
                "flavor_text": "When several of these POKéMON gather, their electricity can cause lightning storms.",
                "language": {
                    "name": "en",
                    "url": "https://pokeapi.co/api/v2/language/9/",
                },
                "version": {"name": "x", "url": ""},
            },
        ],
    )


@pytest.mark.asyncio
async def test_get_pokedex_entry_success(sample_pokemon_with_species, sample_species):
    """Test successful Pokédex entry retrieval with full JSON output."""
    import json

    with patch("src.tools.pokemon_tools.get_pokemon_client") as mock_client:
        mock_api_client = AsyncMock()
        mock_api_client.get_pokemon.return_value = sample_pokemon_with_species
        mock_api_client.get_pokemon_species.return_value = sample_species
        mock_api_client.get_evolution_chain = AsyncMock(
            return_value=SAMPLE_EVOLUTION_CHAIN
        )
        mock_client.return_value = mock_api_client

        result = await get_pokedex_entry("pikachu")

        assert not result.is_error
        data = json.loads(result.content[0]["text"])

        # Core fields
        assert data["id"] == 25
        assert data["name"] == "pikachu"
        assert data["types"] == ["electric"]
        assert data["base_stats"]["hp"] == 35
        assert data["abilities"][0]["name"] == "static"
        assert data["abilities"][0]["is_hidden"] is False
        assert data["generation"] == "I"
        assert data["habitat"] == "forest"
        assert data["is_legendary"] is False
        assert data["is_mythical"] is False
        assert data["capture_rate"] == 190
        # Spanish flavor text should be preferred
        assert len(data["flavor_text"]) == 1
        assert "POKEMON" in data["flavor_text"][0]
        # Species resolution uses the URL, not the pokemon id
        mock_api_client.get_pokemon_species.assert_called_once_with("25")

        # New narrative fields from species
        assert data["genus"] == "Ratón eléctrico"
        assert data["color"] == "yellow"
        assert data["shape"] == "quadruped"
        assert data["gender_rate"] == 4
        assert data["base_happiness"] == 70
        assert data["growth_rate"] == "medium"
        assert data["egg_groups"] == ["field", "fairy"]

        # Evolution chain
        chain = data["evolution_chain"]
        assert chain is not None
        assert chain[0]["name"] == "pichu"
        assert chain[0]["is_baby"] is True
        assert chain[1]["name"] == "pikachu"
        assert chain[1]["via"]["trigger"] == "level-up"
        assert chain[1]["via"]["min_happiness"] == 220
        assert chain[2]["name"] == "raichu"
        assert chain[2]["via"]["trigger"] == "use-item"
        assert chain[2]["via"]["item"] == "thunder-stone"


@pytest.mark.asyncio
async def test_get_pokedex_entry_evolution_chain_failure_is_graceful(
    sample_pokemon_with_species, sample_species
):
    """Evolution chain fetch failure must not fail the whole call."""
    import json

    with patch("src.tools.pokemon_tools.get_pokemon_client") as mock_client:
        mock_api_client = AsyncMock()
        mock_api_client.get_pokemon.return_value = sample_pokemon_with_species
        mock_api_client.get_pokemon_species.return_value = sample_species
        mock_api_client.get_evolution_chain = AsyncMock(
            side_effect=Exception("timeout")
        )
        mock_client.return_value = mock_api_client

        result = await get_pokedex_entry("pikachu")

        assert not result.is_error
        data = json.loads(result.content[0]["text"])
        assert data["evolution_chain"] is None


@pytest.mark.asyncio
async def test_get_pokedex_entry_not_found():
    """Test Pokédex entry for an unknown Pokémon."""
    with patch("src.tools.pokemon_tools.get_pokemon_client") as mock_client:
        mock_api_client = AsyncMock()
        mock_api_client.get_pokemon.side_effect = PokemonNotFoundError("Not found")
        mock_client.return_value = mock_api_client

        result = await get_pokedex_entry("fakemon")

        assert result.is_error
        assert "not found" in result.content[0]["text"].lower()


@pytest.mark.asyncio
async def test_get_pokedex_entry_generic_error():
    """Test Pokédex entry on generic API error."""
    with patch("src.tools.pokemon_tools.get_pokemon_client") as mock_client:
        mock_api_client = AsyncMock()
        mock_api_client.get_pokemon.side_effect = Exception("Network failure")
        mock_client.return_value = mock_api_client

        result = await get_pokedex_entry("pikachu")

        assert result.is_error
        assert "Error retrieving Pok\u00e9dex entry" in result.content[0]["text"]


@pytest.mark.asyncio
async def test_get_pokedex_entry_fallback_to_english(sample_pokemon_with_species):
    """Test that English flavor text is used when Spanish is absent."""
    import json

    species_no_es = PokemonSpecies(
        id=25,
        name="pikachu",
        color={"name": "yellow", "url": ""},
        generation={"name": "generation-i", "url": ""},
        is_legendary=False,
        is_mythical=False,
        capture_rate=190,
        # No evolution_chain → chain fetch skipped, evolution_chain=null in output
        flavor_text_entries=[
            {
                "flavor_text": "It can generate electric attacks from the electric pouches located in both of its cheeks.",
                "language": {"name": "en", "url": ""},
                "version": {"name": "red", "url": ""},
            },
        ],
    )

    with patch("src.tools.pokemon_tools.get_pokemon_client") as mock_client:
        mock_api_client = AsyncMock()
        mock_api_client.get_pokemon.return_value = sample_pokemon_with_species
        mock_api_client.get_pokemon_species.return_value = species_no_es
        mock_client.return_value = mock_api_client

        result = await get_pokedex_entry("pikachu")

        assert not result.is_error
        data = json.loads(result.content[0]["text"])
        assert len(data["flavor_text"]) == 1
        assert "electric pouches" in data["flavor_text"][0]
        assert data["evolution_chain"] is None  # no evolution_chain URL in species
