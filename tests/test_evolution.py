"""Tests for get_evolution_chain, built from real PokéAPI evolution-chain shapes."""

import json
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

from src.clients.pokeapi_client import PokemonNotFoundError
from src.models.pokemon_models import PokemonSpecies
from src.server.mcp_server import app
from src.tools.pokemon_tools import (
    _parse_evolution_details,
    get_evolution_chain,
    get_pokedex_entry,
)
from tests.test_apps import make_pokemon

SPECIES_URL = "https://pokeapi.co/api/v2/pokemon-species/{}/"
CHAIN_URL = "https://pokeapi.co/api/v2/evolution-chain/{}/"


def detail(trigger: str = "level-up", **kw: Any) -> dict:
    """An evolution_details entry as PokéAPI returns it (null/false defaults)."""
    d: dict[str, Any] = {
        "trigger": {"name": trigger, "url": ""},
        "gender": None,
        "held_item": None,
        "item": None,
        "known_move": None,
        "known_move_type": None,
        "location": None,
        "min_affection": None,
        "min_beauty": None,
        "min_happiness": None,
        "min_level": None,
        "needs_overworld_rain": False,
        "party_species": None,
        "party_type": None,
        "relative_physical_stats": None,
        "time_of_day": "",
        "trade_species": None,
        "turn_upside_down": False,
        "version_group": {"name": "scarlet-violet", "url": ""},
        "is_default": True,
    }
    for key, value in kw.items():
        d[key] = {"name": value, "url": ""} if isinstance(value, str) and key in (
            "item", "held_item", "location", "known_move", "known_move_type",
            "version_group",
        ) else value  # fmt: skip
    return d


def node(
    name: str,
    pid: int,
    details: list[dict] | None = None,
    *kids: dict,
    baby: bool = False,
) -> dict:
    return {
        "is_baby": baby,
        "species": {"name": name, "url": SPECIES_URL.format(pid)},
        "evolution_details": details or [],
        "evolves_to": list(kids),
    }


# name -> (pokedex id, types, base stats)
DEX = {
    "smoliv": (928, ["grass", "normal"], [41, 35, 45, 58, 51, 30]),
    "dolliv": (929, ["grass", "normal"], [52, 53, 60, 78, 78, 33]),
    "arboliva": (930, ["grass", "normal"], [78, 69, 90, 125, 109, 39]),
    "eevee": (133, ["normal"], [55, 55, 50, 45, 65, 55]),
    "vaporeon": (134, ["water"], [130, 65, 60, 110, 95, 65]),
    "jolteon": (135, ["electric"], [65, 65, 60, 110, 95, 130]),
    "flareon": (136, ["fire"], [65, 130, 60, 95, 110, 65]),
    "espeon": (196, ["psychic"], [65, 65, 60, 130, 95, 110]),
    "umbreon": (197, ["dark"], [95, 65, 110, 60, 130, 65]),
    "leafeon": (470, ["grass"], [65, 110, 130, 60, 65, 95]),
    "glaceon": (471, ["ice"], [65, 60, 110, 130, 95, 65]),
    "sylveon": (700, ["fairy"], [95, 65, 65, 110, 130, 60]),
    "wurmple": (265, ["bug"], [45, 45, 35, 20, 30, 20]),
    "silcoon": (266, ["bug"], [50, 35, 55, 25, 25, 15]),
    "beautifly": (267, ["bug", "flying"], [60, 70, 50, 100, 50, 65]),
    "cascoon": (268, ["bug"], [50, 35, 55, 25, 25, 15]),
    "dustox": (269, ["bug", "poison"], [60, 50, 70, 50, 90, 65]),
    "pichu": (172, ["electric"], [20, 40, 15, 35, 35, 60]),
    "pikachu": (25, ["electric"], [35, 55, 40, 50, 50, 90]),
    "raichu": (26, ["electric"], [60, 90, 55, 90, 80, 110]),
    "tauros": (128, ["normal"], [75, 100, 95, 40, 70, 110]),
}
BY_ID = {pid: make_pokemon(pid, n, t, s) for n, (pid, t, s) in DEX.items()}

CHAINS: dict[str, tuple[int, dict]] = {
    "smoliv": (
        487,
        node(
            "smoliv",
            928,
            None,
            node(
                "dolliv",
                929,
                [detail(min_level=25)],
                node("arboliva", 930, [detail(min_level=35)]),
            ),
        ),
    ),
    "eevee": (
        67,
        node(
            "eevee", 133, None,
            node("vaporeon", 134, [detail("use-item", item="water-stone")]),
            node("jolteon", 135, [detail("use-item", item="thunder-stone")]),
            node("flareon", 136, [detail("use-item", item="fire-stone")]),
            node("espeon", 196, [detail(min_happiness=160, time_of_day="day")]),
            node("umbreon", 197, [detail(min_happiness=160, time_of_day="night")]),
            node(
                "leafeon", 470,
                [detail(location="eterna-forest", near_special_rock=True, is_default=False, version_group="diamond-pearl"),
                 detail("use-item", item="leaf-stone")],
            ),
            node("glaceon", 471, [detail("use-item", item="ice-stone")]),
            node("sylveon", 700, [detail(known_move_type="fairy", min_happiness=160)]),
        ),
    ),  # fmt: skip
    "wurmple": (
        135,
        node(
            "wurmple", 265, None,
            node("silcoon", 266, [detail(min_level=7, condition_expression={"percentage_chance": 50})],
                 node("beautifly", 267, [detail(min_level=10)])),
            node("cascoon", 268, [detail(min_level=7, condition_expression={"percentage_chance": 50})],
                 node("dustox", 269, [detail(min_level=10)])),
        ),
    ),  # fmt: skip
    "pichu": (
        10,
        node(
            "pichu", 172, None,
            node("pikachu", 25, [detail(min_happiness=220)],
                 node("raichu", 26, [detail("use-item", item="thunder-stone"),
                                     detail("use-item", item="thunder-stone", region={"name": "alola", "url": ""},
                                            evolved_pokemon_form={"name": "raichu-alola", "url": ""})])),
            baby=True,
        ),
    ),  # fmt: skip
    "tauros": (63, node("tauros", 128)),
}
CHAINS["dolliv"] = CHAINS["arboliva"] = CHAINS["smoliv"]
CHAINS["vaporeon"] = CHAINS["eevee"]
CHAINS["silcoon"] = CHAINS["wurmple"]
CHAINS["raichu"] = CHAINS["pikachu"] = CHAINS["pichu"]


def species_for(name: str) -> PokemonSpecies:
    pid = DEX[name][0]
    chain_id = CHAINS[name][0]
    return PokemonSpecies(
        id=pid,
        name=name,
        color={"name": "x", "url": ""},
        generation={"name": "generation-i", "url": ""},
        is_legendary=False,
        is_mythical=False,
        evolution_chain={"url": CHAIN_URL.format(chain_id)},
    )


@pytest.fixture
def client():
    c = AsyncMock()

    async def get_pokemon(identifier: str):
        key = identifier.lower()
        if key in DEX:
            p = BY_ID[DEX[key][0]]
            p.species = {"name": key, "url": SPECIES_URL.format(p.id)}
            return p
        raise PokemonNotFoundError(identifier)

    async def get_multiple(ids: list[str]):
        return [BY_ID[int(i)] for i in ids if int(i) in BY_ID]

    async def get_species(identifier: str):
        name = next(n for n, (pid, *_) in DEX.items() if str(pid) == str(identifier))
        return species_for(name)

    async def get_chain(url: str):
        chain_id = int(url.strip("/").split("/")[-1])
        root = next(root for cid, root in CHAINS.values() if cid == chain_id)
        return {"id": chain_id, "chain": root}

    c.get_pokemon.side_effect = get_pokemon
    c.get_multiple_pokemon.side_effect = get_multiple
    c.get_pokemon_species.side_effect = get_species
    c.get_evolution_chain.side_effect = get_chain
    with patch("src.tools.pokemon_tools.get_pokemon_client", AsyncMock(return_value=c)):
        yield c


def flat(tree: dict) -> list[dict]:
    return [tree, *[n for c in tree["evolves_to"] for n in flat(c)]]


async def test_linear_chain_with_levels(client):
    result = await get_evolution_chain("smoliv")
    assert not result.is_error
    data = result.structured_content
    assert data["stages"] == 3
    root = data["root"]
    assert [n["name"] for n in flat(root)] == ["smoliv", "dolliv", "arboliva"]
    dolliv = root["evolves_to"][0]
    arboliva = dolliv["evolves_to"][0]
    assert root["via"] == []
    assert dolliv["via"][0]["min_level"] == 25
    assert arboliva["via"][0]["min_level"] == 35
    assert (arboliva["id"], arboliva["types"], arboliva["total_bst"]) == (
        930, ["grass", "normal"], 78 + 69 + 90 + 125 + 109 + 39,
    )  # fmt: skip
    assert arboliva["sprite"].endswith("/930.png")
    assert data["evolutions"] == [
        "smoliv -> dolliv (level-up min_level=25)",
        "dolliv -> arboliva (level-up min_level=35)",
    ]
    # The text the LLM reads is the same payload.
    assert json.loads(result.content[0]["text"]) == data


async def test_queried_species_is_marked_from_any_stage(client):
    for name in ("smoliv", "dolliv", "arboliva"):
        data = (await get_evolution_chain(name)).structured_content
        assert [n["name"] for n in flat(data["root"]) if n["queried"]] == [name]
        assert data["queried"] == name


async def test_eevee_has_eight_branches_with_distinct_conditions(client):
    data = (await get_evolution_chain("eevee")).structured_content
    kids = data["root"]["evolves_to"]
    assert data["root"]["queried"] is True and data["stages"] == 2
    assert [k["name"] for k in kids] == [
        "vaporeon", "jolteon", "flareon", "espeon", "umbreon", "leafeon", "glaceon", "sylveon",
    ]  # fmt: skip
    by = {k["name"]: k["via"] for k in kids}
    assert by["vaporeon"][0]["item"] == "water-stone"
    assert by["espeon"][0]["time_of_day"] == "day"
    assert by["umbreon"][0]["time_of_day"] == "night"
    assert by["sylveon"][0]["known_move_type"] == "fairy"
    assert all(k["evolves_to"] == [] and not k["queried"] for k in kids)
    # Querying a child still returns the whole tree rooted at eevee.
    child = (await get_evolution_chain("vaporeon")).structured_content
    assert child["root"]["name"] == "eevee"
    assert [n["name"] for n in flat(child["root"]) if n["queried"]] == ["vaporeon"]


async def test_every_evolution_detail_is_kept(client):
    leafeon = next(
        k
        for k in (await get_evolution_chain("eevee")).structured_content["root"][
            "evolves_to"
        ]
        if k["name"] == "leafeon"
    )
    assert len(leafeon["via"]) == 2
    assert leafeon["via"][0] == {
        "trigger": "level-up",
        "location": "eterna-forest",
        "near_special_rock": True,
        "version_group": "diamond-pearl",
        "is_default": False,
    }
    assert leafeon["via"][1]["item"] == "leaf-stone"
    assert leafeon["via"][1]["is_default"] is True
    # The old flat helper still only looks at the first entry.
    assert _parse_evolution_details([detail(min_level=7), detail(min_level=9)]) == {
        "trigger": "level-up",
        "min_level": 7,
    }


async def test_wurmple_branches_two_levels_deep(client):
    data = (await get_evolution_chain("wurmple")).structured_content
    root = data["root"]
    assert data["stages"] == 3
    assert [c["name"] for c in root["evolves_to"]] == ["silcoon", "cascoon"]
    assert [c["evolves_to"][0]["name"] for c in root["evolves_to"]] == [
        "beautifly",
        "dustox",
    ]
    assert root["evolves_to"][0]["via"][0]["chance_percent"] == 50
    assert root["evolves_to"][1]["evolves_to"][0]["types"] == ["bug", "poison"]
    assert (
        "wurmple -> silcoon (level-up min_level=7 chance_percent=50)"
        in data["evolutions"]
    )


async def test_baby_pichu_and_regional_variants(client):
    data = (await get_evolution_chain("pichu")).structured_content
    pichu, pikachu = data["root"], data["root"]["evolves_to"][0]
    raichu = pikachu["evolves_to"][0]
    assert pichu["is_baby"] is True and pichu["queried"] is True
    assert pikachu["is_baby"] is False
    assert pikachu["via"][0]["min_happiness"] == 220
    assert len(raichu["via"]) == 2
    assert raichu["via"][1]["region"] == "alola"
    assert raichu["via"][1]["evolved_form"] == "raichu-alola"


async def test_species_without_evolution_is_a_single_node(client):
    result = await get_evolution_chain("tauros")
    assert not result.is_error
    data = result.structured_content
    assert data["stages"] == 1 and data["evolutions"] == []
    assert data["root"]["name"] == "tauros"
    assert data["root"]["queried"] is True
    assert data["root"]["evolves_to"] == [] and data["root"]["via"] == []


async def test_species_without_chain_url_is_a_single_node(client):
    species = species_for("tauros")
    species.evolution_chain = None
    client.get_pokemon_species.side_effect = None
    client.get_pokemon_species.return_value = species
    data = (await get_evolution_chain("tauros")).structured_content
    assert [n["name"] for n in flat(data["root"])] == ["tauros"]
    assert data["root"]["types"] == ["normal"]
    client.get_evolution_chain.assert_not_called()


async def test_not_found_matches_other_tools(client):
    result = await get_evolution_chain("fakemon")
    assert result.is_error
    assert result.structured_content is None
    text = result.content[0]["text"]
    assert text == "❌ Pokémon 'fakemon' not found. Please check the name or ID."
    other = await get_pokedex_entry("fakemon")
    assert other.content[0]["text"] == text


async def test_chain_failure_is_an_error(client):
    client.get_evolution_chain.side_effect = RuntimeError("boom")
    result = await get_evolution_chain("eevee")
    assert result.is_error
    assert "boom" in result.content[0]["text"]


async def test_enrichment_failure_still_returns_the_tree(client):
    client.get_multiple_pokemon.side_effect = RuntimeError("down")
    data = (await get_evolution_chain("smoliv")).structured_content
    arboliva = flat(data["root"])[-1]
    assert arboliva["types"] == [] and arboliva["total_bst"] is None
    assert arboliva["sprite"].endswith("/930.png")


async def test_tool_is_registered_with_widget_and_discoverable_description(client):
    tools = {t.name: t for t in await app.list_tools()}
    tool = tools["get_evolution_chain"]
    assert tool.meta == {"ui": {"resourceUri": "ui://pokedex/evolution.html"}}
    assert list(tool.input_schema["properties"]) == ["pokemon"]
    assert tool.input_schema["required"] == ["pokemon"]
    for phrase in (
        "evolution", "línea evolutiva", "¿en qué evoluciona?", "¿de quién evoluciona?",
    ):  # fmt: skip
        assert phrase in tool.description
    result = await app.call_tool("get_evolution_chain", {"pokemon": "eevee"})
    assert not result.is_error
    assert len(result.structured_content["root"]["evolves_to"]) == 8
