"""Interactive elicitation tools for Pokemon MCP server."""

import re
from typing import Any, Dict, List, Optional

from ..clients.pokeapi_client import PokemonNotFoundError, get_pokemon_client
from ..config.logging import get_logger
from ..models.response_models import ToolResult

logger = get_logger(__name__)


class ElicitationState:
    """Helper class to manage elicitation state."""

    def __init__(self, state: Dict[str, Any]):
        self.state = state

    def get(self, key: str, default: Any = None) -> Any:
        """Get value from state."""
        return self.state.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set value in state."""
        self.state[key] = value

    def update(self, updates: Dict[str, Any]) -> None:
        """Update multiple values in state."""
        self.state.update(updates)

    def clear(self) -> None:
        """Clear all state."""
        self.state.clear()


def create_elicit_response(prompt: str, state: Dict[str, Any]) -> ToolResult:
    """Helper to create an elicitation response."""
    content = [
        {
            "type": "text",
            "text": f"🤖 {prompt}",
        }
    ]
    return ToolResult(content=content, elicit={"prompt": prompt, "state": state})


async def get_pokemon_info_elicit(
    pokemon_name: Optional[str] = None, state: Optional[Dict[str, Any]] = None
) -> ToolResult:
    """
    Interactive Pokemon information retrieval with elicitation.

    Example 1: Simple elicitation - asks for Pokemon name if not provided.

    Args:
        pokemon_name: Optional Pokemon name from user input
        state: Conversation state for elicitation

    Returns:
        ToolResult with Pokemon info or elicitation prompt
    """
    logger.info(
        "Starting interactive Pokemon info elicitation",
        pokemon_name=pokemon_name,
        state=state,
    )

    elicit_state = ElicitationState(state or {})

    # Get Pokemon name from parameter or state
    name = pokemon_name or elicit_state.get("pokemon_name")

    if not name:
        return create_elicit_response(
            "¿De qué Pokémon quieres saber información? (Escribe el nombre o número)",
            elicit_state.state,
        )

    # Validate and normalize the name
    name = name.lower().strip()

    try:
        client = await get_pokemon_client()
        pokemon = await client.get_pokemon(name)

        # Success - return Pokemon information
        content = [
            {
                "type": "text",
                "text": f"# ✨ {pokemon.name.title()} (#{pokemon.id})\n\n"
                f"**Altura:** {pokemon.height_meters:.1f}m\n"
                f"**Peso:** {pokemon.weight_kg:.1f}kg\n"
                f"**Tipos:** {', '.join([t.title() for t in pokemon.type_names])}\n"
                f"**Experiencia Base:** {pokemon.base_experience or 'Desconocida'}\n\n"
                f"## 📊 Estadísticas\n"
                + "\n".join(
                    [
                        f"- **{stat.replace('-', ' ').title()}:** {value}"
                        for stat, value in pokemon.stat_dict.items()
                    ]
                )
                + "\n\n"
                "## 🎯 Habilidades\n"
                + "\n".join(
                    [
                        f"- {ability.ability['name'].title()}"
                        + (" (Oculta)" if ability.is_hidden else "")
                        for ability in pokemon.abilities
                    ]
                )
                + "\n\n*¿Quieres información de otro Pokémon? ¡Solo dímelo!*",
            }
        ]

        return ToolResult(content=content)

    except PokemonNotFoundError:
        # Pokemon not found - ask again with helpful message
        return create_elicit_response(
            f"❌ No encontré información para '{name}'. "
            "¿Puedes escribir otro nombre? (Ejemplos: pikachu, charizard, 25)",
            {},  # Reset state on error
        )

    except Exception as e:
        logger.error(
            "Error in Pokemon info elicitation", pokemon_name=name, error=str(e)
        )
        return create_elicit_response(
            f"❌ Ocurrió un error al buscar '{name}'. ¿Puedes intentar con otro nombre?",
            {},  # Reset state on error
        )


async def build_pokemon_team_elicit(
    pokemon_name: Optional[str] = None, state: Optional[Dict[str, Any]] = None
) -> ToolResult:
    """
    Interactive Pokemon team builder with elicitation.

    Example 2: Intermediate elicitation - builds a team of 3 Pokemon step by step.

    Args:
        pokemon_name: Pokemon name to add to team
        state: Conversation state containing team progress

    Returns:
        ToolResult with team status or elicitation prompt
    """
    logger.info(
        "Building Pokemon team interactively", pokemon_name=pokemon_name, state=state
    )

    elicit_state = ElicitationState(state or {})
    team = elicit_state.get("team", [])
    team_size = 3  # Target team size

    # If we have a new Pokemon name, validate it first
    if pokemon_name:
        name = pokemon_name.lower().strip()

        # Check for duplicates
        existing_names = [p.get("name", "").lower() for p in team]
        if name in existing_names:
            return create_elicit_response(
                f"❌ Ya tienes a {name.title()} en tu equipo. "
                f"Elige un Pokémon diferente para la posición #{len(team) + 1}:",
                elicit_state.state,
            )

        try:
            client = await get_pokemon_client()
            pokemon = await client.get_pokemon(name)

            # Add valid Pokemon to team
            team.append(
                {
                    "name": pokemon.name,
                    "id": pokemon.id,
                    "types": pokemon.type_names,
                    "total_stats": sum(pokemon.stat_dict.values()),
                }
            )
            elicit_state.set("team", team)

        except PokemonNotFoundError:
            return create_elicit_response(
                f"❌ '{name}' no es un Pokémon válido. "
                f"Por favor, ingresa un nombre correcto para la posición #{len(team) + 1}:",
                elicit_state.state,
            )
        except Exception as e:
            logger.error(
                "Error validating Pokemon for team", pokemon_name=name, error=str(e)
            )
            return create_elicit_response(
                f"❌ Error al validar '{name}'. "
                f"Intenta con otro Pokémon para la posición #{len(team) + 1}:",
                elicit_state.state,
            )

    # Check if team is complete
    if len(team) < team_size:
        # Show current progress
        progress_text = ""
        if team:
            progress_text = (
                "\n\n**Equipo actual:**\n"
                + "\n".join(
                    [
                        f"{i+1}. {p['name'].title()} (#{p['id']}) - "
                        f"Tipos: {', '.join([t.title() for t in p['types']])}"
                        for i, p in enumerate(team)
                    ]
                )
                + "\n"
            )

        return create_elicit_response(
            f"🎯 Construyamos tu equipo Pokémon de {team_size}."
            f"{progress_text}"
            f"Dime el nombre del Pokémon #{len(team) + 1}:",
            elicit_state.state,
        )

    # Team is complete - show final result
    total_team_stats = sum(p["total_stats"] for p in team)
    avg_stats = total_team_stats / len(team)

    # Analyze team composition
    all_types = []
    for pokemon in team:
        all_types.extend(pokemon["types"])
    type_coverage = len(set(all_types))

    content = [
        {
            "type": "text",
            "text": f"# 🎉 ¡Equipo Pokémon Completo!\n\n"
            f"## 👥 Tu Equipo\n"
            + "\n".join(
                [
                    f"**{i+1}. {p['name'].title()}** (#{p['id']})\n"
                    f"   - Tipos: {', '.join([t.title() for t in p['types']])}\n"
                    f"   - Stats totales: {p['total_stats']}\n"
                    for i, p in enumerate(team)
                ]
            )
            + f"\n## 📈 Análisis del Equipo\n"
            f"- **Estadísticas promedio:** {avg_stats:.1f}\n"
            f"- **Cobertura de tipos:** {type_coverage} tipos únicos\n"
            f"- **Estadísticas totales:** {total_team_stats}\n\n"
            f"*¡Excelente equipo! ¿Quieres crear otro equipo?*",
        }
    ]

    return ToolResult(content=content)


async def suggest_pokemon_by_criteria_elicit(
    user_input: Optional[str] = None, state: Optional[Dict[str, Any]] = None
) -> ToolResult:
    """
    Advanced interactive Pokemon suggestion with multiple criteria elicitation.

    Example 3: Advanced elicitation - suggests Pokemon based on type and role preferences.

    Args:
        user_input: User's response to current elicitation step
        state: Conversation state containing preferences and suggestions

    Returns:
        ToolResult with suggestion or elicitation prompt
    """
    logger.info(
        "Starting Pokemon suggestion elicitation", user_input=user_input, state=state
    )

    elicit_state = ElicitationState(state or {})

    # Valid types and roles for validation
    VALID_TYPES = [
        "normal",
        "fighting",
        "flying",
        "poison",
        "ground",
        "rock",
        "bug",
        "ghost",
        "steel",
        "fire",
        "water",
        "grass",
        "electric",
        "psychic",
        "ice",
        "dragon",
        "dark",
        "fairy",
    ]

    VALID_ROLES = ["ataque", "defensa", "soporte", "velocidad", "equilibrado"]

    # Step 1: Get Pokemon type preference
    poke_type = elicit_state.get("type")
    if not poke_type and user_input:
        # Validate type input
        type_input = user_input.lower().strip()

        # Handle Spanish type names
        type_translations = {
            "fuego": "fire",
            "agua": "water",
            "planta": "grass",
            "hierba": "grass",
            "eléctrico": "electric",
            "electrico": "electric",
            "psíquico": "psychic",
            "psiquico": "psychic",
            "hielo": "ice",
            "dragón": "dragon",
            "dragon": "dragon",
            "siniestro": "dark",
            "oscuro": "dark",
            "hada": "fairy",
            "lucha": "fighting",
            "veneno": "poison",
            "tierra": "ground",
            "roca": "rock",
            "bicho": "bug",
            "fantasma": "ghost",
            "acero": "steel",
            "volador": "flying",
        }

        normalized_type = type_translations.get(type_input, type_input)

        if normalized_type in VALID_TYPES:
            elicit_state.set("type", normalized_type)
            poke_type = normalized_type
        else:
            return create_elicit_response(
                f"❌ '{user_input}' no es un tipo válido. "
                f"Tipos disponibles: {', '.join(VALID_TYPES[:8])}... "
                f"¿Qué tipo prefieres?",
                elicit_state.state,
            )

    if not poke_type:
        return create_elicit_response(
            "🎯 ¡Te ayudo a encontrar el Pokémon perfecto!\n\n"
            "¿Qué tipo de Pokémon prefieres? "
            "(Ejemplos: fuego, agua, planta, eléctrico, dragón...)",
            elicit_state.state,
        )

    # Step 2: Get role preference
    role = elicit_state.get("role")
    if not role and user_input and poke_type:
        role_input = user_input.lower().strip()
        if role_input in VALID_ROLES:
            elicit_state.set("role", role_input)
            role = role_input
        else:
            return create_elicit_response(
                f"❌ '{user_input}' no es un rol válido. "
                f"¿Qué rol buscas?\n"
                f"- **ataque**: Pokémon ofensivos\n"
                f"- **defensa**: Pokémon defensivos\n"
                f"- **soporte**: Pokémon de apoyo\n"
                f"- **velocidad**: Pokémon rápidos\n"
                f"- **equilibrado**: Pokémon versátiles",
                elicit_state.state,
            )

    if not role:
        return create_elicit_response(
            f"Perfecto, tipo {poke_type.title()} 🔥\n\n"
            f"¿Qué rol buscas?\n"
            f"- **ataque**: Pokémon ofensivos\n"
            f"- **defensa**: Pokémon defensivos\n"
            f"- **soporte**: Pokémon de apoyo\n"
            f"- **velocidad**: Pokémon rápidos\n"
            f"- **equilibrado**: Pokémon versátiles",
            elicit_state.state,
        )

    # Handle restart command at any point
    if user_input and user_input.lower().strip() == "reiniciar":
        return create_elicit_response(
            "🔄 ¡Empecemos de nuevo!\n\n" "¿Qué tipo de Pokémon prefieres?", {}
        )

    # Step 3: Generate or confirm suggestion
    current_suggestion = elicit_state.get("current_suggestion")
    rejected_suggestions = elicit_state.get("rejected_suggestions", [])

    if not current_suggestion:
        # Generate first suggestion
        try:
            suggestions = await _get_pokemon_suggestions_by_criteria(
                poke_type, role, excluded=rejected_suggestions
            )

            if not suggestions:
                return create_elicit_response(
                    f"❌ No encontré Pokémon de tipo {poke_type} con rol {role}. "
                    f"¿Quieres intentar con otro tipo o rol? (escribe 'reiniciar')",
                    {},
                )

            suggestion = suggestions[0]
            elicit_state.set("current_suggestion", suggestion)
            elicit_state.set("available_suggestions", suggestions[1:])
            current_suggestion = suggestion  # Update the local variable

        except Exception as e:
            logger.error(
                "Error generating Pokemon suggestions",
                type=poke_type,
                role=role,
                error=str(e),
            )
            return create_elicit_response(
                f"❌ Error al buscar sugerencias. ¿Quieres intentar de nuevo? (escribe 'reiniciar')",
                {},
            )

    # Handle user response to suggestion
    if user_input and current_suggestion:
        response = user_input.lower().strip()

        if response in ["sí", "si", "yes", "ok", "vale", "perfecto", "me gusta"]:
            # User accepted the suggestion
            suggestion = current_suggestion
            content = [
                {
                    "type": "text",
                    "text": f"# 🎉 ¡Excelente elección!\n\n"
                    f"**{suggestion['name'].title()}** (#{suggestion['id']})\n"
                    f"- **Tipo:** {', '.join([t.title() for t in suggestion['types']])}\n"
                    f"- **Rol:** {role.title()}\n"
                    f"- **Stats destacadas:** {suggestion['highlight']}\n\n"
                    f"**¿Por qué es perfecto para ti?**\n{suggestion['reason']}\n\n"
                    f"*¿Quieres otra sugerencia para un equipo completo?*",
                }
            ]
            return ToolResult(content=content)

        elif response in ["no", "nah", "otro", "siguiente", "no me gusta"]:
            # User rejected suggestion - try next one
            rejected_suggestions.append(current_suggestion["name"])
            elicit_state.set("rejected_suggestions", rejected_suggestions)

            available = elicit_state.get("available_suggestions", [])
            if available:
                next_suggestion = available[0]
                elicit_state.set("current_suggestion", next_suggestion)
                elicit_state.set("available_suggestions", available[1:])
                current_suggestion = next_suggestion
            else:
                # No more suggestions
                return create_elicit_response(
                    f"😅 No tengo más sugerencias de tipo {poke_type} con rol {role}. "
                    f"¿Quieres intentar con otro tipo o rol? (escribe 'reiniciar')",
                    {},
                )

    # Show current suggestion and ask for confirmation
    if current_suggestion:
        return create_elicit_response(
            f"🎯 Te sugiero **{current_suggestion['name'].title()}**!\n\n"
            f"- **Tipo:** {', '.join([t.title() for t in current_suggestion['types']])}\n"
            f"- **Fortaleza:** {current_suggestion['highlight']}\n"
            f"- **¿Por qué?** {current_suggestion['reason']}\n\n"
            f"¿Te gusta esta opción? (sí/no, o 'otro' para ver más opciones)",
            elicit_state.state,
        )

    # Fallback
    return create_elicit_response(
        "❌ Algo salió mal. ¿Quieres empezar de nuevo? (escribe 'reiniciar')", {}
    )


async def _get_pokemon_suggestions_by_criteria(
    poke_type: str, role: str, excluded: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Helper function to get Pokemon suggestions based on type and role.

    This is a simplified implementation. In a real application, you might:
    - Query a database with Pokemon stats
    - Use machine learning to recommend based on battle performance
    - Implement more sophisticated filtering logic
    """
    excluded = excluded or []

    try:
        client = await get_pokemon_client()

        # Get Pokemon of the specified type
        type_data = await client.get_type_info(poke_type)
        type_pokemon = type_data.get("pokemon", [])

        suggestions = []

        # Sample a few Pokemon from this type (simplified logic)
        for i, pokemon_entry in enumerate(type_pokemon[:20]):  # Limit to first 20
            pokemon_name = pokemon_entry["pokemon"]["name"]

            if pokemon_name in excluded:
                continue

            try:
                pokemon = await client.get_pokemon(pokemon_name)
                stats = pokemon.stat_dict

                # Simple role-based filtering
                suggestion = _analyze_pokemon_for_role(pokemon, role, stats)
                if suggestion:
                    suggestions.append(suggestion)

                if len(suggestions) >= 5:  # Limit suggestions
                    break

            except Exception:
                continue  # Skip problematic Pokemon

        return suggestions

    except Exception as e:
        logger.error(
            "Error getting Pokemon suggestions", type=poke_type, role=role, error=str(e)
        )
        return []


def _analyze_pokemon_for_role(
    pokemon: Any, role: str, stats: Dict[str, int]
) -> Optional[Dict[str, Any]]:
    """Analyze if a Pokemon fits a given role."""
    total_stats = sum(stats.values())

    # Skip very weak Pokemon (likely early forms)
    if total_stats < 300:
        return None

    # Role-based analysis
    if role == "ataque":
        if stats.get("attack", 0) >= 80 or stats.get("special-attack", 0) >= 80:
            highlight = (
                f"Ataque: {max(stats.get('attack', 0), stats.get('special-attack', 0))}"
            )
            reason = "Excelente para roles ofensivos con alto daño."
        else:
            return None

    elif role == "defensa":
        if stats.get("defense", 0) >= 80 or stats.get("special-defense", 0) >= 80:
            highlight = f"Defensa: {max(stats.get('defense', 0), stats.get('special-defense', 0))}"
            reason = "Perfecto para aguantar ataques enemigos."
        else:
            return None

    elif role == "velocidad":
        if stats.get("speed", 0) >= 90:
            highlight = f"Velocidad: {stats.get('speed', 0)}"
            reason = "Ideal para atacar primero en batalla."
        else:
            return None

    elif role == "soporte":
        # Look for balanced stats or specific movesets (simplified)
        if stats.get("hp", 0) >= 70:
            highlight = f"HP: {stats.get('hp', 0)}"
            reason = "Excelente para soporte con buena supervivencia."
        else:
            return None

    elif role == "equilibrado":
        # Look for well-rounded stats
        if total_stats >= 450 and min(stats.values()) >= 50:
            highlight = f"Stats balanceadas (Total: {total_stats})"
            reason = "Versátil, funciona en múltiples roles."
        else:
            return None
    else:
        return None

    return {
        "name": pokemon.name,
        "id": pokemon.id,
        "types": pokemon.type_names,
        "stats": stats,
        "total_stats": total_stats,
        "highlight": highlight,
        "reason": reason,
        "role": role,
    }


# Interactive tools registry
INTERACTIVE_TOOLS = {
    "get_pokemon_info_elicit": get_pokemon_info_elicit,
    "build_pokemon_team_elicit": build_pokemon_team_elicit,
    "suggest_pokemon_by_criteria_elicit": suggest_pokemon_by_criteria_elicit,
}
