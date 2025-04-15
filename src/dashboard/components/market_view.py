"""Market Snapshot Component.

A Streamlit component that provides a market snapshot view with:
- Title section
- Executive summary
- KPI metrics (4 indicators)
- Category selectors (Shows, Creators, Genres, Networks)
- Market distribution visualization
- Performance metrics (4 indicators)

Uses secure Supabase views for data access.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import logging
from src.data_processing.market_analysis.market_analyzer_secure import MarketAnalyzer
from src.dashboard.utils.style_config import COLORS

logger = logging.getLogger(__name__)


def render_market_snapshot(market_analyzer, supabase):
    """Render the market snapshot component.
    
    Args:
        market_analyzer: MarketAnalyzer instance with processed data
        supabase: Initialized Supabase client for querying data
    """
    # Initialize filtered DataFrame
    filtered_df = market_analyzer.shows_df.copy()
    
    # Calculate initial insights with ALL networks - used for displaying total numbers 
    # in the metrics section (total shows, total networks, etc.)
    # We want these numbers to reflect the entire dataset before filtering
    initial_insights = market_analyzer.generate_market_insights(filtered_df)
    
    # Add custom CSS for selectbox
    st.markdown("""
    <style>
    div[data-baseweb="select"] > div {
        background-color: white;
        border-radius: 4px;
        border-color: rgb(49, 51, 63);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Display key dataset metrics and filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Titles", f"{initial_insights['total_shows']:,}")
        shows = sorted(market_analyzer.shows_df['title'].unique())
        selected_shows = st.multiselect(
            "Filter Titles", 
            shows,
            max_selections=5,
            help="Select up to 5 titles to filter the data",
            key="market_filter_shows"
        )
    with col2:
        # Get total unique team members from secure API view
        unique_members = set()
        
        # Get all records with pagination
        page = 0
        while True:
            names = supabase.table('api_show_team').select('name').range(page*1000, (page+1)*1000-1).execute()
            if not names.data:
                break
            # Clean names and ensure no empty values
            unique_members.update(member['name'].strip() for member in names.data if member.get('name'))
            page += 1
        
        st.metric("Unique Creatives", f"{len(unique_members):,}")
        creatives = sorted(name for name in unique_members if name)
        selected_creatives = st.multiselect(
            "Filter Creatives", 
            creatives,
            max_selections=5,
            help="Select up to 5 creatives to filter the data",
            key="market_filter_creatives"
        )
    with col3:
        st.metric("Networks", f"{initial_insights['total_networks']:,}")
        networks = sorted(market_analyzer.shows_df['network_name'].unique())
        selected_networks = st.multiselect(
            "Filter Networks", 
            networks,
            help="Select networks to filter the data",
            key="market_filter_networks"
        )
    with col4:
        avg_success = initial_insights['avg_success_score']
        st.metric(
            "Success Score", 
            f"{avg_success:.0f}/100",
            help="Average title success score (0-100) based on:\n" +
                 "- Number of Seasons (40pts for S2, +20pts each for S3/S4/S5+)\n" +
                 "- Show Status (bonus for planned ending, penalty for cancellation)\n" +
                 "- Episode Volume (penalty for <11 eps)\n\n" +
                 "Note: Limited series typically score low since the metric focuses on multi-season success."
        )
        success_filter = st.selectbox(
            "Success Tier", 
            ["All", "High (>80)", "Medium (50-80)", "Low (<50)"],
            help="Filter by success score range",
            key="market_filter_success",
            label_visibility="visible"
        )
        
    # Track which filter is active and disable others
    active_filter = None
    if selected_shows:
        active_filter = "shows"
    elif selected_networks:
        active_filter = "networks"
    elif selected_creatives:
        active_filter = "creatives"
        
    # Only show warning for multi-select filters that need to be cleared
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
        if success_filter == "High (>80)":
            high_success_ids = [id for id, score in success_scores.items() if score > 80]
            filtered_df = filtered_df[filtered_df['tmdb_id'].isin(high_success_ids)]
        elif success_filter == "Medium (50-80)":
            med_success_ids = [id for id, score in success_scores.items() if 50 <= score <= 80]
            filtered_df = filtered_df[filtered_df['tmdb_id'].isin(med_success_ids)]
        elif success_filter == "Low (<50)":
            low_success_ids = [id for id, score in success_scores.items() if score < 50]
            filtered_df = filtered_df[filtered_df['tmdb_id'].isin(low_success_ids)]
    
    # Apply show filters if selected
    if selected_shows:  # Check if any shows are selected
        filtered_df = filtered_df[filtered_df['title'].isin(selected_shows)]
    
    # Apply creative filters if selected
    if selected_creatives:
        # Find shows for selected creatives using api_show_team view
        creative_shows = set()
        for creative in selected_creatives:
            # Get show titles for this creative
            shows = supabase.table('api_show_team').select('title').eq('name', creative).execute()
            creative_shows.update(show['title'] for show in shows.data if show.get('title'))
        
        # Filter shows by matching show names
        filtered_df = filtered_df[filtered_df['title'].isin(creative_shows)]
        
        if len(filtered_df) == 0:
            st.info("No shows found for selected creatives.")
    
    # Get networks with more than 1 show
    network_counts = filtered_df.groupby('network_name').size()
    multi_show_networks = network_counts[network_counts > 1].index
    
    # Filter DataFrame to only include multi-show networks
    filtered_df = filtered_df[filtered_df['network_name'].isin(multi_show_networks)]
    
    # Calculate filtered insights using only networks with multiple shows
    # This is used for the graph and success metrics to avoid single-show networks
    # skewing the network performance calculations
    insights = market_analyzer.generate_market_insights(filtered_df)
    
    # Get success metrics from the filtered data
    success_metrics = market_analyzer.success_analyzer.analyze_market(filtered_df)
    
    # Get success scores by network first
    network_scores = {}
    for show_id, show_data in success_metrics['shows'].items():
        show = filtered_df[filtered_df['tmdb_id'] == show_id].iloc[0] if len(filtered_df[filtered_df['tmdb_id'] == show_id]) > 0 else None
        if show is not None:
            network = show['network_name']
            if network not in network_scores:
                network_scores[network] = []
            network_scores[network].append(show_data['score'])
    
    # If filtering by success tier, only include networks that have scores
    if success_filter != "All":
        networks_with_scores = set(network_scores.keys())
        filtered_df = filtered_df[filtered_df['network_name'].isin(networks_with_scores)]
    
    # Get network distribution after filtering
    shows_by_network = filtered_df.groupby('network_name').size()
    # Filter to only networks with more than 1 show
    shows_by_network = shows_by_network[shows_by_network > 1].sort_values(ascending=False)
    
    # Calculate average scores and create hover text
    avg_scores = []
    hover_text = []
    for network, count in shows_by_network.items():
        text = f'{network}<br>Titles: {count}'
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
            # Use grey color for networks without score data
            colors.append(COLORS['success']['none'])
        else:
            # Use predefined success colors based on score ranges
            if score > 80:
                colors.append(COLORS['success']['high'])
            elif score >= 50:
                colors.append(COLORS['success']['medium'])
            else:
                colors.append(COLORS['success']['low'])
    
    # Create chart
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=list(shows_by_network.index),
        y=list(shows_by_network.values),
        name="Titles per Network",
        marker_color=colors,
        hovertext=hover_text,
        hoverinfo='text'
    ))
    
    # Update layout
    fig.update_layout(
        xaxis_title="Network",
        yaxis_title="Number of Titles",
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
            help=f"Share of titles from top 3 networks: {', '.join(insights['top_3_networks'].index)}"
        )
    with col3:
        st.metric(
            "Vertical Integration", 
            f"{insights['vertical_integration']:.0f}%",
            help="Percentage of titles from vertically integrated studios"
        )
    
