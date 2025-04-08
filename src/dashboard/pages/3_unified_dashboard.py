"""
Unified Dashboard Page

Provides a unified view of TV series data across acquisition, packaging, and development.
"""

import streamlit as st
from dataclasses import asdict, dataclass, field
from src.data_processing.analyze_shows import shows_analyzer
from src.data_processing.success_analysis.success_analyzer import SuccessAnalyzer
from src.dashboard.components.unified_view import render_unified_dashboard
from src.dashboard.state.session import get_page_state, FilterState

@dataclass
class UnifiedState:
    """State for unified dashboard page."""
    analysis_type: str = "Acquisition"
    source_type: str = "All"
    genre: str = "All"
    network: str = "All"
    year_range: tuple[int, int] = field(default_factory=lambda: (2020, 2025))
    selected_shows: list[str] = field(default_factory=list)
    selected_networks: list[str] = field(default_factory=list)
    success_filter: str = "All"

# Page title
st.markdown('<p class="section-header">Content Analysis</p>', unsafe_allow_html=True)

try:
    # Get page state
    state = get_page_state("unified_dashboard")
    if "unified" not in state:
        state["unified"] = asdict(UnifiedState())
    
    # Initialize data and analyzers
    shows_df, team_df = shows_analyzer.fetch_data()
    success_analyzer = SuccessAnalyzer()
    success_analyzer.initialize_data(shows_df)
    
    # Update state with filter values
    unified_state = state["unified"]
    if "analysis_type" in st.session_state:
        unified_state["analysis_type"] = st.session_state["analysis_type"]
    if "source_type" in st.session_state:
        unified_state["source_type"] = st.session_state["source_type"]
    if "genre" in st.session_state:
        unified_state["genre"] = st.session_state["genre"]
    if "network" in st.session_state:
        unified_state["network"] = st.session_state["network"]
    if "year_range" in st.session_state:
        unified_state["year_range"] = st.session_state["year_range"]
    
    # Render view with state
    render_unified_dashboard(success_analyzer)
    
except Exception as e:
    st.error(f"Error displaying unified dashboard: {str(e)}")
    st.info("Please ensure Google Sheets credentials are properly configured.")
