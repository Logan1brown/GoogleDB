"""Tests for table template."""

import plotly.graph_objects as go
from src.dashboard.templates.defaults.table import create_table_defaults

def test_table_template():
    """Test that table template applies all styles correctly."""
    # Create figure with table template
    fig = go.Figure()
    fig.update_layout(template=create_table_defaults())
    
    # Sample data
    headers = ['Genre', 'Shows', 'Avg Rating']
    data = [
        ['Drama', 150, 8.2],
        ['Comedy', 120, 7.9],
        ['Action', 80, 8.1],
        ['Romance', 60, 7.8]
    ]
    
    # Add table trace
    fig.add_table(
        header=dict(values=headers),
        cells=dict(values=list(zip(*data)))  # Transpose data for column-wise input
    )
    
    # Show the figure
    fig.show()
