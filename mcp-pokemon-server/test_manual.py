#!/usr/bin/env python3
"""Simple test script to verify the MCP server functionality."""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.clients.pokeapi_client import PokemonAPIClient
from src.tools.pokemon_tools import get_pokemon_info, search_pokemon


async def test_basic_functionality():
    """Test basic functionality of the Pokemon MCP server."""
    print("🧪 Testing MCP Pokemon Server functionality...\n")
    
    # Test 1: API Client
    print("1️⃣ Testing PokéAPI Client...")
    try:
        async with PokemonAPIClient() as client:
            pikachu = await client.get_pokemon("pikachu")
            print(f"✅ Successfully fetched {pikachu.name} (#{pikachu.id})")
            print(f"   Types: {', '.join(pikachu.type_names)}")
            print(f"   Total Stats: {sum(pikachu.stat_dict.values())}")
    except Exception as e:
        print(f"❌ API Client test failed: {e}")
        return False
    
    print()
    
    # Test 2: Pokemon Info Tool
    print("2️⃣ Testing get_pokemon_info tool...")
    try:
        result = await get_pokemon_info("charizard")
        if not result.is_error:
            print("✅ get_pokemon_info tool working")
            print(f"   Response length: {len(result.content[0]['text'])} characters")
        else:
            print(f"❌ Tool returned error: {result.content[0]['text']}")
            return False
    except Exception as e:
        print(f"❌ Tool test failed: {e}")
        return False
    
    print()
    
    # Test 3: Search Tool
    print("3️⃣ Testing search_pokemon tool...")
    try:
        result = await search_pokemon(limit=5)
        if not result.is_error:
            print("✅ search_pokemon tool working")
            print(f"   Response contains search results")
        else:
            print(f"❌ Search tool returned error: {result.content[0]['text']}")
            return False
    except Exception as e:
        print(f"❌ Search tool test failed: {e}")
        return False
    
    print()
    print("🎉 All basic functionality tests passed!")
    return True


async def test_error_handling():
    """Test error handling."""
    print("\n🛡️ Testing error handling...\n")
    
    # Test with non-existent Pokemon
    print("1️⃣ Testing with non-existent Pokemon...")
    try:
        result = await get_pokemon_info("definitely-not-a-pokemon-12345")
        if result.is_error and "not found" in result.content[0]["text"].lower():
            print("✅ Error handling working correctly")
        else:
            print("❌ Error handling not working as expected")
            return False
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False
    
    print("\n🎉 Error handling tests passed!")
    return True


async def main():
    """Run all tests."""
    print("🚀 Starting MCP Pokemon Server Tests\n" + "="*50)
    
    success = True
    
    # Run basic functionality tests
    success &= await test_basic_functionality()
    
    # Run error handling tests
    success &= await test_error_handling()
    
    print("\n" + "="*50)
    if success:
        print("✅ ALL TESTS PASSED! The MCP server is ready for Phase 3.")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Please check the implementation.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
