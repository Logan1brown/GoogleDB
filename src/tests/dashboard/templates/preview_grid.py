"""Preview any grid template with sample data.

Usage:
    python -m src.tests.dashboard.templates.preview_grid dual
    python -m src.tests.dashboard.templates.preview_grid market
"""

import plotly.graph_objects as go
from src.dashboard.templates.defaults.bar import create_bar_defaults
from src.dashboard.templates.defaults.scatter import create_scatter_defaults

def preview_market_snapshot():
    """Preview market snapshot grid with sample data."""
    from src.dashboard.templates.grids.chart_insights import create_chart_insights_grid
    
    fig = create_chart_insights_grid(
        title="TV Series Market Snapshot",
        distribution_title="Current Market Distribution"
    )

    # Add executive summary to title area
    fig.add_annotation(
        text="Executive Summary: Strong growth in streaming platforms with increasing demand for original content.",
        xref="paper", yref="paper",
        x=0.5, y=0.85,
        showarrow=False,
        align="center",
        font=dict(size=14)
    )

    # Add KPI metrics (row 2)
    kpi_data = [
        (492, 32, "Total Shows"),
        (8.2, -0.5, "Avg Rating"),
        (156, 12, "New Series"),
        (45, 5, "Networks")
    ]
    for i, (value, delta, title) in enumerate(kpi_data):
        fig.add_trace(
            go.Indicator(
                mode="number+delta",
                value=value,
                delta={"reference": value - delta, "relative": True},
                title={"text": title},
            ),
            row=2, col=i+1  # Columns are 1-based
        )

    # Add market distribution (row 3)
    fig.add_trace(
        go.Bar(
            x=["Netflix", "HBO", "Prime", "Disney+", "Apple TV+"],
            y=[35, 28, 22, 18, 15],
            text=["35%", "28%", "22%", "18%", "15%"],
            textposition="auto",
            marker_color='#3498db',
            hovertemplate='%{x}<br>%{text}<extra></extra>'
        ),
        row=3, col=1  # Uses colspan=4
    )
    
    # Add performance metrics (row 4)
    perf_data = [
        (85, 5, "Viewer Score"),
        (4.2, 0.3, "Avg Episodes"),
        (92, 8, "Completion %"),
        (78, -2, "Retention")
    ]
    for i, (value, delta, title) in enumerate(perf_data):
        fig.add_trace(
            go.Indicator(
                mode="number+delta",
                value=value,
                delta={"reference": value - delta, "relative": True},
                title={"text": title},
            ),
            row=4, col=i+1
        )
    
    return fig

def preview_market_grid():
    """Preview market snapshot grid with sample data."""
    from src.dashboard.templates.grids.chart_insights import create_chart_insights_grid
    
    fig = create_chart_insights_grid(
        title="TV Series Market Snapshot",
        distribution_title="Current Market Distribution"
    )

    # Add executive summary
    fig.add_annotation(
        text="Executive Summary: Strong growth in streaming platforms with increasing demand for original content.",
        xref="paper", yref="paper",
        x=0.5, y=0.85,
        showarrow=False,
        align="center",
        font=dict(size=14)
    )

    # Add KPI metrics
    for i, (value, delta, title) in enumerate([
        (492, 32, "Total Shows"),
        (8.2, -0.5, "Avg Rating"),
        (156, 12, "New Series"),
        (45, 5, "Networks")
    ], 1):
        fig.add_trace(
            go.Indicator(
                mode="number+delta",
                value=value,
                delta={"reference": value - delta, "relative": True},
                title={"text": title},
            ),
            row=2, col=i
        )

    # Add market distribution
    fig.add_trace(
        go.Bar(
            x=["Netflix", "HBO", "Prime", "Disney+", "Apple TV+"],
            y=[35, 28, 22, 18, 15],
            text=["35%", "28%", "22%", "18%", "15%"],
            textposition="auto",
            marker_color='#3498db',
            hovertemplate='%{x}<br>%{text}<extra></extra>'
        ),
        row=3, col=1
    )
    
    return fig



def preview_stacked():
    """Preview stacked grid with sample data."""
    from src.dashboard.templates.grids.stacked import create_stacked_grid
    
    fig = create_stacked_grid(
        title="Content Performance",
        top_title="Viewership Metrics",
        bottom_title="Engagement Data"
    )
    
    # Sample data
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May']
    views = [1000, 1200, 1100, 1400, 1300]
    engagement = [75, 80, 78, 85, 82]
    
    # Add charts
    fig.add_bar(
        name="Views",
        x=months,
        y=views,
        row=1, col=1
    )
    fig.add_scatter(
        name="Engagement %",
        x=months,
        y=engagement,
        row=2, col=1
    )
    
    return fig

def preview_grid(grid_type: str):
    """Preview a grid template.
    
    Args:
        grid_type: Type of grid to preview:
            - 'market': Market snapshot dashboard
            - 'stacked': Stacked charts
    """
    preview_funcs = {
        'market': preview_market_snapshot,
        'stacked': preview_stacked
    }
    
    if grid_type not in preview_funcs:
        raise ValueError(f"Unknown grid type: {grid_type}. Valid types: {list(preview_funcs.keys())}")
    
    fig = preview_funcs[grid_type]()
    fig.show()

if __name__ == "__main__":
    import sys
    grid_type = sys.argv[1] if len(sys.argv) > 1 else 'dual'
    preview_grid(grid_type)
