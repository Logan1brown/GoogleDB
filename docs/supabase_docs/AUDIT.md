# Database Audit System

## Overview

The Google Database includes comprehensive audit tracking in a separate `audit` schema, capturing all data changes for security and compliance.

## Audit Schema

### Tables

1. **audit.shows_log**
   - Tracks changes to the shows table
   - Records old and new values
   - Maintains complete history

2. **audit.show_team_log**
   - Captures team member changes
   - Important for tracking role changes
   - Links to original show records

### Common Fields

All audit tables include:
- `id`: Unique audit entry ID
- `table_name`: Source table
- `action`: INSERT, UPDATE, or DELETE
- `old_data`: JSON of previous values
- `new_data`: JSON of new values
- `changed_by`: User who made the change
- `changed_at`: Timestamp of change
- `client_info`: Application context

## Querying History

### Show History
```sql
SELECT 
    changed_at,
    changed_by,
    old_data->>'title' as old_title,
    new_data->>'title' as new_title,
    action
FROM audit.shows_log
WHERE new_data->>'id' = $1
ORDER BY changed_at DESC;
```

### Team Changes
```sql
SELECT 
    changed_at,
    changed_by,
    old_data->>'name' as old_name,
    new_data->>'name' as new_name,
    old_data->>'role_type_id' as old_role,
    new_data->>'role_type_id' as new_role
FROM audit.show_team_log
WHERE new_data->>'show_id' = $1
ORDER BY changed_at DESC;
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

## Reports

### Standard Reports
1. Daily modification summary
2. Weekly user activity
3. Monthly data quality check
4. Quarterly security review

### Custom Queries
```sql
-- Example: Find all changes by user in date range
SELECT 
    table_name,
    action,
    changed_at,
    changed_by
FROM audit.log_view
WHERE changed_by = $1
AND changed_at BETWEEN $2 AND $3
ORDER BY changed_at DESC;
```
