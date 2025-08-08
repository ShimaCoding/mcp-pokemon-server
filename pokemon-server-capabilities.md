## Pokemon MCP Server 1.12.3
| 🟢 Tools (4) | 🟢 Prompts (6) | 🟢 Resources | <span style="opacity:0.6">🔴 Logging</span> | 🟢 Experimental |
| --- | --- | --- | --- | --- |
## 🛠️ Tools (4)

<table style="text-align: left;">
<thead>
    <tr>
        <th style="width: auto;"></th>
        <th style="width: auto;">Tool Name</th>
        <th style="width: auto;">Description</th>
        <th style="width: auto;">Inputs</th>
    </tr>
</thead>
<tbody style="vertical-align: top;">
        <tr>
            <td>1.</td>
            <td>
                <code><b>analyze_pokemon_stats</b></code>
            </td>
            <td>Analyze Pokemon stats and provide insights.<br/><br/>Args:<br/>    name_or_id: Pokemon name or ID to analyze<br/></td>
            <td>
                <ul>
                    <li> <code>name_or_id</code> : string<br /></li>
                </ul>
            </td>
        </tr>
        <tr>
            <td>2.</td>
            <td>
                <code><b>get_pokemon_info</b></code>
            </td>
            <td>Get detailed information about a Pokemon by name or ID.<br/><br/>Args:<br/>    name_or_id: Pokemon name or ID to lookup<br/></td>
            <td>
                <ul>
                    <li> <code>name_or_id</code> : string<br /></li>
                </ul>
            </td>
        </tr>
        <tr>
            <td>3.</td>
            <td>
                <code><b>get_type_effectiveness</b></code>
            </td>
            <td>Get type effectiveness chart for a Pokemon type.<br/><br/>Args:<br/>    attacking_type: The attacking type name (e.g., <code>fire</code>, <code>water</code>, <code>electric</code>)<br/></td>
            <td>
                <ul>
                    <li> <code>attacking_type</code> : string<br /></li>
                </ul>
            </td>
        </tr>
        <tr>
            <td>4.</td>
            <td>
                <code><b>search_pokemon</b></code>
            </td>
            <td>Search for Pokemon with pagination.<br/><br/>Args:<br/>    limit: Maximum number of results (default: 20)<br/>    offset: Offset for pagination (default: 0)<br/></td>
            <td>
                <ul>
                    <li> <code>limit</code> : integer<br /></li>
                    <li> <code>offset</code> : integer<br /></li>
                </ul>
            </td>
        </tr>
</tbody>
</table>

## 📝 Prompts (6)

<table style="text-align: left;">
<thead>
    <tr>
        <th style="width: auto;"></th>
        <th style="width: auto;">Prompt Name</th>
        <th style="width: auto;">Description</th>
    </tr>
</thead>
<tbody style="vertical-align: top;">
        <tr>
            <td>1.</td>
            <td>
                <code><b>educational/pokemon-analysis</b></code>
            </td>
            <td>Educational prompt for Pokemon analysis.<br/><br/>Args:<br/>    pokemon_name: Name of the Pokemon to analyze<br/>    analysis_type: Type of analysis (general, battle, competitive)<br/>    user_level: User experience level (beginner, intermediate, advanced)<br/></td>
        </tr>
        <tr>
            <td>2.</td>
            <td>
                <code><b>educational/team-building</b></code>
            </td>
            <td>Educational prompt for team building guidance.<br/><br/>Args:<br/>    theme: Team theme (balanced, offensive, defensive, type-specific)<br/>    format: Battle format (casual, competitive, tournament)<br/>    restrictions: Optional restrictions (no legendaries, specific generation, etc.)<br/></td>
        </tr>
        <tr>
            <td>3.</td>
            <td>
                <code><b>educational/type-effectiveness</b></code>
            </td>
            <td>Educational prompt for type effectiveness learning.<br/><br/>Args:<br/>    scenario: Learning scenario (learning, quiz, battle-analysis)<br/>    attacking_type: Specific attacking type to focus on<br/>    defending_types: Specific defending types to analyze<br/></td>
        </tr>
        <tr>
            <td>4.</td>
            <td>
                <code><b>battle/strategy</b></code>
            </td>
            <td>Battle strategy planning prompt.<br/><br/>Args:<br/>    user_team: List of Pokemon names in user's team<br/>    opponent_team: Optional list of opponent's Pokemon<br/>    battle_format: singles, doubles, or multi<br/>    strategy_focus: offensive, defensive, balanced, or utility<br/></td>
        </tr>
        <tr>
            <td>5.</td>
            <td>
                <code><b>battle/matchup-analysis</b></code>
            </td>
            <td>Pokemon matchup analysis prompt.<br/><br/>Args:<br/>    pokemon1: First Pokemon name<br/>    pokemon2: Second Pokemon name<br/>    scenario: 1v1, team-context, or switch-prediction<br/>    environment: neutral, weather, terrain effects<br/></td>
        </tr>
        <tr>
            <td>6.</td>
            <td>
                <code><b>battle/team-preview</b></code>
            </td>
            <td>Team preview analysis prompt.<br/><br/>Args:<br/>    team: List of Pokemon names to analyze<br/>    analysis_depth: quick, standard, or comprehensive<br/>    focus_areas: specific areas to focus on (offense, defense, synergy, etc.)<br/></td>
        </tr>
</tbody>
</table>


## 🧩 Resource Templates (4)

<table style="text-align: left;">
<thead>
    <tr>
        <th style="width: auto;"></th>
        <th style="width: auto;">Name</th>
        <th style="width: auto;">Uri Template</th>
        <th style="width: auto;">Description</th>
    </tr>
</thead>
<tbody style="vertical-align: top;">
        <tr>
            <td>1.</td>
            <td>
                <code><b>pokemon_info_resource</b></code>
            </td>
            <td>
                <a>pokemon://info/{name_or_id}</a>
            </td>
            <td>Get detailed Pokemon information as a resource.<br/><br/>Args:<br/>    name_or_id: Pokemon name or ID to lookup<br/></td>
        </tr>
        <tr>
            <td>2.</td>
            <td>
                <code><b>pokemon_stats_resource</b></code>
            </td>
            <td>
                <a>pokemon://stats/{name_or_id}</a>
            </td>
            <td>Get Pokemon statistics analysis as a resource.<br/><br/>Args:<br/>    name_or_id: Pokemon name or ID to analyze<br/></td>
        </tr>
        <tr>
            <td>3.</td>
            <td>
                <code><b>pokemon_type_resource</b></code>
            </td>
            <td>
                <a>pokemon://type/{type_name}</a>
            </td>
            <td>Get type effectiveness information as a resource.<br/><br/>Args:<br/>    type_name: Pokemon type name (e.g., <code>fire</code>, <code>water</code>, <code>electric</code>)<br/></td>
        </tr>
        <tr>
            <td>4.</td>
            <td>
                <code><b>pokemon_comparison_resource</b></code>
            </td>
            <td>
                <a>pokemon://comparison/{pokemon1}/{pokemon2}</a>
            </td>
            <td>Get Pokemon comparison as a resource.<br/><br/>Args:<br/>    pokemon1: First Pokemon name<br/>    pokemon2: Second Pokemon name<br/></td>
        </tr>
</tbody>
</table>

<sup>◾ generated by [mcp-discovery](https://github.com/rust-mcp-stack/mcp-discovery)</sup>
