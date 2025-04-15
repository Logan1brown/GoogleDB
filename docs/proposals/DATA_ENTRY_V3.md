# Data Entry App V3 Proposal

## Current State
1. Have working Add Show functionality with proper state management (ShowFormState/DataEntryState)
2. Have improved search functionality using streamlit_searchbox and fuzzy matching
3. Have better UI with consistent button styling
4. Need to handle multiple operations (Add/Edit/Remove) cleanly

## Issues to Address
1. Each operation needs its own flow but should share common components
2. State management needs to handle operation-specific states
3. Form components need to adapt based on operation (editable vs read-only)
4. Search functionality needs to be consistent across operations

## Proposed Solution

### State Management
```python
@dataclass
class DataEntryState:
    operation: str  # "Add Show", "Edit Show", "Remove Show"
    form_started: bool  # Past landing page?
    show_form: ShowFormState  # Form data
    read_only: bool  # For Remove operation
    search_results: List[str]  # Search results
```

### Operation-Specific Flows

#### Add Show
1. Landing page:
   - Fuzzy search to check for duplicates
   - "Add New Show" button
2. Form:
   - All fields empty and editable
   - Submit creates new show

#### Edit Show
1. Landing page:
   - Search with dropdown of existing shows
   - "Edit Selected" button
2. Form:
   - Fields populated with existing data
   - All fields editable
   - Submit updates show

#### Remove Show
1. Landing page:
   - Search with dropdown of existing shows
   - "Review Selected" button
2. Form:
   - Fields populated with existing data
   - All fields read-only
   - "Delete Show" button on review tab

### Code Organization
```python
# 1. State Management
def initialize_session_state():
    if "form" not in st.session_state:
        st.session_state.form = DataEntryState()

# 2. Landing Pages
def render_landing_page(operation):
    if operation == "Add Show":
        render_add_show_landing()
    elif operation == "Edit Show":
        render_edit_show_landing()
    else:
        render_remove_show_landing()

# 3. Form Components
def render_form_field(field_name, value, readonly=False):
    """Render a form field with appropriate behavior"""
    if readonly:
        st.write(f"{field_name}: {value}")
    else:
        st.text_input(field_name, value=value)

# 4. Form Tabs
def render_tabs(operation, show_data):
    tabs = st.tabs(["Show Details", "Studios", "Team Members", "Review"])
    readonly = (operation == "Remove Show")
    
    with tabs[0]:
        render_show_details(show_data, readonly)
    with tabs[1]:
        render_studios(show_data, readonly)
    # etc...
```

### Implementation Plan
1. Start with working Add Show as foundation
2. Add operation-specific state management
3. Implement landing pages for each operation
4. Make form components adapt to operation
5. Add Edit/Remove functionality
6. Port over search improvements
7. Apply consistent UI styling
