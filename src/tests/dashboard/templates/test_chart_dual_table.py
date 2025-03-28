"""Test the chart with dual table layout."""

import plotly.graph_objects as go
from src.dashboard.templates.grids.chart_dual_table import create_chart_dual_table_grid
from src.dashboard.templates.defaults import create_bar_defaults


def test_chart_dual_table_grid():
    """Test that chart + dual table layout works correctly."""
    # Create figure with grid layout
    fig = create_chart_dual_table_grid(
        title="Genre Analysis",
        chart_title="Distribution by Genre",
        top_table_title="Raw Data",
        bottom_table_title="Summary Stats"
    )
    
    # Chart data (top 8 genres)
    chart_genres = ['Drama', 'Comedy', 'Action', 'Thriller', 'Romance', 'Horror', 'Documentary', 'Animation']
    chart_counts = [100, 80, 60, 75, 85, 45, 30, 70]
    
    # Table data (all genres)
    genres = ['Drama', 'Comedy', 'Action', 'Thriller', 'Romance', 'Horror', 
             'Documentary', 'Animation', 'Fantasy', 'Sci-Fi', 'Musical',
             'Western', 'Sports', 'Family', 'Adventure'] * 2  # 30 rows for scrolling
    counts = [100, 80, 60, 75, 85, 45, 30, 70, 55, 40, 25, 20, 35, 65, 50] * 2
    
    # Detailed stats (30 rows for scrolling)
    stats = {
        'Metric': ['Total Shows', 'Average per Genre', 'Maximum Count', 'Minimum Count',
                   'Standard Deviation', 'Top Genre', 'Bottom Genre', 'Mid-tier Genres',
                   'Growth Rate', 'YoY Change', 'Market Share', 'Trend Direction',
                   'Seasonal Peak', 'Genre Velocity', 'Correlation Score'] * 2,
        'Value': [1000, 66.7, 100, 20, 23.4, 'Drama', 'Western', '5',
                 '+15%', '+50', '23%', 'Upward', 'Summer', 'High', '0.8'] * 2
    }
    
    # Add bar chart to left side (top 8 genres)
    fig.add_bar(
        name="Genre Distribution",
        x=chart_genres,
        y=chart_counts,
        row=1, col=1
    )
    
    # Add raw data table to top right with scrolling
    fig.add_table(
        header=dict(
            values=["Genre", "Count"],
            font=dict(size=12, color="white"),
            fill_color="rgb(55, 83, 109)",
            align="left",
            height=30
        ),
        cells=dict(
            values=[genres, counts],
            font=dict(size=11),
            align="left",
            height=25
        ),
        row=1, col=2,
        columnwidth=[150, 100],  # Fixed column widths
    )
    
    # Add summary stats table to bottom right with scrolling
    fig.add_table(
        header=dict(
            values=list(stats.keys()),
            font=dict(size=12, color="white"),
            fill_color="rgb(55, 83, 109)",
            align="left",
            height=30
        ),
        cells=dict(
            values=list(stats.values()),
            font=dict(size=11),
            align="left",
            height=25
        ),
        row=2, col=2,
        columnwidth=[150, 100]  # Fixed column widths
    )
    
    # Apply styling
    fig.update_layout(
        template=create_bar_defaults()
    )
    
    # Verify structure
    assert len(fig.data) == 3  # bar + 2 tables
    assert fig.layout.title.text == "Genre Analysis"
    assert fig.layout.annotations[0].text == "Distribution by Genre"
    assert fig.layout.annotations[1].text == "Raw Data"
    assert fig.layout.annotations[2].text == "Summary Stats"
    
    # Show the figure
    fig.show()
