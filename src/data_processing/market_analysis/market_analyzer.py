"""Market Analysis Module.

This module provides market overview analytics including network distribution and key metrics.

=== CRITICAL COLUMN NAMES ===
1. Show IDs: We use 'tmdb_id' as the ID column
2. Show Names: We use 'title' column everywhere
3. Network Names: We use 'network_name' column
4. Studio Names: We use 'studio_names' column
"""

import logging
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from ..success_analysis.success_analyzer import SuccessAnalyzer, SuccessConfig
from ..studio_performance.studio_analyzer import analyze_studio_relationships
from ..external.tmdb.tmdb_models import ShowStatus


logger = logging.getLogger(__name__)

class MarketAnalyzer:
    """Analyzer for market overview and network patterns."""
    
    def __init__(self, titles_df: pd.DataFrame = None, team_df: pd.DataFrame = None, network_df: pd.DataFrame = None, success_config: SuccessConfig = None):
        """Initialize the analyzer.
        
        Args:
            titles_df: Optional DataFrame for titles data
            team_df: Optional DataFrame for team data
            network_df: Optional DataFrame for network data
            success_config: Optional custom config for success calculation
        
        Raises:
            ValueError: If required columns are missing from titles_df
        """
        if titles_df is not None and team_df is not None and network_df is not None:
            self.titles_df = titles_df.copy(deep=True)
            self.team_df = team_df.copy(deep=True)
            self.network_df = network_df.copy(deep=True)
        else:
            from ..analyze_shows import ShowsAnalyzer
            shows_analyzer = ShowsAnalyzer()
            self.titles_df, self.team_df, self.network_df = shows_analyzer.fetch_data(force=True)
        
        # Create deep copies to avoid modifying original data
        # Only select columns we need, keeping studio_names for vertical integration
        needed_cols = ['title', 'network_name', 'tmdb_id', 'tmdb_seasons', 'tmdb_total_episodes', 
                      'tmdb_status', 'status_name', 'studio_names',
                      'writers', 'producers', 'directors', 'creators']
        available_cols = [col for col in needed_cols if col in self.titles_df.columns]
        self.titles_df = self.titles_df[available_cols].copy(deep=True)
        
        # Reset index to ensure clean data
        self.titles_df = self.titles_df.reset_index(drop=True)
        
        # Calculate average episodes per season for success scoring
        self.titles_df['tmdb_avg_eps'] = self.titles_df.apply(
            lambda x: x['tmdb_total_episodes'] / x['tmdb_seasons'] 
            if pd.notna(x['tmdb_total_episodes']) and pd.notna(x['tmdb_seasons']) and x['tmdb_seasons'] > 0 
            else None,
            axis=1
        )
        
        # Initialize success analyzer
        self.success_analyzer = SuccessAnalyzer(success_config)
        self.success_analyzer.initialize_data(self.titles_df)
        
        # Validate titles_df required columns
        required_shows_cols = ['network_name', 'tmdb_id', 'title', 'studio_names']
        missing_shows_cols = [col for col in required_shows_cols if col not in self.titles_df.columns]
        if missing_shows_cols:
            raise ValueError(f"Missing required columns in titles_df: {missing_shows_cols}")
        
        # Calculate success scores for all shows
        self.titles_df['success_score'] = self.titles_df.apply(self.success_analyzer.calculate_success, axis=1)
        
        # Log initial state
        logger.info("Market overview:")
        logger.info(f"Total shows: {len(self.titles_df)}")
        logger.info(f"Total networks: {len(self.titles_df['network_name'].unique())}")
        
        # Log team stats if available
        team_cols = ['writers', 'producers', 'directors', 'creators']
        if all(col in self.titles_df.columns for col in team_cols):
            total_creatives = set()
            for col in team_cols:
                total_creatives.update([
                    name for names in self.titles_df[col].dropna() 
                    for name in names if name
                ])
            logger.info(f"Total creatives: {len(total_creatives)}")
    
    def get_network_distribution(self) -> pd.Series:
        """Get distribution of shows across networks.
        
        Returns:
            Series with show counts by network
        """
        # Create a DataFrame with only scalar columns needed for this operation
        df = self.titles_df[['network_name']].copy()
        return df['network_name'].value_counts()
    
    def get_network_success_scores(self) -> pd.Series:
        """Get average success scores by network.
        
        Returns:
            Series of success scores indexed by network
        """
        # Create a DataFrame with only scalar columns needed for this operation
        df = self.titles_df[['network_name', 'success_score']].copy()
        return df.groupby('network_name')['success_score'].mean().sort_values(ascending=False)
    

    
    def generate_market_insights(self, df: pd.DataFrame = None) -> Dict[str, Any]:
        """Generate insights about market patterns.
        
        Args:
            df: Optional DataFrame to use instead of self.titles_df
            
        Returns:
            Dictionary containing market insights
        """
        # Only select columns we need to avoid unhashable list columns
        needed_cols = ['title', 'network_name', 'tmdb_id', 'tmdb_seasons', 'tmdb_total_episodes', 'tmdb_status', 'tmdb_avg_eps']
        df = df[needed_cols].copy()
        if df is None:
            df = self.titles_df
        
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
        df['network_name'] = df['network_name'].fillna('Unknown')
        df['network_name'] = df['network_name'].str.strip()
        df.loc[df['network_name'] == '', 'network_name'] = 'Unknown'
        
        # Create a separate DataFrame without list columns for groupby operations
        df_no_lists = df[['network_name']].copy()
        
        # Calculate basic metrics first
        total_shows = len(df)
        total_networks = len(df_no_lists['network_name'].unique())
        
        # Calculate network concentration (% of shows in top 3 networks)
        network_counts = df_no_lists['network_name'].value_counts()
        top_3_networks = network_counts.head(3)
        network_concentration = (top_3_networks.sum() / total_shows) * 100
        
        # Make sure we have studio_names column
        if 'studio_names' not in df.columns:
            logger.error(f"Missing studio_names column. Available columns: {df.columns.tolist()}")
            # Return basic metrics without studio-related insights
            return {
                'total_shows': total_shows,
                'total_networks': total_networks,
                'total_creatives': 0,
                'network_success': {},
                'top_networks': [],
                'network_concentration': network_concentration,
                'top_3_networks': top_3_networks,
                'vertical_integration': 0,
                'avg_success_score': 0,
                'top_success_network': 'None',
                'top_success_score': 0,
                'studio_insights': {}
            }
            
        # Calculate vertical integration
        logger.info("Starting vertical integration calculation...")
        
        # Calculate vertical integration
        
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
            studios = row['studio_names']
            network = str(row['network_name']).strip()
            
            # Handle non-list studios
            if not isinstance(studios, list):
                return False
            
            # Check each studio in the list
            for studio in studios:
                studio = str(studio).strip()
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
        def has_lookup_studio(studios):
            if not isinstance(studios, list):
                return False
            return any(any(parent.lower() in str(s).lower() for parent in LOOKUP_STUDIOS.keys()) for s in studios)
        
        lookup_studio_mask = df['studio_names'].apply(has_lookup_studio)
        lookup_studio_shows = df[lookup_studio_mask]
        
        if len(lookup_studio_shows) > 0:
            studio_network_matches = lookup_studio_shows.apply(is_vertically_integrated, axis=1)
            vertically_integrated_count = studio_network_matches.sum()
            vertical_integration = (vertically_integrated_count / len(lookup_studio_shows)) * 100
        top_networks = []
        top_success_network = 'None'
        top_success_score = 0
        high_success_networks = 0
        
        # Get success metrics for all shows
        success_metrics = self.success_analyzer.analyze_market(self.titles_df)
        if not success_metrics or 'titles' not in success_metrics:
            return {
                'vertical_integration': 0,
                'avg_success_score': 0,
                'top_networks': [],
                'high_success_networks': 0
            }
            
        # Calculate overall average success score
        total_score = 0
        num_shows = 0
        for show_id, show_data in success_metrics['titles'].items():
            if 'score' in show_data:
                total_score += show_data['score']
                num_shows += 1
        avg_success_score = total_score / num_shows if num_shows > 0 else 0
        
        # Calculate network-level metrics
        # Create a DataFrame with only scalar columns needed for this operation
        df_scalar = df[['network_name']].copy()
        network_metrics = df_scalar.groupby('network_name').size().reset_index()
        network_metrics.columns = ['network_name', 'show_count']
        
        # Filter to networks with enough shows
        min_shows = 3
        significant_networks = network_metrics[network_metrics['show_count'] >= min_shows]
        
        # Calculate success metrics per network
        for network in significant_networks['network_name']:
            # Get success scores for shows in this network from success_metrics
            network_shows = []
            network_scores = []
            
            # === CRITICAL: ID Column Name ===
            # We use 'tmdb_id' as the ID column, not 'id' or 'show_id'
            # This must match the column name in both shows sheet and TMDB metrics
            for show_id, show_data in success_metrics['titles'].items():
                # Convert show_id to int since tmdb_id is numeric
                show_id = int(show_id)
                show = df[df['tmdb_id'] == show_id].iloc[0] if len(df[df['tmdb_id'] == show_id]) > 0 else None
                if show is not None and show['network_name'] == network:
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
        
        # Calculate success rates and find top network
        
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
