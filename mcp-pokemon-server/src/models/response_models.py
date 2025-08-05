"""Response models for MCP tools."""

from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from enum import Enum

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
    data: Optional[Dict[str, Any]] = None
    error_code: Optional[str] = None
    
    
class PokemonInfoResponse(MCPResponse):
    """Response for Pokemon information."""
    pokemon: Optional[Pokemon] = None
    
    
class PokemonSearchResponse(MCPResponse):
    """Response for Pokemon search."""
    results: List[Dict[str, str]] = Field(default_factory=list)
    total_count: int = 0
    
    
class TypeEffectivenessResponse(MCPResponse):
    """Response for type effectiveness analysis."""
    attacking_type: str
    defending_types: Dict[str, float] = Field(default_factory=dict)
    
    
class StatsAnalysisResponse(MCPResponse):
    """Response for Pokemon stats analysis."""
    pokemon_name: str
    total_stats: int
    stat_breakdown: Dict[str, int] = Field(default_factory=dict)
    percentile_rank: Optional[float] = None
    rating: Optional[str] = None
    
    
class TeamBuilderResponse(MCPResponse):
    """Response for team building tools."""
    team: Optional[PokemonTeam] = None
    suggestions: List[str] = Field(default_factory=list)
    type_coverage: Dict[str, int] = Field(default_factory=dict)
    
    
class ErrorResponse(MCPResponse):
    """Error response model."""
    status: ResponseStatus = ResponseStatus.ERROR
    exception_type: Optional[str] = None
    traceback: Optional[str] = None
    
    
class ToolResult(BaseModel):
    """Result from an MCP tool execution."""
    content: List[Dict[str, Any]]
    is_error: bool = False
    
    
class ResourceContent(BaseModel):
    """Content of an MCP resource."""
    uri: str
    mime_type: str = "text/plain"
    text: Optional[str] = None
    blob: Optional[bytes] = None
    
    
class PromptMessage(BaseModel):
    """Message in an MCP prompt."""
    role: str  # "user", "assistant", "system"
    content: Union[str, List[Dict[str, Any]]]
    
    
class PromptResult(BaseModel):
    """Result of an MCP prompt."""
    description: str
    messages: List[PromptMessage]
