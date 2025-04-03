"""Market Snapshot Component.

A Streamlit component that provides a market snapshot view with:
- Title section
- Executive summary
- KPI metrics (4 indicators)
- Category selectors (Shows, Creators, Genres, Networks)
- Market distribution visualization
- Performance metrics (4 indicators)
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import logging

logger = logging.getLogger(__name__)


def render_market_snapshot(market_analyzer):
    """Render the market snapshot component.
    
    Args:
        market_analyzer: MarketAnalyzer instance with processed data
    """
    # Get market insights
    insights = market_analyzer.generate_market_insights()
    
    # Dataset Overview
    st.markdown('<p class="section-header">Dataset Overview</p>', unsafe_allow_html=True)
    
    st.markdown("""
    This analysis is based on a curated dataset of straight-to-series orders tracked from Deadline Hollywood.
    While comprehensive within its scope, please note:
    - Focus is on straight-to-series orders rather than traditional pilots
    - Data collection is more complete for recent years
    - Some historical data may be incomplete
    """)
    
    # Display key dataset metrics and filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Shows", f"{insights['total_shows']:,}")
        shows = sorted(market_analyzer.shows_df['show_name'].unique())
        selected_shows = st.multiselect(
            "Filter Shows", 
            shows,
            max_selections=5,
            help="Select up to 5 shows to filter the data"
        )
    with col2:
        st.metric("Unique Creatives", f"{insights['total_creatives']:,}")
        creatives = sorted(market_analyzer.team_df['name'].unique())
        selected_creatives = st.multiselect(
            "Filter Creatives", 
            creatives,
            max_selections=5,
            help="Select up to 5 creatives to filter the data"
        )
    with col3:
        st.metric("Networks", f"{insights['total_networks']:,}")
        networks = sorted(market_analyzer.shows_df['network'].unique())
        selected_networks = st.multiselect(
            "Filter Networks", 
            networks,
            help="Select networks to filter the data"
        )
    with col4:
        avg_success = insights['avg_success_score']
        st.metric(
            "Success Score", 
            f"{avg_success:.0f}/100",
            help="Success score (0-100) based on TMDB metrics: Season count (40pts for S2, +20pts each for S3/S4/S5+), Episode volume (penalty for <11 eps), and Production status (bonus for planned ending). Note: Limited series typically score low since the metric focuses on multi-season success."
        )
        success_options = ["All", "High Success (>80)", "Medium Success (50-80)", "Low Success (<50)"]
        success_filter = st.selectbox(
            "Filter by Success", 
            success_options,
            help="Filter by success score range"
        )
        
    # Track which filter is active and disable others
    active_filter = None
    if selected_shows:
        active_filter = "shows"
    elif selected_networks:
        active_filter = "networks"
    elif selected_creatives:
        active_filter = "creatives"
    elif success_filter != "All":
        active_filter = "success"
        
    if active_filter:
        st.info(f"⚠️ {active_filter.title()} filter is active. Clear it to use other filters.")

    # Network Distribution Section
    st.markdown('<p class="section-header">Network Distribution</p>', unsafe_allow_html=True)
    
    # Filter data based on success level
    filtered_df = market_analyzer.shows_df.copy()
    if success_filter != "All":
        if success_filter == "High Success (>80)":
            filtered_df = filtered_df[filtered_df['success_score'] > 80]
        elif success_filter == "Medium Success (50-80)":
            filtered_df = filtered_df[(filtered_df['success_score'] >= 50) & (filtered_df['success_score'] <= 80)]
        elif success_filter == "Low Success (<50)":
            filtered_df = filtered_df[filtered_df['success_score'] < 50]
    
    # Apply show filters if selected
    if selected_shows:
        filtered_df = filtered_df[filtered_df['show_name'].isin(selected_shows)]
    
    # Apply network filters if selected
    if selected_networks:
        filtered_df = filtered_df[filtered_df['network'].isin(selected_networks)]
    
    # Apply creative filters if selected - this requires joining with show_team data
    if selected_creatives:
        # Get all shows for selected creatives
        creative_shows = market_analyzer.team_df[
            market_analyzer.team_df['name'].isin(selected_creatives)
        ]['show_id'].unique()
        
        # Filter shows by show_id
        filtered_df = filtered_df[filtered_df['show_id'].isin(creative_shows)]
        
        if len(filtered_df) == 0:
            st.info("No shows found for selected creatives.")
    
    # Update analyzer with filtered data
    market_analyzer.shows_df = filtered_df
    
    # Create and display network chart
    fig = market_analyzer.create_network_chart()
    st.plotly_chart(fig, use_container_width=True)
    
    # Key Metrics Section
    st.markdown('<p class="section-header">Key Metrics</p>', unsafe_allow_html=True)
    
    # Add metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "Top Network",
            f"{insights['top_success_network']}",
            help=f"Highest average success score: {insights['top_success_score']:.0f} out of 100"
        )
    with col2:
        st.metric(
            "Network Concentration", 
            f"{insights['network_concentration']:.1f}%",
            help=f"Share of shows from top 3 networks: {', '.join(insights['top_3_networks'])}"
        )
    with col3:
        st.metric(
            "Vertical Integration", 
            f"{insights['vertical_integration']:.0f}%",
            help="Percentage of shows from vertically integrated studios"
        )
    
