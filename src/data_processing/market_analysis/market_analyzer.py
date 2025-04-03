"""Market Analysis Module.

This module provides market overview analytics including network distribution and key metrics.
"""

import logging
from pathlib import Path
from typing import Dict, List, Tuple, Any
import pandas as pd
import plotly.graph_objects as go

from ..studio_performance.studio_analyzer import analyze_studio_relationships

logger = logging.getLogger(__name__)

class MarketAnalyzer:
    """Analyzer for market overview and network patterns."""
    
    def __init__(self, shows_df: pd.DataFrame, team_df: pd.DataFrame = None):
        """Initialize the analyzer.
        
        Args:
            shows_df: DataFrame containing show information
            team_df: Optional DataFrame containing team member information
            
        Raises:
            ValueError: If required columns are missing from shows_df
        """
        # Validate required columns
        required_cols = ['network', 'studio', 'success_score']
        missing_cols = [col for col in required_cols if col not in shows_df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns in shows_df: {missing_cols}")
        
        # Create deep copies to avoid modifying original data
        self.shows_df = shows_df.copy(deep=True)
        self.team_df = pd.DataFrame() if team_df is None else team_df.copy(deep=True)
        
        # Reset indices to ensure clean data
        self.shows_df = self.shows_df.reset_index(drop=True)
        self.team_df = self.team_df.reset_index(drop=True)
        
        # Convert and validate success_score
        self.shows_df['success_score'] = pd.to_numeric(self.shows_df['success_score'], errors='coerce')
        valid_scores = self.shows_df['success_score'].dropna()
        if len(valid_scores) > 0:
            invalid_scores = valid_scores[(valid_scores < 0) | (valid_scores > 100)]
            if len(invalid_scores) > 0:
                logger.warning(f"Found {len(invalid_scores)} success scores outside valid range [0-100]")
                self.shows_df.loc[invalid_scores.index, 'success_score'] = None
        
        # Log initial state
        logger.info("Market overview:")
        logger.info(f"  Total shows: {len(self.shows_df)}")
        logger.info(f"  Total networks: {len(self.shows_df['network'].unique())}")
        if not self.team_df.empty and 'name' in self.team_df.columns:
            logger.info(f"  Total creatives: {len(self.team_df['name'].unique())}")
    
    def create_network_chart(self) -> go.Figure:
        """Create a bar chart showing the distribution of shows across networks.
        The bars are color-coded by success score:
        - Green: High success (near 100)
        - Red: Low success (near 0)
        - Grey: No success data
        
        Returns:
            Plotly figure object
        """
        # Get network distribution
        shows_by_network = self.shows_df.groupby('network').size().sort_values(ascending=False)
        
        # Calculate average success score per network using the same groupby
        success_by_network = self.shows_df.groupby('network')['success_score'].mean()
        
        # Create colors array aligned with shows_by_network using Viridis colorscale
        import plotly.colors
        viridis = plotly.colors.sequential.Viridis
        colors = ['rgb(220, 220, 220)'] * len(shows_by_network)  # Lighter grey default
        hover_text = [f'{network}<br>Shows: {count}' for network, count in shows_by_network.items()]
        
        # Update colors for networks with success data
        for i, (network, count) in enumerate(shows_by_network.items()):
            if network in success_by_network and not pd.isna(success_by_network[network]):
                score = success_by_network[network]
                # Map score (0-100) to Viridis colorscale (0-1)
                color_idx = int((score/100) * (len(viridis)-1))
                colors[i] = viridis[color_idx]
                hover_text[i] += f'<br>Avg Success Score: {score:.1f}'
        
        # Create chart
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=list(shows_by_network.index),
            y=list(shows_by_network.values),
            name="Shows per Network",
            marker_color=colors,
            hovertext=hover_text,
            hoverinfo='text'
        ))
        
        # Update layout
        fig.update_layout(
            xaxis_title="Network",
            yaxis_title="Number of Shows",
            font_family="Source Sans Pro",
            showlegend=False,
            margin=dict(t=20)
        )
        
        return fig
    
    def generate_market_insights(self, shows_df: pd.DataFrame = None) -> Dict[str, Any]:
        """Generate insights about market patterns.
        
        Args:
            shows_df: Optional DataFrame to use instead of self.shows_df
            
        Returns:
            Dictionary containing market insights
        """
        df = shows_df if shows_df is not None else self.shows_df
        
        # Validate DataFrame
        if len(df) == 0:
            return {
                'total_shows': 0,
                'total_networks': 0,
                'network_success': {},
                'top_networks': [],
                'network_concentration': 0,
                'vertical_integration': 0,
                'high_success_networks': 0,
                'avg_success_score': 0,
                'top_success_network': 'None',
                'top_success_score': 0
            }
        
        # Clean network data
        df['network'] = df['network'].fillna('Unknown')
        df['network'] = df['network'].str.strip()
        df.loc[df['network'] == '', 'network'] = 'Unknown'
        
        # Calculate basic metrics
        total_shows = len(df)
        total_networks = len(df['network'].unique())
        
        # Calculate network concentration (% of shows in top 3 networks)
        network_counts = df['network'].value_counts()
        top_3_networks = network_counts.head(3)
        network_concentration = (top_3_networks.sum() / total_shows) * 100
        
        # Calculate vertical integration
        # A show is vertically integrated if its studio and network are related
        studio_network_matches = df.apply(
            lambda row: str(row['network']).lower() in str(row['studio']).lower() or 
                       str(row['studio']).lower() in str(row['network']).lower(),
            axis=1
        )
        vertical_integration = (studio_network_matches.sum() / total_shows) * 100
        
        # Calculate success metrics
        network_success = {}
        top_networks = []
        avg_success_score = 0
        top_success_network = 'None'
        top_success_score = 0
        high_success_networks = 0
        
        # Only calculate success metrics if we have valid scores
        valid_scores = df[df['success_score'].notna()]
        if len(valid_scores) > 0:
            # Get success rates by network
            network_metrics = valid_scores.groupby('network').agg({
                'success_score': ['mean', 'count']
            })
            network_metrics.columns = ['avg_success', 'show_count']
            network_metrics = network_metrics.reset_index()
            
            # Filter to networks with enough shows
            min_shows = 3  # Minimum shows for a network to be considered
            significant_networks = network_metrics[network_metrics['show_count'] >= min_shows]
            
            # Sort by success and get top networks
            top_networks_df = significant_networks.nlargest(5, 'avg_success')
            
            # Format results
            network_success = significant_networks.set_index('network')['avg_success'].to_dict()
            top_networks = [
                {
                    'network': row['network'],
                    'success_score': row['avg_success'],
                    'show_count': row['show_count']
                }
                for _, row in top_networks_df.iterrows()
            ]
            
            # Calculate additional success metrics
            avg_success_score = valid_scores['success_score'].mean()
            if top_networks:
                top_success_network = top_networks[0]['network']
                top_success_score = top_networks[0]['success_score']
            
            # Count networks with high success (>80)
            high_success_networks = len(significant_networks[significant_networks['avg_success'] > 80])
            
            logger.info(f"Calculated success rates for {len(network_success)} networks")
            logger.info(f"Top network: {top_success_network} ({top_success_score:.1f})")
        
        # Get studio insights using existing analyzer
        studio_insights = analyze_studio_relationships(df)
        
        # Calculate total creatives if team data is available
        total_creatives = 0
        if not self.team_df.empty and 'name' in self.team_df.columns:
            total_creatives = len(self.team_df['name'].unique())
        
        return {
            'total_shows': total_shows,
            'total_networks': total_networks,
            'total_creatives': total_creatives,
            'network_success': network_success,
            'top_networks': top_networks,
            'network_concentration': network_concentration,
            'vertical_integration': vertical_integration,
            'high_success_networks': high_success_networks,
            'avg_success_score': avg_success_score,
            'top_success_network': top_success_network,
            'top_success_score': top_success_score,
            'top_3_networks': top_3_networks.index.tolist(),
            'studio_insights': studio_insights
        }
