# Guía de Conexión al MCP Pokemon Server

Esta guía explica cómo conectarse al MCP Pokemon Server tanto local como en Docker.

## 🐳 Conectando al Servidor en Docker

### 1. Iniciar el Servidor

#### Desarrollo (con hot-reload):
```bash
# Usando el script utilitario
./docker/docker-utils.sh run-dev

# O manualmente
docker-compose -f docker-compose.dev.yml up -d
```

#### Producción:
```bash
# Usando el script utilitario
./docker/docker-utils.sh run-prod

# O manualmente
docker-compose up -d
```

### 2. Verificar que el Servidor está Ejecutándose

```bash
# Verificar estado del contenedor
docker-compose ps

# Ver logs
docker-compose logs -f mcp-pokemon-server-dev  # para desarrollo
docker-compose logs -f mcp-pokemon-server      # para producción

# Verificar la conexión HTTP
curl -X GET http://localhost:8000/mcp \
  -H "Accept: text/event-stream, application/json" \
  -H "Content-Type: application/json"
```

### 3. Configuración del Cliente

Para conectar un cliente MCP al servidor Docker, usa esta configuración:

#### Para Claude Desktop:
Edita `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "pokemon-server": {
      "transport": "streamable-http",
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

#### Para otros clientes MCP:
Usa el archivo de configuración incluido: `config/mcp_client_config_docker.json`

### 4. Endpoints Disponibles

El servidor expone los siguientes endpoints:

- **Base URL**: `http://localhost:8000`
- **MCP Endpoint**: `http://localhost:8000/mcp`
- **SSE Stream**: `GET http://localhost:8000/mcp` (con headers correctos)
- **JSON-RPC**: `POST http://localhost:8000/mcp`

## 🖥️ Conectando al Servidor Local (stdio)

### 1. Preparar el Entorno

```bash
# Activar el entorno virtual
source venv/bin/activate

# Instalar dependencias
pip install -e .
```

### 2. Ejecutar el Servidor

```bash
# Con transporte stdio (para clientes locales)
MCP_TRANSPORT=stdio python -m src.main

# Con transporte HTTP (para testing local)
MCP_TRANSPORT=streamable-http python -m src.main
```

### 3. Configuración del Cliente Local

#### Para Claude Desktop (Configuración que funciona actualmente):
Edita `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "pokemon-server": {
      "command": "/Users/francobeltran/Code/Projects/mcp-test/venv/bin/python",
      "args": ["-m", "src.main"],
      "cwd": "/Users/francobeltran/Code/Projects/mcp-test"
    }
  }
}
```

**Notas importantes:**
- Usar `claude_desktop_config.json` (no `config.json`)
- El `transport` se omite porque Claude Desktop usa `stdio` por defecto
- La ruta debe apuntar al Python del entorno virtual (`venv/bin/python`)
- El `cwd` debe ser el directorio raíz del proyecto

#### Para otros clientes MCP con stdio transport:

```json
{
  "servers": {
    "pokemon-server": {
      "transport": "stdio",
      "command": "/Users/francobeltran/Code/Projects/mcp-test/venv/bin/python",
      "args": ["-m", "src.main"],
      "cwd": "/Users/francobeltran/Code/Projects/mcp-test",
      "env": {
        "PYTHONPATH": "/Users/francobeltran/Code/Projects/mcp-test",
        "MCP_TRANSPORT": "stdio"
      }
    }
  }
}
```

## 🔧 Variables de Entorno

| Variable | Valores | Descripción |
|----------|---------|-------------|
| `MCP_TRANSPORT` | `stdio`, `streamable-http`, `sse` | Tipo de transporte |
| `MCP_SERVER_HOST` | `0.0.0.0`, `localhost` | Host del servidor HTTP |
| `MCP_SERVER_PORT` | `8000` (default) | Puerto del servidor HTTP |
| `LOG_LEVEL` | `DEBUG`, `INFO`, `WARNING`, `ERROR` | Nivel de logging |
| `POKEAPI_BASE_URL` | URL | Base URL de la PokéAPI |

## 🧪 Testing de la Conexión

### Usando curl para HTTP:

```bash
# Test de conexión básica
curl -X GET http://localhost:8000/mcp \
  -H "Accept: text/event-stream, application/json" \
  -H "Content-Type: application/json"

# Test de envío de mensaje JSON-RPC
curl -X POST http://localhost:8000/mcp \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {},
      "clientInfo": {
        "name": "test-client",
        "version": "1.0.0"
      }
    }
  }'
```

### Usando un cliente Python MCP:

```python
import asyncio
from mcp.client.streamable_http import streamablehttp_client
from mcp.client.session import ClientSession

async def test_connection():
    async with streamablehttp_client("http://localhost:8000/mcp") as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:
            # Inicializar la sesión
            result = await session.initialize()
            print(f"Server: {result.serverInfo.name} v{result.serverInfo.version}")

            # Listar herramientas disponibles
            tools = await session.list_tools()
            print(f"Available tools: {[tool.name for tool in tools.tools]}")

            # Ejemplo de uso de una herramienta
            pokemon_info = await session.call_tool("get_pokemon_info", {"name_or_id": "pikachu"})
            print(f"Pikachu info: {pokemon_info.content[0].text}")

# Ejecutar el test
asyncio.run(test_connection())
```

## 🚨 Troubleshooting

### Problemas Comunes:

1. **Contenedor en loop de reinicio**:
   - Verificar que `MCP_TRANSPORT=streamable-http` esté configurado
   - Revisar logs: `docker-compose logs mcp-pokemon-server-dev`

2. **Error de conexión HTTP**:
   - Verificar que el puerto 8000 esté libre
   - Confirmar que el contenedor está ejecutándose: `docker-compose ps`

3. **Error en cliente stdio**:
   - Verificar que el entorno virtual esté activado
   - Confirmar que las rutas en la configuración sean correctas
   - **Para Claude Desktop**: Verificar que el archivo sea `claude_desktop_config.json` (no `config.json`)
   - **Para Claude Desktop**: Reiniciar Claude Desktop completamente después de cambios en la configuración

4. **Problemas específicos de Claude Desktop**:
   - Verificar que la ruta al Python del venv sea correcta: `/Users/francobeltran/Code/Projects/mcp-test/venv/bin/python`
   - El `cwd` debe apuntar al directorio raíz del proyecto, no al subdirectorio `mcp-pokemon-server`
   - No incluir `transport` en la configuración (Claude Desktop usa `stdio` por defecto)
   - Verificar logs de Claude Desktop en la consola del desarrollador

5. **Error de permisos**:
   - Verificar que Docker tenga permisos para acceder a los directorios montados
   - En sistemas Unix: `chmod +x docker/docker-utils.sh`

### Debug Mode:

```bash
# Ejecutar en modo debug
MCP_TRANSPORT=streamable-http LOG_LEVEL=DEBUG python -m src.main

# O en Docker
docker-compose -f docker-compose.dev.yml up
```

## 📚 Recursos Adicionales

- [MCP Protocol Specification](https://spec.modelcontextprotocol.io/)
- [FastMCP Documentation](https://github.com/modelcontextprotocol/python-sdk)
- [PokéAPI Documentation](https://pokeapi.co/docs/v2)

## 🔄 Gestión del Servidor

### Comandos Útiles:

```bash
# Ver estado
./docker/docker-utils.sh status

# Ver logs en tiempo real
./docker/docker-utils.sh logs-dev

# Entrar al contenedor
./docker/docker-utils.sh shell-dev

# Ejecutar tests
./docker/docker-utils.sh test

# Limpiar recursos
./docker/docker-utils.sh cleanup
```
