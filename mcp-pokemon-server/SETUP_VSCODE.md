# 🛠️ Configuración MCP Pokemon Server para VS Code

## 📦 Instalación de Extensiones

### Opción 1: Copilot MCP (Recomendada)
```
Extensión ID: automatalabs.copilot-mcp
```
Esta extensión te permite buscar, gestionar e instalar servidores MCP de código abierto.

### Opción 2: Cline (Claude Dev)
```
Extensión ID: saoudrizwan.claude-dev
```
Agente de codificación autónomo que soporta MCP directamente en VS Code.

### Opción 3: MCP Server Runner
```
Extensión ID: zebradev.mcp-server-runner
```
Para gestionar y ejecutar servidores MCP localmente.

## ⚙️ Configuración para Copilot MCP

### 1. Configuración en settings.json

Abre `Command Palette` (Cmd+Shift+P) → `Preferences: Open User Settings (JSON)`

Agrega esta configuración:

```json
{
  "copilot-mcp.servers": {
    "pokemon-server": {
      "command": "/Users/francobeltran/Code/Projects/mcp-test/.venv/bin/python",
      "args": ["-m", "src.main"],
      "cwd": "/Users/francobeltran/Code/Projects/mcp-test/mcp-pokemon-server",
      "env": {
        "PYTHONPATH": "/Users/francobeltran/Code/Projects/mcp-test/mcp-pokemon-server"
      }
    }
  }
}
```

### 2. Configuración para Cline

Si usas Cline, crea un archivo `.cline_mcp_settings.json` en tu proyecto:

```json
{
  "mcpServers": {
    "pokemon-server": {
      "command": "/Users/francobeltran/Code/Projects/mcp-test/.venv/bin/python",
      "args": ["-m", "src.main"],
      "cwd": "/Users/francobeltran/Code/Projects/mcp-test/mcp-pokemon-server",
      "env": {
        "PYTHONPATH": "/Users/francobeltran/Code/Projects/mcp-test/mcp-pokemon-server"
      }
    }
  }
}
```

## 🚀 Uso en VS Code

### Con Copilot MCP:
1. Instala la extensión
2. Configura en settings.json
3. Reinicia VS Code
4. Usa `@pokemon` en el chat de Copilot

### Con Cline:
1. Instala la extensión Cline
2. Abre el panel de Cline
3. Configura tu API key (Claude/OpenAI)
4. Usa comandos como:
   - "¿Puedes usar el servidor Pokemon para obtener info de Pikachu?"
   - "Busca información de Charizard usando las herramientas MCP"

### Con MCP Server Runner:
1. Instala la extensión
2. Ve a la vista "MCP Servers"
3. Agrega tu servidor Pokemon
4. Ejecuta el servidor desde la interfaz

## 🔍 Testing en VS Code

### Para probar tu servidor:

1. **Abre Command Palette** (Cmd+Shift+P)
2. **Busca**: "MCP: List Servers" o "Copilot MCP: Refresh"
3. **Verifica** que aparezca "pokemon-server"
4. **Usa el chat** con comandos como:
   ```
   @pokemon get info about Pikachu
   @pokemon search for the first 5 Pokemon
   @pokemon analyze Charizard stats
   ```

## 📝 Configuración Alternativa

### Para workspace específico:

Crea `.vscode/settings.json` en tu proyecto:

```json
{
  "copilot-mcp.servers": {
    "pokemon-server": {
      "command": "/Users/francobeltran/Code/Projects/mcp-test/.venv/bin/python",
      "args": ["-m", "src.main"],
      "cwd": "/Users/francobeltran/Code/Projects/mcp-test/mcp-pokemon-server",
      "env": {
        "PYTHONPATH": "/Users/francobeltran/Code/Projects/mcp-test/mcp-pokemon-server"
      }
    }
  },
  "cline.mcpServers": {
    "pokemon-server": {
      "command": "/Users/francobeltran/Code/Projects/mcp-test/.venv/bin/python",
      "args": ["-m", "src.main"],
      "cwd": "/Users/francobeltran/Code/Projects/mcp-test/mcp-pokemon-server"
    }
  }
}
```

## 🛠️ Troubleshooting

### Si no aparece el servidor:
1. Verifica que las rutas sean correctas
2. Asegúrate de que el entorno virtual esté activo
3. Reinicia VS Code completamente
4. Revisa la consola de desarrollador: `Help > Toggle Developer Tools`

### Para depurar:
1. Instala "MCP Inspector" (dhananjaysenday.mcp--inspector)
2. Usa la vista de inspector para probar conexiones
3. Verifica logs en Output Panel

## 🎯 Ejemplos de Uso

Una vez configurado, puedes usar comandos como:

```
# En el chat de Copilot o Cline:
"Usa el servidor Pokemon para obtener información de Mewtwo"
"¿Puedes analizar las estadísticas de Charizard vs Blastoise?"
"Busca los primeros 10 Pokemon y muéstrame sus tipos"
"¿Qué tan efectivo es el tipo eléctrico contra otros tipos?"
```

## ✅ Verificación

El servidor está funcionando si:
- Aparece en la lista de servidores MCP
- Puedes usar comandos @pokemon en el chat
- Las herramientas responden con información de Pokemon
- No hay errores en la consola de desarrollador

¡Tu servidor Pokemon ya está listo para usar en VS Code! 🎮⚡
