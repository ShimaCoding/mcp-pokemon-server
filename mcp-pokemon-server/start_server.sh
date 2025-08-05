#!/bin/bash

# Script para levantar el servidor MCP Pokemon
echo "🎮 Iniciando servidor MCP Pokemon..."

# Navegar al directorio del proyecto
cd /Users/francobeltran/Code/Projects/mcp-test/mcp-pokemon-server

# Configurar variables de entorno
export PYTHONPATH="/Users/francobeltran/Code/Projects/mcp-test/mcp-pokemon-server:$PYTHONPATH"

echo "📁 Directorio: $(pwd)"
echo "🐍 Python Path: $PYTHONPATH"
echo "⚡ Ejecutando servidor..."

# Ejecutar el servidor
/Users/francobeltran/Code/Projects/mcp-test/.venv/bin/python -m src.main

echo "✅ Servidor MCP Pokemon iniciado!"
