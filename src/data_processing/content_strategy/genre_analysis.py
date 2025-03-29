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
from src.dashboard.utils.style_config import COLORS, FONTS
from src.dashboard.utils.templates.insight import InsightTemplate
from src.dashboard.utils.templates.dual_analysis import DualAnalysisTemplate

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
    
    def create_genre_chart(self) -> go.Figure:
        """Create a bar chart showing the distribution of shows across genres.
        Uses InsightTemplate for consistent styling and insights.
        
        Returns:
            Plotly figure object with genre distribution and insights
        """
        # Get insights
        insights = self.generate_genre_insights()
        
        # Create insight text
        insight_text = f"{insights['top_genre']} leads with {insights['top_genre_share']}% of shows"
        
        # Create figure with template
        fig = InsightTemplate.create_insight_slide(
            title="Genre Distribution",
            insight=insight_text,
            chart_type='bar'
        )
        
        # Add KPI metrics
        InsightTemplate.add_kpi_banner(fig, {
            "Total Shows": str(insights['total_shows']),
            "Unique Genres": str(insights['unique_genres']),
            f"Top Genre ({insights['top_genre']})": f"{insights['top_genre_count']} shows"
        })
        
        # Get genre distribution
        genre_counts = self.shows_df['genre'].value_counts()
        total_shows = len(self.shows_df)
        genre_pcts = (genre_counts / total_shows * 100).round(1)
        
        # Create hover text
        hover_text = [f"{genre}<br>{count} shows<br>{pct}% of total" 
                     for genre, count, pct in zip(genre_counts.index, 
                                                genre_counts.values,
                                                genre_pcts)]
        
        # Add bar chart
        fig.add_trace(go.Bar(
            x=list(genre_counts.index),
            y=list(genre_counts.values),
            name="Shows per Genre",
            hovertext=hover_text,
            hoverinfo="text",
            marker_color=COLORS['chart']['sequence'][0]
        ))
        
        # Update axes
        fig.update_xaxes(title="Genre")
        fig.update_yaxes(title="Number of Shows")
        
        return fig
    
    def generate_genre_insights(self) -> Dict:
        """Generate key insights about genre patterns.
        
        Returns:
            Dictionary containing:
            - total_shows: Total number of shows analyzed
            - unique_genres: Number of distinct genres
            - top_genre: Most common genre
            - top_genre_count: Number of shows in top genre
            - top_genre_share: Percentage of shows in top genre
            - network_leaders: Networks leading in specific genres
            - genre_diversity: Networks with most/least genre diversity
            - unique_patterns: Notable genre specializations
        """
        # Basic counts
        total_shows = len(self.shows_df)
        genre_counts = self.shows_df['genre'].value_counts()
        unique_genres = len(genre_counts)
        
        # Top genre stats
        top_genre = genre_counts.index[0]
        top_genre_count = genre_counts[top_genre]
        top_genre_share = (top_genre_count / total_shows) * 100
        
        # Network genre analysis
        network_genre = pd.crosstab(
            self.shows_df['network'],
            self.shows_df['genre']
        )
        
        # Calculate percentages
        network_genre_pct = network_genre.div(network_genre.sum(axis=1), axis=0) * 100
        
        # Find network leaders (networks with highest share in each genre)
        network_leaders = {}
        for network in network_genre_pct.index:
            if network_genre.loc[network].sum() >= 3:  # Minimum threshold
                genres = network_genre_pct.loc[network]
                primary_genre = genres.idxmax()
                primary_share = genres[primary_genre]
                
                secondary_genres = genres[genres > 20].index.tolist()
                secondary_genres.remove(primary_genre)
                
                network_leaders[network] = {
                    'primary': (primary_genre, primary_share),
                    'secondary': [(g, genres[g]) for g in secondary_genres]
                }
        
        # Calculate genre diversity (genres with >10% share)
        def count_major_genres(row):
            return (row > 10).sum()
        
        genre_diversity = network_genre_pct.apply(count_major_genres, axis=1)
        
        # Filter for networks with sufficient shows
        valid_networks = network_genre.sum(axis=1) >= 3
        filtered_diversity = genre_diversity[valid_networks]
        
        # Get most/least diverse
        most_diverse = filtered_diversity.nlargest(3)
        least_diverse = filtered_diversity.nsmallest(3)
        
        # Find significant genre specializations
        unique_patterns = []
        overall_avg = network_genre_pct.mean()
        
        for network in network_genre_pct.index:
            if network_genre.loc[network].sum() >= 3:
                differences = network_genre_pct.loc[network] - overall_avg
                significant = differences[differences > 15]
                
                if not significant.empty:
                    for genre, diff in significant.items():
                        unique_patterns.append({
                            'network': network,
                            'genre': genre,
                            'difference': round(diff, 1),
                            'network_share': round(network_genre_pct.loc[network, genre], 1),
                            'market_average': round(overall_avg[genre], 1)
                        })
        
        return {
            'total_shows': total_shows,
            'unique_genres': unique_genres,
            'top_genre': top_genre,
            'top_genre_count': int(top_genre_count),
            'top_genre_share': round(top_genre_share, 1),
            'network_leaders': network_leaders,
            'genre_diversity': {
                'most_diverse': {
                    k: int(v) for k, v in most_diverse.items()
                },
                'least_diverse': {
                    k: int(v) for k, v in least_diverse.items()
                }
            },
            'unique_patterns': sorted(unique_patterns,
                                    key=lambda x: x['difference'],
                                    reverse=True)
        }
    
    def create_genre_chart(self) -> go.Figure:
        """Create a bar chart showing the distribution of shows across genres.
        Includes tooltips with show counts and percentage of total.
        
        Returns:
            Plotly figure object
        """
        # Calculate genre distribution
        genre_counts = self.shows_df['genre'].value_counts()
        total_shows = len(self.shows_df)
        genre_pcts = (genre_counts / total_shows * 100).round(1)
        
        # Sort by count descending
        sorted_genres = genre_counts.sort_values(ascending=False)
        
        # Create hover text
        hover_text = []
        for genre in sorted_genres.index:
            count = genre_counts[genre]
            pct = genre_pcts[genre]
            hover_text.append(
                f"Genre: {genre}<br>"
                f"Shows: {count}<br>"
                f"Share: {pct}%"
            )
        
        # Create figure using template
        from src.dashboard.utils.templates import MarketOverviewTemplate
        fig = MarketOverviewTemplate.basic_chart('bar')
        
        # Add bar chart
        fig.add_trace(go.Bar(
            x=sorted_genres.index,
            y=sorted_genres.values,
            hoverinfo='text',
            hovertext=hover_text,
            marker_color=COLORS['accent']
        ))
        
        # Update axes
        fig.update_xaxes(title_text="Genre")
        fig.update_yaxes(title_text="Number of Shows")
        
        return fig

    def create_genre_network_analysis(self) -> go.Figure:
        """Create a dual view showing genre distribution across networks.
        Left: Heatmap of genre percentages
        Right: Table of network specializations and diversity
        
        Returns:
            Plotly figure with heatmap and insights table
        """
        # Get insights for the analysis
        insights = self.generate_genre_insights()
        
        # Create figure using template
        from src.dashboard.utils.templates import MarketOverviewTemplate
        fig = MarketOverviewTemplate.multi_chart(
            rows=1,
            cols=2,
            context='dashboard'
        )
        
        # Get network-genre data
        network_genre = pd.crosstab(
            self.shows_df['network'],
            self.shows_df['genre']
        )
        
        # Calculate percentages
        network_genre_pct = network_genre.div(network_genre.sum(axis=1), axis=0) * 100
        
        # Filter networks with sufficient shows
        valid_networks = network_genre.sum(axis=1) >= 3
        filtered_data = network_genre_pct[valid_networks]
        
        # Sort networks by genre diversity
        diversity_scores = filtered_data.apply(lambda row: (row > 10).sum(), axis=1)
        sorted_networks = diversity_scores.sort_values(ascending=False).index
        sorted_data = filtered_data.loc[sorted_networks]
        
        # Create hover text
        hover_text = []
        for network in sorted_data.index:
            row_text = []
            for genre in sorted_data.columns:
                pct = sorted_data.loc[network, genre]
                count = network_genre.loc[network, genre]
                row_text.append(
                    f"Network: {network}<br>"
                    f"Genre: {genre}<br>"
                    f"Shows: {int(count)}<br>"
                    f"Share: {pct:.1f}%"
                )
            hover_text.append(row_text)
        
        # Add heatmap
        fig.add_trace(
            go.Heatmap(
                z=sorted_data.values,
                x=sorted_data.columns,
                y=sorted_data.index,
                colorscale='Viridis',
                hoverongaps=False,
                hoverinfo='text',
                hovertext=hover_text,
                colorbar=dict(
                    title=dict(
                        text='Percentage of Network\'s Shows',
                        side='right'
                    )
                )
            ),
            row=1, col=1
        )
        
        # Prepare insights text
        insights_text = []
        
        # Add diversity insights
        insights_text.append("Most Genre-Diverse Networks:")
        for network, score in insights['genre_diversity']['most_diverse'].items():
            insights_text.append(f"• {network}: {score} genres with >10% share")
        
        # Add network specializations
        insights_text.append("\nNetwork Specializations:")
        specializations = [
            (network, data['primary'])
            for network, data in insights['network_leaders'].items()
            if data['primary'][1] > 40  # Only show strong preferences
        ]
        specializations.sort(key=lambda x: x[1][1], reverse=True)
        for network, (genre, pct) in specializations:
            insights_text.append(f"• {network}: {genre} ({pct:.0f}%)")
        
        # Add unique patterns
        insights_text.append("\nUnique Genre Patterns:")
        for pattern in insights['unique_patterns']:
            insights_text.append(
                f"• {pattern['network']}: {pattern['difference']:.0f}% "
                f"more {pattern['genre']} than average"
            )
        
        # Add insights table
        fig.add_trace(
            go.Table(
                header=dict(
                    values=['Key Insights'],
                    align='left',
                    font=dict(family='Source Sans Pro', size=14)
                ),
                cells=dict(
                    values=[insights_text],
                    align='left',
                    font=dict(family='Source Sans Pro', size=12)
                )
            ),
            row=1, col=2
        )
        
        # Update layout
        fig.update_layout(
            showlegend=False,
            font_family='Source Sans Pro',
            margin=dict(t=30),
            height=max(500, len(sorted_networks) * 25)  # Dynamic height
        )
        
        # Update axes
        fig.update_xaxes(title="Genre", row=1, col=1)
        fig.update_yaxes(title="Network", row=1, col=1)
        
        return fig
