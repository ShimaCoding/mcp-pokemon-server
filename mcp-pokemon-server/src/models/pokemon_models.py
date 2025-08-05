"""Pydantic models for Pokemon data."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, HttpUrl


class PokemonType(BaseModel):
    """Pokemon type information."""
    slot: int
    type: Dict[str, str]  # name and url


class PokemonStat(BaseModel):
    """Pokemon stat information."""
    base_stat: int
    effort: int
    stat: Dict[str, str]  # name and url


class PokemonAbility(BaseModel):
    """Pokemon ability information."""
    ability: Dict[str, str]  # name and url
    is_hidden: bool
    slot: int


class PokemonSprites(BaseModel):
    """Pokemon sprite URLs."""
    front_default: Optional[HttpUrl] = None
    front_shiny: Optional[HttpUrl] = None
    back_default: Optional[HttpUrl] = None
    back_shiny: Optional[HttpUrl] = None


class Pokemon(BaseModel):
    """Complete Pokemon model."""
    id: int
    name: str
    height: int  # in decimeters
    weight: int  # in hectograms
    base_experience: Optional[int] = None
    types: List[PokemonType]
    stats: List[PokemonStat]
    abilities: List[PokemonAbility]
    sprites: PokemonSprites
    
    @property
    def height_meters(self) -> float:
        """Height in meters."""
        return self.height / 10
    
    @property
    def weight_kg(self) -> float:
        """Weight in kilograms."""
        return self.weight / 10
    
    @property
    def type_names(self) -> List[str]:
        """List of type names."""
        return [t.type["name"] for t in self.types]
    
    @property
    def stat_dict(self) -> Dict[str, int]:
        """Stats as a dictionary."""
        return {stat.stat["name"]: stat.base_stat for stat in self.stats}


class PokemonSpecies(BaseModel):
    """Pokemon species information."""
    id: int
    name: str
    color: Dict[str, str]
    generation: Dict[str, str]
    habitat: Optional[Dict[str, str]] = None
    is_legendary: bool
    is_mythical: bool


class TypeEffectiveness(BaseModel):
    """Type effectiveness data."""
    attacking_type: str
    defending_type: str
    effectiveness: float  # 0.0, 0.5, 1.0, 2.0


class PokemonSearchResult(BaseModel):
    """Search result for Pokemon."""
    count: int
    results: List[Dict[str, Any]]  # name and url
    
    
class PokemonTeam(BaseModel):
    """A team of Pokemon."""
    name: str
    pokemon: List[Pokemon] = Field(max_items=6)
    description: Optional[str] = None
    
    @property
    def team_size(self) -> int:
        """Number of Pokemon in team."""
        return len(self.pokemon)
    
    @property
    def average_level(self) -> float:
        """Average level of team (placeholder, levels not in base data)."""
        return 50.0  # Default level for now
