#!/usr/bin/env python3
"""Simple integration test for Pokemon API client."""

import asyncio
import sys
import httpx


async def test_pokeapi_direct():
    """Test direct connection to PokéAPI."""
    print("🧪 Testing direct connection to PokéAPI...")
    
    async with httpx.AsyncClient() as client:
        try:
            # Test basic Pokemon fetch
            response = await client.get("https://pokeapi.co/api/v2/pokemon/pikachu")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Successfully fetched {data['name']} (#{data['id']})")
                print(f"   Height: {data['height']/10}m, Weight: {data['weight']/10}kg")
                print(f"   Types: {[t['type']['name'] for t in data['types']]}")
                return True
            else:
                print(f"❌ API returned status {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error connecting to PokéAPI: {e}")
            return False


async def test_search():
    """Test Pokemon search."""
    print("\n🔍 Testing Pokemon search...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("https://pokeapi.co/api/v2/pokemon?limit=5")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Found {data['count']} total Pokemon")
                print("   First 5:")
                for pokemon in data['results']:
                    pokemon_id = pokemon['url'].strip('/').split('/')[-1]
                    print(f"   - #{pokemon_id}: {pokemon['name'].title()}")
                return True
            else:
                print(f"❌ Search failed with status {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error during search: {e}")
            return False


async def main():
    """Run integration tests."""
    print("🚀 MCP Pokemon Server - Integration Tests")
    print("=" * 50)
    
    success = True
    success &= await test_pokeapi_direct()
    success &= await test_search()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ All integration tests passed! PokéAPI is accessible.")
        print("🚀 Ready to test the full MCP server implementation.")
    else:
        print("❌ Some tests failed. Check internet connection and PokéAPI status.")
    
    return success


if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
