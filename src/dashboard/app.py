"""
TV Series Database Dashboard
Main application file for the Streamlit dashboard.

This dashboard provides:
- Automatic insights about TV series data
- Interactive visualizations
- Trend analysis
"""

import os
import sys

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Add src directory to Python path
src_dir = os.path.join(project_root, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

import streamlit as st
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Set up Plotly template for consistent styling
import plotly.io as pio
pio.templates.default = "plotly_white"

def main():
    """Main entry point for the dashboard."""
    # Custom CSS for section headers
    st.markdown("""
        <style>
        .section-header {
            font-family: 'Source Sans Pro', sans-serif;
            text-transform: uppercase;
            font-weight: 600;
            letter-spacing: 0.1em;
            color: #1E4D8C;
            margin-bottom: 1em;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("STS Analysis Dashboard")
    
    # Welcome message
    st.markdown("""
        Welcome to the TV Series Database Dashboard. Use the navigation menu in the sidebar
        to explore different views and analyses.
    """)

if __name__ == "__main__":
    main()
