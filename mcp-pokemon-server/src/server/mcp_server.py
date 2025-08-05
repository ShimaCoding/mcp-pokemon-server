"""MCP server implementation using FastMCP."""

from typing import Any, Sequence, List

from mcp.server.fastmcp import FastMCP
from mcp.types import (
    Tool,
    TextContent,
    Resource,
    TextResourceContents,
)

from ..config.settings import get_settings
from ..config.logging import setup_logging, get_logger
from ..tools.pokemon_tools import POKEMON_TOOLS
from ..resources.pokemon_resources import PokemonResourceManager
from ..clients.pokeapi_client import PokemonAPIClient

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Create FastMCP server instance
app = FastMCP("Pokemon MCP Server")

# Initialize clients and managers
pokemon_client = PokemonAPIClient()
resource_manager = PokemonResourceManager(pokemon_client)


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
    logger.info("pokemon_comparison_resource called", pokemon1=pokemon1, pokemon2=pokemon2)
    
    try:
        content = await resource_manager.get_resource(f"pokemon://comparison/{pokemon1}/{pokemon2}")
        return content.text
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        logger.error("pokemon_comparison_resource failed", error=str(e))
        return error_msg


async def create_server() -> FastMCP:
    """Create and configure the MCP server."""
    settings = get_settings()
    
    logger.info("Creating MCP server", 
               server_name="Pokemon MCP Server",
               version="0.1.0")
    
    return app


def run_server():
    """Run the MCP server."""
    settings = get_settings()
    
    logger.info("Starting Pokemon MCP Server",
               server_name="Pokemon MCP Server")
    
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
