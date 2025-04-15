"""
Studio Performance Page

Analyzes and visualizes studio performance metrics.
"""

import os
import streamlit as st
import pandas as pd
from supabase import create_client
from src.dashboard.utils.style_config import COLORS, FONTS
from src.data_processing.market_analysis.market_analyzer_secure import MarketAnalyzer
from src.dashboard.components.studio_view import render_studio_performance_dashboard
from src.dashboard.state.session import get_page_state, FilterState

# Page title using style from style_config
st.markdown(f'<p style="font-family: {FONTS["primary"]["family"]}; font-size: {FONTS["primary"]["sizes"]["header"]}px; text-transform: uppercase; font-weight: 600; letter-spacing: 0.1em; color: {COLORS["accent"]}; margin-bottom: 1em;">Studio Performance</p>', unsafe_allow_html=True)

try:
    # Get page state
    state = get_page_state("studio_performance")
    
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
        
        # Render view with state
        render_studio_performance_dashboard(market_analyzer.shows_df)
    
except Exception as e:
    st.error(f"Error analyzing studio performance: {str(e)}")
    st.info("Please ensure Supabase configuration is properly set up.")
