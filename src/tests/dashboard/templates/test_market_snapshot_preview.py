"""Preview test for market snapshot grid."""
import plotly.graph_objects as go
from src.dashboard.templates.grids.market_snapshot import create_market_snapshot_grid

# Create the base grid
fig = create_market_snapshot_grid()

# 1. Add header title
fig.add_trace(
    go.Scatter(x=[0.5], y=[0.5], text=["TV Series Market Pulse"], mode='text'),
    row=1, col=1
)

# 2. Add executive summary
fig.add_trace(
    go.Scatter(x=[0.5], y=[0.5], 
              text=["Current market shows 25% increase in multi-hyphenate creators, with drama dominating but comedy growing fastest."],
              mode='text'),
    row=2, col=1
)

# 3. Add KPI widgets
kpis = [
    {'title': 'Total Shows', 'value': 342, 'change': 15},
    {'title': 'Avg Budget', 'value': 3.2, 'change': 8},
    {'title': 'New Creators', 'value': 127, 'change': 22},
    {'title': 'Market Share', 'value': 23, 'change': 5}
]

for i, kpi in enumerate(kpis):
    fig.add_trace(
        go.Indicator(
            mode="number+delta",
            value=kpi['value'],
            title={'text': kpi['title']},
            delta={'reference': 100, 'relative': True, 'valueformat': '.0%', 'value': kpi['change']}
        ),
        row=3, col=i+1
    )

# 4. Add searchable dropdowns
dropdowns = [
    ('Shows', ['Stranger Things', 'The Crown', 'Bridgerton']),
    ('Creators', ['Shonda Rhimes', 'Ryan Murphy', 'The Duffer Brothers']),
    ('Networks', ['Netflix', 'Amazon', 'Hulu']),
    ('Genres', ['Drama', 'Comedy', 'Sci-Fi'])
]

for i, (title, items) in enumerate(dropdowns):
    fig.add_trace(
        go.Scatter(x=[0.5], y=[0.5],
                  text=[f"{title}\n" + "\n".join(items)],
                  mode='text'),
        row=4, col=i+1
    )

# 5. Add market distribution chart
fig.add_trace(
    go.Bar(
        x=['Q1', 'Q2', 'Q3', 'Q4'],
        y=[10, 15, 13, 17],
        name='Market Share'
    ),
    row=5, col=1
)

# 6. Add key metrics
metrics = [
    {'title': 'ROI', 'value': 127, 'change': 12},
    {'title': 'Engagement', 'value': 85, 'change': 5},
    {'title': 'Retention', 'value': 92, 'change': 3},
    {'title': 'Growth', 'value': 45, 'change': 15}
]

for i, metric in enumerate(metrics):
    fig.add_trace(
        go.Indicator(
            mode="number+delta",
            value=metric['value'],
            title={'text': metric['title']},
            delta={'reference': 100, 'relative': True, 'valueformat': '.0%', 'value': metric['change']}
        ),
        row=6, col=i+1
    )

# Display with streamlit
import streamlit as st
st.plotly_chart(fig, use_container_width=True)
