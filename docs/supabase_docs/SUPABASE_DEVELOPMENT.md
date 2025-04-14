# Supabase Development Guide

# Table of Contents
1. [Connection](#1-connection)
2. [Python Client](#2-python-client)
3. [Security](#3-security)
4. [Testing](#4-testing)
5. [Data Verification](#5-data-verification)

# 1. Connection

### 1. Session Mode (Recommended for Local Development)
```python
# .env
DATABASE_URL=postgres://postgres.[project_ref]:[password]@aws-0-us-west-1.pooler.supabase.com:5432/postgres
```
- Uses Supavisor pooler
- Best for IPv6 issues
- Maintains persistent connections
- Good for development and testing

### 2. Transaction Mode
```python
# .env
DATABASE_URL=postgres://postgres.[project_ref]:[password]@aws-0-us-west-1.pooler.supabase.com:6543/postgres
```
- Uses connection pooling
- Best for serverless/edge functions
- Doesn't support prepared statements
- Good for high-concurrency, short-lived connections

### 3. Direct Connection
```python
# .env
DATABASE_URL=postgresql://postgres:[password]@db.[project_ref].supabase.co:5432/postgres
```
- Direct to Postgres
- Requires IPv6 support
- Best for persistent servers
- No connection pooling

# 2. Python Client

### Basic Connection
```python
from supabase import create_client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize client
supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_KEY')  # Use service key for admin access
)
```

### Query Examples

1. Basic Select
```python
response = supabase.table('shows').select('*').limit(1).execute()
```

2. Joins and Foreign Keys
```python
# Join with network_list table
response = supabase.table('shows')\
    .select('title, network_list!inner(name)')\
    .limit(3)\
    .execute()
```

3. Filters and Sorting
```python
response = supabase.table('shows')\
    .select('title, network_list(name)')\
    .filter('title', 'ilike', '%the%')\
    .order('title')\
    .limit(3)\
    .execute()
```

## Troubleshooting

1. Connection Issues:
   - Try Session Mode first (port 5432 with Supavisor)
   - Check if environment supports IPv6
   - Verify correct project reference and credentials

2. Query Issues:
   - Verify table and column names
   - Use `!inner` for inner joins
   - Check foreign key relationships exist

# 3. Security

1. Environment Variables:
   - Store all credentials in .env
   - Use service key for admin operations
   - Use anon key for public operations

2. Connection Management:
   - Reuse client instances
   - Use appropriate connection mode for use case
   - Monitor connection pool usage

3. Security:
   - Never commit credentials
   - Use Row Level Security (RLS)
   - Implement proper role-based access

# 4. Testing

### User Management
```python
# Create a test user with a role
user = TestUser(role='admin')
user_id = user.create()

# User will be automatically cleaned up
with TestUser(role='editor') as user:
    # Run tests with user...
    pass
```

### Test Data Generation
```python
# Generate and insert test shows
test_shows = [
    generate_test_show(title='Test Show 1', network_id=15),
    generate_test_show(title='Test Show 2', network_id=1)
]

# Data will be automatically cleaned up
with TemporaryTestData('shows', test_shows, {'titles': ['Test Show 1', 'Test Show 2']}) as shows:
    # Run tests with shows...
    pass
```

### Foreign Key Handling
Test helpers handle cascading deletes in the correct order:
1. `show_team` references `shows.title`
2. `tmdb_success_metrics` references `shows.tmdb_id`

## 4.2 Authentication & Authorization

### User Roles
- **admin**: Full access to all operations
- **editor**: Can create/edit shows and team data
- **viewer**: Read-only access to shows and metrics
- **authenticated**: Basic authenticated user

### Row Level Security (RLS) Policies

1. Shows Table
```sql
-- Anyone can read active shows
CREATE POLICY "Shows are viewable by everyone" ON shows
    FOR SELECT USING (active = true);

-- Editors and admins can insert/update
CREATE POLICY "Editors can create shows" ON shows
    FOR INSERT TO editor, admin
    WITH CHECK (true);
```

2. Show Team Table
```sql
-- Viewers+ can read team data
CREATE POLICY "Team data viewable by authenticated users" ON show_team
    FOR SELECT TO authenticated
    USING (true);

-- Editors+ can modify team data
CREATE POLICY "Editors can modify team data" ON show_team
    FOR ALL TO editor, admin
    USING (true);
```

3. TMDB Metrics Table
```sql
-- Viewers+ can read metrics
CREATE POLICY "Metrics viewable by authenticated users" ON tmdb_success_metrics
    FOR SELECT TO authenticated
    USING (true);

-- Only admins can modify metrics
CREATE POLICY "Only admins can modify metrics" ON tmdb_success_metrics
    FOR ALL TO admin
    USING (true);
```

# 5. Data Verification

## 5.1 Show Data Verification
Use this query to verify that shows and their related data are being saved correctly:

```sql
WITH recent_shows AS (
    SELECT * FROM shows 
    WHERE created_at > NOW() - INTERVAL '24 hours'
    ORDER BY created_at DESC
)
SELECT 
    -- Basic Info
    s.id,
    s.title,
    s.created_at,
    s.description,
    s.date as announcement_date,
    s.episode_count,
    
    -- Foreign Key Relationships
    n.network as network_name,
    g.genre as genre_name,
    sg.genre as subgenre_name,
    src.type as source_type,
    ord.type as order_type,
    st.status as status_name,
    
    -- Arrays and Complex Types
    array_agg(DISTINCT stud.studio) as studios,
    array_agg(DISTINCT st_mem.name || ' (' || rt.role || ')') as team_members,
    s.subgenres as subgenre_ids,
    
    -- TMDB Info
    s.tmdb_id,
    CASE 
        WHEN tm.id IS NOT NULL THEN 'Yes'
        ELSE 'No'
    END as has_tmdb_metrics,
    
    -- TMDB Metrics (if available)
    tm.seasons,
    tm.total_episodes as tmdb_total_episodes,
    tm.status as tmdb_status,
    tm.last_air_date
    
FROM recent_shows s
LEFT JOIN network_list n ON s.network_id = n.id
LEFT JOIN genre_list g ON s.genre_id = g.id
LEFT JOIN genre_list sg ON sg.id = ANY(s.subgenres)
LEFT JOIN source_types src ON s.source_type_id = src.id
LEFT JOIN order_types ord ON s.order_type_id = ord.id
LEFT JOIN status_types st ON s.status_id = st.id
LEFT JOIN show_team st_mem ON s.id = st_mem.show_id
LEFT JOIN role_types rt ON st_mem.role_type_id = rt.id
LEFT JOIN studio_list stud ON stud.id = ANY(s.studios)
LEFT JOIN tmdb_success_metrics tm ON s.tmdb_id = tm.tmdb_id
GROUP BY 
    s.id, s.title, s.created_at, s.description, s.date,
    s.episode_count, n.network, g.genre, sg.genre,
    src.type, ord.type, st.status, s.subgenres,
    s.tmdb_id, tm.id, tm.seasons, tm.total_episodes,
    tm.status, tm.last_air_date
ORDER BY s.created_at DESC;
```

This query checks:
1. Basic show information
2. All foreign key relationships (network, genre, etc.)
3. Array fields (studios, subgenres)
4. Team members and their roles
5. TMDB data and metrics

# 6. Streamlit Form Best Practices

## 6.1 Form State Management

### Landing Page Pattern
For multi-step forms, use a landing page pattern to properly initialize state:
```python
if not st.session_state.get('show_form_loaded', False):
    with st.form('landing_form'):
        st.markdown('Click Start to begin adding a show')
        st.form_submit_button('Start', on_click=handle_start)
else:
    show_form = st.form('show_details_form')
    # Form fields here...
```

### Form Initialization
Handle form initialization in a callback to ensure clean state:
```python
def handle_start():
    st.session_state.show_form_loaded = True
    # Clear any existing form values
    for key in ['show_network', 'show_genre', 'show_title']:
        if key in st.session_state:
            del st.session_state[key]
```

## 6.2 Dropdown Best Practices

### Default State
To show proper placeholders in selectboxes:
```python
st.selectbox(
    'Network',
    options=network_options,
    format_func=lambda x: x['name'],
    key='show_network',
    index=None  # This shows 'Choose an option' placeholder
)
```

### Form Submission
Use callbacks for form submission to ensure proper state updates:
```python
def handle_save():
    if errors:
        show_form.error('\n'.join(errors))
    else:
        # Update state
        state['form']['show_form']['title'] = st.session_state.show_title
        # Show success message INSIDE the form
        show_form.success('Show details saved!')

# In the form
show_form.form_submit_button('Save', on_click=handle_save)
```

## 6.3 Common Pitfalls

1. **Form Messages**: Always show messages (success/error) inside the form context:
   ```python
   # ❌ Don't do this:
   st.success('Saved!')  # Shows at top of page
   
   # ✅ Do this:
   show_form.success('Saved!')  # Shows in form
   ```

2. **State Updates**: Don't check button values directly, use callbacks:
   ```python
   # ❌ Don't do this:
   if show_form.form_submit_button('Save'):
       update_state()
   
   # ✅ Do this:
   show_form.form_submit_button('Save', on_click=handle_save)
   ```

3. **Form Reset**: Don't use `st.rerun()` in callbacks:
   ```python
   # ❌ Don't do this:
   def handle_save():
       update_state()
       st.rerun()  # Streamlit handles this automatically
   
   # ✅ Do this:
   def handle_save():
       update_state()  # Streamlit will rerun after callback
   ```

4. **Message Timing**: Don't use `time.sleep()` for messages:
   ```python
   # ❌ Don't do this:
   show_form.success('Saved!')
   time.sleep(1.5)  # Blocks unnecessarily
   
   # ✅ Do this:
   show_form.success('Saved!')  # Streamlit handles timing
   ```

## 6.4 Form Components

### Allowed Inside Forms
```python
# ✅ These work in forms:
show_form.text_input('Title')
show_form.selectbox('Network', options)
show_form.number_input('Episodes')
show_form.text_area('Description')
show_form.date_input('Date')
show_form.radio('Type', options)
show_form.checkbox('Active')
show_form.form_submit_button('Save')
show_form.success('Saved!')  # Form messages
```

### Not Allowed Inside Forms
```python
# ❌ These don't work in forms:
st.button('Click')  # Use form_submit_button instead
st.download_button('Download')  # Must be outside form
st.file_uploader('Upload')  # Must be outside form
st.multiselect('Select')  # Must be outside form
st.tabs(['Tab1'])  # Must be outside form
st.expander('More')  # Must be outside form
```

### Form Layout Best Practices
```python
# ✅ Do this: Put form-specific inputs in the form
with st.form('show_form'):
    show_form.text_input('Title')
    show_form.selectbox('Network', options)
    show_form.form_submit_button('Save')

# ✅ Do this: Put shared/persistent elements outside
st.multiselect('Team Members', options)  # Used across forms
st.file_uploader('Attachments')  # Files persist across submissions

# ❌ Don't do this: Mix form/non-form elements
with st.form('bad_form'):
    show_form.text_input('Title')
    st.multiselect('Team')  # Won't submit with form!
    show_form.form_submit_button('Save')
```
