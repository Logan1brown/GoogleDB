"""Test file to isolate chart display issue."""

import streamlit as st
import pandas as pd
from ...data_processing.market_analysis.market_analyzer import MarketAnalyzer
from ..templates.grids.chart_only import create_chart_grid

# Create test data
test_data = pd.DataFrame({
    'network': ['ABC', 'NBC', 'CBS', 'ABC', 'NBC', 'FOX', 'ABC'],
    'studio': ['Studio A', 'Studio B', 'Studio C', 'Studio A', 'Studio B', 'Studio D', 'Studio A'],
    'success_score': [80, 70, 90, 85, 75, 95, 82]
})

# Create analyzer
analyzer = MarketAnalyzer(test_data)

# Create chart directly
direct_chart = analyzer.create_network_chart()
st.write("Direct Chart (no grid):")
st.plotly_chart(direct_chart)

# Create chart with grid
grid = create_chart_grid(
    title="Show Distribution by Network",
    margin=dict(l=50, r=50, t=80, b=50)
)
grid.add_trace(direct_chart.data[0])
st.write("Chart with Grid:")
st.plotly_chart(grid)
