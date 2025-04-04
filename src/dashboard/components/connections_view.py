"""Network Connections View.

Renders the network connections dashboard with:
- Interactive heatmap visualization
- Network comparison dropdowns
- Genre and source filters
- Success stories tab
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Dict, List, Optional

from src.dashboard.utils.style_config import COLORS, CHART_DEFAULTS, DIMENSIONS
from src.dashboard.templates.defaults import create_heatmap_defaults

def render_filter_section() -> Dict[str, Optional[str]]:
    """Render filter dropdowns for networks, genre, and source.
    
    Returns:
        Dict containing selected values for each filter
    """
    # Get filter options from analyzer
    filter_options = st.session_state.get('filter_options', {
        'networks': [],
        'genres': [],
        'sources': []
    })
    
    # Network dropdowns
    st.markdown("### Network Comparison")
    network1 = st.selectbox(
        "First Network",
        ["All Networks"] + filter_options['networks'],
        key="network1"
    )
    
    network2 = st.selectbox(
        "Second Network",
        ["All Networks"] + filter_options['networks'],
        key="network2"
    )
    
    # Additional filters
    st.markdown("### Filters")
    genre = st.selectbox(
        "Genre",
        ["All Genres"] + filter_options['genres'],
        key="genre"
    )
    
    source = st.selectbox(
        "Source Type",
        ["All Sources"] + filter_options['sources'],
        key="source"
    )
    
    return {
        'network1': None if network1 == "All Networks" else network1,
        'network2': None if network2 == "All Networks" else network2,
        'genre': None if genre == "All Genres" else genre,
        'source': None if source == "All Sources" else source
    }

def render_heatmap(connections_analyzer, filters: Dict[str, Optional[str]]) -> None:
    """Render network connections heatmap.
    
    Args:
        connections_analyzer: ConnectionsAnalyzer instance
        filters: Dictionary of filter values
    """
    try:
        # Get filtered matrix data
        matrix, networks = connections_analyzer.get_shared_creators_matrix(
            network1=filters['network1'],
            network2=filters['network2'],
            genre=filters['genre'],
            source=filters['source']
        )
        
        if len(networks) == 0:
            st.info("No network connections found matching the current filters.")
            return
            
        # Calculate dimensions based on content
        n_networks = len(networks)
        cell_size = 30  # Smaller base size for each cell
        plot_width = min(1000, n_networks * cell_size + 200)  # Smaller cap width
        plot_height = min(600, n_networks * cell_size + 100)  # Much smaller cap height
            
        # Create heatmap using plotly express
        df = pd.DataFrame(matrix, columns=networks, index=networks)
        fig = px.imshow(
            df,
            color_continuous_scale=CHART_DEFAULTS['colorscales']['primary'],
            labels=dict(color='Shared Creators'),
            aspect='auto'
        )
        
        # Update hover template
        fig.update_traces(
            hovertemplate='%{x} ↔ %{y}<br>Shared Creators: %{z}<extra></extra>'
        )
        
        # Update layout using style config
        fig.update_layout(
            width=plot_width,
            height=plot_height,
            margin=CHART_DEFAULTS['margin']['plot'],
            font=dict(size=12),  # Base font size
            xaxis=dict(
                title=None,
                tickangle=45,  # Angle network names
                fixedrange=True,  # Prevent zoom
                side='top'  # Move labels to top
            ),
            yaxis=dict(
                title=None,
                fixedrange=True,  # Prevent zoom
                autorange='reversed'  # Show networks top to bottom
            ),
            coloraxis_colorbar=dict(
                title=dict(
                    text='Shared Creators',
                    side='right'
                ),
                thicknessmode='pixels',
                thickness=20,
                lenmode='fraction',
                len=0.75,
                yanchor='middle',
                y=0.5,
                xanchor='left',
                x=1.02
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Add explanation with current filter context
        filter_text = []
        if filters['genre']:
            filter_text.append(f"genre '{filters['genre']}'")
        if filters['source']:
            filter_text.append(f"source '{filters['source']}'")
            
        context = f" for {' and '.join(filter_text)}" if filter_text else ""
        
        st.info(
            "💡 The heatmap shows the strength of connections between networks "
            f"based on shared creative talent{context}. Darker colors indicate more shared creators."
        )
        
    except Exception as e:
        st.error(f"Error rendering heatmap: {str(e)}")
        st.exception(e)
    
    # Add explanation
    st.info(
        "💡 The heatmap shows the strength of connections between networks "
        "based on shared creative talent. Darker colors indicate more shared creators."
    )

def render_success_stories(connections_analyzer, filters: Dict[str, Optional[str]]) -> None:
    """Render success stories section.
    
    Args:
        connections_analyzer: ConnectionsAnalyzer instance
        filters: Dictionary of filter values
    """
    try:
        # Handle network filter - if both selected, show stories for either
        network = None
        if filters['network1'] and filters['network2']:
            network = filters['network1']  # Stories will show both networks if present
        else:
            network = filters['network1'] or filters['network2']
        
        # Get filtered success stories
        stories = connections_analyzer.get_success_stories(
            network=network,
            genre=filters['genre'],
            source=filters['source']
        )
        
        if not stories:
            st.info("No success stories found matching the current filters.")
            return
            
        # Group stories by role
        role_stories = {}
        for story in stories:
            try:
                # Validate story has required fields
                required_fields = {'creator_team', 'networks', 'show_count', 'roles'}
                if not all(field in story for field in required_fields):
                    st.error(f"Invalid story format: {story}")
                    continue
                    
                # Group by primary role
                primary_role = sorted(story['roles'])[0] if story['roles'] else 'Other'
                if primary_role not in role_stories:
                    role_stories[primary_role] = []
                role_stories[primary_role].append(story)
                
            except Exception as e:
                st.error(f"Error processing story: {str(e)}")
                continue
                
        # Display stories by role
        for role, role_group in sorted(role_stories.items()):
            st.markdown(
                f"<h4 style='color: #1f77b4; margin: 0.8em 0 0.3em;'>{role}</h4>",
                unsafe_allow_html=True
            )
            
            # Sort stories by network count
            sorted_stories = sorted(
                role_group,
                key=lambda x: (len(x['networks']), x['show_count']),
                reverse=True
            )
            
            for story in sorted_stories:
                networks = ', '.join(sorted(story['networks']))
                st.markdown(
                    f"• **{story['creator_team']}**: {story['show_count']} shows across "
                    f"{len(story['networks'])} networks ({networks})"
                )
                
    except Exception as e:
        st.error(f"Error getting success stories: {str(e)}")
        st.exception(e)

def render_network_connections_dashboard(connections_analyzer) -> None:
    """Render the complete network connections dashboard.
    
    Args:
        connections_analyzer: ConnectionsAnalyzer instance with processed data
    """
    if not connections_analyzer:
        st.error("Network analyzer not initialized. Please check data loading.")
        return
        
    st.title("Network Connections Analysis")
    
    try:
        # Store filter options in session state if not present
        if 'filter_options' not in st.session_state:
            filter_options = connections_analyzer.get_filter_options()
            if not filter_options:
                st.error("Failed to get filter options. Please check the data.")
                return
            st.session_state.filter_options = filter_options
            
        # Create side-by-side layout
        # Use dashboard dimensions for overall height
        col1, col2 = st.columns([0.6, 0.4])
        
        # Right side: Tabs and Filters
        with col2:
            tab1, tab2 = st.tabs(["Search", "Success Stories"])
            
            with tab1:
                # Network dropdowns and filters
                filters = render_filter_section()
                
                # Show filtered results in scrollable container
                st.markdown("### Results")
                with st.container(height=DIMENSIONS['dashboard']['height']):
                    # Get filtered creators
                    networks = []
                    if filters['network1']:
                        networks.append(filters['network1'])
                    if filters['network2']:
                        networks.append(filters['network2'])
                    
                    # Get filtered creators
                    creators = connections_analyzer.filter_creators(
                        networks=networks if networks else None,
                        genre=filters['genre'],
                        source_type=filters['source']
                    )
                    
                    if not creators:
                        st.info("No creators found matching the current filters.")
                    else:
                        # Show creator info
                        for creator in creators:
                            with st.expander(f"{creator.name} ({creator.total_shows} shows)"):
                                st.write("Networks:", ", ".join(sorted(creator.networks)))
                                st.write("Genres:", ", ".join(sorted(creator.genres)))
                                st.write("Source Types:", ", ".join(sorted(creator.source_types)))
            
            with tab2:
                render_success_stories(connections_analyzer, filters)
                
        # Left side: Heatmap (using filters from right side)
        with col1:
            render_heatmap(connections_analyzer, filters)
            
    except Exception as e:
        st.error(f"Error rendering dashboard: {str(e)}")
        st.exception(e)
