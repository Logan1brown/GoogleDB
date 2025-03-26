"""TV Shows Data Analysis Module.

This module provides comprehensive analysis of TV show data from Google Sheets,
including data cleaning, statistical analysis, and report generation.

Main components:
1. Data fetching and preprocessing
2. Statistical analysis
3. Report generation using ydata-profiling
4. Results caching
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import pandas as pd
from ydata_profiling import ProfileReport

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.dashboard.utils.sheets_client import sheets_client
from src.config.logging_config import setup_logging

logger = setup_logging(__name__)

class ShowsAnalyzer:
    """Analyzer for TV shows data.
    
    This class handles fetching, cleaning, analyzing, and reporting on TV shows data.
    Results are cached to avoid unnecessary recomputation.
    """
    
    # Lookup table file names
    LOOKUP_TABLES = {
        'network': 'STS Sales Database - network_list.csv',
        'studio': 'STS Sales Database - studio_list.csv',
        'genre': 'STS Sales Database - genre_list.csv',
        'subgenre': 'STS Sales Database - subgenre_list.csv',
        'source': 'STS Sales Database - source_types.csv',
        'order': 'STS Sales Database - order_types.csv',
        'status': 'STS Sales Database - status_types.csv',
        'role': 'STS Sales Database - role_types.csv'
    }
    
    def __init__(self, cache_dir: Optional[str] = None):
        """Initialize the analyzer.
        
        Args:
            cache_dir: Directory to store cached results. Defaults to 'cache' in current dir.
        """
        self.cache_dir = Path(cache_dir) if cache_dir else Path.cwd() / 'cache'
        self.cache_dir.mkdir(exist_ok=True)
        
        # Get project root for lookup tables
        self.project_root = Path(__file__).parent.parent.parent
        self.lookup_dir = self.project_root / 'docs' / 'sheets'
        
        self.shows_df: Optional[pd.DataFrame] = None
        self.team_df: Optional[pd.DataFrame] = None
        self.last_fetch: Optional[datetime] = None
        
        # Initialize lookup dictionaries and their last modified times
        self.lookups: Dict[str, Dict[str, str]] = {}
        self.lookup_mtimes: Dict[str, float] = {}
        self._load_lookup_tables()
        
    def fetch_data(self, force: bool = False) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Fetch shows and team data from Google Sheets.
        
        Args:
            force: If True, bypass cache and fetch fresh data.
            
        Returns:
            Tuple of (shows_df, team_df)
        """
        if not force and self.shows_df is not None and self.team_df is not None:
            logger.info("Using cached data from last fetch at %s", self.last_fetch)
            return self.shows_df, self.team_df
            
        try:
            logger.info("Fetching shows data...")
            shows_data = sheets_client.get_shows_data()
            self.shows_df = pd.DataFrame(shows_data)
            
            logger.info("Fetching team data...")
            team_data = sheets_client.get_team_data()
            self.team_df = pd.DataFrame(team_data)
            
            self.last_fetch = datetime.now()
            logger.info("Data fetch completed successfully")
            
            return self.shows_df, self.team_df
            
        except Exception as e:
            logger.error("Error fetching data: %s", str(e))
            raise
    
    def _should_reload_lookup(self, key: str, filepath: Path) -> bool:
        """Check if a lookup table needs to be reloaded based on file modification time."""
        if not filepath.exists():
            return False
            
        current_mtime = filepath.stat().st_mtime
        last_mtime = self.lookup_mtimes.get(key, 0)
        return current_mtime > last_mtime
    
    def _load_lookup_tables(self) -> None:
        """Load and process all lookup tables for data normalization.
        
        Tables are only reloaded if their files have been modified since the last load.
        """
        logger.info("Checking lookup tables...")
        
        for key, filename in self.LOOKUP_TABLES.items():
            filepath = self.lookup_dir / filename
            
            # Skip if file doesn't exist
            if not filepath.exists():
                logger.warning(f"Lookup table not found: {filename}")
                continue
            
            # Skip if file hasn't been modified
            if not self._should_reload_lookup(key, filepath):
                logger.debug(f"Lookup table {filename} unchanged, using cached version")
                continue
                
            try:
                logger.info(f"Loading/reloading lookup table: {filename}")
                df = pd.read_csv(filepath)
                
                # Create mapping from aliases to standard names
                mapping = {}
                for _, row in df.iterrows():
                    # Add the main name as its own alias (lowercase)
                    name = str(row.iloc[0]).lower()
                    mapping[name] = name
                    
                    # Add aliases if they exist
                    if 'aliases' in df.columns and pd.notna(row['aliases']):
                        aliases = str(row['aliases']).split(',')
                        for alias in aliases:
                            mapping[alias.strip().lower()] = name
                            
                self.lookups[key] = mapping
                self.lookup_mtimes[key] = filepath.stat().st_mtime
                logger.debug(f"Loaded {len(mapping)} mappings for {key}")
                
            except Exception as e:
                logger.error(f"Error loading {filename}: {str(e)}")
                
    def _normalize_field(self, value: str, field_type: str) -> str:
        """Normalize a field value using lookup tables.
        
        Args:
            value: The value to normalize
            field_type: Type of field (network, studio, etc.)
            
        Returns:
            Normalized value
        """
        if pd.isna(value) or field_type not in self.lookups:
            return value
            
        value = str(value).strip().lower()
        return self.lookups[field_type].get(value, value)
    
    def _validate_data(self) -> None:
        """Validate cleaned data and log any issues.
        
        This validation is non-blocking and serves to report data quality issues.
        Critical issues (missing network/studio) are logged as warnings.
        Other data quality issues are logged as info.
        """
        critical_issues = []
        quality_warnings = []
        
        # Check for missing critical fields
        for field in ['network', 'studio']:
            missing = self.shows_df[field].isna().sum()
            if missing > 0:
                critical_issues.append(f"Missing {field}: {missing} rows")
        
        # Check for data quality issues
        quality_checks = {
            'show_name': 'Show names',
            'date': 'Announcement dates'
        }
        
        for field, display_name in quality_checks.items():
            missing = self.shows_df[field].isna().sum()
            if missing > 0:
                quality_warnings.append(f"Missing {display_name}: {missing} rows")
        
        # Check for non-standard values in categorical fields
        for field, lookup_type in {
            'genre': 'genre',
            'subgenre': 'subgenre',
            'source_type': 'source',
            'order_type': 'order',
            'status': 'status'
        }.items():
            if field in self.shows_df.columns and lookup_type in self.lookups:
                non_standard = self.shows_df[~self.shows_df[field].isin(
                    set(self.lookups[lookup_type].values())
                )][field].unique()
                if len(non_standard) > 0:
                    quality_warnings.append(
                        f"Non-standard {field} values: {', '.join(str(x) for x in non_standard if pd.notna(x))}"
                    )
        
        # Check team data
        if 'show_name' in self.team_df.columns:
            orphaned = self.team_df[~self.team_df['show_name'].isin(
                self.shows_df['show_name']
            )]['show_name'].unique()
            if len(orphaned) > 0:
                quality_warnings.append(f"Team members with no matching show: {', '.join(orphaned)}")
        
        # Log issues with appropriate severity
        if critical_issues:
            logger.warning("Critical data issues found:\n- " + "\n- ".join(critical_issues))
        
        if quality_warnings:
            logger.info("Data quality warnings:\n- " + "\n- ".join(quality_warnings))
            
    def clean_data(self) -> None:
        """Clean and preprocess the fetched data.
        
        This includes:
        - Setting proper column names
        - Handling missing values
        - Standardizing dates
        - Normalizing categorical fields using lookup tables
        - Creating derived features
        """
        if self.shows_df is None or self.team_df is None:
            self.fetch_data()
            
        # Reload lookup tables in case they've changed
        self._load_lookup_tables()
        
        # Clean shows DataFrame
        logger.info("Cleaning shows data...")
        
        # 1. Fix column names and remove empty columns
        self.shows_df.columns = self.shows_df.iloc[0]
        self.shows_df = self.shows_df.iloc[1:].reset_index(drop=True)
        self.shows_df = self.shows_df.loc[:, self.shows_df.columns.notna()]
        self.shows_df = self.shows_df.loc[:, self.shows_df.columns != '']
        
        # 2. Handle dates
        logger.info("Processing dates...")
        self.shows_df['date'] = pd.to_datetime(self.shows_df['date'], errors='coerce')
        self.shows_df['year'] = self.shows_df['date'].dt.year
        self.shows_df['month'] = self.shows_df['date'].dt.month
        self.shows_df['quarter'] = self.shows_df['date'].dt.quarter
        
        # Add season
        self.shows_df['season'] = self.shows_df['month'].map(
            lambda m: 'Winter' if m in [12,1,2] else
                     'Spring' if m in [3,4,5] else
                     'Summer' if m in [6,7,8] else
                     'Fall' if m in [9,10,11] else None
        )
        
        # 3. Normalize categorical fields using lookup tables
        logger.info("Normalizing categorical fields...")
        field_mappings = {
            'network': 'network',
            'studio': 'studio',
            'genre': 'genre',
            'subgenre': 'subgenre',
            'source_type': 'source',
            'order_type': 'order',
            'status': 'status'
        }
        
        for col, lookup_type in field_mappings.items():
            if col in self.shows_df.columns:
                self.shows_df[col] = self.shows_df[col].apply(
                    lambda x: self._normalize_field(x, lookup_type)
                )
        
        # 4. Handle numeric fields
        logger.info("Processing numeric fields...")
        self.shows_df['episode_count'] = pd.to_numeric(
            self.shows_df['episode_count'], 
            errors='coerce'
        ).fillna(0).astype(int)
        
        # Clean team DataFrame
        logger.info("Cleaning team data...")
        
        # 1. Fix column names
        self.team_df.columns = self.team_df.iloc[0]
        self.team_df = self.team_df.iloc[1:].reset_index(drop=True)
        
        # 2. Clean and normalize role fields
        self.team_df['roles'] = self.team_df['roles'].apply(
            lambda x: self._normalize_field(x, 'role')
        )
        
        # 3. Ensure proper show name relationships
        self.team_df['show_name'] = self.team_df['show_name'].str.strip()
        
        # 4. Sort team members by show and order
        self.team_df['order'] = pd.to_numeric(self.team_df['order'], errors='coerce').fillna(999)
        self.team_df = self.team_df.sort_values(['show_name', 'order'])
        
        logger.info("Data cleaning completed")
        
        # Data validation
        self._validate_data()
    
    def generate_basic_stats(self) -> Dict[str, Union[int, float, str]]:
        """Generate basic statistics about the shows.
        
        Returns:
            Dictionary containing basic statistics:
            - Total number of shows
            - Shows by network
            - Shows by genre
            - Average team size
            etc.
        """
        if self.shows_df is None or self.team_df is None:
            self.fetch_data()
            
        # TODO: Implement basic statistics generation
        return {}
    
    def generate_profile_report(self, output_file: Optional[str] = None) -> None:
        """Generate a comprehensive profile report using ydata-profiling.
        
        Args:
            output_file: Path to save the HTML report. If None, uses default path in cache_dir.
        """
        if self.shows_df is None:
            self.fetch_data()
            
        if output_file is None:
            output_file = self.cache_dir / f'shows_profile_{datetime.now():%Y%m%d}.html'
            
        # TODO: Implement profile report generation
        pass

# Create singleton instance for global use
shows_analyzer = ShowsAnalyzer()
