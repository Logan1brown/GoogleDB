"""Studio Performance Analysis.

Analyzes studio performance metrics including:
- Network relationships
- Genre specialization
- Show volume and success rates
"""

from typing import Dict, List
import pandas as pd
import networkx as nx
from src.dashboard.utils.sheets_client import sheets_client
from src.data_processing.analyze_shows import shows_analyzer

def get_all_studios(shows_df: pd.DataFrame) -> pd.Series:
    """Extract all unique studios from the shows dataframe.
    Handles multiple studios per show by splitting on commas.
    Excludes studios prefixed with 'Other:' as they are not real studios.
    
    Args:
        shows_df: DataFrame with show information
        
    Returns:
        Series of unique studios with their show counts
    """
    # Split multiple studios and create a new series with one studio per row
    all_studios = shows_df['studio'].str.split(',').explode()
    
    # Clean up whitespace and remove empty studios
    all_studios = all_studios.str.strip()
    all_studios = all_studios[all_studios.notna() & (all_studios != '')]
    
    # Filter out studios prefixed with 'Other:'
    all_studios = all_studios[~all_studios.str.startswith('Other:', na=False)]
    
    # Count occurrences of each studio
    return all_studios.value_counts()

def get_shows_for_studio(shows_df: pd.DataFrame, studio: str) -> pd.DataFrame:
    """Get all shows for a specific studio, handling multiple studios per show.
    
    Args:
        shows_df: DataFrame with show information
        studio: Studio name to match
        
    Returns:
        DataFrame containing only shows that include this studio
    """
    # Create a series where each row is a studio-show pair
    studio_show_pairs = shows_df['studio'].str.split(',').explode().str.strip()
    
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

def analyze_studio_relationships(shows_df: pd.DataFrame) -> Dict:
    """Analyze relationships between studios and networks.
    
    Args:
        shows_df: DataFrame with show information
        
    Returns:
        Dictionary containing:
        - studio_sizes: Number of shows per studio
        - studio_genres: Genre distribution by studio
        - network_relationships: Network distribution by studio
        - total_studios: Total number of unique studios
        - top_studios: List of studios sorted by show count
    """
    # Get studio sizes by show count (handling multiple studios per show)
    studio_sizes = get_all_studios(shows_df)
    
    
    # Get genre distribution by studio (if genre column exists)
    studio_genres = {}
    if 'genre' in shows_df.columns:
        for studio in studio_sizes.index:
            studio_shows = get_shows_for_studio(shows_df, studio)
            if not studio_shows.empty:
                studio_genres[studio] = studio_shows['genre'].value_counts().to_dict()
    
    # Get network relationships (if network column exists)
    network_relationships = {}
    if 'network' in shows_df.columns:
        for studio in studio_sizes.index:
            studio_shows = get_shows_for_studio(shows_df, studio)
            if not studio_shows.empty:
                network_relationships[studio] = studio_shows['network'].value_counts().to_dict()
    
    # Load studio categories from live sheet
    try:
        # Get studio list data from the lookup table
        studio_list_data = sheets_client.get_all_values(shows_analyzer.LOOKUP_TABLES['studio'])
        if not studio_list_data:
            raise ValueError('No data found in studio_list sheet')
            
        # Convert to DataFrame
        headers = [col.lower().replace(' ', '_') for col in studio_list_data[0]]
        studio_categories = pd.DataFrame(studio_list_data[1:], columns=headers)
        
        # Get indies (large and mid-size)
        # The category is stored as "Independent,Large" or "Independent,Mid-Size"
        indies_mask = studio_categories['category'].fillna('').str.startswith('Independent', na=False)
        indie_df = studio_categories[indies_mask].copy()
        
        # Build list of indie studios including aliases
        indie_studios = set()
        for _, row in indie_df.iterrows():
            studio_name = row['studio']
            if pd.notna(studio_name):
                indie_studios.add(studio_name.strip())
                # Handle aliases if they exist
                if 'aliases' in row and pd.notna(row['aliases']):
                    aliases = [alias.strip() for alias in row['aliases'].split(',')]
                    indie_studios.update(aliases)
        
        # Filter to only valid studios that exist in our data
        indie_studios = [s for s in indie_studios if s and s.strip() and s in studio_sizes.index]
        
    except Exception as e:
        logger.error(f'Error loading studio categories: {e}')
        indie_studios = []
    indie_insights = {}
    
    for studio in indie_studios:
        shows = get_shows_for_studio(shows_df, studio)
        if not shows.empty:
            indie_insights[studio] = {
                'show_count': len(shows),
                'networks': shows['network'].unique().tolist(),
                'genres': shows['genre'].unique().tolist(),
                'avg_rating': shows['rating'].mean() if 'rating' in shows.columns else None
            }
    
    # Sort indie studios by show count
    sorted_indies = sorted(indie_insights.items(), key=lambda x: x[1]['show_count'], reverse=True)
    # Include all indies, not just top 10
    top_indies = dict(sorted_indies)
    
    return {
        'studio_sizes': studio_sizes.to_dict(),
        'studio_genres': studio_genres,
        'network_relationships': network_relationships,
        'total_studios': len(studio_sizes),
        'top_studios': studio_sizes.index.tolist(),
        'indie_insights': indie_insights,
        'top_indies': top_indies
    }

def get_studio_insights(shows_df: pd.DataFrame, studio: str) -> Dict:
    """Get detailed insights for a specific studio.
    
    Args:
        shows_df: DataFrame with show information
        studio: Name of studio to analyze
        
    Returns:
        Dictionary containing:
        - top_genres: Most common genres
        - network_partners: Networks worked with
        - show_details: List of shows and basic info
    """
    # Get all shows for this studio using exact matching
    studio_shows = get_shows_for_studio(shows_df, studio)
    
    # Work on a copy to avoid modifying original
    studio_shows = studio_shows.copy()
    
    # Get show details directly from the DataFrame
    show_details = []
    for _, row in studio_shows.iterrows():
        # Get title, network, and genre
        title = row.get('shows', '')
        network = row.get('network', 'Unknown Network')
        genre = row.get('genre', 'Unknown Genre')
        
        # Clean up values
        if pd.isna(title) or not isinstance(title, str):
            continue
        
        if pd.isna(network):
            network = 'Unknown Network'
        if pd.isna(genre):
            genre = 'Unknown Genre'
            
        # Only add shows that have a title
        if title.strip():
            show_details.append({
                'title': title.strip(),
                'network': network,
                'genre': genre
            })
    
    # Process shows and build insights
    genre_counts = {}
    network_counts = {}
    
    # Update counts for each show
    for show in show_details:
        genre = show['genre']
        network = show['network']
        
        # Count genres and networks
        genre_counts[genre] = genre_counts.get(genre, 0) + 1
        network_counts[network] = network_counts.get(network, 0) + 1
    
    return {
        'top_genres': genre_counts,
        'network_partners': network_counts,
        'show_details': show_details,
        'show_count': len(show_details)
    }
