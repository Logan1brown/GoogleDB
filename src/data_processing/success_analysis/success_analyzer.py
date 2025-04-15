"""
Success Analyzer Component.
Calculates success metrics for shows based on reliable data.

=== STANDARDIZED COLUMN NAMES ===
All views now use standardized column names:
- 'title' for show names
- 'network_name' for networks
- 'studio_names' for studios
- 'status_name' for status
"""
from dataclasses import dataclass
from typing import Dict, List, Optional
import pandas as pd
import numpy as np

from ..external.tmdb.tmdb_models import ShowStatus


@dataclass
class SuccessConfig:
    """Configuration for success calculations."""
    # Season achievements (40%)
    SEASON2_VALUE: int = 40  # Show renewed for S2
    ADDITIONAL_SEASON_VALUE: int = 20  # Each season after S2
    
    # Episode volume scoring (40% of total)
    EPISODE_BASE_POINTS: int = 20     # Points awarded for reaching min threshold
    EPISODE_BONUS_POINTS: int = 20    # Additional points for reaching high threshold
    EPISODE_MIN_THRESHOLD: int = 8    # Minimum episodes needed for base points
    EPISODE_BONUS_THRESHOLD: int = 10  # Episodes needed for bonus points
    
    # Status modifiers
    STATUS_MODIFIERS: Dict[str, float] = None
    DEVELOPMENT_SCORE: float = 85.0  # Base score for shows in development/production
    
    def __post_init__(self):
        self.STATUS_MODIFIERS = {
            'Returning Series': 1.2,  # 20% bonus for active shows
            'Ended': 1.0,            # Base multiplier for completed shows
            'Canceled': 0.8,         # 20% penalty for canceled shows
            'In Production': 1.0,    # Neutral for shows in production
            'Pilot': 1.0,           # Neutral for pilots
            'In Development': 1.0,   # Neutral for shows in development
        }


class SuccessAnalyzer:
    """
    Analyzes show success based on reliable metrics.
    Only calculates scores for shows with reliable data (Returning, Ended, Canceled).
    """
    def __init__(self, config: Optional[SuccessConfig] = None):
        self.config = config or SuccessConfig()
        self.shows_df = None
        
    def initialize_data(self, shows_df: pd.DataFrame):
        """Initialize analyzer with show data."""
        self.shows_df = shows_df.copy()
        
    def calculate_network_success(self, network: str) -> float:
        """Calculate success score for a specific network.
        
        Args:
            network: Name of the network
            
        Returns:
            Success score as percentage (0-100)
        """
        if self.shows_df is None:
            return 85.0  # Default if no data
            
        network_shows = self.shows_df[self.shows_df['network'] == network]
        if len(network_shows) == 0:
            return 85.0
            
        # Calculate success based on renewal status and episode count
        success_scores = []
        for _, show in network_shows.iterrows():
            score = 0
            
            # Season achievements (40%)
            seasons = pd.to_numeric(show.get('tmdb_seasons', 0), errors='coerce')
            if pd.notna(seasons) and seasons >= 2:
                score += self.config.SEASON2_VALUE
                extra_seasons = seasons - 2
                if extra_seasons > 0:
                    score += min(extra_seasons * self.config.ADDITIONAL_SEASON_VALUE, 40)
                    
            # Episode volume (40%)
            episodes = pd.to_numeric(show.get('tmdb_total_eps', 0), errors='coerce')
            if pd.notna(episodes) and episodes >= self.config.EPISODE_MIN_THRESHOLD:
                score += self.config.EPISODE_BASE_POINTS
                if episodes >= self.config.EPISODE_BONUS_THRESHOLD:
                    score += self.config.EPISODE_BONUS_POINTS
                    
            # Status modifier
            status = show.get('status', 'Unknown')
            score *= self.config.STATUS_MODIFIERS.get(status, 1.0)
            
            success_scores.append(min(score, 100))
            
        return np.mean(success_scores) if success_scores else 85.0
        
    def calculate_overall_success(self, df: Optional[pd.DataFrame] = None) -> float:
        """Calculate overall success score for a set of shows.
        
        Args:
            df: Optional DataFrame to calculate success for. If None, uses all shows.
            
        Returns:
            Success score as percentage (0-100)
        """
        if df is None:
            if self.shows_df is None:
                return 85.0  # Default if no data
            df = self.shows_df
            
        if len(df) == 0:
            return 85.0
            
        # Calculate success based on renewal status and episode count
        success_scores = []
        for _, show in df.iterrows():
            score = 0
            
            # Season achievements (40%)
            seasons = pd.to_numeric(show.get('tmdb_seasons', 0), errors='coerce')
            if pd.notna(seasons) and seasons >= 2:
                score += self.config.SEASON2_VALUE
                extra_seasons = seasons - 2
                if extra_seasons > 0:
                    score += min(extra_seasons * self.config.ADDITIONAL_SEASON_VALUE, 40)
                    
            # Episode volume (40%)
            episodes = pd.to_numeric(show.get('tmdb_total_eps', 0), errors='coerce')
            if pd.notna(episodes) and episodes >= self.config.EPISODE_MIN_THRESHOLD:
                score += self.config.EPISODE_BASE_POINTS
                if episodes >= self.config.EPISODE_BONUS_THRESHOLD:
                    score += self.config.EPISODE_BONUS_POINTS
                    
            # Status modifier
            status = show.get('status', 'Unknown')
            score *= self.config.STATUS_MODIFIERS.get(status, 1.0)
            
            success_scores.append(min(score, 100))
            
        return np.mean(success_scores) if success_scores else 85.0

    def calculate_renewal_rate(self, network: str) -> float:
        """Calculate renewal rate for a specific network.
        
        Args:
            network: Name of the network
            
        Returns:
            Renewal rate as percentage (0-100)
        """
        if self.shows_df is None:
            return 90.0  # Default if no data
            
        network_shows = self.shows_df[self.shows_df['network'] == network]
        if len(network_shows) == 0:
            return 90.0
            
        # Count shows that got renewed (2+ seasons)
        network_shows['seasons'] = pd.to_numeric(network_shows['tmdb_seasons'], errors='coerce')
        renewed = network_shows[network_shows['seasons'] >= 2]
        return (len(renewed) / len(network_shows)) * 100
        
    def analyze_market(self, shows_df: pd.DataFrame) -> Dict:
        """
        Calculate success metrics for all reliable shows in the market.
        Returns thresholds and tiers based on the highest scores.
        """
        # Filter to reliable shows only
        reliable_shows = shows_df[shows_df['tmdb_status'].isin(ShowStatus.RELIABLE)]
        if reliable_shows.empty:
            return {
                'max_score': 0,
                'high_threshold': 0,
                'medium_threshold': 0,
                'shows': {}
            }
            
        # Calculate scores for all reliable shows
        scores = []
        for _, show in reliable_shows.iterrows():
            score = self.calculate_success(show)
            # === CRITICAL: Column Name Difference ===
            # We're working with the shows sheet here, which uses 'shows' column
            # Do NOT use 'show_name' which is only for the show_team sheet
            scores.append({
                'show_id': show['tmdb_id'],
                'name': show['title'],  # Title column from standardized views
                'score': score
            })
            
        # Get max score and set tier thresholds
        max_score = max(s['score'] for s in scores) if scores else 0
        return {
            'max_score': max_score,
            'high_threshold': max_score * 0.8,  # High: Top 20%
            'medium_threshold': max_score * 0.5,  # Medium: Top 50%
            'shows': {
                s['show_id']: {
                    'name': s['name'],
                    'score': s['score'],
                    'tier': self._get_tier(s['score'], max_score)
                }
                for s in scores
            }
        }
        
    def calculate_success(self, show: pd.Series) -> float:
        """Calculate success score for a single show."""
        # For shows in development/production, use base development score
        if show['tmdb_status'] in ShowStatus.IN_DEVELOPMENT:
            return self.config.DEVELOPMENT_SCORE
        elif show['tmdb_status'] not in ShowStatus.RELIABLE:
            return 0
            
        score = 0
        
        # Season achievements
        if pd.notna(show['tmdb_seasons']):
            seasons = int(show['tmdb_seasons'])
            if seasons >= 2:
                score += self.config.SEASON2_VALUE
                extra_seasons = seasons - 2
                if extra_seasons > 0:
                    score += min(extra_seasons * self.config.ADDITIONAL_SEASON_VALUE, 40)  # Cap extra seasons bonus at 40 points
                
        # Episode volume points (40% of total possible)
        if pd.notna(show['tmdb_avg_eps']):
            try:
                avg_eps = float(show['tmdb_avg_eps'])
                if avg_eps >= self.config.EPISODE_BONUS_THRESHOLD:
                    # High volume show (10+ episodes)
                    score += self.config.EPISODE_BASE_POINTS + self.config.EPISODE_BONUS_POINTS
                elif avg_eps >= self.config.EPISODE_MIN_THRESHOLD:
                    # Standard volume show (8-9 episodes)
                    score += self.config.EPISODE_BASE_POINTS
                # No points if below minimum
            except (ValueError, TypeError):
                logger.warning(f"Invalid episode count value: {show['tmdb_avg_eps']}")
            
        # Apply status modifier
        modifier = self.config.STATUS_MODIFIERS.get(show['tmdb_status'], 1.0)
        score *= modifier
        
        return min(100, max(0, score))  # Cap at 100, don't allow negative
        
    def _get_tier(self, score: float, max_score: float) -> str:
        """Get success tier based on score relative to max."""
        if score >= max_score * 0.8:
            return 'high'
        elif score >= max_score * 0.5:
            return 'medium'
        return 'low'
