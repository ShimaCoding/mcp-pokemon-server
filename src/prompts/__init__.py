"""Pokemon MCP Server - Prompts package.

This package contains educational and battle-focused prompts for Pokemon learning and strategy.
"""

from .battle_prompts import BattlePromptManager
from .educational_prompts import EducationalPromptManager

__all__ = [
    "EducationalPromptManager",
    "BattlePromptManager",
]
