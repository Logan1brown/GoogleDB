import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path

# Sample data
labels = ["Network", "ABC", "NBC", "CBS", 
          "Creator 1", "Creator 2", "Creator 3", "Creator 4", "Creator 5"]
parents = ["", "Network", "Network", "Network", 
          "ABC", "ABC", "NBC", "CBS", "CBS"]
values = [0, 2, 2, 2,  # Network level
         1, 1, 2, 1, 1]  # Creator level

# Create figure with subplots
fig = make_subplots(
    rows=2, cols=2,
    specs=[
        [{'type': 'table'}, {'type': 'domain'}],  # Top row: table and sunburst
        [{'type': 'table', 'colspan': 2}, None]   # Bottom row: full-width table
    ],
    column_widths=[0.6, 0.4]
)

# Add sunburst trace
fig.add_trace(
    go.Sunburst(
        labels=labels,
        parents=parents,
        values=values,
        branchvalues='total',
        hovertemplate='<b>%{label}</b><br>Creators: %{value}<br><extra></extra>',
        maxdepth=2
    ),
    row=1, col=2
)

# Add a dummy table trace (just to match structure)
fig.add_trace(
    go.Table(
        header=dict(values=['Column']),
        cells=dict(values=[['Data']])
    ),
    row=1, col=1
)

# Update layout
fig.update_layout(
    title="Network Connections Test",
    width=1200,
    height=800
)

# Save figure
output_dir = Path('output/network_analysis/creative_networks')
output_dir.mkdir(parents=True, exist_ok=True)
fig.write_html(output_dir / 'test_sunburst.html')
