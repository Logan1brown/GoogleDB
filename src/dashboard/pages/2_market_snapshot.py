"""Market Snapshot Page

Displays market analysis and insights for TV series data using secure Supabase views.
"""

import os
import streamlit as st
from dataclasses import asdict, dataclass, field
import pandas as pd
from supabase import create_client

from src.dashboard.utils.style_config import COLORS, FONTS
from src.data_processing.market_analysis.market_analyzer_secure import MarketAnalyzer
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
    
    # Initialize Supabase client
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_anon_key = os.environ.get("SUPABASE_ANON_KEY")
    
    if not supabase_url or not supabase_anon_key:
        st.error("Missing Supabase configuration. Please check your environment variables.")
    else:
        # Initialize Supabase client with anon key
        supabase = create_client(supabase_url, supabase_anon_key)
        
        # Fetch data from secure view
        response = supabase.table('api_market_analysis').select('*').execute()
        market_data = pd.DataFrame(response.data)
        
        # Initialize analyzer with secure data
        market_analyzer = MarketAnalyzer(market_data)
        
        # Update state with filter values
        market_state = state["market"]
        if "market_filter_shows" in st.session_state:
            market_state["selected_shows"] = st.session_state["market_filter_shows"]
        if "market_filter_creatives" in st.session_state:
            market_state["selected_creatives"] = st.session_state["market_filter_creatives"]
        if "market_filter_networks" in st.session_state:
            market_state["selected_networks"] = st.session_state["market_filter_networks"]
        
        # Render view with state and supabase client
        render_market_snapshot(market_analyzer, supabase)
        
except Exception as e:
    st.error(f"Error displaying market snapshot: {str(e)}")
    st.info("Please ensure Supabase configuration is properly set up.")
