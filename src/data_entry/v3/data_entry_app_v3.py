import os
from datetime import date
from typing import Dict, List, Any
import streamlit as st
from supabase import create_client, Client

# Must be the first Streamlit command
st.set_page_config(page_title="Data Entry App", layout="wide")

# Initialize Supabase client
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SERVICE_KEY")

if not url or not key:
    st.error("""
    ⚠️ Missing Supabase credentials
    
    Please ensure you have a .env file in the project root with:
    SUPABASE_URL=your_url
    SUPABASE_KEY=your_key
    """)
    st.stop()

supabase: Client = create_client(url, key)

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_lookup_data() -> Dict[str, List[Dict]]:
    """Load all lookup data from Supabase with caching"""
    try:
        lookups = {}
        
        # Load networks
        response = supabase.table('network_list').select('id, network').execute()
        lookups['networks'] = {n['id']: n['network'] for n in response.data}
        
        # Load genres
        response = supabase.table('genre_list').select('id, genre').execute()
        lookups['genres'] = {g['id']: g['genre'] for g in response.data}
        
        # Load subgenres
        response = supabase.table('subgenre_list').select('id, subgenre').execute()
        lookups['subgenres'] = {s['id']: s['subgenre'] for s in response.data}
        
        # Load source types
        response = supabase.table('source_types').select('id, type').execute()
        lookups['source_types'] = {s['id']: s['type'] for s in response.data}
        
        # Load order types
        response = supabase.table('order_types').select('id, type').execute()
        lookups['order_types'] = {o['id']: o['type'] for o in response.data}
        
        # Load studios
        response = supabase.table('studio_list').select('id, studio').execute()
        lookups['studios'] = {s['id']: s['studio'] for s in response.data}
        
        # Load roles
        response = supabase.table('role_types').select('id, role').execute()
        lookups['roles'] = {r['id']: r['role'] for r in response.data}
        
        return lookups
    except Exception as e:
        st.error(f"Error loading lookup data: {str(e)}")
        return {
            'networks': {},
            'genres': {},
            'subgenres': {},
            'source_types': {},
            'order_types': {},
            'studios': {},
            'roles': {}
        }

def save_studios(studio_data: Dict) -> List[int]:
    """Process and save studios, return list of studio IDs"""
    studio_ids = studio_data['studio_ids']
    for studio_name in studio_data['new_studios']:
        # Check existing (case insensitive)
        existing = supabase.table('studio_list').select('id, studio').ilike('studio', studio_name).execute()
        if existing.data:
            studio_ids.append(existing.data[0]['id'])
            st.success(f"Using existing studio: {existing.data[0]['studio']}")
        else:
            # Create new
            response = supabase.table('studio_list').insert({
                "studio": studio_name,
                "type": "production company"
            }).execute()
            if response.data:
                studio_ids.append(response.data[0]['id'])
                st.success(f"Added new studio: {studio_name}")
    return studio_ids

def save_team(show_id: int, team_data: List[Dict]) -> None:
    """Save team members for a show"""
    for member in team_data:
        for role_id in member['role_ids']:
            supabase.table('show_team').insert({
                'show_id': show_id,
                'name': member['name'],
                'role_type_id': role_id
            }).execute()

def save_show(form_data: Dict) -> bool:
    """Save show and related data"""
    try:
        # Process studios first
        studio_ids = save_studios(form_data['studios'])
        
        # Format show data
        show_data = {
            'title': form_data['title'],
            'network_id': form_data.get('network_id'),
            'genre_id': form_data.get('genre_id'),
            'subgenres': [form_data.get('subgenre_id')] if form_data.get('subgenre_id') else [],
            'source_type_id': form_data.get('source_type_id'),
            'order_type_id': form_data.get('order_type_id'),
            'status_id': form_data.get('status_id'),
            'episode_count': form_data.get('episode_count'),
            'description': form_data.get('description'),
            'studios': studio_ids,
            'tmdb_id': form_data.get('tmdb_id'),
            'date': form_data.get('announcement_date')
        }
        
        # Validate required fields
        if not show_data['network_id']:
            raise ValueError('Network is required')
        
        # Check if show exists
        existing = supabase.table('shows').select('id, title').eq('title', show_data['title']).execute()
        if existing.data:
            raise ValueError(f"A show with title '{show_data['title']}' already exists")
        
        # Save show
        response = supabase.table('shows').insert(show_data).execute()
        if response.data:
            show_id = response.data[0]['id']
            save_team(show_id, form_data['team']['members'])
            st.success(f"✅ Successfully added: {show_data['title']}")
            return True
        else:
            st.error("⚠️ Show not saved - Database error")
            return False
    except Exception as e:
        error_msg = str(e)
        if "duplicate key" in error_msg.lower():
            st.error("⚠️ Show not saved - A show with this title already exists")
        elif "network" in error_msg.lower():
            st.error("⚠️ Show not saved - Network is required")
        else:
            st.error(f"⚠️ Error saving show: {error_msg}")
        return False

def init_session_state():
    """Initialize session state variables"""
    # Auth state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    # Active tab state
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = 0
    
    # Current page tracking
    if 'current_page' not in st.session_state:
        st.session_state.current_page = None
        
    # Load lookup data
    if 'lookups' not in st.session_state:
        st.session_state.lookups = load_lookup_data()
    
    # Initialize show data structure if not present
    if 'show_data' not in st.session_state:
        st.session_state.show_data = {
            'title': '',
            'network_id': None,
            'genre_id': None,
            'subgenre_id': None,
            'source_type_id': None,
            'order_type_id': None,
            'episode_runtime': 0,
            'start_date': None,
            'studio_ids': [],
            'new_studios': [],
            'team_members': []
        }
        
    # Initialize counters if not present
    if 'num_new_studios' not in st.session_state:
        st.session_state.num_new_studios = 0
    if 'num_team_members' not in st.session_state:
        st.session_state.num_team_members = 0
    
    # Track current page
    current_page = __file__
    if 'current_page' not in st.session_state:
        st.session_state.current_page = current_page

def login():
    """Handle user login"""
    # If already logged in, return True
    if 'authenticated' in st.session_state and st.session_state.authenticated:
        return True
        
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        
        if submitted:
            try:
                # Get auth token
                auth = supabase.auth.sign_in_with_password({
                    "email": email,
                    "password": password
                })
                
                # Store auth in session
                st.session_state.user = auth.user
                st.session_state.access_token = auth.session.access_token
                st.session_state.refresh_token = auth.session.refresh_token
                st.session_state.authenticated = True
                
                # Update Supabase client with auth token
                supabase.auth.set_session(auth.session.access_token, auth.session.refresh_token)
                
                st.success("Logged in successfully!")
                st.rerun()
                return True
            except Exception as e:
                st.error(f"Login failed: {str(e)}")
                st.session_state.authenticated = False
                return False
                
    return False

def render_studio_inputs(num_studios: int) -> List[str]:
    """Render studio input fields"""
    new_studios = []
    for i in range(num_studios):
        name = st.text_input(
            f"New Studio {i+1}",
            key=f"new_studio_{i}",
            value=st.session_state.get(f"new_studio_{i}", "")
        )
        if name and name.strip():
            new_studios.append(name.strip())
    return new_studios

def render_team_inputs(num_team: int, roles: List[Dict]) -> List[Dict]:
    """Render team member input fields"""
    team = []
    for i in range(num_team):
        col1, col2 = st.columns([3, 2])
        with col1:
            name = st.text_input(
                f"Team Member {i+1} Name",
                key=f"team_member_{i}_name"
            )
        with col2:
            member_roles = st.multiselect(
                "Role(s)",
                options=[(r['id'], r['name']) for r in roles],
                format_func=lambda x: x[1],
                key=f"team_member_{i}_roles"
            )
        if name and name.strip() and member_roles:
            team.append({
                'name': name.strip(),
                'role_ids': [r[0] for r in member_roles]
            })
    return team

def main():
    """Main application homepage"""
    # Import menu here to avoid circular imports
    from data_entry_menu import menu
    
    # Initialize session state first
    init_session_state()
    
    # Show menu based on auth state
    menu()
    
    # Handle login if not authenticated
    if not st.session_state.authenticated:
        login()
        return
    
    # Show main content
    st.title("Show Data Entry")
    st.write("""
    Welcome to the Show Data Entry application! Use the sidebar to navigate between pages:
    
    - **Add Show**: Add a new show to the database
    - **Edit Show**: Modify an existing show's details
    - **Remove Show**: Remove a show from the database
    """)
    
    # Show some stats or recent activity
    st.subheader("Recent Activity")
    st.info("Coming soon! This section will show recent changes to the database.")


if __name__ == "__main__":
    main()
