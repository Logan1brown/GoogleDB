"""Tests for base template."""

import plotly.graph_objects as go
from src.dashboard.templates.base import create_base_template
from src.dashboard.utils.style_config import COLORS, FONTS, DIMENSIONS

def test_base_template():
    """Test that base template applies all styles correctly."""
    # Create figure with base template
    fig = go.Figure()
    fig.update_layout(template=create_base_template())
    
    # Add sample data
    categories = ["Category A", "Category B", "Category C"]
    bar_values = [10, 20, 30]
    line_values = [12, 25, 35]
    
    # Add a bar trace
    fig.add_bar(
        name="Values",
        x=categories,
        y=bar_values,
        text=[f"{v:,}" for v in bar_values],
        textposition="auto",
        marker_color=COLORS['accent'],
    )
    
    # Add a trend line
    fig.add_scatter(
        name="Trend",
        x=categories,
        y=line_values,
        mode="lines+markers",
    )
    
    # Update title to test fonts
    fig.update_layout(
        title=dict(
            text="Template Test",
            font=dict(size=FONTS['primary']['sizes']['title'])
        )
    )
    
    # Show the figure
    fig.show()
