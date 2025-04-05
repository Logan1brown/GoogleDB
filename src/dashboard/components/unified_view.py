"""
Unified Dashboard View Component.

A Streamlit component that provides a unified view with:
- Acquisition View (Networks, Creators, Pairings, Insights)
- Packaging View
- Development View

=== CRITICAL COLUMN NAME DIFFERENCES ===
1. Show IDs: We use 'tmdb_id' as the ID column
2. Show Names:
   - shows sheet: uses 'shows' column
   - show_team sheet: uses 'show_name' column
NEVER try to normalize these column names - they must stay different.
"""

import streamlit as st
import pandas as pd
import logging
from data_processing.unified.unified_analyzer import UnifiedAnalyzer
from dashboard.utils.style_config import COLORS

logger = logging.getLogger(__name__)

def render_filters():
    """Render source type and genre filters that persist across tabs."""
    with st.sidebar:
        source_type = st.selectbox(
            "Source Type",
            options=["All", "Original", "Book", "IP"],
            key="unified_source_type"
        )
        
        genre = st.selectbox(
            "Genre",
            options=["All", "Drama", "Comedy", "Thriller", "Fantasy"],
            key="unified_genre"
        )
        
    return (
        None if source_type == "All" else source_type,
        None if genre == "All" else genre
    )

def render_acquisition_view(unified_analyzer: UnifiedAnalyzer, source_type: str, genre: str):
    """Render the acquisition view with its tabs.
    
    Args:
        unified_analyzer: UnifiedAnalyzer instance
        source_type: Selected source type filter
        genre: Selected genre filter
    """
    filtered_df = unified_analyzer.get_filtered_data(source_type, genre)
    
    tabs = st.tabs(["Networks", "Creators", "Pairings", "Insights"])
    
    with tabs[0]:  # Networks
        st.markdown("### Network Performance")
        networks = unified_analyzer.analyze_networks(filtered_df)
        
        for network in networks:
            st.markdown(f"""
            {network['network']}<br>
            Shows in Genre: {network['show_count']}<br>
            Success Score: {network['success_score']:.0f}%<br>
            Renewal Rate: {network['renewal_rate']:.0f}%<br>
            <br>
            """, unsafe_allow_html=True)
    
    with tabs[1]:  # Creators
        st.markdown("### Top Creators")
        # Implementation will go here
        
    with tabs[2]:  # Pairings
        st.markdown("### Successful Pairings")
        # Implementation will go here
        
    with tabs[3]:  # Insights
        st.markdown("### Market Insights")
        # Implementation will go here

def render_packaging_view(unified_analyzer: UnifiedAnalyzer, source_type: str, genre: str):
    """Render the packaging view with suggestions.
    
    Args:
        unified_analyzer: UnifiedAnalyzer instance
        source_type: Selected source type filter
        genre: Selected genre filter
    """
    st.markdown("### Package Suggestions")
    # Implementation will go here

def render_development_view(unified_analyzer: UnifiedAnalyzer, source_type: str, genre: str):
    """Render the development view with network alignment.
    
    Args:
        unified_analyzer: UnifiedAnalyzer instance
        source_type: Selected source type filter
        genre: Selected genre filter
    """
    st.markdown("### Development Strategy")
    # Implementation will go here

def render_unified_dashboard(shows_df: pd.DataFrame, team_df: pd.DataFrame):
    """Main entry point for the unified dashboard view.
    
    Args:
        shows_df: DataFrame containing show information
        team_df: DataFrame containing team member information
    """
    try:
        logger.info("Starting unified dashboard render")
        logger.info(f"Shows DataFrame columns: {shows_df.columns.tolist()}")
        logger.info(f"Team DataFrame columns: {team_df.columns.tolist()}")
        
        # Initialize analyzer
        try:
            unified_analyzer = UnifiedAnalyzer(shows_df, team_df)
            logger.info("Successfully initialized UnifiedAnalyzer")
        except Exception as e:
            logger.error(f"Failed to initialize UnifiedAnalyzer: {str(e)}")
            raise
        
        # Render persistent filters
        try:
            source_type, genre = render_filters()
            logger.info(f"Filters selected - Source Type: {source_type}, Genre: {genre}")
        except Exception as e:
            logger.error(f"Failed to render filters: {str(e)}")
            raise
        
        # Render view tabs
        try:
            view_tabs = st.tabs(["Acquisition", "Packaging", "Development"])
            
            with view_tabs[0]:
                render_acquisition_view(unified_analyzer, source_type, genre)
                
            with view_tabs[1]:
                render_packaging_view(unified_analyzer, source_type, genre)
                
            with view_tabs[2]:
                render_development_view(unified_analyzer, source_type, genre)
                
            logger.info("Successfully rendered all view tabs")
        except Exception as e:
            logger.error(f"Failed to render view tabs: {str(e)}")
            raise
            
    except Exception as e:
        logger.error(f"Error in unified dashboard: {str(e)}")
        st.error(f"An error occurred while rendering the unified dashboard: {str(e)}")
