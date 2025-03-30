"""Tests for heatmap template."""

import plotly.graph_objects as go
from src.dashboard.templates.defaults.heatmap import create_heatmap_defaults

def test_heatmap_template():
    """Test that heatmap template applies all styles correctly."""
    # Create figure with heatmap template
    fig = go.Figure()
    fig.update_layout(template=create_heatmap_defaults())
    
    # Add sample data
    categories_x = ["A", "B", "C"]
    categories_y = ["X", "Y", "Z"]
    values = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9]
    ]
    
    # Add heatmap trace
    fig.add_heatmap(
        x=categories_x,
        y=categories_y,
        z=values,
    )
    
    # Update title
    fig.update_layout(
        title="Heatmap Test"
    )
    
    # Show the figure
    fig.show()
