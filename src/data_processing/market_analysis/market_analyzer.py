"""Market Analysis Module.

This module provides market overview analytics including network distribution and key metrics.

=== CRITICAL COLUMN NAME DIFFERENCES ===
1. Show IDs: We use 'tmdb_id' as the ID column, not 'id' or 'show_id'
2. Show Names:
   - shows sheet: uses 'shows' column
   - show_team sheet: uses 'show_name' column
NEVER try to normalize these column names - they must stay different.
"""

import logging
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
import pandas as pd
import plotly.graph_objects as go

from ..success_analysis.success_analyzer import SuccessAnalyzer, SuccessConfig
from ..studio_performance.studio_analyzer import analyze_studio_relationships
from ..external.tmdb.tmdb_models import ShowStatus

logger = logging.getLogger(__name__)

class MarketAnalyzer:
    """Analyzer for market overview and network patterns."""
    
    def __init__(self, shows_df: pd.DataFrame, team_df: pd.DataFrame = None, success_config: SuccessConfig = None):
        """Initialize the analyzer.
        
        Args:
            shows_df: DataFrame containing show information
            team_df: Optional DataFrame containing team member information
            success_config: Optional custom config for success calculation
            
        Raises:
            ValueError: If required columns are missing from shows_df
        """
        # Create deep copies to avoid modifying original data
        self.shows_df = shows_df.copy(deep=True)
        self.team_df = pd.DataFrame() if team_df is None else team_df.copy(deep=True)
        
        # Reset indices to ensure clean data
        self.shows_df = self.shows_df.reset_index(drop=True)
        self.team_df = self.team_df.reset_index(drop=True)
        
        # Initialize success analyzer
        self.success_analyzer = SuccessAnalyzer(success_config)
        
        # === CRITICAL: Column Name Differences ===
        # 1. Show IDs: We use 'tmdb_id' as the ID column, not 'id' or 'show_id'
        # 2. Show Names:
        #    - shows sheet: uses 'shows' column
        #    - show_team sheet: uses 'show_name' column
        
        # Validate shows_df required columns
        required_shows_cols = ['network', 'studio', 'tmdb_id', 'shows']
        missing_shows_cols = [col for col in required_shows_cols if col not in self.shows_df.columns]
        if missing_shows_cols:
            raise ValueError(f"Missing required columns in shows_df: {missing_shows_cols}")
            
        # Calculate success scores for all shows
        self.shows_df['success_score'] = self.shows_df.apply(self.success_analyzer.calculate_success, axis=1)
            
        # Validate team_df required columns if provided
        if not self.team_df.empty:
            required_team_cols = ['show_name', 'name']
            missing_team_cols = [col for col in required_team_cols if col not in self.team_df.columns]
            if missing_team_cols:
                raise ValueError(f"Missing required columns in team_df: {missing_team_cols}")
        
        # Log initial state
        logger.info("Market overview:")
        logger.info(f"Total shows: {len(self.shows_df)}")
        logger.info(f"Total networks: {len(self.shows_df['network'].unique())}")
        if not self.team_df.empty and 'name' in self.team_df.columns:
            logger.info(f"Total creatives: {len(self.team_df['name'].unique())}")
    
    def get_network_distribution(self) -> pd.Series:
        """Get distribution of shows across networks.
        
        Returns:
            Series with network counts, sorted by count descending
        """
        return self.shows_df['network'].value_counts()
    
    def get_success_by_network(self) -> pd.Series:
        """Get average success score by network.
        
        Returns:
            Series with average success scores by network, sorted by score descending
        """
        return self.shows_df.groupby('network')['success_score'].mean().sort_values(ascending=False)
    

    
    def generate_market_insights(self, shows_df: pd.DataFrame = None) -> Dict[str, Any]:
        """Generate insights about market patterns.
        
        Args:
            shows_df: Optional DataFrame to use instead of self.shows_df
            
        Returns:
            Dictionary containing market insights
        """
        df = shows_df if shows_df is not None else self.shows_df
        
        # Validate DataFrame
        if len(df) == 0:
            return {
                'total_shows': 0,
                'total_networks': 0,
                'network_success': {},
                'top_networks': [],
                'network_concentration': 0,
                'vertical_integration': 0,
                'high_success_networks': 0,
                'avg_success_score': 0,
                'top_success_network': 'None',
                'top_success_score': 0
            }
        
        # Clean network data
        df['network'] = df['network'].fillna('Unknown')
        df['network'] = df['network'].str.strip()
        df.loc[df['network'] == '', 'network'] = 'Unknown'
        
        # Calculate basic metrics
        total_shows = len(df)
        total_networks = len(df['network'].unique())
        
        # Calculate network concentration (% of shows in top 3 networks)
        network_counts = df['network'].value_counts()
        top_3_networks = network_counts.head(3)
        network_concentration = (top_3_networks.sum() / total_shows) * 100
        
        # Calculate vertical integration using only major studios from lookup
        LOOKUP_STUDIOS = {
            'Warner Bros.': ['HBO', 'Max', 'TBS', 'TNT', 'The CW', 'Adult Swim', 'Cartoon Network'],
            'Disney': ['ABC', 'Disney+', 'FX', 'Hulu', 'National Geographic', 'Freeform', 'Disney Channel'],
            'NBCUniversal': ['NBC', 'USA Network', 'Syfy', 'Peacock', 'Bravo', 'E!', 'Universal Kids'],
            'Paramount': ['CBS', 'Paramount+', 'Showtime', 'MTV', 'Nickelodeon', 'Comedy Central', 'BET'],
            'Netflix': ['Netflix'],
            'Amazon': ['Prime Video', 'MGM+', 'Freevee'],
            'Apple': ['Apple TV+'],
            'Sony': ['Sony Pictures Television'],
            'AMC Networks': ['AMC', 'AMC+', 'BBC America', 'IFC', 'Sundance TV', 'WE tv'],
            'Lionsgate': ['Starz']
        }
        
        # Define which studios are vertically integrated
        VERTICALLY_INTEGRATED = {
            'Warner Bros.', 'Disney', 'NBCUniversal', 'Paramount',
            'Netflix', 'Amazon', 'Apple'
        }
        
        def is_vertically_integrated(row):
            studio = str(row['studio']).strip()
            network = str(row['network']).strip()
            
            # Only check vertically integrated studio relationships
            for parent_studio in VERTICALLY_INTEGRATED:
                if parent_studio.lower() in studio.lower():
                    networks = LOOKUP_STUDIOS[parent_studio]
                    # Check if any part of the network name matches
                    for net in networks:
                        if (net.lower() in network.lower() or 
                            network.lower() in net.lower()):
                            return True
            return False
            
        # Get shows from lookup studios (both vertically integrated and not)
        lookup_studio_mask = df['studio'].apply(lambda x: any(studio.lower() in str(x).lower() for studio in LOOKUP_STUDIOS.keys()))
        lookup_studio_shows = df[lookup_studio_mask]
        
        if len(lookup_studio_shows) > 0:
            # Log details about the calculation
            logger.info(f"Total shows in dataset: {len(df)}")
            logger.info(f"Shows from lookup studios: {len(lookup_studio_shows)}")
            
            studio_network_matches = lookup_studio_shows.apply(is_vertically_integrated, axis=1)
            vertically_integrated_count = studio_network_matches.sum()
            logger.info(f"Vertically integrated shows: {vertically_integrated_count}")
            
            # Get unique studios for debugging
            unique_studios = lookup_studio_shows['studio'].unique()
            logger.info(f"Unique studios found: {unique_studios}")
            
            vertical_integration = (vertically_integrated_count / len(lookup_studio_shows)) * 100
            logger.info(f"Vertical integration: {vertical_integration:.1f}%")
        else:
            vertical_integration = 0
            logger.warning("No shows found from lookup studios")
        
        # Calculate success metrics using success analyzer
        success_metrics = self.success_analyzer.analyze_market(df)
        logger.info(f"Success metrics: {success_metrics}")
        
        # Initialize network metrics
        network_success = {}
        top_networks = []
        top_success_network = 'None'
        top_success_score = 0
        high_success_networks = 0
        
        # Calculate overall average success score from all shows
        all_scores = [show_data['score'] for show_data in success_metrics['shows'].values()]
        avg_success_score = sum(all_scores) / len(all_scores) if all_scores else 0
        logger.info(f"Average success score across {len(all_scores)} shows: {avg_success_score}")
        
        # Calculate network-level metrics
        network_metrics = df.groupby('network').size().reset_index()
        network_metrics.columns = ['network', 'show_count']
        
        # Filter to networks with enough shows
        min_shows = 3
        significant_networks = network_metrics[network_metrics['show_count'] >= min_shows]
        
        # Calculate success metrics per network
        for network in significant_networks['network']:
            # Get success scores for shows in this network from success_metrics
            network_shows = []
            network_scores = []
            
            # === CRITICAL: ID Column Name ===
            # We use 'tmdb_id' as the ID column, not 'id' or 'show_id'
            # This must match the column name in both shows sheet and TMDB metrics
            for show_id, show_data in success_metrics['shows'].items():
                show = df[df['tmdb_id'] == show_id].iloc[0] if len(df[df['tmdb_id'] == show_id]) > 0 else None
                if show is not None and show['network'] == network:
                    network_shows.append(show)
                    network_scores.append(show_data['score'])
            
            if network_scores:  # Only process networks with valid scores
                avg_score = sum(network_scores) / len(network_scores)
                network_success[network] = avg_score
                logger.info(f"Network {network}: {len(network_scores)} valid shows, avg score {avg_score}")
                
                # Track top networks
                if avg_score > top_success_score:
                    top_success_score = avg_score
                    top_success_network = network
                
                # Count high success networks
                if avg_score > 80:
                    high_success_networks += 1
                    
                # Add to top networks list
                top_networks.append({
                    'network': network,
                    'success_score': avg_score,
                    'show_count': len(network_scores)
                })
        
        # Sort top networks by success score
        top_networks.sort(key=lambda x: x['success_score'], reverse=True)
        top_networks = top_networks[:5]
        
        logger.info(f"Calculated success rates for {len(network_success)} networks")
        logger.info(f"Top network: {top_success_network} ({top_success_score:.1f})")
        
        # Get studio insights using existing analyzer
        studio_insights = analyze_studio_relationships(df)
        
        # Calculate total creatives if team data is available
        total_creatives = 0
        if not self.team_df.empty and 'name' in self.team_df.columns:
            total_creatives = len(self.team_df['name'].unique())
        
        return {
            'total_shows': total_shows,
            'total_networks': total_networks,
            'total_creatives': total_creatives,
            'network_success': network_success,
            'top_networks': top_networks,
            'network_concentration': network_concentration,
            'vertical_integration': vertical_integration,
            'high_success_networks': high_success_networks,
            'avg_success_score': avg_success_score,
            'top_success_network': top_success_network,
            'top_success_score': top_success_score,
            'top_3_networks': top_3_networks.index.tolist(),
            'studio_insights': studio_insights
        }
