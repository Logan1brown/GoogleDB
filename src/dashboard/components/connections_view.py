"""Network Connections View.

Renders the network connections overview dashboard including:
- Force-directed network graph
- Success stories
- High-level metrics
"""

from typing import Dict, List
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import pandas as pd
import networkx as nx

def render_metrics(metrics: Dict) -> None:
    """Render high-level network metrics.
    
    Args:
        metrics: Dictionary containing network metrics
    """
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Networks",
            len(metrics['network_sizes']),
            help="Total number of networks in analysis"
        )
    
    with col2:
        total_talent = sum(metrics['talent_counts'].values())
        st.metric(
            "Total Creators",
            total_talent,
            help="Total number of unique creators"
        )
    
    with col3:
        st.metric(
            "Cross-Network %",
            f"{metrics['cross_network_activity']:.1f}%",
            help="Percentage of creators working with multiple networks"
        )

def create_network_graph(shows_df: pd.DataFrame, team_df: pd.DataFrame) -> go.Figure:
    """Create force-directed network graph.
    
    Args:
        shows_df: DataFrame with show information
        team_df: DataFrame with team member information
    
    Returns:
        Plotly figure with network graph
    """
    # Create network graph
    G = nx.Graph()
    
    # Get network sizes by unique individuals
    network_people = pd.merge(team_df, shows_df[['show_name', 'network']], on='show_name')
    network_sizes = network_people.groupby('network')['name'].nunique()
    major_networks = network_sizes[network_sizes > 5].index
    
    # Add nodes for major networks
    max_people = network_sizes[major_networks].max()
    for network in major_networks:
        people_count = network_sizes[network]
        # Scale size relative to maximum, targeting max radius of 60
        scaled_size = (people_count / max_people) * 60
        G.add_node(network, size=scaled_size, people_count=people_count)
    
    # Add edges for shared talent (only for major networks)
    merged = pd.merge(team_df, shows_df[['show_name', 'network']], on='show_name')
    merged = merged[merged['network'].isin(major_networks)]
    for name, group in merged.groupby('name'):
        networks = group['network'].unique()
        if len(networks) > 1:
            for i in range(len(networks)):
                for j in range(i+1, len(networks)):
                    if G.has_edge(networks[i], networks[j]):
                        G[networks[i]][networks[j]]['weight'] += 1
                    else:
                        G.add_edge(networks[i], networks[j], weight=1)
    
    # Get node positions using force-directed layout
    # k controls the distance between nodes (higher = more spread out)
    # iterations controls how long to run the layout algorithm
    # Weight the repulsion force by node size
    # This makes bigger nodes push away more strongly
    # Use edge weights based on node sizes to control spacing
    for edge in G.edges():
        n1, n2 = edge
        # Make edges between bigger nodes have less weight (more spacing)
        size_factor = (G.nodes[n1]['size'] + G.nodes[n2]['size']) / 2
        G[n1][n2]['weight'] = 1 / (size_factor + 1)
    
    # Try kamada_kawai_layout for less circular arrangement
    try:
        pos = nx.kamada_kawai_layout(G, weight='weight')
    except:
        # Fall back to spring layout if kamada_kawai fails
        pos = nx.spring_layout(G, k=8, iterations=150, weight='weight')
    
    # Create edges trace
    edge_x = []
    edge_y = []
    edge_weights = []
    
    for edge in G.edges(data=True):
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        edge_weights.append(edge[2]['weight'])
    
    edges_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='rgba(136, 136, 136, 0.2)'),  # Thinner and transparent
        hoverinfo='none',
        mode='lines'
    )
    
    # Create nodes trace
    node_x = []
    node_y = []
    node_text = []
    hover_text = []
    node_size = []
    
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        # Just network name for label
        node_text.append(node)
        # Creator count for hover
        hover_text.append(f"{node}<br>{G.nodes[node]['people_count']} creators")
        node_size.append(G.nodes[node]['size'])  # Size is already scaled
    
    nodes_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        hovertext=hover_text,
        text=node_text,
        textposition="top center",
        marker=dict(
            showscale=True,
            size=node_size,
            # Color nodes by number of creators
            color=[G.nodes[node]['people_count'] for node in G.nodes()],
            colorscale='Viridis',
            colorbar=dict(title='Creators'),
            line=dict(width=2, color='white')
        )
    )
    
    # Create figure
    fig = go.Figure(
        data=[edges_trace, nodes_trace],
        layout=go.Layout(
            title='Network Relationships',
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20,l=5,r=5,t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
        )
    )
    
    return fig

def render_success_stories(stories_data: Dict[str, List[Dict]]) -> None:
    """Render multi-network success stories and emerging collaborations.
    
    Args:
        stories_data: Dictionary containing success_stories and emerging_collaborations
    """
    # Create a single scrollable container for both sections
    stories_container = st.container(height=600)  # Taller to fit both sections
    with stories_container:
        # Success Stories
        st.subheader("Multi-Network Success Stories")
        for story in stories_data['success_stories']:
            with st.expander(f"{story['creator_team']} ({len(story['networks'])} networks)", expanded=False):
                st.write(f"**Networks:** {', '.join(sorted(story['networks']))}")
                st.write(f"**Shows:** {story['show_count']}")
        
        # Emerging Collaborations
        st.subheader("Emerging Multi-Network Collaborations")
        for story in stories_data['emerging_collaborations']:
            with st.expander(f"{story['creator_team']} ({len(story['networks'])} networks)", expanded=False):
                st.write(f"**Networks:** {', '.join(sorted(story['networks']))}")
                st.write(f"**Shows:** {story['show_count']}")

def render_network_filter(shows_df: pd.DataFrame, team_df: pd.DataFrame) -> None:
    """Render network and genre filtering interface to find creators.
    
    Args:
        shows_df: DataFrame with show information
        team_df: DataFrame with team member information
    """
    st.markdown("### Network & Genre Filter")
    st.markdown("Find creators by network and optionally filter by genre:")
    
    # Create two columns for filters
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**1. Select Networks**")
        # Get unique networks and sort them
        networks = sorted(shows_df['network'].unique())
        
        # Allow selecting multiple networks
        selected_networks = st.multiselect(
            "Networks (must work with all)",
            options=networks,
            default=None,
            help="Select 2 or more networks to find creators who have worked with all of them"
        )
    
    with col2:
        st.markdown("**2. Filter by Genre (Optional)**")
        # Get unique genres and sort them
        genres = sorted(shows_df['genre'].unique())
        
        # Allow selecting multiple genres
        selected_genres = st.multiselect(
            "Genres (must work in any)",
            options=genres,
            default=None,
            help="Further filter to creators who have worked in ANY selected genre"
        )
    
    # Show results if at least 2 networks are selected
    if len(selected_networks) >= 2:
        # Merge team and show data with both network and genre
        merged_df = pd.merge(
            team_df,
            shows_df[['show_name', 'network', 'genre']],
            on='show_name'
        )
        
        # Find creators who have worked with all selected networks
        matching_creators = []
        
        # Group by creator
        for creator in merged_df['name'].unique():
            creator_df = merged_df[merged_df['name'] == creator]
            creator_networks = creator_df['network'].unique()
            
            # Check if creator has worked with all selected networks
            if all(network in creator_networks for network in selected_networks):
                # If genres are selected, check if creator has worked in any of them
                if selected_genres and not any(g in creator_df['genre'].unique() for g in selected_genres):
                    continue
                
                # Get detailed information for this creator
                creator_info = {
                    'network_shows': {},
                    'genre_shows': {},
                    'shows': set()
                }
                
                # Collect shows by network
                for network in selected_networks:
                    network_shows = creator_df[
                        creator_df['network'] == network
                    ]['show_name'].unique()
                    creator_info['network_shows'][network] = list(network_shows)
                    creator_info['shows'].update(network_shows)
                
                # If genres selected, collect shows by genre
                if selected_genres:
                    for genre in selected_genres:
                        genre_shows = creator_df[
                            creator_df['genre'] == genre
                        ]['show_name'].unique()
                        if len(genre_shows) > 0:
                            creator_info['genre_shows'][genre] = list(genre_shows)
                
                matching_creators.append((creator, creator_info))
        
        # Display results in a scrollable container
        if matching_creators:
            st.markdown(f"**Found {len(matching_creators)} creators:**")
            results_container = st.container(height=400)
            with results_container:
                for creator, details in sorted(
                    matching_creators,
                    key=lambda x: len(x[1]['shows']),
                    reverse=True
                ):
                    with st.expander(f"**{creator}** ({len(details['shows'])} shows)"):
                        # Networks section
                        st.markdown("**Networks:**")
                        for network in selected_networks:
                            shows = details['network_shows'][network]
                            st.markdown(f"• {network}: {len(shows)} shows")
                            if len(shows) <= 3:  # Show all if 3 or fewer
                                for show in shows:
                                    st.markdown(f"  - {show}")
                        
                        # Genres section (if filtered)
                        if selected_genres and details['genre_shows']:
                            st.markdown("\n**Matching Genres:**")
                            for genre in selected_genres:
                                if genre in details['genre_shows']:
                                    shows = details['genre_shows'][genre]
                                    st.markdown(f"• {genre}: {len(shows)} shows")
                                    if len(shows) <= 3:  # Show all if 3 or fewer
                                        for show in shows:
                                            st.markdown(f"  - {show}")
        else:
            if selected_genres:
                st.warning("No creators found who have worked with all selected networks in any of the selected genres.")
            else:
                st.warning("No creators found who have worked with all selected networks.")

def render_network_connections_dashboard(
    shows_df: pd.DataFrame,
    team_df: pd.DataFrame,
    analysis_results: Dict
) -> None:
    """Render the complete network connections dashboard.
    
    Args:
        shows_df: DataFrame with show information
        team_df: DataFrame with team member information
        analysis_results: Results from network_connections analyzer
    """
    st.title("Network Connections Overview")
    
    # Render metrics
    render_metrics(analysis_results['metrics'])
    
    # Use columns for side-by-side layout
    col1, col2 = st.columns([3, 2])
    
    with col1:
        fig = create_network_graph(shows_df, team_df)
        st.plotly_chart(fig, use_container_width=True)
        
        st.info(
            "💡 The size of each node represents the number of shows. "
            "Connections indicate shared talent between networks."
        )
    
    with col2:
        # Create tabs for Network Filter and Success Stories
        filter_tab, stories_tab = st.tabs(["Network Filter", "Success Stories"])
        
        # Network Filter tab
        with filter_tab:
            render_network_filter(shows_df, team_df)
        
        # Success Stories tab
        with stories_tab:
            render_success_stories(analysis_results['success_stories'])
