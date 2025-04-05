"""
Unified View Analyzer Component.
Provides data analysis and transformations for the unified dashboard view.

=== CRITICAL COLUMN NAME DIFFERENCES ===
1. Show IDs: We use 'tmdb_id' as the ID column
2. Show Names:
   - shows sheet: uses 'shows' column
   - show_team sheet: uses 'show_name' column
NEVER try to normalize these column names - they must stay different.
"""

from typing import Dict, List, Optional
import pandas as pd
import logging
from data_processing.success_analysis.success_analyzer import SuccessAnalyzer

logger = logging.getLogger(__name__)

class UnifiedAnalyzer:
    """Analyzer for the unified dashboard view providing acquisition, packaging, and development insights."""
    
    def __init__(self, shows_df: pd.DataFrame, team_df: pd.DataFrame, success_analyzer: Optional[SuccessAnalyzer] = None):
        """Initialize the analyzer.
        
        Args:
            shows_df: DataFrame containing show information
            team_df: DataFrame containing team member information
            success_analyzer: Optional SuccessAnalyzer instance
        """
        # Validate required columns
        required_show_columns = ['shows', 'network', 'source_type', 'genre']
        required_team_columns = ['show_name', 'name', 'roles']
        
        missing_show_cols = [col for col in required_show_columns if col not in shows_df.columns]
        missing_team_cols = [col for col in required_team_columns if col not in team_df.columns]
        
        if missing_show_cols:
            msg = f"Missing required columns in shows_df: {missing_show_cols}"
            logger.error(msg)
            raise ValueError(msg)
            
        if missing_team_cols:
            msg = f"Missing required columns in team_df: {missing_team_cols}"
            logger.error(msg)
            raise ValueError(msg)
        
        # Create deep copies to avoid modifying original data
        self.shows_df = shows_df.copy(deep=True)
        self.team_df = team_df.copy(deep=True)
        
        # Initialize success analyzer if not provided
        self.success_analyzer = success_analyzer or SuccessAnalyzer()
        
        # Reset indices to ensure clean data
        self.shows_df = self.shows_df.reset_index(drop=True)
        self.team_df = self.team_df.reset_index(drop=True)
        
        logger.info(f"Initialized UnifiedAnalyzer with {len(self.shows_df)} shows and {len(self.team_df)} team members")
        
    def get_filtered_data(self, source_type: Optional[str] = None, genre: Optional[str] = None) -> pd.DataFrame:
        """Get filtered show data based on source type and genre.
        
        Args:
            source_type: Optional filter for source type (Original/Book/IP)
            genre: Optional filter for genre
            
        Returns:
            Filtered DataFrame
        """
        filtered_df = self.shows_df.copy()
        
        if source_type:
            filtered_df = filtered_df[filtered_df['source_type'] == source_type]
        if genre:
            filtered_df = filtered_df[filtered_df['genre'] == genre]
            
        return filtered_df
        
    def analyze_networks(self, filtered_df: pd.DataFrame) -> List[Dict]:
        """Analyze network performance for filtered shows.
        
        Args:
            filtered_df: Pre-filtered DataFrame of shows
            
        Returns:
            List of network analysis results
        """
        results = []
        for network in filtered_df['network'].unique():
            network_shows = filtered_df[filtered_df['network'] == network]
            
            # For now, just return basic stats since we don't have status data
            results.append({
                'network': network,
                'show_count': len(network_shows),
                'success_score': 75,  # Placeholder
                'renewal_rate': 80  # Placeholder
            })
            
        return sorted(results, key=lambda x: x['show_count'], reverse=True)
        
    def analyze_creators(self, filtered_df: pd.DataFrame) -> List[Dict]:
        """Analyze creator performance for filtered shows.
        
        Args:
            filtered_df: Pre-filtered DataFrame of shows
            
        Returns:
            List of creator analysis results
        """
        # Implementation will go here
        pass
        
    def analyze_pairings(self, filtered_df: pd.DataFrame) -> List[Dict]:
        """Analyze successful network-creator pairings.
        
        Args:
            filtered_df: Pre-filtered DataFrame of shows
            
        Returns:
            List of pairing analysis results
        """
        # Implementation will go here
        pass
        
    def get_package_suggestions(self, filtered_df: pd.DataFrame) -> List[Dict]:
        """Generate package suggestions based on success patterns.
        
        Args:
            filtered_df: Pre-filtered DataFrame of shows
            
        Returns:
            List of package suggestions
        """
        # Implementation will go here
        pass
