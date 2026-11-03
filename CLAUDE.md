# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MCP Pokemon Server is a Model Context Protocol (MCP) server built with FastMCP that exposes Pokemon data from PokéAPI as tools, resources, and prompts. It's designed as an educational reference for building production-quality MCP servers in Python.

## Common Commands

### Local Development
```bash
pip install -e ".[dev]"      # Install with dev dependencies
python -m src.main           # Run server directly
pytest                       # Run all tests
pytest --cov=src             # Run with coverage
pytest -m "not slow"         # Skip slow tests
pytest tests/test_tools.py   # Run a single test file
```

### Code Quality
```bash
black .                      # Format code
isort .                      # Sort imports
ruff check .                 # Lint
mypy src/                    # Type check (strict mode)
bandit -r src/               # Security scan
pre-commit run --all-files   # Run all checks
```

### Docker
```bash
make build-dev && make run-dev   # Dev (port 8001)
make build-prod && make run-prod # Prod with Redis (port 8000)
make test                        # Run tests in container
make shell-dev                   # Shell into dev container
make logs-dev                    # Tail dev logs
make health                      # Check server health
make stop && make clean          # Stop and remove everything
```

## Architecture

The server uses **FastMCP** to expose three MCP primitives:

- **Tools** (`src/tools/pokemon_tools.py`): 8 callable tools — `get_pokemon_info`, `search_pokemon`, `get_type_effectiveness`, `analyze_pokemon_stats`, `analyze_team`, `get_pokedex_entry`, `compare_pokemon`, `get_evolution_chain`
- **Resources** (`src/resources/pokemon_resources.py`): Dynamic URI patterns — `pokemon://info/{name}`, `pokemon://stats/{name}`, `pokemon://type/{type}`, `pokemon://comparison/{name1}/{name2}`
- **Prompts** (`src/prompts/`): 6 prompt templates split into educational (`educational_prompts.py`) and battle strategy (`battle_prompts.py`)

All tools and resources call through `PokemonAPIClient` (`src/clients/pokeapi_client.py`), which wraps httpx with tenacity retry logic against `https://pokeapi.co/api/v2`.

**Request flow:** MCP client → FastMCP server (`src/server/mcp_server.py`) → tools/resources/prompts → `PokemonAPIClient` → PokéAPI

**Data models** (`src/models/`): Pydantic v2 models for Pokemon, stats, types, abilities, sprites, moves, and search results. `ToolResult` wraps all MCP tool responses.

**Configuration** (`src/config/settings.py`): Pydantic settings loaded from environment variables. Key vars: `MCP_SERVER_HOST`, `MCP_SERVER_PORT`, `MCP_TRANSPORT` (stdio or streamable-http), `LOG_LEVEL`, `REDIS_PASSWORD`.

## MCP Apps (widgets)

The server uses the SDK's `mcp.server.apps.Apps` extension. Every tool is bound to a widget and returns a `CallToolResult`: text content for the LLM plus `structuredContent` for the widget (built in `pokemon_tools.py`):

| Widget | Tools | Payload |
|---|---|---|
| `ui://pokedex/card.html` | `get_pokemon_info`, `get_pokedex_entry` | `pokemon_card()` (+ species fields) |
| `ui://pokedex/stats.html` | `analyze_pokemon_stats`, `compare_pokemon` | `{"pokemon": [stats_entry()]}` |
| `ui://pokedex/types.html` | `get_type_effectiveness` | `type_chart()`: attack/defense multipliers |
| `ui://pokedex/team.html` | `analyze_team` | members (`stats_entry()` + roles), `team_analysis`, `not_found` |
| `ui://pokedex/search.html` | `search_pokemon` | `count`, `limit`, `offset`, `results` |
| `ui://pokedex/evolution.html` | `get_evolution_chain` | `queried`, `stages`, `root` (tree: name/id/types/total_bst/sprite/is_baby/queried/via[]/evolves_to), `evolutions` |

The search widget is interactive: clicking a Pokémon calls `app.sendMessage` (the host posts it to the chat) and paging calls `app.callServerTool("search_pokemon")`.

- UI-bound tools (`@apps.tool`) must be declared **before** `MCPServer(extensions=[apps])` is constructed; the extension is consumed at construction time.
- Widget sources live in `widgets/` (Vite + TS + `vite-plugin-singlefile`, runtime `@modelcontextprotocol/ext-apps`). `make widgets` builds them into `src/widgets/html/*.html`, which **is committed** so the Python image needs no Node. Rebuild and commit after editing widget sources.
- Widget HTML must stay self-contained: the host iframe CSP only allows `raw.githubusercontent.com` (sprites) as an external origin.

## Transport

The server supports two transports configured via `MCP_TRANSPORT`:
- `stdio` — for direct Claude Desktop integration
- `streamable-http` — for containerized/networked deployment (default in Docker)

## Docker Setup

- **Production**: `docker-compose.yml` — MCP server + Redis, two networks (`mcp-network` public, `mcp-backend` internal), resource limits
- **Development**: `docker-compose.dev.yml` — live code reload via volume mount, port 8001, debug logging

## Testing

Tests live in `tests/` with shared fixtures in `conftest.py` (mock httpx client, mock Redis, sample Pikachu data). Asyncio mode is set to `auto` — no manual event loop management needed in tests.
