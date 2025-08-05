"""MCP server implementation using FastMCP."""

import asyncio
from typing import Any, Sequence

from mcp.server.fastmcp import FastMCP
from mcp.server.models import InitializationOptions
from mcp.types import (
    CallToolRequest,
    ListToolsRequest,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)

from ..config.settings import get_settings
from ..config.logging import setup_logging, get_logger
from ..clients.pokeapi_client import close_pokemon_client
from ..tools.pokemon_tools import POKEMON_TOOLS

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Create FastMCP server instance
mcp_server = FastMCP("Pokemon MCP Server")


@mcp_server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available tools."""
    logger.info("Listing available tools")
    
    tools = [
        Tool(
            name="get_pokemon_info",
            description="Get detailed information about a Pokemon by name or ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "name_or_id": {
                        "type": "string",
                        "description": "Pokemon name or ID to lookup"
                    }
                },
                "required": ["name_or_id"]
            }
        ),
        Tool(
            name="search_pokemon",
            description="Search for Pokemon with pagination",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (optional)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results",
                        "default": 20
                    },
                    "offset": {
                        "type": "integer", 
                        "description": "Offset for pagination",
                        "default": 0
                    }
                }
            }
        ),
        Tool(
            name="get_type_effectiveness",
            description="Get type effectiveness chart for a Pokemon type",
            inputSchema={
                "type": "object",
                "properties": {
                    "attacking_type": {
                        "type": "string",
                        "description": "The attacking type name (e.g., 'fire', 'water', 'electric')"
                    }
                },
                "required": ["attacking_type"]
            }
        ),
        Tool(
            name="analyze_pokemon_stats",
            description="Analyze Pokemon stats and provide insights",
            inputSchema={
                "type": "object",
                "properties": {
                    "name_or_id": {
                        "type": "string",
                        "description": "Pokemon name or ID to analyze"
                    }
                },
                "required": ["name_or_id"]
            }
        )
    ]
    
    logger.info("Tools listed successfully", tool_count=len(tools))
    return tools


@mcp_server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
    """Handle tool calls."""
    logger.info("Tool called", tool_name=name, arguments=arguments)
    
    try:
        # Get the tool function
        tool_function = POKEMON_TOOLS.get(name)
        if not tool_function:
            error_msg = f"Unknown tool: {name}"
            logger.error(error_msg)
            return [TextContent(type="text", text=f"❌ {error_msg}")]
        
        # Call the tool with provided arguments
        result = await tool_function(**arguments)
        
        # Convert ToolResult to MCP response format
        response_content = []
        for content_item in result.content:
            if content_item["type"] == "text":
                response_content.append(TextContent(
                    type="text", 
                    text=content_item["text"]
                ))
            # Add support for other content types as needed
        
        logger.info("Tool executed successfully", 
                   tool_name=name, 
                   success=not result.is_error)
        
        return response_content
        
    except Exception as e:
        error_msg = f"Error executing tool '{name}': {str(e)}"
        logger.error("Tool execution failed", 
                    tool_name=name, 
                    error=str(e), 
                    exc_info=True)
        return [TextContent(type="text", text=f"❌ {error_msg}")]


async def create_server() -> FastMCP:
    """Create and configure the MCP server."""
    settings = get_settings()
    
    logger.info("Creating MCP server", 
               server_name="Pokemon MCP Server",
               version="0.1.0")
    
    # Server is already created above, just return it
    return mcp_server


async def run_server():
    """Run the MCP server."""
    settings = get_settings()
    
    logger.info("Starting Pokemon MCP Server",
               host=settings.server_host,
               port=settings.server_port,
               debug=settings.debug)
    
    try:
        # Create server instance
        server = await create_server()
        
        # Run the server
        await server.run(
            transport="stdio"  # MCP typically uses stdio transport
        )
        
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error("Server error", error=str(e), exc_info=True)
        raise
    finally:
        # Cleanup
        await cleanup_resources()


async def cleanup_resources():
    """Cleanup server resources."""
    logger.info("Cleaning up server resources")
    
    try:
        await close_pokemon_client()
        logger.info("Resources cleaned up successfully")
    except Exception as e:
        logger.error("Error during cleanup", error=str(e))


if __name__ == "__main__":
    # This allows running the server directly for testing
    asyncio.run(run_server())
