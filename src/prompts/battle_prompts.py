"""Battle-focused prompts for Pokemon strategy and analysis."""

from typing import Any

from mcp.types import GetPromptResult, PromptMessage, TextContent

from ..clients.pokeapi_client import PokemonAPIClient
from ..config.logging import get_logger

logger = get_logger(__name__)


class BattlePromptManager:
    """Manager for battle-focused Pokemon prompts."""

    def __init__(self, pokemon_client: PokemonAPIClient):
        self.pokemon_client = pokemon_client
        self.logger = logger

    async def create_battle_strategy_prompt(
        self,
        user_team: list[str],
        opponent_team: list[str] | None = None,
        battle_format: str = "singles",
        strategy_focus: str = "balanced",
    ) -> GetPromptResult:
        """Create a prompt for battle strategy planning.

        Args:
            user_team: List of Pokemon names in user's team
            opponent_team: Optional list of opponent's Pokemon
            battle_format: singles, doubles, or multi
            strategy_focus: offensive, defensive, balanced, or utility
        """
        try:
            # Get data for user's team
            user_team_data = []
            for pokemon_name in user_team[:6]:  # Max 6 Pokemon
                pokemon_data = await self.pokemon_client.get_pokemon(pokemon_name)
                if pokemon_data:
                    user_team_data.append(pokemon_data)

            # Get data for opponent's team if provided
            opponent_team_data = []
            if opponent_team:
                for pokemon_name in opponent_team[:6]:
                    pokemon_data = await self.pokemon_client.get_pokemon(pokemon_name)
                    if pokemon_data:
                        opponent_team_data.append(pokemon_data)

            context = self._build_battle_strategy_context(
                user_team_data, opponent_team_data, battle_format, strategy_focus
            )

            prompt_text = self._generate_battle_strategy_prompt_text(
                user_team_data,
                opponent_team_data,
                battle_format,
                strategy_focus,
                context,
            )

            description = (
                f"Battle strategy prompt - {strategy_focus} {battle_format} format"
            )
            if opponent_team:
                description += " (with opponent analysis)"

            return GetPromptResult(
                description=description,
                messages=[
                    PromptMessage(
                        role="user", content=TextContent(type="text", text=prompt_text)
                    )
                ],
            )

        except Exception as e:
            self.logger.error("Failed to create battle strategy prompt", error=str(e))
            return GetPromptResult(
                description="Error creating battle strategy prompt",
                messages=[
                    PromptMessage(
                        role="user",
                        content=TextContent(
                            type="text", text=f"❌ Error creating prompt: {str(e)}"
                        ),
                    )
                ],
            )

    async def create_matchup_analysis_prompt(
        self,
        pokemon1: str,
        pokemon2: str,
        scenario: str = "1v1",
        environment: str = "neutral",
    ) -> GetPromptResult:
        """Create a prompt for analyzing specific Pokemon matchups.

        Args:
            pokemon1: First Pokemon name
            pokemon2: Second Pokemon name
            scenario: 1v1, team-context, or switch-prediction
            environment: neutral, weather, terrain effects
        """
        try:
            # Get Pokemon data
            pokemon1_data = await self.pokemon_client.get_pokemon(pokemon1)
            pokemon2_data = await self.pokemon_client.get_pokemon(pokemon2)

            if not pokemon1_data or not pokemon2_data:
                missing = []
                if not pokemon1_data:
                    missing.append(pokemon1)
                if not pokemon2_data:
                    missing.append(pokemon2)

                return GetPromptResult(
                    description=f"Matchup analysis: {pokemon1} vs {pokemon2}",
                    messages=[
                        PromptMessage(
                            role="user",
                            content=TextContent(
                                type="text",
                                text=f"❌ Could not find Pokemon: {', '.join(missing)}",
                            ),
                        )
                    ],
                )

            context = self._build_matchup_analysis_context(
                pokemon1_data, pokemon2_data, scenario, environment
            )

            prompt_text = self._generate_matchup_analysis_prompt_text(
                pokemon1_data, pokemon2_data, scenario, environment, context
            )

            return GetPromptResult(
                description=f"Matchup analysis: {pokemon1} vs {pokemon2} ({scenario})",
                messages=[
                    PromptMessage(
                        role="user", content=TextContent(type="text", text=prompt_text)
                    )
                ],
            )

        except Exception as e:
            self.logger.error("Failed to create matchup analysis prompt", error=str(e))
            return GetPromptResult(
                description=f"Error analyzing {pokemon1} vs {pokemon2}",
                messages=[
                    PromptMessage(
                        role="user",
                        content=TextContent(
                            type="text", text=f"❌ Error creating prompt: {str(e)}"
                        ),
                    )
                ],
            )

    async def create_team_preview_prompt(
        self,
        team: list[str],
        analysis_depth: str = "standard",
        focus_areas: list[str] | None = None,
    ) -> GetPromptResult:
        """Create a prompt for team preview analysis.

        Args:
            team: List of Pokemon names to analyze
            analysis_depth: quick, standard, or comprehensive
            focus_areas: specific areas to focus on (offense, defense, synergy, etc.)
        """
        try:
            # Get team data
            team_data = []
            for pokemon_name in team[:6]:
                pokemon_data = await self.pokemon_client.get_pokemon(pokemon_name)
                if pokemon_data:
                    team_data.append(pokemon_data)

            if not team_data:
                return GetPromptResult(
                    description="Team preview analysis",
                    messages=[
                        PromptMessage(
                            role="user",
                            content=TextContent(
                                type="text",
                                text="❌ Could not find any valid Pokemon in the team",
                            ),
                        )
                    ],
                )

            context = self._build_team_preview_context(
                team_data, analysis_depth, focus_areas
            )
            prompt_text = self._generate_team_preview_prompt_text(
                team_data, analysis_depth, focus_areas, context
            )

            return GetPromptResult(
                description=f"Team preview analysis ({analysis_depth} depth)",
                messages=[
                    PromptMessage(
                        role="user", content=TextContent(type="text", text=prompt_text)
                    )
                ],
            )

        except Exception as e:
            self.logger.error("Failed to create team preview prompt", error=str(e))
            return GetPromptResult(
                description="Error creating team preview prompt",
                messages=[
                    PromptMessage(
                        role="user",
                        content=TextContent(
                            type="text", text=f"❌ Error creating prompt: {str(e)}"
                        ),
                    )
                ],
            )

    def _build_battle_strategy_context(
        self,
        user_team_data: list[Any],  # List of Pokemon model instances
        opponent_team_data: list[Any],  # List of Pokemon model instances
        battle_format: str,
        strategy_focus: str,
    ) -> dict[str, Any]:
        """Build context for battle strategy prompts."""
        system_message = (
            "You are an expert Pokemon battle strategist and coach. Analyze teams "
            "and provide detailed strategic guidance for competitive battles. "
            "Consider type matchups, stat distributions, potential movesets, "
            "and strategic positioning."
        )

        format_specific_guidance = {
            "singles": "focus on 1v1 matchups, switching strategies, and individual Pokemon performance",
            "doubles": "emphasize Pokemon synergies, target selection, and double battle mechanics",
            "multi": "consider team coordination, role distribution, and multi-target strategies",
        }

        strategy_approaches = {
            "offensive": "aggressive play, fast KOs, and maintaining offensive pressure",
            "defensive": "stall tactics, status effects, and long-term battle control",
            "balanced": "adaptable strategy combining offensive pressure with defensive stability",
            "utility": "support moves, field control, and strategic positioning",
        }

        return {
            "system_message": system_message,
            "format_guidance": format_specific_guidance.get(
                battle_format, format_specific_guidance["singles"]
            ),
            "strategy_approach": strategy_approaches.get(
                strategy_focus, strategy_approaches["balanced"]
            ),
            "user_team_count": len(user_team_data),
            "opponent_team_count": len(opponent_team_data),
            "has_opponent_data": len(opponent_team_data) > 0,
        }

    def _generate_battle_strategy_prompt_text(
        self,
        user_team_data: list[Any],  # List of Pokemon model instances
        opponent_team_data: list[Any],  # List of Pokemon model instances
        battle_format: str,
        strategy_focus: str,
        context: dict[str, Any],
    ) -> str:
        """Generate battle strategy prompt text."""
        user_team_summary = self._create_team_summary(user_team_data)

        base_prompt = f"""
{context["system_message"]}

Please develop a comprehensive battle strategy for the following scenario:

Battle Format: {battle_format.title()}
Strategy Focus: {strategy_focus.title()} - {context["strategy_approach"]}
Format Considerations: {context["format_guidance"]}

My Team:
{user_team_summary}

"""

        if opponent_team_data:
            opponent_team_summary = self._create_team_summary(opponent_team_data)
            base_prompt += f"""
Opponent's Team:
{opponent_team_summary}

"""

        strategy_request = """
Please provide:
1. Overall strategic approach and game plan
2. Lead Pokemon recommendation with justification
3. Key matchups to watch (favorable and threatening)
4. Switching strategies and timing recommendations
5. Win conditions and how to achieve them
6. Contingency plans for common scenarios
"""

        if battle_format == "doubles":
            strategy_request += """
7. Pokemon pairing recommendations
8. Target priority in double battles
9. Synergistic move combinations
"""

        if opponent_team_data:
            strategy_request += """
7. Specific counter-strategies for opponent's threats
8. Predicted opponent game plan and how to disrupt it
"""

        return base_prompt + strategy_request

    def _build_matchup_analysis_context(
        self,
        pokemon1_data: Any,  # Pokemon model instance
        pokemon2_data: Any,  # Pokemon model instance
        scenario: str,
        environment: str,
    ) -> dict[str, Any]:
        """Build context for matchup analysis prompts."""
        system_message = (
            "You are a Pokemon battle analyst specializing in matchup prediction "
            "and strategic analysis. Provide detailed breakdowns of Pokemon "
            "interactions, considering stats, types, abilities, and potential movesets."
        )

        scenario_contexts = {
            "1v1": "isolated 1v1 battle with no switching or team context",
            "team-context": "matchup within the context of full team battles",
            "switch-prediction": "analyzing optimal switch timing and prediction",
        }

        environment_effects = {
            "neutral": "standard battle conditions with no special effects",
            "weather": "considering weather effects and weather-dependent strategies",
            "terrain": "factoring in terrain effects and terrain-based tactics",
        }

        return {
            "system_message": system_message,
            "scenario_context": scenario_contexts.get(
                scenario, scenario_contexts["1v1"]
            ),
            "environment_effects": environment_effects.get(
                environment, environment_effects["neutral"]
            ),
            "pokemon1_name": pokemon1_data.name,
            "pokemon2_name": pokemon2_data.name,
        }

    def _generate_matchup_analysis_prompt_text(
        self,
        pokemon1_data: Any,  # Pokemon model instance
        pokemon2_data: Any,  # Pokemon model instance
        scenario: str,
        environment: str,
        context: dict[str, Any],
    ) -> str:
        """Generate matchup analysis prompt text."""
        pokemon1_summary = self._create_pokemon_summary(pokemon1_data)
        pokemon2_summary = self._create_pokemon_summary(pokemon2_data)

        return f"""
{context["system_message"]}

Please analyze the following Pokemon matchup:

Scenario: {scenario.title()} - {context["scenario_context"]}
Environment: {environment.title()} - {context["environment_effects"]}

Pokemon 1: {context["pokemon1_name"]}
{pokemon1_summary}

Pokemon 2: {context["pokemon2_name"]}
{pokemon2_summary}

Please provide:
1. Type effectiveness analysis and damage calculations
2. Stat comparison and speed tiers
3. Likely movesets and their effectiveness
4. Ability interactions and their impact
5. Predicted battle flow and key decision points
6. Win conditions for each Pokemon
7. Strategic recommendations for both sides
8. Environmental factors and their influence

Consider both offensive and defensive perspectives for a complete analysis.
"""

    def _build_team_preview_context(
        self,
        team_data: list[Any],  # List of Pokemon model instances
        analysis_depth: str,
        focus_areas: list[str] | None,
    ) -> dict[str, Any]:
        """Build context for team preview prompts."""
        system_message = (
            "You are a Pokemon team analyst providing comprehensive team "
            "evaluations. Assess team composition, synergies, weaknesses, "
            "and strategic potential for competitive play."
        )

        depth_descriptions = {
            "quick": "rapid overview focusing on key strengths and obvious weaknesses",
            "standard": "balanced analysis covering major strategic elements",
            "comprehensive": "detailed examination of all team aspects and strategic possibilities",
        }

        default_focus_areas = ["offense", "defense", "synergy", "coverage", "balance"]
        actual_focus_areas = focus_areas or default_focus_areas

        return {
            "system_message": system_message,
            "depth_description": depth_descriptions.get(
                analysis_depth, depth_descriptions["standard"]
            ),
            "focus_areas": actual_focus_areas,
            "team_size": len(team_data),
        }

    def _generate_team_preview_prompt_text(
        self,
        team_data: list[Any],  # List of Pokemon model instances
        analysis_depth: str,
        focus_areas: list[str] | None,
        context: dict[str, Any],
    ) -> str:
        """Generate team preview prompt text."""
        team_summary = self._create_detailed_team_summary(team_data)
        focus_areas_text = ", ".join(context["focus_areas"])

        base_prompt = f"""
{context["system_message"]}

Please analyze this Pokemon team with {analysis_depth} depth:

Team Composition:
{team_summary}

Analysis Focus Areas: {focus_areas_text}
Analysis Depth: {context["depth_description"]}

"""

        analysis_sections = {
            "quick": [
                "1. Overall team rating and tier classification",
                "2. Primary strengths and win conditions",
                "3. Major weaknesses and vulnerabilities",
                "4. Key Pokemon and their roles",
            ],
            "standard": [
                "1. Team archetype and strategic identity",
                "2. Individual Pokemon roles and contributions",
                "3. Type coverage analysis",
                "4. Offensive and defensive capabilities",
                "5. Synergistic combinations",
                "6. Weakness identification and mitigation",
                "7. Meta positioning and viability",
            ],
            "comprehensive": [
                "1. Complete team archetype analysis",
                "2. Detailed role breakdown for each Pokemon",
                "3. Comprehensive type coverage matrix",
                "4. Stat distribution and speed tier analysis",
                "5. Potential moveset optimization",
                "6. Advanced synergy identification",
                "7. Weakness analysis with specific threats",
                "8. Meta matchup predictions",
                "9. Alternative Pokemon suggestions",
                "10. Strategic gameplay recommendations",
            ],
        }

        sections = analysis_sections.get(analysis_depth, analysis_sections["standard"])

        return base_prompt + "Please provide:\n" + "\n".join(sections)

    def _create_team_summary(self, team_data: list[Any]) -> str:
        """Create a concise team summary."""
        summaries = []
        for i, pokemon in enumerate(team_data, 1):
            name = pokemon.name
            types = [ptype.type["name"] for ptype in pokemon.types]
            types_str = ", ".join(types)

            # Calculate BST
            bst = sum(stat.base_stat for stat in pokemon.stats)

            summaries.append(f"{i}. {name} ({types_str}) - BST: {bst}")

        return "\n".join(summaries)

    def _create_detailed_team_summary(self, team_data: list[Any]) -> str:
        """Create a detailed team summary with more information."""
        summaries = []
        for i, pokemon in enumerate(team_data, 1):
            name = pokemon.name
            types = [ptype.type["name"] for ptype in pokemon.types]
            types_str = ", ".join(types)

            # Extract stats
            stats = {}
            for stat in pokemon.stats:
                stat_name = stat.stat["name"].replace("-", "_")
                stats[stat_name] = stat.base_stat

            stat_line = " / ".join(
                [
                    f"HP: {stats.get('hp', 0)}",
                    f"Att: {stats.get('attack', 0)}",
                    f"Def: {stats.get('defense', 0)}",
                    f"SpA: {stats.get('special_attack', 0)}",
                    f"SpD: {stats.get('special_defense', 0)}",
                    f"Spe: {stats.get('speed', 0)}",
                ]
            )

            abilities = [ability.ability["name"] for ability in pokemon.abilities]
            abilities_text = ", ".join(abilities[:2]) if abilities else "Unknown"

            summaries.append(
                f"""
{i}. {name}
   Type(s): {types_str}
   Stats: {stat_line}
   Abilities: {abilities_text}
"""
            )

        return "\n".join(summaries)

    def _create_pokemon_summary(self, pokemon_data: Any) -> str:
        """Create a summary for a single Pokemon."""
        name = pokemon_data.name
        types = [ptype.type["name"] for ptype in pokemon_data.types]
        types_str = ", ".join(types)

        # Extract stats
        stats = {}
        for stat in pokemon_data.stats:
            stat_name = stat.stat["name"].replace("-", "_")
            stats[stat_name] = stat.base_stat

        stat_line = " / ".join(
            [
                f"HP: {stats.get('hp', 0)}",
                f"Att: {stats.get('attack', 0)}",
                f"Def: {stats.get('defense', 0)}",
                f"SpA: {stats.get('special_attack', 0)}",
                f"SpD: {stats.get('special_defense', 0)}",
                f"Spe: {stats.get('speed', 0)}",
            ]
        )

        abilities = [ability.ability["name"] for ability in pokemon_data.abilities]
        abilities_text = ", ".join(abilities) if abilities else "Unknown"

        return f"""{name.title()}:
Type(s): {types_str}
Stats: {stat_line}
Abilities: {abilities_text}"""
