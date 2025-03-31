"""TMDB data models for request/response validation."""
from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

class Genre(BaseModel):
    """Genre model from TMDB."""
    id: int
    name: str

class TVShow(BaseModel):
    """TV show model from TMDB search results."""
    id: int
    name: str
    original_name: str
    overview: Optional[str] = None
    first_air_date: Optional[date] = None
    genre_ids: List[int] = Field(default_factory=list)
    popularity: float
    vote_average: float = 0.0
    vote_count: int = 0
    
    @field_validator('first_air_date', mode='before')
    @classmethod
    def validate_date(cls, v: Optional[str]) -> Optional[date]:
        """Convert empty string to None for dates."""
        if not v:
            return None
        return v  # Pydantic will convert valid date string to date object
        
    def model_dump_json(self) -> str:
        """Convert model to JSON string."""
        return self.model_dump_json()
        
    def dict(self) -> dict:
        """Convert model to dict for JSON serialization."""
        return self.model_dump()

class Network(BaseModel):
    """Network model from TMDB."""
    id: int
    name: str

class TVShowDetails(TVShow):
    """Detailed TV show model from TMDB."""
    genres: List[Genre] = Field(default_factory=list)
    networks: List[Network] = Field(default_factory=list)
    status: str
    type: str
    number_of_seasons: int
    number_of_episodes: int
    in_production: bool
    languages: List[str] = Field(default_factory=list)
    last_air_date: Optional[date] = None
    
    @field_validator('last_air_date', mode='before')
    @classmethod
    def validate_last_air_date(cls, v: Optional[str]) -> Optional[date]:
        """Convert empty string to None for dates."""
        if not v:
            return None
        return v
    
    def get_genre_names(self) -> List[str]:
        """Get list of genre names."""
        return [genre.name for genre in self.genres]
