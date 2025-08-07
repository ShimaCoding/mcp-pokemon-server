"""Pokemon Resources for MCP Server.

This module implements dynamic resources that allow LLMs to access
Pokemon data as if they were documents or files.

Resources provided:
- pokemon://info/{name_or_id} - Detailed Pokemon information
- pokemon://stats/{name_or_id} - Pokemon statistics analysis
- pokemon://moveset/{name_or_id} - Pokemon moveset data
- pokemon://type/{type_name} - Type effectiveness data
- pokemon://generation/{gen_number} - Generation-specific Pokemon list
"""

from typing import Any, cast
from urllib.parse import parse_qs, urlparse

from mcp.types import Resource, TextResourceContents
from pydantic import AnyUrl

from ..clients.pokeapi_client import PokemonAPIClient
from ..config.logging import get_logger

logger = get_logger(__name__)


class PokemonResourceManager:
    """Manages dynamic Pokemon resources for MCP."""

    def __init__(self, pokemon_client: PokemonAPIClient):
        """Initialize the resource manager.

        Args:
            pokemon_client: Client for PokéAPI interactions
        """
        self.pokemon_client = pokemon_client
        self.resource_handlers = {
            "info": self._handle_pokemon_info,
            "stats": self._handle_pokemon_stats,
            "moveset": self._handle_pokemon_moveset,
            "type": self._handle_type_info,
            "generation": self._handle_generation_info,
            "comparison": self._handle_pokemon_comparison,
        }
        logger.info(
            "PokemonResourceManager initialized",
            handlers=list(self.resource_handlers.keys()),
        )

    async def list_resources(self) -> list[Resource]:
        """List available Pokemon resources.

        Returns:
            List of available resource templates
        """
        resources = [
            Resource(
                uri=cast(AnyUrl, "pokemon://info/{name_or_id}"),
                name="Pokemon Information",
                description="Detailed information about a specific Pokemon",
                mimeType="text/markdown",
            ),
            Resource(
                uri=cast(AnyUrl, "pokemon://stats/{name_or_id}"),
                name="Pokemon Statistics",
                description="Detailed statistical analysis of a Pokemon",
                mimeType="text/markdown",
            ),
            Resource(
                uri=cast(AnyUrl, "pokemon://moveset/{name_or_id}"),
                name="Pokemon Moveset",
                description="Complete moveset and learn methods for a Pokemon",
                mimeType="text/markdown",
            ),
            Resource(
                uri=cast(AnyUrl, "pokemon://type/{type_name}"),
                name="Type Information",
                description="Type effectiveness chart and Pokemon of this type",
                mimeType="text/markdown",
            ),
            Resource(
                uri=cast(AnyUrl, "pokemon://generation/{gen_number}"),
                name="Generation Pokemon",
                description="All Pokemon from a specific generation",
                mimeType="text/markdown",
            ),
            Resource(
                uri=cast(
                    AnyUrl, "pokemon://comparison/{pokemon1_name}/{pokemon2_name}"
                ),
                name="Pokemon Comparison",
                description="Side-by-side comparison of two Pokemon",
                mimeType="text/markdown",
            ),
        ]

        logger.info("Listed resources", count=len(resources))
        return resources

    async def get_resource(self, uri: str) -> TextResourceContents:
        """Get content for a specific resource URI.

        Args:
            uri: Resource URI to fetch

        Returns:
            Resource content as text

        Raises:
            ValueError: If URI format is invalid
            Exception: If resource cannot be fetched
        """
        logger.info("Getting resource", uri=uri)

        try:
            # Parse the URI
            parsed = urlparse(uri)
            if parsed.scheme != "pokemon":
                raise ValueError(f"Unsupported URI scheme: {parsed.scheme}")

            # Extract resource type and parameters from netloc and path
            # For URIs like pokemon://info/pikachu, netloc='info', path='/pikachu'
            if parsed.netloc:
                resource_type = parsed.netloc
                path_parts = (
                    parsed.path.strip("/").split("/") if parsed.path.strip("/") else []
                )
            else:
                # Fallback: extract from path like /info/pikachu
                path_parts = parsed.path.strip("/").split("/")
                if not path_parts or not path_parts[0]:
                    raise ValueError("Missing resource type in URI")
                resource_type = path_parts[0]
                path_parts = path_parts[1:] if len(path_parts) > 1 else []

            # Get query parameters
            query_params = parse_qs(parsed.query)

            # Route to appropriate handler
            handler = self.resource_handlers.get(resource_type)
            if not handler:
                raise ValueError(f"Unknown resource type: {resource_type}")

            content = await handler(path_parts, query_params)

            logger.info(
                "Resource fetched successfully", uri=uri, content_length=len(content)
            )

            return TextResourceContents(
                uri=cast(AnyUrl, uri), mimeType="text/markdown", text=content
            )

        except Exception as e:
            logger.error(
                "Error fetching resource", uri=uri, error=str(e), exc_info=True
            )
            raise

    async def _handle_pokemon_info(
        self, params: list[str], query: dict[str, list[str]]
    ) -> str:
        """Handle pokemon://info/{name_or_id} resources."""
        if not params:
            raise ValueError("Pokemon name or ID required")

        name_or_id = params[0]

        try:
            # Get Pokemon data
            pokemon_data = await self.pokemon_client.get_pokemon(name_or_id)
            species_data = await self.pokemon_client.get_pokemon_species(name_or_id)

            # Format as markdown resource
            content = f"""# {pokemon_data.name.title()} (#{pokemon_data.id})

## Basic Information
- **Height**: {pokemon_data.height / 10:.1f}m
- **Weight**: {pokemon_data.weight / 10:.1f}kg
- **Base Experience**: {pokemon_data.base_experience}
- **Types**: {", ".join([t.type["name"] for t in pokemon_data.types])}

## Physical Description
{species_data.flavor_text_entries[0]["flavor_text"].replace(chr(10), " ") if species_data.flavor_text_entries and len(species_data.flavor_text_entries) > 0 else "No description available."}

## Base Stats
"""

            # Add stats table
            content += "| Stat | Value | Rank |\n|------|-------|------|\n"
            total_stats = 0
            for stat in pokemon_data.stats:
                stat_name = stat.stat["name"].replace("-", " ").title()
                stat_value = stat.base_stat
                total_stats += stat_value

                # Determine rank
                if stat_value >= 120:
                    rank = "Excellent"
                elif stat_value >= 90:
                    rank = "Great"
                elif stat_value >= 60:
                    rank = "Good"
                elif stat_value >= 40:
                    rank = "Average"
                else:
                    rank = "Poor"

                content += f"| {stat_name} | {stat_value} | {rank} |\n"

            content += f"| **Total** | **{total_stats}** | - |\n\n"

            # Add abilities
            content += "## Abilities\n"
            for ability in pokemon_data.abilities:
                ability_name = ability.ability["name"].replace("-", " ").title()
                hidden = " (Hidden)" if ability.is_hidden else ""
                content += f"- **{ability_name}**{hidden}\n"

            # Add generation info
            generation = (
                species_data.generation["name"]
                if species_data.generation
                else "unknown"
            )
            content += f"\n## Generation\n{generation.replace('-', ' ').title()}\n"

            return content

        except Exception as e:
            logger.error(
                "Error handling pokemon info resource",
                name_or_id=name_or_id,
                error=str(e),
            )
            raise Exception(
                f"Could not fetch Pokemon info for '{name_or_id}': {str(e)}"
            )

    async def _handle_pokemon_stats(
        self, params: list[str], query: dict[str, list[str]]
    ) -> str:
        """Handle pokemon://stats/{name_or_id} resources."""
        if not params:
            raise ValueError("Pokemon name or ID required")

        name_or_id = params[0]

        try:
            pokemon_data = await self.pokemon_client.get_pokemon(name_or_id)

            content = f"""# {pokemon_data.name.title()} - Statistical Analysis

## Stat Distribution
"""

            stats = {stat.stat["name"]: stat.base_stat for stat in pokemon_data.stats}
            total_stats = sum(stats.values())

            # Create visual stat bars
            max_stat = max(stats.values())
            for stat_name, value in stats.items():
                stat_display = stat_name.replace("-", " ").title()
                bar_length = int((value / max_stat) * 20)
                bar = "█" * bar_length + "░" * (20 - bar_length)
                percentage = (value / total_stats) * 100

                content += f"**{stat_display}**: {value}\n"
                content += f"`{bar}` {percentage:.1f}% of total\n\n"

            # Statistical analysis
            highest_stat_name = max(stats, key=lambda x: stats[x])
            lowest_stat_name = min(stats, key=lambda x: stats[x])

            content += f"""
## Statistical Summary
- **Total Base Stats**: {total_stats}
- **Average Stat**: {total_stats / 6:.1f}
- **Highest Stat**: {max(stats.values())} ({highest_stat_name.replace("-", " ").title()})
- **Lowest Stat**: {min(stats.values())} ({lowest_stat_name.replace("-", " ").title()})

## Battle Role Analysis
"""

            # Determine battle role based on stats
            roles = []
            if stats.get("attack", 0) >= 100 or stats.get("special-attack", 0) >= 100:
                roles.append("Sweeper/Attacker")
            if stats.get("defense", 0) >= 100 or stats.get("special-defense", 0) >= 100:
                roles.append("Tank/Wall")
            if stats.get("hp", 0) >= 90:
                roles.append("Bulky")
            if stats.get("speed", 0) >= 100:
                roles.append("Fast")

            if not roles:
                roles.append("Balanced")

            content += f"**Suggested Roles**: {', '.join(roles)}\n"

            # Type effectiveness
            types = [t.type["name"] for t in pokemon_data.types]
            content += f"\n**Types**: {', '.join(types)}\n"

            return content

        except Exception as e:
            logger.error(
                "Error handling pokemon stats resource",
                name_or_id=name_or_id,
                error=str(e),
            )
            raise Exception(
                f"Could not fetch Pokemon stats for '{name_or_id}': {str(e)}"
            )

    async def _handle_pokemon_moveset(
        self, params: list[str], query: dict[str, list[str]]
    ) -> str:
        """Handle pokemon://moveset/{name_or_id} resources."""
        if not params:
            raise ValueError("Pokemon name or ID required")

        name_or_id = params[0]

        try:
            pokemon_data = await self.pokemon_client.get_pokemon(name_or_id)

            content = f"""# {pokemon_data.name.title()} - Moveset

## Available Moves
"""

            # Group moves by learn method
            moves_by_method: dict[str, list[dict[str, Any]]] = {}
            if pokemon_data.moves:
                for move_entry in pokemon_data.moves:
                    move_name = move_entry.move["name"]
                    for version_detail in move_entry.version_group_details:
                        method = version_detail["move_learn_method"]["name"]
                        level = version_detail["level_learned_at"]

                        if method not in moves_by_method:
                            moves_by_method[method] = []

                        moves_by_method[method].append(
                            {"name": move_name, "level": level}
                        )

            # Display moves by category
            for method, moves in moves_by_method.items():
                method_display = method.replace("-", " ").title()
                content += f"\n### {method_display}\n"

                if method == "level-up":
                    # Sort by level for level-up moves
                    moves.sort(key=lambda x: x["level"])
                    content += "| Level | Move |\n|-------|------|\n"
                    for move in moves[:20]:  # Limit to first 20 moves
                        move_display = move["name"].replace("-", " ").title()
                        content += f"| {move['level']} | {move_display} |\n"
                else:
                    # Just list other moves
                    for move in moves[:15]:  # Limit to first 15 moves
                        move_display = move["name"].replace("-", " ").title()
                        content += f"- {move_display}\n"

            return content

        except Exception as e:
            logger.error(
                "Error handling pokemon moveset resource",
                name_or_id=name_or_id,
                error=str(e),
            )
            raise Exception(
                f"Could not fetch Pokemon moveset for '{name_or_id}': {str(e)}"
            )

    async def _handle_type_info(
        self, params: list[str], query: dict[str, list[str]]
    ) -> str:
        """Handle pokemon://type/{type_name} resources."""
        if not params:
            raise ValueError("Type name required")

        type_name = params[0]

        try:
            type_data = await self.pokemon_client.get_type_data(type_name)

            content = f"""# {type_name.title()} Type Information

## Type Effectiveness

### Strong Against (2x damage)
"""

            # Strong against
            strong_against = type_data.get("damage_relations", {}).get(
                "double_damage_to", []
            )
            if strong_against:
                for target_type in strong_against:
                    content += f"- {target_type['name'].title()}\n"
            else:
                content += "- None\n"

            content += "\n### Weak Against (0.5x damage)\n"
            weak_against = type_data.get("damage_relations", {}).get(
                "half_damage_to", []
            )
            if weak_against:
                for target_type in weak_against:
                    content += f"- {target_type['name'].title()}\n"
            else:
                content += "- None\n"

            content += "\n### No Effect Against (0x damage)\n"
            no_effect = type_data.get("damage_relations", {}).get("no_damage_to", [])
            if no_effect:
                for target_type in no_effect:
                    content += f"- {target_type['name'].title()}\n"
            else:
                content += "- None\n"

            content += "\n## Defensive Matchups\n"
            content += "\n### Resists (0.5x damage taken)\n"
            resists = type_data.get("damage_relations", {}).get("half_damage_from", [])
            if resists:
                for attacking_type in resists:
                    content += f"- {attacking_type['name'].title()}\n"
            else:
                content += "- None\n"

            content += "\n### Weak To (2x damage taken)\n"
            weak_to = type_data.get("damage_relations", {}).get(
                "double_damage_from", []
            )
            if weak_to:
                for attacking_type in weak_to:
                    content += f"- {attacking_type['name'].title()}\n"
            else:
                content += "- None\n"

            content += "\n### Immune To (0x damage taken)\n"
            immune_to = type_data.get("damage_relations", {}).get("no_damage_from", [])
            if immune_to:
                for attacking_type in immune_to:
                    content += f"- {attacking_type['name'].title()}\n"
            else:
                content += "- None\n"

            return content

        except Exception as e:
            logger.error(
                "Error handling type info resource", type_name=type_name, error=str(e)
            )
            raise Exception(f"Could not fetch type info for '{type_name}': {str(e)}")

    async def _handle_generation_info(
        self, params: list[str], query: dict[str, list[str]]
    ) -> str:
        """Handle pokemon://generation/{gen_number} resources."""
        if not params:
            raise ValueError("Generation number required")

        gen_number = params[0]

        try:
            # This would require additional API calls to get generation data
            # For now, return a placeholder
            content = f"""# Generation {gen_number} Pokemon

## Overview
Generation {gen_number} Pokemon information.

*Note: Detailed generation data requires additional API implementation.*
"""
            return content

        except Exception as e:
            logger.error(
                "Error handling generation info resource",
                gen_number=gen_number,
                error=str(e),
            )
            raise Exception(
                f"Could not fetch generation info for '{gen_number}': {str(e)}"
            )

    async def _handle_pokemon_comparison(
        self, params: list[str], query: dict[str, list[str]]
    ) -> str:
        """Handle pokemon://comparison/{pokemon1}/{pokemon2} resources."""
        if len(params) < 2:
            raise ValueError("Two Pokemon names required for comparison")

        pokemon1_name = params[0]
        pokemon2_name = params[1]

        try:
            # Get data for both Pokemon
            pokemon1_data = await self.pokemon_client.get_pokemon(pokemon1_name)
            pokemon2_data = await self.pokemon_client.get_pokemon(pokemon2_name)

            content = f"""# Pokemon Comparison: {pokemon1_data.name.title()} vs {pokemon2_data.name.title()}

## Basic Comparison
| Attribute | {pokemon1_data.name.title()} | {pokemon2_data.name.title()} |
|-----------|{"-" * len(pokemon1_data.name)}|{"-" * len(pokemon2_data.name)}|
| ID | #{pokemon1_data.id} | #{pokemon2_data.id} |
| Height | {pokemon1_data.height / 10:.1f}m | {pokemon2_data.height / 10:.1f}m |
| Weight | {pokemon1_data.weight / 10:.1f}kg | {pokemon2_data.weight / 10:.1f}kg |
| Base Exp | {pokemon1_data.base_experience} | {pokemon2_data.base_experience} |

## Stat Comparison
"""

            # Compare stats
            pokemon1_stats = {
                stat.stat["name"]: stat.base_stat for stat in pokemon1_data.stats
            }
            pokemon2_stats = {
                stat.stat["name"]: stat.base_stat for stat in pokemon2_data.stats
            }

            content += f"| Stat | {pokemon1_data.name.title()} | {pokemon2_data.name.title()} | Winner |\n"
            content += f"|------|{'-' * len(pokemon1_data.name)}|{'-' * len(pokemon2_data.name)}|--------|\n"

            for stat_name in pokemon1_stats.keys():
                stat_display = stat_name.replace("-", " ").title()
                val1 = pokemon1_stats[stat_name]
                val2 = pokemon2_stats[stat_name]

                if val1 > val2:
                    winner = pokemon1_data.name.title()
                elif val2 > val1:
                    winner = pokemon2_data.name.title()
                else:
                    winner = "Tie"

                content += f"| {stat_display} | {val1} | {val2} | {winner} |\n"

            # Total stats
            total1 = sum(pokemon1_stats.values())
            total2 = sum(pokemon2_stats.values())
            winner = (
                pokemon1_data.name.title()
                if total1 > total2
                else pokemon2_data.name.title() if total2 > total1 else "Tie"
            )
            content += f"| **Total** | **{total1}** | **{total2}** | **{winner}** |\n"

            # Type comparison
            types1 = [t.type["name"] for t in pokemon1_data.types]
            types2 = [t.type["name"] for t in pokemon2_data.types]

            content += f"""
## Type Comparison
- **{pokemon1_data.name.title()}**: {", ".join(types1)}
- **{pokemon2_data.name.title()}**: {", ".join(types2)}
"""

            return content

        except Exception as e:
            logger.error(
                "Error handling pokemon comparison resource",
                pokemon1=pokemon1_name,
                pokemon2=pokemon2_name,
                error=str(e),
            )
            raise Exception(
                f"Could not compare '{pokemon1_name}' and '{pokemon2_name}': {str(e)}"
            )
