"""
Data entry state management.
"""

from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional

@dataclass
class ShowFormState:
    """State for show entry form."""
    title: str = ""
    description: str = ""
    network_id: Optional[int] = None
    genre_id: Optional[int] = None
    subgenres: List[int] = field(default_factory=list)
    source_type_id: Optional[int] = None
    order_type_id: Optional[int] = None
    status_id: Optional[int] = None
    date: date = field(default_factory=date.today)
    episode_count: int = 0
    studios: List[int] = field(default_factory=list)
    new_studios: List[str] = field(default_factory=list)
    active: bool = True
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    team_members: List[dict] = field(default_factory=list)

@dataclass
class DataEntryState:
    """Overall state for data entry pages."""
    show_form: ShowFormState = field(default_factory=ShowFormState)
    active_tab: int = 0
    num_new_studios: int = 0
    num_team_members: int = 0
    lookups: dict = field(default_factory=dict)
