"""
Market Snapshot Page

Displays market analysis and insights for TV series data.
"""

import streamlit as st
from dataclasses import asdict, dataclass, field
from src.dashboard.utils.style_config import COLORS, FONTS
from src.data_processing.analyze_shows import shows_analyzer
from src.data_processing.market_analysis.market_analyzer import MarketAnalyzer
from src.dashboard.components.market_view import render_market_snapshot
from src.dashboard.state.session import get_page_state, FilterState

@dataclass
class MarketState:
    """State for market snapshot page."""
    selected_shows: list[str] = field(default_factory=list)
    selected_creatives: list[str] = field(default_factory=list)
    selected_networks: list[str] = field(default_factory=list)
    success_filter: str = "All"

# Page title using style from style_config
st.markdown(f'<p style="font-family: {FONTS["primary"]["family"]}; font-size: {FONTS["primary"]["sizes"]["header"]}px; text-transform: uppercase; font-weight: 600; letter-spacing: 0.1em; color: {COLORS["accent"]}; margin-bottom: 1em;">Market Snapshot</p>', unsafe_allow_html=True)

try:
    # Get page state
    state = get_page_state("market_snapshot")
    if "market" not in state:
        state["market"] = asdict(MarketState())
    
    # Initialize data and analyzer
    shows_df, team_df = shows_analyzer.fetch_data()
    market_analyzer = MarketAnalyzer(shows_df, team_df)
    
    # Update state with filter values
    market_state = state["market"]
    if "market_filter_shows" in st.session_state:
        market_state["selected_shows"] = st.session_state["market_filter_shows"]
    if "market_filter_creatives" in st.session_state:
        market_state["selected_creatives"] = st.session_state["market_filter_creatives"]
    if "market_filter_networks" in st.session_state:
        market_state["selected_networks"] = st.session_state["market_filter_networks"]
    
    # Render view with state
    render_market_snapshot(market_analyzer)
    
except Exception as e:
    st.error(f"Error displaying market snapshot: {str(e)}")
    st.info("Please ensure Google Sheets credentials are properly configured.")
