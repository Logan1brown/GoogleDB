"""Tests for grid layouts."""

import plotly.graph_objects as go
from src.dashboard.templates.grids.with_table import create_with_table_grid
from src.dashboard.templates.defaults.bar import create_bar_defaults

def test_with_table_grid():
    """Test that chart + table grid layout works correctly."""
    # Create figure with grid layout
    fig = make_subplots(
        rows=2, cols=1,
        row_heights=[0.7, 0.3],
        vertical_spacing=0.1,
        specs=[
            [{"type": "xy"}],      # Top: Any chart type
            [{"type": "table"}]   # Bottom: Table only
        ]
    )
    
    # Apply templates
    fig.update_layout(
        template=create_bar_defaults(),
        template2=create_with_table_grid()
    )
    
    # Add sample data
    categories = ["Category A", "Category B", "Category C"]
    values = [30, 20, 10]
    
    # Add bar chart
    fig.add_bar(
        x=categories,
        y=values
    )
    
    # Add table
    fig.add_table(
        header=dict(
            values=["Category", "Value"],
            fill_color='rgba(0,0,0,0.1)',
            align='left'
        ),
        cells=dict(
            values=[categories, values],
            align='left'
        )
    )
    
    # Apply grid layout
    fig.update_layout(
        template=create_with_table_grid(),
        title="Chart + Table Grid Test"
    )
    
    # Show the figure
    fig.show()
