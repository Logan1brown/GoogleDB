"""Network Connection Analysis.

This module analyzes relationships between networks through shared creators,
with filtering capabilities for networks, genres, and source types.
"""

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple, Any
from enum import Enum

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

class DataFields(Enum):
    """Constants for data field names."""
    SHOW_NAME = 'show_name'
    SHOWS = 'shows'
    NETWORK = 'network'
    GENRE = 'genre'
    SOURCE_TYPE = 'source_type'
    NAME = 'name'

@dataclass
class CreatorProfile:
    """Profile of a creator's work across networks."""
    name: str
    networks: Set[str]
    genres: Set[str]
    source_types: Set[str]
    total_shows: int

class ConnectionsAnalyzer:
    """Analyzer for network relationships and creator filtering."""
    
    UNKNOWN_VALUE = 'Unknown'
    REQUIRED_SHOW_COLUMNS = {DataFields.NETWORK.value, DataFields.GENRE.value, 
                           DataFields.SOURCE_TYPE.value}
    REQUIRED_TEAM_COLUMNS = {DataFields.NAME.value, DataFields.SHOW_NAME.value}
    
    def __init__(self, shows_df: pd.DataFrame, team_df: pd.DataFrame) -> None:
        """Initialize the analyzer.
        
        Args:
            shows_df: DataFrame with show information (network, genre, source_type)
            team_df: DataFrame with creator information
            
        Raises:
            ValueError: If required columns are missing
        """
        self._validate_dataframes(shows_df, team_df)
        self.shows_df = self._prepare_shows_data(shows_df)
        self.team_df = team_df
        self.combined_df = self._merge_data()
        self.creator_profiles = self._build_creator_profiles()
        self._log_stats()
    
    def _validate_dataframes(self, shows_df: pd.DataFrame, team_df: pd.DataFrame) -> None:
        """Validate required columns exist in dataframes."""
        missing_show_cols = self.REQUIRED_SHOW_COLUMNS - set(shows_df.columns)
        missing_team_cols = self.REQUIRED_TEAM_COLUMNS - set(team_df.columns)
        
        if missing_show_cols:
            raise ValueError(f"Missing required show columns: {missing_show_cols}")
        if missing_team_cols:
            raise ValueError(f"Missing required team columns: {missing_team_cols}")
    
    def _prepare_shows_data(self, shows_df: pd.DataFrame) -> pd.DataFrame:
        """Prepare shows data by handling column names and missing values."""
        df = shows_df.copy()
        
        # Handle column name differences
        if DataFields.SHOWS.value in df.columns:
            df = df.rename(columns={DataFields.SHOWS.value: DataFields.SHOW_NAME.value})
        
        # Handle missing values
        for col in [DataFields.GENRE.value, DataFields.SOURCE_TYPE.value]:
            df[col] = df[col].fillna(self.UNKNOWN_VALUE)
            
        return df
    
    def _merge_data(self) -> pd.DataFrame:
        """Merge show and creator data safely."""
        try:
            return pd.merge(
                self.team_df,
                self.shows_df[[DataFields.SHOW_NAME.value, DataFields.NETWORK.value,
                              DataFields.GENRE.value, DataFields.SOURCE_TYPE.value]],
                on=DataFields.SHOW_NAME.value
            )
        except Exception as e:
            raise ValueError(f"Failed to merge show and creator data: {e}")
    
    def _log_stats(self) -> None:
        """Log basic statistics about the data."""
        logger.info("Network connection stats:")
        logger.info(f"  Networks: {self.combined_df[DataFields.NETWORK.value].nunique()}")
        logger.info(f"  Genres: {self.combined_df[DataFields.GENRE.value].nunique()}")
        logger.info(f"  Source types: {self.combined_df[DataFields.SOURCE_TYPE.value].nunique()}")
        logger.info(f"  Unique creators: {self.combined_df[DataFields.NAME.value].nunique()}")
    
    def _build_creator_profiles(self) -> Dict[str, CreatorProfile]:
        """Build cached profiles of creators and their work.
        
        Returns:
            Dict mapping creator names to their profiles
        """
        profiles = {}
        
        for name, group in self.combined_df.groupby(DataFields.NAME.value):
            profiles[name] = CreatorProfile(
                name=name,
                networks=set(group[DataFields.NETWORK.value]),
                genres=set(group[DataFields.GENRE.value]),
                source_types=set(group[DataFields.SOURCE_TYPE.value]),
                total_shows=len(set(group[DataFields.SHOW_NAME.value]))
            )
            
        return profiles
    
    def get_shared_creators_matrix(self) -> np.ndarray:
        """Get matrix of shared creator counts between networks.
        Returns:
            Dict mapping creator names to their profiles
        """
        profiles = {}
        
        for name, group in self.combined_df.groupby(DataFields.NAME.value):
            profiles[name] = CreatorProfile(
                name=name,
                networks=set(group[DataFields.NETWORK.value].unique()),
                genres=set(group[DataFields.GENRE.value].unique()),
                source_types=set(group[DataFields.SOURCE_TYPE.value].unique()),
                total_shows=len(group[DataFields.SHOW_NAME.value].unique())
            )
        
        return profiles
    
    def get_filter_options(self) -> Dict[str, List[str]]:
        """Get available filter options.
        
        Returns:
            Dict with lists of available networks, genres, and source types
        """
        return {
            'networks': sorted(self.combined_df[DataFields.NETWORK.value].unique()),
            'genres': sorted(self.combined_df[DataFields.GENRE.value].unique()),
            'sources': sorted(self.combined_df[DataFields.SOURCE_TYPE.value].unique())
        }
    
    def filter_creators(
        self,
        networks: Optional[List[str]] = None,
        genre: Optional[str] = None,
        source_type: Optional[str] = None
    ) -> List[CreatorProfile]:
        """Filter creators based on specified criteria.
        
        Args:
            networks: List of networks to filter by
            genre: Genre to filter by
            source_type: Source type to filter by
            
        Returns:
            List of filtered creator profiles sorted by total shows
        """
        filtered_profiles = []
        
        for profile in self.creator_profiles.values():
            # Check all specified criteria must match (AND logic)
            if networks and not all(net in profile.networks for net in networks):
                continue
            
            if genre and genre not in profile.genres:
                continue
                
            if source_type and source_type not in profile.source_types:
                continue
            
            filtered_profiles.append(profile)
        
        # Sort by total shows descending
        return sorted(filtered_profiles, key=lambda x: x.total_shows, reverse=True)
    
    def get_shared_creators_matrix(
        self,
        network1: Optional[str] = None,
        network2: Optional[str] = None,
        genre: Optional[str] = None,
        source: Optional[str] = None
    ) -> Tuple[np.ndarray, List[str]]:
        """Generate matrix of shared creators between networks.
        
        Args:
            network1: First network to compare (optional)
            network2: Second network to compare (optional)
            genre: Filter by genre (optional)
            source: Filter by source type (optional)
            
        Returns:
            Tuple of (matrix, network_labels) where matrix[i,j] is the number
            of creators shared between networks[i] and networks[j]
        """
        # Filter the combined data
        filtered_df = self.combined_df.copy()
        
        if genre:
            filtered_df = filtered_df[filtered_df[DataFields.GENRE.value] == genre]
        if source:
            filtered_df = filtered_df[filtered_df[DataFields.SOURCE_TYPE.value] == source]
            
        # Get networks to compare
        if network1 and network2:
            networks = sorted([network1, network2])
            filtered_df = filtered_df[filtered_df[DataFields.NETWORK.value].isin(networks)]
        elif network1:
            networks = sorted([network1] + list(filtered_df[filtered_df[DataFields.NETWORK.value] != network1][DataFields.NETWORK.value].unique()))
            filtered_df = filtered_df[filtered_df[DataFields.NETWORK.value].isin(networks)]
        elif network2:
            networks = sorted([network2] + list(filtered_df[filtered_df[DataFields.NETWORK.value] != network2][DataFields.NETWORK.value].unique()))
            filtered_df = filtered_df[filtered_df[DataFields.NETWORK.value].isin(networks)]
        else:
            networks = sorted(filtered_df[DataFields.NETWORK.value].unique())
        
        # Initialize matrix
        n = len(networks)
        matrix = np.zeros((n, n))
        net_to_idx = {net: i for i, net in enumerate(networks)}
        
        # Count shared creators
        for name, group in filtered_df.groupby(DataFields.NAME.value):
            creator_networks = list(group[DataFields.NETWORK.value].unique())
            for i, net1 in enumerate(creator_networks):
                for net2 in creator_networks[i+1:]:
                    idx1 = net_to_idx[net1]
                    idx2 = net_to_idx[net2]
                    matrix[idx1][idx2] += 1
                    matrix[idx2][idx1] += 1  # Symmetric
        
        return matrix, networks
    
    def get_success_stories(
        self,
        network: Optional[str] = None,
        genre: Optional[str] = None,
        source: Optional[str] = None,
        min_networks: int = 2,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Get creators who have worked across multiple networks.
        
        Args:
            min_networks: Minimum number of networks
            top_k: Number of creators to return
            
        Returns:
            List of creator profiles with network counts, sorted by network count
            and total shows
        """
        stories = []
        
        for profile in self.creator_profiles.values():
            # Apply filters
            if network and network not in profile.networks:
                continue
            if genre and genre not in profile.genres:
                continue
            if source and source not in profile.source_types:
                continue
                
            if len(profile.networks) >= min_networks:
                stories.append({
                    'creator_team': profile.name,
                    'networks': sorted(list(profile.networks)),
                    'show_count': profile.total_shows,
                    'roles': sorted(list(profile.source_types))
                })
        
        return sorted(stories,
                     key=lambda x: (x['network_count'], x['total_shows']),
                     reverse=True)[:top_k]
        return {
            'networks': sorted(self.combined_df[DataFields.NETWORK.value].unique()),
            'genres': sorted(self.combined_df[DataFields.GENRE.value].unique()),
            'sources': sorted(self.combined_df[DataFields.SOURCE_TYPE.value].unique())
        }

def analyze_network_connections(shows_df: pd.DataFrame, team_df: pd.DataFrame) -> ConnectionsAnalyzer:
    """Initialize and return a ConnectionsAnalyzer instance.
    
    Args:
        shows_df: DataFrame with show information
        team_df: DataFrame with creator information
        
    Returns:
        ConnectionsAnalyzer instance ready for analysis
    """
    return ConnectionsAnalyzer(shows_df, team_df)
