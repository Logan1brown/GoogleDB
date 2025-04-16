"""
Unified View Analyzer Component.
Provides data analysis and transformations for the unified dashboard view.

=== COLUMN NAME STANDARDS ===
1. Base Tables:
   - tmdb_id: Title ID from TMDB
   - network_id: Foreign key to network_list
   - studios: Array of foreign keys to studio_list
   - status_id: Foreign key to status_types

2. Views/APIs:
   - network_name: Network name (from network_id)
   - studio_names: Studio names (from studios array)
   - status_name: Status name (from status_id)
   - title: Title name (no transformation)
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
        try:
            st.write("Inside UnifiedAnalyzer __init__")
            """Initialize the analyzer.
            
            Args:
                success_analyzer: Optional SuccessAnalyzer instance
            """
            # Get normalized data from shows_analyzer
            st.write("Fetching data from shows_analyzer")
            try:
                self.titles_df, self.team_df, self.network_df = shows_analyzer.fetch_data()
                st.write(f"Data fetch successful - got {len(self.titles_df)} titles")
                st.write("Titles DataFrame columns:")
                st.write(self.titles_df.columns.tolist())
            except Exception as e:
                st.error(f"Error fetching data: {str(e)}")
                raise
            
            st.write("Converting episode_count")
            # Convert episode_count to float since it comes as strings
            self.titles_df['episode_count'] = pd.to_numeric(self.titles_df['episode_count'], errors='coerce')
            
            st.write("Setting up success analyzer")
            # Initialize success analyzer if not provided
            self.success_analyzer = success_analyzer or SuccessAnalyzer()
            # Initialize analyzer with title data
            self.success_analyzer.initialize_data(self.titles_df)
            
            st.write("Verifying columns")
            # Verify required columns exist after data cleaning
            required_columns = ['source_type_name', 'genre_name', 'network_name', 'title', 'episode_count', 'order_type_name']
            missing_columns = [col for col in required_columns if col not in self.titles_df.columns]
            if missing_columns:
                error_msg = f"Missing required columns in titles_df: {missing_columns}"
                st.error(error_msg)
                raise ValueError(error_msg)
            
            st.write("Getting network list")
            # Get filter options from titles data
            self._networks = sorted([n for n in self.titles_df['network_name'].dropna().unique() if n.strip()])
            
            st.write(f"Initialized UnifiedAnalyzer with {len(self.titles_df)} titles and {len(self.team_df)} team members")
        except Exception as e:
            st.error(f"Error in UnifiedAnalyzer init: {str(e)}")
            st.write("Type of error:", type(e))
            st.write("Error args:", e.args)
            raise
        
    def get_titles_by_episode_count(self, episode_count: int, source_type: Optional[str] = None, genre: Optional[str] = None) -> pd.DataFrame:
        """Get titles with a specific episode count.
        
        Args:
            episode_count: Number of episodes to filter by
            source_type: Optional filter for source type
            genre: Optional filter for genre
            
        Returns:
            DataFrame with titles matching the episode count
        """
        df = self.titles_df.copy(deep=True)
        
        # Verify required columns exist
        required_columns = ['source_type_name', 'genre_name', 'network_name', 'title', 'episode_count', 'order_type_name']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            logger.error(f"Missing required columns: {missing_columns}")
            return pd.DataFrame(columns=['title', 'network_name', 'genre_name', 'source_type_name', 'order_type_name', 'episode_count'])
        
        if source_type is not None and source_type != 'All':
            df = df[df['source_type_name'] == source_type]
        if genre is not None and genre != 'All':
            df = df[df['genre_name'] == genre]
            
        # Episode count should already be clean integers from analyze_titles.py
        if not pd.api.types.is_integer_dtype(df['episode_count']):
            logger.error(f"Episode count has wrong type: {df['episode_count'].dtype}")
            logger.error(f"Episode count sample: {df['episode_count'].head().tolist()}")
        
        # Filter for titles with required data
        has_order_type = df['order_type_name'].notna() & (df['order_type_name'] != '')
        has_episode_count = df['episode_count'].notna()
        
        # Keep titles that meet criteria
        reliable_df = df[has_order_type & has_episode_count]
        
        # Filter by episode count
        return reliable_df[reliable_df['episode_count'] == episode_count][['title', 'network_name', 'genre_name', 'source_type_name', 'order_type_name', 'episode_count']]
    
    def get_format_insights(self, source_type: Optional[str] = None, genre: Optional[str] = None) -> Dict[str, Any]:
        """Get insights about successful title formats.
        
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
        df = self.titles_df.copy(deep=True)
        
        # Verify required columns exist
        required_columns = ['source_type_name', 'genre_name', 'network_name', 'title', 'episode_count', 'order_type_name']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            logger.error(f"Missing required columns: {missing_columns}")
            return {
                'distribution': {'episodes': [], 'title_counts': []},
                'most_common': None,
                'avg_episodes': None
            }
            
        if source_type is not None and source_type != 'All':
            df = df[df['source_type_name'] == source_type]
        if genre is not None and genre != 'All':
            df = df[df['genre_name'] == genre]
            
        # Episode count should already be clean integers from analyze_titles.py
        # Filter for titles with required data
        has_order_type = df['order_type_name'].notna() & (df['order_type_name'] != '')
        has_episode_count = df['episode_count'].notna()
        
        # Keep titles that meet criteria
        reliable_df = df[has_order_type & has_episode_count]
        
        # Calculate success score for each title
        reliable_df['success_score'] = reliable_df.apply(self.success_analyzer.calculate_success, axis=1)
        
        # Get actual episode counts and their frequencies
        episode_counts = reliable_df['episode_count'].value_counts().sort_index()
        
        most_common_eps = int(episode_counts.index[episode_counts.argmax()]) if not episode_counts.empty else None
        
        episode_insights = {
            'distribution': {
                'episodes': episode_counts.index.tolist(),
                'title_counts': episode_counts.values.tolist()
            },
            'most_common': most_common_eps,
            'avg_episodes': float(reliable_df['episode_count'].mean()) if not reliable_df.empty else None
        }
        
        # Analyze series by order type
        # First normalize the order_type values
        reliable_df['order_type_name'] = reliable_df['order_type_name'].fillna('')
        reliable_df['order_type_name'] = reliable_df['order_type_name'].str.strip()
        
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
        reliable_df['order_type_name'] = reliable_df['order_type_name'].str.lower().map(lambda x: order_type_map.get(x, x))
        
        # Filter out pilots and empty values
        has_order = (
            (reliable_df['order_type_name'] != 'Pilot') & 
            (reliable_df['order_type_name'] != '') & 
            (reliable_df['order_type_name'].notna())
        )
        reliable_df = reliable_df[has_order]
        
        # Get series type counts from order_type_name
        order_type_counts = reliable_df['order_type_name'].value_counts()
        
        # Copy to avoid modifying original
        series_type_counts = order_type_counts.copy()
        
        # Get non-zero counts for cleaner output
        non_zero_types = [order_type for order_type in series_type_counts.index
                         if series_type_counts[order_type] > 0]
        
        # Calculate total titles for percentages
        total_titles = series_type_counts.sum()
        
        # Format counts and percentages
        type_insights = {
            'counts': {
                order_type: int(series_type_counts[order_type])
                for order_type in non_zero_types
            },
            'percentages': {
                order_type: float(series_type_counts[order_type] / total_titles * 100)
                for order_type in non_zero_types
            }
        }
        
        # Analyze by network
        network_insights = {}
        for network in reliable_df['network_name'].dropna().unique():
            network_df = reliable_df[reliable_df['network_name'] == network]
            # Get episode count data
            valid_eps = network_df['episode_count'].dropna()
            
            if len(valid_eps) > 0:
                # Get preferred series type based on frequency
                type_counts = network_df['order_type_name'].value_counts()
                if not type_counts.empty:
                    preferred_type = type_counts.index[0]  # Most frequent type
                    type_percentage = (type_counts[0] / len(network_df)) * 100
                    # Only consider it a preference if it's more than 50% of titles
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
            'series_insights': type_insights,  # This contains the limited vs ongoing breakdown
            'network_insights': network_insights,
            'total_titles_analyzed': len(reliable_df)
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
        df = self.titles_df.copy(deep=True)
        
        if source_type:
            df = df[df['source_type_name'] == source_type]
        if genre:
            df = df[df['genre_name'] == genre]
            
        # Calculate metrics for each network
        network_metrics = {}
        
        for network in self._networks:
            network_titles = df[df['network_name'] == network]
            if len(network_titles) == 0:
                continue
                
            # Calculate success metrics using analyzer
            success_score = self.success_analyzer.calculate_network_success(network)
            renewal_rate = self.success_analyzer.calculate_renewal_rate(network)
            
            # Get list of titles for this network
            title_list = network_titles['title'].tolist()
            
            network_metrics[network] = {
                'title_count': len(network_titles),
                'titles': title_list,
                'success_score': success_score
            }
            
        return network_metrics
        self.titles_df = self.titles_df.reset_index(drop=True)
        self.team_df = self.team_df.reset_index(drop=True)
        
        logger.info(f"Initialized UnifiedAnalyzer with {len(self.titles_df)} titles and {len(self.team_df)} team members")
        
    def get_filter_options(self) -> Dict[str, List[str]]:
        """Get available filter options from normalized data.
        
        Returns:
            Dict with lists of available source types, genres, and networks
            that are currently in use by shows in the database.
        """
        return {
            'source_types': sorted([s for s in self.titles_df['source_type_name'].dropna().unique() if s.strip()]),
            'genres': sorted([g for g in self.titles_df['genre_name'].dropna().unique() if g.strip()]),
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
        df = self.titles_df.copy(deep=True)
        if source_type:
            df = df[df['source_type_name'] == source_type]
        if genre:
            df = df[df['genre_name'] == genre]
            
        # Calculate metrics
        total_titles = len(df)
        avg_success = self.success_analyzer.calculate_overall_success(df)
        
        # Source type distribution
        source_dist = df['source_type_name'].value_counts().to_dict()
        
        # Network preferences
        network_prefs = {}
        for network in self._networks:
            network_df = df[df['network_name'] == network]
            if len(network_df) > 0:
                network_prefs[network] = {
                    'total_titles': len(network_df),
                    'avg_success': self.success_analyzer.calculate_network_success(network)
                }
        
        return {
            'total_titles': total_titles,
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
        # Start with all titles but track which ones match filters
        df = self.titles_df.copy(deep=True)
        filtered_titles = set()
        if source_type:
            filtered_titles.update(df[df['source_type_name'] == source_type]['title'].tolist())
        if genre:
            genre_titles = set(df[df['genre_name'] == genre]['title'].tolist())
            filtered_titles = filtered_titles & genre_titles if filtered_titles else genre_titles
            
        # If no titles match filters, return empty list
        if source_type or genre:
            if not filtered_titles:
                return []
            
        # Get creators who have at least one title matching the filters
        creators_with_filtered = set(self.team_df[self.team_df['title'].isin(filtered_titles)]['name']) if filtered_titles else set()
            
        # Get all titles by these creators (or all creators if no filters)
        merged_df = df.merge(self.team_df, left_on='title', right_on='title', how='inner')
        if creators_with_filtered:
            merged_df = merged_df[merged_df['name'].isin(creators_with_filtered)]
            
        # Pre-calculate success scores for all titles
        title_scores = {}
        for title_name in merged_df['title'].unique():
            title_df = merged_df[merged_df['title'] == title_name].iloc[[0]]  # Get first occurrence
            title_scores[title_name] = self.success_analyzer.calculate_overall_success(title_df)
            
        suggestions = []
        
        # First, identify creator teams based on title overlap
        teams = []
        used_creators = set()
        
        # Group by creator to get their titles once
        creator_titles = {}
        for creator in merged_df['name'].unique():
            titles = set(merged_df[merged_df['name'] == creator]['title'])
            if len(titles) >= 2:  # Only store creators with 2+ titles
                creator_titles[creator] = titles
        
        all_creators = list(creator_titles.keys())
        
        for i, creator1 in enumerate(all_creators):
            if creator1 in used_creators:
                continue
                
            creator1_titles = creator_titles[creator1]
            # Start a new team
            team = [(creator1, creator1_titles)]
            used_creators.add(creator1)
            
            # Look for team members with high title overlap
            for creator2 in all_creators[i+1:]:
                if creator2 in used_creators:
                    continue
                    
                creator2_titles = creator_titles[creator2]
                # Calculate title overlap in both directions
                intersection = creator1_titles & creator2_titles
                overlap1 = len(intersection) / len(creator1_titles)  # % of creator1's titles
                overlap2 = len(intersection) / len(creator2_titles)  # % of creator2's titles
                
                # Team up if they appear in 80% of each other's titles
                if overlap1 >= 0.8 and overlap2 >= 0.8:
                    team.append((creator2, creator2_titles))
                    used_creators.add(creator2)
            
            teams.append(team)
        
        # Process each team
        for team in teams:
            # Get all titles for the team
            team_titles = set().union(*[titles for _, titles in team])
            
            # Group titles by network
            network_titles = {}
            for title in team_titles:
                title_data = merged_df[merged_df['title'] == title].iloc[0]
                network = title_data['network_name']
                if network not in network_titles:
                    network_titles[network] = []
                network_titles[network].append({
                    'title': title,
                    'success_score': title_scores[title]
                })
            
            # Only suggest teams with multiple networks
            if len(network_titles) >= 2:
                networks = []
                for network, titles in network_titles.items():
                    network_success = sum(s['success_score'] for s in titles) / len(titles)
                    networks.append({
                        'name': network,
                        'title_count': len(titles),
                        'titles': sorted(titles, key=lambda x: x['success_score'], reverse=True),
                        'success_score': network_success
                    })
                
                # Calculate overall success
                overall_success = sum(title_scores[title] for title in team_titles) / len(team_titles)
                suggestions.append({
                    'creator': ' & '.join(creator for creator, _ in team),
                    'overall_success': overall_success,
                    'network_count': len(networks),
                    'total_titles': len(team_titles),
                    'networks': sorted(networks, key=lambda x: (x['title_count'], x['success_score']), reverse=True),
                    'titles': sorted(list(team_titles))
                })
        
        # Sort primarily by network count, then by total titles, then by success
        return sorted(suggestions,
                     key=lambda x: (x['network_count'], x['total_titles'], x['overall_success']),
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
        df = self.titles_df.copy(deep=True)
        if source_type:
            df = df[df['source_type_name'] == source_type]
        if genre:
            df = df[df['genre_name'] == genre]
            
        # Merge with team data
        merged_df = df.merge(self.team_df, left_on='title', right_on='title', how='inner')
        
        # Calculate metrics for each creator
        creator_metrics = {}
        
        for creator in merged_df['name'].unique():
            creator_titles = merged_df[merged_df['name'] == creator]
            if len(creator_titles) == 0:
                continue
                
            # Calculate success score for creator's titles
            success_score = self.success_analyzer.calculate_overall_success(creator_titles)
            
            # Get list of titles
            title_list = creator_titles['title'].tolist()
            
            # Get preferred networks (where they've had most success)
            network_success = {}
            for network in creator_titles['network_name'].unique():
                network_titles = creator_titles[creator_titles['network_name'] == network]
                network_success[network] = {
                    'title_count': len(network_titles),
                    'success_score': self.success_analyzer.calculate_overall_success(network_titles),
                    'titles': network_titles['title'].tolist()
                }
            
            creator_metrics[creator] = {
                'total_titles': len(creator_titles),
                'success_score': success_score,
                'titles': title_list,
                'network_success': network_success
            }
        
        # Sort creators by success score
        sorted_creators = dict(sorted(creator_metrics.items(),
                                    key=lambda x: (x[1]['success_score'], x[1]['total_titles']),
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
        df = self.titles_df.copy(deep=True)
        
        # Verify required columns exist
        required_columns = ['source_type_name', 'genre_name', 'title']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            logger.error(f"Missing required columns: {missing_columns}")
            return {'top_combinations': []}
            
        if source_type:
            df = df[df['source_type_name'] == source_type]
        if genre:
            df = df[df['genre_name'] == genre]
            
        # Calculate genre + source type combinations
        combinations = df.groupby(['genre_name', 'source_type_name']).agg(
            title_count=('title', 'count')
        ).reset_index()
        
        # Calculate success score for each combination
        combo_success = []
        for _, row in combinations.iterrows():
            combo_df = df[(df['genre_name'] == row['genre_name']) & 
                         (df['source_type_name'] == row['source_type_name'])]
            success = self.success_analyzer.calculate_overall_success(combo_df)
            # Get list of titles for this combination
            titles_list = combo_df['title'].tolist()
            
            combo_success.append({
                'genre_name': row['genre_name'],
                'source_type_name': row['source_type_name'],
                'title_count': row['title_count'],
                'success_score': success,
                'titles': titles_list
            })
        
        # Sort by success score
        combo_success.sort(key=lambda x: x['success_score'], reverse=True)
        
        return {
            'top_combinations': combo_success[:5],  # Top 5 combinations
        }
    
    def get_filtered_data(self, source_type: Optional[str] = None, genre: Optional[str] = None) -> pd.DataFrame:
        """Get filtered title data based on source type and genre.
        
        Args:
            source_type: Optional filter for source type
            genre: Optional filter for genre
            
        Returns:
            Filtered DataFrame with normalized values
        """
        filtered_df = self.titles_df.copy(deep=True)
        
        # Apply filters if not None or 'All'
        if source_type and source_type != 'All':
            filtered_df = filtered_df[filtered_df['source_type_name'] == source_type]
        if genre and genre != 'All':
            filtered_df = filtered_df[filtered_df['genre_name'] == genre]
            
        return filtered_df
        
    def analyze_networks(self, filtered_df: pd.DataFrame) -> List[Dict]:
        """Analyze network performance for filtered titles.
        
        Args:
            filtered_df: Pre-filtered DataFrame of titles
            
        Returns:
            List of network analysis results
        """
        results = []
        for network in filtered_df['network_name'].unique():
            network_titles = filtered_df[filtered_df['network_name'] == network]
            
            # Calculate real success metrics
            success_score = self.success_analyzer.calculate_network_success(network)
            renewal_rate = self.success_analyzer.calculate_renewal_rate(network)
            
            results.append({
                'network_name': network,
                'title_count': len(network_titles),
                'success_score': success_score,
                'renewal_rate': renewal_rate
            })
            
        return sorted(results, key=lambda x: x['title_count'], reverse=True)
        
    def analyze_creators(self, filtered_df: pd.DataFrame) -> List[Dict]:
        """Analyze creator performance for filtered titles.
        
        Args:
            filtered_df: Pre-filtered DataFrame of titles
            
        Returns:
            List of creator analysis results with:
            - name: Creator name
            - roles: List of roles
            - title_count: Number of titles
            - networks: List of networks worked with
            - success_score: Average success score of titles
        """
        # Get titles that match our filter
        title_names = set(filtered_df['title'].tolist())
        
        # Filter team data to only include matching titles
        filtered_team = self.team_df[self.team_df['title'].isin(title_names)]
        
        # Group by creator name
        creator_stats = []
        for name, creator_data in filtered_team.groupby('name'):
            # Get unique roles and titles
            roles = creator_data['roles'].unique().tolist()
            titles = creator_data['title'].unique().tolist()
            
            # Get networks for these titles
            creator_titles = filtered_df[filtered_df['title'].isin(titles)]
            networks = creator_titles['network_name'].unique().tolist()
            
            # Calculate average success score if available
            success_score = 0
            if self.success_analyzer:
                scores = [self.success_analyzer.calculate_success(title) 
                         for _, title in creator_titles.iterrows()]
                success_score = sum(scores) / len(scores) if scores else 0
            
            creator_stats.append({
                'name': name,
                'roles': roles,
                'title_count': len(titles),
                'networks': networks,
                'success_score': success_score
            })
        
        # Sort by title count and success score
        return sorted(creator_stats, 
                     key=lambda x: (x['title_count'], x['success_score']), 
                     reverse=True)