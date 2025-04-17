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

__all__ = ['ShowsAnalyzer']

import logging
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import os

import streamlit as st

import pandas as pd
from ydata_profiling import ProfileReport
from supabase import create_client

logger = logging.getLogger(__name__)

# Import the centralized Supabase client
from src.config.supabase_client import get_client

class ShowsAnalyzer:
    """Analyzer for TV titles data.
    
    This class handles fetching and analyzing TV title data from Supabase materialized views.
    Results are cached to avoid unnecessary recomputation.
    """
    
    # View names
    VIEWS = {
        'titles': 'api_market_analysis',  # Use market analysis view for market snapshot
        'networks': 'api_network_stats',
        'team': 'api_show_team'  # Team member data (correct key)
    }
    
    def __init__(self, cache_dir: Optional[str] = None):
        """Initialize the analyzer.
        
        Args:
            cache_dir: Directory to store cached results. Defaults to 'cache' in current dir.
        """
        try:
            self.cache_dir = Path(cache_dir) if cache_dir else Path.cwd() / 'cache'
            self.cache_dir.mkdir(exist_ok=True)
            
            self.titles_df: Optional[pd.DataFrame] = None
            self.team_df: Optional[pd.DataFrame] = None
            self.network_df: Optional[pd.DataFrame] = None
            self.last_fetch: Optional[datetime] = None
        except Exception as e:
            logger.error(f"Error during initialization: {str(e)}")
            raise

    def fetch_data(self, force: bool = False) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Fetch title data from Supabase secure API views.
        
        Args:
            force (bool): If True, bypass cache and fetch fresh data

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]: titles_df, team_df, network_df
        """
        import streamlit as st
        if not force and self.titles_df is not None and self.team_df is not None and self.network_df is not None:
            return self.titles_df, self.team_df, self.network_df

        try:
            # Get Supabase client with service key for full access
            supabase = get_client(use_service_key=True)
            
            if supabase is None:
                raise ValueError("Supabase client not initialized. Check your environment variables.")
                
            # Fetch from secure API views
            titles_data = supabase.table(self.VIEWS['titles']).select('*').execute()
            network_data = supabase.table(self.VIEWS['networks']).select('*').execute()
            # Fetch all pages for team data (pagination)
            all_team_rows = []
            start = 0
            page_size = 1000
            page_num = 1
            while True:
                page = supabase.table(self.VIEWS['team']).select('*').range(start, start + page_size - 1).execute()
                if not page.data:
                    break
                all_team_rows.extend(page.data)
                if len(page.data) < page_size:
                    break
                start += page_size
                page_num += 1
            self.team_df = pd.DataFrame(all_team_rows)

            # Create DataFrames from the other data
            self.titles_df = pd.DataFrame(titles_data.data if titles_data and hasattr(titles_data, 'data') else [])
            self.network_df = pd.DataFrame(network_data.data if network_data and hasattr(network_data, 'data') else [])
            
            # Store fetch time
            self.last_fetch = datetime.now()
            
            return self.titles_df, self.team_df, self.network_df
        except Exception as e:
            logger.error(f"Error fetching data: {str(e)}")
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

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
        if self.titles_df is None:
            self.fetch_data()
            
        # Clean data before generating stats
        # Data is already clean from the view
        
        try:
            # Basic show statistics from market analysis view
            stats = {
                'total_shows': len(self.titles_df),
                'active_shows': len(self.titles_df[self.titles_df['status_name'].str.lower() == 'active']),
                'genres': self.titles_df['genre'].value_counts().to_dict() if 'genre' in self.titles_df.columns else {},
                'status_breakdown': self.titles_df['status_name'].value_counts().to_dict(),
                'source_types': self.titles_df['source_type'].value_counts().to_dict() if 'source_type' in self.titles_df.columns else {},
                'avg_episodes': self.titles_df['tmdb_total_episodes'].mean() if 'tmdb_total_episodes' in self.titles_df.columns else 0
            }
            
            # Add network statistics
            # Get network statistics from network_df
            if self.network_df is not None and len(self.network_df) > 0:
                # Get unique networks from network_df since it has the complete list
                unique_networks = self.network_df['network_name'].unique()
                stats['networks'] = {}
                
                # For each unique network, calculate stats from titles_df
                for network in unique_networks:
                    network_titles = self.titles_df[self.titles_df['network_name'] == network]
                    
                    if len(network_titles) > 0:
                        status_counts = network_titles['status_name'].value_counts().to_dict()
                        genre_counts = network_titles['genre'].value_counts().to_dict() if 'genre' in network_titles.columns else {}
                        source_type_counts = network_titles['source_type'].value_counts().to_dict() if 'source_type' in network_titles.columns else {}
                        
                        stats['networks'][network] = {
                            'total_shows': len(network_titles),
                            'active_shows': status_counts.get('Active', 0),
                            'ended_shows': status_counts.get('Ended', 0),
                            'genres': genre_counts,
                            'source_types': source_type_counts
                        }
                    else:
                        # Network exists but has no shows in current filter
                        stats['networks'][network] = {
                            'total_shows': 0,
                            'active_shows': 0,
                            'ended_shows': 0,
                            'genres': {},
                            'source_types': {}
                        }
                        
                # For backward compatibility, provide simple network counts
                stats['network_counts'] = {net: data['total_shows'] 
                                         for net, data in stats['networks'].items()}
            
            # Add studio stats if available
            if 'studio_names' in self.titles_df.columns:
                studio_counts = self.titles_df['studio_names'].explode().value_counts()
                stats['studios'] = studio_counts.to_dict() if not studio_counts.empty else {}
            
            # Add team stats if available
            if not self.team_df.empty:
                # Get unique team members and their networks
                team_networks = self.team_df.groupby('name')['network_name'].unique().to_dict()
                all_members = self.team_df['name'].unique()
                
                stats['team_stats'] = {
                    'total_members': len(team_networks),
                    'team_networks': team_networks  # Map of team member -> list of networks they work with
                }
                
                # Calculate team size metrics
                stats['avg_team_size'] = len(all_members) / len(self.titles_df) if len(self.titles_df) > 0 else 0
                stats['total_team_members'] = len(all_members)
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
            stats['avg_team_size'] = len(self.team_roles_df) / len(self.titles_df) if len(self.titles_df) > 0 else 0
            stats['total_team_members'] = len(self.team_roles_df['name'].unique())
        else:
            stats['roles'] = {}
            stats['avg_team_size'] = 0
            stats['total_team_members'] = 0
            
        # Add date-based statistics
        if 'announced_date' in self.titles_df.columns:
            try:
                last_month = pd.Timestamp.now() - pd.DateOffset(months=1)
                stats['new_shows_last_month'] = len(self.titles_df[self.titles_df['announced_date'] >= last_month])
                
                # Titles by year
                stats['shows_by_year'] = self.titles_df['announced_date'].dt.year.value_counts().sort_index().to_dict()
                
                # Recent trends (last 12 months)
                last_year = datetime.now() - pd.DateOffset(months=12)
                recent_shows = self.titles_df[self.titles_df['announced_date'] >= last_year]
                stats['recent_trends'] = {
                    'total_shows': len(recent_shows),
                    'top_networks': recent_shows['network_name'].value_counts().head(5).to_dict(),
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
        if self.titles_df is None or self.team_df is None:
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
            shows_with_team = self.titles_df.copy()
            
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


