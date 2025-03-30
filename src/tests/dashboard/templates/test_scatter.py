"""Tests for scatter template."""

import plotly.graph_objects as go
from src.dashboard.templates.defaults.scatter import create_scatter_defaults

def test_scatter_template():
    """Test that scatter template applies all styles correctly."""
    # Create figure with scatter template
    fig = go.Figure()
    fig.update_layout(template=create_scatter_defaults())
    
    # Add sample data
    x = [1, 2, 3, 4, 5]
    y1 = [10, 15, 13, 17, 20]
    y2 = [5, 10, 8, 12, 15]
    
    # Add two scatter traces to test styling
    fig.add_scatter(
        name="Series 1",
        x=x,
        y=y1,
    )
    fig.add_scatter(
        name="Series 2",
        x=x,
        y=y2,
    )
    
    # Update title
    fig.update_layout(
        title="Scatter Test",
        xaxis_title="X Axis",
        yaxis_title="Y Axis"
    )
    
    # Show the figure
    fig.show()
