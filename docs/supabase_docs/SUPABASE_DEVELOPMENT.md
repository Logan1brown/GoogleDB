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
