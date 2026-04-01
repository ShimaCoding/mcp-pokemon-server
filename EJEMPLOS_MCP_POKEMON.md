# 🎮 Guía Completa de Ejemplos - MCP Pokemon Server

**Extrae el máximo potencial del servidor MCP de Pokemon con ejemplos prácticos y creativos para tools, prompts y resources.**

---

## 📋 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Tools - Ejemplos Prácticos](#tools---ejemplos-prácticos)
3. [Prompts - Guías y Estrategias](#prompts---guías-y-estrategias)
4. [Resources - Acceso a Datos](#resources---acceso-a-datos)
5. [Combinaciones Avanzadas](#combinaciones-avanzadas)
6. [Casos de Uso Completos](#casos-de-uso-completos)
7. [Tips y Best Practices](#tips-y-best-practices)

---

## Introducción

El **MCP Pokemon Server** expone la API de PokéAPI a través del protocolo Model Context Protocol, permitiendo que LLMs como Claude accedan a datos de Pokemon de tres formas:

- **🛠️ Tools**: Llamadas directas a funciones para buscar y analizar datos
- **📝 Prompts**: Plantillas de contexto enriquecidas para análisis y estrategia
- **📚 Resources**: URIs de documentos que pueden ser referenciados como si fueran archivos

### Capacidades del Servidor

```
✅ 6 Tools
✅ 6 Prompts
✅ 6 Resource Types dinámicos
✅ Integración con PokéAPI v2
✅ Análisis de estadísticas
✅ Cálculos de efectividad de tipos
✅ Entrada completa de Pokédex con cadena evolutiva
✅ Análisis de equipo completo en paralelo
```

---

## 🛠️ Tools - Ejemplos Prácticos

### Tool 1: `get_pokemon_info`

**Propósito**: Obtener información detallada de un Pokemon específico.

**Parámetros**:
- `name_or_id` (string): Nombre o ID del Pokemon

**Casos de Uso**:

#### Ejemplo 1.1: Análisis Rápido
```
Pregunta: "Quién es Pikachu? Dame toda su información"
Acción: get_pokemon_info("pikachu")

Resultado:
• Nombre: Pikachu (#25)
• Altura: 0.4m
• Peso: 6.0kg
• Tipos: Electric
• Estadísticas base: HP 35, Ataque 55, Defensa 40, Sp.Ataque 50, Sp.Defensa 50, Velocidad 90
• Habilidades: Static, Lightning Rod (Hidden)
```

#### Ejemplo 1.2: Comparación de Evoluciones
```
Pregunta: "Compara a Charmander, Charmeleon y Charizard"
Acciones en cadena:
1. get_pokemon_info("charmander")
2. get_pokemon_info("charmeleon")
3. get_pokemon_info("charizard")

Obtén estadísticas para analizar cómo cambian los atributos en cada etapa de evolución
y qué nuevos tipos o habilidades aparecen.
```

#### Ejemplo 1.3: Verificación de Compatibilidad
```
Pregunta: "¿Puedo usar a Alakazam en modo offline?"
Acción: get_pokemon_info("alakazam")

Verifica: Estadísticas base, tipos, habilidades necesarias
Respuesta: Sí, es un Pokemon clásico disponible desde Gen 1
```

#### Ejemplo 1.4: Análisis de Base Stats para Competencia
```
Pregunta: "¿Es Dragonite competitivamente viable a nivel profesional?"
Acción: get_pokemon_info("dragonite")

Análisis:
• BST (Base Stat Total): 600 (Tier competitivo ✅)
• Tipos: Dragon/Flying (cobertura defensiva interesante)
• Ataque: 134 (muy alto para atacante físico)
• SpA: 100 (también viable en especial)
• Velocidad: 80 (moderada, necesita setup)
```

---

### Tool 2: `search_pokemon`

**Propósito**: Buscar y paginar a través de la lista de Pokemon.

**Parámetros**:
- `query` (string, opcional): Término de búsqueda para filtrar resultados
- `limit` (int, default: 20): Número máximo de resultados
- `offset` (int, default: 0): Posición inicial en la lista

**Casos de Uso**:

#### Ejemplo 2.1: Exploración Generacional
```
Pregunta: "Muéstrame los primeros 10 Pokemon originales"
Acción: search_pokemon(limit=10, offset=0)

Resultado:
#1: Bulbasaur
#2: Ivysaur
#3: Venusaur
#4: Charmander
#5: Charmeleon
#6: Charizard
#7: Squirtle
#8: Wartortle
#9: Blastoise
#10: Caterpie
```

#### Ejemplo 2.2: Navegación Paginada
```
Pregunta: "Dame los Pokemon del #50 al #70"
Acción: search_pokemon(limit=20, offset=49)

Útil para: Análisis de tendencias por generación, identificar patrones de diseño
```

#### Ejemplo 2.3: Descubrimiento Aleatorio
```
Pregunta: "Sugiere 5 Pokemon aleatorios para mi equipo nuevo"
Acciones:
1. search_pokemon(limit=100, offset=random())
2. Selecciona 5 de los resultados

Genera equipos impredecibles para desafíos de "Nuzlocke" o juego casual
```

#### Ejemplo 2.4: Análisis de Cobertura
```
Pregunta: "Necesito cobertura de tipos Dragon y Electric. ¿Quiénes son mis opciones?"
Acción: search_pokemon(limit=1000, offset=0)  # obtén lista completa después con paginación
Filtra: Busca Pokemon con tipo Dragon O Electric
```

---

### Tool 3: `get_type_effectiveness`

**Propósito**: Obtener tabla de efectividad de tipos (resistencias, debilidades).

**Parámetros**:
- `attacking_type` (string): Tipo atacante (ej: "fire", "water", "psychic")

**Casos de Uso**:

#### Ejemplo 3.1: Planificación Defensiva
```
Pregunta: "¿Contra qué tipos es débil un Pokemon Ghost?"
Acción: get_type_effectiveness("ghost")

Análisis:
• Super Efectivo CONTRA: Ghost, Psychic
• Débil ANTE: Ghost, Dark
• Immune A: Normal, Fighting
• Información clave: Busca Pokemon defensores Ghost para counter
```

#### Ejemplo 3.2: Construcción de Equipo Ofensivo
```
Pregunta: "Necesito atacantes que cubran todos los tipos"
Acciones:
1. get_type_effectiveness("water")
2. get_type_effectiveness("grass")
3. get_type_effectiveness("electric")
4. ... [continúa con todos los tipos]

Genera tabla de cobertura: qué tipos golpea cada movimiento
```

#### Ejemplo 3.3: Counter-Picking
```
Pregunta: "El líder de gimnasio tiene un equipo Fire. ¿Qué tipos debo usar?"
Acción: get_type_effectiveness("fire")

Resultado: Water, Ground, Rock son super efectivos
Busca Pokemon de esos tipos para construir estrategia
```

#### Ejemplo 3.4: Análisis de Cadenas de Tipo
```
Pregunta: "¿Cuál es el mejor tipo defensivo en Pokemon?"
Acciones:
1. get_type_effectiveness para TODOS los 18 tipos
2. Analiza cuántos tipos son super efectivos contra cada uno
3. Crea ranking de "defensas más sólidas"

Resultado: Tipos como Water, Psychic, Ground suelen tener defensas valiosas
```

---

### Tool 4: `analyze_pokemon_stats`

**Propósito**: Análisis profundo de estadísticas de un Pokemon.

**Parámetros**:
- `name_or_id` (string): Nombre o ID del Pokemon

**Casos de Uso**:

#### Ejemplo 4.1: Evaluación de Rol en Equipo
```
Pregunta: "¿En qué rol juega mejor Alakazam?"
Acción: analyze_pokemon_stats("alakazam")

Análisis:
• Velocidad: 120 (EXCELENTE - outspeeds casi todo)
• SpA: 135 (EXTREMADAMENTE ALTO)
• Ataque: 65 (TERRIBLE)
• Defensa: 65 (TERRIBLE)
• HP: 55 (BAJO - frágil)

Conclusión: Sweeper especial + velocidad. Nunca lo uses como defensor.
```

#### Ejemplo 4.2: Viabilidad de Sets
```
Pregunta: "¿Puedo hacer un Dragonite defensivo?"
Acción: analyze_pokemon_stats("dragonite")

Stats:
• Defensa: 80 (medio-bajo)
• Sp.Def: 80 (medio-bajo)
• HP: 91 (medio)
• Ataque: 134 (EXCELENTE)

Recomendación: Mejor como atacante físico. Si quieres defensivo, 
busca Pokemon especializados como Slowbro o Cresselia.
```

#### Ejemplo 4.3: Construcción de Sinergias
```
Pregunta: "¿Qué tipos de Pokemon complementan bien a Blissey en mi equipo?"
Acción: analyze_pokemon_stats("blissey")

Stats de Blissey:
• HP: 255 (MÁS ALTO DE TODOS)
• Defensa Esp: 135 (DEFENSOR ESPECIAL EXPERTO)
• Defensa: 35 (VULNERABLE FÍSICAMENTE)

Conclusión: Necesita compañeros que defiendan físicamente (Ferrothorn, Incineroar)
```

#### Ejemplo 4.4: Predicción de Tiers
```
Pregunta: "¿Es Metagross OU o UU tier?"
Acciones:
1. analyze_pokemon_stats("metagross")
2. Compara con otros del mismo tipo/rol

Stats: BST 600, ataque 135, velocidad 70, defensas decentes
Conclusión: OU tier (Overused) - bastante potente
```

---

### Tool 5: `get_pokedex_entry`

**Propósito**: Obtener una entrada completa de Pokédex con datos de especie, cadena evolutiva, textos de sabor (en español o inglés), habitat, tasa de captura, grupos de huevo, y más.

**Parámetros**:
- `name_or_id` (string): Nombre o ID del Pokemon (soporta formas alternativas, ej: "pikachu-alola")

**Casos de Uso**:

#### Ejemplo 5.1: Entrada Completa de Pokédex
```
Pregunta: "Dame la entrada completa de Pokédex de Pikachu como si fuera Dexter"
Acción: get_pokedex_entry("pikachu")

Resultado (JSON):
{
  "id": 25,
  "name": "pikachu",
  "genus": "Pokémon Ratón",
  "height_dm": 4,
  "weight_hg": 60,
  "color": "yellow",
  "types": ["electric"],
  "base_stats": { "hp": 35, "attack": 55, ... },
  "flavor_text": ["Almacena electricidad en sus mejillas..."],
  "generation": "I",
  "habitat": "forest",
  "is_legendary": false,
  "capture_rate": 190,
  "egg_groups": ["field", "fairy"],
  "evolution_chain": [
    {"name": "pichu", "via": {"trigger": "level-up", "min_happiness": 220}},
    {"name": "pikachu", "via": {"trigger": "level-up"}},
    {"name": "raichu", "via": {"trigger": "use-item", "item": "thunder-stone"}}
  ]
}
```

#### Ejemplo 5.2: Investigar Condiciones Evolutivas
```
Pregunta: "¿Cómo evoluciona Eevee y qué opciones tiene?"
Acción: get_pokedex_entry("eevee")

Resultado: Cadena evolutiva completa con todas las bifurcaciones de Eevee
y las condiciones de cada evolución (piedra, felicidad, horario, etc.)
```

#### Ejemplo 5.3: Comparar Formas Alternativas
```
Pregunta: "¿Es diferente Charizard de Kanto al Mega Charizard X?"
Acciones:
1. get_pokedex_entry("charizard")
2. get_pokedex_entry("charizard-mega-x")

Compara tipos, stats, habitat y generación de cada forma
```

#### Ejemplo 5.4: Filtrar Legendarios con Contexto Rico
```
Pregunta: "Cuéntame la historia de Mewtwo"
Acción: get_pokedex_entry("mewtwo")

Resultado:
• is_legendary: true
• habitat: "rare"
• flavor_text: ["Fue creado por un científico tras años de ingeniería genética..."]
• capture_rate: 3 (extremadamente difícil de capturar)
• generation: "I"
```

---

### Tool 6: `analyze_team`

**Propósito**: Analizar un equipo de 2-6 Pokémon en paralelo. Devuelve datos por miembro (tipos, stats, BST, roles de batalla) más métricas globales del equipo.

**Parámetros**:
- `pokemon_names` (list[string]): Lista de 2 a 6 nombres o IDs de Pokémon

**Casos de Uso**:

#### Ejemplo 6.1: Análisis Básico de Equipo Starter
```
Pregunta: "¿Es mi equipo de starters bien balanceado?"
Acción: analyze_team(["charizard", "blastoise", "venusaur"])

Resultado (JSON):
{
  "team_size": 3,
  "members": [
    {"name": "charizard", "types": ["fire", "flying"], "total_bst": 534, "roles": ["Attacker"]},
    {"name": "blastoise", "types": ["water"], "total_bst": 530, "roles": ["Tank"]},
    {"name": "venusaur", "types": ["grass", "poison"], "total_bst": 525, "roles": ["Balanced"]}
  ],
  "team_analysis": {
    "avg_bst": 529.7,
    "type_coverage": ["fire", "flying", "grass", "poison", "water"],
    "fastest": {"name": "charizard", "speed": 100},
    "strongest_physical": {"name": "charizard", "attack": 84},
    "strongest_special": {"name": "venusaur", "special_attack": 100},
    "bulkiest": {"name": "blastoise", "bulk_score": 244.8}
  }
}
```

#### Ejemplo 6.2: Equipo Competitivo - Identificar Roles
```
Pregunta: "¿Qué rol cumple cada Pokemon de mi equipo competitivo?"
Acción: analyze_team(["alakazam", "dragonite", "ferrothorn", "rotom-wash", "clefable", "landorus-therian"])

Analiza:
• Roles: Fast/Attacker, Attacker/Bulky, Tank, Tank, Bulky, Fast/Attacker
• Cobertura de tipos: psychic, dragon, flying, grass, steel, water, electric, normal, ground
• BST promedio del equipo
• Detecta si el equipo está sesgado a un tipo de rol
```

#### Ejemplo 6.3: Detectar Debilidades de Equipo
```
Pregunta: "¿Qué cubre peor mi equipo?"
Acción: analyze_team(["charizard", "raichu", "alakazam", "gengar", "machamp", "lapras"])

Con type_coverage puedes ver qué tipos tienes y combinar con
get_type_effectiveness para identificar huecos de cobertura defensiva/ofensiva
```

#### Ejemplo 6.4: Validar BST Promedio para Formato
```
Pregunta: "¿Mi equipo es lo suficientemente fuerte para el meta competitivo?"
Acción: analyze_team(["scizor", "garchomp", "blissey", "heatran", "tornadus-therian", "keldeo"])

Análisis:
• avg_bst >= 580 → Equipo muy fuerte (OU viable)
• role_distribution → ¿Hay balance de Attackers, Tanks, Fast?
• bulkiest → ¿Quién aguanta más para ser el wall?
```

---

## 📝 Prompts - Guías y Estrategias

El servidor incluye 6 plantillas de prompts divididas en dos categorías: **Educacionales** y **Batalla**.

### Categoría 1: Prompts Educacionales

#### Prompt 1: `educational/pokemon-analysis`

**Parámetros**:
- `pokemon_name`: El Pokemon a analizar
- `analysis_type`: "general" | "battle" | "competitive"
- `user_level`: "beginner" | "intermediate" | "advanced"

**Ejemplo 1.1: Análisis General para Principiantes**
```
Prompt: pokemon-analysis
Parámetros:
  pokemon_name: "pikachu"
  analysis_type: "general"
  user_level: "beginner"

Contenido generado:
📖 GUÍA PARA PRINCIPIANTES: Pikachu

¿Qué es Pikachu?
Pikachu es el Pokemon mascota más icónico de la franquicia...

Consejos para comenzar:
• Es débil contra tipos Ground
• Sus ataques son principalmente Electric
• Evoluciona a Raichu con Piedra Trueno
• Excelente para principiantes: velocidad alta, ataques decentes
```

**Ejemplo 1.2: Análisis Competitivo para Avanzados**
```
Prompt: pokemon-analysis
Parámetros:
  pokemon_name: "alakazam"
  analysis_type: "competitive"
  user_level: "advanced"

Contenido:
🏆 ANÁLISIS COMPETITIVO: Alakazam

Meta-role: Sweeper Especial de Velocidad
Tier: OU (Overused)

Setups Meta Actuales:
1. Choice Specs Sweeper
   • EV: 252 SpA / 4 SpD / 252 Spe
   • Moveset: Psychic, Focus Blast, Shadow Ball, Dazzling Gleam

2. Life Orb Mixed
   • EV: 64 Atk / 252 SpA / 192 Spe
   • Moveset: Psychic, Focus Blast, Hidden Power Fire, Trick

Counters: Pursuit trapper, Heatran, Tyranitar
```

**Ejemplo 1.3: Análisis de Batalla para Nivel Intermedio**
```
Prompt: pokemon-analysis
Parámetros:
  pokemon_name: "dragonite"
  analysis_type: "battle"
  user_level: "intermediate"

Contenido:
⚔️ GUÍA DE BATALLA: Dragonite

Ventajas:
• Ataque base 134 - puede KO muchos Pokemon
• Tipo Dragon/Flying - buena cobertura
• Habilidades útiles: Marvel Scale (resiste estatus)

Desventajas:
• 4x débil a Hielo (CRÍTICO)
• Velocidad 80 - necesita soporte

Tácticas Recomendadas:
1. Usa como sweeper con stat boosts
2. Apunta a Pokemon débiles contra Dragon
3. Cuida la entrada - los movimientos Hielo son peligrosos
```

---

#### Prompt 2: `educational/type-effectiveness`

**Parámetros**:
- `scenario`: "learning" | "quiz" | "battle-analysis"
- `attacking_type`: Tipo específico a enfocarse
- `defending_types`: Opcional - tipos defensores para analizar

**Ejemplo 2.1: Aprendizaje Interactivo**
```
Prompt: type-effectiveness
Parámetros:
  scenario: "learning"
  attacking_type: "water"
  defending_types: null

Contenido:
🌊 APRENDE: Tipos en Pokemon - Water

¿Por qué Water es importante?

Agua está super efectiva contra:
• Fire - imagina verter agua en fuego
• Ground - el agua erosiona la tierra
• Rock - el agua disuelve la roca

Agua es débil ante:
• Electric - el agua conduce electricidad
• Grass - las plantas absorben agua
• Ice - su mismo tipo, congelado

Consejos prácticos:
• Usa Water contra Pokemon Fire para ganar fácil
• Evita Pokemon Electric
• Servicios como Aqua Jet dan ventaja de velocidad
```

**Ejemplo 2.2: Quiz Interactivo**
```
Prompt: type-effectiveness
Parámetros:
  scenario: "quiz"
  attacking_type: "psychic"

Contenido:
❓ QUIZ: ¿Cuánto sabes sobre Psychic?

Pregunta 1: ¿Contra qué tipo es super efectivo Psychic?
Opciones: A) Dark  B) Fighting  C) Normal  D) Electric

Pregunta 2: ¿Qué tipo realmente RESISTE ataques Psychic?
Opciones: A) Poison  B) Psychic  C) Steel  D) Water

[+ 8 preguntas más con explicaciones]
```

**Ejemplo 2.3: Análisis de Batalla**
```
Prompt: type-effectiveness
Parámetros:
  scenario: "battle-analysis"
  attacking_type: "ground"
  defending_types: ["fire", "electric", "poison"]

Contenido:
⚔️ ANÁLISIS: Ground vs Fire/Electric/Poison

Ground Attack vs Fire:
✅ Super Efectivo - Earthquake destruye Pokemon Fire

Ground Attack vs Electric:
✅ EXCELENTE - Ningún Pokemon Electric verá venir tu Earthquake

Ground Attack vs Poison:
✅ Super Efectivo - Coverage excelente

Conclusión: Un movimiento Ground destruye todos estos tipos
```

---

#### Prompt 3: `educational/team-building`

**Parámetros**:
- `theme`: "balanced" | "offensive" | "defensive" | "type-specific"
- `format`: "casual" | "competitive" | "tournament"
- `restrictions`: Opcional (ej: "no legendaries", "gen 1 only")

**Ejemplo 3.1: Equipo Balanceado Casual**
```
Prompt: team-building
Parámetros:
  theme: "balanced"
  format: "casual"
  restrictions: "no legendaries"

Contenido Generado:
🎮 EQUIPO BALANCEADO PARA CASUAL

Equipo Recomendado:
1. Charizard (Fuego/Volador) - Physical Sweeper
2. Blastoise (Agua) - Defensivo/Support
3. Venusaur (Planta/Veneno) - Especial/Coverage
4. Machamp (Lucha) - Sweeper Físico
5. Gengar (Fantasma/Veneno) - Sweeper Especial
6. Arcanine (Fuego) - Velocidad/Sweeper

Cobertura de Tipos:
✅ Cubre: Fire, Water, Grass, Fighting, Ghost, Psychic
✅ Resistencias cruzadas múltiples
⚠️ Débil a: Rock (común)

Estrategia: Alternancia de atacantes
```

**Ejemplo 3.2: Equipo Ofensivo Competitivo**
```
Prompt: team-building
Parámetros:
  theme: "offensive"
  format: "competitive"
  restrictions: null

Contenido:
🔥 EQUIPO OFENSIVO COMPETITIVO

Núcleo Ofensivo:
1. Dragonite (Dragon/Flying) - Dragon Dance Sweeper
2. Alakazam (Psychic) - Choice Specs Sweeper Especial
3. Landorus-T (Ground/Flying) - Stealth Rock / Pivot / Ofensiva
4. Weavile (Dark/Ice) - Taunt / Trick Room denier
5. Gengar (Ghost/Poison) - Specs Sweeper / Taunt
6. Blaziken (Fire/Fighting) - Speed Boost Setup Sweeper

Estrategia: Hazards + múltiples sweepers
Roles: 3 sweepers, 1 hazard setter, 1 pivot, 1 support
```

**Ejemplo 3.3: Equipo Defensivo Corporativo Con Restricciones**
```
Prompt: team-building
Parámetros:
  theme: "defensive"
  format: "competitive"
  restrictions: "Gen 1-5 only, no dupes"

Contenido:
🛡️ EQUIPO DEFENSIVO (Gens 1-5)

Línea Defensiva Especializada:
1. Ferrothorn (Grass/Steel) - Hazard Setup / Core Defensivo
2. Blissey (Normal) - Especial Wall
3. Slowbro (Water/Psychic) - Físico Wall
4. Tyranitar (Rock/Dark) - Hazard Setup / Special Wall
5. Alakazam (Psychic) - Sweeper para balance ofensivo
6. Dragonite (Dragon/Flying) - Pivot / Sweeper

Cobertura Defensiva: Todas las debilidades cubiertas
Stall vs Ofensiva: Híbrido defensivo
```

---

### Categoría 2: Prompts de Batalla

#### Prompt 4: `battle/strategy-analysis`

**Parámetros**:
- `user_team`: Lista de Pokemon en tu equipo
- `opponent_team`: Lista opcional del equipo contrario
- `battle_format`: "singles" | "doubles" | "multi"
- `strategy_focus`: "offensive" | "defensive" | "balanced" | "utility"

**Ejemplo 4.1: Análisis de Estrategia en Singles sin Conocer al Oponente**
```
Prompt: battle/strategy-analysis
Parámetros:
  user_team: ["Alakazam", "Dragonite", "Landorus-T", "Weavile", "Gengar", "Blaziken"]
  opponent_team: null
  battle_format: "singles"
  strategy_focus: "offensive"

Contenido:
⚔️ ESTRATEGIA DE BATALLA - SINGLES OFENSIVO

Tu Equipo: Seis sweepers / Hazard setter
Ventaja: Presión constante, múltiples amenazas
Desventaja: Sin defensas claras

Aperturas Recomendadas:
1. Landorus-T si hay Stealth Rocks disponibles
2. Alakazam contra equipos lentos
3. Dragonite si ves oportunidad para Dance

Puntos Críticos:
⚠️ Evita entradas malas - podrías perder momentum
✅ Abusa de tu velocidad
```

**Ejemplo 4.2: Counter-Picking con Equipo Conocido**
```
Prompt: battle/strategy-analysis
Parámetros:
  user_team: ["Ferrothorn", "Blissey", "Slowbro", "Tyranitar", "Alakazam", "Dragonite"]
  opponent_team: ["Blaziken", "Alakazam", "Ferrothorn", "Rotom-W", "Gastrodon", "Gengar"]
  battle_format: "singles"
  strategy_focus: "balanced"

Contenido:
📊 ANÁLISIS: TU EQUIPO vs OPONENTE

Matchups Críticos:
✅ Tu Ferrothorn > Su Blaziken (switcheo seguro)
❌ Su Alakazam > Tu Blissey (trap peligroso)
✅ Tu Tyranitar > Su Gengar (resiste ataques)
⚠️ Su Rotom-W es problema para ambos lados

Recomendación de Orden de Batalla:
1. Entra con Ferrothorn contra Blaziken
2. Usa Tyranitar como pivot
3. Salva Alakazam para limpiar final
```

#### Prompt 5: `battle/movepool-optimization`

**Parámetros**:
- `pokemon_name`: Pokemon a optimizar
- `role`: Rol asignado ("sweeper", "wall", "pivot", etc)
- `metagame`: "ou" | "uu" | "ru" | "casual" | "rental"

**Ejemplo 5.1: Optimización de Sweeper**
```
Prompt: battle/movepool-optimization
Parámetros:
  pokemon_name: "Alakazam"
  role: "sweeper"
  metagame: "ou"

Contenido:
🎯 MOVESET ÓPTIMO: Alakazam Sweeper (OU)

Opciones Primarias (STAB):
1. Psychic - STAB confiable, buen poder
2. Focused Blast - Coverage vs Dark/Psychic

Opciones de Coverage:
1. Shadow Ball - Hits Dark types switcheando en
2. Dazzling Gleam - Hits Dark types, bonus coverage
3. Hidden Power Fire - Hits Steel types

MOVESET 1: Choice Specs
Psychic / Focused Blast / Shadow Ball / Dazzling Gleam

MOVESET 2: Life Orb Mixed
Psychic / Focused Blast / Hidden Power Fire / Trick
```

**Ejemplo 5.2: Optimización Defensiva**
```
Prompt: battle/movepool-optimization
Parámetros:
  pokemon_name: "Ferrothorn"
  role: "wall"
  metagame: "ou"

Contenido:
🛡️ MOVESET ÓPTIMO: Ferrothorn Wall (OU)

Moveset Principal:
Power Whip - STAB ofensivo para no ser 100% pasivo
Stealth Rock - Hazard setup crítico
Leech Seed - Recovery sostenida
Protect - Stalling core

Alternativas:
- Spikes en lugar de SR si hay redundancia
- Thunder Wave para paralización
- Knock Off para remover items

MOVESET RECOMENDADO:
Power Whip / Stealth Rock / Leech Seed / Protect
EV: 252 HP / 88 Def / 168 SpD
```

#### Prompt 6: `battle/format-guide`

**Parámetros**:
- `format`: Formato de batalla
- `skill_level`: "casual" | "intermediate" | "competitive"

**Ejemplo 6.1: Guía de Dobles para Principiantes**
```
Prompt: battle/format-guide
Parámetros:
  format: "doubles"
  skill_level: "casual"

Contenido:
👥 GUÍA: BATALLAS EN DOBLES

¿Qué es diferente?
• 4 Pokemon en campo simultáneamente
• Synergy > Contador individual
• Ataques AOE son valiosísimos

Pokémon Excelentes para Dobles Casual:
1. Landorus - Intimidate reduce ataque físico
2. Salamence - Siempre fue diseñado para dobles
3. Vulkan - Guarda a su partner
4. Dusknoir - Opción defensiva

Movimientos Clave en Dobles:
• Earthquake - AOE estándar
• Fake Out - Priority que afecta a dos
• Tailwind - Boosts compartidos
• Protect - Cierra turno defensivamente
```

**Ejemplo 6.2: Metagame de Multibatalla Avanzado**
```
Prompt: battle/format-guide
Parámetros:
  format: "multi"
  skill_level: "competitive"

Contenido:
🎮 METAGAME AVANZADO: MULTIBATALLA

Dinámicas de 3 vs 1:
• Los 3 pueden coordinarse teóricamente
• El 1 debe ser especialmente fuerte
• Alianzas cambian según ataques

EV Distribution para Multi:
Los Pokémon necesitan balances raros porque:
- Un atacante puede KO en 1 golpe
- Necesitas velocidad para outspeeds múltiples oponentes

Estrategias Top Tier:
1. Equipo "Carry" con inmunidades
2. Setup sweeper + Walls tanquean
3. Misdirection spreads damage
```

---

## 📚 Resources - Acceso a Datos

Resources permiten referenciar datos como si fueran documentos. Son especialmente útiles para proporcionar contexto sin llamadas de herramienta explícitas.

### Resource 1: `pokemon://info/{name}`

**Patrón**: Información detallada de un Pokemon

**Ejemplo 1.1: Contexto para Análisis**
```
Request: 
"Basándote en pokemon://info/dragonite, construye un set competitivo"

Contenido del recurso:
# Dragonite (Dragon/Flying)

## Stats Base
- HP: 91
- Ataque: 134
- Defensa: 80
- SpA: 100
- SpD: 80
- Velocidad: 80
- BST: 600

## Abilities
- Intimidate (standard)
- Multiscale (hidden)
- Marvel Scale (competitive)

## Moves learned
[Lista completa de movimientos]
```

### Resource 2: `pokemon://stats/{name}`

**Patrón**: Análisis estadístico profundo

**Ejemplo 2.1: Comparativa de Atributos**
```
Request:
"Necesito saber si pokemon://stats/alakazam vs pokemon://stats/alakazam-galar 
para decidir cuál entrenador usar"

Análisis automático:
- Alakazam: SpA 135, Velocidad 120
- Alakazam-Galar: SpA 65, Velocidad 80, Especia Def 95 (nuevo tipo Psychic/Normal)

Diferencia clara: Normal Alakazam es sweeper, Galar es defensivo
```

### Resource 3: `pokemon://moveset/{name}`

**Patrón**: Todos los movimientos disponibles

**Ejemplo 3.1: Construcción de Moveset**
```
Request:
"Quiero hacer un set troll con Alakazam. Usa pokemon://moveset/alakazam 
para ver qué movimientos raros puede aprender"

Resultado:
- Thunder Punch (Move Tutor)
- Fire Punch (Move Tutor)
- Ice Punch (Move Tutor)
- Trick (solo en algunos genomes)
- Disabled (breeding)
- Memento (breeding)

Idea troll: "Memento Alakazam" - surprise factor 100%
```

### Resource 4: `pokemon://type/{type_name}`

**Patrón**: Información de un tipo

**Ejemplo 4.1: Construcción de Equipo Mono-Tipo**
```
Request:
"Quiero un equipo mono-Fire. Usa pokemon://type/fire para ver opciones"

Resultado incluye:
- Todos los Pokemon de tipo Fire
- Efectividades base
- Resumen de debilidades del tipo

Análisis:
- Fire tipo es débil a Water/Ground/Rock (muchas debilidades)
- Necesitarás defensive Pokemon para cubrir estas
```

### Resource 5: `pokemon://comparison/{pokemon1}/{pokemon2}`

**Patrón**: Comparación lado a lado

**Ejemplo 5.1: Decidir Evolución**
```
Request:
"Debo elegir entre Alakazam o Machamp. Compárelos con 
pokemon://comparison/alakazam/machamp"

Resultado:
| Stat | Alakazam | Machamp |
|------|----------|---------|
| Ataque | 65 | 130 |
| SpA | 135 | 65 |
| Velocidad | 120 | 55 |
| Hp | 55 | 63 |

Conclusión: Alakazam si quieres velocidad y magia especial,
Machamp si quieres poder físico brutal
```

---

## 🚀 Combinaciones Avanzadas

### Combinación 1: "Dream Team Analyzer"

**Objetivo**: Crear un equipo y analizar cada Pokemon + sinergias

**Proceso**:
```
1. search_pokemon(limit=100) - Obtén opciones amplias
2. Para cada Pokemon elegido:
   - get_pokedex_entry(pokemon)     ← entrada completa con cadena evolutiva
   - analyze_pokemon_stats(pokemon) ← insights estadísticos
3. analyze_team([pokemon1, ..., pokemon6]) ← métricas globales del equipo
4. Para cada tipo del equipo:
   - get_type_effectiveness(type)
5. Usa prompt: team-building + strategy-analysis
```

**Ejemplo**:
```
"Quiero los 6 mejores Pokemon para mi primer juego. Que sea canon, balanceado
y divertido. Usa las herramientas para sugerirme opciones, analiza coberturas
de tipo, y dame una estrategia inicial."

Resultado: Equipo completo con estrategia personalizada + cadenas evolutivas
```

### Combinación 2: "Competitive Builder"

**Objetivo**: Meta-game analysis y team construction

**Pasos**:
```
1. analyze_pokemon_stats - de varios Pokemon candidatos
2. get_type_effectiveness - para todas las debilidades
3. analyze_team([lista final]) - métricas del equipo de golpe
4. prompt: competitive team-building
5. prompt: strategy-analysis
```

**Ejemplo**:
```
"Construyeme un equipo OU competitivo. Analiza el meta actual y dame
setups de movimientos optimizados para cada Pokemon del equipo."
```

### Combinación 3: "Weakness Finder & Counter Kit"

**Objetivo**: Identificar debilidades y construir counters

**Flujo**:
```
1. get_pokemon_info - del Pokemon problema
2. get_type_effectiveness - del tipo del Pokemon
3. search_pokemon - filtrando tipos super efectivos
4. compare statsísticas - de options de counters
```

**Ejemplo**:
```
"Dragonite me está destruyendo. ¿Cómo lo counter?"

Respuesta:
1. Analiza Dragonite (Dragon/Flying)
2. Muestra que Hielo es 4x efectivo
3. Sugiere Pokemon Ice como Lapras, Mamoswine
4. Compara cual es el mejor contador
```

### Combinación 4: "Pokédex Narrator & Evolution Planner"

**Objetivo**: Contar la historia completa de un Pokemon con cadena evolutiva

**Flujo**:
```
1. get_pokedex_entry(pokemon) - Obtén flavor text, habitat, rareza, genus
2. Para cada etapa de la cadena evolutiva del resultado:
   - get_pokemon_info(etapa) - Stats y detalles de cada forma
3. analyze_team([todas las etapas]) - Compara BST a través de la evolución
```

**Ejemplo**:
```
"Narraré la historia de Magikarp a Gyarados"

1. get_pokedex_entry("magikarp")
   → flavor_text: "Pokémon casi inútil, muy débil"
   → evolution_chain: magikarp → gyarados (level 20)
   → capture_rate: 45 (fácil de capturar)

2. get_pokedex_entry("gyarados")
   → is_legendary: false, pero BST 540
   → flavor_text: "Cuando se enfurece, destruye todo..."

3. analyze_team(["magikarp", "gyarados"])
   → BST: 200 vs 540 — la mayor diferencia de la línea evolutiva
```

### Combinación 5: "Team Health Check"

**Objetivo**: Diagnóstico rápido de un equipo existente

**Flujo**:
```
1. analyze_team([equipo completo]) - Diagnóstico de golpe
2. Para los Pokemon con roles inesperados:
   - analyze_pokemon_stats(pokemon) - Verificar si encajan en el rol
3. get_type_effectiveness para los tipos no cubiertos por type_coverage
```

**Ejemplo**:
```
"Tengo este equipo, ¿está bien?"
analyze_team(["garchomp", "blissey", "scizor", "starmie", "heatran", "rotom-wash"])

En una sola llamada obtienes:
• avg_bst: 555 → Sólido
• role_distribution: {Fast: 3, Attacker: 4, Tank: 2, Bulky: 2}
• type_coverage: 12 tipos distintos → Buena cobertura
• bulkiest: blissey → Confirma su rol de wall especial
```
```

---

## 🎯 Casos de Uso Completos

### Caso 1: "Entrenador Principiante - Primer Aventura"

**Escenario**: Usuario jugando Pokemon por primera vez

**Workflow Completo**:
```
Paso 1: "¿Qué starter debo elegir?"
- Acción: get_pokemon_info("bulbasaur", "charmander", "squirtle")
- Acción: analyze_pokemon_stats para cada uno
- Resultado: Recomendaciones basadas en estilos de juego

Paso 2: "¿Cómo construyo mi equipo?"
- Acción: prompt educational/team-building (casual, beginner)
- Resultado: Equipo equilibrado sugerido

Paso 3: "¿Cómo gano los primeros gimnasios?"
- Acción: get_type_effectiveness para tipos de líderes
- Acción: prompt pokemon-analysis para cada team member (beginner level)
- Resultado: Guía de batalla personalizada

Paso 4: "¿Es mi equipo competitivo?"
- Acción: analyze_pokemon_stats de todo el equipo
- Resultado: Hones feedback - "Bueno para casual, pero..."
```

**Resultado Final**: Usuario aprende jugando + construye confianza

---

### Caso 2: "Competidor Serio - Meta Mastery"

**Escenario**: Usuario quiere ser competitivo OU

**El Workflow**:
```
Semana 1 - Meta Analysis:
- search_pokemon + analyze_pokemon_stats de top 50 OU Pokemon
- get_type_effectiveness para construir tabla de matchups
- Result: Comprende qué es viable

Semana 2 - Team Building:
- prompt: competitive team-building (theme: balanced, competitive)
- result: Arquitectura de equipo

Semana 3 - Team Refinement:
- prompt: movepool-optimization para cada Pokemon
- prompt: battle/strategy-analysis
- result: 6 Pokemon en optimal sets

Semana 4 - Battle Practice:
- prompt: strategy-analysis con opposition analysis
- result: Gana primeros torneos
```

---

### Caso 3: "Content Creator - Video Ejemplos"

**Escenario**: YouTuber que hace guías de Pokemon

**Content Template**:
```
Video Script Builder:
1. Intro: analyze_pokemon_stats del "Pokemon del episodio"
2. Evolution Line: get_pokemon_info para Charmander -> Char -> Zard
3. Type Advantage Segment: get_type_effectiveness
4. Team Building Guide: prompt team-building para tema específico
5. Battle Strategy: prompt battle/strategy-analysis con ejemplo
6. Moveset Guide: prompt movepool-optimization

Todo automáticamente referenciable, sin investigación manual
```

---

### Caso 4: "Nuzlocke Challenge Strategist"

**Escenario**: Guía para desafíos tipo "Nuzlocke" (permadeath)

**Workflow**:
```
Previo a Gymn Leader:
1. search_pokemon: obtén team del líder (spoiler-free si quiered)
2. Para cada Pokemon del líder:
   - get_pokemon_info
   - get_type_effectiveness
3. prompt: battle/strategy-analysis (defensive focus)
4. Resultado: Counter picks + táctica de batalla

Durante la batalla:
- Referencia los matchups
- Adapta basado en sets reales visto

Post-victoria:
- Graba tus Pokemon majestuosos (o entierros memorables)
```

---

## 💡 Tips y Best Practices

### ✅ DO - Lo que SÍ debes hacer

1. **Combina Tools + Prompts**
   ```
   ❌ Evita: Solo get_pokemon_info("alakazam")
   ✅ Haz: get_pokemon_info + analyze_pokemon_stats + prompt analysis
   ```

2. **Usa Resources para Contexto**
   ```
   ✅ Referencia pokemon://info/charizard en tus análisis
   ✅ El server inyecta el contexto automáticamente
   ```

3. **Aprovecha la Paginación**
   ```
   ✅ search_pokemon(limit=20, offset=n) para descubrir estrategias
   ✅ No necesitas resultados - usa para exploración
   ```

4. **Especializa los Prompts**
   ```
   ✅ Para principiantes: user_level="beginner"
   ✅ Para competencia: format="competitive"
   ✅ Nivel correcto = explicación más relevante
   ```

### ❌ DON'T - Lo que NO debes hacer

1. **Sobre-llamar Tools**
   ```
   ❌ Evita: get_pokemon_info para todos los 1000 Pokemon
   ✅ Usa: search_pokemon primero, luego filtra
   ```

2. **Ignorar Type Matchups**
   ```
   ❌ Construir equipo sin get_type_effectiveness
   ✅ Siempre verifica coberturas
   ```

3. **No aprovechar análisis profundo**
   ```
   ❌ Solo mirar números de base stats
   ✅ Usa analyze_pokemon_stats para insights
   ```

### 🎯 Optimization Tips

**Para Searches Grandes**:
```
search_pokemon(limit=100, offset=n) -> filtra cliente-side
Mejor que llamar 1000 veces
```

**Para Análisis Rápidos**:
```
get_pokemon_info + get_type_effectiveness en paralelo
No necesitas esperar entre llamadas
```

**Para Documentación**:
```
Referencia Resources: pokemon://info/{name}
Se carga automáticamente como contexto
Más limpio que tool responses raw
```

---

## 🎬 Plantillas Listas para Usar

### Template 1: "Team Builder X"
```
"Necesito un equipo {theme} para {format}. 
Build usando: 
1. search_pokemon para opciones
2. analyze_pokemon_stats para viabilidad
3. get_type_effectiveness para cobertura
4. prompt team-building para estrategia
Resultado: Equipo completo listo"
```

### Template 2: "Counter Finder"
```
"El entrenador {name} tiene {pokemon1, pokemon2, ...}
Usa:
1. get_pokemon_info para cada uno
2. get_type_effectiveness para debilidades
3. search_pokemon filtrando tipos super efectivos
Resultado: Counters clasificados + táctica"
```

### Template 3: "Competitive Optimizer"
```
"Optimiza mi team {pokemon_list} para {metagame}
1. analyze_pokemon_stats de cada uno
2. prompt movepool-optimization con role específico
3. prompt strategy-analysis
Resultado: Movesets + estrategia competitive"
```

### Template 4: "Pokédex Deep Dive"
```
"Cuéntame todo sobre {pokemon}: su historia, evoluciones y rareza
1. get_pokedex_entry({pokemon}) - Entrada completa con cadena evolutiva
2. Para cada etapa: get_pokemon_info({etapa})
Resultado: Narrativa completa con flavor text y condiciones evolutivas"
```

### Template 5: "Quick Team Audit"
```
"Audita mi equipo actual: {pokemon1, pokemon2, ..., pokemon6}
1. analyze_team([{lista}]) - Diagnóstico instantáneo
2. get_type_effectiveness para huecos de cobertura detectados
Resultado: Métricas del equipo, roles, fortalezas y debilidades"
```

---

## 📞 Soporte & Recursos

- **PokéAPI Docs**: https://pokeapi.co/docs/v2
- **Competitive Meta**: Usa "OU/UU/RU tier" en búsquedas
- **Gen Filtering**: search_pokemon con offsets específicos

---

**¡Ahora tienes todo lo que necesitas para dominar el MCP Pokemon Server! 🚀**

*Última actualización: 2026 — v2.0 (6 tools: añadidas get_pokedex_entry y analyze_team)*
