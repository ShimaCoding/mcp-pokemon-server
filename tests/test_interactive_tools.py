"""Tests for interactive elicitation tools."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.clients.pokeapi_client import PokemonNotFoundError
from src.tools.interactive_tools import (
    ElicitationState,
    _analyze_pokemon_for_role,
    _get_pokemon_suggestions_by_criteria,
    build_pokemon_team_elicit,
    create_elicit_response,
    get_pokemon_info_elicit,
    suggest_pokemon_by_criteria_elicit,
)


class TestElicitationState:
    """Test the ElicitationState helper class."""

    def test_elicitation_state_basic_operations(self):
        """Test basic get/set operations."""
        state = ElicitationState({})

        # Test get with default
        assert state.get("nonexistent") is None
        assert state.get("nonexistent", "default") == "default"

        # Test set and get
        state.set("key", "value")
        assert state.get("key") == "value"

        # Test update
        state.update({"key2": "value2", "key3": "value3"})
        assert state.get("key2") == "value2"
        assert state.get("key3") == "value3"

        # Test clear
        state.clear()
        assert state.get("key") is None

    def test_elicitation_state_with_initial_data(self):
        """Test ElicitationState with initial data."""
        initial_data = {"existing": "data"}
        state = ElicitationState(initial_data)

        assert state.get("existing") == "data"
        state.set("new", "value")
        assert state.get("new") == "value"


class TestCreateElicitResponse:
    """Test the create_elicit_response helper."""

    def test_create_elicit_response_structure(self):
        """Test that create_elicit_response creates proper structure."""
        prompt = "Test prompt"
        state = {"key": "value"}

        result = create_elicit_response(prompt, state)

        assert result.content[0]["type"] == "text"
        assert "🤖 Test prompt" in result.content[0]["text"]
        assert result.elicit["prompt"] == prompt
        assert result.elicit["state"] == state


class TestGetPokemonInfoElicit:
    """Test the simple Pokemon info elicitation tool."""

    @pytest.mark.asyncio
    async def test_no_pokemon_name_triggers_elicitation(self):
        """Test that missing Pokemon name triggers elicitation."""
        result = await get_pokemon_info_elicit()

        assert result.elicit is not None
        assert "¿De qué Pokémon quieres saber información?" in result.elicit["prompt"]

    @pytest.mark.asyncio
    async def test_pokemon_name_from_parameter(self):
        """Test providing Pokemon name directly as parameter."""
        mock_pokemon = MagicMock()
        mock_pokemon.name = "pikachu"
        mock_pokemon.id = 25
        mock_pokemon.height_meters = 0.4
        mock_pokemon.weight_kg = 6.0
        mock_pokemon.type_names = ["electric"]
        mock_pokemon.base_experience = 112
        mock_pokemon.stat_dict = {
            "hp": 35,
            "attack": 55,
            "defense": 40,
            "special-attack": 50,
            "special-defense": 50,
            "speed": 90,
        }
        mock_pokemon.abilities = [
            MagicMock(ability={"name": "static"}, is_hidden=False)
        ]

        with patch("src.tools.interactive_tools.get_pokemon_client") as mock_client:
            mock_client.return_value.get_pokemon = AsyncMock(return_value=mock_pokemon)

            result = await get_pokemon_info_elicit(pokemon_name="pikachu")

            assert result.elicit is None  # No elicitation needed
            assert "Pikachu" in result.content[0]["text"]
            assert "#25" in result.content[0]["text"]

    @pytest.mark.asyncio
    async def test_pokemon_name_from_state(self):
        """Test getting Pokemon name from elicitation state."""
        state = {"pokemon_name": "charizard"}

        mock_pokemon = MagicMock()
        mock_pokemon.name = "charizard"
        mock_pokemon.id = 6
        mock_pokemon.height_meters = 1.7
        mock_pokemon.weight_kg = 90.5
        mock_pokemon.type_names = ["fire", "flying"]
        mock_pokemon.base_experience = 267
        mock_pokemon.stat_dict = {
            "hp": 78,
            "attack": 84,
            "defense": 78,
            "special-attack": 109,
            "special-defense": 85,
            "speed": 100,
        }
        mock_pokemon.abilities = [MagicMock(ability={"name": "blaze"}, is_hidden=False)]

        with patch("src.tools.interactive_tools.get_pokemon_client") as mock_client:
            mock_client.return_value.get_pokemon = AsyncMock(return_value=mock_pokemon)

            result = await get_pokemon_info_elicit(state=state)

            assert result.elicit is None
            assert "Charizard" in result.content[0]["text"]

    @pytest.mark.asyncio
    async def test_pokemon_not_found_triggers_re_elicitation(self):
        """Test that Pokemon not found triggers re-elicitation."""
        with patch("src.tools.interactive_tools.get_pokemon_client") as mock_client:
            mock_client.return_value.get_pokemon = AsyncMock(
                side_effect=PokemonNotFoundError("not found")
            )

            result = await get_pokemon_info_elicit(pokemon_name="fakemon")

            assert result.elicit is not None
            assert "No encontré información para 'fakemon'" in result.elicit["prompt"]
            assert result.elicit["state"] == {}  # State reset on error

    @pytest.mark.asyncio
    async def test_api_error_triggers_re_elicitation(self):
        """Test that API errors trigger re-elicitation."""
        with patch("src.tools.interactive_tools.get_pokemon_client") as mock_client:
            mock_client.return_value.get_pokemon = AsyncMock(
                side_effect=Exception("API error")
            )

            result = await get_pokemon_info_elicit(pokemon_name="pikachu")

            assert result.elicit is not None
            assert "Ocurrió un error al buscar 'pikachu'" in result.elicit["prompt"]


class TestBuildPokemonTeamElicit:
    """Test the Pokemon team building elicitation tool."""

    @pytest.mark.asyncio
    async def test_empty_team_starts_elicitation(self):
        """Test that empty team starts elicitation process."""
        result = await build_pokemon_team_elicit()

        assert result.elicit is not None
        assert "Construyamos tu equipo Pokémon de 3" in result.elicit["prompt"]
        assert "Pokémon #1" in result.elicit["prompt"]

    @pytest.mark.asyncio
    async def test_adding_first_pokemon_to_team(self):
        """Test adding the first Pokemon to the team."""
        mock_pokemon = MagicMock()
        mock_pokemon.name = "pikachu"
        mock_pokemon.id = 25
        mock_pokemon.type_names = ["electric"]
        mock_pokemon.stat_dict = {"hp": 35, "attack": 55, "defense": 40}

        with patch("src.tools.interactive_tools.get_pokemon_client") as mock_client:
            mock_client.return_value.get_pokemon = AsyncMock(return_value=mock_pokemon)

            result = await build_pokemon_team_elicit(pokemon_name="pikachu")

            assert result.elicit is not None
            assert "Pokémon #2" in result.elicit["prompt"]
            assert "1. Pikachu" in result.elicit["prompt"]  # Shows current team

    @pytest.mark.asyncio
    async def test_duplicate_pokemon_rejected(self):
        """Test that duplicate Pokemon are rejected."""
        existing_team = [
            {"name": "pikachu", "id": 25, "types": ["electric"], "total_stats": 320}
        ]
        state = {"team": existing_team}

        result = await build_pokemon_team_elicit(pokemon_name="pikachu", state=state)

        assert result.elicit is not None
        assert "Ya tienes a Pikachu en tu equipo" in result.elicit["prompt"]

    @pytest.mark.asyncio
    async def test_invalid_pokemon_rejected(self):
        """Test that invalid Pokemon names are rejected."""
        with patch("src.tools.interactive_tools.get_pokemon_client") as mock_client:
            mock_client.return_value.get_pokemon = AsyncMock(
                side_effect=PokemonNotFoundError("not found")
            )

            result = await build_pokemon_team_elicit(pokemon_name="fakemon")

            assert result.elicit is not None
            assert "'fakemon' no es un Pokémon válido" in result.elicit["prompt"]

    @pytest.mark.asyncio
    async def test_complete_team_shows_analysis(self):
        """Test that completing a team shows final analysis."""
        # Mock three different Pokemon
        mock_pokemon1 = MagicMock()
        mock_pokemon1.name = "pikachu"
        mock_pokemon1.id = 25
        mock_pokemon1.type_names = ["electric"]
        mock_pokemon1.stat_dict = {
            "hp": 35,
            "attack": 55,
            "defense": 40,
            "special-attack": 50,
            "special-defense": 50,
            "speed": 90,
        }

        existing_team = [
            {"name": "pikachu", "id": 25, "types": ["electric"], "total_stats": 320},
            {
                "name": "charizard",
                "id": 6,
                "types": ["fire", "flying"],
                "total_stats": 534,
            },
        ]
        state = {"team": existing_team}

        with patch("src.tools.interactive_tools.get_pokemon_client") as mock_client:
            mock_client.return_value.get_pokemon = AsyncMock(return_value=mock_pokemon1)

            result = await build_pokemon_team_elicit(
                pokemon_name="blastoise", state=state
            )

            # Should complete the team and show analysis
            assert result.elicit is None
            assert "¡Equipo Pokémon Completo!" in result.content[0]["text"]
            assert "Análisis del Equipo" in result.content[0]["text"]


class TestSuggestPokemonByCriteriaElicit:
    """Test the advanced Pokemon suggestion elicitation tool."""

    @pytest.mark.asyncio
    async def test_no_input_asks_for_type(self):
        """Test that no input triggers type question."""
        result = await suggest_pokemon_by_criteria_elicit()

        assert result.elicit is not None
        assert "¿Qué tipo de Pokémon prefieres?" in result.elicit["prompt"]

    @pytest.mark.asyncio
    async def test_valid_type_input_asks_for_role(self):
        """Test that valid type input progresses to role question."""
        result = await suggest_pokemon_by_criteria_elicit(user_input="fire")

        assert result.elicit is not None
        assert "¿Qué rol buscas?" in result.elicit["prompt"]
        assert "ataque" in result.elicit["prompt"]
        assert "defensa" in result.elicit["prompt"]

    @pytest.mark.asyncio
    async def test_spanish_type_translation(self):
        """Test that Spanish type names are translated correctly."""
        result = await suggest_pokemon_by_criteria_elicit(user_input="fuego")

        assert result.elicit is not None
        assert "¿Qué rol buscas?" in result.elicit["prompt"]
        # State should contain "fire", not "fuego"
        assert result.elicit["state"]["type"] == "fire"

    @pytest.mark.asyncio
    async def test_invalid_type_asks_again(self):
        """Test that invalid type triggers re-asking."""
        result = await suggest_pokemon_by_criteria_elicit(user_input="invalidtype")

        assert result.elicit is not None
        assert "'invalidtype' no es un tipo válido" in result.elicit["prompt"]

    @pytest.mark.asyncio
    async def test_invalid_role_asks_again(self):
        """Test that invalid role triggers re-asking."""
        state = {"type": "fire"}
        result = await suggest_pokemon_by_criteria_elicit(
            user_input="invalidrole", state=state
        )

        assert result.elicit is not None
        assert "'invalidrole' no es un rol válido" in result.elicit["prompt"]

    @pytest.mark.asyncio
    async def test_generate_suggestion_flow(self):
        """Test the suggestion generation flow."""
        state = {"type": "fire", "role": "ataque"}

        # Mock the suggestion generation
        mock_suggestions = [
            {
                "name": "charizard",
                "id": 6,
                "types": ["fire", "flying"],
                "highlight": "Ataque: 84",
                "reason": "Excelente para roles ofensivos con alto daño.",
                "total_stats": 534,
            }
        ]

        with patch(
            "src.tools.interactive_tools._get_pokemon_suggestions_by_criteria"
        ) as mock_suggestions_func:
            mock_suggestions_func.return_value = mock_suggestions

            result = await suggest_pokemon_by_criteria_elicit(state=state)

            assert result.elicit is not None
            assert "Te sugiero **Charizard**" in result.elicit["prompt"]
            assert "¿Te gusta esta opción?" in result.elicit["prompt"]

    @pytest.mark.asyncio
    async def test_accept_suggestion(self):
        """Test accepting a suggestion."""
        state = {
            "type": "fire",
            "role": "ataque",
            "current_suggestion": {
                "name": "charizard",
                "id": 6,
                "types": ["fire", "flying"],
                "highlight": "Ataque: 84",
                "reason": "Excelente para roles ofensivos con alto daño.",
            },
        }

        result = await suggest_pokemon_by_criteria_elicit(user_input="sí", state=state)

        assert result.elicit is None  # No more elicitation
        assert "¡Excelente elección!" in result.content[0]["text"]
        assert "Charizard" in result.content[0]["text"]

    @pytest.mark.asyncio
    async def test_reject_suggestion_with_alternatives(self):
        """Test rejecting a suggestion when alternatives exist."""
        state = {
            "type": "fire",
            "role": "ataque",
            "current_suggestion": {
                "name": "charizard",
                "id": 6,
                "types": ["fire", "flying"],
                "highlight": "Ataque: 84",
                "reason": "Excelente para roles ofensivos.",
            },
            "available_suggestions": [
                {
                    "name": "arcanine",
                    "id": 59,
                    "types": ["fire"],
                    "highlight": "Ataque: 110",
                    "reason": "Gran atacante físico.",
                }
            ],
        }

        result = await suggest_pokemon_by_criteria_elicit(user_input="no", state=state)

        assert result.elicit is not None
        assert "Te sugiero **Arcanine**" in result.elicit["prompt"]

    @pytest.mark.asyncio
    async def test_reject_suggestion_no_alternatives(self):
        """Test rejecting suggestion when no alternatives exist."""
        state = {
            "type": "fire",
            "role": "ataque",
            "current_suggestion": {
                "name": "charizard",
                "id": 6,
                "types": ["fire", "flying"],
                "highlight": "Ataque: 84",
                "reason": "Excelente para roles ofensivos.",
            },
            "available_suggestions": [],
            "rejected_suggestions": [],
        }

        result = await suggest_pokemon_by_criteria_elicit(user_input="no", state=state)

        assert result.elicit is not None
        assert "No tengo más sugerencias" in result.elicit["prompt"]

    @pytest.mark.asyncio
    async def test_restart_command(self):
        """Test the restart command."""
        state = {"type": "fire", "role": "ataque"}

        result = await suggest_pokemon_by_criteria_elicit(
            user_input="reiniciar", state=state
        )

        assert result.elicit is not None
        assert "¡Empecemos de nuevo!" in result.elicit["prompt"]
        assert result.elicit["state"] == {}  # State cleared


class TestHelperFunctions:
    """Test helper functions for Pokemon suggestions."""

    @pytest.mark.asyncio
    async def test_get_pokemon_suggestions_by_criteria(self):
        """Test getting Pokemon suggestions by criteria."""
        # Mock the client and type data
        mock_type_data = {
            "pokemon": [
                {"pokemon": {"name": "charizard"}},
                {"pokemon": {"name": "arcanine"}},
            ]
        }

        mock_pokemon = MagicMock()
        mock_pokemon.name = "charizard"
        mock_pokemon.id = 6
        mock_pokemon.type_names = ["fire", "flying"]
        mock_pokemon.stat_dict = {
            "hp": 78,
            "attack": 84,
            "defense": 78,
            "special-attack": 109,
            "special-defense": 85,
            "speed": 100,
        }

        with patch("src.tools.interactive_tools.get_pokemon_client") as mock_client:
            mock_client.return_value.get_type_info = AsyncMock(
                return_value=mock_type_data
            )
            mock_client.return_value.get_pokemon = AsyncMock(return_value=mock_pokemon)

            with patch(
                "src.tools.interactive_tools._analyze_pokemon_for_role"
            ) as mock_analyze:
                mock_analyze.return_value = {
                    "name": "charizard",
                    "id": 6,
                    "types": ["fire", "flying"],
                    "highlight": "Ataque: 84",
                    "reason": "Excelente para roles ofensivos.",
                }

                suggestions = await _get_pokemon_suggestions_by_criteria(
                    "fire", "ataque"
                )

                assert len(suggestions) >= 1
                assert suggestions[0]["name"] == "charizard"

    def test_analyze_pokemon_for_role_attack(self):
        """Test analyzing Pokemon for attack role."""
        mock_pokemon = MagicMock()
        mock_pokemon.name = "charizard"
        mock_pokemon.id = 6
        mock_pokemon.type_names = ["fire", "flying"]

        stats = {
            "hp": 78,
            "attack": 84,
            "defense": 78,
            "special-attack": 109,
            "special-defense": 85,
            "speed": 100,
        }

        result = _analyze_pokemon_for_role(mock_pokemon, "ataque", stats)

        assert result is not None
        assert result["name"] == "charizard"
        assert result["role"] == "ataque"
        assert "Ataque: 109" in result["highlight"]  # Should pick special-attack

    def test_analyze_pokemon_for_role_defense(self):
        """Test analyzing Pokemon for defense role."""
        mock_pokemon = MagicMock()
        mock_pokemon.name = "blastoise"
        mock_pokemon.id = 9
        mock_pokemon.type_names = ["water"]

        stats = {
            "hp": 79,
            "attack": 83,
            "defense": 100,
            "special-attack": 85,
            "special-defense": 105,
            "speed": 78,
        }

        result = _analyze_pokemon_for_role(mock_pokemon, "defensa", stats)

        assert result is not None
        assert result["name"] == "blastoise"
        assert "Defensa: 105" in result["highlight"]

    def test_analyze_pokemon_for_role_speed(self):
        """Test analyzing Pokemon for speed role."""
        mock_pokemon = MagicMock()
        mock_pokemon.name = "crobat"
        mock_pokemon.id = 169
        mock_pokemon.type_names = ["poison", "flying"]

        stats = {
            "hp": 85,
            "attack": 90,
            "defense": 80,
            "special-attack": 70,
            "special-defense": 80,
            "speed": 130,
        }

        result = _analyze_pokemon_for_role(mock_pokemon, "velocidad", stats)

        assert result is not None
        assert result["name"] == "crobat"
        assert "Velocidad: 130" in result["highlight"]

    def test_analyze_pokemon_for_role_weak_pokemon_rejected(self):
        """Test that weak Pokemon are rejected."""
        mock_pokemon = MagicMock()
        mock_pokemon.name = "caterpie"
        mock_pokemon.id = 10
        mock_pokemon.type_names = ["bug"]

        # Very weak stats
        stats = {
            "hp": 45,
            "attack": 30,
            "defense": 35,
            "special-attack": 20,
            "special-defense": 20,
            "speed": 45,
        }

        result = _analyze_pokemon_for_role(mock_pokemon, "ataque", stats)

        assert result is None  # Should be rejected for being too weak

    def test_analyze_pokemon_for_role_doesnt_fit(self):
        """Test Pokemon that doesn't fit the role."""
        mock_pokemon = MagicMock()
        mock_pokemon.name = "chansey"
        mock_pokemon.id = 113
        mock_pokemon.type_names = ["normal"]

        # High HP but low attack stats
        stats = {
            "hp": 250,
            "attack": 5,
            "defense": 5,
            "special-attack": 35,
            "special-defense": 105,
            "speed": 50,
        }

        result = _analyze_pokemon_for_role(mock_pokemon, "ataque", stats)

        assert result is None  # Should be rejected for low attack


if __name__ == "__main__":
    pytest.main([__file__])
