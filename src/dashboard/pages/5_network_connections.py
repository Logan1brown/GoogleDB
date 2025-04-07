"""
Network Connections Page

Analyzes and visualizes network connection patterns.
"""

import streamlit as st
from src.data_processing.analyze_shows import shows_analyzer
from src.dashboard.components.connections_view import render_network_connections_dashboard
from src.data_processing.creative_networks.connections_analyzer import analyze_network_connections
from src.dashboard.state.session import get_page_state, FilterState

# Page title
st.markdown('<p class="section-header">Network Connections Analysis</p>', unsafe_allow_html=True)

try:
    # Get page state
    state = get_page_state("network_connections")
    
    # Initialize data
    shows_df, team_df = shows_analyzer.fetch_data()
    
    # Initialize analyzer and render view
    connections_analyzer = analyze_network_connections(shows_df, team_df)
    render_network_connections_dashboard(connections_analyzer)
    
except Exception as e:
    st.error(f"Error analyzing network connections: {str(e)}")
    st.info("Please ensure Google Sheets credentials are properly configured.")
