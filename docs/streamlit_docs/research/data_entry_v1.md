# Data Entry Implementation Research

## Components to Research

### 1. Landing Page Implementation
- Research how v2 handles the landing page
- Document the flow and state management
- Note any special handling for form resets

### 2. Search and Fuzzy Logic
- Document how v2 implements show search
- Research Supabase ILIKE functionality
- Analyze fuzzy matching approach

### 3. Form State Management
- Research how v2 handles form state
- Document form clearing/reset behavior
- Note session state interactions

### 4. Integration Points
- Document how these components work together
- Note dependencies and interactions
- Identify potential issues

## Research Notes

### Landing Page (v2 Implementation)

1. Page Structure:
```python
# Main layout setup
st.set_page_config(
    page_title="Data Entry App",
    layout="wide"
)

# User authentication check
if 'user' not in st.session_state:
    login()
    return

# Load lookup data
lookups = load_lookup_data()

# Create main tabs
tab1, tab2 = st.tabs(["Add Show", "Edit/Remove Show"])
```

Key Points:
- Starts with wide layout configuration
- Checks for user authentication
- Loads lookup data before showing any forms
- Uses tabs for organization
- No form elements outside of tabs

### Search Implementation (v2)

1. Search UI:
```python
# Search section (outside form)
search_text = st.text_input("Search Shows", key="add_search")
if search_text:
    matches = search_shows(search_text)
    if matches:
        st.warning("Similar shows found: " + ", ".join(matches))
```

2. Search Logic:
```python
def search_shows(title: str) -> List[str]:
    """Search for shows with similar titles"""
    if len(title) < 3:
        return []
    
    response = supabase.table('shows').select('title').execute()
    return [s['title'] for s in response.data if title.lower() in s['title'].lower()]
```

Key Points:
- Search is placed outside the form
- Uses simple case-insensitive substring matching
- Minimum 3 characters required
- Shows results as a warning message
- Search results don't block form submission

### Form State Management (v2)

1. Form Structure:
```python
# Add form with submit button
with st.form("add_show_form"):
    # Form fields
    title = st.text_input("Title", value=search_text)
    
    # Dropdown fields
    network = st.selectbox(
        "Network",
        options=[(n['id'], n['name']) for n in lookups['networks']],
        format_func=lambda x: x[1],
        key="add_network"
    )
    
    # Submit button at bottom
    submitted = st.form_submit_button("Add Show")
```

2. Key State Management Points:
- Each form field has a unique key (e.g., "add_network")
- No explicit None/placeholder options added to dropdowns
- Uses tuples (id, name) for dropdown options
- Form fields are inside st.form() context
- Search field is outside form
- Uses index=None for selectboxes to show placeholder

3. Form Reset Behavior:
- Form automatically resets after submission
- No explicit clearing of session state needed
- Each field maintains its own state via key
- Submit button triggers form processing

4. Data Collection:
```python
if submitted:
    data = {
        'title': title,
        'network_id': network[0] if network else None,
        'genre_id': genre[0] if genre else None,
        # ...
    }
    if validate_form(data):
        save_show(data)
        st.success("Show added successfully!")
```

### Integration Analysis

1. Component Flow:
```
Landing Page
    |
    +-- Load Lookup Data (cached)
    |
    +-- Create Tabs
        |
        +-- Add Show Tab
        |   |
        |   +-- Search (outside form)
        |   |   |
        |   |   +-- Show matches if found
        |   |
        |   +-- Show Form
        |       |
        |       +-- Title (linked to search)
        |       +-- Dropdowns (with placeholders)
        |       +-- Submit -> Validate -> Save
        |
        +-- Edit Tab
            |
            +-- Show selector
            +-- Edit form
```

2. State Management:
- Session state holds lookups and form data
- Form fields use unique keys
- No manual state clearing needed
- Search state is separate from form

3. Key Interactions:
- Search text populates title field
- Form submission triggers validation
- Success message shown after save
- Dropdowns use tuples for id/name

4. Best Practices:
- Keep search outside form
- Use proper key naming
- Let Streamlit handle form resets
- Use index=None for placeholders
- Don't add custom None options

## Action Items
1. [ ] Analyze v2's landing page implementation
2. [ ] Study v2's search functionality
3. [ ] Document form state management
4. [ ] Create integration plan
