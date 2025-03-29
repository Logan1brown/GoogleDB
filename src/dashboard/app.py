"""
TV Series Database Dashboard
Main application file for the Streamlit dashboard.

This dashboard provides:
- Automatic insights about TV series data
- Interactive visualizations
- Trend analysis
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from data_processing.analyze_shows import shows_analyzer
from data_processing.creative_networks.role_analysis import RoleAnalyzer
from data_processing.content_strategy.source_analysis import SourceAnalyzer
from data_processing.market_analysis.market_analysis import MarketAnalyzer

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
        ["Market Snapshot", "Genre Analysis", "Source Analysis"]
    )
    
    try:
        # Initialize analyzers with fresh data
        shows_df, team_df = shows_analyzer.fetch_data(force=True)
        role_analyzer = RoleAnalyzer(shows_df, team_df)
        source_analyzer = SourceAnalyzer(shows_df)
        market_analyzer = MarketAnalyzer(shows_df, team_df)
    except Exception as e:
        st.error(f"Error initializing data: {str(e)}")
        st.info("Please ensure Google Sheets credentials are properly configured.")
        return
    
    if page == "Market Snapshot":
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
        
        try:
            # Display key dataset metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Shows", f"{insights['total_shows']:,}")
                shows = sorted(shows_df['show_name'].unique())
                selected_shows = st.multiselect("Filter Shows", shows, max_selections=5)
            with col2:
                st.metric("Unique Creatives", f"{insights['total_creatives']:,}")
                creatives = sorted(team_df['name'].unique())
                selected_creatives = st.multiselect("Filter Creatives", creatives, max_selections=5)
            with col3:
                st.metric("Networks", f"{insights['total_networks']:,}")
                networks = sorted(shows_df['network'].unique())
                selected_networks = st.multiselect("Filter Networks", networks)
            with col4:
                st.metric("Role Types", f"{insights['total_roles']:,}")
                # Use standard roles from RoleAnalyzer
                standard_roles = [
                    'Creator', 'Writer', 'Director', 'Showrunner', 'Co-Showrunner',
                    'Writer/Executive Producer', 'Creative Producer',
                    'Executive Producer', 'Producer', 'Co-Producer', 'Line Producer',
                    'Studio Executive', 'Network Executive', 'Development Executive',
                    'Actor', 'Host'
                ]
                selected_roles = st.multiselect("Filter Roles", sorted(standard_roles))
        except Exception as e:
            st.error(f"Error displaying dataset metrics: {str(e)}")
        
        # Network Distribution Section
        st.markdown('<p class="section-header">Network Distribution</p>', unsafe_allow_html=True)
        
        try:
            # Create and display network chart
            fig = market_analyzer.create_network_chart()
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error creating network visualization: {str(e)}")
            
        # Key Metrics Section
        st.markdown('<p class="section-header">Key Metrics</p>', unsafe_allow_html=True)
        
        # Add metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "Total Shows", 
                f"{insights['total_shows']:,}",
                help="Shows currently in database"
            )
        with col2:
            st.metric(
                "Network Concentration", 
                f"{insights['network_concentration']:.1f}%",
                help=f"Share of shows from top 3 networks: {', '.join(insights['top_3_networks'])}"
            )
        with col3:
            st.metric(
                "Top Genre Network", 
                insights['top_genre_network'],
                f"{insights['top_genre_count']} {insights['top_genre']} Shows",
                help=f"Network with most shows in {insights['top_genre']} genre"
            )
        
    elif page == "Genre Analysis":
        st.header("Genre Analysis")
        st.info("Genre Analysis page is under development. Check back soon!")
            
    elif page == "Source Analysis":
        # Get source insights
        insights = source_analyzer.generate_source_insights()
        
        # Source Distribution Section
        st.markdown('<p class="section-header">Source Distribution</p>', unsafe_allow_html=True)
        
        # Create and display source distribution chart
        fig = source_analyzer.create_distribution_chart()
        st.plotly_chart(fig, use_container_width=True)
        
        # Source Metrics Section
        st.markdown('<p class="section-header">Source Insights</p>', unsafe_allow_html=True)
        
        # Display metrics
        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                "Most Common Source",
                insights['top_source'],
                f"{insights['top_source_count']} Shows"
            )
        with col2:
            st.metric(
                "Original Content",
                f"{insights['original_share']:.1f}%",
                help="Percentage of shows that are original content"
            )
    
if __name__ == "__main__":
    main()
