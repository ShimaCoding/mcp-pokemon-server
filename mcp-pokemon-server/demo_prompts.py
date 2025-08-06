#!/usr/bin/env python3
"""Interactive test script for Pokemon MCP Server prompts."""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.server.mcp_server import educational_prompts, battle_prompts


async def demo_educational_prompts():
    """Demonstrate educational prompts with real examples."""
    print("🎓 EDUCATIONAL PROMPTS DEMO")
    print("=" * 50)
    
    # 1. Beginner analysis
    print("\n1. 📚 Beginner Pokemon Analysis (Pikachu)")
    result = await educational_prompts.create_pokemon_analysis_prompt(
        pokemon_name="pikachu",
        analysis_type="general",
        user_level="beginner"
    )
    print(f"Prompt: {result.description}")
    print("Content preview:")
    content = result.messages[0].content.text
    print(content[:200] + "..." if len(content) > 200 else content)
    
    # 2. Team building
    print("\n2. 🏗️ Team Building (Offensive Competitive)")
    result = await educational_prompts.create_team_building_prompt(
        theme="offensive",
        format="competitive",
        restrictions=["no-legendaries"]
    )
    print(f"Prompt: {result.description}")
    
    # 3. Type effectiveness quiz
    print("\n3. ❓ Type Effectiveness Quiz (Fire type)")
    result = await educational_prompts.create_type_effectiveness_prompt(
        scenario="quiz",
        attacking_type="fire"
    )
    print(f"Prompt: {result.description}")


async def demo_battle_prompts():
    """Demonstrate battle prompts with real examples."""
    print("\n\n⚔️ BATTLE PROMPTS DEMO")
    print("=" * 50)
    
    # 1. Battle strategy
    print("\n1. 🎯 Battle Strategy (Classic starters)")
    result = await battle_prompts.create_battle_strategy_prompt(
        user_team=["charizard", "blastoise", "venusaur"],
        battle_format="singles",
        strategy_focus="balanced"
    )
    print(f"Prompt: {result.description}")
    
    # 2. Matchup analysis
    print("\n2. ⚡ Matchup Analysis (Pikachu vs Charizard)")
    result = await battle_prompts.create_matchup_analysis_prompt(
        pokemon1="pikachu",
        pokemon2="charizard",
        scenario="1v1",
        environment="neutral"
    )
    print(f"Prompt: {result.description}")
    
    # 3. Team preview
    print("\n3. 👥 Team Preview (Competitive team)")
    result = await battle_prompts.create_team_preview_prompt(
        team=["garchomp", "rotom-wash", "ferrothorn", "latios"],
        analysis_depth="standard"
    )
    print(f"Prompt: {result.description}")


def print_usage_examples():
    """Print Claude Desktop usage examples."""
    print("\n\n🗣️ CLAUDE DESKTOP USAGE EXAMPLES")
    print("=" * 50)
    
    examples = [
        ("Beginner Pokemon Analysis", 
         '@educational/pokemon-analysis pokemon_name="pikachu" user_level="beginner"'),
        
        ("Advanced Competitive Analysis", 
         '@educational/pokemon-analysis pokemon_name="metagross" analysis_type="competitive" user_level="advanced"'),
        
        ("Offensive Team Building", 
         '@educational/team-building theme="offensive" format="competitive" restrictions=["no-legendaries"]'),
        
        ("Type Effectiveness Quiz", 
         '@educational/type-effectiveness scenario="quiz" attacking_type="electric"'),
        
        ("Battle Strategy", 
         '@battle/strategy user_team=["pikachu", "charizard", "blastoise"] battle_format="singles"'),
        
        ("Matchup Analysis", 
         '@battle/matchup-analysis pokemon1="garchomp" pokemon2="dragonite" scenario="1v1"'),
        
        ("Team Preview", 
         '@battle/team-preview team=["alakazam", "machamp", "gengar"] analysis_depth="comprehensive"')
    ]
    
    for i, (title, command) in enumerate(examples, 1):
        print(f"\n{i}. {title}:")
        print(f"   {command}")


async def interactive_prompt_tester():
    """Interactive prompt tester."""
    print("\n\n🧪 INTERACTIVE PROMPT TESTER")
    print("=" * 50)
    print("Choose a prompt to test:")
    print("1. Pokemon Analysis")
    print("2. Team Building") 
    print("3. Type Effectiveness")
    print("4. Battle Strategy")
    print("5. Matchup Analysis")
    print("6. Team Preview")
    print("0. Exit")
    
    try:
        choice = input("\nEnter your choice (0-6): ").strip()
        
        if choice == "0":
            return
        elif choice == "1":
            pokemon = input("Pokemon name: ").strip().lower()
            level = input("User level (beginner/intermediate/advanced): ").strip().lower()
            result = await educational_prompts.create_pokemon_analysis_prompt(
                pokemon_name=pokemon,
                user_level=level if level in ["beginner", "intermediate", "advanced"] else "beginner"
            )
            print(f"\n✅ Generated prompt: {result.description}")
            print(f"Content preview: {result.messages[0].content.text[:300]}...")
            
        elif choice == "2":
            theme = input("Theme (balanced/offensive/defensive): ").strip().lower()
            format_type = input("Format (casual/competitive/tournament): ").strip().lower()
            result = await educational_prompts.create_team_building_prompt(
                theme=theme if theme in ["balanced", "offensive", "defensive"] else "balanced",
                format=format_type if format_type in ["casual", "competitive", "tournament"] else "casual"
            )
            print(f"\n✅ Generated prompt: {result.description}")
            
        elif choice == "4":
            team_input = input("Your team (comma-separated, e.g., pikachu,charizard,blastoise): ").strip()
            team = [p.strip().lower() for p in team_input.split(",") if p.strip()]
            if team:
                result = await battle_prompts.create_battle_strategy_prompt(
                    user_team=team,
                    battle_format="singles",
                    strategy_focus="balanced"
                )
                print(f"\n✅ Generated prompt: {result.description}")
            else:
                print("❌ Please provide at least one Pokemon")
                
        else:
            print("🚧 This option is not implemented in the interactive tester yet.")
            print("Please use the Claude Desktop examples above.")
            
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")


async def main():
    """Main function."""
    print("🚀 POKEMON MCP SERVER - PROMPTS DEMONSTRATION")
    print("=" * 60)
    
    try:
        await demo_educational_prompts()
        await demo_battle_prompts()
        print_usage_examples()
        
        print("\n" + "=" * 60)
        print("✅ All demos completed successfully!")
        print("\nYou can now use these prompts in Claude Desktop using the @ syntax shown above.")
        
        # Optional interactive tester
        test_more = input("\nWould you like to test prompts interactively? (y/n): ").strip().lower()
        if test_more in ["y", "yes"]:
            await interactive_prompt_tester()
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
