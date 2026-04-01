# MCP Pokemon Server

Servidor MCP en producción construido con **FastMCP** y **PokéAPI**. Expone herramientas, recursos y prompts para que cualquier cliente MCP pueda consultar datos de Pokémon de forma conversacional.

**Endpoint público:** `https://mcpokedex.com/mcp`

---

## Capacidades

### Herramientas (Tools)

| Herramienta | Descripción |
|-------------|-------------|
| `get_pokemon_info` | Información completa de un Pokémon por nombre o ID (tipos, stats, habilidades, altura, peso) |
| `search_pokemon` | Listado paginado de Pokémon (`limit`, `offset`) |
| `get_type_effectiveness` | Tabla de efectividades de un tipo atacante |
| `analyze_pokemon_stats` | Análisis de stats base con rating automático (Legendary / Strong / Average / Below Average) |
| `get_pokedex_entry` | Entrada completa de la Pokédex: flavor text en español, generación, hábitat, captura, legendario/mítico |
| `analyze_team` | Análisis completo de un equipo de 2-6 Pokémon: coverage de tipos, miembros más rápidos/fuertes/tankys, distribución de roles |

### Prompts

| Prompt | Descripción |
|--------|-------------|
| `educational/pokemon-analysis` | Análisis de un Pokémon adaptado al nivel del usuario (beginner / intermediate / advanced) |
| `educational/team-building` | Guía de construcción de equipo por tema y formato |
| `educational/type-effectiveness` | Aprendizaje interactivo de efectividades de tipos |
| `battle/strategy` | Planificación de estrategia de batalla |
| `battle/matchup-analysis` | Análisis de enfrentamiento entre dos Pokémon |
| `battle/team-preview` | Análisis de equipo completo antes de una batalla |

### Resources

| URI template | Descripción |
|--------------|-------------|
| `pokemon://info/{name_or_id}` | Información detallada como recurso |
| `pokemon://stats/{name_or_id}` | Estadísticas y análisis como recurso |
| `pokemon://moveset/{name_or_id}` | Moveset completo y métodos de aprendizaje |
| `pokemon://type/{type_name}` | Efectividades de tipo como recurso |
| `pokemon://generation/{gen_number}` | Lista de todos los Pokémon de una generación específica |
| `pokemon://comparison/{pokemon1_name}/{pokemon2_name}` | Comparativa detallada entre dos Pokémon |

---

## 📚 Ejemplos de Uso

Para ejemplos prácticos y detallados sobre cómo usar cada herramienta, prompt y resource, consulta:

👉 **[EJEMPLOS_MCP_POKEMON.md](EJEMPLOS_MCP_POKEMON.md)** — Guía completa con casos de uso reales, combinaciones avanzadas y best practices.

---

## Conectar al servidor público

El servidor acepta conexiones MCP vía HTTP en `https://mcpokedex.com/mcp`.

**Desde Python (Strands Agents SDK):**

```python
from strands import Agent
from strands.tools.mcp import MCPClient
from mcp import ClientSession, StdioServerParameters
from mcp.client.streamable_http import streamablehttp_client

MCP_SERVER_URL = "https://mcpokedex.com/mcp"

async with streamablehttp_client(MCP_SERVER_URL) as (read, write, _):
    async with ClientSession(read, write) as session:
        await session.initialize()
        tools = await session.list_tools()
```


**Desde Claude**

```
claude mcp add --transport http MCPokedex https://mcp.mcpokedex.com/mcp
```

**Desde Claude Desktop (`claude_desktop_config.json`):**

```json
{
  "mcpServers": {
    "MCPokedex": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://mcp.mcpokedex.com/mcp"]
    }
  }
}
```

```json
**Desde VS Code

		"MCPokedex": {
			"url": "https://mcp.mcpokedex.com/mcp",
			"type": "http"
		}
```

---

## Ejecutar localmente

### Con Docker (recomendado)

```bash
git clone https://github.com/ShimaCoding/mcp-pokemon-server
cd mcp-pokemon-server

# Opción 1: Con Make (Linux/Mac)
make dev

# Opción 2: Con docker-compose (Windows/Mac/Linux)
docker-compose up --build
```

El servidor quedará disponible en `http://localhost:8001/mcp` (desarrollo) o `http://localhost:8000/mcp` (producción).

### Sin Docker

```bash
pip install -e ".[dev]"
make run-local         # Stdio transport
make run-uvicorn       # HTTP transport en http://localhost:8000
```

---

## Comandos Útiles (Makefile)

| Comando | Descripción |
|---------|-------------|
| `make dev` | Build y ejecuta desarrollo con live reload |
| `make prod` | Build y ejecuta producción con Redis |
| `make run-dev` | Ejecuta contenedor de desarrollo |
| `make run-local` | Ejecuta servidor localmente (stdio) |
| `make run-uvicorn` | Ejecuta con uvicorn en http://localhost:8000 |
| `make test` | Ejecuta tests en Docker |
| `make test-local` | Ejecuta tests localmente |
| `make logs-dev` | Muestra logs del desarrollo en vivo |
| `make health` | Verifica salud del servidor |
| `make status` | Muestra estado de contenedores |
| `make stop` | Detiene todos los contenedores |
| `make clean` | Limpia recursos Docker |
| `make install-dev` | Instala dependencias localmente |
| `make restart` | Reinicia contenedor de desarrollo |
| `make help` | Lista todos los comandos disponibles |

---

## Arquitectura

```
src/
├── main.py                    # Punto de entrada
├── server/mcp_server.py       # FastMCP app — tools, prompts y resources registrados
├── clients/pokeapi_client.py  # Cliente async para PokéAPI con retry y caché
├── tools/pokemon_tools.py     # Implementación de las 5 herramientas
├── prompts/
│   ├── educational_prompts.py # 3 prompts educativos dinámicos
│   └── battle_prompts.py      # 3 prompts de batalla
├── resources/pokemon_resources.py  # 4 resource templates
├── models/                    # Modelos Pydantic
└── config/                    # Settings y logging estructurado
```

**Stack:** Python 3.12 · FastMCP · httpx (async) · Pydantic · structlog · Docker multi-stage

---

## Proyecto relacionado

Este servidor es la fuente de datos del **Pokémon MCP Agent** — un sandbox educativo para entender flujos agénticos de principio a fin:

[ShimaCoding/pokemon-agent](https://github.com/ShimaCoding/pokemon-agent)
