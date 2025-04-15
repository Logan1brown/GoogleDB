# Database Audit System

## Overview

The Google Database includes comprehensive audit tracking in a separate `audit` schema, capturing all data changes for security and compliance. All changes to the database are automatically logged in a centralized audit table.

## Audit Schema

### Table Structure

The audit system uses a single table `audit.logs` with the following structure:

```sql
                                          Table "audit.logs"
   Column   |           Type           | Collation | Nullable |                Default                 
------------+--------------------------+-----------+----------+----------------------------------------
 id         | bigint                   |           | not null | nextval('audit.logs_id_seq'::regclass)
 table_name | text                     |           | not null | 
 operation  | text                     |           | not null | 
 old_data   | jsonb                    |           |          | 
 new_data   | jsonb                    |           |          | 
 changed_by | text                     |           |          | 
 created_at | timestamp with time zone |           |          | now()
```

### Key Fields

- `id`: Unique audit entry ID
- `table_name`: Name of the modified table (e.g., 'shows', 'show_team')
- `operation`: Type of change ('INSERT', 'UPDATE', or 'DELETE')
- `old_data`: JSON containing previous values (for UPDATE/DELETE)
- `new_data`: JSON containing new values (for INSERT/UPDATE)
- `changed_by`: User who made the change
- `created_at`: Timestamp when the change occurred

## Querying History

### Recent Changes
```sql
-- Get most recent changes across all tables
SELECT created_at, changed_by, operation, table_name, 
       old_data, new_data
FROM audit.logs 
ORDER BY created_at DESC
LIMIT 10;
```

### Show History
```sql
-- View changes to a specific show
SELECT created_at, changed_by, operation,
       old_data->>'title' as old_title,
       new_data->>'title' as new_title
FROM audit.logs
WHERE table_name = 'shows'
  AND (old_data->>'id' = $1 OR new_data->>'id' = $1)
ORDER BY created_at DESC;
```

### Team Changes
```sql
-- Track team member changes for a show
SELECT created_at, changed_by, operation,
       old_data->>'name' as old_name,
       new_data->>'name' as new_name,
       old_data->>'role_type_id' as old_role,
       new_data->>'role_type_id' as new_role
FROM audit.logs
WHERE table_name = 'show_team'
  AND (old_data->>'show_id' = $1 OR new_data->>'show_id' = $1)
ORDER BY created_at DESC;
```

## Retention Policy

1. **Active Records**
   - Full history maintained
   - No automatic pruning
   - Queryable through views

2. **Inactive Records**
   - History preserved for 7 years
   - Archived to cold storage
   - Available through archive queries

## Security

### Access Control
- Only admins can query audit tables
- Read-only access enforced
- No manual modifications allowed

### Monitoring
- Large-scale changes flagged
- Unusual patterns reported
- Regular audit reviews

## Best Practices

1. **Querying**
   - Use provided views when possible
   - Include date ranges for performance
   - Index on frequently queried fields

2. **Analysis**
   - Regular review of changes
   - Track modification patterns
   - Monitor user activity

3. **Maintenance**
   - Monthly integrity checks
   - Verify trigger operation
   - Update statistics regularly

## Common Queries

### By Time Period
```sql
-- Find changes in a date range
SELECT created_at, changed_by, operation, table_name
FROM audit.logs
WHERE created_at BETWEEN $1 AND $2
ORDER BY created_at DESC;
```

### By User
```sql
-- Find all changes by a specific user
SELECT created_at, operation, table_name, 
       old_data, new_data
FROM audit.logs
WHERE changed_by = $1
ORDER BY created_at DESC;
```

### By Operation Type
```sql
-- Find all deletions
SELECT created_at, changed_by, table_name, old_data
FROM audit.logs
WHERE operation = 'DELETE'
ORDER BY created_at DESC;
```

### Data Analysis
```sql
-- Get operation counts by table
SELECT table_name, operation, COUNT(*) as count
FROM audit.logs
GROUP BY table_name, operation
ORDER BY table_name, count DESC;
```
