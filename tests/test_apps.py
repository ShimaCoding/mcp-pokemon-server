"""Tests for the MCP Apps surface: UI-bound tools, widget resources and prompts."""

import json
from unittest.mock import AsyncMock, patch

import pytest
from mcp.types import GetPromptResult, PromptMessage, TextContent

from src.models.pokemon_models import (
    Pokemon,
    PokemonAbility,
    PokemonSprites,
    PokemonStat,
    PokemonType,
)
from src.server.mcp_server import app, battle_prompts
from src.tools.pokemon_tools import (
    analyze_team,
    compare_pokemon,
    pokemon_card,
    stats_entry,
    type_chart,
)
from src.widgets import CARD_URI, SEARCH_URI, STATS_URI, TEAM_URI, TYPES_URI

STAT_NAMES = ["hp", "attack", "defense", "special-attack", "special-defense", "speed"]
UI_TOOLS = {
    "get_pokemon_info": CARD_URI,
    "get_pokedex_entry": CARD_URI,
    "analyze_pokemon_stats": STATS_URI,
    "compare_pokemon": STATS_URI,
    "get_type_effectiveness": TYPES_URI,
    "analyze_team": TEAM_URI,
    "search_pokemon": SEARCH_URI,
}
WIDGET_URIS = sorted(set(UI_TOOLS.values()))


def make_pokemon(pid: int, name: str, types: list[str], stats: list[int]) -> Pokemon:
    return Pokemon(
        id=pid,
        name=name,
        height=10,
        weight=100,
        types=[
            PokemonType(slot=i + 1, type={"name": t, "url": ""})
            for i, t in enumerate(types)
        ],
        stats=[
            PokemonStat(base_stat=v, effort=0, stat={"name": n, "url": ""})
            for n, v in zip(STAT_NAMES, stats, strict=True)
        ],
        abilities=[
            PokemonAbility(
                ability={"name": "overgrow", "url": ""}, is_hidden=False, slot=1
            ),
            PokemonAbility(
                ability={"name": "chlorophyll", "url": ""}, is_hidden=True, slot=3
            ),
        ],
        sprites=PokemonSprites(
            front_default=f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{pid}.png"
        ),
    )


@pytest.fixture
def bulbasaur() -> Pokemon:
    return make_pokemon(1, "bulbasaur", ["grass", "poison"], [45, 49, 49, 65, 65, 45])


@pytest.fixture
def charmander() -> Pokemon:
    return make_pokemon(4, "charmander", ["fire"], [39, 52, 43, 60, 50, 65])


@pytest.fixture
def mock_client(bulbasaur, charmander):
    client = AsyncMock()
    client.get_pokemon.return_value = bulbasaur
    client.get_multiple_pokemon.return_value = [bulbasaur, charmander]
    with patch(
        "src.tools.pokemon_tools.get_pokemon_client", AsyncMock(return_value=client)
    ):
        yield client


# --- Tool metadata ---------------------------------------------------------


async def test_ui_tools_declare_resource_uri():
    tools = {t.name: t for t in await app.list_tools()}
    for name, uri in UI_TOOLS.items():
        assert tools[name].meta == {"ui": {"resourceUri": uri}}
    for name in set(tools) - set(UI_TOOLS):
        assert not (tools[name].meta or {}).get("ui")


# --- Widget resources ------------------------------------------------------


async def test_widget_resources_are_listed_with_csp():
    resources = {str(r.uri): r for r in await app.list_resources()}
    for uri in WIDGET_URIS:
        res = resources[uri]
        assert res.mime_type == "text/html;profile=mcp-app"
        assert res.meta["ui"]["csp"]["resourceDomains"] == [
            "https://raw.githubusercontent.com"
        ]


@pytest.mark.parametrize("uri", WIDGET_URIS)
async def test_widget_html_is_self_contained(uri):
    [content] = list(await app.read_resource(uri))
    html = content.content
    assert html.lstrip().lower().startswith("<!doctype html>")
    # The iframe CSP blocks external scripts: the runtime must be inlined.
    assert '<script type="module"' in html
    assert 'src="' not in html.split("<body>")[0]


# --- Structured content ----------------------------------------------------


def test_pokemon_card_payload(bulbasaur):
    card = pokemon_card(bulbasaur)
    assert card["id"] == 1
    assert card["types"] == ["grass", "poison"]
    assert card["sprite"].endswith("/1.png")
    assert card["artwork"].endswith("/official-artwork/1.png")
    assert card["stats"]["special-attack"] == 65
    assert card["abilities"] == [
        {"name": "overgrow", "hidden": False},
        {"name": "chlorophyll", "hidden": True},
    ]


def test_stats_entry_total(charmander):
    assert stats_entry(charmander)["total"] == 309


async def test_get_pokemon_info_returns_structured_content(mock_client):
    result = await app.call_tool("get_pokemon_info", {"name_or_id": "bulbasaur"})
    assert not result.is_error
    assert result.structured_content["name"] == "bulbasaur"
    assert "Bulbasaur" in result.content[0].text


async def test_analyze_stats_wraps_single_pokemon(mock_client):
    result = await app.call_tool("analyze_pokemon_stats", {"name_or_id": "bulbasaur"})
    assert [p["name"] for p in result.structured_content["pokemon"]] == ["bulbasaur"]
    assert "Stats Analysis" in result.content[0].text


async def test_tool_errors_are_flagged(mock_client):
    from src.clients.pokeapi_client import PokemonNotFoundError

    mock_client.get_pokemon.side_effect = PokemonNotFoundError("missingno")
    result = await app.call_tool("get_pokemon_info", {"name_or_id": "missingno"})
    assert result.is_error
    assert result.structured_content is None


async def test_search_returns_clickable_entries():
    client = AsyncMock()
    client.search_pokemon.return_value = type(
        "SearchResult",
        (),
        {
            "count": 1302,
            "results": [
                {"name": "pikachu", "url": "https://pokeapi.co/api/v2/pokemon/25/"},
                {"name": "raichu", "url": "https://pokeapi.co/api/v2/pokemon/26/"},
            ],
        },
    )
    with patch(
        "src.tools.pokemon_tools.get_pokemon_client", AsyncMock(return_value=client)
    ):
        result = await app.call_tool("search_pokemon", {"limit": 2, "offset": 24})
    assert not result.is_error
    data = result.structured_content
    assert (data["count"], data["limit"], data["offset"]) == (1302, 2, 24)
    assert data["results"][0]["id"] == 25
    assert data["results"][0]["name"] == "pikachu"
    assert data["results"][1]["sprite"].endswith("/pokemon/26.png")
    assert "#25: Pikachu" in result.content[0].text


def test_type_chart_payload():
    relations = {
        "double_damage_to": [{"name": "water"}, {"name": "flying"}],
        "half_damage_to": [{"name": "grass"}],
        "no_damage_to": [{"name": "ground"}],
        "double_damage_from": [{"name": "ground"}],
        "half_damage_from": [{"name": "steel"}, {"name": "electric"}],
    }
    assert type_chart("electric", relations) == {
        "type": "electric",
        "attack": {
            "double": ["water", "flying"],
            "half": ["grass"],
            "none": ["ground"],
        },
        "defense": {"double": ["ground"], "half": ["steel", "electric"], "none": []},
    }


async def test_type_effectiveness_returns_structured_content():
    client = AsyncMock()
    client.get_type_info.return_value = {
        "name": "ghost",
        "damage_relations": {"no_damage_to": [{"name": "normal"}]},
    }
    with patch(
        "src.tools.pokemon_tools.get_pokemon_client", AsyncMock(return_value=client)
    ):
        result = await app.call_tool(
            "get_type_effectiveness", {"attacking_type": "Ghost"}
        )
    assert result.structured_content["type"] == "ghost"
    assert result.structured_content["attack"]["none"] == ["normal"]
    assert "Ghost Type Effectiveness" in result.content[0].text


async def test_analyze_team_structured_content(mock_client):
    result = await analyze_team(["bulbasaur", "charmander", "missingno"])
    assert not result.is_error
    data = result.structured_content
    assert [m["name"] for m in data["members"]] == ["bulbasaur", "charmander"]
    assert data["members"][0]["sprite"].endswith("/1.png")
    assert data["members"][0]["total"] == 318
    assert data["members"][0]["roles"] == ["Balanced"]
    assert data["team_analysis"]["fastest"]["name"] == "charmander"
    assert data["not_found"] == ["missingno"]
    # The LLM still gets the full JSON analysis.
    assert json.loads(result.content[0]["text"])["team_size"] == 2


async def test_analyze_team_errors_are_flagged():
    result = await app.call_tool("analyze_team", {"pokemon_names": ["pikachu"]})
    assert result.is_error
    assert result.structured_content is None


# --- compare_pokemon -------------------------------------------------------


async def test_compare_pokemon(mock_client):
    result = await compare_pokemon(["bulbasaur", "charmander"])
    assert not result.is_error
    names = [p["name"] for p in result.structured_content["pokemon"]]
    assert names == ["bulbasaur", "charmander"]
    text = result.content[0]["text"]
    assert "| Bulbasaur | 45 | 49 | 49 | 65 | 65 | 45 | 318 |" in text
    assert "Spe: Charmander" in text
    assert "Not found" not in text


async def test_compare_pokemon_accepts_ids(mock_client):
    result = await compare_pokemon(["1", "4"])
    assert "Not found" not in result.content[0]["text"]


async def test_compare_pokemon_reports_missing(mock_client, bulbasaur, charmander):
    result = await compare_pokemon(["bulbasaur", "charmander", "missingno"])
    assert not result.is_error
    assert "**Not found:** missingno" in result.content[0]["text"]


async def test_compare_pokemon_needs_two_valid(mock_client, bulbasaur):
    mock_client.get_multiple_pokemon.return_value = [bulbasaur]
    result = await compare_pokemon(["bulbasaur", "missingno"])
    assert result.is_error
    assert "missingno" in result.content[0]["text"]


@pytest.mark.parametrize("names", [["bulbasaur"], ["a", "b", "c", "d", "e", "f", "g"]])
async def test_compare_pokemon_size_limits(names):
    result = await compare_pokemon(names)
    assert result.is_error


# --- Prompts ---------------------------------------------------------------


async def test_prompt_returns_plain_messages():
    """Regression: prompts used to arrive as a JSON-serialized GetPromptResult."""
    fake = GetPromptResult(
        description="d",
        messages=[
            PromptMessage(
                role="user", content=TextContent(type="text", text="Analiza")
            ),
            PromptMessage(
                role="assistant", content=TextContent(type="text", text="Ok")
            ),
        ],
    )
    with patch.object(
        battle_prompts, "create_matchup_analysis_prompt", AsyncMock(return_value=fake)
    ):
        result = await app.get_prompt(
            "battle/matchup-analysis", {"pokemon1": "pikachu", "pokemon2": "onix"}
        )
    assert [(m.role, m.content.text) for m in result.messages] == [
        ("user", "Analiza"),
        ("assistant", "Ok"),
    ]


async def test_prompt_error_is_a_message():
    with patch.object(
        battle_prompts,
        "create_matchup_analysis_prompt",
        AsyncMock(side_effect=RuntimeError("boom")),
    ):
        result = await app.get_prompt(
            "battle/matchup-analysis", {"pokemon1": "pikachu", "pokemon2": "onix"}
        )
    [msg] = result.messages
    assert msg.content.text == "❌ Error: boom"
    with pytest.raises(json.JSONDecodeError):
        json.loads(msg.content.text)
