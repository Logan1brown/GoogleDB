"""Custom navigation menu for the data entry app."""
import streamlit as st

def authenticated_menu():
    """Show navigation menu for authenticated users."""
    # Data Entry section
    st.sidebar.markdown("### Data Entry")
    st.sidebar.page_link("data_entry_app_v3.py", label="🏠 Home")
    st.sidebar.page_link("pages/1_add_show.py", label="➕ Add Show")
    st.sidebar.page_link("pages/2_edit_show.py", label="✏️ Edit Show")
    st.sidebar.page_link("pages/3_remove_show.py", label="❌ Remove Show")
    
    # TMDB Integration section (if we add those pages later)
    st.sidebar.markdown("### TMDB Integration")
    st.sidebar.page_link(
        "pages/4_tmdb_matches.py",
        label="🔍 Review Matches",
        disabled=True  # Enable when implemented
    )
    st.sidebar.page_link(
        "pages/5_tmdb_metrics.py",
        label="📊 TMDB Metrics",
        disabled=True  # Enable when implemented
    )

def unauthenticated_menu():
    """Show navigation menu for unauthenticated users."""
    st.sidebar.page_link("data_entry_app_v3.py", label="🔑 Login")

def menu():
    """Show the appropriate menu based on authentication state."""
    if "authenticated" not in st.session_state or not st.session_state.authenticated:
        unauthenticated_menu()
        return
    authenticated_menu()

def menu_with_redirect():
    """Show menu and handle auth state."""
    # Just show menu - let the page handle auth
    menu()
