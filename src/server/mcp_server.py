"""MCP server implementation using MCPServer (MCP Python SDK v2)."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from mcp.server.apps import Apps
from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.prompts.base import Message, UserMessage
from mcp.types import CallToolResult, GetPromptResult, TextContent

from .. import __version__
from ..cache.redis_cache import close_redis_cache, init_redis_cache
from ..clients.pokeapi_client import PokemonAPIClient, set_pokemon_client
from ..config.logging import get_logger, setup_logging
from ..config.settings import get_settings
from ..models.response_models import ToolResult
from ..prompts.battle_prompts import BattlePromptManager
from ..prompts.educational_prompts import EducationalPromptManager
from ..resources.pokemon_resources import PokemonResourceManager
from ..tools.pokemon_tools import POKEMON_TOOLS
from ..widgets import CARD_URI, STATS_URI, register_widgets

# Setup logging
setup_logging()
logger = get_logger(__name__)

settings = get_settings()

# Initialize clients and managers (http client started in lifespan)
pokemon_client = PokemonAPIClient()
resource_manager = PokemonResourceManager(pokemon_client)
educational_prompts = EducationalPromptManager(pokemon_client)
battle_prompts = BattlePromptManager(pokemon_client)


@asynccontextmanager
async def lifespan(server: MCPServer) -> AsyncGenerator[None, None]:
    """Manage server lifecycle: start and close the HTTP client and Redis cache."""
    logger.info("[SERVER] Startup")
    await pokemon_client.start()
    set_pokemon_client(pokemon_client)  # share instance with tools
    await init_redis_cache(settings)
    try:
        yield
    finally:
        logger.info("[SERVER] Shutdown")
        set_pokemon_client(None)
        await close_redis_cache()
        await pokemon_client.close()


# MCP Apps: tools bound to a `ui://` widget still return LLM-facing text, plus a
# `structuredContent` payload the host hands to the widget.
apps = Apps()
register_widgets(apps)


def _call_tool_result(result: ToolResult) -> CallToolResult:
    return CallToolResult(
        content=[TextContent(type="text", text=str(c["text"])) for c in result.content],
        structured_content=result.structured_content,
        is_error=result.is_error,
    )


def _tool_error(tool: str, e: Exception) -> CallToolResult:
    logger.error(f"[TOOL] {tool} error", error=str(e))
    return CallToolResult(
        content=[TextContent(type="text", text=f"❌ Error: {str(e)}")], is_error=True
    )


def _prompt_messages(result: GetPromptResult) -> list[Message]:
    return [Message(m.content, role=m.role) for m in result.messages]


# UI-bound tools must be declared before MCPServer consumes the extension.
@apps.tool(resource_uri=CARD_URI)
async def get_pokemon_info(name_or_id: str) -> CallToolResult:
    """Get detailed information about a Pokemon by name or ID.

    Args:
        name_or_id: Pokemon name or ID to lookup
    """
    logger.info("[TOOL] get_pokemon_info", identifier=name_or_id)

    try:
        return _call_tool_result(await POKEMON_TOOLS["get_pokemon_info"](name_or_id))
    except Exception as e:
        return _tool_error("get_pokemon_info", e)


@apps.tool(resource_uri=STATS_URI)
async def analyze_pokemon_stats(name_or_id: str) -> CallToolResult:
    """Analyze Pokemon stats and provide insights.

    Args:
        name_or_id: Pokemon name or ID to analyze
    """
    logger.info("[TOOL] analyze_pokemon_stats", identifier=name_or_id)

    try:
        return _call_tool_result(
            await POKEMON_TOOLS["analyze_pokemon_stats"](name_or_id)
        )
    except Exception as e:
        return _tool_error("analyze_pokemon_stats", e)


@apps.tool(resource_uri=CARD_URI)
async def get_pokedex_entry(pokemon: str) -> CallToolResult:
    """Get a complete Pokédex entry for a Pokémon, including flavor texts.

    Returns a JSON object with types, base stats, abilities, height, weight,
    flavor text descriptions (Spanish preferred, English fallback), generation,
    habitat, legendary/mythical status, and capture rate. Ideal for narration
    by the Dexter persona.

    Args:
        pokemon: Pokémon name (e.g. 'pikachu') or Pokédex number (e.g. '25').
                 Alternate forms are supported (e.g. 'pikachu-alola').
    """
    logger.info("[TOOL] get_pokedex_entry", identifier=pokemon)

    try:
        return _call_tool_result(await POKEMON_TOOLS["get_pokedex_entry"](pokemon))
    except Exception as e:
        return _tool_error("get_pokedex_entry", e)


@apps.tool(resource_uri=STATS_URI)
async def compare_pokemon(pokemon_names: list[str]) -> CallToolResult:
    """Compare the base stats of 2–6 Pokémon side by side.

    Returns a markdown table with HP, Attack, Defense, Sp. Atk, Sp. Def, Speed
    and total for each Pokémon, plus which one leads each stat.

    Args:
        pokemon_names: List of 2–6 Pokémon names or Pokédex IDs.
    """
    logger.info("[TOOL] compare_pokemon", pokemon=pokemon_names)

    try:
        return _call_tool_result(await POKEMON_TOOLS["compare_pokemon"](pokemon_names))
    except Exception as e:
        return _tool_error("compare_pokemon", e)


# Create MCP server instance (host/port are transport options in SDK v2, see run_server)
app = MCPServer(
    "Pokemon MCP Server",
    version=__version__,
    lifespan=lifespan,
    extensions=[apps],
)


@app.tool()
async def search_pokemon(limit: int = 20, offset: int = 0) -> str:
    """Search for Pokemon with pagination.

    Args:
        limit: Maximum number of results (default: 20)
        offset: Offset for pagination (default: 0)
    """
    logger.info("[TOOL] search_pokemon", limit=limit, offset=offset)

    try:
        result = await POKEMON_TOOLS["search_pokemon"](limit=limit, offset=offset)
        if result.is_error:
            return str(result.content[0]["text"])
        return str(result.content[0]["text"])
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        logger.error("[TOOL] search_pokemon error", error=str(e))
        return error_msg


@app.tool()
async def get_type_effectiveness(attacking_type: str) -> str:
    """Get type effectiveness chart for a Pokemon type.

    Args:
        attacking_type: The attacking type name (e.g., 'fire', 'water', 'electric')
    """
    logger.info("[TOOL] get_type_effectiveness", attacking_type=attacking_type)

    try:
        result = await POKEMON_TOOLS["get_type_effectiveness"](attacking_type)
        if result.is_error:
            return str(result.content[0]["text"])
        return str(result.content[0]["text"])
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        logger.error("[TOOL] get_type_effectiveness error", error=str(e))
        return error_msg


@app.tool()
async def analyze_team(pokemon_names: list[str]) -> str:
    """Analyze a team of 2–6 Pokémon fetched in parallel.

    Returns a JSON object with per-member data (types, base stats, BST, battle
    roles) plus team-wide metrics: average BST, type coverage, fastest/
    strongest/bulkiest members, and role distribution.

    Args:
        pokemon_names: List of 2–6 Pokémon names or Pokédex IDs.
    """
    logger.info("[TOOL] analyze_team", team=pokemon_names)

    try:
        result = await POKEMON_TOOLS["analyze_team"](pokemon_names)
        return str(result.content[0]["text"])
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        logger.error("[TOOL] analyze_team error", error=str(e))
        return error_msg


# Resource handlers - Dynamic Pokemon Resources
@app.resource("pokemon://info/{name_or_id}")
async def pokemon_info_resource(name_or_id: str) -> str:
    """Get detailed Pokemon information as a resource.

    Args:
        name_or_id: Pokemon name or ID to lookup
    """
    logger.info("[RESOURCE] pokemon://info", identifier=name_or_id)

    try:
        content = await resource_manager.get_resource(f"pokemon://info/{name_or_id}")
        return content.text
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        logger.error("[RESOURCE] pokemon://info error", error=str(e))
        return error_msg


@app.resource("pokemon://stats/{name_or_id}")
async def pokemon_stats_resource(name_or_id: str) -> str:
    """Get Pokemon statistics analysis as a resource.

    Args:
        name_or_id: Pokemon name or ID to analyze
    """
    logger.info("[RESOURCE] pokemon://stats", identifier=name_or_id)

    try:
        content = await resource_manager.get_resource(f"pokemon://stats/{name_or_id}")
        return content.text
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        logger.error("[RESOURCE] pokemon://stats error", error=str(e))
        return error_msg


@app.resource("pokemon://type/{type_name}")
async def pokemon_type_resource(type_name: str) -> str:
    """Get type effectiveness information as a resource.

    Args:
        type_name: Pokemon type name (e.g., 'fire', 'water', 'electric')
    """
    logger.info("[RESOURCE] pokemon://type", type_name=type_name)

    try:
        content = await resource_manager.get_resource(f"pokemon://type/{type_name}")
        return content.text
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        logger.error("[RESOURCE] pokemon://type error", error=str(e))
        return error_msg


@app.resource("pokemon://comparison/{pokemon1}/{pokemon2}")
async def pokemon_comparison_resource(pokemon1: str, pokemon2: str) -> str:
    """Get Pokemon comparison as a resource.

    Args:
        pokemon1: First Pokemon name
        pokemon2: Second Pokemon name
    """
    logger.info("[RESOURCE] pokemon://comparison", pokemon1=pokemon1, pokemon2=pokemon2)

    try:
        content = await resource_manager.get_resource(
            f"pokemon://comparison/{pokemon1}/{pokemon2}"
        )
        return content.text
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        logger.error("[RESOURCE] pokemon://comparison error", error=str(e))
        return error_msg


# Prompt handlers - Educational Prompts
@app.prompt("educational/pokemon-analysis")
async def pokemon_analysis_prompt(
    pokemon_name: str, analysis_type: str = "general", user_level: str = "beginner"
) -> list[Message]:
    """Educational prompt for Pokemon analysis.

    Args:
        pokemon_name: Name of the Pokemon to analyze
        analysis_type: Type of analysis (general, battle, competitive)
        user_level: User experience level (beginner, intermediate, advanced)
    """
    logger.info(
        "pokemon_analysis_prompt called",
        pokemon_name=pokemon_name,
        analysis_type=analysis_type,
        user_level=user_level,
    )

    try:
        result = await educational_prompts.create_pokemon_analysis_prompt(
            pokemon_name, analysis_type, user_level
        )
        return _prompt_messages(result)
    except Exception as e:
        logger.error("pokemon_analysis_prompt failed", error=str(e))
        return [UserMessage(f"❌ Error: {str(e)}")]


@app.prompt("educational/team-building")
async def team_building_prompt(
    theme: str = "balanced",
    format: str = "casual",
    restrictions: list[str] | None = None,
) -> list[Message]:
    """Educational prompt for team building guidance.

    Args:
        theme: Team theme (balanced, offensive, defensive, type-specific)
        format: Battle format (casual, competitive, tournament)
        restrictions: Optional restrictions (no legendaries, specific generation, etc.)
    """
    logger.info(
        "team_building_prompt called",
        theme=theme,
        format=format,
        restrictions=restrictions,
    )

    try:
        result = await educational_prompts.create_team_building_prompt(
            theme, format, restrictions
        )
        return _prompt_messages(result)
    except Exception as e:
        logger.error("team_building_prompt failed", error=str(e))
        return [UserMessage(f"❌ Error: {str(e)}")]


@app.prompt("educational/type-effectiveness")
async def type_effectiveness_prompt(
    scenario: str = "learning",
    attacking_type: str | None = None,
    defending_types: list[str] | None = None,
) -> list[Message]:
    """Educational prompt for type effectiveness learning.

    Args:
        scenario: Learning scenario (learning, quiz, battle-analysis)
        attacking_type: Specific attacking type to focus on
        defending_types: Specific defending types to analyze
    """
    logger.info(
        "type_effectiveness_prompt called",
        scenario=scenario,
        attacking_type=attacking_type,
        defending_types=defending_types,
    )

    try:
        result = await educational_prompts.create_type_effectiveness_prompt(
            scenario, attacking_type, defending_types
        )
        return _prompt_messages(result)
    except Exception as e:
        logger.error("type_effectiveness_prompt failed", error=str(e))
        return [UserMessage(f"❌ Error: {str(e)}")]


# Battle Prompts
@app.prompt("battle/strategy")
async def battle_strategy_prompt(
    user_team: list[str],
    opponent_team: list[str] | None = None,
    battle_format: str = "singles",
    strategy_focus: str = "balanced",
) -> list[Message]:
    """Battle strategy planning prompt.

    Args:
        user_team: List of Pokemon names in user's team
        opponent_team: Optional list of opponent's Pokemon
        battle_format: singles, doubles, or multi
        strategy_focus: offensive, defensive, balanced, or utility
    """
    logger.info(
        "battle_strategy_prompt called",
        user_team=user_team,
        opponent_team=opponent_team,
        battle_format=battle_format,
        strategy_focus=strategy_focus,
    )

    try:
        result = await battle_prompts.create_battle_strategy_prompt(
            user_team, opponent_team, battle_format, strategy_focus
        )
        return _prompt_messages(result)
    except Exception as e:
        logger.error("battle_strategy_prompt failed", error=str(e))
        return [UserMessage(f"❌ Error: {str(e)}")]


@app.prompt("battle/matchup-analysis")
async def matchup_analysis_prompt(
    pokemon1: str, pokemon2: str, scenario: str = "1v1", environment: str = "neutral"
) -> list[Message]:
    """Pokemon matchup analysis prompt.

    Args:
        pokemon1: First Pokemon name
        pokemon2: Second Pokemon name
        scenario: 1v1, team-context, or switch-prediction
        environment: neutral, weather, terrain effects
    """
    logger.info(
        "matchup_analysis_prompt called",
        pokemon1=pokemon1,
        pokemon2=pokemon2,
        scenario=scenario,
        environment=environment,
    )

    try:
        result = await battle_prompts.create_matchup_analysis_prompt(
            pokemon1, pokemon2, scenario, environment
        )
        return _prompt_messages(result)
    except Exception as e:
        logger.error("matchup_analysis_prompt failed", error=str(e))
        return [UserMessage(f"❌ Error: {str(e)}")]


@app.prompt("battle/team-preview")
async def team_preview_prompt(
    team: list[str],
    analysis_depth: str = "standard",
    focus_areas: list[str] | None = None,
) -> list[Message]:
    """Team preview analysis prompt.

    Args:
        team: List of Pokemon names to analyze
        analysis_depth: quick, standard, or comprehensive
        focus_areas: specific areas to focus on (offense, defense, synergy, etc.)
    """
    logger.info(
        "team_preview_prompt called",
        team=team,
        analysis_depth=analysis_depth,
        focus_areas=focus_areas,
    )

    try:
        result = await battle_prompts.create_team_preview_prompt(
            team, analysis_depth, focus_areas
        )
        return _prompt_messages(result)
    except Exception as e:
        logger.error("team_preview_prompt failed", error=str(e))
        return [UserMessage(f"❌ Error: {str(e)}")]


async def create_server() -> MCPServer:
    """Create and configure the MCP server."""
    logger.info(
        "Creating MCP server", server_name="Pokemon MCP Server", version="0.1.0"
    )

    return app


def run_server() -> None:
    """Run the MCP server."""
    logger.info("[SERVER] Starting", transport=settings.transport)

    try:
        if settings.transport == "stdio":
            logging.getLogger("uvicorn").setLevel(logging.WARNING)
            logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
            app.run(transport="stdio")
        else:
            import uvicorn

            # Passing the real bind host keeps DNS rebinding protection off, as in v1;
            # with the default (127.0.0.1) public Host headers would get 421.
            uvicorn.run(
                app.streamable_http_app(host=settings.server_host),
                host=settings.server_host,
                port=settings.server_port,
                workers=settings.uvicorn_workers,
                timeout_keep_alive=settings.uvicorn_timeout_keep_alive,
                access_log=settings.uvicorn_access_log,
            )
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error("Server error", error=str(e), exc_info=True)
        raise


if __name__ == "__main__":
    run_server()
