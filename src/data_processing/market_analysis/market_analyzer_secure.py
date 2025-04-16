"""Market Analysis Module using secure database views.

This module provides market overview analytics including network distribution and key metrics.
"""

import logging
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
import os
from dotenv import load_dotenv
import pandas as pd
import plotly.graph_objects as go
from supabase import create_client, Client

from ..success_analysis.success_analyzer import SuccessAnalyzer, SuccessConfig
from ..studio_performance.studio_analyzer import analyze_studio_relationships
from ..external.tmdb.tmdb_models import ShowStatus

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Supabase client
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_ANON_KEY')  # Use anon key for secure views

if not url or not key:
    raise ValueError("Missing Supabase credentials. Make sure SUPABASE_URL and SUPABASE_ANON_KEY are set in .env")

supabase: Client = create_client(url, key)

class MarketAnalyzer:
    """Analyzer for market overview and network patterns."""
    
    def __init__(self, shows_df: pd.DataFrame, success_config: SuccessConfig = None):
        """Initialize the analyzer.
        
        Args:
            shows_df: DataFrame from api_market_analysis view
            success_config: Optional custom config for success calculation
            
        Raises:
            ValueError: If required columns are missing from shows_df
        """
        # Create deep copy to avoid modifying original data
        self.shows_df = shows_df.copy(deep=True)
        
        # Reset index to ensure clean data
        self.shows_df = self.shows_df.reset_index(drop=True)
        
        # Initialize success analyzer
        self.success_analyzer = SuccessAnalyzer(success_config)
        self.success_analyzer.initialize_data(self.shows_df)
        
        # Validate required columns
        required_shows_cols = ['network_name', 'studio_names', 'tmdb_id', 'title']
        missing_shows_cols = [col for col in required_shows_cols if col not in self.shows_df.columns]
        if missing_shows_cols:
            raise ValueError(f"Missing required columns in shows_df: {missing_shows_cols}")
            
        # Calculate average episodes per season
        self.shows_df['tmdb_avg_eps'] = self.shows_df.apply(
            lambda x: x['tmdb_total_episodes'] / x['tmdb_seasons'] if pd.notna(x['tmdb_total_episodes']) and pd.notna(x['tmdb_seasons']) and x['tmdb_seasons'] > 0 else None,
            axis=1
        )
        
        # Calculate success scores for all shows
        self.shows_df['success_score'] = self.shows_df.apply(self.success_analyzer.calculate_success, axis=1)
        
        # Log initial state
        logger.info("Market overview:")
        logger.info(f"Total shows: {len(self.shows_df)}")
        logger.info(f"Total networks: {len(self.shows_df['network_name'].unique())}")
        
        # Log team stats if available
        team_cols = ['writers', 'producers', 'directors', 'creators']
        if all(col in self.shows_df.columns for col in team_cols):
            total_creatives = set()
            for col in team_cols:
                total_creatives.update([
                    name for names in self.shows_df[col].dropna() 
                    for name in names if name
                ])
            logger.info(f"Total creatives: {len(total_creatives)}")
    
    def get_network_distribution(self) -> pd.Series:
        """Get distribution of shows across networks.
        
        Returns:
            Series with network counts, sorted by count descending
        """
        return self.shows_df['network_name'].value_counts()
    
    def get_success_by_network(self) -> pd.Series:
        """Get average success score by network.
        
        Returns:
            Series with average success scores by network, sorted by score descending
        """
        return self.shows_df.groupby('network_name')['success_score'].mean().sort_values(ascending=False)
    
    def generate_market_insights(self, shows_df: pd.DataFrame = None) -> Dict[str, Any]:
        """Generate insights about market patterns.
        
        Args:
            shows_df: Optional DataFrame to use instead of self.shows_df
            
        Returns:
            Dictionary containing market insights
        """
        df = shows_df if shows_df is not None else self.shows_df
        
        # Debug: print column names
        logger.info(f"DataFrame columns: {df.columns.tolist()}")
        
        # Validate DataFrame
        if len(df) == 0:
            return {
                'total_shows': 0,
                'total_networks': 0,
                'network_success': {},
                'top_networks': [],
                'top_3_networks': pd.Series(),
                'network_concentration': 0,
                'vertical_integration': 0,
                'high_success_networks': 0,
                'avg_success_score': 0,
                'top_success_network': 'None',
                'top_success_score': 0
            }
        
        # Clean up network values
        df['network_name'] = df['network_name'].fillna('Unknown')
        df['network_name'] = df['network_name'].str.strip()
        df.loc[df['network_name'] == '', 'network_name'] = 'Unknown'
        
        # Calculate basic metrics
        total_shows = len(df)
        total_networks = len(df['network_name'].unique())
        
        # Calculate network concentration (% of shows in top 3 networks)
        network_counts = df['network_name'].value_counts()
        top_3_networks = network_counts.head(3)
        network_concentration = (top_3_networks.sum() / total_shows) * 100
        
        # Calculate vertical integration based on studio categories
        def is_vertically_integrated(row):
            """Check if show has any studios with 'vertically integrated' category."""
            # Handle empty or null arrays
            if not isinstance(row['studio_names'], list) or not row['studio_names']:
                return False
                
            logger.info(f"Checking studios for show: {row['title']}")
            logger.info(f"Studio names: {row['studio_names']}")
            
            # Check if any studio categories contain 'Vertically Integrated'
            if not isinstance(row['studio_categories'], list) or not row['studio_categories']:
                return False
                
            # Flatten the array of arrays into a single set
            all_categories = set()
            for category_array in row['studio_categories']:
                if isinstance(category_array, list):
                    all_categories.update(category_array)
                    
            logger.info(f"All categories for {row['title']}: {all_categories}")
            return 'Vertically Integrated' in all_categories
            
            return False
        
        vertical_integration = (df.apply(is_vertically_integrated, axis=1).sum() / total_shows) * 100
        
        # Calculate success metrics
        network_success = df.groupby('network_name')['success_score'].mean().to_dict()
        high_success_threshold = df['success_score'].mean() + df['success_score'].std()
        high_success_networks = len(df[df['success_score'] >= high_success_threshold]['network_name'].unique())
        
        avg_success = df['success_score'].mean()
        top_success_network = df.groupby('network_name')['success_score'].mean().idxmax()
        top_success_score = df.groupby('network_name')['success_score'].mean().max()
        
        return {
            'total_shows': total_shows,
            'total_networks': total_networks,
            'network_success': network_success,
            'top_networks': top_3_networks.index.tolist(),
            'top_3_networks': top_3_networks,
            'network_concentration': network_concentration,
            'vertical_integration': vertical_integration,
            'high_success_networks': high_success_networks,
            'avg_success_score': avg_success,
            'top_success_network': top_success_network,
            'top_success_score': top_success_score
        }
