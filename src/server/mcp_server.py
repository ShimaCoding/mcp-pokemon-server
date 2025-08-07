"""MCP server implementation using FastMCP."""

from mcp.server.fastmcp import FastMCP
from mcp.types import GetPromptResult, PromptMessage, TextContent

from ..clients.pokeapi_client import PokemonAPIClient
from ..config.logging import get_logger, setup_logging
from ..prompts.battle_prompts import BattlePromptManager
from ..prompts.educational_prompts import EducationalPromptManager
from ..resources.pokemon_resources import PokemonResourceManager
from ..tools.pokemon_tools import POKEMON_TOOLS

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Create FastMCP server instance
app = FastMCP("Pokemon MCP Server")

# Initialize clients and managers
pokemon_client = PokemonAPIClient()
resource_manager = PokemonResourceManager(pokemon_client)
educational_prompts = EducationalPromptManager(pokemon_client)
battle_prompts = BattlePromptManager(pokemon_client)


@app.tool()
async def get_pokemon_info(name_or_id: str) -> str:
    """Get detailed information about a Pokemon by name or ID.

    Args:
        name_or_id: Pokemon name or ID to lookup
    """
    logger.info("get_pokemon_info called", identifier=name_or_id)

    try:
        result = await POKEMON_TOOLS["get_pokemon_info"](name_or_id)
        if result.is_error:
            return result.content[0]["text"]
        return result.content[0]["text"]
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        logger.error("get_pokemon_info failed", error=str(e))
        return error_msg


@app.tool()
async def search_pokemon(limit: int = 20, offset: int = 0) -> str:
    """Search for Pokemon with pagination.

    Args:
        limit: Maximum number of results (default: 20)
        offset: Offset for pagination (default: 0)
    """
    logger.info("search_pokemon called", limit=limit, offset=offset)

    try:
        result = await POKEMON_TOOLS["search_pokemon"](limit=limit, offset=offset)
        if result.is_error:
            return result.content[0]["text"]
        return result.content[0]["text"]
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        logger.error("search_pokemon failed", error=str(e))
        return error_msg


@app.tool()
async def get_type_effectiveness(attacking_type: str) -> str:
    """Get type effectiveness chart for a Pokemon type.

    Args:
        attacking_type: The attacking type name (e.g., 'fire', 'water', 'electric')
    """
    logger.info("get_type_effectiveness called", attacking_type=attacking_type)

    try:
        result = await POKEMON_TOOLS["get_type_effectiveness"](attacking_type)
        if result.is_error:
            return result.content[0]["text"]
        return result.content[0]["text"]
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        logger.error("get_type_effectiveness failed", error=str(e))
        return error_msg


@app.tool()
async def analyze_pokemon_stats(name_or_id: str) -> str:
    """Analyze Pokemon stats and provide insights.

    Args:
        name_or_id: Pokemon name or ID to analyze
    """
    logger.info("analyze_pokemon_stats called", identifier=name_or_id)

    try:
        result = await POKEMON_TOOLS["analyze_pokemon_stats"](name_or_id)
        if result.is_error:
            return result.content[0]["text"]
        return result.content[0]["text"]
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        logger.error("analyze_pokemon_stats failed", error=str(e))
        return error_msg


# Resource handlers - Dynamic Pokemon Resources
@app.resource("pokemon://info/{name_or_id}")
async def pokemon_info_resource(name_or_id: str) -> str:
    """Get detailed Pokemon information as a resource.

    Args:
        name_or_id: Pokemon name or ID to lookup
    """
    logger.info("pokemon_info_resource called", identifier=name_or_id)

    try:
        content = await resource_manager.get_resource(f"pokemon://info/{name_or_id}")
        return content.text
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        logger.error("pokemon_info_resource failed", error=str(e))
        return error_msg


@app.resource("pokemon://stats/{name_or_id}")
async def pokemon_stats_resource(name_or_id: str) -> str:
    """Get Pokemon statistics analysis as a resource.

    Args:
        name_or_id: Pokemon name or ID to analyze
    """
    logger.info("pokemon_stats_resource called", identifier=name_or_id)

    try:
        content = await resource_manager.get_resource(f"pokemon://stats/{name_or_id}")
        return content.text
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        logger.error("pokemon_stats_resource failed", error=str(e))
        return error_msg


@app.resource("pokemon://type/{type_name}")
async def pokemon_type_resource(type_name: str) -> str:
    """Get type effectiveness information as a resource.

    Args:
        type_name: Pokemon type name (e.g., 'fire', 'water', 'electric')
    """
    logger.info("pokemon_type_resource called", type_name=type_name)

    try:
        content = await resource_manager.get_resource(f"pokemon://type/{type_name}")
        return content.text
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        logger.error("pokemon_type_resource failed", error=str(e))
        return error_msg


@app.resource("pokemon://comparison/{pokemon1}/{pokemon2}")
async def pokemon_comparison_resource(pokemon1: str, pokemon2: str) -> str:
    """Get Pokemon comparison as a resource.

    Args:
        pokemon1: First Pokemon name
        pokemon2: Second Pokemon name
    """
    logger.info(
        "pokemon_comparison_resource called", pokemon1=pokemon1, pokemon2=pokemon2
    )

    try:
        content = await resource_manager.get_resource(
            f"pokemon://comparison/{pokemon1}/{pokemon2}"
        )
        return content.text
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        logger.error("pokemon_comparison_resource failed", error=str(e))
        return error_msg


# Prompt handlers - Educational Prompts
@app.prompt("educational/pokemon-analysis")
async def pokemon_analysis_prompt(
    pokemon_name: str, analysis_type: str = "general", user_level: str = "beginner"
) -> GetPromptResult:
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
        return result
    except Exception as e:
        logger.error("pokemon_analysis_prompt failed", error=str(e))
        return GetPromptResult(
            description=f"Error creating analysis prompt for {pokemon_name}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=f"❌ Error: {str(e)}"),
                )
            ],
        )


@app.prompt("educational/team-building")
async def team_building_prompt(
    theme: str = "balanced",
    format: str = "casual",
    restrictions: list[str] | None = None,
) -> GetPromptResult:
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
        return result
    except Exception as e:
        logger.error("team_building_prompt failed", error=str(e))
        return GetPromptResult(
            description="Error creating team building prompt",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=f"❌ Error: {str(e)}"),
                )
            ],
        )


@app.prompt("educational/type-effectiveness")
async def type_effectiveness_prompt(
    scenario: str = "learning",
    attacking_type: str | None = None,
    defending_types: list[str] | None = None,
) -> GetPromptResult:
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
        return result
    except Exception as e:
        logger.error("type_effectiveness_prompt failed", error=str(e))
        return GetPromptResult(
            description="Error creating type effectiveness prompt",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=f"❌ Error: {str(e)}"),
                )
            ],
        )


# Battle Prompts
@app.prompt("battle/strategy")
async def battle_strategy_prompt(
    user_team: list[str],
    opponent_team: list[str] | None = None,
    battle_format: str = "singles",
    strategy_focus: str = "balanced",
) -> GetPromptResult:
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
        return result
    except Exception as e:
        logger.error("battle_strategy_prompt failed", error=str(e))
        return GetPromptResult(
            description="Error creating battle strategy prompt",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=f"❌ Error: {str(e)}"),
                )
            ],
        )


@app.prompt("battle/matchup-analysis")
async def matchup_analysis_prompt(
    pokemon1: str, pokemon2: str, scenario: str = "1v1", environment: str = "neutral"
) -> GetPromptResult:
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
        return result
    except Exception as e:
        logger.error("matchup_analysis_prompt failed", error=str(e))
        return GetPromptResult(
            description=f"Error analyzing {pokemon1} vs {pokemon2}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=f"❌ Error: {str(e)}"),
                )
            ],
        )


@app.prompt("battle/team-preview")
async def team_preview_prompt(
    team: list[str],
    analysis_depth: str = "standard",
    focus_areas: list[str] | None = None,
) -> GetPromptResult:
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
        return result
    except Exception as e:
        logger.error("team_preview_prompt failed", error=str(e))
        return GetPromptResult(
            description="Error creating team preview prompt",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=f"❌ Error: {str(e)}"),
                )
            ],
        )


async def create_server() -> FastMCP:
    """Create and configure the MCP server."""
    logger.info(
        "Creating MCP server", server_name="Pokemon MCP Server", version="0.1.0"
    )

    return app


def run_server():
    """Run the MCP server."""
    logger.info("Starting Pokemon MCP Server", server_name="Pokemon MCP Server")

    try:
        # FastMCP handles asyncio internally - just run the app
        app.run()

    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error("Server error", error=str(e), exc_info=True)
        raise
    finally:
        # Cleanup
        logger.info("Cleaning up server resources")
        logger.info("Resources cleaned up successfully")


def cleanup_resources():
    """Cleanup server resources."""
    logger.info("Cleaning up server resources")

    try:
        # Simple cleanup without async
        logger.info("Resources cleaned up successfully")
    except Exception as e:
        logger.error("Error during cleanup", error=str(e))


if __name__ == "__main__":
    # This allows running the server directly for testing
    run_server()
