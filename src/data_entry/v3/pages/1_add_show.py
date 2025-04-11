"""Add a new show to the database."""
import streamlit as st
import sys
import os
from datetime import date

# Add parent directory to path so we can import from the parent
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

# Import menu and data functions
from data_entry_menu import menu
from data_entry_app_v3 import (
    load_lookup_data,
    save_show,
    supabase
)

# Initialize session state
if 'show_data' not in st.session_state:
    st.session_state.show_data = {
        'title': '',
        'network_id': None,
        'genre_id': None,
        'subgenre_id': None,
        'source_type_id': None,
        'order_type_id': None,
        'episode_runtime': 0,
        'start_date': date.today(),
        'studio_ids': [],
        'new_studios': [],
        'team_members': []
    }

if 'active_tab' not in st.session_state:
    st.session_state.active_tab = 0

if 'num_new_studios' not in st.session_state:
    st.session_state.num_new_studios = 0

if 'num_team_members' not in st.session_state:
    st.session_state.num_team_members = 0

# Show menu
menu()

# Check auth before showing content
if not st.session_state.authenticated:
    st.warning("Please log in to access this page")
    st.stop()

# Load lookup data
try:
    lookups = load_lookup_data()
    if not lookups:
        st.error("Failed to load required data. Please refresh the page.")
        st.stop()
    
    # Store lookups in session state
    st.session_state.lookups = lookups
        
except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.stop()

# Page title
st.title("Add New Show")

# Tab indices
TAB_DETAILS = 0
TAB_STUDIOS = 1
TAB_TEAM = 2
TAB_REVIEW = 3

# Helper functions
def format_lookup(key: str):
    """Format lookup values for dropdowns"""
    def _format(x):
        if x is None:
            return f'Select {key.replace("_", " ").title()}...'
        return st.session_state.lookups[key].get(x, str(x))
    return _format

def on_show_submit():
    """Save show details"""
    st.session_state.show_data.update({
        'title': st.session_state.title,
        'network_id': st.session_state.network_id,
        'genre_id': st.session_state.genre_id,
        'subgenre_id': st.session_state.subgenre_id,
        'source_type_id': st.session_state.source_type_id,
        'order_type_id': st.session_state.order_type_id,
        'episode_runtime': st.session_state.episode_runtime,
        'start_date': st.session_state.start_date
    })
    st.session_state.active_tab = TAB_STUDIOS

def on_studios_submit():
    """Save studio selections"""
    st.session_state.show_data['studio_ids'] = st.session_state.studio_ids
    st.session_state.show_data['new_studios'] = [
        st.session_state[f'new_studio_{i}']
        for i in range(st.session_state.num_new_studios)
        if st.session_state[f'new_studio_{i}']
    ]
    st.session_state.active_tab = TAB_TEAM

def on_team_submit():
    """Save team members"""
    st.session_state.show_data['team_members'] = [
        {
            'name': st.session_state[f'member_name_{i}'],
            'role_ids': st.session_state[f'member_roles_{i}']
        }
        for i in range(st.session_state.num_team_members)
        if st.session_state.get(f'member_name_{i}') and st.session_state.get(f'member_roles_{i}')
    ]
    st.session_state.active_tab = TAB_REVIEW

# Create tabs
tabs = st.tabs(["Show Details", "Studios", "Team Members", "Review"])

# Show Details Tab
with tabs[TAB_DETAILS]:
    st.subheader("Add Show Details")
    
    with st.form("show_details_form"):
        # Title
        st.text_input(
            "Title",
            key="title",
            value=st.session_state.show_data['title']
        )
        
        # Network
        st.selectbox(
            "Network",
            key="network",
            options=list(st.session_state.lookups['networks'].keys()),
            format_func=format_lookup('networks'),
            index=None if st.session_state.show_data['network_id'] is None else 
                list(st.session_state.lookups['networks'].keys()).index(st.session_state.show_data['network_id'])
        )
        
        # Genre
        st.selectbox(
            "Genre",
            key="genre",
            options=list(st.session_state.lookups['genres'].keys()),
            format_func=format_lookup('genres'),
            index=None if st.session_state.show_data['genre_id'] is None else 
                list(st.session_state.lookups['genres'].keys()).index(st.session_state.show_data['genre_id'])
        )
        
        # Subgenre
        st.selectbox(
            "Subgenre",
            key="subgenre",
            options=list(st.session_state.lookups['subgenres'].keys()),
            format_func=format_lookup('subgenres'),
            index=None if st.session_state.show_data['subgenre_id'] is None else 
                list(st.session_state.lookups['subgenres'].keys()).index(st.session_state.show_data['subgenre_id'])
        )
        
        # Source Type
        st.selectbox(
            "Source Type",
            key="source_type",
            options=list(st.session_state.lookups['source_types'].keys()),
            format_func=format_lookup('source_types'),
            index=None if st.session_state.show_data['source_type_id'] is None else 
                list(st.session_state.lookups['source_types'].keys()).index(st.session_state.show_data['source_type_id'])
        )
        
        # Order Type
        st.selectbox(
            "Order Type",
            key="order_type",
            options=list(st.session_state.lookups['order_types'].keys()),
            format_func=format_lookup('order_types'),
            index=None if st.session_state.show_data['order_type_id'] is None else 
                list(st.session_state.lookups['order_types'].keys()).index(st.session_state.show_data['order_type_id'])
        )
        
        # Episode Runtime
        st.number_input(
            "Episode Runtime (minutes)",
            key="episode_runtime",
            min_value=0,
            value=st.session_state.show_data['episode_runtime']
        )
        
        # Start Date
        st.date_input(
            "Start Date",
            key="start_date",
            value=st.session_state.show_data['start_date']
        )
        
        # Submit button
        if st.form_submit_button("Continue to Studios", type="primary"):
            # Update show data
            st.session_state.show_data.update({
                'title': st.session_state.title,
                'network_id': st.session_state.network,
                'genre_id': st.session_state.genre,
                'subgenre_id': st.session_state.subgenre,
                'source_type_id': st.session_state.source_type,
                'order_type_id': st.session_state.order_type,
                'episode_runtime': st.session_state.episode_runtime,
                'start_date': st.session_state.start_date
            })
            st.rerun()

# Studios Tab
with tabs[TAB_STUDIOS]:
    st.subheader("Add Studios")
    
    with st.form("studios_form"):
        # Existing studios
        st.multiselect(
            "Select Existing Studios",
            key="studio_ids",
            options=list(st.session_state.lookups['studios'].keys()),
            format_func=format_lookup('studios'),
            default=st.session_state.show_data['studio_ids']
        )
        
        # New studios
        st.number_input(
            "Number of New Studios to Add",
            key="num_new_studios",
            min_value=0,
            value=st.session_state.num_new_studios
        )
        
        # New studio inputs
        new_studios = []
        for i in range(st.session_state.num_new_studios):
            new_studio = st.text_input(f"New Studio {i+1}", key=f"new_studio_{i}")
            if new_studio:
                new_studios.append(new_studio)
        
        if st.form_submit_button("Continue to Team Members", type="primary"):
            # Update show data
            st.session_state.show_data['studio_ids'] = st.session_state.studio_ids
            st.session_state.show_data['new_studios'] = new_studios
            st.session_state.active_tab = TAB_TEAM
            st.rerun()

# Team Members Tab
with tabs[TAB_TEAM]:
    st.subheader("Add Team Members")
    
    with st.form("team_members_form"):
        # Number of team members
        st.number_input(
            "Number of Team Members to Add",
            key="num_team_members",
            min_value=0,
            value=st.session_state.num_team_members
        )
        
        # Team member inputs
        team_members = []
        for i in range(st.session_state.num_team_members):
            st.markdown(f"### Team Member {i+1}")
            
            name = st.text_input(f"Name", key=f"team_member_{i}_name")
            roles = st.multiselect(
                "Roles",
                options=list(st.session_state.lookups['roles'].keys()),
                format_func=format_lookup('roles'),
                key=f"member_roles_{i}"
            )
            
            if name and roles:
                team_members.append({
                    'name': name,
                    'role_ids': roles
                })
        
        if st.form_submit_button("Continue to Review", type="primary"):
            # Update show data
            st.session_state.show_data['team_members'] = team_members
            st.session_state.active_tab = TAB_REVIEW
            st.rerun()

# Review Tab
with tabs[TAB_REVIEW]:
    st.subheader("Review Show Details")
    
    # Show Details
    st.markdown("### 📺 Show Information")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Title:**", st.session_state.show_data['title'] or "*Not set*")
        st.write("**Network:**", format_lookup('networks')(st.session_state.show_data['network_id']))
        st.write("**Genre:**", format_lookup('genres')(st.session_state.show_data['genre_id']))
        st.write("**Subgenre:**", format_lookup('subgenres')(st.session_state.show_data['subgenre_id']))
    
    with col2:
        st.write("**Source Type:**", format_lookup('source_types')(st.session_state.show_data['source_type_id']))
        st.write("**Order Type:**", format_lookup('order_types')(st.session_state.show_data['order_type_id']))
        st.write("**Episode Runtime:**", f"{st.session_state.show_data['episode_runtime']} minutes")
        st.write("**Start Date:**", st.session_state.show_data['start_date'].strftime('%Y-%m-%d'))
    
    # Studios
    st.markdown("### 🎬 Studios")
    
    # Existing studios
    if st.session_state.show_data['studio_ids']:
        st.write("**Selected Studios:**")
        for studio_id in st.session_state.show_data['studio_ids']:
            st.write(f"- {format_lookup('studios')(studio_id)}")
    
    # New studios
    if st.session_state.show_data['new_studios']:
        st.write("**New Studios:**")
        for studio in st.session_state.show_data['new_studios']:
            st.write(f"- {studio}")
    
    # Team Members
    if st.session_state.show_data['team_members']:
        st.markdown("### 👥 Team Members")
        for i, member in enumerate(st.session_state.show_data['team_members'], 1):
            st.markdown(f"**Team Member {i}**")
            st.write(f"Name: {member['name']}")
            st.write("Roles:")
            for role_id in member['role_ids']:
                st.write(f"- {format_lookup('roles')(role_id)}")
    
    # Submit button
    if st.button("Submit Show", type="primary"):
        try:
            # Save show to database
            save_show(st.session_state.show_data)
            st.success("Show saved successfully!")
            
            # Reset form
            st.session_state.show_data = {
                'title': '',
                'network_id': None,
                'genre_id': None,
                'subgenre_id': None,
                'source_type_id': None,
                'order_type_id': None,
                'episode_runtime': 0,
                'start_date': date.today(),
                'studio_ids': [],
                'new_studios': [],
                'team_members': []
            }
            st.session_state.active_tab = TAB_DETAILS
            st.session_state.num_new_studios = 0
            st.session_state.num_team_members = 0
            
            # Rerun to refresh the page
            st.rerun()
            
        except Exception as e:
            st.error(f"Error saving show: {str(e)}")
