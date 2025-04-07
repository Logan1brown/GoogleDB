"""
TV Series Database Dashboard
Main application file for the Streamlit dashboard.

This dashboard provides:
- Automatic insights about TV series data
- Interactive visualizations
- Trend analysis
"""

import os
import sys

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Add src directory to Python path
src_dir = os.path.join(project_root, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Set up Plotly template for consistent styling
import plotly.io as pio
pio.templates.default = "plotly_white"

# Data processing and analysis
from src.data_processing.analyze_shows import shows_analyzer
from src.data_processing.content_strategy.source_analyzer import analyze_source_patterns
from src.data_processing.content_strategy.genre_analyzer import analyze_genre_patterns
from src.data_processing.market_analysis.market_analyzer import MarketAnalyzer
from src.dashboard.components.genre_view import render_genre_analysis
from src.dashboard.components.source_view import render_source_analysis
from src.dashboard.components.connections_view import render_network_connections_dashboard
from src.dashboard.components.studio_view import render_studio_performance_dashboard
from src.dashboard.components.prototype_market_intel_view import render_market_intel
from src.dashboard.components.unified_view import render_unified_dashboard
from src.data_processing.creative_networks.connections_analyzer import analyze_network_connections
from src.data_processing.success_analysis.success_analyzer import SuccessAnalyzer
import plotly.graph_objects as go

def main():
    # Custom CSS for section headers
    st.markdown("""
        <style>
        .section-header {
            font-family: 'Source Sans Pro', sans-serif;
            text-transform: uppercase;
            font-weight: 600;
            letter-spacing: 0.1em;
            color: #1E4D8C;
            margin-bottom: 1em;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("STS Analysis Dashboard")
    
    # Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a View",
        ["Market Snapshot", "Network Connections", "Studio Performance", "(Prototype) Market Intel", "Unified Dashboard"]
    )
    
    try:
        # Initialize analyzers with fresh data
        shows_df, team_df = shows_analyzer.fetch_data(force=True)
        market_analyzer = MarketAnalyzer(shows_df, team_df)
    except Exception as e:
        st.error(f"Error initializing data: {str(e)}")
        st.info("Please ensure Google Sheets credentials are properly configured.")
        return
    
    if page == "(Prototype) Market Intel":
        try:
            render_market_intel()
        except Exception as e:
            st.error(f"Error displaying market intel: {str(e)}")
            
    elif page == "Unified Dashboard":
        st.markdown('<p class="section-header">Unified TV Series Dashboard</p>', unsafe_allow_html=True)
        
        try:
            # Initialize success analyzer
            from data_processing.success_analysis.success_analyzer import SuccessAnalyzer
            success_analyzer = SuccessAnalyzer()
            success_analyzer.initialize_data(shows_df)
            
            render_unified_dashboard(shows_df, team_df, success_analyzer)
        except Exception as e:
            st.error(f"Error displaying unified dashboard: {str(e)}")
            
    elif page == "Market Snapshot":
        try:
            from dashboard.components.market_view import render_market_snapshot
            render_market_snapshot(market_analyzer)
        except Exception as e:
            st.error(f"Error displaying market snapshot: {str(e)}")
        

        
    elif page == "Genre Analysis":
        try:
            # Run genre analysis
            analysis_results = analyze_genre_patterns(shows_df)
            
            # Render genre analysis component
            render_genre_analysis(analysis_results)
        except Exception as e:
            st.error(f"Error displaying genre analysis: {str(e)}")

            
    elif page == "Source Analysis":
        st.markdown('<p class="section-header">Source Type Analysis</p>', unsafe_allow_html=True)
        
        try:
            # Get source insights
            source_insights = analyze_source_patterns(shows_df)
            render_source_analysis(source_insights)
        except Exception as e:
            st.error(f"Error displaying source analysis: {str(e)}")
            
    elif page == "Network Connections":
        st.markdown('<p class="section-header">Network Connections Analysis</p>', unsafe_allow_html=True)
        
        try:
            # Initialize connections analyzer using factory function
            connections_analyzer = analyze_network_connections(shows_df, team_df)
            render_network_connections_dashboard(connections_analyzer)
        except Exception as e:
            st.error(f"Error analyzing network connections: {str(e)}")
            
    elif page == "Studio Performance":
        st.markdown('<p class="section-header">Studio Performance Analysis</p>', unsafe_allow_html=True)
        
        try:
            render_studio_performance_dashboard(shows_df)
        except Exception as e:
            st.error(f"Error analyzing studio performance: {str(e)}")
    
if __name__ == "__main__":
    main()
