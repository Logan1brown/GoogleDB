"""Test the chart with table layout."""

import plotly.graph_objects as go
from src.dashboard.templates.grids.chart_table import create_chart_table_grid
from src.dashboard.templates.defaults import create_bar_defaults


def test_chart_table_grid():
    """Test that chart + table layout works correctly."""
    # Create figure with grid layout
    fig = create_chart_table_grid(
        title="Genre Analysis",
        chart_title="Distribution by Genre",
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
        row=2, col=1
    )
    
    # Apply styling
    fig.update_layout(
        template=create_bar_defaults()
    )
    
    # Verify structure
    assert len(fig.data) == 2  # bar + table
    assert fig.layout.title.text == "Genre Analysis"
    assert fig.layout.annotations[0].text == "Distribution by Genre"
    assert fig.layout.annotations[1].text == "Raw Data"
    
    # Show the figure
    fig.show()
