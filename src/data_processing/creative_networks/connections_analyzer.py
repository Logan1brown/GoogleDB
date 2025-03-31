"""Network Connections Analyzer.

Analyzes network relationships and success stories for the overview dashboard.
Focuses on high-level metrics and network-to-network relationships.
"""

from typing import Dict, List, Set, Tuple
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def analyze_network_metrics(shows_df: pd.DataFrame, team_df: pd.DataFrame) -> Dict:
    """Analyze high-level network metrics.
    
    Args:
        shows_df: DataFrame with show information
        team_df: DataFrame with team member information
        
    Returns:
        Dictionary containing:
        - network_sizes: Number of shows per network
        - talent_counts: Number of creators per network
        - cross_network_activity: % of creators working across networks
    """
    # Merge show and team data
    combined_df = pd.merge(
        team_df,
        shows_df[['show_name', 'network']],
        on='show_name'
    )
    
    # Calculate network sizes
    network_sizes = shows_df['network'].value_counts().to_dict()
    
    # Calculate talent counts
    talent_counts = combined_df.groupby('network')['name'].nunique().to_dict()
    
    # Calculate cross-network activity
    creator_networks = combined_df.groupby('name')['network'].nunique()
    multi_network = (creator_networks > 1).sum()
    total_creators = len(creator_networks)
    cross_network_pct = (multi_network / total_creators) * 100 if total_creators > 0 else 0
    
    return {
        'network_sizes': network_sizes,
        'talent_counts': talent_counts,
        'cross_network_activity': cross_network_pct
    }

def identify_success_stories(shows_df: pd.DataFrame, team_df: pd.DataFrame) -> List[Dict]:
    """Identify multi-network success stories.
    
    Args:
        shows_df: DataFrame with show information
        team_df: DataFrame with team member information
        
    Returns:
        List of dictionaries containing success stories:
        - creator_team: Name of individual or partnership
        - networks: List of networks worked with
        - show_count: Number of shows
        - roles: List of roles across shows
    """
    # Known creative partnerships
    partnerships = {
        'Seth Rogen': ('Evan Goldberg', 'Seth Rogen & Evan Goldberg'),
        'Evan Goldberg': ('Seth Rogen', 'Seth Rogen & Evan Goldberg'),
        'John Davis': ('John Fox', 'John Davis & John Fox'),
        'John Fox': ('John Davis', 'John Davis & John Fox')
    }
    
    # Merge show and team data
    combined_df = pd.merge(
        team_df,
        shows_df[['show_name', 'network']],
        on='show_name'
    )
    
    success_stories = []
    processed = set()
    
    for _, row in combined_df.iterrows():
        creator = row['name']
        if creator in processed:
            continue
            
        # Check if part of partnership
        if creator in partnerships:
            partner, team_name = partnerships[creator]
            processed.add(creator)
            processed.add(partner)
            
            # Get combined shows for partnership
            team_shows = combined_df[
                combined_df['name'].isin([creator, partner])
            ]
        else:
            team_name = creator
            team_shows = combined_df[combined_df['name'] == creator]
        
        networks = team_shows['network'].unique()
        if len(networks) > 1:  # Only include multi-network stories
            success_stories.append({
                'creator_team': team_name,
                'networks': sorted(networks),
                'show_count': team_shows['show_name'].nunique(),
                'roles': sorted(team_shows['role'].unique())
            })
    
    # Sort by show count
    success_stories.sort(key=lambda x: x['show_count'], reverse=True)
    return success_stories

def analyze_network_connections(shows_df: pd.DataFrame, team_df: pd.DataFrame) -> Dict:
    """Main analysis function for network connections dashboard.
    
    Args:
        shows_df: DataFrame with show information
        team_df: DataFrame with team member information
        
    Returns:
        Dictionary containing all metrics and data for the dashboard:
        - metrics: High-level network metrics
        - success_stories: Multi-network success stories
    """
    metrics = analyze_network_metrics(shows_df, team_df)
    success_stories = identify_success_stories(shows_df, team_df)
    
    return {
        'metrics': metrics,
        'success_stories': success_stories
    }
