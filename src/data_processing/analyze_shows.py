"""TV Titles Data Analysis Module.

This module provides comprehensive analysis of TV title data from Supabase,
using materialized views for efficient data retrieval and analysis.

Main components:
1. Data fetching from materialized views
2. Statistical analysis
3. Report generation using ydata-profiling
4. Results caching

=== CRITICAL COLUMN NAMES ===
Standardized column names used across all views:
1. Title Names: 'title' column
2. Network Names: 'network_name' column
3. Studio Names: 'studio_names' column
4. Status Names: 'status_name' column
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import os

import streamlit

import pandas as pd
from ydata_profiling import ProfileReport
from supabase import create_client

# Create singleton instance
shows_analyzer = None

logger = logging.getLogger(__name__)

# Initialize Supabase client with anon key
supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_ANON_KEY')  # Use anon key since we have proper view security
)

class ShowsAnalyzer:
    """Analyzer for TV titles data.
    
    This class handles fetching and analyzing TV title data from Supabase materialized views.
    Results are cached to avoid unnecessary recomputation.
    """
    
    # View names (using secure API views)
    VIEWS = {
        'titles': 'api_market_analysis',  # Use market_analysis view for market snapshot
        'networks': 'api_network_stats',
        'teams': 'api_show_team'  # Use show_team view for all team data
    }

    def __init__(self, cache_dir: Optional[str] = None):
        """Initialize the analyzer.
        
        Args:
            cache_dir: Directory to store cached results. Defaults to 'cache' in current dir.
        """
        self.cache_dir = Path(cache_dir) if cache_dir else Path.cwd() / 'cache'
        self.cache_dir.mkdir(exist_ok=True)
        
        self.shows_df: Optional[pd.DataFrame] = None
        self.team_df: Optional[pd.DataFrame] = None
        self.network_df: Optional[pd.DataFrame] = None
        self.last_fetch: Optional[datetime] = None

    def fetch_data(self, force: bool = False) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Fetch title data from Supabase secure API views.

        Args:
            force (bool): If True, bypass cache and fetch fresh data

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]: titles_df, team_df, network_df
        """
        if not force and all(df is not None for df in [self.shows_df, self.team_df, self.network_df]):
            return self.shows_df, self.team_df, self.network_df

        try:
            # Fetch from secure API views using anon key
            logger.info("Fetching data from api_market_analysis and api_show_team")
            titles_data = supabase.table(self.VIEWS['titles']).select('*').execute()
            network_data = supabase.table(self.VIEWS['networks']).select('*').execute()
            
            # Fetch team data with pagination
            team_data_list = []
            start = 0
            page_size = 1000
            while True:
                page = supabase.table(self.VIEWS['teams']).select('*').range(start, start + page_size - 1).execute()
                if not page.data:
                    break
                team_data_list.extend(page.data)
                if len(page.data) < page_size:
                    break
                start += page_size
                logger.info(f"Fetched {len(team_data_list)} team members so far...")
            
            if titles_data.data:
                logger.info("Converting to DataFrames")
                df = pd.DataFrame(titles_data.data)
                logger.info(f"Shows DataFrame shape: {df.shape}")
                logger.info(f"Shows DataFrame columns: {df.columns.tolist()}")
            # Convert to pandas DataFrames
            self.shows_df = pd.DataFrame(titles_data.data)
            self.network_df = pd.DataFrame(network_data.data)
            self.team_df = pd.DataFrame(team_data_list)
            
            # Log team data info
            if not self.team_df.empty:
                logger.info(f"Team DataFrame shape: {self.team_df.shape}")
                logger.info(f"Unique team members: {len(self.team_df['name'].unique())}")
            
            logger.debug(f"Network DataFrame columns: {self.network_df.columns.tolist()}")
            logger.debug(f"First row of network data: {self.network_df.iloc[0].to_dict() if not self.network_df.empty else 'Empty'}")
            logger.debug(f"Shows DataFrame columns: {self.shows_df.columns.tolist()}")
            
            logger.info(f"Loaded {len(self.shows_df)} titles, {len(self.team_df)} team records, and {len(self.network_df)} networks")
            
            self.last_fetch = datetime.now()
            logger.info("Data fetch completed successfully")
            
            # No indexing for now - will add when we need performance optimization
                
            # Return the indexed DataFrames (shows, team, network)
            return self.shows_df, self.team_df, self.network_df
            
        except Exception as e:
            logger.error(f"Error fetching data: {str(e)}")
            raise

    def convert_to_list(self, x):
        """Convert a value to a list.
        
        Args:
            x: Value to convert. Could be:
            - Python list
            - JSON array string
            - PostgreSQL array string
            - Single value
            
        Returns:
            List version of the value
        """
        try:
            if isinstance(x, list):
                return x
            if isinstance(x, str):
                # Handle PostgreSQL array format: {"item1","item2"}
                if x.startswith('{') and x.endswith('}'):
                    # Remove {} and split on commas, handling escaped quotes
                    items = x[1:-1].split(',')
                    return [item.strip('"') for item in items if item.strip()]
                # Handle JSON array format
                if x.startswith('[') and x.endswith(']'):
                    import ast
                    return ast.literal_eval(x)
                return [x]  # Single value
            if pd.isna(x) or x is None:
                return []
            return [str(x)]  # Convert other types to string
        except Exception as e:
            logger.warning(f"Error converting {x} to list: {e}")
            return []

    def clean_shows_data(self) -> None:
        """Apply any final transformations to the fetched data.
        
        Since we're using materialized views, most cleaning is handled at the database level.
        This method only handles any final transformations needed for analysis, such as:
        - Converting data types
        - Creating derived features
        - Handling array fields (studios, subgenres)
        """
        try:
            # Convert date fields
            logger.info("Data cleaning completed successfully")
            
        except Exception as e:
            logger.error(f"Error during data cleaning: {str(e)}")
            raise

    def generate_basic_stats(self) -> Dict[str, Any]:
        """Generate basic statistics about the shows.
        
        Returns:
            Dictionary containing basic statistics:
            - Total number of shows
            - Active shows
            - Shows by network
            - Shows by genre
            - Average team size
            etc.
        """
        if self.shows_df is None:
            self.fetch_data()
            
        # Clean data before generating stats
        # Data is already clean from the view
        
        try:
            # Basic show statistics from market analysis view
            stats = {
                'total_shows': len(self.shows_df),
                'active_shows': len(self.shows_df[self.shows_df['status'].str.lower() == 'active']),
                'genres': self.shows_df['genre'].value_counts().to_dict(),
                'status_breakdown': self.shows_df['status'].value_counts().to_dict(),
                'source_types': self.shows_df['source_type'].value_counts().to_dict(),  # Using source_type from view
                'avg_episodes': self.shows_df['tmdb_total_episodes'].mean() if 'tmdb_total_episodes' in self.shows_df.columns else 0
            }
            
            # Add network statistics
            if self.network_df is not None and len(self.network_df) > 0:
                # Group by network to get statistics
                network_stats = self.network_df.groupby('network').agg({
                    'title': 'count',
                    'status': lambda x: x.value_counts().to_dict(),
                    'genre': lambda x: x.value_counts().to_dict(),
                    'source_type': lambda x: x.value_counts().to_dict()
                }).reset_index()
                
                stats['networks'] = {}
                for _, row in network_stats.iterrows():
                    status_counts = row['status']
                    stats['networks'][row['network']] = {
                        'total_shows': row['title'],
                        'active_shows': status_counts.get('Active', 0),
                        'ended_shows': status_counts.get('Ended', 0),
                        'genres': row['genre'],
                        'source_types': row['source_type']  # Using source_type from view
                    }
                # For backward compatibility, provide simple network counts
                stats['network_counts'] = {net: data['total_shows'] 
                                         for net, data in stats['networks'].items()}
            
            # Add studio stats if available
            if 'studio' in self.shows_df.columns:
                studio_counts = self.shows_df['studio'].explode().value_counts()
                stats['studios'] = studio_counts.to_dict() if not studio_counts.empty else {}
            
            # Add team stats if available
            team_cols = ['writers', 'producers', 'directors', 'creators']
            if all(col in self.shows_df.columns for col in team_cols):
                # Count unique team members across all roles
                all_members = set()
                for role in team_cols:
                    members = self.shows_df[role].dropna().explode().unique()
                    all_members.update(members)
                
                # Calculate role counts
                role_counts = {}
                for role in team_cols:
                    count = self.shows_df[role].dropna().explode().nunique()
                    role_counts[role[:-1]] = count  # Remove 's' to get singular form
                
                stats['avg_team_size'] = len(all_members) / len(self.shows_df) if len(self.shows_df) > 0 else 0
                stats['total_team_members'] = len(all_members)
                stats['roles'] = role_counts
            else:
                stats['avg_team_size'] = 0
                stats['total_team_members'] = 0
                stats['roles'] = {}
        except Exception as e:
            logger.error(f"Error calculating basic stats: {str(e)}")
            stats = {
                'total_titles': 0,
                'active_shows': 0,
                'networks': {},
                'genres': {},
                'studios': {},
                'avg_episodes': 0,
                'avg_team_size': 0,
                'status_breakdown': {},
                'source_types': {}
            }
        
        # Add team role statistics
        if self.team_roles_df is not None and len(self.team_roles_df) > 0:
            stats['roles'] = self.team_roles_df['role_type'].value_counts().to_dict()
            stats['avg_team_size'] = len(self.team_roles_df) / len(self.shows_df) if len(self.shows_df) > 0 else 0
            stats['total_team_members'] = len(self.team_roles_df['name'].unique())
        else:
            stats['roles'] = {}
            stats['avg_team_size'] = 0
            stats['total_team_members'] = 0
            
        # Add date-based statistics
        if 'announced_date' in self.shows_df.columns:
            try:
                last_month = pd.Timestamp.now() - pd.DateOffset(months=1)
                stats['new_shows_last_month'] = len(self.shows_df[self.shows_df['announced_date'] >= last_month])
                
                # Titles by year
                stats['shows_by_year'] = self.shows_df['announced_date'].dt.year.value_counts().sort_index().to_dict()
                
                # Recent trends (last 12 months)
                last_year = datetime.now() - pd.DateOffset(months=12)
                recent_shows = self.shows_df[self.shows_df['announced_date'] >= last_year]
                stats['recent_trends'] = {
                    'total_shows': len(recent_shows),
                    'top_networks': recent_shows['network'].value_counts().head(5).to_dict(),
                    'top_genres': recent_shows['genre'].value_counts().head(5).to_dict()
                }
            except Exception as e:
                logger.error(f"Error processing dates: {e}")
                stats['new_titles_last_month'] = 0
                stats['titles_by_year'] = {}
                stats['recent_trends'] = {
                    'total_titles': 0,
                    'top_networks': {},
                    'top_genres': {}
                }
        else:
            stats['new_titles_last_month'] = 0
            stats['titles_by_year'] = {}
            stats['recent_trends'] = {
                'total_titles': 0,
                'top_networks': {},
                'top_genres': {}
            }
        
        logger.info(f"Analysis complete - {stats['total_shows']} shows processed")
        return stats

    def generate_profile_report(self, output_file: Optional[str] = None) -> None:
        """Generate comprehensive profile reports using ydata-profiling.
        
        This generates a report with:
        1. Show statistics and distributions
        2. Team member analysis
        3. Network and genre trends
        
        Args:
            output_file: Path to save the HTML report. If None, uses default path in cache_dir.
        """
        if self.shows_df is None or self.team_df is None:
            self.fetch_data()
            # Data is already clean from the view
            
        # Default output paths
        if output_file is None:
            base_path = self.cache_dir / f'profile_{datetime.now():%Y%m%d}'
            titles_output = base_path.with_name(f'{base_path.name}_titles.html')
            team_output = base_path.with_name(f'{base_path.name}_team.html')
        else:
            titles_output = Path(output_file)
            team_output = titles_output.with_name(f'{titles_output.stem}_team.html')
        
        logger.info('Generating profile reports...')
        
        try:
            # Prepare data for profile report
            shows_with_team = self.shows_df.copy()
            
            # Add team metrics if team data is available
            if self.team_df is not None and len(self.team_df) > 0:
                team_metrics = self.team_df.groupby('title').agg({
                    'name': 'count',
                    'role_name': lambda x: len(set([role for roles in x for role in roles]))
                }).rename(columns={
                    'name': 'team_size',
                    'role_name': 'unique_roles'
                })
                titles_with_team = titles_with_team.join(team_metrics, on='title')
            
            # Fill NaN values for better reporting
            numeric_cols = titles_with_team.select_dtypes(include=['int64', 'float64']).columns
            titles_with_team[numeric_cols] = titles_with_team[numeric_cols].fillna(0)
            
            # Create shows profile report
            shows_profile = ProfileReport(
                shows_with_team,
                title="TV Shows Analysis Report",
                explorative=True
            )
            
            # Save report if output file is specified
            if output_file:
                logger.info(f'Saving shows profile report to {output_file}')
                shows_profile.to_file(output_file)
            
            logger.info('Profile report generation completed')
            
        except Exception as e:
            logger.error(f'Error generating profile reports: {str(e)}')
            raise

# Create singleton instance for global use
shows_analyzer = ShowsAnalyzer()
