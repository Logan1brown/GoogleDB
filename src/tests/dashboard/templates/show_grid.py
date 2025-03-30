"""Simple script to show market snapshot grid layout."""

import plotly.graph_objects as go
from src.dashboard.templates.grids.market_snapshot import create_market_snapshot_grid

def main():
    # Create grid with titles
    fig = create_market_snapshot_grid(
        title="TV Series Market Snapshot",
        distribution_title="C