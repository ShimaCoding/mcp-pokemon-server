"""Basic Pokemon tools for MCP server."""

import asyncio
import json
from collections import Counter
from typing import Any

from ..clients.pokeapi_client import PokemonNotFoundError, get_pokemon_client
from ..config.logging import get_logger
from ..models.pokemon_models import Pokemon
from ..models.response_models import ToolResult

logger = get_logger(__name__)

_ARTWORK_URL = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{id}.png"
_SPRITE_URL = (
    "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{id}.png"
)

# List-size bounds, shared by the validation below and the tools' input schema.
COMPARE_MIN_POKEMON = 2
COMPARE_MAX_POKEMON = 9  # Eevee plus its 8 evolutions
TEAM_MIN_SIZE = 2
TEAM_MAX_SIZE = 6  # a Pokémon team holds at most 6


def _sorted_types(pokemon: Pokemon) -> list[str]:
    return [t.type["name"] for t in sorted(pokemon.types, key=lambda x: x.slot)]


def pokemon_card(pokemon: Pokemon) -> dict[str, Any]:
    """Widget payload for the Pokédex card (``ui://pokedex/card.html``)."""
    sprite = pokemon.sprites.front_default
    return {
        "id": pokemon.id,
        "name": pokemon.name,
        "sprite": str(sprite) if sprite else None,
        "artwork": _ARTWORK_URL.format(id=pokemon.id),
        "types": _sorted_types(pokemon),
        "height_m": pokemon.height_meters,
        "weight_kg": pokemon.weight_kg,
        "stats": pokemon.stat_dict,
        "abilities": [
            {"name": a.ability["name"], "hidden": a.is_hidden}
            for a in sorted(pokemon.abilities, key=lambda x: x.slot)
        ],
    }


def stats_entry(pokemon: Pokemon) -> dict[str, Any]:
    """One item of the stats chart payload (``ui://pokedex/stats.html``)."""
    sprite = pokemon.sprites.front_default
    stats = pokemon.stat_dict
    return {
        "id": pokemon.id,
        "name": pokemon.name,
        "sprite": str(sprite) if sprite else None,
        "types": _sorted_types(pokemon),
        "stats": stats,
        "total": sum(stats.values()),
    }


def type_chart(type_name: str, damage_relations: dict[str, Any]) -> dict[str, Any]:
    """Widget payload for the type chart (``ui://pokedex/types.html``).

    ``attack`` lists the types this type hits for 2x / 0.5x / 0x; ``defense``
    the types that hit it for those multipliers.
    """

    def names(key: str) -> list[str]:
        return [t["name"] for t in damage_relations.get(key, [])]

    return {
        "type": type_name,
        "attack": {
            "double": names("double_damage_to"),
            "half": names("half_damage_to"),
            "none": names("no_damage_to"),
        },
        "defense": {
            "double": names("double_damage_from"),
            "half": names("half_damage_from"),
            "none": names("no_damage_from"),
        },
    }


async def get_pokemon_info(name_or_id: str) -> ToolResult:
    """Get detailed information about a Pokemon.

    Args:
        name_or_id: Pokemon name or ID

    Returns:
        ToolResult with Pokemon information
    """
    try:
        client = await get_pokemon_client()
        pokemon = await client.get_pokemon(name_or_id)

        # Format for MCP response
        content = [
            {
                "type": "text",
                "text": f"# {pokemon.name.title()} (#{pokemon.id})\n\n"
                f"**Height:** {pokemon.height_meters:.1f}m\n"
                f"**Weight:** {pokemon.weight_kg:.1f}kg\n"
                f"**Types:** {', '.join(pokemon.type_names)}\n"
                f"**Base Experience:** {pokemon.base_experience or 'Unknown'}\n\n"
                f"## Stats\n"
                + "\n".join(
                    [
                        f"- **{stat.title()}:** {value}"
                        for stat, value in pokemon.stat_dict.items()
                    ]
                )
                + "\n\n"
                "## Abilities\n"
                + "\n".join(
                    [
                        f"- {ability.ability['name'].title()}"
                        + (" (Hidden)" if ability.is_hidden else "")
                        for ability in pokemon.abilities
                    ]
                ),
            }
        ]

        return ToolResult(content=content, structured_content=pokemon_card(pokemon))

    except PokemonNotFoundError:
        error_content = [
            {
                "type": "text",
                "text": f"❌ Pokemon '{name_or_id}' not found. Please check the name or ID.",
            }
        ]
        return ToolResult(content=error_content, is_error=True)

    except Exception as e:
        logger.error("Error getting Pokemon info", identifier=name_or_id, error=str(e))
        error_content = [
            {
                "type": "text",
                "text": f"❌ Error retrieving Pokemon information: {str(e)}",
            }
        ]
        return ToolResult(content=error_content, is_error=True)


async def search_pokemon(
    query: str | None = None, limit: int = 20, offset: int = 0
) -> ToolResult:
    """Search for Pokemon with optional filtering.

    Args:
        query: Search query (not used in basic implementation)
        limit: Maximum number of results
        offset: Offset for pagination

    Returns:
        ToolResult with search results
    """
    try:
        client = await get_pokemon_client()
        search_result = await client.search_pokemon(limit=limit, offset=offset)

        # Format results for display
        pokemon_list = []
        entries = []
        for pokemon in search_result.results:
            # Extract ID from URL
            pokemon_id = pokemon["url"].strip("/").split("/")[-1]
            pokemon_list.append(f"#{pokemon_id}: {pokemon['name'].title()}")
            entries.append(
                {
                    "id": int(pokemon_id),
                    "name": pokemon["name"],
                    "sprite": _SPRITE_URL.format(id=pokemon_id),
                }
            )

        content = [
            {
                "type": "text",
                "text": f"# Pokemon Search Results\n\n"
                f"**Total Pokemon:** {search_result.count}\n"
                f"**Showing:** {len(search_result.results)} results (offset: {offset})\n\n"
                + "\n".join(pokemon_list)
                + "\n\n"
                "*Use get_pokemon_info with a name or ID for detailed information.*",
            }
        ]

        return ToolResult(
            content=content,
            structured_content={
                "count": search_result.count,
                "limit": limit,
                "offset": offset,
                "results": entries,
            },
        )

    except Exception as e:
        logger.error("Error searching Pokemon", error=str(e))
        error_content = [
            {"type": "text", "text": f"❌ Error searching Pokemon: {str(e)}"}
        ]
        return ToolResult(content=error_content, is_error=True)


async def get_type_effectiveness(attacking_type: str) -> ToolResult:
    """Get type effectiveness chart for a given type.

    Args:
        attacking_type: The attacking type name

    Returns:
        ToolResult with type effectiveness information
    """
    try:
        client = await get_pokemon_client()
        type_data = await client.get_type_info(attacking_type)

        # Parse damage relations
        damage_relations = type_data.get("damage_relations", {})

        effectiveness = {
            "Super Effective (2x)": [
                t["name"] for t in damage_relations.get("double_damage_to", [])
            ],
            "Not Very Effective (0.5x)": [
                t["name"] for t in damage_relations.get("half_damage_to", [])
            ],
            "No Effect (0x)": [
                t["name"] for t in damage_relations.get("no_damage_to", [])
            ],
        }

        content_text = f"# {attacking_type.title()} Type Effectiveness\n\n"

        for category, types in effectiveness.items():
            if types:
                content_text += f"## {category}\n"
                content_text += ", ".join([t.title() for t in types]) + "\n\n"
            else:
                content_text += f"## {category}\n*None*\n\n"

        content = [{"type": "text", "text": content_text}]
        return ToolResult(
            content=content,
            structured_content=type_chart(
                type_data.get("name", attacking_type.lower()), damage_relations
            ),
        )

    except PokemonNotFoundError:
        error_content = [
            {
                "type": "text",
                "text": f"❌ Type '{attacking_type}' not found. Please check the type name.",
            }
        ]
        return ToolResult(content=error_content, is_error=True)

    except Exception as e:
        logger.error(
            "Error getting type effectiveness",
            attacking_type=attacking_type,
            error=str(e),
        )
        error_content = [
            {
                "type": "text",
                "text": f"❌ Error retrieving type effectiveness: {str(e)}",
            }
        ]
        return ToolResult(content=error_content, is_error=True)


async def analyze_pokemon_stats(name_or_id: str) -> ToolResult:
    """Analyze Pokemon stats and provide insights.

    Args:
        name_or_id: Pokemon name or ID

    Returns:
        ToolResult with stats analysis
    """
    try:
        client = await get_pokemon_client()
        pokemon = await client.get_pokemon(name_or_id)

        stats = pokemon.stat_dict
        total_stats = sum(stats.values())

        # Basic analysis
        highest_stat = max(stats.items(), key=lambda x: x[1])
        lowest_stat = min(stats.items(), key=lambda x: x[1])

        # Rating based on total stats (rough approximation)
        if total_stats >= 600:
            rating = "Legendary/Pseudo-Legendary"
        elif total_stats >= 500:
            rating = "Strong"
        elif total_stats >= 400:
            rating = "Average"
        else:
            rating = "Below Average"

        content_text = f"# {pokemon.name.title()} Stats Analysis\n\n"
        content_text += f"**Total Base Stats:** {total_stats}\n"
        content_text += f"**Rating:** {rating}\n\n"
        content_text += f"**Highest Stat:** {highest_stat[0].title().replace('-', ' ')} ({highest_stat[1]})\n"
        content_text += f"**Lowest Stat:** {lowest_stat[0].title().replace('-', ' ')} ({lowest_stat[1]})\n\n"
        content_text += "## Detailed Stats\n"

        for stat_name, value in stats.items():
            bar_length = min(value // 10, 20)  # Scale down for display
            bar = "█" * bar_length + "░" * (20 - bar_length)
            content_text += (
                f"**{stat_name.title().replace('-', ' ')}:** {value} `{bar}`\n"
            )

        content_text += "\n*Based on base stats only. Actual performance depends on level, nature, IVs, and EVs.*"

        content = [{"type": "text", "text": content_text}]
        return ToolResult(
            content=content, structured_content={"pokemon": [stats_entry(pokemon)]}
        )

    except PokemonNotFoundError:
        error_content = [
            {
                "type": "text",
                "text": f"❌ Pokemon '{name_or_id}' not found. Please check the name or ID.",
            }
        ]
        return ToolResult(content=error_content, is_error=True)

    except Exception as e:
        logger.error(
            "Error analyzing Pokemon stats", identifier=name_or_id, error=str(e)
        )
        error_content = [
            {"type": "text", "text": f"❌ Error analyzing Pokemon stats: {str(e)}"}
        ]
        return ToolResult(content=error_content, is_error=True)


def _collect_texts(entries: list[dict], lang: str, max_count: int = 3) -> list[str]:
    """Return up to *max_count* deduplicated flavor texts for *lang*."""
    seen: set[str] = set()
    result: list[str] = []
    for entry in entries:
        if entry["language"]["name"] == lang:
            text = entry["flavor_text"].replace("\f", " ").replace("\n", " ").strip()
            if text and text not in seen:
                seen.add(text)
                result.append(text)
                if len(result) == max_count:
                    break
    return result


def _get_genus(genera: list[dict], lang: str) -> str:
    """Return the Pokémon classification string for *lang* (e.g. 'Mouse Pokémon')."""
    for entry in genera:
        if entry.get("language", {}).get("name") == lang:
            return str(entry.get("genus", ""))
    return ""


def _parse_evolution_detail(d: dict) -> dict[str, Any]:
    """Extract the non-null conditions of ONE ``evolution_details`` entry."""
    trigger = d.get("trigger") or {}
    via: dict[str, Any] = {"trigger": trigger.get("name", "unknown")}
    if d.get("min_level"):
        via["min_level"] = d["min_level"]
    if d.get("min_happiness"):
        via["min_happiness"] = d["min_happiness"]
    if d.get("item"):
        via["item"] = d["item"]["name"]
    if d.get("held_item"):
        via["held_item"] = d["held_item"]["name"]
    if d.get("location"):
        via["location"] = d["location"]["name"]
    if d.get("known_move"):
        via["known_move"] = d["known_move"]["name"]
    if d.get("known_move_type"):
        via["known_move_type"] = d["known_move_type"]["name"]
    gender = d.get("gender")
    if gender is not None:
        via["gender"] = "female" if gender == 1 else "male"
    if d.get("time_of_day"):
        via["time_of_day"] = d["time_of_day"]
    if d.get("min_beauty"):
        via["min_beauty"] = d["min_beauty"]
    if d.get("min_affection"):
        via["min_affection"] = d["min_affection"]
    if d.get("needs_overworld_rain"):
        via["needs_overworld_rain"] = True
    if d.get("turn_upside_down"):
        via["turn_upside_down"] = True
    relative_stats = d.get("relative_physical_stats")
    if relative_stats is not None:
        via["relative_physical_stats"] = relative_stats
    # Conditions below are rarer (trade partners, party requirements, newer games).
    for key in ("party_species", "party_type", "trade_species", "used_move", "region"):
        if d.get(key):
            via[key] = d[key]["name"]
    for key in ("min_move_count", "min_steps", "min_damage_taken"):
        if d.get(key):
            via[key] = d[key]
    if d.get("near_special_rock"):
        via["near_special_rock"] = True
    if d.get("evolved_pokemon_form"):
        via["evolved_form"] = d["evolved_pokemon_form"]["name"]
    chance = (d.get("condition_expression") or {}).get("percentage_chance")
    if chance is not None:
        via["chance_percent"] = chance
    return via


def _parse_evolution_details(details: list[dict]) -> dict[str, Any]:
    """Conditions of the FIRST details entry (compact form used by the flat chain).

    ``get_evolution_chain`` keeps every entry instead; see ``_parse_all_evolution_details``.
    """
    if not details:
        return {}
    return _parse_evolution_detail(details[0])


def _parse_all_evolution_details(details: list[dict]) -> list[dict[str, Any]]:
    """Conditions of ALL entries, tagged with the game version they come from.

    PokéAPI lists one entry per way (or per game generation) of evolving, e.g.
    Leafeon has one per Eevee-evolving location plus the Leaf Stone.
    """
    result = []
    for d in details:
        via = _parse_evolution_detail(d)
        if d.get("version_group"):
            via["version_group"] = d["version_group"]["name"]
        if "is_default" in d:
            via["is_default"] = bool(d["is_default"])
        result.append(via)
    return result


def _flatten_chain(node: dict) -> list[dict]:
    """Recursively flatten a chain node into an ordered list of evolution stages."""
    entry: dict[str, Any] = {"name": node.get("species", {}).get("name", "")}
    if node.get("is_baby"):
        entry["is_baby"] = True
    evo_details = node.get("evolution_details")
    if evo_details:
        via = _parse_evolution_details(evo_details)
        if via:
            entry["via"] = via
    result = [entry]
    for child in node.get("evolves_to", []):
        result.extend(_flatten_chain(child))
    return result


def _determine_roles(stats: dict[str, int]) -> list[str]:
    """Return the battle roles for a Pokémon given its base stats."""
    roles = []
    if stats.get("speed", 0) >= 100:
        roles.append("Fast")
    if stats.get("attack", 0) >= 100 or stats.get("special-attack", 0) >= 100:
        roles.append("Attacker")
    if stats.get("defense", 0) >= 100 or stats.get("special-defense", 0) >= 100:
        roles.append("Tank")
    if stats.get("hp", 0) >= 90:
        roles.append("Bulky")
    return roles or ["Balanced"]


def _bulk_score(stats: dict[str, int]) -> float:
    """Composite bulk: HP × (DEF + SPDEF) / 100."""
    return (
        stats.get("hp", 0)
        * (stats.get("defense", 0) + stats.get("special-defense", 0))
        / 100
    )


async def get_pokedex_entry(name_or_id: str) -> ToolResult:
    """Fetch a complete Pokédex entry for a Pokémon.

    Retrieves types, base stats, abilities, height, weight, flavor text
    descriptions from the games (in Spanish when available, otherwise English),
    generation, habitat, legendary/mythical status, capture rate, genus
    classification, gender ratio, base happiness, growth rate, egg groups,
    body shape, color, and full evolution chain with conditions.

    Args:
        name_or_id: Pokemon name (lowercase, e.g. 'pikachu') or Pokédex number
                    as a string (e.g. '25'). Alternate forms are supported
                    (e.g. 'pikachu-alola').

    Returns:
        ToolResult whose text content is a JSON object with the full Pokédex
        entry, or an error message on failure.
    """
    try:
        client = await get_pokemon_client()

        # Primary endpoint — core pokemon data
        pokemon = await client.get_pokemon(name_or_id)

        # Resolve species via the URL embedded in the pokemon response so that
        # alternate forms (e.g. pikachu-alola, id=10080) correctly resolve to
        # their base species (pikachu, species-id=25).
        if pokemon.species and pokemon.species.get("url"):
            species_url = pokemon.species["url"]
            species_id = species_url.strip("/").split("/")[-1]
        else:
            species_id = str(pokemon.id)

        species = await client.get_pokemon_species(species_id)

    except PokemonNotFoundError:
        return ToolResult(
            content=[
                {
                    "type": "text",
                    "text": f"❌ Pokémon '{name_or_id}' not found. Please check the name or ID.",
                }
            ],
            is_error=True,
        )
    except Exception as e:
        logger.error(
            "Error fetching Pokédex entry", identifier=name_or_id, error=str(e)
        )
        return ToolResult(
            content=[
                {
                    "type": "text",
                    "text": f"❌ Error retrieving Pokédex entry: {str(e)}",
                }
            ],
            is_error=True,
        )

    # Fetch evolution chain — graceful, never fails the whole call
    evolution_stages: list[dict] | None = None
    if species.evolution_chain and species.evolution_chain.get("url"):
        try:
            chain_data = await client.get_evolution_chain(
                species.evolution_chain["url"]
            )
            evolution_stages = _flatten_chain(chain_data.get("chain", {}))
        except Exception:
            logger.warning("Failed to fetch evolution chain", identifier=name_or_id)

    # Enrich evolution stages with stats fetched in parallel — graceful
    if evolution_stages:
        try:
            stage_names = [s["name"] for s in evolution_stages if s.get("name")]
            stage_pokemon = await client.get_multiple_pokemon(stage_names)
            stats_by_name = {
                p.name: {
                    "id": p.id,
                    "types": [
                        t.type["name"] for t in sorted(p.types, key=lambda x: x.slot)
                    ],
                    "total_bst": sum(s.base_stat for s in p.stats),
                }
                for p in stage_pokemon
            }
            for stage in evolution_stages:
                if stage["name"] in stats_by_name:
                    stage.update(stats_by_name[stage["name"]])
        except Exception:
            logger.warning("Failed to enrich evolution stages", identifier=name_or_id)

    # Types ordered by slot
    types = [t.type["name"] for t in sorted(pokemon.types, key=lambda x: x.slot)]

    # Base stats as a plain dict
    base_stats = {s.stat["name"]: s.base_stat for s in pokemon.stats}

    # Abilities ordered by slot
    abilities = [
        {"name": a.ability["name"], "is_hidden": a.is_hidden}
        for a in sorted(pokemon.abilities, key=lambda x: x.slot)
    ]

    # Flavor texts: prefer Spanish, fall back to English; deduplicated; max 3
    flavor_entries = species.flavor_text_entries or []
    flavor_texts = _collect_texts(flavor_entries, "es") or _collect_texts(
        flavor_entries, "en"
    )

    # Generation: "generation-i" → "I"
    generation_raw = species.generation.get("name", "")
    generation = (
        generation_raw.replace("generation-", "").upper()
        if generation_raw
        else "unknown"
    )

    # PokéAPI has no Spanish genus for the newest generations; the English
    # fallback is flagged so the narrator doesn't mix it into Spanish prose.
    genus_es = _get_genus(species.genera, "es")
    genus_en = "" if genus_es else _get_genus(species.genera, "en")
    genus = genus_es or genus_en or None
    genus_lang = "es" if genus_es else ("en" if genus_en else None)

    entry = {
        "id": pokemon.id,
        "name": pokemon.name,
        "genus": genus,
        "genus_lang": genus_lang,
        "height_dm": pokemon.height,
        "weight_hg": pokemon.weight,
        "color": species.color.get("name") if species.color else None,
        "shape": species.shape.get("name") if species.shape else None,
        "types": types,
        "base_stats": base_stats,
        "abilities": abilities,
        "flavor_text": flavor_texts,
        "generation": generation,
        "habitat": species.habitat["name"] if species.habitat else "unknown",
        "is_legendary": species.is_legendary,
        "is_mythical": species.is_mythical,
        "capture_rate": species.capture_rate,
        "gender_rate": species.gender_rate,
        "base_happiness": species.base_happiness,
        "growth_rate": species.growth_rate.get("name") if species.growth_rate else None,
        "egg_groups": [g["name"] for g in species.egg_groups],
        "evolution_chain": evolution_stages,
    }

    card = {
        **pokemon_card(pokemon),
        "genus": entry["genus"],
        "flavor_text": flavor_texts[0] if flavor_texts else None,
        "generation": generation,
        "habitat": entry["habitat"],
        "is_legendary": species.is_legendary,
        "is_mythical": species.is_mythical,
    }

    return ToolResult(
        content=[{"type": "text", "text": json.dumps(entry, ensure_ascii=False)}],
        structured_content=card,
    )


def _species_id(node: dict) -> int | None:
    """Pokédex number of a chain node, from its species URL."""
    try:
        return int(str(node["species"]["url"]).strip("/").split("/")[-1])
    except (KeyError, ValueError):
        return None


def _chain_nodes(node: dict) -> list[dict]:
    nodes = [node]
    for child in node.get("evolves_to", []):
        nodes.extend(_chain_nodes(child))
    return nodes


def _via_text(via: dict[str, Any]) -> str:
    """Short English description of one evolution condition (for the LLM)."""
    parts = [str(via.get("trigger", "unknown"))]
    for key, value in via.items():
        if key in ("trigger", "version_group", "is_default"):
            continue
        parts.append(key if value is True else f"{key}={value}")
    return " ".join(parts)


def _evolution_node(
    node: dict, queried: str, pokemon_by_id: dict[int, Pokemon]
) -> dict[str, Any]:
    """Build one tree node (and, recursively, its ``evolves_to``)."""
    name = node.get("species", {}).get("name", "")
    sid = _species_id(node)
    pokemon = pokemon_by_id.get(sid) if sid is not None else None
    sprite = pokemon.sprites.front_default if pokemon else None
    return {
        "name": name,
        "id": sid,
        "types": _sorted_types(pokemon) if pokemon else [],
        "total_bst": sum(s.base_stat for s in pokemon.stats) if pokemon else None,
        "sprite": (
            str(sprite) if sprite else (_SPRITE_URL.format(id=sid) if sid else None)
        ),
        "is_baby": bool(node.get("is_baby")),
        "queried": name == queried,
        "via": _parse_all_evolution_details(node.get("evolution_details") or []),
        "evolves_to": [
            _evolution_node(child, queried, pokemon_by_id)
            for child in node.get("evolves_to", [])
        ],
    }


def _evolution_edges(tree: dict[str, Any]) -> list[str]:
    """One ``from -> to (conditions)`` line per evolution in the tree."""
    edges: list[str] = []
    for child in tree["evolves_to"]:
        # Current-game entries only: ``via`` keeps the per-generation history.
        current = [v for v in child["via"] if v.get("is_default")] or child["via"]
        conditions = " OR ".join(dict.fromkeys(_via_text(v) for v in current))
        edges.append(f"{tree['name']} -> {child['name']} ({conditions})")
        edges.extend(_evolution_edges(child))
    return edges


def _tree_depth(tree: dict[str, Any]) -> int:
    return 1 + max((_tree_depth(c) for c in tree["evolves_to"]), default=0)


async def get_evolution_chain(pokemon: str) -> ToolResult:
    """Get the full evolution line of a Pokémon as a tree.

    Answers "what does X evolve into?", "who does X evolve from?" and "show me
    the evolution line of X". Each node carries name, id, types, total_bst,
    sprite, is_baby, ``via`` (every way of reaching it: trigger, level, item,
    happiness, time of day, location, ...) and ``evolves_to``. The queried
    species is flagged ``queried: true``. A Pokémon that does not evolve
    returns a single node.

    Args:
        pokemon: Pokémon name or Pokédex number; any form of the line works.

    Returns:
        ToolResult whose text content is the JSON tree, or an error message.
    """
    try:
        client = await get_pokemon_client()
        found = await client.get_pokemon(pokemon)
        # Resolve through the species URL so alternate forms map to their species.
        if found.species and found.species.get("url"):
            species_id = str(found.species["url"]).strip("/").split("/")[-1]
        else:
            species_id = str(found.id)
        species = await client.get_pokemon_species(species_id)

        root: dict | None = None
        if species.evolution_chain and species.evolution_chain.get("url"):
            chain_data = await client.get_evolution_chain(
                species.evolution_chain["url"]
            )
            root = chain_data.get("chain") or None
        if root is None:  # species without a chain: a single node
            root = {
                "species": {
                    "name": species.name,
                    "url": f"https://pokeapi.co/api/v2/pokemon-species/{species.id}/",
                },
                "is_baby": False,
                "evolution_details": [],
                "evolves_to": [],
            }

        # Fetch by Pokédex number: many species names (wormadam, darmanitan,
        # meowstic...) are not valid Pokémon names in PokéAPI.
        ids = [i for i in (_species_id(n) for n in _chain_nodes(root)) if i is not None]
        try:
            members = await client.get_multiple_pokemon([str(i) for i in ids])
        except Exception:
            logger.warning("Failed to enrich evolution chain", identifier=pokemon)
            members = []
        tree = _evolution_node(root, species.name, {p.id: p for p in members})
    except PokemonNotFoundError:
        return ToolResult(
            content=[
                {
                    "type": "text",
                    "text": f"❌ Pokémon '{pokemon}' not found. Please check the name or ID.",
                }
            ],
            is_error=True,
        )
    except Exception as e:
        logger.error("Error fetching evolution chain", identifier=pokemon, error=str(e))
        return ToolResult(
            content=[
                {"type": "text", "text": f"❌ Error retrieving evolution chain: {e}"}
            ],
            is_error=True,
        )

    payload = {
        "queried": species.name,
        "stages": _tree_depth(tree),
        "root": tree,
        "evolutions": _evolution_edges(tree),
    }
    return ToolResult(
        content=[{"type": "text", "text": json.dumps(payload, ensure_ascii=False)}],
        structured_content=payload,
    )


def defensive_profile(
    types: list[str], relations: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    """Damage multipliers taken by a Pokémon of ``types`` (``relations``: type → damage_relations).

    Returns ``weak_to`` (type → 2 or 4), ``resists`` (type → 0.5 or 0.25) and ``immune_to``,
    each sorted by type name. Pure.
    """
    mult: dict[str, float] = {}
    for own in types:
        rel = relations.get(own) or {}
        for key, factor in (
            ("double_damage_from", 2.0),
            ("half_damage_from", 0.5),
            ("no_damage_from", 0.0),
        ):
            for t in rel.get(key, []):
                mult[t["name"]] = mult.get(t["name"], 1.0) * factor
    weak = {t: int(m) for t, m in sorted(mult.items()) if m > 1}
    resists = {t: m for t, m in sorted(mult.items()) if 0 < m < 1}
    immune = sorted(t for t, m in mult.items() if m == 0)
    return {"weak_to": weak, "resists": resists, "immune_to": immune}


def team_weaknesses(members: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Attacking types that hit 2+ members super-effectively, most dangerous first. Pure.

    Each entry lists who is weak, who resists and who is immune to that type.
    """
    attackers = sorted({t for m in members for t in m["defense"]["weak_to"]})
    out = []
    for t in attackers:
        weak = [m["name"] for m in members if t in m["defense"]["weak_to"]]
        if len(weak) < 2:
            continue
        resist = [m["name"] for m in members if t in m["defense"]["resists"]]
        immune = [m["name"] for m in members if t in m["defense"]["immune_to"]]
        out.append({"type": t, "weak": weak, "resist": resist, "immune": immune})
    return sorted(
        out,
        key=lambda e: (-len(e["weak"]), len(e["resist"]) + len(e["immune"]), e["type"]),
    )


async def _type_relations(
    client: Any, types: set[str]
) -> dict[str, dict[str, Any]] | None:
    """damage_relations of each type (Redis-cached by the client); None if any is missing."""
    try:
        data = await asyncio.gather(*(client.get_type_data(t) for t in sorted(types)))
    except (
        Exception
    ) as e:  # noqa: BLE001 — the team analysis works without defense data
        logger.warning("Type data unavailable for team defense", error=str(e))
        return None
    relations = {}
    for t, d in zip(sorted(types), data, strict=True):
        rel = d.get("damage_relations") if isinstance(d, dict) else None
        if not isinstance(rel, dict):
            return None
        relations[t] = rel
    return relations


async def analyze_team(pokemon_names: list[str]) -> ToolResult:
    """Analyze a team of 2–6 Pokémon fetched in parallel.

    Fetches all Pokémon concurrently and returns a JSON object with per-member
    data (types, base stats, BST, battle roles) plus team-wide metrics: average
    BST, type coverage, fastest/strongest/bulkiest members, and role distribution.

    Args:
        pokemon_names: List of TEAM_MIN_SIZE–TEAM_MAX_SIZE Pokémon names or
            Pokédex IDs.

    Returns:
        ToolResult whose text content is a JSON object with the full team
        analysis, or an error message on failure.
    """
    if not TEAM_MIN_SIZE <= len(pokemon_names) <= TEAM_MAX_SIZE:
        return ToolResult(
            content=[
                {
                    "type": "text",
                    "text": f"❌ A team must have between {TEAM_MIN_SIZE} and "
                    f"{TEAM_MAX_SIZE} Pokémon.",
                }
            ],
            is_error=True,
        )

    try:
        client = await get_pokemon_client()
        team = await client.get_multiple_pokemon(
            [str(n).lower() for n in pokemon_names]
        )
    except Exception as e:
        logger.error("Error fetching team", error=str(e))
        return ToolResult(
            content=[{"type": "text", "text": f"❌ Error fetching team: {str(e)}"}],
            is_error=True,
        )

    if not team:
        return ToolResult(
            content=[
                {
                    "type": "text",
                    "text": "❌ Could not fetch any Pokémon from the provided names.",
                }
            ],
            is_error=True,
        )

    members: list[dict[str, Any]] = []
    widget_members: list[dict[str, Any]] = []
    for p in team:
        stats = {s.stat["name"]: s.base_stat for s in p.stats}
        members.append(
            {
                "name": p.name,
                "id": p.id,
                "types": [
                    t.type["name"] for t in sorted(p.types, key=lambda x: x.slot)
                ],
                "base_stats": stats,
                "total_bst": sum(stats.values()),
                "roles": _determine_roles(stats),
            }
        )
        widget_members.append({**stats_entry(p), "roles": members[-1]["roles"]})

    # Defense: what each member takes from every attacking type (best effort).
    relations = await _type_relations(client, {t for m in members for t in m["types"]})
    if relations is not None:
        for m in members:
            m["defense"] = defensive_profile(m["types"], relations)

    # Team-wide metrics
    avg_bst = sum(m["total_bst"] for m in members) / len(members)
    type_coverage = sorted({t for m in members for t in m["types"]})

    fastest = max(members, key=lambda m: m["base_stats"].get("speed", 0))
    strongest_physical = max(members, key=lambda m: m["base_stats"].get("attack", 0))
    strongest_special = max(
        members, key=lambda m: m["base_stats"].get("special-attack", 0)
    )
    bulkiest = max(members, key=lambda m: _bulk_score(m["base_stats"]))
    role_distribution = dict(Counter(r for m in members for r in m["roles"]))

    # Flag names that were requested but not returned (e.g. typos)
    fetched_names = {m["name"] for m in members}
    not_found = [
        n for n in [str(x).lower() for x in pokemon_names] if n not in fetched_names
    ]

    analysis: dict[str, Any] = {
        "team_size": len(members),
        "members": members,
        "team_analysis": {
            "avg_bst": round(avg_bst, 1),
            "type_coverage": type_coverage,
            "fastest": {
                "name": fastest["name"],
                "speed": fastest["base_stats"].get("speed", 0),
            },
            "strongest_physical": {
                "name": strongest_physical["name"],
                "attack": strongest_physical["base_stats"].get("attack", 0),
            },
            "strongest_special": {
                "name": strongest_special["name"],
                "special_attack": strongest_special["base_stats"].get(
                    "special-attack", 0
                ),
            },
            "bulkiest": {
                "name": bulkiest["name"],
                "bulk_score": round(_bulk_score(bulkiest["base_stats"]), 1),
            },
            "role_distribution": role_distribution,
        },
    }
    if relations is not None:
        analysis["team_analysis"]["shared_weaknesses"] = team_weaknesses(members)

    if not_found:
        analysis["not_found"] = not_found

    return ToolResult(
        content=[{"type": "text", "text": json.dumps(analysis, ensure_ascii=False)}],
        structured_content={
            "members": widget_members,
            "team_analysis": analysis["team_analysis"],
            "not_found": not_found,
        },
    )


_STAT_LABELS = {
    "hp": "HP",
    "attack": "Atk",
    "defense": "Def",
    "special-attack": "SpA",
    "special-defense": "SpD",
    "speed": "Spe",
}


def _compare_batches(names: list[str]) -> list[list[str]]:
    """Split ``names`` into the fewest balanced batches that compare_pokemon accepts.

    Balancing (10 -> 5 + 5 rather than 9 + 1) keeps every batch above the minimum.
    """
    count = -(-len(names) // COMPARE_MAX_POKEMON)
    size, extra = divmod(len(names), count)
    batches: list[list[str]] = []
    start = 0
    for i in range(count):
        end = start + size + (1 if i < extra else 0)
        batches.append(names[start:end])
        start = end
    return batches


def _compare_size_error(pokemon_names: list[str]) -> str:
    got = len(pokemon_names)
    text = (
        f"❌ compare_pokemon accepts {COMPARE_MIN_POKEMON}–{COMPARE_MAX_POKEMON} "
        f"Pokémon, got {got}."
    )
    if got < COMPARE_MIN_POKEMON:
        return (
            f"{text} Add at least {COMPARE_MIN_POKEMON - got} more to compare "
            "against, or use analyze_pokemon_stats for a single Pokémon."
        )
    batches = ", ".join(
        json.dumps(b, ensure_ascii=False)
        for b in _compare_batches([str(n) for n in pokemon_names])
    )
    return (
        f"{text} Split into batches of ≤{COMPARE_MAX_POKEMON} and call "
        f"compare_pokemon once per batch: {batches}"
    )


async def compare_pokemon(pokemon_names: list[str]) -> ToolResult:
    """Compare the base stats of 2–9 Pokémon side by side.

    Args:
        pokemon_names: List of COMPARE_MIN_POKEMON–COMPARE_MAX_POKEMON Pokémon
            names or Pokédex IDs.

    Returns:
        ToolResult with a markdown stats table for the LLM and a
        ``{"pokemon": [...]}`` payload for the stats widget.
    """
    if not COMPARE_MIN_POKEMON <= len(pokemon_names) <= COMPARE_MAX_POKEMON:
        return ToolResult(
            content=[{"type": "text", "text": _compare_size_error(pokemon_names)}],
            is_error=True,
        )

    requested = [str(n).strip().lower() for n in pokemon_names]
    try:
        client = await get_pokemon_client()
        fetched = await client.get_multiple_pokemon(requested)
    except Exception as e:
        logger.error("Error fetching Pokémon to compare", error=str(e))
        return ToolResult(
            content=[{"type": "text", "text": f"❌ Error fetching Pokémon: {str(e)}"}],
            is_error=True,
        )

    not_found = [
        n for n in requested if not any(n in (p.name, str(p.id)) for p in fetched)
    ]
    if len(fetched) < 2:
        return ToolResult(
            content=[
                {
                    "type": "text",
                    "text": "❌ Need at least 2 valid Pokémon to compare. "
                    f"Not found: {', '.join(not_found) or '—'}",
                }
            ],
            is_error=True,
        )

    entries = [stats_entry(p) for p in fetched]

    header = "| Pokémon | " + " | ".join(_STAT_LABELS.values()) + " | Total |"
    divider = "|---" * (len(_STAT_LABELS) + 2) + "|"
    rows = [
        f"| {e['name'].title()} | "
        + " | ".join(str(e["stats"].get(k, 0)) for k in _STAT_LABELS)
        + f" | {e['total']} |"
        for e in entries
    ]
    best = [
        f"{label}: {max(entries, key=lambda e: e['stats'].get(key, 0))['name'].title()}"
        for key, label in _STAT_LABELS.items()
    ]
    text = "\n".join([header, divider, *rows])
    text += "\n\n**Best per stat:** " + ", ".join(best)
    if not_found:
        text += f"\n\n**Not found:** {', '.join(not_found)}"

    return ToolResult(
        content=[{"type": "text", "text": text}],
        structured_content={"pokemon": entries},
    )


# Tool registry for easy access
POKEMON_TOOLS = {
    "get_pokemon_info": get_pokemon_info,
    "search_pokemon": search_pokemon,
    "get_type_effectiveness": get_type_effectiveness,
    "analyze_pokemon_stats": analyze_pokemon_stats,
    "get_pokedex_entry": get_pokedex_entry,
    "get_evolution_chain": get_evolution_chain,
    "analyze_team": analyze_team,
    "compare_pokemon": compare_pokemon,
}
