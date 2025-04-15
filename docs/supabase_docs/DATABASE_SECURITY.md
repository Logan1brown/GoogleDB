# Database Security Architecture

## Overview

The Market Analyzer application uses a layered security approach to protect data while maintaining performance through materialized views. This document outlines the security architecture and access patterns.

## Data Access Layers

### 1. Materialized Views (Base Layer)
- `show_details`: Denormalized show data
- `network_stats`: Network performance metrics
- `team_summary`: Team member aggregations
- Access: Restricted to `service_role` and `postgres` only
- Purpose: High-performance data storage and computation

### 2. Security Definer Functions (Security Layer)
```sql
get_show_details()
get_network_stats()
get_team_summary()
```
- Run with elevated privileges (as function owner)
- Provide controlled access to materialized views
- Enable secure data access without exposing base tables

### 3. API Views (Access Layer)
- `api_show_details`: Public interface for show data
- `api_network_stats`: Public interface for network statistics
- `api_team_summary`: Public interface for team data
- `api_market_analysis`: Combined market analysis view
- Access: Available to `anon` and `authenticated` roles
- Purpose: Provide secure, read-only access to application data

## Role-Based Access Control

### Service Role
- Full access to materialized views
- Used for backend operations and data updates
- Never exposed to frontend code
- Environment Variable: `SUPABASE_SERVICE_KEY`

### Anonymous Role
- Read-only access to API views
- Used for frontend applications
- Safe to expose in client-side code
- Environment Variable: `SUPABASE_ANON_KEY`

## Security Best Practices

1. **Frontend Code**
   ```python
   # Always use anon key in frontend
   supabase = create_client(
       os.getenv('SUPABASE_URL'),
       os.getenv('SUPABASE_ANON_KEY')
   )
   ```

2. **Backend Operations**
   ```python
   # Use service key for admin operations only
   supabase = create_client(
       os.getenv('SUPABASE_URL'),
       os.getenv('SUPABASE_SERVICE_KEY')
   )
   ```

3. **View Access**
   - Always access data through API views in frontend code
   - Never attempt to access materialized views directly
   - Use the appropriate key for your context

## Implementation Details

### Security Definer Functions
```sql
CREATE OR REPLACE FUNCTION get_show_details()
RETURNS SETOF show_details
LANGUAGE sql
SECURITY DEFINER
AS $$
    SELECT * FROM show_details;
$$;
```

### API Views
```sql
CREATE OR REPLACE VIEW api_show_details AS 
SELECT * FROM get_show_details();

CREATE OR REPLACE VIEW api_market_analysis AS
WITH show_base AS (
    SELECT 
        tmdb_id,
        title as shows,
        network_name as network,
        studio_names[1] as studio,
        -- ... other fields
    FROM get_show_details()
)
SELECT 
    s.*,
    t.writers,
    t.producers,
    t.directors,
    t.creators
FROM show_base s
LEFT JOIN get_team_summary() t ON t.show_title = s.shows;
```

## Maintaining Security

1. **Regular Audits**
   - Review function permissions
   - Check view access grants
   - Verify role assignments

2. **Development Guidelines**
   - Always use the least privileged role needed
   - Document any new security-related changes
   - Test both anon and service role access paths

3. **Deployment Checklist**
   - Verify all API views are accessible
   - Confirm materialized views are protected
   - Test frontend with anon key only
