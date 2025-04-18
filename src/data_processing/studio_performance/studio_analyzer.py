"""Studio Performance Analysis.

Analyzes studio performance metrics including:
- Network relationships
- Genre specialization
- Show volume and success rates
"""

from typing import Dict, List
import pandas as pd
import networkx as nx
import logging
logger = logging.getLogger(__name__)
# No longer using Google Sheets
# from src.dashboard.utils.sheets_client import sheets_client


def filter_active_shows(shows_df: pd.DataFrame) -> pd.DataFrame:
    """Filter for active shows if the active column exists.
    
    Args:
        shows_df: DataFrame with show information
        
    Returns:
        DataFrame with only active shows if active column exists,
        otherwise returns original DataFrame
    """
    if 'active' in shows_df.columns:
        return shows_df[shows_df['active']].copy()
    return shows_df


def get_all_studios(shows_df: pd.DataFrame) -> pd.Series:
    """Get all unique studios and their show counts.
    
    Args:
        shows_df: DataFrame with show data
        
    Returns:
        Series with studio names as index and show counts as values
    """
    # Explode studio_names to get one row per show-studio combination
    studio_shows = shows_df.explode('studio_names')
    studio_names = studio_shows['studio_names']
    studio_names = studio_names[studio_names.notna() & (studio_names != '')]
    
    # Filter out studios prefixed with 'Other:'
    studio_names = studio_names[~studio_names.str.startswith('Other:', na=False)]
    
    # Count each studio once per show by dropping duplicates
    studio_shows = pd.DataFrame({'studio_names': studio_names, 'title': studio_shows['title']})
    studio_shows = studio_shows.drop_duplicates()
    
    # Count occurrences of each studio
    return studio_shows['studio_names'].value_counts()

def get_shows_for_studio(shows_df: pd.DataFrame, studio: str) -> pd.DataFrame:
    """Get all shows for a specific studio, handling multiple studios per show.
    
    Args:
        shows_df: DataFrame with show information
        studio: Studio name to match
        
    Returns:
        DataFrame containing only shows that include this studio
    """
    # Filter for active shows if column exists
    shows_df = filter_active_shows(shows_df)
    
    # Get indices of shows that have this studio in their studio_names list
    if 'studio_names' in shows_df.columns:
        matching_indices = shows_df[
            shows_df['studio_names'].apply(lambda x: studio in x if isinstance(x, list) else False)
        ].index
    else:
        # Handle legacy format with comma-separated studio string
        studio_show_pairs = shows_df['studio_names'].str.split(',').explode().str.strip()
        # Don't match empty studio names
        if not studio or not studio.strip():
            return pd.DataFrame()
            
        # Look for both exact match and 'Other: <studio>' format
        matching_indices = studio_show_pairs[
            (studio_show_pairs == studio) |
            (studio_show_pairs == f'Other: {studio}')
        ].index
    
    # Get matching shows
    matching_shows = shows_df.loc[matching_indices]
    
    return matching_shows

def analyze_studio_relationships(shows_df: pd.DataFrame, studio_categories_df: pd.DataFrame) -> Dict:
    """Analyze relationships between studios and networks.
    
    Args:
        shows_df: DataFrame with show information including:
            - studio_names: List of studios for each show
            - network_name: Network name
            - active: Whether the show is active
            - status_name: Show status (e.g. Active, Cancelled)
            - tmdb_seasons: Number of seasons
            - tmdb_total_episodes: Total episodes
        
    Returns:
        Dictionary containing:
        - studio_sizes: Number of shows per studio
        - network_relationships: Network distribution by studio
        - total_studios: Total number of unique studios
        - top_studios: List of studios sorted by show count
        - studio_success: Success metrics by studio
    """
    # Filter for active shows if column exists
    shows_df = filter_active_shows(shows_df)
    
    # Get studio sizes by show count (handling multiple studios per show)
    # First get unique studio-show combinations
    studio_shows = shows_df.explode('studio_names')
    studio_shows = studio_shows[studio_shows['studio_names'].notna() & (studio_shows['studio_names'] != '')]
    studio_shows = studio_shows[~studio_shows['studio_names'].str.startswith('Other:', na=False)]
    
    # Group by studio to get unique shows per studio
    studio_show_pairs = studio_shows[['studio_names', 'title']].groupby('studio_names')['title'].unique()
    
    # Count shows per studio
    studio_sizes = studio_show_pairs.apply(len)
    
    # Get network relationships
    network_relationships = {}
    for studio in studio_sizes.index:
        studio_shows = get_shows_for_studio(shows_df, studio)
        if not studio_shows.empty:
            network_relationships[studio] = studio_shows['network_name'].value_counts().to_dict()
    
    # Calculate success metrics by studio
    studio_success = {}
    for studio in studio_sizes.index:
        studio_shows = get_shows_for_studio(shows_df, studio)
        if not studio_shows.empty:
            # Calculate success metrics
            avg_seasons = studio_shows['tmdb_seasons'].mean()
            avg_episodes = studio_shows['tmdb_total_episodes'].mean()
            
            # Get show status distribution
            status_dist = studio_shows['status_name'].value_counts().to_dict()
            
            # Calculate active show percentage if active column exists
            success_metrics = {
                'avg_seasons': avg_seasons,
                'avg_episodes': avg_episodes,
                'status_distribution': status_dist,
                'total_shows': len(studio_shows)
            }
            
            if 'active' in studio_shows.columns:
                success_metrics.update({
                    'active_percentage': 100.0,  # All shows are active since we filtered at the start
                    'active_shows': len(studio_shows)
                })
            
            studio_success[studio] = success_metrics
    
    # Sort studios by total shows
    sorted_studios = sorted(
        studio_success.items(),
        key=lambda x: x[1]['total_shows'],
        reverse=True
    )
    top_studios = [studio for studio, _ in sorted_studios]
    
    # Create map of studio categories
    studio_categories = {}
    
    for _, row in studio_categories_df.iterrows():
        categories = []
        cat = row.get('category')
        
        # Handle both list and string formats
        if isinstance(cat, list):
            # If it's already a list, use it directly
            categories = cat
        elif isinstance(cat, str):
            # If it's a string, split by comma
            categories = [c.strip() for c in cat.split(',')]
        
        # Check for Independent in categories
        if any(c.strip() == 'Independent' for c in categories):
            # Use studio column from studio_list table
            studio_categories[row['studio']] = 'Independent'
    
    # Identify indie studios based on category
    indie_studios = {}
    for studio, metrics in studio_success.items():
        if studio in studio_categories:
            logger.info(f"Found indie studio in list: {studio}")
            # Get shows for this indie studio
            studio_shows = get_shows_for_studio(shows_df, studio)
            if len(studio_shows) >= 2:  # Only include if they have 2+ shows
                indie_studios[studio] = {
                    'show_count': len(studio_shows),
                    'shows': studio_shows['title'].tolist(),
                    'networks': studio_shows['network_name'].value_counts().to_dict()
                }
    
    # Convert studio_sizes to dict and get sorted studios
    studio_sizes_dict = {}
    for studio, count in studio_sizes.items():
        if isinstance(studio, str):  # Only include string keys
            studio_sizes_dict[studio] = count
    
    # Sort studios by show count
    sorted_studios = sorted(
        studio_sizes_dict.items(),
        key=lambda x: x[1],
        reverse=True
    )
    top_studios = [studio for studio, _ in sorted_studios]
    
    return {
        'studio_sizes': studio_sizes_dict,
        'network_relationships': network_relationships,
        'total_studios': len(studio_sizes),
        'top_studios': top_studios,
        'studio_success': studio_success,
        'indie_studios': indie_studios
    }

def get_studio_insights(shows_df: pd.DataFrame, studio: str) -> Dict:
    """Get detailed insights for a specific studio.
    
    Args:
        shows_df: DataFrame with show information
        studio: Studio to analyze
        
    Returns:
        Dictionary containing:
        - network_partners: Network distribution
        - show_details: Basic show information
        - success_metrics: Success rate metrics
    """
    # Filter for active shows if column exists
    shows_df = filter_active_shows(shows_df)
    
    # Get all shows for this studio
    studio_shows = get_shows_for_studio(shows_df, studio)
    if studio_shows.empty:
        return {
            'error': f'No shows found for studio: {studio}'
        }
        
    # Get network partners with show counts
    network_partners = studio_shows['network_name'].value_counts().to_dict()
        
    # Calculate success metrics
    success_metrics = {
        'total_shows': len(studio_shows),
        'avg_seasons': studio_shows['tmdb_seasons'].mean(),
        'avg_episodes': studio_shows['tmdb_total_episodes'].mean(),
        'status_distribution': studio_shows['status_name'].value_counts().to_dict()
    }
    
    # Add active metrics if column exists
    if 'active' in studio_shows.columns:
        success_metrics.update({
            'active_shows': len(studio_shows),  # All shows are active since we filtered at the start
            'active_percentage': 100.0
        })
        
    # Get basic show info
    show_details = []
    for _, show in studio_shows.iterrows():
        show_info = {
            'title': show['title'],
            'network_name': show['network_name'],  # Changed from 'network' to match standardized names
            'status': show['status_name'],
            'seasons': show['tmdb_seasons'],
            'episodes': show['tmdb_total_episodes'],
            'genre': show.get('genre', 'Unknown')  # Add genre which studio_view expects
        }
        if 'active' in show:
            show_info['active'] = show['active']
        if 'tmdb_last_air_date' in show:
            show_info['last_air_date'] = show['tmdb_last_air_date']
        show_details.append(show_info)
    
    # Get genre distribution
    genres = []
    for show in studio_shows.iterrows():
        if 'genre' in show[1]:
            genres.extend([g.strip() for g in show[1]['genre'].split(',')])
    top_genres = pd.Series(genres).value_counts().to_dict() if genres else {}
    
    return {
        'network_partners': network_partners,
        'show_details': show_details,
        'success_metrics': success_metrics,
        'show_count': len(studio_shows),  # Add show count which studio_view expects
        'top_genres': top_genres  # Add genre distribution which studio_view expects
    }
