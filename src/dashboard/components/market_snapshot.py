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

from ..templates.grids.chart_only import create_chart_grid
from ..templates.defaults.bar import create_bar_defaults

def render_market_snapshot(market_analyzer):
    """Render the market snapshot component.
    
    Args:
        market_analyzer: MarketAnalyzer instance with processed data
    """
    # Title and Executive Summary
    st.title("Market Snapshot")
    st.markdown("""Executive Summary: Analysis of current market distribution 
                across key dimensions with performance indicators.""")
    
    # KPI Metrics Row
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        total_shows = len(market_analyzer.shows_df)
        st.metric("Total Shows", str(total_shows), None)
    with kpi2:
        total_networks = len(market_analyzer.shows_df['network'].unique())
        st.metric("Networks", str(total_networks), None)
    with kpi3:
        total_creators = len(market_analyzer.team_df['name'].unique())
        st.metric("Creators", str(total_creators), None)
    with kpi4:
        total_genres = len(market_analyzer.shows_df['genre'].unique())
        st.metric("Genres", str(total_genres), None)
    
    # Category Selectors
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.selectbox("Shows", ["All Shows"] + sorted(market_analyzer.shows_df['show_name'].unique().tolist()))
    with col2:
        st.selectbox("Creators", ["All Creators"] + sorted(market_analyzer.team_df['name'].unique().tolist()))
    with col3:
        st.selectbox("Genres", ["All Genres"] + sorted(market_analyzer.shows_df['genre'].unique().tolist()))
    with col4:
        st.selectbox("Networks", ["All Networks"] + sorted(market_analyzer.shows_df['network'].unique().tolist()))
    
    # Market Distribution Chart
    fig = create_chart_grid(
        chart_title="Market Distribution",
        margin=dict(t=50, b=20, l=20, r=20)
    )
    
    # Get network distribution from analyzer
    network_fig = market_analyzer.create_network_chart()
    
    # Transfer the trace to our grid
    for trace in network_fig.data:
        fig.add_trace(trace)
    
    # Apply bar styling
    fig.update_layout(template=create_bar_defaults())
    
    # Display the chart
    st.plotly_chart(fig, use_container_width=True)
    
    # Performance Metrics (using top networks/genres)
    perf1, perf2, perf3, perf4 = st.columns(4)
    with perf1:
        top_network = market_analyzer.shows_df['network'].mode()[0]
        st.metric("Top Network", top_network)
    with perf2:
        top_genre = market_analyzer.shows_df['genre'].mode()[0]
        st.metric("Top Genre", top_genre)
    with perf3:
        network_count = len(market_analyzer.shows_df['network'].unique())
        st.metric("Network Coverage", f"{network_count} Networks")
    with perf4:
        genre_count = len(market_analyzer.shows_df['genre'].unique())
        st.metric("Genre Coverage", f"{genre_count} Genres")
