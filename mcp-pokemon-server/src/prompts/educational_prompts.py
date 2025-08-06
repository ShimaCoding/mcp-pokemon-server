"""Educational prompts for Pokemon learning and analysis."""

from typing import Dict, List, Optional, Any
from mcp.types import PromptMessage, GetPromptResult, TextContent
from ..clients.pokeapi_client import PokemonAPIClient
from ..config.logging import get_logger

logger = get_logger(__name__)


class EducationalPromptManager:
    """Manager for educational Pokemon prompts."""
    
    def __init__(self, pokemon_client: PokemonAPIClient):
        self.pokemon_client = pokemon_client
        self.logger = logger

    async def create_pokemon_analysis_prompt(
        self, 
        pokemon_name: str,
        analysis_type: str = "general",
        user_level: str = "beginner"
    ) -> GetPromptResult:
        """Create a prompt for Pokemon analysis based on user level.
        
        Args:
            pokemon_name: Name of the Pokemon to analyze
            analysis_type: Type of analysis (general, battle, competitive)
            user_level: User experience level (beginner, intermediate, advanced)
        """
        try:
            # Get Pokemon data
            pokemon_data = await self.pokemon_client.get_pokemon(pokemon_name)
            
            if not pokemon_data:
                return GetPromptResult(
                    description=f"Analysis prompt for {pokemon_name}",
                    messages=[
                        PromptMessage(
                            role="user",
                            content=TextContent(
                                type="text",
                                text=f"❌ Could not find Pokemon: {pokemon_name}"
                            )
                        )
                    ]
                )

            # Build context based on analysis type and user level
            context = self._build_analysis_context(pokemon_data, analysis_type, user_level)
            
            prompt_text = self._generate_analysis_prompt_text(
                pokemon_data, analysis_type, user_level, context
            )
            
            return GetPromptResult(
                description=f"{analysis_type.title()} analysis prompt for {pokemon_name} ({user_level} level)",
                messages=[
                    PromptMessage(
                        role="user",
                        content=TextContent(
                            type="text",
                            text=prompt_text
                        )
                    )
                ]
            )
            
        except Exception as e:
            self.logger.error("Failed to create analysis prompt", error=str(e))
            return GetPromptResult(
                description=f"Error creating prompt for {pokemon_name}",
                messages=[
                    PromptMessage(
                        role="user",
                        content=TextContent(
                            type="text",
                            text=f"❌ Error creating prompt: {str(e)}"
                        )
                    )
                ]
            )

    async def create_team_building_prompt(
        self,
        theme: str = "balanced",
        format: str = "casual",
        restrictions: Optional[List[str]] = None
    ) -> GetPromptResult:
        """Create a prompt for team building guidance.
        
        Args:
            theme: Team theme (balanced, offensive, defensive, type-specific)
            format: Battle format (casual, competitive, tournament)
            restrictions: Optional restrictions (no legendaries, specific generation, etc.)
        """
        try:
            context = self._build_team_building_context(theme, format, restrictions)
            prompt_text = self._generate_team_building_prompt_text(theme, format, restrictions, context)
            
            return GetPromptResult(
                description=f"Team building prompt - {theme} theme for {format} format",
                messages=[
                    PromptMessage(
                        role="user",
                        content=TextContent(
                            type="text",
                            text=prompt_text
                        )
                    )
                ]
            )
            
        except Exception as e:
            self.logger.error("Failed to create team building prompt", error=str(e))
            return GetPromptResult(
                description="Error creating team building prompt",
                messages=[
                    PromptMessage(
                        role="user",
                        content=TextContent(
                            type="text",
                            text=f"❌ Error creating prompt: {str(e)}"
                        )
                    )
                ]
            )

    async def create_type_effectiveness_prompt(
        self,
        scenario: str = "learning",
        attacking_type: Optional[str] = None,
        defending_types: Optional[List[str]] = None
    ) -> GetPromptResult:
        """Create a prompt for type effectiveness learning.
        
        Args:
            scenario: Learning scenario (learning, quiz, battle-analysis)
            attacking_type: Specific attacking type to focus on
            defending_types: Specific defending types to analyze
        """
        try:
            context = self._build_type_effectiveness_context(scenario, attacking_type, defending_types)
            prompt_text = self._generate_type_effectiveness_prompt_text(
                scenario, attacking_type, defending_types, context
            )
            
            return GetPromptResult(
                description=f"Type effectiveness prompt - {scenario} scenario",
                messages=[
                    PromptMessage(
                        role="user",
                        content=TextContent(
                            type="text",
                            text=prompt_text
                        )
                    )
                ]
            )
            
        except Exception as e:
            self.logger.error("Failed to create type effectiveness prompt", error=str(e))
            return GetPromptResult(
                description="Error creating type effectiveness prompt",
                messages=[
                    PromptMessage(
                        role="user",
                        content=TextContent(
                            type="text",
                            text=f"❌ Error creating prompt: {str(e)}"
                        )
                    )
                ]
            )

    def _build_analysis_context(
        self, 
        pokemon_data: Any,  # Pokemon model instance
        analysis_type: str, 
        user_level: str
    ) -> Dict[str, str]:
        """Build context for Pokemon analysis prompts."""
        # Extract stats as dictionary
        base_stats = {}
        for stat in pokemon_data.stats:
            stat_name = stat.stat["name"].replace("-", "_")
            base_stats[stat_name] = stat.base_stat
        
        # Extract types as list of strings
        types = [ptype.type["name"] for ptype in pokemon_data.types]
        
        # Extract abilities as list of strings
        abilities = [ability.ability["name"] for ability in pokemon_data.abilities]
        
        system_messages = {
            "beginner": (
                "You are a friendly Pokemon teacher helping beginners learn about Pokemon. "
                "Use simple language, explain basic concepts, and focus on fundamental "
                "characteristics. Avoid complex competitive terminology."
            ),
            "intermediate": (
                "You are a Pokemon strategist helping intermediate players improve their "
                "understanding. Use moderate complexity, introduce competitive concepts "
                "gradually, and provide strategic insights."
            ),
            "advanced": (
                "You are a competitive Pokemon expert providing advanced analysis. "
                "Use technical terminology, deep strategic analysis, and comprehensive "
                "competitive insights including meta considerations."
            )
        }
        
        analysis_focus = {
            "general": "overall characteristics, strengths, and weaknesses",
            "battle": "battle performance, matchups, and strategic usage",
            "competitive": "competitive viability, tier placement, and meta analysis"
        }
        
        return {
            "system_message": system_messages.get(user_level, system_messages["beginner"]),
            "analysis_focus": analysis_focus.get(analysis_type, analysis_focus["general"]),
            "pokemon_name": pokemon_data.name,
            "types": ", ".join(types),
            "base_stat_total": sum(base_stats.values()) if base_stats else 0,
            "primary_abilities": ", ".join(abilities[:2]) if abilities else "Unknown"
        }

    def _generate_analysis_prompt_text(
        self,
        pokemon_data: Any,  # Pokemon model instance
        analysis_type: str,
        user_level: str,
        context: Dict[str, str]
    ) -> str:
        """Generate the analysis prompt text based on context."""
        pokemon_name = context["pokemon_name"]
        types = context["types"]
        bst = context["base_stat_total"]
        abilities = context["primary_abilities"]
        
        base_prompt = f"""
You are {context['system_message'].lower()}

Please analyze {pokemon_name} focusing on {context['analysis_focus']}.

Pokemon Details:
- Name: {pokemon_name}
- Types: {types}
- Base Stat Total: {bst}
- Key Abilities: {abilities}

"""
        
        level_specific_additions = {
            "beginner": f"""
For a beginner trainer, please explain:
1. What makes {pokemon_name} unique?
2. What are its main strengths in simple terms?
3. What should a new trainer know about using {pokemon_name}?
4. Any fun facts or interesting characteristics?

Please use simple language and avoid complex terminology.
""",
            "intermediate": f"""
For an intermediate trainer, please analyze:
1. {pokemon_name}'s role in different team compositions
2. Optimal movesets and strategies
3. Key matchups (favorable and unfavorable)
4. Training and development recommendations
5. Synergies with other Pokemon

Use moderate complexity and introduce strategic concepts.
""",
            "advanced": f"""
For an advanced competitive player, please provide:
1. Comprehensive tier analysis and meta positioning
2. Optimal EV spreads and nature recommendations
3. Detailed matchup analysis against current meta threats
4. Team building considerations and core synergies
5. Advanced strategies and niche applications
6. Comparison with similar Pokemon in the meta

Use full competitive terminology and deep strategic analysis.
"""
        }
        
        return base_prompt + level_specific_additions.get(user_level, level_specific_additions["beginner"])

    def _build_team_building_context(
        self,
        theme: str,
        format: str,
        restrictions: Optional[List[str]]
    ) -> Dict[str, str]:
        """Build context for team building prompts."""
        system_message = (
            "You are an expert Pokemon team builder and strategist. Help users create "
            "effective teams based on their preferences and constraints. Provide detailed "
            "explanations for your recommendations and consider synergies, coverage, "
            "and strategic balance."
        )
        
        theme_descriptions = {
            "balanced": "a well-rounded team with good offensive and defensive balance",
            "offensive": "a high-pressure offensive team focused on dealing damage",
            "defensive": "a tanky team focused on stall and attrition tactics",
            "type-specific": "a team centered around a specific type or type combination"
        }
        
        format_considerations = {
            "casual": "friendly battles with focus on fun and creativity",
            "competitive": "ranked battles with meta considerations",
            "tournament": "official tournament play with strict rules"
        }
        
        return {
            "system_message": system_message,
            "theme_description": theme_descriptions.get(theme, theme_descriptions["balanced"]),
            "format_description": format_considerations.get(format, format_considerations["casual"]),
            "restrictions": restrictions or []
        }

    def _generate_team_building_prompt_text(
        self,
        theme: str,
        format: str,
        restrictions: Optional[List[str]],
        context: Dict[str, str]
    ) -> str:
        """Generate team building prompt text."""
        restrictions_text = ""
        if restrictions:
            restrictions_text = f"\nRestrictions: {', '.join(restrictions)}"
        
        return f"""
{context['system_message']}

Please help me build a Pokemon team with the following specifications:

Team Theme: {theme.title()} - {context['theme_description']}
Battle Format: {format.title()} - {context['format_description']}{restrictions_text}

Please provide:
1. 6 Pokemon recommendations with justifications
2. Role assignments (lead, sweeper, tank, support, etc.)
3. Key moves and abilities for each Pokemon
4. Team synergies and strategic approach
5. Potential weaknesses and how to address them
6. Alternative options for each role

Consider type coverage, stat distribution, and strategic balance in your recommendations.
"""

    def _build_type_effectiveness_context(
        self,
        scenario: str,
        attacking_type: Optional[str],
        defending_types: Optional[List[str]]
    ) -> Dict[str, str]:
        """Build context for type effectiveness prompts."""
        system_messages = {
            "learning": (
                "You are a Pokemon type effectiveness teacher. Help users understand "
                "type matchups through clear explanations and practical examples. "
                "Focus on helping them remember and apply type effectiveness rules."
            ),
            "quiz": (
                "You are a Pokemon quiz master testing type effectiveness knowledge. "
                "Create engaging questions and provide detailed explanations for answers. "
                "Help users learn through interactive challenges."
            ),
            "battle-analysis": (
                "You are a battle analyst explaining type effectiveness in competitive "
                "contexts. Focus on practical applications, prediction, and strategic "
                "decision-making based on type matchups."
            )
        }
        
        return {
            "system_message": system_messages.get(scenario, system_messages["learning"]),
            "attacking_type": attacking_type,
            "defending_types": defending_types or []
        }

    def _generate_type_effectiveness_prompt_text(
        self,
        scenario: str,
        attacking_type: Optional[str],
        defending_types: Optional[List[str]],
        context: Dict[str, str]
    ) -> str:
        """Generate type effectiveness prompt text."""
        base_scenarios = {
            "learning": f"""
{context['system_message']}

Please help me understand Pokemon type effectiveness. I want to learn:

1. The basic principles of type effectiveness
2. How to remember common matchups
3. Practical applications in battle
4. Tips for predicting opponent moves based on types

""",
            "quiz": f"""
{context['system_message']}

Please create a type effectiveness quiz for me. Include:

1. Multiple choice questions about type matchups
2. Scenario-based questions about battle situations
3. Progressive difficulty levels
4. Detailed explanations for each answer

""",
            "battle-analysis": f"""
{context['system_message']}

Please analyze type effectiveness in competitive battle scenarios:

1. How to use type advantage strategically
2. When to switch Pokemon based on type matchups
3. Predicting opponent strategies from team composition
4. Advanced type interaction concepts (abilities, items, etc.)

"""
        }
        
        base_text = base_scenarios.get(scenario, base_scenarios["learning"])
        
        if attacking_type:
            base_text += f"Focus specifically on {attacking_type.title()} type attacks.\n"
        
        if defending_types:
            base_text += f"Consider defending types: {', '.join([t.title() for t in defending_types])}\n"
        
        return base_text
