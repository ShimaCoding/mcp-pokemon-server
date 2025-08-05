#!/usr/bin/env python3
"""Test the MCP server directly."""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.server.mcp_server import app, get_pokemon_info


async def test_server():
    """Test the MCP server tools."""
    print("🧪 Testing MCP Server Tools...")
    
    # Test get_pokemon_info
    print("\n1️⃣ Testing get_pokemon_info...")
    try:
        result = await get_pokemon_info("pikachu")
        print("✅ get_pokemon_info works!")
        print(f"Response length: {len(result)} characters")
        print("Preview:", result[:200] + "..." if len(result) > 200 else result)
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n🎉 Server test complete!")


if __name__ == "__main__":
    asyncio.run(test_server())
