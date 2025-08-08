"""Response models for MCP tools."""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from .pokemon_models import Pokemon, PokemonTeam


class ResponseStatus(str, Enum):
    """Response status enumeration."""

    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"


class MCPResponse(BaseModel):
    """Base MCP response model."""

    status: ResponseStatus
    message: str
    data: dict[str, Any] | None = None
    error_code: str | None = None


class PokemonInfoResponse(MCPResponse):
    """Response for Pokemon information."""

    pokemon: Pokemon | None = None


class PokemonSearchResponse(MCPResponse):
    """Response for Pokemon search."""

    results: list[dict[str, str]] = Field(default_factory=list)
    total_count: int = 0


class TypeEffectivenessResponse(MCPResponse):
    """Response for type effectiveness analysis."""

    attacking_type: str
    defending_types: dict[str, float] = Field(default_factory=dict)


class StatsAnalysisResponse(MCPResponse):
    """Response for Pokemon stats analysis."""

    pokemon_name: str
    total_stats: int
    stat_breakdown: dict[str, int] = Field(default_factory=dict)
    percentile_rank: float | None = None
    rating: str | None = None


class TeamBuilderResponse(MCPResponse):
    """Response for team building tools."""

    team: PokemonTeam | None = None
    suggestions: list[str] = Field(default_factory=list)
    type_coverage: dict[str, int] = Field(default_factory=dict)


class ErrorResponse(MCPResponse):
    """Error response model."""

    status: ResponseStatus = ResponseStatus.ERROR
    exception_type: str | None = None
    traceback: str | None = None


class ToolResult(BaseModel):
    """Result from an MCP tool execution."""

    content: list[dict[str, Any]]
    is_error: bool = False
    elicit: dict[str, Any] | None = None  # For interactive elicitation


class ResourceContent(BaseModel):
    """Content of an MCP resource."""

    uri: str
    mime_type: str = "text/plain"
    text: str | None = None
    blob: bytes | None = None


class PromptMessage(BaseModel):
    """Message in an MCP prompt."""

    role: str  # "user", "assistant", "system"
    content: str | list[dict[str, Any]]


class PromptResult(BaseModel):
    """Result of an MCP prompt."""

    description: str
    messages: list[PromptMessage]
