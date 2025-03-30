"""Tests for bar chart template."""

import plotly.graph_objects as go
from src.dashboard.templates.defaults.bar import create_bar_defaults

def test_bar_template():
    """Test that bar template applies all styles correctly."""
    # Create figure with bar template
    fig = go.Figure()
    fig.update_layout(template=create_bar_defaults())
    
    # Add sample data
    categories = ["Category A", "Category B", "Category C"]
    values = [30, 20, 10]  # Pre-sorted descending
    
    # Add bar trace
    fig.add_bar(
        x=categories,
        y=values,
    )
    
    # Update title
    fig.update_layout(
        title="Bar Chart Test"
    )
    
    # Show the figure
    fig.show()
