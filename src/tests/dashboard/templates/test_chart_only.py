"""Test the single chart layout."""

import plotly.graph_objects as go
from src.dashboard.templates.grids.chart_only import create_chart_grid
from src.dashboard.templates.defaults import create_bar_defaults


def test_chart_grid():
    """Test that single chart layout works correctly."""
    # Create figure with grid layout
    fig = create_chart_grid(
        title="Genre Distribution",
        chart_title="Shows by Genre"
    )
    
    # Sample data
    genres = ['Drama', 'Comedy', 'Action']
    counts = [100, 80, 60]
    
    # Add bar chart
    fig.add_bar(
        name="Genre Distribution",
        x=genres,
        y=counts
    )
    
    # Apply styling
    fig.update_layout(
        template=create_bar_defaults()
    )
    
    # Verify structure
    assert len(fig.data) == 1
    assert fig.layout.title.text == "Genre Distribution"
    assert fig.layout.annotations[0].text == "Shows by Genre"  # subplot title
    
    # Show the figure
    fig.show()
