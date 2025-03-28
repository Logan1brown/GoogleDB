"""Tests for dual grid layout."""

from plotly.subplots import make_subplots
import plotly.graph_objects as go
from src.dashboard.templates.grids.dual import create_dual_grid
from src.dashboard.templates.defaults.bar import create_bar_defaults
from src.dashboard.templates.defaults.scatter import create_scatter_defaults

def test_dual_grid():
    """Test that dual grid layout works correctly."""
    # Create figure with grid layout
    fig = create_dual_grid(
        title="Content Analysis Dashboard",
        left_title="Genres by Count",
        right_title="Rating Trends"
    )
    
    # Sample data for bar chart
    genres = ['Drama', 'Comedy', 'Action']
    counts = [100, 80, 60]
    
    # Sample data for scatter plot
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May']
    ratings = [8.1, 8.3, 8.0, 8.4, 8.2]
    
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
        row=1, col=2
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
