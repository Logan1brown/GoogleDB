"""Genre Analysis Module.

This module provides specialized analysis of genre patterns with automated insights.
"""

import logging
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

logger = logging.getLogger(__name__)

class GenreAnalyzer:
    """Analyzer for genre patterns and trends."""
    
    def __init__(self, shows_df: pd.DataFrame):
        """Initialize the analyzer.
        
        Args:
            shows_df: DataFrame containing show information
        """
        self.shows_df = shows_df
        
        # Log genre distribution
        logger.info("Genre distribution:")
        genre_counts = self.shows_df['genre'].value_counts()
        for genre, count in genre_counts.items():
            logger.info(f"  {genre}: {count} shows")
    
    def generate_genre_insights(self) -> Dict:
        """Generate key insights about genre patterns.
        
        Returns:
            Dictionary containing various genre insights
        """
        # Network genre focus
        network_genre = pd.crosstab(
            self.shows_df['network'],
            self.shows_df['genre']
        )
        
        # Calculate percentages
        network_genre_pct = network_genre.div(network_genre.sum(axis=1), axis=0) * 100
        
        # Find dominant genres for networks with sufficient data
        MIN_SHOWS = 3  # Minimum number of shows needed for meaningful analysis
        dominant_genres = {}
        for network in network_genre_pct.index:
            total_shows = network_genre.loc[network].sum()
            if total_shows >= MIN_SHOWS:
                network_data = network_genre_pct.loc[network]
                dominant = network_data.nlargest(2)
                if len(dominant) >= 2:  # Only include if we have at least 2 genres
                    dominant_genres[network] = {
                        'primary': (dominant.index[0], dominant.iloc[0]),
                        'secondary': (dominant.index[1], dominant.iloc[1])
                    }
        
        # Calculate genre diversity (number of genres with >10% share)
        def count_major_genres(row):
            return (row > 10).sum()
            
        genre_diversity = network_genre_pct.apply(count_major_genres, axis=1)
        most_diverse = genre_diversity.nlargest(5)
        least_diverse = genre_diversity.nsmallest(5)
        
        logger.info("\nNetwork diversity scores:")
        for network, score in most_diverse.items():
            logger.info(f"{network}: {score} major genres")
        
        # Find unique patterns for networks with sufficient data
        unique_patterns = []
        for network in network_genre_pct.index:
            total_shows = network_genre.loc[network].sum()
            if total_shows >= MIN_SHOWS:
                network_data = network_genre_pct.loc[network]
                overall_avg = network_genre_pct.mean()
                differences = network_data - overall_avg
                significant_diff = differences[abs(differences) > 15]
                if not significant_diff.empty:
                    for genre, diff in significant_diff.items():
                        unique_patterns.append({
                            'network': network,
                            'genre': genre,
                            'difference': diff,
                            'network_pct': network_data[genre],
                            'overall_avg': overall_avg[genre],
                            'total_shows': total_shows
                        })
        
        return {
            'network_genre_matrix': network_genre,
            'network_genre_percentages': network_genre_pct,
            'dominant_genres': dominant_genres,
            'genre_diversity': {
                'most_diverse': most_diverse.to_dict(),
                'least_diverse': least_diverse.to_dict()
            },
            'unique_patterns': unique_patterns
        }
    
    def create_genre_heatmap(self) -> None:
        """Create an enhanced genre heatmap with insights."""
        insights = self.generate_genre_insights()
        
        # Create figure with secondary y-axis
        fig = make_subplots(
            rows=1, cols=2,
            column_widths=[0.7, 0.3],
            subplot_titles=('Genre Distribution by Network', 'Key Insights'),
            specs=[[{"type": "heatmap"}, {"type": "table"}]]
        )
        
        # Filter and sort networks
        network_genre_pct = insights['network_genre_percentages']
        network_genre = insights['network_genre_matrix']
        
        # Filter out networks with too few shows
        MIN_SHOWS = 3
        valid_networks = network_genre.sum(axis=1) >= MIN_SHOWS
        filtered_data = network_genre_pct[valid_networks]
        
        # Sort by diversity score
        diversity_scores = filtered_data.apply(lambda row: (row > 10).sum(), axis=1)
        sorted_networks = diversity_scores.sort_values(ascending=False).index
        sorted_data = filtered_data.loc[sorted_networks]
        
        # Add heatmap
        heatmap = go.Heatmap(
            z=sorted_data.values,
            x=sorted_data.columns,
            y=sorted_data.index,
            colorscale='Viridis',
            colorbar=dict(title='Percentage of Network\'s Shows')
        )
        fig.add_trace(heatmap, row=1, col=1)
        
        # Prepare insights text
        insights_text = []
        
        # Add diversity insights
        most_diverse = insights['genre_diversity']['most_diverse']
        network_genre_pct = insights['network_genre_percentages']
        
        insights_text.append(f"Most Genre-Diverse Networks:")
        for network, score in most_diverse.items():
            insights_text.append(f"• {network}: {score} genres with >10% share")
        
        # Add dominant genre insights
        insights_text.append("\nNetwork Specializations:")
        # Sort by percentage
        specializations = [
            (network, data['primary'])
            for network, data in insights['dominant_genres'].items()
            if data['primary'][1] > 40  # Only show strong preferences
        ]
        specializations.sort(key=lambda x: x[1][1], reverse=True)  # Sort by percentage
        for network, primary in specializations:
            insights_text.append(f"• {network}: {primary[0]} ({primary[1]:.0f}%)")
        
        # Add unique pattern insights
        insights_text.append("\nUnique Patterns:")
        for pattern in insights['unique_patterns']:
            if pattern['difference'] > 20:  # Only show strong differences
                insights_text.append(
                    f"• {pattern['network']}: {pattern['difference']:.0f}% "
                    f"more {pattern['genre']} than average"
                )
        
        # Add table
        fig.add_trace(
            go.Table(
                header=dict(
                    values=['Key Insights'],
                    align='left',
                    font=dict(size=12)
                ),
                cells=dict(
                    values=[insights_text],
                    align='left',
                    font=dict(size=11)
                )
            ),
            row=1, col=2
        )
        
        # Update layout
        fig.update_layout(
            title='Network Genre Analysis',
            showlegend=False,
            height=800
        )
        
        # Save to HTML file
        output_dir = Path('output/visualizations')
        output_dir.mkdir(parents=True, exist_ok=True)
        fig.write_html(output_dir / 'genre_analysis.html')
