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
import os
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
        """
        Generate insights about market patterns, including calculating success scores and identifying top networks.
        """
        # Initialize tracking variables at the top to avoid NameError in all code paths
        top_success_network = None
        top_success_score = 0
        high_success_networks = 0
        top_networks = []
        if df is None or (hasattr(df, 'empty') and df.empty):
            return {
                "total_shows": 0,
                "total_networks": 0,
                "total_creatives": 0,
                "network_success": {},
                "top_networks": [],
                "network_concentration": 0,
                "top_3_networks": None,
                "vertical_integration": 0,
                "avg_success_score": 0,
                "top_success_network": None,
                "top_success_score": 0,
                "studio_insights": {}
            }

        # Fetch studio_list from Supabase
        from src.config.supabase_client import get_client
        supabase = get_client(use_service_key=True)
        studio_list_data = supabase.table('studio_list').select('*').execute()
        studio_list_df = pd.DataFrame(studio_list_data.data if studio_list_data and hasattr(studio_list_data, 'data') else [])

        # Build set of vertically integrated studios
        vertically_integrated_studios = set()
        if not studio_list_df.empty and 'name' in studio_list_df.columns and 'category' in studio_list_df.columns:
            vertically_integrated_studios = set(
                studio_list_df.loc[studio_list_df['category'].str.lower() == 'vertically integrated', 'name'].str.lower()
            )

        def is_vertically_integrated(row):
            studios = row['studio_names']
            if not isinstance(studios, list):
                return False
            return any(str(studio).lower() in vertically_integrated_studios for studio in studios)

        studio_vi_matches = df.apply(is_vertically_integrated, axis=1)
        vertical_integration = (studio_vi_matches.sum() / len(df)) * 100 if len(df) > 0 else 0

        top_networks = []
        top_success_network = 'None'
        top_success_score = 0
        high_success_networks = 0
        
        # Get success metrics for all shows
        try:
            success_metrics = self.success_analyzer.analyze_market(self.titles_df)
        except Exception as e:
            import traceback
            success_metrics = None
        if not success_metrics or 'titles' not in success_metrics:
            return {
                'vertical_integration': vertical_integration,
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

        # Minimal debug output for DataFrame shape and head
        import streamlit as st
        st.write('DEBUG: df.shape =', df.shape)
        st.write('DEBUG: df.head() =', df.head())
        
        # Filter to networks with enough shows
        min_shows = 3
        significant_networks = network_metrics[network_metrics['show_count'] >= min_shows]

        # Initialize network_success dictionary
        network_success = {}

        # Calculate success metrics per network
        for network in significant_networks['network_name']:
            # Get success scores for shows in this network from success_metrics
            network_shows = []
            network_scores = []
            
            # Robust: always compare as string for ID matching
            df_tmdb_id_str = df['tmdb_id'].astype(str)
            for show_id, show_data in success_metrics['titles'].items():
                show_id_str = str(show_id)
                show_idx = df_tmdb_id_str[df_tmdb_id_str == show_id_str].index
                show = df.loc[show_idx[0]] if len(show_idx) > 0 else None
                if show is not None and show['network_name'] == network:
                    network_shows.append(show)
                    network_scores.append(show_data['score'])
            
            if network_scores:  # Only process networks with valid scores
                avg_score = sum(network_scores) / len(network_scores)
                network_success[network] = avg_score
                logger.info(f"Network {network}: {len(network_scores)} valid shows, avg score {avg_score}")

        # Get studio insights using existing analyzer
        studio_insights = analyze_studio_relationships(df)
        
        # Calculate total creatives if team data is available
        total_creatives = 0
        if not self.team_df.empty and 'name' in self.team_df.columns:
            total_creatives = len(self.team_df['name'].unique())

        # Initialize tracking variables for top networks and scores
        top_success_network = None
        top_success_score = 0
        high_success_networks = 0
        top_networks = []

        # Track top networks
        for network, avg_score in network_success.items():
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
                'show_count': None  # If needed, can be refined
            })
        
        # If no top_success_network was found in the loop, pick the network with the highest score if any exist
        if (top_success_network == 'None' or not top_success_network) and network_success:
            sorted_networks = sorted(network_success.items(), key=lambda x: x[1], reverse=True)
            top_success_network, top_success_score = sorted_networks[0]

        return {
            'vertical_integration': vertical_integration,
            'avg_success_score': avg_success_score,
            'top_networks': top_networks,
            'high_success_networks': high_success_networks,
            'top_success_network': top_success_network,
            'top_success_score': top_success_score
        }
