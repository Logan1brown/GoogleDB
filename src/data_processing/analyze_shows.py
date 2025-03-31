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
            # First row contains headers
            headers = [col.lower().replace(' ', '_') for col in shows_data[0]]
            
            # Rename 'shows' to 'show_name' to match show_team.csv
            # This is important because:
            # 1. shows.csv has one row per show with 'shows' column
            # 2. show_team.csv has multiple rows per show with 'show_name' column
            # 3. We need to join these tables on the same column name
            headers = ['show_name' if h == 'shows' else h for h in headers]
            logger.info(f"Number of rows in shows_data: {len(shows_data)}")
            if len(shows_data) > 1:
                logger.info(f"First data row: {shows_data[1]}")
            
            self.shows_df = pd.DataFrame(shows_data[1:], columns=headers)
            
            
            logger.info(f"DataFrame shape: {self.shows_df.shape}")
            logger.info(f"DataFrame columns: {list(self.shows_df.columns)}")
            logger.info(f"First few rows:\n{self.shows_df.head()}")
            
            logger.info("Fetching team data...")
            team_data = sheets_client.get_team_data()
            # First row contains headers
            headers = [col.lower().replace(' ', '_') for col in team_data[0]]
            logger.info(f"Team data headers: {headers}")
            if len(team_data) > 1:
                logger.info(f"First team data row: {team_data[1]}")
            self.team_df = pd.DataFrame(team_data[1:], columns=headers)
            logger.info(f"Team DataFrame columns: {list(self.team_df.columns)}")
            
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
                    # Get the standard name, preserving original case
                    standard_name = str(row[df.columns[0]])
                    # Add the main name as its own alias (lowercase)
                    mapping[standard_name.lower()] = standard_name
                    
                    # Add aliases if they exist
                    if 'aliases' in df.columns and pd.notna(row['aliases']):
                        aliases = str(row['aliases']).split(',')
                        for alias in aliases:
                            mapping[alias.strip().lower()] = standard_name
                            
                    # For subgenres, also add any parent genres as valid values
                    if key == 'subgenre' and 'parent_genres' in df.columns and pd.notna(row['parent_genres']):
                        parent_genres = str(row['parent_genres']).split(',')
                        for genre in parent_genres:
                            mapping[genre.strip().lower()] = standard_name
                            
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
            
        # For subgenres, handle multiple values
        if field_type == 'subgenre':
            if pd.isna(value) or not str(value).strip():
                return ''
                
            # Split on commas and clean each subgenre
            subgenres = [s.strip() for s in str(value).split(',')]
            normalized = []
            
            for subgenre in subgenres:
                # Skip empty values
                if not subgenre:
                    continue
                    
                # Try to find a match in lookups
                norm_value = self.lookups[field_type].get(subgenre.lower())
                if norm_value:
                    normalized.append(norm_value)
                else:
                    # For unmatched values, ensure Title Case
                    # Log for review
                    logger.debug(f'Unmatched subgenre: {subgenre}')
                    normalized.append(' '.join(word.capitalize() for word in subgenre.split()))
            
            # Remove duplicates while preserving order
            seen = set()
            unique_normalized = [x for x in normalized if not (x.lower() in seen or seen.add(x.lower()))]
            
            # Join with standardized comma spacing
            return ', '.join(unique_normalized) if unique_normalized else ''
        
        # For other fields, simple lookup
        original = str(value).strip()
        lookup_key = original.lower()
        return self.lookups[field_type].get(lookup_key, original)
    
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
                # Get set of valid values (case-insensitive)
                valid_values = {v.lower() for v in self.lookups[lookup_type].values()}
                # Find non-standard values
                # For subgenres, split on commas and check each value
                if field == 'subgenre':
                    non_standard_values = set()
                    for value in self.shows_df[field].dropna():
                        subgenres = [s.strip() for s in str(value).split(',')]
                        for subgenre in subgenres:
                            if subgenre and subgenre.lower() not in valid_values:
                                non_standard_values.add(subgenre)
                    non_standard = sorted(non_standard_values)
                else:
                    non_standard = self.shows_df[~self.shows_df[field].str.lower().isin(valid_values)][field].unique()
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
        
        # 1. Remove empty columns
        self.shows_df = self.shows_df.loc[:, self.shows_df.columns.notna()]
        self.shows_df = self.shows_df.loc[:, self.shows_df.columns != '']
        
        # Replace empty strings with NaN for better handling
        self.shows_df = self.shows_df.replace('', pd.NA)
        
        # 2. Handle dates if present
        logger.info("Processing dates...")
        if 'date' in self.shows_df.columns:
            self.shows_df['date'] = pd.to_datetime(self.shows_df['date'], errors='coerce')
            
            # Extract date components for valid dates
            self.shows_df['year'] = self.shows_df['date'].dt.year
            self.shows_df['month'] = self.shows_df['date'].dt.month
            self.shows_df['quarter'] = self.shows_df['date'].dt.quarter
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
        
        # 4. Handle numeric fields if present
        logger.info("Processing numeric fields...")
        if 'episode_count' in self.shows_df.columns:
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
        def normalize_roles(roles_str):
            if pd.isna(roles_str) or not str(roles_str).strip():
                return ''
            
            # Pre-process input
            roles_str = str(roles_str).strip()
            
            # Build reverse lookup for faster alias matching
            if not hasattr(self, '_role_alias_map'):
                self._role_alias_map = {}
                self._compound_roles = set()  # Track multi-word roles
                for role, data in self.lookups['role'].items():
                    # Add the main role
                    role_lower = role.lower()
                    self._role_alias_map[role_lower] = role
                    if ' ' in role_lower:
                        self._compound_roles.add(role_lower)
                    
                    # Add aliases
                    if ',' in data:
                        for alias in data.split(','):
                            alias = alias.strip().lower()
                            self._role_alias_map[alias] = role
                            if ' ' in alias:
                                self._compound_roles.add(alias)
            
            # First try to match the entire string as it might be a compound role
            roles_str_lower = roles_str.lower().replace('.', '')
            if roles_str_lower in self._role_alias_map:
                return self._role_alias_map[roles_str_lower]
            
            # Split on commas and normalize each part
            roles = [r.strip() for r in roles_str.split(',')]
            normalized = []
            
            for role in roles:
                role_lower = role.lower().strip().replace('.', '')
                
                # Try exact match first
                if role_lower in self._role_alias_map:
                    normalized.append(self._role_alias_map[role_lower])
                    continue
                
                # Try splitting on spaces to handle compound roles
                parts = role_lower.split()
                if len(parts) > 1:
                    part_roles = []
                    for part in parts:
                        if part in self._role_alias_map:
                            part_roles.append(self._role_alias_map[part])
                    if part_roles:
                        normalized.extend(part_roles)
                        continue
                
                # Try compound role matches
                matched = False
                for compound in self._compound_roles:
                    if compound in role_lower:
                        normalized.append(self._role_alias_map[compound])
                        matched = True
                        break
                
                if not matched:
                    # Log unrecognized role for future lookup table updates
                    logger.warning(f"Unrecognized role: {role} from {roles_str}")
                    normalized.append(role.strip('.'))
            
            return ', '.join(sorted(set(normalized)))
        
        if 'roles' in self.team_df.columns:
            self.team_df['roles'] = self.team_df['roles'].apply(normalize_roles)
            
            # Log role standardization results
            unique_roles = self.team_df['roles'].unique()
            logger.info(f"Standardized roles: {sorted(r for r in unique_roles if r)}")
        
        # 3. Ensure proper show name relationships
        if 'show_name' in self.team_df.columns:
            self.team_df['show_name'] = self.team_df['show_name'].str.strip()
            
            # 4. Sort team members by show and order
            if 'order' in self.team_df.columns:
                self.team_df['order'] = pd.to_numeric(self.team_df['order'], errors='coerce').fillna(999)
                self.team_df = self.team_df.sort_values(['show_name', 'order'])
        
        logger.info("Data cleaning completed")
        
        # Data validation
        self._validate_data()
    
    def generate_basic_stats(self) -> Dict[str, Union[int, float, Dict]]:
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
            
        stats = {}
        
        # Basic counts
        stats['total_shows'] = len(self.shows_df)
        
        # Shows by network
        if 'network' in self.shows_df.columns:
            network_counts = self.shows_df['network'].value_counts()
            stats['shows_by_network'] = network_counts.to_dict()
        else:
            stats['shows_by_network'] = {}
            
        # New shows in last month
        if 'date' in self.shows_df.columns:
            try:
                # Convert date column to datetime
                self.shows_df['date'] = pd.to_datetime(self.shows_df['date'], errors='coerce')
                
                # Get year from date
                self.shows_df['year'] = self.shows_df['date'].dt.year
                
                # Calculate new shows
                last_month = pd.Timestamp.now() - pd.DateOffset(months=1)
                stats['new_shows_last_month'] = len(self.shows_df[self.shows_df['date'] >= last_month])
                
                # Shows by year
                yearly_counts = self.shows_df['year'].value_counts().sort_index()
                stats['shows_by_year'] = yearly_counts.to_dict()
            except Exception as e:
                logger.error(f"Error processing dates: {e}")
                stats['new_shows_last_month'] = 0
                stats['shows_by_year'] = {}
        else:
            stats['new_shows_last_month'] = 0
            stats['shows_by_year'] = {}
            
        return stats
        
        # Recent trends (last 12 months)
        if 'date' in self.shows_df.columns:
            last_year = datetime.now() - pd.DateOffset(months=12)
            recent_shows = self.shows_df[self.shows_df['date'] >= last_year]
            stats['recent_trends'] = {
                'total_shows': len(recent_shows),
                'top_networks': recent_shows['network'].value_counts().head(5).to_dict(),
                'top_genres': recent_shows['genre'].value_counts().head(5).to_dict()
            }
        
        return stats
    
    def generate_profile_report(self, output_file: Optional[str] = None) -> None:
        """Generate comprehensive profile reports using ydata-profiling.
        
        This generates two reports:
        1. Shows report with aggregated team metrics
        2. Team members report with detailed creative analysis
        
        Args:
            output_file: Path to save the HTML report. If None, uses default path in cache_dir.
        """
        if self.shows_df is None or self.team_df is None:
            self.fetch_data()
            self.clean_data()
            
        # Default output paths
        if output_file is None:
            base_path = self.cache_dir / f'profile_{datetime.now():%Y%m%d}'
            shows_output = base_path.with_name(f'{base_path.name}_shows.html')
            team_output = base_path.with_name(f'{base_path.name}_team.html')
        else:
            shows_output = Path(output_file)
            team_output = shows_output.with_name(f'{shows_output.stem}_team.html')
        
        logger.info('Generating profile reports...')
        
        try:
            # Debug: Print DataFrame columns
            logger.info(f'Shows DataFrame columns: {self.shows_df.columns.tolist()}')
            logger.info(f'Team DataFrame columns: {self.team_df.columns.tolist()}')
            
            # Add team metrics to shows DataFrame
            shows_with_team = self.shows_df.copy()
            team_metrics = self.team_df.groupby('show_name').agg({
                'name': 'count',
                'roles': lambda x: len(set(x))
            }).rename(columns={
                'name': 'team_size',
                'roles': 'unique_roles'
            })
            shows_with_team = shows_with_team.join(team_metrics, on='show_name')
            
            # Create shows profile report
            shows_profile = ProfileReport(
                shows_with_team,
                title='TV Shows Analysis Report',
                explorative=True,
                correlations={
                    'pearson': {'calculate': True},
                    'spearman': {'calculate': True},
                    'kendall': {'calculate': True},
                    'phi_k': {'calculate': True},
                    'cramers': {'calculate': True}
                },
                interactions={'continuous': True},
                samples={'head': 10, 'tail': 10}
            )
            
            # Create team profile report
            team_profile = ProfileReport(
                self.team_df,
                title='TV Shows Team Analysis Report',
                explorative=True,
                correlations={
                    'pearson': {'calculate': True},
                    'spearman': {'calculate': True},
                    'kendall': {'calculate': True},
                    'phi_k': {'calculate': True},
                    'cramers': {'calculate': True}
                },
                interactions={'continuous': True},
                samples={'head': 10, 'tail': 10}
            )
            
            # Save reports
            logger.info(f'Saving shows profile report to {shows_output}')
            shows_profile.to_file(str(shows_output))
            
            logger.info(f'Saving team profile report to {team_output}')
            team_profile.to_file(str(team_output))
            
            logger.info('Profile reports generation completed')
            
        except Exception as e:
            logger.error(f'Error generating profile reports: {str(e)}')
            raise

# Create singleton instance for global use
shows_analyzer = ShowsAnalyzer()
