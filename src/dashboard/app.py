"""
TV Series Database Dashboard
Main application file for the Streamlit dashboard.
"""

import streamlit as st

# Define pages with custom titles
pg = st.navigation([
    st.Page("pages/overview.py", title="Overview"),
    st.Page("pages/1_market_snapshot.py", title="Market Snapshot"),
    st.Page("pages/2_content_analysis.py", title="Content Analysis"),
    st.Page("pages/3_studio_performance.py", title="Studio Performance")
])

# Run the selected page
pg.run()
