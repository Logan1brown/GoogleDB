"""
Studio Performance Page

Analyzes and visualizes studio performance metrics.
"""

import streamlit as st
from src.dashboard.utils.style_config import COLORS, FONTS
from src.data_processing.analyze_shows import shows_analyzer
from src.dashboard.components.studio_view import render_studio_performance_dashboard
from src.dashboard.state.session import get_page_state, FilterState

# Page title using style from style_config
st.markdown(f'<p style="font-family: {FONTS["primary"]["family"]}; font-size: {FONTS["primary"]["sizes"]["header"]}px; text-transform: uppercase; font-weight: 600; letter-spacing: 0.1em; color: {COLORS["accent"]}; margin-bottom: 1em;">Studio Performance</p>', unsafe_allow_html=True)

try:
    # Get page state
    state = get_page_state("studio_performance")
    
    # Initialize data
    shows_df, team_df = shows_analyzer.fetch_data()
    
    # Render view
    render_studio_performance_dashboard(shows_df)
    
except Exception as e:
    st.error(f"Error analyzing studio performance: {str(e)}")
    st.info("Please ensure Google Sheets credentials are properly configured.")
