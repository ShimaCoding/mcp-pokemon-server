# Guía de Uso de Prompts - Pokemon MCP Server

## 📋 Prompts Disponibles

### 🎓 Prompts Educativos

#### 1. Análisis de Pokémon (`educational/pokemon-analysis`)
Analiza un Pokémon específico con diferentes niveles de detalle.

**Parámetros:**
- `pokemon_name` (requerido): Nombre del Pokémon
- `analysis_type`: "general", "battle", "competitive" (default: "general")
- `user_level`: "beginner", "intermediate", "advanced" (default: "beginner")

**Ejemplos de uso:**
```
@educational/pokemon-analysis pokemon_name="pikachu" analysis_type="competitive" user_level="advanced"
@educational/pokemon-analysis pokemon_name="charizard" analysis_type="battle" user_level="intermediate"
@educational/pokemon-analysis pokemon_name="bulbasaur" user_level="beginner"
```

#### 2. Construcción de Equipos (`educational/team-building`)
Guía para construir equipos Pokémon efectivos.

**Parámetros:**
- `theme`: "balanced", "offensive", "defensive", "type-specific" (default: "balanced")
- `format`: "casual", "competitive", "tournament" (default: "casual")
- `restrictions`: Lista opcional de restricciones

**Ejemplos de uso:**
```
@educational/team-building theme="offensive" format="competitive"
@educational/team-building theme="defensive" format="tournament" restrictions=["no-legendaries", "gen-1-only"]
@educational/team-building theme="type-specific" format="casual"
```

#### 3. Efectividad de Tipos (`educational/type-effectiveness`)
Aprende sobre efectividad de tipos Pokémon.

**Parámetros:**
- `scenario`: "learning", "quiz", "battle-analysis" (default: "learning")
- `attacking_type`: Tipo atacante específico (opcional)
- `defending_types`: Lista de tipos defensores (opcional)

**Ejemplos de uso:**
```
@educational/type-effectiveness scenario="quiz" attacking_type="fire"
@educational/type-effectiveness scenario="battle-analysis" attacking_type="water" defending_types=["fire", "ground"]
@educational/type-effectiveness scenario="learning"
```

### ⚔️ Prompts de Batalla

#### 1. Estrategia de Batalla (`battle/strategy`)
Desarrolla estrategias para batallas competitivas.

**Parámetros:**
- `user_team` (requerido): Lista de nombres de Pokémon en tu equipo
- `opponent_team`: Lista de Pokémon del oponente (opcional)
- `battle_format`: "singles", "doubles", "multi" (default: "singles")
- `strategy_focus`: "offensive", "defensive", "balanced", "utility" (default: "balanced")

**Ejemplos de uso:**
```
@battle/strategy user_team=["pikachu", "charizard", "blastoise"] battle_format="singles" strategy_focus="offensive"
@battle/strategy user_team=["alakazam", "machamp", "gengar"] opponent_team=["dragonite", "tyranitar", "metagross"] battle_format="doubles"
```

#### 2. Análisis de Matchup (`battle/matchup-analysis`)
Analiza enfrentamientos específicos entre Pokémon.

**Parámetros:**
- `pokemon1` (requerido): Primer Pokémon
- `pokemon2` (requerido): Segundo Pokémon
- `scenario`: "1v1", "team-context", "switch-prediction" (default: "1v1")
- `environment`: "neutral", "weather", "terrain" (default: "neutral")

**Ejemplos de uso:**
```
@battle/matchup-analysis pokemon1="pikachu" pokemon2="charizard" scenario="1v1"
@battle/matchup-analysis pokemon1="gyarados" pokemon2="zapdos" scenario="team-context" environment="weather"
```

#### 3. Vista Previa de Equipo (`battle/team-preview`)
Analiza la composición y efectividad de un equipo.

**Parámetros:**
- `team` (requerido): Lista de nombres de Pokémon
- `analysis_depth`: "quick", "standard", "comprehensive" (default: "standard")
- `focus_areas`: Lista de áreas específicas a analizar (opcional)

**Ejemplos de uso:**
```
@battle/team-preview team=["pikachu", "charizard", "blastoise", "venusaur", "alakazam", "machamp"] analysis_depth="comprehensive"
@battle/team-preview team=["dragonite", "tyranitar", "metagross"] analysis_depth="quick" focus_areas=["offense", "synergy"]
```

## 🚀 Consejos de Uso

### 1. **Empezar con lo básico**
```
@educational/pokemon-analysis pokemon_name="pikachu" user_level="beginner"
```

### 2. **Análisis competitivo avanzado**
```
@educational/pokemon-analysis pokemon_name="metagross" analysis_type="competitive" user_level="advanced"
```

### 3. **Construcción de equipos temáticos**
```
@educational/team-building theme="type-specific" format="competitive" restrictions=["fire-type-focus"]
```

### 4. **Análisis de batalla completo**
```
@battle/strategy user_team=["garchomp", "rotom-wash", "ferrothorn", "latios", "heatran", "tyranitar"] opponent_team=["dragonite", "skarmory", "blissey"] battle_format="singles" strategy_focus="balanced"
```

### 5. **Entrenamiento con quiz**
```
@educational/type-effectiveness scenario="quiz" attacking_type="psychic"
```

## 🎯 Casos de Uso Comunes

### Para Principiantes:
1. Análisis básico: `@educational/pokemon-analysis pokemon_name="starter-pokemon" user_level="beginner"`
2. Aprender tipos: `@educational/type-effectiveness scenario="learning"`
3. Primer equipo: `@educational/team-building theme="balanced" format="casual"`

### Para Jugadores Intermedios:
1. Estrategia de batalla: `@battle/strategy user_team=["your-team"] battle_format="singles"`
2. Análisis de matchups: `@battle/matchup-analysis pokemon1="your-pokemon" pokemon2="opponent-pokemon"`
3. Mejora de equipos: `@battle/team-preview team=["your-team"] analysis_depth="standard"`

### Para Jugadores Avanzados:
1. Meta analysis: `@educational/pokemon-analysis pokemon_name="meta-pokemon" analysis_type="competitive" user_level="advanced"`
2. Estrategia competitiva: `@battle/strategy user_team=["competitive-team"] opponent_team=["known-threats"] battle_format="singles" strategy_focus="utility"`
3. Análisis profundo: `@battle/team-preview team=["full-team"] analysis_depth="comprehensive" focus_areas=["synergy", "coverage", "meta"]`

## 🔧 Troubleshooting

### Errores Comunes:
1. **Pokémon no encontrado**: Verifica el nombre del Pokémon (usar nombres en inglés y minúsculas)
2. **Parámetros inválidos**: Revisa que los valores estén en las opciones válidas
3. **Lista vacía**: Asegúrate de incluir al menos un Pokémon en las listas

### Mejores Prácticas:
1. Usa nombres de Pokémon en inglés y minúsculas
2. Para listas, separa con comas: `["pokemon1", "pokemon2", "pokemon3"]`
3. Especifica el nivel de usuario apropiado para obtener respuestas relevantes
4. Combina diferentes prompts para análisis completos
