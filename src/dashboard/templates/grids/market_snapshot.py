"""Grid layout for market snapshot dashboard.

This module provides a function to create a market snapshot that shows:
- Title and filters header
- Current KPI metrics (4 cards)
- Market distribution chart
- Key market indicators
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots


def create_market_snapshot_grid(
    title="Market Snapshot",
    distribution_title="Market Distribution",
    indicators_title="Key Market Indicators",
    height=800
):
    """Create a figure with market snapshot layout.

    Args:
        title: Title for the dashboard (default "Market Snapshot")
        distribution_title: Title for market distribution section
        indicators_title: Title for market indicators section
        height: Total figure height in pixels (default 800)

    Returns:
        go.Figure: Figure with market analysis layout:
        - Header with title and filters
        - KPI metric cards (4 across)
        - Current market distribution
        - Key market indicators
    """
    # Create subplot structure - using xy for text content
    specs = [
        # Row 1: Executive summary
        [{'type': 'xy', 'colspan': 4}, None, None, None],
        # Row 2: Searchable dropdowns
        [{'type': 'xy'}, {'type': 'xy'}, {'type': 'xy'}, {'type': 'xy'}],
        # Row 3: KPI metric cards
        [{'type': 'indicator'}, {'type': 'indicator'}, {'type': 'indicator'}, {'type': 'indicator'}],
        # Row 4: Market distribution chart
        [{'type': 'xy', 'colspan': 4}, None, None, None],
        # Row 5: Market metrics
        [{'type': 'indicator'}, {'type': 'indicator'}, {'type': 'indicator'}, {'type': 'indicator'}]
    ]
    
    # Set row heights - give more space to the visualization
    row_heights = [
        0.1,   # Executive summary
        0.15,  # Searchable dropdowns
        0.2,   # Metric cards
        0.35,  # Distribution chart
        0.2    # Bottom metrics
    ]
    
    fig = make_subplots(
        rows=5,
        cols=4,
        row_heights=row_heights,
        vertical_spacing=0.03,  # Tighter spacing
        horizontal_spacing=0.02,
        specs=specs,
        subplot_titles=[
            "Executive Summary",  # Row 1
            "Shows", "Creators", "Genres", "Platforms",  # Row 2
            None, None, None, None,  # Row 3 (metrics have their own titles)
            distribution_title,  # Row 4
            None, None, None, None  # Row 5 (metrics have their own titles)
        ]
    )
    
    # Apply layout settings
    fig.update_layout(
        # Main title and filters section
        title=dict(
            text=title,
            x=0.5,
            y=0.99,
            xanchor='center',
            yanchor='top',
            font=dict(size=24)
        ),
        # Add filter bar below title
        annotations=[
            dict(
                text='Filters:',
                x=0.01,
                y=0.995,
                xref='paper',
                yref='paper',
                showarrow=False,
                font=dict(size=12)
            )
        ],
        # General layout
        showlegend=True,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        ),
        margin=dict(l=50, r=50, t=120, b=50),  # Extra top margin for filters
        height=height,
        paper_bgcolor='white',
        plot_bgcolor='white'
    )
    
    # Configure grid and add borders
    fig.update_layout(
        grid={
            'rows': 5,
            'columns': 4,
            'pattern': 'independent'
        },
        shapes=[
            # Borders for metric cards
            *[dict(
                type="rect",
                xref="paper", yref="paper",
                x0=i/4 + 0.02, x1=(i+1)/4 - 0.02,
                y0=0.4, y1=0.6,  # Row 3 (metrics)
                line=dict(color="lightgray", width=2),
                fillcolor="white",
                layer="below"
            ) for i in range(4)],
            # Borders for bottom metrics
            *[dict(
                type="rect",
                xref="paper", yref="paper",
                x0=i/4 + 0.02, x1=(i+1)/4 - 0.02,
                y0=0.05, y1=0.2,  # Row 5 (bottom metrics)
                line=dict(color="lightgray", width=2),
                fillcolor="white",
                layer="below"
            ) for i in range(4)],
            # Borders for search dropdowns
            *[dict(
                type="rect",
                xref="paper", yref="paper",
                x0=i/4 + 0.02, x1=(i+1)/4 - 0.02,
                y0=0.7, y1=0.85,  # Row 2 (search)
                line=dict(color="lightgray", width=2),
                fillcolor="white",
                layer="below"
            ) for i in range(4)]
        ]
    )
    
    # Style distribution section (second row)
    fig.update_xaxes(
        showgrid=True,
        gridcolor='lightgray',
        row=2, col=1
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor='lightgray',
        row=2, col=1
    )
    
    # Style indicators section (third row)
    fig.update_xaxes(
        showgrid=False,
        showticklabels=False,
        row=3, col=1
    )
    fig.update_yaxes(
        showgrid=False,
        showticklabels=False,
        row=3, col=1
    )
    
    return fig
