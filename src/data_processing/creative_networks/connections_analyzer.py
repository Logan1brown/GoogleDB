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
    # Merge show and team data and drop duplicates
    combined_df = pd.merge(
        shows_df[['show_name', 'network']],
        team_df,
        on='show_name'
    ).drop_duplicates(['show_name', 'network', 'name', 'roles'])
    
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

def find_partnerships(combined_df: pd.DataFrame, min_shows: int = 3, overlap_threshold: float = 0.8) -> Dict[str, Tuple[str, str]]:
    """Find partnerships based on shared shows.
    
    Args:
        combined_df: DataFrame with merged show and team data
        min_shows: Minimum number of shows for a creator to be considered
        overlap_threshold: Minimum percentage of shared shows to be considered partners
        
    Returns:
        Dictionary mapping creator names to their partner and team name
    """
    # Get shows per creator
    creator_shows = {}
    for name in combined_df['name'].unique():
        shows = set(combined_df[combined_df['name'] == name]['show_name'])
        if len(shows) >= min_shows:
            creator_shows[name] = shows
    
    # Find partnerships
    partnerships = {}
    processed = set()
    
    for creator1 in creator_shows:
        if creator1 in processed:
            continue
            
        shows1 = creator_shows[creator1]
        for creator2 in creator_shows:
            if creator2 <= creator1 or creator2 in processed:  # Use <= for consistent ordering
                continue
                
            shows2 = creator_shows[creator2]
            shared = len(shows1 & shows2)
            total = min(len(shows1), len(shows2))  # Use smaller total for threshold
            
            if shared / total >= overlap_threshold:
                team_name = f"{creator1} & {creator2}"
                partnerships[creator1] = (creator2, team_name)
                partnerships[creator2] = (creator1, team_name)
                processed.add(creator1)
                processed.add(creator2)
                break
    
    return partnerships

def identify_success_stories(shows_df: pd.DataFrame, team_df: pd.DataFrame) -> Dict[str, List[Dict]]:
    """Identify multi-network success stories and emerging collaborations.
    
    Args:
        shows_df: DataFrame with show information
        team_df: DataFrame with team member information
        
    Returns:
        Dictionary containing:
        - success_stories: List of creators/teams with 3+ shows
        - emerging_collaborations: List of creators/teams with 2 shows
        Each story contains:
        - creator_team: Name of individual or partnership
        - networks: List of networks worked with
        - show_count: Number of shows
        - roles: List of roles across shows
    """
    
    # Merge show and team data and drop duplicates
    combined_df = pd.merge(
        shows_df[['show_name', 'network']],
        team_df,
        on='show_name'
    ).drop_duplicates(['show_name', 'network', 'name', 'roles'])
    
    # Find partnerships based on shared shows
    partnerships = find_partnerships(combined_df, min_shows=3, overlap_threshold=0.8)
    
    # Group by creator to avoid duplicates
    success_stories = []
    processed = set()
    
    # Process each creator only once
    for creator in combined_df['name'].unique():
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
        show_count = team_shows['show_name'].nunique()
        
        # Only include creators who work across networks
        if len(networks) > 1:
            story = {
                'creator_team': team_name,
                'networks': sorted(networks),
                'show_count': show_count,
                'roles': sorted(team_shows['roles'].unique())
            }
            success_stories.append(story)
    
    # Separate stories into categories
    all_stories = success_stories.copy()
    success_stories = [s for s in all_stories if s['show_count'] >= 3 and len(s['networks']) >= 3]
    emerging_collabs = [s for s in all_stories if (
        (s['show_count'] == 2 and len(s['networks']) >= 2) or  # 2 shows across 2+ networks
        (s['show_count'] >= 3 and len(s['networks']) == 2)    # 3+ shows but only 2 networks
    )]
    
    # Sort both lists by number of networks first, then show count
    for stories in [success_stories, emerging_collabs]:
        stories.sort(key=lambda x: (len(x['networks']), x['show_count']), reverse=True)
    
    return {
        'success_stories': success_stories,
        'emerging_collaborations': emerging_collabs
    }

def analyze_network_connections(shows_df: pd.DataFrame, team_df: pd.DataFrame) -> Dict:
    logger.info(f"Shows DataFrame columns: {list(shows_df.columns)}")
    logger.info(f"Team DataFrame columns: {list(team_df.columns)}")
    logger.info(f"Shows DataFrame first row: {shows_df.iloc[0] if len(shows_df) > 0 else 'empty'}")
    logger.info(f"Team DataFrame first row: {team_df.iloc[0] if len(team_df) > 0 else 'empty'}")
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
