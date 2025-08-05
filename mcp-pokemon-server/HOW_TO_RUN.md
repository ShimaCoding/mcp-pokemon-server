# 🚀 Cómo Levantar el Servidor MCP Pokemon

## 🎯 Formas de Ejecutar el Servidor

### ✅ Opción 1: Comando Directo (Más Simple)

```bash
cd /Users/francobeltran/Code/Projects/mcp-test/mcp-pokemon-server
PYTHONPATH=/Users/francobeltran/Code/Projects/mcp-test/mcp-pokemon-server /Users/francobeltran/Code/Projects/mcp-test/.venv/bin/python -m src.main
```

### ✅ Opción 2: Script de Shell

```bash
cd /Users/francobeltran/Code/Projects/mcp-test/mcp-pokemon-server
./start_server.sh
```

### ✅ Opción 3: Runner de Python

```bash
cd /Users/francobeltran/Code/Projects/mcp-test/mcp-pokemon-server
python run_server.py
```

### ✅ Opción 4: Usando el Entorno Virtual

```bash
# Activar entorno virtual
source /Users/francobeltran/Code/Projects/mcp-test/.venv/bin/activate

# Navegar al directorio
cd /Users/francobeltran/Code/Projects/mcp-test/mcp-pokemon-server

# Configurar Python path
export PYTHONPATH=/Users/francobeltran/Code/Projects/mcp-test/mcp-pokemon-server

# Ejecutar
python -m src.main
```

## 🔧 Variables de Entorno Necesarias

```bash
PYTHONPATH=/Users/francobeltran/Code/Projects/mcp-test/mcp-pokemon-server
```

## 📋 Estados del Servidor

### ✅ Servidor Funcionando
Cuando el servidor esté funcionando correctamente, verás:
- Sin errores en la consola
- El proceso se mantiene activo
- Listo para recibir conexiones MCP

### ❌ Posibles Errores

#### Error de Módulo no Encontrado:
```
ModuleNotFoundError: No module named 'src'
```
**Solución**: Asegúrate de estar en el directorio correcto y tener PYTHONPATH configurado.

#### Error de Import Relativo:
```
ImportError: attempted relative import beyond top-level package
```
**Solución**: Usa el comando con PYTHONPATH como se muestra arriba.

## 🎮 Uso con Claude Desktop

Una vez que el servidor esté ejecutándose, Claude Desktop lo utilizará automáticamente si está configurado en:
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

## 🛠️ Para Desarrollo

### Modo Debug:
```bash
cd /Users/francobeltran/Code/Projects/mcp-test/mcp-pokemon-server
PYTHONPATH=/Users/francobeltran/Code/Projects/mcp-test/mcp-pokemon-server /Users/francobeltran/Code/Projects/mcp-test/.venv/bin/python -m src.main --debug
```

### Con Logs Detallados:
```bash
cd /Users/francobeltran/Code/Projects/mcp-test/mcp-pokemon-server
PYTHONPATH=/Users/francobeltran/Code/Projects/mcp-test/mcp-pokemon-server LOG_LEVEL=DEBUG /Users/francobeltran/Code/Projects/mcp-test/.venv/bin/python -m src.main
```

## ⚡ Comando Rápido (Copia y Pega)

Para levantar rápidamente:

```bash
cd /Users/francobeltran/Code/Projects/mcp-test/mcp-pokemon-server && PYTHONPATH=/Users/francobeltran/Code/Projects/mcp-test/mcp-pokemon-server /Users/francobeltran/Code/Projects/mcp-test/.venv/bin/python -m src.main
```

## 🔍 Verificar que Funciona

### Test Rápido:
```bash
# En otra terminal, mientras el servidor está ejecutándose
cd /Users/francobeltran/Code/Projects/mcp-test/mcp-pokemon-server
/Users/francobeltran/Code/Projects/mcp-test/.venv/bin/python test_server.py
```

### En Claude Desktop:
1. Reinicia Claude Desktop
2. Inicia una nueva conversación
3. Pregunta: "¿Puedes darme información sobre Pikachu?"
4. Claude debería usar tu servidor MCP Pokemon

## 🎉 ¡Listo!

Tu servidor MCP Pokemon está funcionando y listo para proporcionar información Pokemon a través de Claude Desktop y VS Code.

**Comando recomendado para uso diario:**
```bash
cd /Users/francobeltran/Code/Projects/mcp-test/mcp-pokemon-server && ./start_server.sh
```
