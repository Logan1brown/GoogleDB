"""
TV Series Database Dashboard
Main application file for the Streamlit dashboard.
"""

import streamlit as st

# Configure the app
st.set_page_config(
    page_title="TV Series Database",
    page_icon="📺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main page content
st.title("📺 TV Series Database")
st.sidebar.success("Select a page from the menu above.")

# Overview content
st.markdown("""
### Welcome to the TV Series Database Dashboard

This dashboard provides tools for:
- 📊 Market analysis and insights
- 📈 Content performance tracking
- 🏢 Studio performance metrics
- ✨ Data entry and management

Select a page from the menu to get started.
""")
