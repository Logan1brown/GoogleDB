# Database Security Architecture

## Overview

The TV Series Database uses a layered security approach with role-based access control. This document outlines the database security architecture, focusing on performance, security, and maintainability.

## Data Access Layers

### 1. Base Tables
- Normalized data storage
- Direct access restricted to admin role
- Full audit trail and history
- Examples:
  ```sql
  shows
  network_list
  studio_list
  team_members
  ```

### 2. Materialized Views
- Denormalized for performance
- Automatically refreshed
- Role-specific access
- Examples:
  ```sql
  mv_show_details      -- Denormalized show data
  mv_network_stats     -- Network performance metrics
  mv_studio_analytics  -- Studio relationship analysis
  mv_market_trends     -- Market trend calculations
  ```

### 3. Application Views
- Role-specific interfaces
- Built-in security filters
- Optimized for specific use cases

#### Dashboard Views
```sql
-- Viewer, Editor, Admin access
CREATE VIEW dashboard.show_analytics AS
  SELECT * FROM mv_show_details
  WHERE active = true;

CREATE VIEW dashboard.market_trends AS
  SELECT * FROM mv_market_trends
  WHERE active = true;
```

#### Data Entry Views
```sql
-- Editor, Admin access only
CREATE VIEW data_entry.show_management AS
  SELECT * FROM shows
  WHERE active = true;

CREATE VIEW data_entry.team_management AS
  SELECT * FROM team_members
  WHERE active = true;
```

## Role-Based Access Control

### 1. Admin Role
```sql
-- Full access to all tables
GRANT ALL ON ALL TABLES IN SCHEMA public TO admin;
GRANT ALL ON ALL TABLES IN SCHEMA dashboard TO admin;
GRANT ALL ON ALL TABLES IN SCHEMA data_entry TO admin;
```

### 2. Editor Role
```sql
-- Read access to dashboard
GRANT SELECT ON ALL TABLES IN SCHEMA dashboard TO editor;

-- Write access to data entry
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA data_entry TO editor;
```

### 3. Viewer Role
```sql
-- Read-only access to dashboard
GRANT SELECT ON ALL TABLES IN SCHEMA dashboard TO viewer;
```

## Performance Optimization

### 1. Materialized View Refresh
```sql
-- Refresh strategy for each view
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_show_details;
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_network_stats;
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_studio_analytics;
```

### 2. Access Path Optimization
- Indexes aligned with access patterns
- Partitioning for large tables
- Statistics maintenance for query planning

### 3. Caching Strategy
- Application-level caching for read-only data
- Invalidation based on data changes
- Role-specific cache policies

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
