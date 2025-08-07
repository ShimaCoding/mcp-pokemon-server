"""Pydantic models for Pokemon data."""

from typing import Any

from pydantic import BaseModel, Field, HttpUrl


class PokemonType(BaseModel):
    """Pokemon type information."""

    slot: int
    type: dict[str, str]  # name and url


class PokemonStat(BaseModel):
    """Pokemon stat information."""

    base_stat: int
    effort: int
    stat: dict[str, str]  # name and url


class PokemonAbility(BaseModel):
    """Pokemon ability information."""

    ability: dict[str, str]  # name and url
    is_hidden: bool
    slot: int


class PokemonSprites(BaseModel):
    """Pokemon sprite URLs."""

    front_default: HttpUrl | None = None
    front_shiny: HttpUrl | None = None
    back_default: HttpUrl | None = None
    back_shiny: HttpUrl | None = None


class PokemonMove(BaseModel):
    """Pokemon move information."""

    move: dict[str, str]  # name and url
    version_group_details: list[dict[str, Any]]


class Pokemon(BaseModel):
    """Complete Pokemon model."""

    id: int
    name: str
    height: int  # in decimeters
    weight: int  # in hectograms
    base_experience: int | None = None
    types: list[PokemonType]
    stats: list[PokemonStat]
    abilities: list[PokemonAbility]
    sprites: PokemonSprites
    moves: list[PokemonMove] | None = None

    @property
    def height_meters(self) -> float:
        """Height in meters."""
        return self.height / 10

    @property
    def weight_kg(self) -> float:
        """Weight in kilograms."""
        return self.weight / 10

    @property
    def type_names(self) -> list[str]:
        """List of type names."""
        return [t.type["name"] for t in self.types]

    @property
    def stat_dict(self) -> dict[str, int]:
        """Stats as a dictionary."""
        return {stat.stat["name"]: stat.base_stat for stat in self.stats}


class PokemonSpecies(BaseModel):
    """Pokemon species information."""

    id: int
    name: str
    color: dict[str, str]
    generation: dict[str, str]
    habitat: dict[str, str] | None = None
    is_legendary: bool
    is_mythical: bool
    flavor_text_entries: list[dict[str, Any]] | None = None


class TypeEffectiveness(BaseModel):
    """Type effectiveness data."""

    attacking_type: str
    defending_type: str
    effectiveness: float  # 0.0, 0.5, 1.0, 2.0


class PokemonSearchResult(BaseModel):
    """Search result for Pokemon."""

    count: int
    results: list[dict[str, Any]]  # name and url


class PokemonTeam(BaseModel):
    """A team of Pokemon."""

    name: str
    pokemon: list[Pokemon] = Field(max_length=6)
    description: str | None = None

    @property
    def team_size(self) -> int:
        """Number of Pokemon in team."""
        return len(self.pokemon)

    @property
    def average_level(self) -> float:
        """Average level of team (placeholder, levels not in base data)."""
        return 50.0  # Default level for now
