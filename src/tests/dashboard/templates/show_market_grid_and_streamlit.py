"""Example showing market snapshot grid with Streamlit integration."""

import plotly.graph_objects as go
from src.dashboard.templates.grids.market_snapshot import create_market_snapshot_grid

def show_grid_only():
    """Show just the Plotly grid layout (what the template provides)."""
    fig = create_market_snapshot_grid(
        title="TV Series Market Snapshot",
        distribution_title="Current Market Distribution"
    )

    # Row 2: Executive Summary
    fig.add_annotation(
        text="Executive Summary: Strong growth in streaming platforms with increasing demand for original content.",
        xref="paper", yref="paper",
        x=0.5, y=0.85,
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

    # Row 4: Empty space for Streamlit dropdowns
    # (This row will be blank in Plotly, filled by Streamlit)

    # Row 5: Market Distribution
    fig.add_trace(
        go.Bar(
            x=["Netflix", "HBO", "Prime", "Disney+", "Apple TV+"],
            y=[35, 28, 22, 18, 15],
            text=["35%", "28%", "22%", "18%", "15%"],  # Format as percentages
            textposition="auto",
            marker_color='#3498db',
            hovertemplate='%{x}<br>%{text}<extra></extra>'
        ),
        row=5, col=1
    )
    
    # Adjust bar chart axis
    fig.update_xaxes(
        row=5, col=1,
        tickangle=0,  # Keep labels horizontal
        title_standoff=25  # Move title away from axis
    )
    fig.update_yaxes(
        row=5, col=1,
        title_standoff=25  # Move title away from axis
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
                title={"text": title}
            ),
            row=6, col=i
        )

    fig.show()

def example_streamlit_integration():
    """Example of how this would be used in Streamlit (not runnable)."""
    # This is just example code - it won't run without Streamlit
    """
    import streamlit as st

    # Create the grid layout
    fig = create_market_snapshot_grid(...)
    
    # Add all the Plotly elements (KPIs, charts, etc)
    add_plotly_elements(fig)
    
    # Before showing the Plotly figure, add Streamlit dropdowns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.selectbox("Shows", ["Stranger Things", "The Crown", "Bridgerton"])
    
    with col2:
        st.selectbox("Creators", ["Shonda Rhimes", "Ryan Murphy", "The Duffer Brothers"])
    
    with col3:
        st.selectbox("Genres", ["Drama", "Comedy", "Sci-Fi"])
    
    with col4:
        st.selectbox("Platforms", ["Netflix", "Amazon Prime", "Hulu"])
    
    # Now show the Plotly figure
    st.plotly_chart(fig)
    """

if __name__ == "__main__":
    # Show just the grid layout
    show_grid_only()
