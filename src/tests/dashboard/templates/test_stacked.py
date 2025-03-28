"""Test the stacked grid layout."""

import plotly.graph_objects as go
from src.dashboard.templates.grids import create_stacked_grid
from src.dashboard.templates.defaults import create_bar_defaults, create_scatter_defaults

def test_stacked_grid():
    """Test that stacked grid layout works correctly."""
    # Create figure with grid layout
    fig = create_stacked_grid(
        title="Content Performance",
        subplot_titles=["Genre Distribution", "Rating Trends", "Network Share"],
        heights=[0.4, 0.3, 0.3]  # More space for top chart
    )
    
    # Sample data for charts
    genres = ['Drama', 'Comedy', 'Action']
    counts = [100, 80, 60]
    
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May']
    ratings = [8.1, 8.3, 8.0, 8.4, 8.2]
    
    networks = ['Netflix', 'HBO', 'Amazon']
    shares = [40, 35, 25]
    
    # Add traces to specific grid positions
    fig.add_bar(
        name="Genre Distribution",
        x=genres,
        y=counts,
        row=1, col=1
    )
    
    fig.add_scatter(
        name="Average Rating",
        x=months,
        y=ratings,
        row=2, col=1
    )
    
    fig.add_bar(
        name="Network Share",
        x=networks,
        y=shares,
        row=3, col=1
    )
    
    # Apply chart type styling
    fig.update_layout(
        template=create_bar_defaults()
    )
    fig.update_traces(
        overwrite=True,
        selector={'type': 'scatter'},
        marker=create_scatter_defaults().data.scatter[0].marker,
        line=create_scatter_defaults().data.scatter[0].line
    )
    
    # Show the figure
    fig.show()
