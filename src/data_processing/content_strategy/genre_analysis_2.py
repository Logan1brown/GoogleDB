"""Genre Analysis Module.

Analyzes genre patterns and trends, providing visualizations and insights
using the standard template system.
"""

import logging
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from src.dashboard.utils.style_config import COLORS, FONTS
from src.dashboard.utils.templates.insight import InsightTemplate
from src.dashboard.utils.templates.dual_analysis import DualAnalysisTemplate

logger = logging.getLogger(__name__)

class GenreAnalyzer:
    """Analyzer for genre patterns and trends."""
    
    def __init__(self, shows_df: pd.DataFrame):
        """Initialize with show data.
        
        Args:
            shows_df: DataFrame with show information
        """
        self.shows_df = shows_df
        
    def create_genre_heatmap(self) -> go.Figure:
        """Create a heatmap showing genre distribution across networks.
        Uses DualAnalysisTemplate for consistent styling and layout.
        
        Returns:
            Plotly figure with genre heatmap and network specialization insights
        """
        # Get genre insights
        insights = self.analyze_genres()
        
        # Create pivot table for heatmap
        genre_pivot = pd.crosstab(
            self.shows_df['network'],
            self.shows_df['genre'],
            normalize='index'  # Show percentages
        ) * 100
        
        # Sort networks by total show count
        network_totals = self.shows_df['network'].value_counts()
        genre_pivot = genre_pivot.reindex(network_totals.index)
        
        # Create heatmap trace
        heatmap = go.Heatmap(
            z=genre_pivot.values,
            x=genre_pivot.columns,
            y=genre_pivot.index,
            colorscale='Viridis',
            colorbar=dict(title='% of Network Shows'),
            hoverongaps=False
        )
        
        # Create template with insights
        template = DualAnalysisTemplate()
        fig = template.create_dual_analysis(
            traces=[heatmap],
            title='Genre Distribution by Network',
            subtitle=f"Networks specialize in different genres - {insights['network_leaders']['insight']}",
            left_insight=f"Genre Diversity: {insights['genre_diversity']['insight']}",
            right_insight=f"Unique Patterns: {insights['unique_patterns']['insight']}"
        )
        
        # Update layout for better readability
        fig.update_layout(
            xaxis_title='Genre',
            yaxis_title='Network',
            xaxis={'tickangle': 45}
        )
        
        return fig
        
    def analyze_genres(self) -> Dict:
        """Generate complete genre analysis with all insights.
        
        Returns:
            Dict containing:
            - total_shows: Total shows analyzed
            - unique_genres: Number of distinct genres
            - top_genre: Most common genre and stats
            - network_leaders: Networks leading in specific genres
            - genre_diversity: Networks with most/least genre diversity
            - unique_patterns: Notable genre specializations
        """
        # Basic counts
        total_shows = len(self.shows_df)
        genre_counts = self.shows_df['genre'].value_counts()
        
        # Genre stats
        genre_stats = {
            'total_shows': total_shows,
            'unique_genres': len(genre_counts),
            'top_genre': genre_counts.index[0],
            'top_genre_count': int(genre_counts.iloc[0]),
            'top_genre_share': round((genre_counts.iloc[0] / total_shows) * 100, 1)
        }
        
        # Network analysis
        network_genre = pd.crosstab(
            self.shows_df['network'],
            self.shows_df['genre']
        )
        network_genre_pct = network_genre.div(network_genre.sum(axis=1), axis=0) * 100
        
        # Find network leaders
        network_stats = self._analyze_network_patterns(network_genre_pct)
        
        return {**genre_stats, **network_stats}
    
    def create_genre_overview(self) -> go.Figure:
        """Create genre distribution overview with insights.
        
        Returns:
            Figure with genre distribution bar chart and key metrics
        """
        insights = self.analyze_genres()
        
        # Create figure with template
        fig = InsightTemplate.create_insight_slide(
            title="Genre Distribution",
            insight=f"{insights['top_genre']} leads with {insights['top_genre_share']}% of shows",
            chart_type='bar'
        )
        
        # Add KPI metrics
        InsightTemplate.add_kpi_banner(fig, {
            "Total Shows": str(insights['total_shows']),
            "Unique Genres": str(insights['unique_genres']),
            f"Top Genre ({insights['top_genre']})": f"{insights['top_genre_count']} shows"
        })
        
        # Add genre distribution
        genre_counts = self.shows_df['genre'].value_counts()
        total_shows = len(self.shows_df)
        genre_pcts = (genre_counts / total_shows * 100).round(1)
        
        hover_text = [
            f"{genre}<br>{count} shows<br>{pct}% of total" 
            for genre, count, pct in zip(
                genre_counts.index, 
                genre_counts.values,
                genre_pcts
            )
        ]
        
        fig.add_trace(go.Bar(
            x=list(genre_counts.index),
            y=list(genre_counts.values),
            name="Shows per Genre",
            hovertext=hover_text,
            hoverinfo="text",
            marker_color=COLORS['chart']['sequence'][0]
        ))
        
        fig.update_xaxes(title="Genre")
        fig.update_yaxes(title="Number of Shows")
        
        return fig
    
    def create_network_analysis(self) -> go.Figure:
        """Create network genre analysis with heatmap and insights.
        
        Returns:
            Figure with genre heatmap and network insights table
        """
        insights = self.analyze_genres()
        
        # Create dual view
        fig = DualAnalysisTemplate.create_dual_view(
            title="Genre Network Analysis",
            insight=self._format_network_insight(insights),
            chart_types=('heatmap', 'table')
        )
        
        # Add heatmap
        network_genre = pd.crosstab(
            self.shows_df['network'],
            self.shows_df['genre']
        )
        network_genre_pct = network_genre.div(network_genre.sum(axis=1), axis=0) * 100
        
        fig.add_trace(
            go.Heatmap(
                z=network_genre_pct.values,
                x=network_genre_pct.columns,
                y=network_genre_pct.index,
                colorscale='Viridis',
                colorbar=dict(title='% of Network Shows'),
                hoverongaps=False,
                hovertemplate=(
                    "Network: %{y}<br>"
                    "Genre: %{x}<br>"
                    "Share: %{z:.1f}%<extra></extra>"
                )
            ),
            row=1, col=1
        )
        
        # Add insights table
        table_data = self._format_network_table(insights)
        
        fig.add_trace(
            go.Table(
                header=dict(
                    values=['Network', 'Primary Genre', 'Secondary Genres', 'Diversity Score'],
                    font=dict(size=FONTS['primary']['sizes']['sm']),
                    align='left',
                    fill_color=COLORS['background']['alt']
                ),
                cells=dict(
                    values=list(zip(*table_data)),
                    font=dict(size=FONTS['primary']['sizes']['sm']),
                    align='left',
                    fill_color=COLORS['background']['main']
                )
            ),
            row=1, col=2
        )
        
        return fig
    
    def _analyze_network_patterns(self, network_genre_pct: pd.DataFrame) -> Dict:
        """Analyze network genre patterns.
        
        Args:
            network_genre_pct: DataFrame of network genre percentages
        
        Returns:
            Dict with network leaders, diversity scores, and unique patterns
        """
        # Find network leaders
        network_leaders = {}
        for network in network_genre_pct.index:
            if network_genre_pct.loc[network].sum() >= 300:  # 3 shows @ 100%
                genres = network_genre_pct.loc[network]
                primary_genre = genres.idxmax()
                primary_share = genres[primary_genre]
                
                secondary = genres[genres > 20].index.tolist()
                secondary.remove(primary_genre)
                
                network_leaders[network] = {
                    'primary': (primary_genre, primary_share),
                    'secondary': [(g, genres[g]) for g in secondary]
                }
        
        # Calculate genre diversity
        genre_diversity = network_genre_pct.apply(
            lambda row: (row > 10).sum(),  # Count genres with >10% share
            axis=1
        )
        
        # Filter for networks with sufficient shows
        valid_mask = network_genre_pct.sum(axis=1) >= 300
        filtered_diversity = genre_diversity[valid_mask]
        
        diversity_scores = {
            'most_diverse': {
                k: int(v) for k, v in filtered_diversity.nlargest(3).items()
            },
            'least_diverse': {
                k: int(v) for k, v in filtered_diversity.nsmallest(3).items()
            }
        }
        
        # Find unique patterns
        market_avg = network_genre_pct.mean()
        unique_patterns = []
        
        for network in network_genre_pct.index:
            if network_genre_pct.loc[network].sum() >= 300:
                differences = network_genre_pct.loc[network] - market_avg
                significant = differences[differences > 15]
                
                for genre, diff in significant.items():
                    unique_patterns.append({
                        'network': network,
                        'genre': genre,
                        'difference': round(diff, 1),
                        'network_share': round(network_genre_pct.loc[network, genre], 1),
                        'market_average': round(market_avg[genre], 1)
                    })
        
        return {
            'network_leaders': network_leaders,
            'genre_diversity': diversity_scores,
            'unique_patterns': sorted(
                unique_patterns,
                key=lambda x: x['difference'],
                reverse=True
            )
        }
    
    def _format_network_insight(self, insights: Dict) -> str:
        """Format network analysis insight text."""
        most_diverse = list(insights['genre_diversity']['most_diverse'].keys())[0]
        most_diverse_count = insights['genre_diversity']['most_diverse'][most_diverse]
        
        unique_pattern = insights['unique_patterns'][0]
        specialist = unique_pattern['network']
        specialty = unique_pattern['genre']
        specialty_share = unique_pattern['network_share']
        
        return (
            f"{most_diverse} leads in genre diversity with {most_diverse_count} "
            f"major genres, while {specialist} specializes in {specialty} "
            f"({specialty_share:.1f}%)"
        )
    
    def _format_network_table(self, insights: Dict) -> List[List[str]]:
        """Format network data for table display."""
        table_rows = []
        
        for network, data in insights['network_leaders'].items():
            primary = f"{data['primary'][0]} ({data['primary'][1]:.1f}%)"
            secondary = ", ".join(
                [f"{g} ({p:.1f}%)" for g, p in data['secondary']]
            )
            
            diversity = (
                insights['genre_diversity']['most_diverse'].get(network) or
                insights['genre_diversity']['least_diverse'].get(network)
            )
            
            table_rows.append([
                network,
                primary,
                secondary or "None",
                str(diversity)
            ])
        
        return sorted(table_rows, key=lambda x: int(x[3]), reverse=True)
