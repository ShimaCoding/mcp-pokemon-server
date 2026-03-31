"""Basic Pokemon tools for MCP server."""

import json
from typing import Any

from ..clients.pokeapi_client import PokemonNotFoundError, get_pokemon_client
from ..config.logging import get_logger
from ..models.response_models import ToolResult

logger = get_logger(__name__)


async def get_pokemon_info(name_or_id: str) -> ToolResult:
    """Get detailed information about a Pokemon.

    Args:
        name_or_id: Pokemon name or ID

    Returns:
        ToolResult with Pokemon information
    """
    logger.info("Getting Pokemon info", identifier=name_or_id)

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

        return ToolResult(content=content)

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
    logger.info("Searching Pokemon", query=query, limit=limit, offset=offset)

    try:
        client = await get_pokemon_client()
        search_result = await client.search_pokemon(limit=limit, offset=offset)

        # Format results for display
        pokemon_list = []
        for pokemon in search_result.results:
            # Extract ID from URL
            pokemon_id = pokemon["url"].strip("/").split("/")[-1]
            pokemon_list.append(f"#{pokemon_id}: {pokemon['name'].title()}")

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

        return ToolResult(content=content)

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
    logger.info("Getting type effectiveness", attacking_type=attacking_type)

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
        return ToolResult(content=content)

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
    logger.info("Analyzing Pokemon stats", identifier=name_or_id)

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
        return ToolResult(content=content)

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


def _parse_evolution_details(details: list[dict]) -> dict[str, Any]:
    """Extract non-null evolution conditions from the first details entry."""
    if not details:
        return {}
    d = details[0]
    via: dict[str, Any] = {"trigger": d.get("trigger", {}).get("name", "unknown")}
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
    return via


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
    logger.info("Fetching Pokédex entry", identifier=name_or_id)

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

    entry = {
        "id": pokemon.id,
        "name": pokemon.name,
        "genus": _get_genus(species.genera, "es")
        or _get_genus(species.genera, "en")
        or None,
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

    return ToolResult(
        content=[{"type": "text", "text": json.dumps(entry, ensure_ascii=False)}]
    )


# Tool registry for easy access
POKEMON_TOOLS = {
    "get_pokemon_info": get_pokemon_info,
    "search_pokemon": search_pokemon,
    "get_type_effectiveness": get_type_effectiveness,
    "analyze_pokemon_stats": analyze_pokemon_stats,
    "get_pokedex_entry": get_pokedex_entry,
}
