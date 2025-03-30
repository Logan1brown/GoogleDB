"""Quick visualization of market snapshot grid layout."""

import plotly.graph_objects as go
from src.dashboard.templates.grids.market_snapshot import create_market_snapshot_grid

# Create the grid
fig = create_market_snapshot_grid(
    title="TV Series Market Snapshot",
    distribution_title="Current Market Distribution"
)

# Row 2: Executive Summary
fig.add_annotation(
    text="Executive Summary: Strong growth in streaming platforms with increasing demand for original content.",
    xref="paper", yref="paper",
    x=0.5, y=0.85,  # Positioned in executive summary row
    showarrow=False,
    align="center",
    font=dict(size=14)
)

# Row 3: KPI Metrics
for i, (value, delta, title) in enumerate([
    (492, 32, "Total Shows"),
    (8.2, -0.5, "Avg Rating"),
    (156, 12, "New Series"),
    (45, 5, "Networks")
], 1):
    fig.add_trace(
        go.Indicator(
            mode="number+delta",
            value=value,
            delta={"reference": value - delta, "relative": True},
            title={"text": title},
        ),
        row=3, col=i
    )

# Row 4: Searchable Dropdowns
search_categories = [
    ("Shows", ["Stranger Things", "The Crown", "Bridgerton"]),
    ("Creators", ["Shonda Rhimes", "Ryan Murphy", "The Duffer Brothers"]),
    ("Genres", ["Drama", "Comedy", "Sci-Fi"]),
    ("Platforms", ["Netflix", "Amazon Prime", "Hulu"])
]

for i, (category, items) in enumerate(search_categories, 1):
    # Add category title at the top
    fig.add_trace(
        go.Scatter(
            x=[0.5],
            y=[0.8],
            text=[f"<b>{category}</b>"],
            mode='text',
            textposition="middle center",
            textfont=dict(
                size=14,
                color='#2c3e50'
            ),
            hoverinfo='none',
            showlegend=False
        ),
        row=4, col=i,
        secondary_y=False  # Use primary y-axis for title
    )
    
    # Add preview items below with different styling
    preview = "<br>".join(items) + "<br>..."
    fig.add_trace(
        go.Scatter(
            x=[0.5],
            y=[0.3],
            text=[preview],
            mode='text',
            textposition="middle center",
            textfont=dict(
                size=12,
                color='#7f8c8d'
            ),
            hoverinfo='none',
            showlegend=False
        ),
        row=4, col=i,
        secondary_y=True  # Use secondary y-axis for preview
    )

# Row 5: Market Distribution
fig.add_trace(
    go.Bar(
        x=["Netflix", "HBO", "Prime", "Disney+", "Apple TV+"],
        y=[35, 28, 22, 18, 15],
        text=[35, 28, 22, 18, 15],
        textposition="auto",
        marker_color='#3498db',
        hovertemplate='%{x}<br>%{y}%<extra></extra>'
    ),
    row=5, col=1
)

# Row 6: Performance Metrics
for i, (value, delta, title) in enumerate([
    (92, 5, "Viewer Score"),
    (4.8, 0.2, "Avg Budget"),
    (82, -3, "Renewal Rate"),
    (68, 8, "Int'l Reach")
], 1):
    fig.add_trace(
        go.Indicator(
            mode="number+delta",
            value=value,
            delta={"reference": value - delta, "relative": True},
            title={"text": title},
        ),
        row=6, col=i
    )

# Update axes for dropdowns to remove all lines/ticks
for i in range(1, 5):  # For each dropdown column
    fig.update_xaxes(showgrid=False, showticklabels=False, zeroline=False, row=4, col=i)
    fig.update_yaxes(showgrid=False, showticklabels=False, zeroline=False, row=4, col=i)
    # Also update secondary y-axis
    fig.update_yaxes(
        showgrid=False, showticklabels=False, zeroline=False,
        row=4, col=i, secondary_y=True
    )

# Show the figure in browser
fig.show()
