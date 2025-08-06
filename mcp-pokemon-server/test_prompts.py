#!/usr/bin/env python3
"""Manual test for Pokemon MCP Server prompts."""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.server.mcp_server import educational_prompts, battle_prompts


async def test_educational_prompts():
    """Test educational prompts functionality."""
    print("🧪 Testing Educational Prompts...")
    
    # Test Pokemon analysis prompt
    print("\n1. Testing Pokemon Analysis Prompt:")
    result = await educational_prompts.create_pokemon_analysis_prompt(
        pokemon_name="pikachu",
        analysis_type="general",
        user_level="beginner"
    )
    print(f"   Description: {result.description}")
    print(f"   Messages: {len(result.messages)} message(s)")
    
    # Test team building prompt
    print("\n2. Testing Team Building Prompt:")
    result = await educational_prompts.create_team_building_prompt(
        theme="balanced",
        format="casual"
    )
    print(f"   Description: {result.description}")
    print(f"   Messages: {len(result.messages)} message(s)")
    
    # Test type effectiveness prompt
    print("\n3. Testing Type Effectiveness Prompt:")
    result = await educational_prompts.create_type_effectiveness_prompt(
        scenario="learning",
        attacking_type="electric"
    )
    print(f"   Description: {result.description}")
    print(f"   Messages: {len(result.messages)} message(s)")


async def test_battle_prompts():
    """Test battle prompts functionality."""
    print("\n🧪 Testing Battle Prompts...")
    
    # Test battle strategy prompt
    print("\n1. Testing Battle Strategy Prompt:")
    result = await battle_prompts.create_battle_strategy_prompt(
        user_team=["pikachu", "charizard", "blastoise"],
        battle_format="singles",
        strategy_focus="balanced"
    )
    print(f"   Description: {result.description}")
    print(f"   Messages: {len(result.messages)} message(s)")
    
    # Test matchup analysis prompt
    print("\n2. Testing Matchup Analysis Prompt:")
    result = await battle_prompts.create_matchup_analysis_prompt(
        pokemon1="pikachu",
        pokemon2="charizard",
        scenario="1v1"
    )
    print(f"   Description: {result.description}")
    print(f"   Messages: {len(result.messages)} message(s)")
    
    # Test team preview prompt
    print("\n3. Testing Team Preview Prompt:")
    result = await battle_prompts.create_team_preview_prompt(
        team=["pikachu", "charizard", "blastoise"],
        analysis_depth="standard"
    )
    print(f"   Description: {result.description}")
    print(f"   Messages: {len(result.messages)} message(s)")


async def main():
    """Run all tests."""
    print("🚀 Pokemon MCP Server - Prompts Test")
    print("=" * 50)
    
    try:
        await test_educational_prompts()
        await test_battle_prompts()
        
        print("\n✅ All prompt tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
