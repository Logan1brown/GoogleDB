# Data Entry App V2 Proposal

## Current Issues
1. Form sections are overly complex with expanders and Continue buttons
2. Message handling is scattered across different sections
3. Session state management is more complex than needed
4. Code organization could be clearer

## Proposed Solution

### File Structure
```
src/data_entry/
├── v1/ (current implementation)
└── v2/
    └── data_entry_app.py (~470 lines)
```

### Key Components

```python
# Constants and setup
COLORS = {...}
REQUIRED_FIELDS = [...]

# Database functions
def load_lookup_data():
    """Load all lookup data at once"""

def search_shows(title):
    """Search for similar shows"""

def load_all_shows():
    """Get all shows for edit selector"""
    return supabase.table('shows').select('*').execute().data

def save_show(data):
    """Save new show in one transaction"""

def update_show(show_id, data):
    """Update existing show and related data"""
    with supabase.transaction() as txn:
        txn.table('shows').update(data).eq('id', show_id)
        # Update studios and team members
        update_show_relations(txn, show_id, data)

def delete_show(show_id):
    """Delete show and all related data"""
    with supabase.transaction() as txn:
        txn.table('show_team').delete().eq('show_id', show_id)
        txn.table('show_studios').delete().eq('show_id', show_id)
        txn.table('shows').delete().eq('id', show_id)

# Main app
def main():
    tab1, tab2 = st.tabs(["Add Show", "Edit/Remove Show"])
    
    with tab1:
        # Search section (outside form)
        search_text = st.text_input("Search Shows")
        status = st.empty()  # For search results
        
        # Add form
        with st.form("add_show_form"):
            title = st.text_input("Title", value=search_text)
            network = st.selectbox(...)
            
            # Studios section
            selected_studios = st.multiselect(...)
            num_new_studios = st.number_input(...)
            
            # Team section
            num_team = st.number_input(...)
            
            # Submit and validate
            if st.form_submit_button("Add Show"):
                if validate_form():
                    save_show(get_form_data())
    
    with tab2:
        # Show selector for edit
        shows = load_all_shows()
        selected = st.selectbox("Select Show", shows, 
                              format_func=lambda x: x['title'])
        
        if selected:
            with st.form("edit_show_form"):
                # Same fields as add form but pre-filled
                title = st.text_input("Title", value=selected['title'])
                network = st.selectbox(..., default=selected['network'])
                
                # Load and show existing data
                existing_studios = load_show_studios(selected['id'])
                existing_team = load_show_team(selected['id'])
                
                selected_studios = st.multiselect(..., default=existing_studios)
                num_team = st.number_input(..., value=len(existing_team))
                
                # Save/Delete buttons
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("Save Changes"):
                        update_show(selected['id'], get_form_data())
                with col2:
                    if st.form_submit_button("Delete", type="secondary"):
                        if st.warning("Are you sure?"):
                            delete_show(selected['id'])
```

### Key Improvements

1. **Simplified Structure**
   - Single form instead of multiple sections
   - No expanders or Continue buttons
   - Clearer data flow

2. **Search Feature**
   - Kept outside form for immediate feedback
   - Title field mirrors search input
   - Clear similar show warnings

3. **Form Management**
   - All fields visible at once
   - Single submit and validation
   - Simpler state management

4. **Database Operations**
   - Grouped database functions together
   - Single transaction for saving
   - Clear error handling

### Migration Plan

1. **Phase 1: Basic Structure**
   - Create v2 directory
   - Set up single form structure
   - Implement search feature

2. **Phase 2: Form Fields**
   - Add all form fields
   - Keep dynamic studio/team fields
   - Set up validation

3. **Phase 3: Database**
   - Organize database functions
   - Test data integrity
   - Complete testing

### Future Considerations

1. **Edit Mode**
   - Can be added as a separate page
   - Will reuse same form structure
   - Just pre-fill the fields

2. **Delete Function**
   - Add to edit page
   - Use transactions
   - Track in audit log

3. **TMDB Integration**
   - Keep TMDB ID field

## Success Metrics
1. Code is under 500 lines
2. Form is easier to understand
3. Validation is centralized
4. Database code is organized
5. Testing is simpler
6. UX is more straightforward