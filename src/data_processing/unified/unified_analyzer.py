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

from typing import Dict, List, Optional, Any
import pandas as pd
import logging
import streamlit as st
from src.data_processing.success_analysis.success_analyzer import SuccessAnalyzer
from src.data_processing.analyze_shows import shows_analyzer

logger = logging.getLogger(__name__)

class UnifiedAnalyzer:
    """Analyzer for the unified dashboard view providing acquisition, packaging, and development insights."""
    
    def __init__(self, success_analyzer: Optional[SuccessAnalyzer] = None):
        """Initialize the analyzer.
        
        Args:
            success_analyzer: Optional SuccessAnalyzer instance
        """
        # Get normalized data from shows_analyzer
        self.shows_df, self.team_df = shows_analyzer.fetch_data()
        
        # Convert episode_count to float since it comes as strings
        self.shows_df['episode_count'] = pd.to_numeric(self.shows_df['episode_count'], errors='coerce')
        # Initialize success analyzer if not provided
        self.success_analyzer = success_analyzer or SuccessAnalyzer()
        # Initialize analyzer with show data
        self.success_analyzer.initialize_data(self.shows_df)
        
        # Get filter options from normalized data and remove empty values
        self._source_types = sorted([s for s in self.shows_df['source_type'].dropna().unique() if s.strip()])
        self._genres = sorted([g for g in self.shows_df['genre'].dropna().unique() if g.strip()])
        self._networks = sorted([n for n in self.shows_df['network'].dropna().unique() if n.strip()])
        
        logger.info(f"Initialized UnifiedAnalyzer with {len(self.shows_df)} shows and {len(self.team_df)} team members")
        
    def get_shows_by_episode_count(self, episode_count: int, source_type: Optional[str] = None, genre: Optional[str] = None) -> pd.DataFrame:
        """Get shows with a specific episode count.
        
        Args:
            episode_count: Number of episodes to filter by
            source_type: Optional filter for source type
            genre: Optional filter for genre
            
        Returns:
            DataFrame with shows matching the episode count
        """
        df = self.shows_df.copy(deep=True)
        if source_type and source_type.lower() != 'all':
            df = df[df['source_type'] == source_type]
        if genre and genre.lower() != 'all':
            df = df[df['genre'] == genre]
            
        # Episode count should already be clean integers from analyze_shows.py
        if not pd.api.types.is_integer_dtype(df['episode_count']):
            logger.error(f"Episode count has wrong type: {df['episode_count'].dtype}")
            logger.error(f"Episode count sample: {df['episode_count'].head().tolist()}")
        
        # Filter for shows with required data
        has_order_type = df['order_type'].notna() & (df['order_type'] != '')
        has_episode_count = df['episode_count'].notna()
        
        # Keep shows that meet criteria
        reliable_df = df[has_order_type & has_episode_count]
        
        # Filter by episode count
        return reliable_df[reliable_df['episode_count'] == episode_count][['shows', 'network', 'genre', 'source_type', 'order_type', 'episode_count']]
    
    def get_format_insights(self, source_type: Optional[str] = None, genre: Optional[str] = None) -> Dict[str, Any]:
        """Get insights about successful show formats.
        
        Args:
            source_type: Optional filter for source type
            genre: Optional filter for genre
            
        Returns:
            Dictionary with format insights including:
            - Episode count distribution by success tier
            - Season count patterns
            - Limited vs ongoing success rates
        """
        # Start with filtered data - use copy(deep=True) to preserve numeric types
        df = self.shows_df.copy(deep=True)
        if source_type and source_type.lower() != 'all':
            df = df[df['source_type'] == source_type]
        if genre and genre.lower() != 'all':
            df = df[df['genre'] == genre]
            
        # Episode count should already be clean integers from analyze_shows.py
        # Filter for shows with required data
        has_order_type = df['order_type'].notna() & (df['order_type'] != '')
        has_episode_count = df['episode_count'].notna()
        
        # Keep shows that meet criteria
        reliable_df = df[has_order_type & has_episode_count]
        
        # Calculate success score for each show
        reliable_df['success_score'] = reliable_df.apply(self.success_analyzer.calculate_success, axis=1)
        
        # Get actual episode counts and their frequencies
        episode_counts = reliable_df['episode_count'].value_counts().sort_index()
        
        most_common_eps = int(episode_counts.index[episode_counts.argmax()]) if not episode_counts.empty else None
        
        episode_insights = {
            'distribution': {
                'episodes': episode_counts.index.tolist(),
                'show_counts': episode_counts.values.tolist()
            },
            'most_common': most_common_eps,
            'avg_episodes': float(reliable_df['episode_count'].mean()) if not reliable_df.empty else None
        }
        
        # Analyze series by order type
        # First normalize the order_type values
        reliable_df['order_type'] = reliable_df['order_type'].fillna('')
        reliable_df['order_type'] = reliable_df['order_type'].str.strip()
        
        # Map common variations to standard types
        order_type_map = {
            'limited series': 'Limited',
            'limited': 'Limited',
            'mini-series': 'Miniseries',
            'miniseries': 'Miniseries',
            'mini series': 'Miniseries',
            'ongoing': 'Ongoing',
            'series': 'Ongoing',
            'regular series': 'Ongoing',
            'anthology': 'Anthology',
            'anthology series': 'Anthology',
            'pilot': 'Pilot'
        }
        
        # Apply case-insensitive mapping
        reliable_df['order_type'] = reliable_df['order_type'].str.lower().map(lambda x: order_type_map.get(x, x))
        
        # Filter out pilots and empty values first
        has_valid_order = (
            (reliable_df['order_type'] != 'Pilot') & 
            (reliable_df['order_type'] != '') & 
            (reliable_df['order_type'].notna())
        )
        reliable_df = reliable_df[has_valid_order]
        
        # Get series type counts from order_type
        order_type_counts = reliable_df['order_type'].value_counts()
        
        # Use order type counts directly
        series_type_counts = order_type_counts.copy()
        
        total_shows = len(reliable_df) if not reliable_df.empty else 1  # Prevent division by zero
        
        # Get non-zero types from the data
        non_zero_types = [order_type for order_type in series_type_counts.index
                         if series_type_counts[order_type] > 0]
        
        # Get counts and percentages for types with non-zero counts
        series_insights = {
            'counts': {
                order_type: int(series_type_counts[order_type])
                for order_type in non_zero_types
            },
            'percentages': {
                order_type: float(series_type_counts[order_type] / total_shows * 100)
                for order_type in non_zero_types
            }
        }
        
        
        # Analyze by network
        network_insights = {}
        for network in reliable_df['network'].dropna().unique():
            network_df = reliable_df[reliable_df['network'] == network]
            # Get episode count data
            valid_eps = network_df['episode_count'].dropna()
            
            if len(valid_eps) > 0:
                # Get preferred series type based on frequency
                type_counts = network_df['order_type'].value_counts()
                if not type_counts.empty:
                    preferred_type = type_counts.index[0]  # Most frequent type
                    type_percentage = (type_counts[0] / len(network_df)) * 100
                    # Only consider it a preference if it's more than 50% of shows
                    if type_percentage < 50:
                        preferred_type = 'Mixed'
                else:
                    preferred_type = 'Unknown'
                
                network_insights[network] = {
                    'avg_episodes': float(valid_eps.mean()),
                    'most_successful_format': {
                        'episodes': float(network_df['episode_count'].mean()),
                        'preferred_type': preferred_type
                    }
                }
        
        return {
            'episode_insights': episode_insights,
            'series_insights': series_insights,  # This contains the limited vs ongoing breakdown
            'network_insights': network_insights,
            'total_shows_analyzed': len(reliable_df)
        }
        
    def get_network_metrics(self, source_type: Optional[str] = None, genre: Optional[str] = None) -> Dict[str, Dict[str, float]]:
        """Get performance metrics for each network based on filters.
        
        Args:
            source_type: Optional filter for source type
            genre: Optional filter for genre
            
        Returns:
            Dictionary mapping network names to their metrics
        """
        # Start with filtered data
        df = self.shows_df.copy(deep=True)
        
        if source_type:
            df = df[df['source_type'] == source_type]
        if genre:
            df = df[df['genre'] == genre]
            
        # Calculate metrics for each network
        network_metrics = {}
        
        for network in self._networks:
            network_shows = df[df['network'] == network]
            if len(network_shows) == 0:
                continue
                
            # Calculate success metrics using analyzer
            success_score = self.success_analyzer.calculate_network_success(network)
            renewal_rate = self.success_analyzer.calculate_renewal_rate(network)
            
            # Get list of shows for this network
            shows_list = network_shows['shows'].tolist()
            
            network_metrics[network] = {
                'show_count': len(network_shows),
                'shows': shows_list,
                'success_score': success_score
            }
            
        return network_metrics
        self.shows_df = self.shows_df.reset_index(drop=True)
        self.team_df = self.team_df.reset_index(drop=True)
        
        logger.info(f"Initialized UnifiedAnalyzer with {len(self.shows_df)} shows and {len(self.team_df)} team members")
        
    def get_filter_options(self) -> Dict[str, List[str]]:
        """Get available filter options from normalized data.
        
        Returns:
            Dict with lists of available source types, genres, and networks
        """
        return {
            'source_types': self._source_types,
            'genres': self._genres,
            'networks': self._networks
        }
        
    def get_market_snapshot(self, source_type: Optional[str] = None, genre: Optional[str] = None) -> Dict[str, Any]:
        """Get current market snapshot metrics.
        
        Args:
            source_type: Optional filter for source type
            genre: Optional filter for genre
            
        Returns:
            Dictionary with market metrics
        """
        # Start with filtered data
        df = self.shows_df.copy(deep=True)
        if source_type:
            df = df[df['source_type'] == source_type]
        if genre:
            df = df[df['genre'] == genre]
            
        # Calculate metrics
        total_shows = len(df)
        avg_success = self.success_analyzer.calculate_overall_success(df)
        
        # Source type distribution
        source_dist = df['source_type'].value_counts().to_dict()
        
        # Network preferences
        network_prefs = {}
        for network in self._networks:
            network_df = df[df['network'] == network]
            if len(network_df) > 0:
                network_prefs[network] = {
                    'total_shows': len(network_df),
                    'avg_success': self.success_analyzer.calculate_network_success(network)
                }
        
        return {
            'total_shows': total_shows,
            'avg_success': avg_success,
            'source_distribution': source_dist,
            'network_preferences': network_prefs
        }
        
    def get_package_suggestions(self, source_type: Optional[str] = None, genre: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get package suggestions based on creators with broad network appeal.
        
        Args:
            source_type: Optional filter for source type
            genre: Optional filter for genre
            
        Returns:
            List of suggestions with creator metrics and network breadth
        """
        # Start with all shows but track which ones match filters
        df = self.shows_df.copy(deep=True)
        filtered_shows = set()
        if source_type:
            filtered_shows.update(df[df['source_type'] == source_type]['shows'].tolist())
        if genre:
            genre_shows = set(df[df['genre'] == genre]['shows'].tolist())
            filtered_shows = filtered_shows & genre_shows if filtered_shows else genre_shows
            
        # If no shows match filters, return empty list
        if source_type or genre:
            if not filtered_shows:
                return []
            
        # Get creators who have at least one show matching the filters
        creators_with_filtered = set(self.team_df[self.team_df['show_name'].isin(filtered_shows)]['name']) if filtered_shows else set()
            
        # Get all shows by these creators (or all creators if no filters)
        merged_df = df.merge(self.team_df, left_on='shows', right_on='show_name', how='inner')
        if creators_with_filtered:
            merged_df = merged_df[merged_df['name'].isin(creators_with_filtered)]
            
        # Pre-calculate success scores for all shows
        show_scores = {}
        for show_title in merged_df['shows'].unique():
            show_df = merged_df[merged_df['shows'] == show_title].iloc[[0]]  # Get first occurrence
            show_scores[show_title] = self.success_analyzer.calculate_overall_success(show_df)
            
        suggestions = []
        
        # First, identify creator teams based on show overlap
        teams = []
        used_creators = set()
        
        # Group by creator to get their shows once
        creator_shows = {}
        for creator in merged_df['name'].unique():
            shows = set(merged_df[merged_df['name'] == creator]['shows'])
            if len(shows) >= 2:  # Only store creators with 2+ shows
                creator_shows[creator] = shows
        
        all_creators = list(creator_shows.keys())
        
        for i, creator1 in enumerate(all_creators):
            if creator1 in used_creators:
                continue
                
            creator1_shows = creator_shows[creator1]
            # Start a new team
            team = [(creator1, creator1_shows)]
            used_creators.add(creator1)
            
            # Look for team members with high show overlap
            for creator2 in all_creators[i+1:]:
                if creator2 in used_creators:
                    continue
                    
                creator2_shows = creator_shows[creator2]
                # Calculate show overlap in both directions
                intersection = creator1_shows & creator2_shows
                overlap1 = len(intersection) / len(creator1_shows)  # % of creator1's shows
                overlap2 = len(intersection) / len(creator2_shows)  # % of creator2's shows
                
                # Team up if they appear in 80% of each other's shows
                if overlap1 >= 0.8 and overlap2 >= 0.8:
                    team.append((creator2, creator2_shows))
                    used_creators.add(creator2)
            
            teams.append(team)
        
        # Process each team
        for team in teams:
            # Get all shows for the team
            team_shows = set().union(*[shows for _, shows in team])
            
            # Group shows by network
            network_shows = {}
            for show in team_shows:
                show_data = merged_df[merged_df['shows'] == show].iloc[0]
                network = show_data['network']
                if network not in network_shows:
                    network_shows[network] = []
                network_shows[network].append({
                    'title': show,
                    'success_score': show_scores[show]
                })
            
            # Only suggest teams with multiple networks
            if len(network_shows) >= 2:
                networks = []
                for network, shows in network_shows.items():
                    network_success = sum(s['success_score'] for s in shows) / len(shows)
                    networks.append({
                        'name': network,
                        'show_count': len(shows),
                        'shows': sorted(shows, key=lambda x: x['success_score'], reverse=True),
                        'success_score': network_success
                    })
                
                # Calculate overall success
                overall_success = sum(show_scores[show] for show in team_shows) / len(team_shows)
                suggestions.append({
                    'creator': ' & '.join(creator for creator, _ in team),
                    'overall_success': overall_success,
                    'network_count': len(networks),
                    'total_shows': len(team_shows),
                    'networks': sorted(networks, key=lambda x: (x['show_count'], x['success_score']), reverse=True),
                    'shows': sorted(list(team_shows))
                })
        
        # Sort primarily by network count, then by total shows, then by success
        return sorted(suggestions,
                     key=lambda x: (x['network_count'], x['total_shows'], x['overall_success']),
                     reverse=True)

    def get_creator_metrics(self, source_type: Optional[str] = None, genre: Optional[str] = None) -> Dict[str, Any]:
        """Get creator performance metrics.
        
        Args:
            source_type: Optional filter for source type
            genre: Optional filter for genre
            
        Returns:
            Dictionary with creator metrics
        """
        # Start with filtered data
        df = self.shows_df.copy(deep=True)
        if source_type:
            df = df[df['source_type'] == source_type]
        if genre:
            df = df[df['genre'] == genre]
            
        # Merge with team data
        merged_df = df.merge(self.team_df, left_on='shows', right_on='show_name', how='inner')
        
        # Calculate metrics for each creator
        creator_metrics = {}
        
        for creator in merged_df['name'].unique():
            creator_shows = merged_df[merged_df['name'] == creator]
            if len(creator_shows) == 0:
                continue
                
            # Calculate success score for creator's shows
            success_score = self.success_analyzer.calculate_overall_success(creator_shows)
            
            # Get list of shows
            shows_list = creator_shows['shows'].tolist()
            
            # Get preferred networks (where they've had most success)
            network_success = {}
            for network in creator_shows['network'].unique():
                network_shows = creator_shows[creator_shows['network'] == network]
                network_success[network] = {
                    'show_count': len(network_shows),
                    'success_score': self.success_analyzer.calculate_overall_success(network_shows),
                    'shows': network_shows['shows'].tolist()
                }
            
            creator_metrics[creator] = {
                'total_shows': len(creator_shows),
                'success_score': success_score,
                'shows': shows_list,
                'network_success': network_success
            }
        
        # Sort creators by success score
        sorted_creators = dict(sorted(creator_metrics.items(),
                                    key=lambda x: (x[1]['success_score'], x[1]['total_shows']),
                                    reverse=True))
        
        return sorted_creators

    def get_success_patterns(self, source_type: Optional[str] = None, genre: Optional[str] = None) -> Dict[str, Any]:
        """Get success patterns in the market.
        
        Args:
            source_type: Optional filter for source type
            genre: Optional filter for genre
            
        Returns:
            Dictionary with success pattern metrics
        """
        # Start with filtered data
        df = self.shows_df.copy(deep=True)
        if source_type:
            df = df[df['source_type'] == source_type]
        if genre:
            df = df[df['genre'] == genre]
            
        # Calculate genre + source type combinations
        combinations = df.groupby(['genre', 'source_type']).agg({
            'shows': 'count'
        }).reset_index()
        
        # Calculate success score for each combination
        combo_success = []
        for _, row in combinations.iterrows():
            combo_df = df[(df['genre'] == row['genre']) & 
                         (df['source_type'] == row['source_type'])]
            success = self.success_analyzer.calculate_overall_success(combo_df)
            # Get list of shows for this combination
            shows_list = combo_df['shows'].tolist()
            
            combo_success.append({
                'genre': row['genre'],
                'source_type': row['source_type'],
                'show_count': row['shows'],
                'success_score': success,
                'shows': shows_list
            })
        
        # Sort by success score
        combo_success.sort(key=lambda x: x['success_score'], reverse=True)
        
        return {
            'top_combinations': combo_success[:5],  # Top 5 combinations
        }
    
    def get_filtered_data(self, source_type: Optional[str] = None, genre: Optional[str] = None) -> pd.DataFrame:
        """Get filtered show data based on source type and genre.
        
        Args:
            source_type: Optional filter for source type
            genre: Optional filter for genre
            
        Returns:
            Filtered DataFrame with normalized values
        """
        filtered_df = self.shows_df.copy(deep=True)
        
        # Apply filters if not None or 'All'
        if source_type and source_type != 'All' and source_type in self._source_types:
            filtered_df = filtered_df[filtered_df['source_type'] == source_type]
        if genre and genre != 'All' and genre in self._genres:
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
            
            # Calculate real success metrics
            success_score = self.success_analyzer.calculate_network_success(network)
            renewal_rate = self.success_analyzer.calculate_renewal_rate(network)
            
            results.append({
                'network': network,
                'show_count': len(network_shows),
                'success_score': success_score,
                'renewal_rate': renewal_rate
            })
            
        return sorted(results, key=lambda x: x['show_count'], reverse=True)
        
    def analyze_creators(self, filtered_df: pd.DataFrame) -> List[Dict]:
        """Analyze creator performance for filtered shows.
        
        Args:
            filtered_df: Pre-filtered DataFrame of shows
            
        Returns:
            List of creator analysis results with:
            - name: Creator name
            - roles: List of roles
            - show_count: Number of shows
            - networks: List of networks worked with
            - success_score: Average success score of shows
        """
        # Get shows that match our filter
        show_names = set(filtered_df['shows'].tolist())
        
        # Filter team data to only include matching shows
        filtered_team = self.team_df[self.team_df['show_name'].isin(show_names)]
        
        # Group by creator name
        creator_stats = []
        for name, creator_data in filtered_team.groupby('name'):
            # Get unique roles and shows
            roles = creator_data['roles'].unique().tolist()
            shows = creator_data['show_name'].unique().tolist()
            
            # Get networks for these shows
            creator_shows = filtered_df[filtered_df['shows'].isin(shows)]
            networks = creator_shows['network'].unique().tolist()
            
            # Calculate average success score if available
            success_score = 0
            if self.success_analyzer:
                scores = [self.success_analyzer.calculate_success(show) 
                         for _, show in creator_shows.iterrows()]
                success_score = sum(scores) / len(scores) if scores else 0
            
            creator_stats.append({
                'name': name,
                'roles': roles,
                'show_count': len(shows),
                'networks': networks,
                'success_score': success_score
            })
        
        # Sort by show count and success score
        return sorted(creator_stats, 
                     key=lambda x: (x['show_count'], x['success_score']), 
                     reverse=True)