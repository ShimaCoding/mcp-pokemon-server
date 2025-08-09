# Ejemplos de Uso - Herramientas de Elicitación Interactiva

Este documento muestra ejemplos prácticos de cómo usar las herramientas de elicitación interactiva del servidor MCP Pokemon.

## 🎯 ¿Qué es la Elicitación Interactiva?

La elicitación interactiva es un patrón conversacional donde el servidor MCP guía al usuario a través de múltiples pasos para recopilar información necesaria y proporcionar respuestas personalizadas. Es especialmente útil para:

- Flujos complejos que requieren múltiples entradas
- Validación de datos en tiempo real
- Experiencias conversacionales más naturales
- Construcción progresiva de respuestas complejas

## 🛠️ Herramientas Disponibles

### 1. `get_pokemon_info_interactive` - Elicitación Simple

**Propósito:** Obtener información de un Pokémon con guía interactiva.

**Ejemplo de Flujo:**

```
Usuario: [Llama la herramienta sin parámetros]
Servidor: "🤖 ¿De qué Pokémon quieres saber información? (Escribe el nombre o número)"

Usuario: "pikachu"
Servidor: [Devuelve información completa de Pikachu]

Usuario: "fakemon"
Servidor: "🤖 ❌ No encontré información para 'fakemon'. ¿Puedes escribir otro nombre? (Ejemplos: pikachu, charizard, 25)"
```

**Características:**
- Manejo de errores con re-elicitación
- Validación de nombres de Pokémon
- Respuesta inmediata para nombres válidos

### 2. `build_pokemon_team_interactive` - Elicitación Intermedia

**Propósito:** Construir un equipo de 3 Pokémon paso a paso.

**Ejemplo de Flujo:**

```
Usuario: [Llama la herramienta]
Servidor: "🤖 🎯 Construyamos tu equipo Pokémon de 3. Dime el nombre del Pokémon #1:"

Usuario: "charizard"
Servidor: "🤖 🎯 Construyamos tu equipo Pokémon de 3.

**Equipo actual:**
1. Charizard (#6) - Tipos: Fire, Flying

Dime el nombre del Pokémon #2:"

Usuario: "charizard"
Servidor: "🤖 ❌ Ya tienes a charizard en tu equipo. Elige un Pokémon diferente para la posición #2:"

Usuario: "blastoise"
Servidor: [Continúa con el Pokémon #3]

Usuario: "venusaur"
Servidor: [Muestra análisis final del equipo completo]
```

**Características:**
- Seguimiento del progreso del equipo
- Detección de duplicados
- Validación de cada Pokémon
- Análisis estadístico final del equipo
- Cobertura de tipos y balance

### 3. `suggest_pokemon_by_criteria_interactive` - Elicitación Avanzada

**Propósito:** Sugerir Pokémon basado en tipo y rol con múltiples criterios.

**Ejemplo de Flujo Completo:**

```
Usuario: [Llama la herramienta]
Servidor: "🤖 🎯 ¡Te ayudo a encontrar el Pokémon perfecto!

¿Qué tipo de Pokémon prefieres? (Ejemplos: fuego, agua, planta, eléctrico, dragón...)"

Usuario: "fuego"
Servidor: "🤖 Perfecto, tipo Fuego 🔥

¿Qué rol buscas?
- **ataque**: Pokémon ofensivos
- **defensa**: Pokémon defensivos
- **soporte**: Pokémon de apoyo
- **velocidad**: Pokémon rápidos
- **equilibrado**: Pokémon versátiles"

Usuario: "ataque"
Servidor: "🤖 🎯 Te sugiero **Charizard**!

- **Tipo:** Fire, Flying
- **Fortaleza:** Ataque: 109
- **¿Por qué?** Excelente para roles ofensivos con alto daño.

¿Te gusta esta opción? (sí/no, o 'otro' para ver más opciones)"

Usuario: "no"
Servidor: "🤖 🎯 Te sugiero **Arcanine**!

- **Tipo:** Fire
- **Fortaleza:** Ataque: 110
- **¿Por qué?** Gran atacante físico con excelente velocidad.

¿Te gusta esta opción? (sí/no, o 'otro' para ver más opciones)"

Usuario: "sí"
Servidor: [Devuelve información detallada de Arcanine como elección final]
```

**Características Avanzadas:**
- Traducción automática de tipos (español ↔ inglés)
- Múltiples sugerencias basadas en criterios
- Manejo de rechazo con alternativas
- Análisis inteligente de roles (ataque, defensa, velocidad, etc.)
- Comando "reiniciar" para empezar de nuevo
- Exclusión de sugerencias ya rechazadas

## 🔧 Manejo de Estados

### Estado en Elicitación Simple
```python
# Estado mínimo
{
    "pokemon_name": "pikachu"
}
```

### Estado en Elicitación Intermedia
```python
# Estado del equipo en progreso
{
    "team": [
        {
            "name": "charizard",
            "id": 6,
            "types": ["fire", "flying"],
            "total_stats": 534
        },
        {
            "name": "blastoise",
            "id": 9,
            "types": ["water"],
            "total_stats": 534
        }
    ]
}
```

### Estado en Elicitación Avanzada
```python
# Estado complejo con múltiples criterios
{
    "type": "fire",
    "role": "ataque",
    "current_suggestion": {
        "name": "charizard",
        "id": 6,
        "types": ["fire", "flying"],
        "highlight": "Ataque: 109",
        "reason": "Excelente para roles ofensivos."
    },
    "available_suggestions": [
        {"name": "arcanine", ...},
        {"name": "rapidash", ...}
    ],
    "rejected_suggestions": ["charmander"]
}
```

## 🧪 Casos de Prueba

### Casos de Error Manejados

1. **Pokémon Inexistente:**
   ```
   Usuario: "fakemon"
   Respuesta: Re-elicitación con mensaje de error útil
   ```

2. **Tipo Inválido:**
   ```
   Usuario: "tipofalso"
   Respuesta: Lista de tipos válidos y re-elicitación
   ```

3. **Duplicados en Equipo:**
   ```
   Usuario: "pikachu" (ya en equipo)
   Respuesta: Mensaje de error y solicitud de otro Pokémon
   ```

4. **Sin Más Sugerencias:**
   ```
   Usuario: "no" (a todas las sugerencias)
   Respuesta: Opción de cambiar criterios o reiniciar
   ```

### Comandos Especiales

- **"reiniciar"**: Borra todo el estado y comienza de nuevo
- **"sí"/"si"/"yes"**: Acepta la sugerencia actual
- **"no"/"otro"**: Rechaza y pide siguiente sugerencia

## 📊 Validaciones Implementadas

### Validación de Tipos Pokémon
- 18 tipos oficiales soportados
- Traducción automática español-inglés
- Sugerencias cuando el tipo es inválido

### Validación de Roles
- **ataque**: Pokémon con stats ofensivas altas
- **defensa**: Pokémon con stats defensivas altas
- **velocidad**: Pokémon con speed ≥ 90
- **soporte**: Pokémon con HP alto para supervivencia
- **equilibrado**: Pokémon con stats balanceadas

### Análisis Estadístico
- Filtrado de Pokémon débiles (total stats < 300)
- Análisis de rol basado en stats base
- Cálculo de balance y cobertura de tipos en equipos

## 🚀 Integración con Cliente MCP

### Llamada Básica
```python
# Cliente MCP
result = await client.call_tool(
    "get_pokemon_info_interactive",
    {"pokemon_name": "pikachu"}
)
```

### Llamada con Estado
```python
# Continuación de conversación
result = await client.call_tool(
    "build_pokemon_team_interactive",
    {
        "pokemon_name": "charizard",
        "state": {"team": []}
    }
)
```

### Detección de Elicitación
```python
# Verificar si necesita más información
if result.startswith("ELICIT:"):
    prompt = result[7:]  # Remover prefijo "ELICIT:"
    # Mostrar prompt al usuario y esperar respuesta
else:
    # Mostrar resultado final
    print(result)
```

## 🎯 Beneficios de Este Enfoque

1. **Experiencia de Usuario Natural**: Conversación fluida sin formularios complejos
2. **Validación en Tiempo Real**: Errores detectados y corregidos inmediatamente
3. **Estado Persistente**: El contexto se mantiene entre interacciones
4. **Recuperación de Errores**: Manejo elegante de entradas inválidas
5. **Flexibilidad**: Usuarios pueden cambiar de opinión o reiniciar en cualquier momento
6. **Escalabilidad**: Patrón fácil de extender para nuevas funcionalidades

## 🔮 Casos de Uso Futuros

- Construcción de equipos competitivos con restricciones de tier
- Análisis de matchups con múltiples variables
- Simulador de batallas interactivo
- Tutorial paso a paso para nuevos jugadores
- Configurador de movimientos y habilidades
- Planificador de entrenamientos EV/IV

## 📝 Notas para Desarrolladores

- **Performance**: Las sugerencias están limitadas a los primeros 20 Pokémon del tipo para evitar timeouts
- **Cache**: Considera implementar cache para las consultas de tipo frecuentes
- **Extensibilidad**: El patrón `_analyze_pokemon_for_role` es fácil de extender
- **Testing**: Cada flujo tiene tests unitarios completos
- **Logging**: Todas las interacciones están loggeadas para debugging
