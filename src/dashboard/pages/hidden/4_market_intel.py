"""
Market Intelligence Page (Prototype)

Prototype view for market intelligence analysis.
"""

import streamlit as st
from src.data_processing.analyze_shows import shows_analyzer
from src.dashboard.components.prototype_market_intel_view import render_market_intel
from src.dashboard.state.session import get_page_state, FilterState

# Page title
st.markdown('<p class="section-header">Market Intelligence (Prototype)</p>', unsafe_allow_html=True)

try:
    # Get page state
    state = get_page_state("market_intel")
    
    # Initialize data
    shows_df, team_df = shows_analyzer.fetch_data()
    
    # Render view
    render_market_intel()
    
except Exception as e:
    st.error(f"Error displaying market intel: {str(e)}")
    st.info("Please ensure Google Sheets credentials are properly configured.")
