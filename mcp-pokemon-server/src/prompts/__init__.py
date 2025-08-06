"""Pokemon MCP Server - Prompts package.

This package contains educational and battle-focused prompts for Pokemon learning and strategy.
"""

from .educational_prompts import EducationalPromptManager
from .battle_prompts import BattlePromptManager

__all__ = [
    "EducationalPromptManager",
    "BattlePromptManager",
]