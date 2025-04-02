"""Studio Performance View.

Renders the studio performance dashboard including:
- Force-directed studio relationship graph
- Studio filtering and analysis interface
- Studio insights and metrics
"""

from typing import Dict
import plotly.graph_objects as go
import streamlit as st
import pandas as pd
import networkx as nx
from src.data_processing.studio_performance.studio_analyzer import (
    analyze_studio_relationships,
    get_studio_insights
)

def create_studio_graph(shows_df: pd.DataFrame) -> go.Figure:
    """Create grouped bar chart showing studio-network distribution.
    
    Args:
        shows_df: DataFrame with show information
        
    Returns:
        Plotly figure with studio-network distribution
    """
    # Get studio relationship data
    analysis = analyze_studio_relationships(shows_df)
    
    # Get top 15 studios by total shows (excluding empty/whitespace studios)
    studio_sizes = pd.Series({s: count for s, count in analysis['studio_sizes'].items() 
                            if s and not s.isspace()})
    print("Studios:", sorted(studio_sizes.index))  # Debug print
    top_studios = studio_sizes.nlargest(15)
    
    # Get network distribution for each studio
    data = []
    networks = set()
    studio_network_counts = {}
    
    for studio in top_studios.index:
        # Get show counts by network for this studio
        studio_shows = shows_df[shows_df['studio'].str.contains(studio, na=False)]
        # Filter out null/empty networks
        studio_shows = studio_shows[studio_shows['network'].notna() & (studio_shows['network'] != '')]
        network_counts = studio_shows['network'].value_counts()
        
        # Store counts and track unique networks
        studio_network_counts[studio] = network_counts
        networks.update(network_counts.index)
    
    # Create bar for each network
    for network in sorted(networks):
        y_vals = []
        hover_text = []
        
        for studio in top_studios.index:
            count = studio_network_counts[studio].get(network, 0)
            y_vals.append(count)
            hover_text.append(f"{studio} on {network}: {count} shows")
        
        data.append(go.Bar(
            name=network,
            x=top_studios.index,
            y=y_vals,
            text=y_vals,
            textposition='auto',
            hovertext=hover_text,
            hoverinfo='text'
        ))
    
    # Create figure
    fig = go.Figure(data=data)
    
    # Update layout
    fig.update_layout(
        title='Studio Distribution Across Networks',
        barmode='stack',
        showlegend=True,
        legend=dict(
            title_text='Networks',
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02,  # Position legend just outside the plot
            bgcolor="rgba(255, 255, 255, 0.8)"
        ),
        height=600,
        margin=dict(l=50, r=150, b=150),  # More space for studio names at bottom
        xaxis=dict(
            title=None,  # No need for title since studio names are self-explanatory
            tickfont=dict(size=10),
            tickangle=45  # Angle the studio names for better readability
        ),
        yaxis=dict(
            title="Number of Shows",
            range=[0, 45],  # Set max just above highest value (41)
            tickfont=dict(size=10)
        ),
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Arial"
        )
    )
    
    return fig

def render_studio_metrics(analysis_results: Dict) -> None:
    """Render key metrics about studios.
    
    Args:
        analysis_results: Results from analyze_studio_relationships
    """
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Total Studios",
            analysis_results['total_studios'],
            help="Total number of unique studios in database"
        )
    
    # Get top studio by show count
    top_studio = analysis_results['top_studios'][0]
    top_count = analysis_results['studio_sizes'][top_studio]
    
    with col2:
        st.metric(
            "Most Active Studio",
            top_studio,
            f"{top_count} shows",
            help="Studio with the most shows in database"
        )
    
    # Calculate network diversity (avg networks per studio)
    network_counts = [len(networks) for networks in analysis_results['network_relationships'].values()]
    avg_networks = sum(network_counts) / len(network_counts) if network_counts else 0
    
    with col3:
        st.metric(
            "Avg Networks per Studio",
            f"{avg_networks:.1f}",
            help="Average number of different networks each studio works with"
        )

def render_studio_filter(shows_df: pd.DataFrame, analysis_results: Dict) -> None:
    """Render studio filtering and analysis interface.
    
    Args:
        shows_df: DataFrame with show information
        analysis_results: Results from analyze_studio_relationships
    """
    # Get all studios and their show counts
    studio_counts = pd.Series(analysis_results['studio_sizes'])
    
    # Filter out empty/whitespace studios and sort by count
    valid_studios = pd.Series({k: v for k, v in studio_counts.items() 
                              if k and not str(k).isspace()})
    valid_studios = valid_studios.sort_values(ascending=False)
    
    # Create studio options with show counts
    studio_options = [f"{studio} ({count} shows)" for studio, count in valid_studios.items()]
    
    # Studio selection
    selected_option = st.selectbox(
        "Select Studio",
        studio_options,
        help="Choose a studio to analyze"
    )
    
    # Extract studio name from selection
    selected_studio = selected_option.split(' (')[0] if selected_option else None
    
    if selected_studio:
        # Get insights for selected studio
        insights = get_studio_insights(shows_df, selected_studio)
        
        # Cache insights in session state
        if 'studio_insights' not in st.session_state:
            st.session_state.studio_insights = {}
        st.session_state.studio_insights[selected_studio] = insights
        
        # Debug insights
        print("\nInsights received:")
        for key, value in insights.items():
            print(f"{key}: {value}")
        
        # Show total valid shows
        st.write(f"### {insights.get('show_count', 0)} Shows")
        
        # Display insights in expandable sections
        if insights.get('top_genres'):
            with st.expander("Genre Distribution", expanded=True):
                for genre, count in sorted(insights['top_genres'].items(), key=lambda x: x[1], reverse=True):
                    st.write(f"{genre}: {count} shows")
        
        if insights.get('network_partners'):
            with st.expander("Network Partners", expanded=True):
                for network, count in sorted(insights['network_partners'].items(), key=lambda x: x[1], reverse=True):
                    st.write(f"{network}: {count} shows")
        
        if insights.get('show_details'):
            with st.expander("Show List", expanded=True):
                # Create a table of shows
                show_data = []
                for show in sorted(insights['show_details'], key=lambda x: x['title']):
                    show_data.append([show['title'], show['network'], show['genre']])
                
                if show_data:
                    df = pd.DataFrame(show_data, columns=['Title', 'Network', 'Genre'])
                    st.dataframe(df, hide_index=True)

def render_studio_success_stories(analysis_results: Dict) -> None:
    """Render studio success stories and collaborations.
    
    Args:
        analysis_results: Results from analyze_studio_relationships
    """
    # Show indie studio success stories
    st.subheader("Independent Studio Performance")
    top_indies = analysis_results.get('top_indies', {})
    
    if top_indies:
        # Show top indie studios table
        indie_data = []
        all_genres = set()
        
        for studio, data in top_indies.items():
            # Clean up studio name - remove category prefix
            studio_name = studio.split(' - ')[0] if ' - ' in studio else studio
            
            indie_data.append({
                'Studio': studio_name,
                'Shows': data['show_count'],
                'Networks': len(data['networks']),
                'Genres': len(data['genres'])
            })
            all_genres.update(data['genres'])
        
        if indie_data:
            df = pd.DataFrame(indie_data)
            st.dataframe(df, hide_index=True)
            
            st.write("**Genre Coverage**")
            genre_list = sorted(all_genres)
            st.write(", ".join(genre_list))
            
            # Show studio details
            st.write("\n**Studio Details**")
            for studio, data in top_indies.items():
                studio_name = studio.split(' - ')[0] if ' - ' in studio else studio
                with st.expander(studio_name):
                    st.write(f"**Shows:** {data['show_count']}")
                    st.write("**Networks:**")
                    st.write(", ".join(sorted(data['networks'])))
                    st.write("**Genres:**")
                    st.write(", ".join(sorted(data['genres'])))
                    if data['avg_rating']:
                        st.write(f"**Rating:** {data['avg_rating']:.1f}")

def render_studio_performance_dashboard(shows_df: pd.DataFrame) -> None:
    """Render the complete studio performance dashboard.
    
    Args:
        shows_df: DataFrame with show information
    """
    st.title("Studio Performance Dashboard")
    
    try:
        # Get analysis results once for all components
        analysis_results = analyze_studio_relationships(shows_df)
        
        # Render metrics at the top
        render_studio_metrics(analysis_results)
        
        # Create two columns for main content
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Studio relationship graph
            fig = create_studio_graph(shows_df)
            st.plotly_chart(fig, use_container_width=True)
            
            # Add note about graph
            st.info(
                "💡 The size of each node represents the number of shows. "
                "Connections indicate shared networks between studios."
            )
        
        with col2:
            # Create tabs for Studio Filter and Success Stories
            filter_tab, stories_tab = st.tabs(["Studio Filter", "Success Stories"])
            
            # Studio Filter tab
            with filter_tab:
                render_studio_filter(shows_df, analysis_results)
            
            # Success Stories tab
            with stories_tab:
                render_studio_success_stories(analysis_results)
                
    except Exception as e:
        st.error(f"Error in studio analysis: {str(e)}")
        st.exception(e)
