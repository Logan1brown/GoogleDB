"""Test the market snapshot layout."""

import plotly.graph_objects as go
from src.dashboard.templates.grids.market_snapshot import create_market_snapshot_grid
from src.dashboard.templates.defaults import create_bar_defaults


def test_market_snapshot_grid():
    """Test that market snapshot layout works correctly."""
    # Create figure with grid layout
    fig = create_market_snapshot_grid(
        title="Current Market Analysis",
        distribution_title="Genre Distribution",
        indicators_title="Market Indicators"
    )
    
    # Add executive summary
    summary = (
        "Current market analysis shows strong performance in drama and comedy genres, "
        "with 23% overall market share. Original content drives 70% of engagement, "
        "while maintaining healthy ROI across all categories."
    )
    fig.add_trace(
        go.Scatter(
            x=[0.5],  # Center point
            y=[0.5],
            text=[summary],
            mode='text',
            textfont=dict(size=14),
            hoverinfo='none'
        ),
        row=2, col=1  # Executive summary goes in row 2
    )
    
    # Add searchable dropdown section
    search_categories = [
        ("Shows", ["Stranger Things", "The Crown", "Bridgerton"]),
        ("Creators", ["Shonda Rhimes", "Ryan Murphy", "The Duffer Brothers"]),
        ("Genres", ["Drama", "Comedy", "Sci-Fi"]),
        ("Platforms", ["Netflix", "Amazon Prime", "Hulu"])
    ]
    
    for i, (category, items) in enumerate(search_categories):
        # Add category and preview
        preview = "<br>".join(items) + "<br>..."
        fig.add_trace(
            go.Scatter(
                x=[0.5],  # Center point
                y=[0.7, 0.3],  # Title at top, content below
                text=[f"<b>{category}</b>", preview],
                mode='text',
                textfont=dict(
                    size=[14, 12],
                    color=['#2c3e50', '#7f8c8d']
                ),
                hoverinfo='none'
            ),
            row=4, col=i+1  # Searchable dropdowns go in row 4
        )
    
    # Add top KPI metric cards
    top_metrics = [
        ("Total Shows", 1245, "+15%"),
        ("Market Share", 23, "-2%"),
        ("Avg Budget", 2.5, "+8%"),
        ("ROI", 185, "+25%")
    ]
    
    for i, (title, value, delta) in enumerate(top_metrics, 1):
        fig.add_trace(
            go.Indicator(
                mode="number+delta",
                value=value,
                title={
                    'text': title,
                    'font': {'size': 14}
                },
                delta={
                    'reference': value * (1 - float(delta.strip('%+-'))/100),
                    'relative': True,
                    'valueformat': '.1%',
                    'font': {'size': 14}
                },
                number={
                    'font': {'size': 24},
                    'valueformat': (
                        ',.0f' if title in ["Total Shows", "ROI"] else
                        '.0%' if title == "Market Share" else
                        '$.1fM'
                    )
                }
            ),
            row=3, col=i
        )
    
    # Add market distribution chart
    genres = ['Drama', 'Comedy', 'Action', 'Thriller', 'Romance', 
             'Horror', 'Documentary', 'Animation']
    shares = [25, 20, 15, 12, 10, 8, 6, 4]
    
    fig.add_trace(
        go.Bar(
            name="Market Share",
            x=genres,
            y=shares,
            text=shares,
            textposition='auto'
        ),
        row=5, col=1  # Market distribution chart goes in row 5
    )
    
    # Add bottom metric cards
    bottom_metrics = [
        ("Content Mix", 70, "+5%"),   # 70% original content
        ("Engagement", 4.2, "+12%"),  # 4.2 hours/user/week
        ("Retention", 92, "+3%"),    # 92% monthly retention
        ("Growth", 18, "+4%")       # 18% YoY growth
    ]
    
    for i, (title, value, delta) in enumerate(bottom_metrics, 1):
        fig.add_trace(
            go.Indicator(
                mode="number+delta",
                value=value,
                title={
                    'text': title,
                    'font': {'size': 14}
                },
                delta={
                    'reference': value * (1 - float(delta.strip('%+-'))/100),
                    'relative': True,
                    'valueformat': '.1%',
                    'font': {'size': 14}
                },
                number={
                    'font': {'size': 24},
                    'valueformat': (
                        '.0%' if title in ["Content Mix", "Retention"] else
                        '.1f' if title == "Engagement" else
                        '.0f'
                    )
                }
            ),
            row=6, col=i  # Bottom metrics go in row 6
        )
    
    # Show the figure
    fig.show()
