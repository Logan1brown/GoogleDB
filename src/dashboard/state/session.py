"""
Session state management for the dashboard.
Provides utilities for managing page-scoped state.
"""

import streamlit as st
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

@dataclass
class FilterState:
    """Common filter state used across pages."""
    source_type: Optional[str] = None
    genre: Optional[str] = None

def get_page_state(page_name: str) -> Dict[str, Any]:
    """Get state for a specific page.
    
    Args:
        page_name: Name of the page to get state for
        
    Returns:
        Dictionary containing the page's state
    """
    key = f"state_{page_name}"
    if key not in st.session_state:
        st.session_state[key] = {}
    return st.session_state[key]

def get_filter_state(page_name: str) -> FilterState:
    """Get filter state for a specific page.
    
    Args:
        page_name: Name of the page to get filter state for
        
    Returns:
        FilterState instance for the page
    """
    state = get_page_state(page_name)
    if "filters" not in state:
        state["filters"] = asdict(FilterState())
    return FilterState(**state["filters"])

def update_filter_state(page_name: str, filters: FilterState) -> None:
    """Update filter state for a specific page.
    
    Args:
        page_name: Name of the page to update filter state for
        filters: New filter state
    """
    state = get_page_state(page_name)
    state["filters"] = asdict(filters)
