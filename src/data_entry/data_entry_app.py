import os
from datetime import date
from typing import Dict, List, Tuple
import difflib

import streamlit as st
from streamlit_searchbox import st_searchbox
from supabase import create_client

# Initialize Supabase client
supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_KEY')
)

# Cache lookup data
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_lookup_data() -> Dict[str, List[Dict]]:
    """Load lookup data for dropdowns"""
    lookups = {}
    
    # Load networks
    response = supabase.table('network_list').select('id, name').execute()
    lookups['networks'] = response.data
    
    # Load studios
    response = supabase.table('studio_list').select('id, name, type').execute()
    lookups['studios'] = response.data
    
    # Load genres
    response = supabase.table('genre_list').select('id, name').execute()
    lookups['genres'] = response.data
    
    # Load subgenres
    response = supabase.table('subgenre_list').select('id, name').execute()
    lookups['subgenres'] = response.data
    
    # Load source types
    response = supabase.table('source_types').select('id, name').execute()
    lookups['source_types'] = response.data
    
    # Load order types
    response = supabase.table('order_types').select('id, name').execute()
    lookups['order_types'] = response.data
    
    # Load status types
    response = supabase.table('status_types').select('id, name').execute()
    lookups['statuses'] = response.data
    
    # Load roles
    response = supabase.table('role_types').select('id, name').execute()
    lookups['roles'] = response.data
    
    return lookups

# Style constants
COLORS = {
    'text': {
        'primary': 'rgb(49, 51, 63)',
        'secondary': 'rgb(120, 120, 120)'
    },
    'background': '#FFFFFF',
    'accent': 'rgb(55, 83, 109)'
}

# Page config
st.set_page_config(
    page_title="TV Shows Data Entry",
    page_icon="📺",
    layout="wide"
)

# Set page styles
st.markdown("""
<style>
    /* Form labels */
    .stTextInput > label,
    .stTextArea > label,
    .stSelectbox > label,
    .stMultiSelect > label,
    .stDateInput > label,
    .stNumberInput > label {
        font-size: 14px;
        font-weight: bold;
        color: rgb(49, 51, 63);
    }
    
    /* Placeholder text */
    div[data-baseweb="select"] > div:first-child {
        color: rgba(49, 51, 63, 0.4);
        font-size: 16px;
    }
    
    /* Form field text */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div,
    .stMultiSelect > div > div > div,
    div[data-baseweb="select"] div[role="button"] {
        font-size: 16px;
        color: rgb(49, 51, 63);
    }
    
    /* Form field placeholder */
    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {
        color: rgba(49, 51, 63, 0.4);
    }
    
    /* Headers */
    h1 {
        font-size: 20px;
        font-weight: bold;
        color: rgb(49, 51, 63);
    }
    h2 {
        font-size: 16px;
        font-weight: bold;
        color: rgb(49, 51, 63);
    }
</style>
""", unsafe_allow_html=True)

# Session state for authentication
if 'user' not in st.session_state:
    st.session_state.user = None

def login():
    """Handle user login"""
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        
        if submitted:
            try:
                response = supabase.auth.sign_in_with_password({
                    "email": email,
                    "password": password
                })
                st.session_state.user = response.user
                st.success("Logged in successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Login failed: {str(e)}")

def main():
    """Main app logic"""
    if not st.session_state.user:
        st.markdown("# 📺 TV Shows Data Entry")
        st.markdown("Please login to continue")
        login()
        return
    
    # Main content
    st.markdown("# 📺 TV Shows Data Entry")
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["Add Show", "Edit Show", "Add Team Member"])
    
    with tab1:
        st.markdown("## Add New Show")
        
        # Load lookup data
        lookups = load_lookup_data()
        
        # Title search outside form
        st.write("### Check for Existing Shows")
        
        # Cache show titles
        @st.cache_data(ttl=3600)  # Cache for 1 hour
        def get_show_titles() -> List[str]:
            response = supabase.table('shows').select('title').execute()
            return [show['title'] for show in response.data]
        
        def search_shows(searchterm: str) -> List[str]:
            if not searchterm:
                return []
            searchterm = searchterm.lower()
            shows = get_show_titles()
            # First look for exact substring matches
            exact_matches = [show for show in shows if searchterm in show.lower()]
            if exact_matches:
                return exact_matches[:5]
            # If no substring matches, try fuzzy matching
            return difflib.get_close_matches(searchterm, shows, n=5, cutoff=0.6)
        
        # Initialize session state for search
        if 'search_text' not in st.session_state:
            st.session_state.search_text = ''
        
        # Track search text changes
        if 'show_search' in st.session_state and isinstance(st.session_state.show_search, dict):
            st.session_state.search_text = st.session_state.show_search.get('search', '')
            
        selected_title = st_searchbox(
            search_shows,
            placeholder="Search shows...",
            label="Search Title",
            key="show_search"
        )
        
        # Check if there are any matches
        current_text = st.session_state.search_text.strip()
        
        # Create a placeholder for status messages
        status_placeholder = st.empty()
        
        # Initialize form title from search if not already set
        if 'form_title' not in st.session_state:
            st.session_state.form_title = ''
        
        # Update form title only when search changes
        if current_text != st.session_state.get('last_search', ''):
            st.session_state.form_title = current_text
            st.session_state.last_search = current_text
        
        # Show warning if there are matches
        if current_text and len(current_text) >= 3:
            matches = search_shows(current_text)
            if matches:
                status_placeholder.warning("⚠️ Similar shows found in database: " + ", ".join(matches))
            else:
                status_placeholder.success("✅ No similar shows found in database.")
        
        # Initialize session state for storing form data if not exists
        if 'form_data' not in st.session_state:
            st.session_state.form_data = {}
        
        # Show Details Form
        with st.form("show_details_form"):
            st.subheader("Show Details")
            
            # Title from search
            title = st.text_input(
                "Title",
                value=st.session_state.get('form_title', ''),
                key="show_title_input",  # Different key from search state
                disabled=False  # Allow editing in case user wants to modify the title slightly
            )
            # Update form_title state with any manual edits
            st.session_state.form_title = title
            
            # Create two columns for the form layout
            left_col, right_col = st.columns(2)
            
            # Left Column
            with left_col:
                # Network
                network = st.selectbox(
                    "Network",
                    options=[(n['id'], n['name']) for n in lookups['networks']],
                    format_func=lambda x: x[1],
                    index=None,
                    key="network_dropdown"
                )
                network_id = network[0] if network else None
                
                # Genre selection
                genre = st.selectbox(
                    "Genre (optional)",
                    options=[(g['id'], g['name']) for g in lookups['genres']],
                    format_func=lambda x: x[1],
                    index=None,
                    key="genre_dropdown"
                )
                genre_id = genre[0] if genre else None
                
                # Subgenre selection
                subgenre = st.selectbox(
                    "Subgenre (optional)",
                    options=[(s['id'], s['name']) for s in lookups['subgenres']],
                    format_func=lambda x: x[1],
                    index=None,
                    key="subgenre_dropdown"
                )
                subgenre_id = subgenre[0] if subgenre else None
                
                # Source type selection
                source_type = st.selectbox(
                    "Source Type (optional)",
                    options=[(s['id'], s['name']) for s in lookups['source_types']],
                    format_func=lambda x: x[1],
                    index=None,
                    key="source_type_dropdown"
                )
                source_type_id = source_type[0] if source_type else None
            
            # Right Column
            with right_col:
                # Announcement Date
                date = st.date_input(
                    "Announcement Date (optional)",
                    value=None,
                    key="announcement_date"
                )
                
                # Episode count
                episode_count = st.number_input(
                    "Episode Count (optional)",
                    min_value=0,
                    value=0,
                    step=1,
                    help="Leave at 0 if unknown",
                    key="episode_count"
                )
                # Convert 0 to None for database storage
                episode_count = None if episode_count == 0 else episode_count
                
                # Order type selection
                order_type = st.selectbox(
                    "Order Type (optional)",
                    options=[(o['id'], o['name']) for o in lookups['order_types']],
                    format_func=lambda x: x[1],
                    index=None,
                    key="order_type_dropdown"
                )
                order_type_id = order_type[0] if order_type else None
                
                # Status selection
                status = st.selectbox(
                    "Status (optional)",
                    options=[(s['id'], s['name']) for s in lookups['statuses']],
                    format_func=lambda x: x[1],
                    index=None,
                    key="status_dropdown"
                )
                status_id = status[0] if status else None
            
            # Description (full width)
            description = st.text_area(
                "Description (optional)",
                key="description"
            )
                
            # Submit button
            show_details_submitted = st.form_submit_button("Save Show Details")
            
            if show_details_submitted:
                if not title:
                    st.error("Please search for a show title first")
                    return
                
                # Validate genre and subgenre aren't the same
                if genre and subgenre and genre[0] == subgenre[0]:
                    st.error("⚠️ Genre and Subgenre cannot be the same")
                    return
                
                form_data = {
                    'title': title,
                    'network_id': network_id,
                    'genre_id': genre_id,
                    'subgenre_id': subgenre_id,
                    'source_type_id': source_type_id,
                    'order_type_id': order_type_id,
                    'status_id': status_id,
                    'episode_count': None if episode_count == 0 else episode_count,
                    'description': description,
                    'announcement_date': date.isoformat() if date else None
                }
                st.session_state.form_data.update(form_data)
                st.success("Show details saved!")
                
                # Debug view
                with st.expander("Debug: View saved form data"):
                    st.json(form_data)
            
        # Studios Form
        with st.expander("Studios", expanded=True):
            st.subheader("Studios")
            with st.form("studios_form"):
                    # Filter for only type='Studio'
                    studio_options = [(s['id'], s['name']) for s in lookups['studios'] if s.get('type') == 'Studio']
                    
                    # Multi-select existing studios
                    selected_studios = st.multiselect(
                        "Select Studios",
                        options=studio_options,
                        format_func=lambda x: x[1],
                        key="studio_multiselect"
                    )
                    
                    # Number input for new studios
                    num_new_studios = st.number_input(
                        "Number of new studios to add (press Enter to confirm)",
                        min_value=0,
                        max_value=5,
                        value=0,
                        step=1,
                        help="Enter a number from 0-5 and press Enter to add that many studio fields",
                        key="num_new_studios"
                    )
                    
                    # Text inputs for new studios
                    new_studios = []
                    for i in range(num_new_studios):
                        new_name = st.text_input(
                            f"Studio Name {i+1}",
                            key=f"new_studio_{i}"
                        )
                        if new_name:
                            new_studios.append(new_name)
                    
                    # Submit button
                    studios_submitted = st.form_submit_button("Save Studios")
                    
                    if studios_submitted:
                        # Save to form data without creating in DB yet
                        studio_data = {
                            'selected_studios': selected_studios,  # List of (id, name) tuples for existing studios
                            'new_studios': [s for s in new_studios if s]  # List of new studio names to create
                        }
                        st.session_state.form_data['studios'] = studio_data
                        st.success("Studios saved! (Will be created when you submit all)")
                        
        # Debug view for studios (outside expander)
        if 'studios' in st.session_state.form_data:
            with st.expander("Debug: View saved studio data"):
                st.json(st.session_state.form_data['studios'])
        
        # Team Members Form
        with st.expander("Team Members", expanded=True):
            st.subheader("Team Members")
            with st.form("team_form"):
                # Number input for team members
                num_members = st.number_input(
                    "Number of team members to add (press Enter to confirm)",
                    min_value=0,
                    max_value=10,
                    value=0,
                    step=1,
                    help="Enter a number from 0-10 and press Enter to add that many member fields",
                    key="num_team_members"
                )
                
                # Team member inputs
                team_members = []
                for i in range(num_members):
                    col1, col2 = st.columns([3, 2])
                    
                    # Name input
                    with col1:
                        name = st.text_input(
                            f"Team Member {i+1}",
                            key=f"team_member_{i}_name"
                        )
                    
                    # Role multiselect
                    with col2:
                        roles = st.multiselect(
                            "Roles",
                            options=[(r['id'], r['name']) for r in lookups['roles']],
                            format_func=lambda x: x[1],
                            key=f"team_member_{i}_roles"
                        )
                    
                    if name:
                        team_members.append({
                            'name': name,
                            'role_ids': [r[0] for r in roles]
                        })
                
                # Submit button
                team_submitted = st.form_submit_button("Save Team Members")
                
                if team_submitted:
                    try:
                        # Process team members
                        member_data = {
                            'members': team_members
                        }
                        st.session_state.form_data['team'] = member_data
                        st.success("Team members saved!")
                    except Exception as e:
                        st.error(f"Error saving team members: {str(e)}")
        
        # Debug view for team members (outside expander)
        if 'team' in st.session_state.form_data:
            with st.expander("Debug: View saved team data"):
                st.json(st.session_state.form_data['team'])
        
        # Additional Info Form
        with st.expander("Additional Information", expanded=False):
            with st.form("additional_info_form"):
                tmdb_id = st.text_input(
                    "TMDB ID",
                    help="The Movie Database ID (if known)"
                )
                additional_submitted = st.form_submit_button("Save Additional Info")
                
                if additional_submitted:
                    st.session_state.form_data['tmdb_id'] = tmdb_id
                    st.success("Additional info saved!")
        
        # Debug view of combined data
        if st.session_state.form_data:
            with st.expander("Debug: Combined form data"):
                # Format data same way it will be submitted
                combined_data = {
                    'title': st.session_state.form_data.get('title'),
                    'studio_ids': st.session_state.form_data.get('studios', {}).get('studio_ids'),
                    'team_members': st.session_state.form_data.get('team', {}).get('members'),
                    'tmdb_id': st.session_state.form_data.get('tmdb_id')
                }
                st.json(combined_data)
        
        # Final Submit Button
        if st.button("Submit All", use_container_width=True):
            # Validate we have all required data
            if 'title' not in st.session_state.form_data:
                st.error("Please fill out and save show details first")
            elif 'studios' not in st.session_state.form_data:
                st.error("Please select or add studios first")
            elif 'team' not in st.session_state.form_data:
                st.error("Please add team members first")
            else:
                try:
                    # Process studios first
                    studio_data = st.session_state.form_data['studios']
                    studio_ids = [s[0] for s in studio_data['selected_studios']]  # IDs of existing studios
                    
                    # Add new studios
                    for studio_name in studio_data['new_studios']:
                        try:
                            # Check if studio exists (case insensitive)
                            existing = supabase.table('studio_list') \
                                .select('id, name') \
                                .ilike('name', studio_name) \
                                .execute()
                            
                            if existing.data:
                                # Studio exists, use its ID
                                studio_ids.append(existing.data[0]['id'])
                                st.warning(f"Using existing studio: {existing.data[0]['name']}")
                            else:
                                # Create new studio
                                response = supabase.table('studio_list').insert({
                                    "name": studio_name,
                                    "type": "production company"
                                }).execute()
                                if response.data:
                                    studio_ids.append(response.data[0]['id'])
                                    st.success(f"Added new studio: {studio_name}")
                        except Exception as e:
                            st.error(f"Error with studio '{studio_name}': {str(e)}")
                            continue
                    
                    # Format show data
                    show_data = {
                        'title': st.session_state.form_data['title'],
                        'studios': studio_ids if studio_ids else None,  # Array of all studio IDs
                        'tmdb_id': st.session_state.form_data.get('tmdb_id')
                    }
                    
                    # Add show to database
                    response = supabase.table('shows').insert(show_data).execute()
                    
                    if response.data:
                        show_id = response.data[0]['id']
                        
                        # Add team members
                        for member in st.session_state.form_data['team']['members']:
                            for role_id in member['role_ids']:
                                supabase.table('show_team').insert({
                                    'show_id': show_id,
                                    'name': member['name'],
                                    'role_id': role_id
                                }).execute()
                        
                        st.success(f"Successfully added show: {show_data['title']}")
                        # Clear form data
                        st.session_state.form_data = {}
                        st.rerun()
                    else:
                        st.error("Failed to add show to database")
                except Exception as e:
                    st.error(f"Error submitting show: {str(e)}")
                    # Clear form data
                    st.session_state.form_data = {}
                    st.session_state.form_title = ''
                    st.experimental_rerun()
                else:
                    st.error("Failed to add show")

                
                # Create new studio if needed
                studio_id = None
                if studio_selection[0] is None and new_studio_name:
                    # Add new studio
                    response = supabase.table('studios').insert({
                        'name': new_studio_name
                    }).execute()
                    
                    if response.data:
                        studio_id = response.data[0]['id']
                        st.success(f"Created new studio: {new_studio_name}")
                    else:
                        st.error("Failed to create new studio")
                        return
                else:
                    studio_id = studio_selection[0]
                
                # Add show
                show_data = {
                    'title': title,
                    'description': description if description else None,
                    'status_id': status[0] if status else None,
                    'network_id': network[0] if network else None,
                    'studio_id': studio_id,
                    'genre_id': genre[0] if genre else None,
                    'subgenres': [g[0] for g in subgenres] if subgenres else None,
                    'source_type_id': source_type[0] if source_type else None,
                    'order_type_id': order_type[0] if order_type else None,
                    'date': date.isoformat() if date else None,
                    'episode_count': episode_count if episode_count > 0 else None,
                    'tmdb_id': int(tmdb_id) if tmdb_id else None
                }
                
                # Add show and get its ID
                response = supabase.table('shows').insert(show_data).execute()
                
                if response.data:
                    st.success(f"Added show: {title}")
                    # Clear form
                    st.session_state.form_title = ''
                    st.experimental_rerun()
                else:
                    st.error("Failed to add show")
    
    with tab2:
        st.markdown("## Edit Existing Show")
        # TODO: Implement edit show form with fuzzy matching
    
    with tab3:
        st.markdown("## Add Team Member")
        # TODO: Implement team member form

if __name__ == "__main__":
    main()
