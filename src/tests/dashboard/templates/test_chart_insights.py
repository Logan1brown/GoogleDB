"""Test the chart with insights layout."""

import plotly.graph_objects as go
from src.dashboard.templates.grids.chart_insights import create_chart_insights_grid
from src.dashboard.templates.defaults import create_bar_defaults


def test_chart_insights_grid():
    """Test that chart + insights layout works correctly."""
    # Create figure with grid layout
    fig = create_chart_insights_grid(
        title="Genre Analysis",
        chart_title="Distribution by Genre",
        insights_title="Key Findings"
    )
    
    # Sample data
    genres = ['Drama', 'Comedy', 'Action', 'Thriller', 'Romance', 'Horror', 'Documentary', 'Animation']
    counts = [100, 80, 60, 75, 85, 45, 30, 70]
    
    # Add bar chart to left side
    fig.add_bar(
        name="Genre Distribution",
        x=genres,
        y=counts,
        row=1, col=1
    )
    
    # Add key insights
    insights = [
        "Drama leads with 100 shows (16%)",
        "Comedy and Romance tied for 2nd",
        "Horror shows underperforming",
        "Documentary needs more focus",
        "Animation showing strong growth"
    ]
    
    # Add each insight as an annotation
    for i, text in enumerate(insights):
        fig.add_annotation(
            text=text,
            xref="x domain", yref="y domain",
            x=0.5, y=0.9 - i*0.15,  # Evenly space insights
            showarrow=False,
            font=dict(size=12),
            align="left",
            row=1, col=2
        )
    
    # Apply styling
    fig.update_layout(
        template=create_bar_defaults()
    )
    
    # Verify structure
    assert len(fig.data) == 1  # just the bar chart
    assert fig.layout.title.text == "Genre Analysis"
    assert fig.layout.annotations[0].text == "Distribution by Genre"
    assert fig.layout.annotations[1].text == "Key Findings"
    
    # Show the figure
    fig.show()
