"""Test the chart with insights and table layout."""

import plotly.graph_objects as go
from src.dashboard.templates.grids.chart_insights_table import create_with_table_grid
from src.dashboard.templates.defaults import create_bar_defaults

def test_with_table_grid():
    """Test that chart + insights + table layout works correctly."""
    # Create figure with grid layout
    fig = create_with_table_grid(
        title="Genre Analysis",
        chart_title="Distribution by Genre",
        insights_title="Key Findings",
        table_title="Raw Data"
    )
    
    # Sample data
    genres = ['Drama', 'Comedy', 'Action']
    counts = [100, 80, 60]
    
    # Add bar chart to main section
    fig.add_bar(
        name="Genre Distribution",
        x=genres,
        y=counts,
        row=1, col=1
    )
    
    # Add key insights
    insights = [
        "Drama dominates with 45% share",
        "Comedy shows steady growth",
        "Action underrepresented"
    ]
    for i, text in enumerate(insights):
        fig.add_annotation(
            text=text,
            xref="x domain", yref="y domain",
            x=0.5, y=0.9 - i*0.2,
            showarrow=False,
            row=1, col=2
        )
    
    # Add data table
    fig.add_table(
        header=dict(
            values=["Genre", "Count"],
            font=dict(size=12, color="white"),
            fill_color="rgb(55, 83, 109)",
            align="left"
        ),
        cells=dict(
            values=[genres, counts],
            font=dict(size=11),
            align="left"
        ),
        row=2, col="all"
    )
    
    # Apply styling
    fig.update_layout(
        template=create_bar_defaults()
    )
    
    # Show the figure
    fig.show()
