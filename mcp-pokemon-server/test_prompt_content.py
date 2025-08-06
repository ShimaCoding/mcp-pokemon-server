#!/usr/bin/env python3
"""Detailed test to see the actual content of prompts."""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.server.mcp_server import educational_prompts, battle_prompts


async def test_prompt_content():
    """Test and display actual prompt content."""
    print("🔍 Detailed Prompt Content Test")
    print("=" * 50)
    
    # Test educational analysis prompt
    print("\n📚 Educational Analysis Prompt for Pikachu (Beginner):")
    result = await educational_prompts.create_pokemon_analysis_prompt(
        pokemon_name="pikachu",
        analysis_type="general",
        user_level="beginner"
    )
    
    print(f"Description: {result.description}")
    print(f"Number of messages: {len(result.messages)}")
    print("Content:")
    print("-" * 40)
    for i, message in enumerate(result.messages):
        print(f"Message {i+1} (Role: {message.role}):")
        print(message.content.text[:500] + "..." if len(message.content.text) > 500 else message.content.text)
        print("-" * 40)
    
    # Test battle strategy prompt
    print("\n⚔️ Battle Strategy Prompt:")
    result = await battle_prompts.create_battle_strategy_prompt(
        user_team=["pikachu", "charizard"],
        battle_format="singles",
        strategy_focus="offensive"
    )
    
    print(f"Description: {result.description}")
    print(f"Number of messages: {len(result.messages)}")
    print("Content:")
    print("-" * 40)
    for i, message in enumerate(result.messages):
        print(f"Message {i+1} (Role: {message.role}):")
        print(message.content.text[:500] + "..." if len(message.content.text) > 500 else message.content.text)
        print("-" * 40)


if __name__ == "__main__":
    asyncio.run(test_prompt_content())
