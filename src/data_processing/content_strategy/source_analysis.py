"""Source Type Analysis Module.

This module analyzes patterns in source types (original vs adaptations) across networks.
"""

import logging
from pathlib import Path
from typing import Dict

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

logger = logging.getLogger(__name__)

class SourceAnalyzer:
    """Analyzer for source type patterns and trends."""
    
    def __init__(self, shows_df: pd.DataFrame):
        """Initialize the analyzer.
        
        Args:
            shows_df: DataFrame containing show information
        """
        self.shows_df = shows_df
        
        # Log source type distribution
        logger.info("Source type distribution:")
        source_counts = self.shows_df['source_type'].value_counts()
        for source, count in source_counts.items():
            logger.info(f"  {source}: {count} shows")
    
    def create_distribution_chart(self) -> go.Figure:
        """Create a bar chart showing the distribution of shows across source types.
        
        Returns:
            Plotly figure object
        """
        # Get source counts
        source_counts = self.shows_df['source_type'].value_counts()
        
        # Create chart
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=list(source_counts.index),
            y=list(source_counts.values),
            name="Shows per Source Type"
        ))
        
        # Update layout
        fig.update_layout(
            xaxis_title="Source Type",
            yaxis_title="Number of Shows",
            font_family="Source Sans Pro",
            showlegend=False,
            margin=dict(t=20)
        )
        
        return fig
    
    def generate_source_insights(self) -> Dict:
        """Generate key insights about source type patterns.
        
        Returns:
            Dictionary containing various source type insights including:
            - top_source: Most common source type
            - top_source_count: Number of shows from top source
            - original_share: Percentage of shows that are original content
            - network_preferences: Dict of network -> preferred source type
        """
        # Get source counts
        source_counts = self.shows_df['source_type'].value_counts()
        total_shows = len(self.shows_df)
        
        # Get top source info
        top_source = source_counts.index[0]
        top_source_count = source_counts[top_source]
        
        # Calculate original content share
        original_count = source_counts.get('Original', 0)
        original_share = (original_count / total_shows) * 100
        
        # Network source type focus
        network_source = pd.crosstab(
            self.shows_df['network'],
            self.shows_df['source_type']
        )
        
        # Calculate percentages
        network_source_pct = network_source.div(network_source.sum(axis=1), axis=0) * 100
        
        # Filter out networks with too few shows
        MIN_SHOWS = 3
        valid_networks = network_source.sum(axis=1) >= MIN_SHOWS
        filtered_data = network_source_pct[valid_networks]
        filtered_counts = network_source[valid_networks]
        
        # Calculate source diversity (using Shannon entropy)
        def shannon_diversity(row):
            props = row[row > 0] / 100  # Convert percentages to proportions
            return -(props * np.log(props)).sum()
        
        diversity_scores = filtered_data.apply(shannon_diversity, axis=1)
        
        # Find networks with strong preferences for each source type
        source_preferences = {}
        for source_type in filtered_data.columns:
            # Get networks with highest percentage for this source
            source_data = filtered_data[source_type].sort_values(ascending=False)
            source_counts = filtered_counts[source_type]
            
            # Only include if percentage > 30% and at least 2 shows
            significant = source_data[(source_data > 30) & (source_counts >= 2)]
            
            if not significant.empty:
                source_preferences[source_type] = [
                    {
                        'network': network,
                        'percentage': pct,
                        'count': filtered_counts.loc[network, source_type],
                        'total_shows': filtered_counts.loc[network].sum()
                    }
                    for network, pct in significant.items()
                ]
        
        # Sort source types by total volume
        source_volumes = filtered_counts.sum().sort_values(ascending=False)
        
        return {
            'network_source_matrix': network_source,
            'network_source_percentages': filtered_data,
            'source_preferences': source_preferences,
            'source_volumes': source_volumes,
            'diversity_scores': diversity_scores
        }
    
    def create_source_visualization(self) -> None:
        """Create source type distribution visualization with insights."""
        insights = self.generate_source_insights()
        
        # Create figure with subplots
        fig = make_subplots(
            rows=1, cols=2,
            column_widths=[0.7, 0.3],
            subplot_titles=('Source Type Distribution by Network', 'Key Insights'),
            specs=[[{"type": "heatmap"}, {"type": "table"}]]
        )
        
        # Sort source types by volume
        source_volumes = insights['source_volumes']
        network_source_pct = insights['network_source_percentages']
        sorted_data = network_source_pct[source_volumes.index]
        
        # Sort networks by their highest percentage
        network_max_pct = sorted_data.max(axis=1)
        sorted_data = sorted_data.loc[network_max_pct.sort_values(ascending=False).index]
        
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
        
        # Add source volume summary
        insights_text.append("Overall Source Distribution:")
        total_shows = insights['network_source_matrix'].sum().sum()
        for source, count in source_volumes.items():
            insights_text.append(
                f"• {source}: {count} shows ({(count/total_shows*100):.1f}%)"
            )
        insights_text.append("")
        
        # Add source type preferences
        insights_text.append("Network Source Preferences:")
        for source_type, networks in insights['source_preferences'].items():
            insights_text.append(f"\n{source_type} Specialists:")
            for net in networks[:3]:  # Show top 3 for each source
                insights_text.append(
                    f"• {net['network']}: {net['percentage']:.0f}% "
                    f"({net['count']}/{net['total_shows']} shows)"
                )
        
        # Add diversity insights
        insights_text.append("\nSource Diversity:")
        diversity = insights['diversity_scores'].sort_values(ascending=False)
        for network, score in diversity.head(3).items():
            insights_text.append(f"• {network}: {score:.2f}")
        
        # Add table
        fig.add_trace(
            go.Table(
                header=dict(
                    values=['Source Type Analysis'],
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
            title='Network Source Type Analysis',
            showlegend=False,
            height=900
        )
        
        # Save to HTML file
        output_dir = Path('output/network_analysis/content_strategy')
        output_dir.mkdir(parents=True, exist_ok=True)
        fig.write_html(output_dir / 'source_type_distribution.html')
