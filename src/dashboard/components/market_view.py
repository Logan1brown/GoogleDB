"""Market Snapshot Component.

A Streamlit component that provides a market snapshot view with:
- Title section
- Executive summary
- KPI metrics (4 indicators)
- Category selectors (Shows, Creators, Genres, Networks)
- Market distribution visualization
- Performance metrics (4 indicators)

=== CRITICAL COLUMN NAME DIFFERENCES ===
1. Show IDs: We use 'tmdb_id' as the ID column, not 'id' or 'show_id'
2. Show Names:
   - shows sheet: uses 'shows' column
   - show_team sheet: uses 'show_name' column
NEVER try to normalize these column names - they must stay different.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import logging
from src.data_processing.market_analysis.market_analyzer import MarketAnalyzer
from src.dashboard.utils.style_config import COLORS

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
        # === CRITICAL: Column Name Difference ===
        # shows sheet uses 'shows' column, show_team sheet uses 'show_name'
        shows = sorted(market_analyzer.shows_df['shows'].unique())
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
            help="Average show success score (0-100) based on:\n" +
                 "- Number of Seasons (40pts for S2, +20pts each for S3/S4/S5+)\n" +
                 "- Show Status (bonus for planned ending, penalty for cancellation)\n" +
                 "- Episode Volume (penalty for <11 eps)\n\n" +
                 "Note: Limited series typically score low since the metric focuses on multi-season success."
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
        # Get success metrics which has scores for each show
        success_metrics = market_analyzer.success_analyzer.analyze_market(filtered_df)
        
        # Create a mapping of show ID to success score
        success_scores = {}
        for show_id, data in success_metrics['shows'].items():
            success_scores[show_id] = data['score']
        
        # Filter based on success tier
        if success_filter == "High Success (>80)":
            high_success_ids = [id for id, score in success_scores.items() if score > 80]
            filtered_df = filtered_df[filtered_df['tmdb_id'].isin(high_success_ids)]
        elif success_filter == "Medium Success (50-80)":
            med_success_ids = [id for id, score in success_scores.items() if 50 <= score <= 80]
            filtered_df = filtered_df[filtered_df['tmdb_id'].isin(med_success_ids)]
        elif success_filter == "Low Success (<50)":
            low_success_ids = [id for id, score in success_scores.items() if score < 50]
            filtered_df = filtered_df[filtered_df['tmdb_id'].isin(low_success_ids)]
    
    # Apply show filters if selected
    if selected_shows:  # Check if any shows are selected
        # === CRITICAL: Column Name Difference ===
        # shows sheet uses 'shows' column, show_team sheet uses 'show_name'
        filtered_df = filtered_df[filtered_df['shows'].isin(selected_shows)]
    
    # Apply network filters if selected
    if selected_networks:
        filtered_df = filtered_df[filtered_df['network'].isin(selected_networks)]
    
    # Apply creative filters if selected - this requires joining with show_team data
    if selected_creatives:
        # === CRITICAL: Column Name Difference ===
        # team_df uses 'show_name' column, shows_df uses 'shows' column
        creative_shows = market_analyzer.team_df[
            market_analyzer.team_df['name'].isin(selected_creatives)
        ]['show_name'].unique()
        
        # Filter shows by matching show_name to shows column
        filtered_df = filtered_df[filtered_df['shows'].isin(creative_shows)]
        
        if len(filtered_df) == 0:
            st.info("No shows found for selected creatives.")
    
    # Get success metrics from the filtered data
    success_metrics = market_analyzer.success_analyzer.analyze_market(filtered_df)
    
    # Get network distribution
    shows_by_network = filtered_df.groupby('network').size().sort_values(ascending=False)
    
    # Get success scores by network
    network_scores = {}
    for show_id, show_data in success_metrics['shows'].items():
        show = filtered_df[filtered_df['tmdb_id'] == show_id].iloc[0] if len(filtered_df[filtered_df['tmdb_id'] == show_id]) > 0 else None
        if show is not None:
            network = show['network']
            if network not in network_scores:
                network_scores[network] = []
            network_scores[network].append(show_data['score'])
    
    # Calculate average scores and create hover text
    avg_scores = []
    hover_text = []
    for network, count in shows_by_network.items():
        text = f'{network}<br>Shows: {count}'
        if network in network_scores:
            avg = sum(network_scores[network]) / len(network_scores[network])
            avg_scores.append(avg)
            text += f'<br>Avg Success Score: {avg:.1f}'
        else:
            avg_scores.append(0)  # No score data
        hover_text.append(text)
    
    # Create color array using Viridis colorscale
    colors = []
    for score in avg_scores:
        if score == 0:
            colors.append(COLORS['success']['none'])  # Grey for no data
        else:
            # Map score (0-100) to Viridis colorscale (0-1)
            normalized_score = score / 100
            colors.append(f'rgb({int(72 + (253-72)*normalized_score)}, {int(17 + (231-17)*normalized_score)}, {int(121 + (37-121)*normalized_score)})')
    
    # Create chart
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=list(shows_by_network.index),
        y=list(shows_by_network.values),
        name="Shows per Network",
        marker_color=colors,
        hovertext=hover_text,
        hoverinfo='text'
    ))
    
    # Update layout
    fig.update_layout(
        xaxis_title="Network",
        yaxis_title="Number of Shows",
        font_family="Source Sans Pro",
        showlegend=False,
        margin=dict(t=20)
    )
    
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
    
