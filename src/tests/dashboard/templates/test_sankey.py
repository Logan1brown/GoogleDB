"""Tests for Sankey template."""

import plotly.graph_objects as go
from src.dashboard.templates.defaults.sankey import create_sankey_defaults

def test_sankey_template():
    """Test that Sankey template applies all styles correctly."""
    # Create figure with Sankey template
    fig = go.Figure()
    fig.update_layout(template=create_sankey_defaults())
    
    # Sample data
    nodes = [
        'Network A', 'Network B', 'Network C',  # Source nodes
        'Genre X', 'Genre Y', 'Genre Z'         # Target nodes
    ]
    
    source = [0, 0, 1, 1, 2, 2]  # Index of source nodes
    target = [3, 4, 4, 5, 3, 5]  # Index of target nodes
    value = [20, 10, 15, 25, 30, 5]  # Flow values
    
    # Add Sankey trace
    fig.add_sankey(
        node=dict(label=nodes),
        link=dict(
            source=source,
            target=target,
            value=value
        )
    )
    
    # Update title
    fig.update_layout(
        title="Network to Genre Flow"
    )
    
    # Show the figure
    fig.show()
