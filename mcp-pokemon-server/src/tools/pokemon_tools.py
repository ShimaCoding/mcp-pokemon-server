"""Basic Pokemon tools for MCP server."""

from typing import List, Dict, Any, Optional
import json

from ..clients.pokeapi_client import get_pokemon_client, PokemonNotFoundError, PokemonAPIError
from ..models.response_models import (
    PokemonInfoResponse, 
    PokemonSearchResponse, 
    TypeEffectivenessResponse,
    StatsAnalysisResponse,
    ResponseStatus,
    ToolResult
)
from ..config.logging import get_logger

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
        
        response = PokemonInfoResponse(
            status=ResponseStatus.SUCCESS,
            message=f"Successfully retrieved information for {pokemon.name}",
            pokemon=pokemon
        )
        
        # Format for MCP response
        content = [{
            "type": "text",
            "text": f"# {pokemon.name.title()} (#{pokemon.id})\n\n"
                   f"**Height:** {pokemon.height_meters:.1f}m\n"
                   f"**Weight:** {pokemon.weight_kg:.1f}kg\n"
                   f"**Types:** {', '.join(pokemon.type_names)}\n"
                   f"**Base Experience:** {pokemon.base_experience or 'Unknown'}\n\n"
                   f"## Stats\n" +
                   "\n".join([f"- **{stat.title()}:** {value}" 
                            for stat, value in pokemon.stat_dict.items()]) + "\n\n"
                   f"## Abilities\n" +
                   "\n".join([f"- {ability.ability['name'].title()}" + 
                            (" (Hidden)" if ability.is_hidden else "")
                            for ability in pokemon.abilities])
        }]
        
        return ToolResult(content=content)
        
    except PokemonNotFoundError:
        error_content = [{
            "type": "text", 
            "text": f"❌ Pokemon '{name_or_id}' not found. Please check the name or ID."
        }]
        return ToolResult(content=error_content, is_error=True)
        
    except Exception as e:
        logger.error("Error getting Pokemon info", identifier=name_or_id, error=str(e))
        error_content = [{
            "type": "text",
            "text": f"❌ Error retrieving Pokemon information: {str(e)}"
        }]
        return ToolResult(content=error_content, is_error=True)


async def search_pokemon(query: Optional[str] = None, limit: int = 20, offset: int = 0) -> ToolResult:
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
        
        content = [{
            "type": "text",
            "text": f"# Pokemon Search Results\n\n"
                   f"**Total Pokemon:** {search_result.count}\n"
                   f"**Showing:** {len(search_result.results)} results (offset: {offset})\n\n" +
                   "\n".join(pokemon_list) + "\n\n"
                   f"*Use get_pokemon_info with a name or ID for detailed information.*"
        }]
        
        return ToolResult(content=content)
        
    except Exception as e:
        logger.error("Error searching Pokemon", error=str(e))
        error_content = [{
            "type": "text",
            "text": f"❌ Error searching Pokemon: {str(e)}"
        }]
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
            "Super Effective (2x)": [t["name"] for t in damage_relations.get("double_damage_to", [])],
            "Not Very Effective (0.5x)": [t["name"] for t in damage_relations.get("half_damage_to", [])],
            "No Effect (0x)": [t["name"] for t in damage_relations.get("no_damage_to", [])]
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
        error_content = [{
            "type": "text",
            "text": f"❌ Type '{attacking_type}' not found. Please check the type name."
        }]
        return ToolResult(content=error_content, is_error=True)
        
    except Exception as e:
        logger.error("Error getting type effectiveness", attacking_type=attacking_type, error=str(e))
        error_content = [{
            "type": "text",
            "text": f"❌ Error retrieving type effectiveness: {str(e)}"
        }]
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
            content_text += f"**{stat_name.title().replace('-', ' ')}:** {value} `{bar}`\n"
        
        content_text += f"\n*Based on base stats only. Actual performance depends on level, nature, IVs, and EVs.*"
        
        content = [{"type": "text", "text": content_text}]
        return ToolResult(content=content)
        
    except PokemonNotFoundError:
        error_content = [{
            "type": "text",
            "text": f"❌ Pokemon '{name_or_id}' not found. Please check the name or ID."
        }]
        return ToolResult(content=error_content, is_error=True)
        
    except Exception as e:
        logger.error("Error analyzing Pokemon stats", identifier=name_or_id, error=str(e))
        error_content = [{
            "type": "text",
            "text": f"❌ Error analyzing Pokemon stats: {str(e)}"
        }]
        return ToolResult(content=error_content, is_error=True)


# Tool registry for easy access
POKEMON_TOOLS = {
    "get_pokemon_info": get_pokemon_info,
    "search_pokemon": search_pokemon,
    "get_type_effectiveness": get_type_effectiveness,
    "analyze_pokemon_stats": analyze_pokemon_stats,
}
