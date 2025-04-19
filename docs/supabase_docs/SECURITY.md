# Database Security

## Overview

This document outlines the security model for the Google Database, including authentication, authorization, and data access controls.

## Authentication

### Architecture

The application consists of two separate components with distinct authentication needs:

1. **Dashboard Application**
   - Primary focus on data visualization and analysis
   - Read-only access for most users
   - Requires viewer or editor role

2. **Data Entry Application**
   - Focused on data management and updates
   - Write access required
   - Requires editor or admin role

### Authentication Implementation

Both applications use Supabase authentication with intentionally separate session states:

1. **Shared Authentication Logic**
   ```python
   # Shared auth utilities (src/shared/auth.py)
   def login(email: str, password: str) -> bool:
       auth = supabase.auth.sign_in_with_password({...})
       return auth.session

   def auth_required(func):
       @wraps(func)
       def wrapper(*args, **kwargs):
           if not check_auth():
               show_login()
           return func(*args, **kwargs)
       return wrapper
   ```

2. **Separate Session States**
   - Each application maintains its own session state
   - Prevents session conflicts
   - Allows for app-specific auth requirements

3. **Security Measures**
   - HTTPS-only cookies
   - Secure token storage
   - Rate limiting on auth endpoints
   - Session timeout after inactivity
   - Audit logging of auth events

## Authorization

### User Roles

1. **Admin**
   - Full access to all functionality
   - Can manage users and permissions
   - Access to audit logs and system settings
   - Can perform permanent deletions
   - Access to both dashboard and data entry

2. **Editor**
   - Full access to data entry application
   - Can create and modify show records
   - Can manage team and studio relationships
   - Cannot permanently delete records (soft delete only)
   - Read access to dashboard analytics

3. **Viewer**
   - Read-only access to dashboard
   - Can view all analytics and reports
   - Cannot access data entry application
   - Cannot modify any records

### Row Level Security (RLS)

RLS is enabled on all tables with fine-grained access control:

1. **Read Access**
   ```sql
   -- Reference data accessible to all authenticated users
   CREATE POLICY "lookup_data_read_access" 
       ON lookup_tables FOR SELECT 
       USING (auth.role() IN ('viewer', 'editor', 'admin'));

   -- Show data accessible to all authenticated users
   CREATE POLICY "show_data_read_access" 
       ON shows FOR SELECT 
       USING (auth.role() IN ('viewer', 'editor', 'admin'));

   -- Analytics views accessible to all authenticated users
   CREATE POLICY "analytics_read_access" 
       ON analytics_views FOR SELECT 
       USING (auth.role() IN ('viewer', 'editor', 'admin'));
   ```

2. **Write Access**
   ```sql
   -- Editors can insert and update shows
   CREATE POLICY "editor_show_write_access" 
       ON shows 
       FOR INSERT UPDATE
       USING (auth.role() IN ('editor', 'admin'))
       WITH CHECK (auth.role() IN ('editor', 'admin'));

   -- Only admins can delete shows
   CREATE POLICY "admin_show_delete_access" 
       ON shows 
       FOR DELETE 
       USING (auth.role() = 'admin');

   -- Editors can manage team relationships
   CREATE POLICY "editor_team_write_access" 
       ON show_team_members 
       FOR ALL
       USING (auth.role() IN ('editor', 'admin'))
       WITH CHECK (auth.role() IN ('editor', 'admin'));
   ```

3. **Special Policies**
   ```sql
   -- User metadata access
   CREATE POLICY "user_metadata_access" 
       ON user_metadata 
       FOR SELECT UPDATE
       USING (auth.uid() = user_id);

   -- Audit log access (admin only)
   CREATE POLICY "audit_log_access" 
       ON audit_logs 
       FOR SELECT
       USING (auth.role() = 'admin');

   -- Success metrics write protection
   CREATE POLICY "success_metrics_protection" 
       ON success_metrics 
       FOR INSERT UPDATE DELETE
       USING (auth.role() = 'admin')
       WITH CHECK (auth.role() = 'admin');
   ```
```

## Data Protection

### Soft Deletes
- All tables include an `active` boolean field
- Records are never physically deleted by application code
- Only admins can perform permanent deletions through special procedures
- Deactivated records hidden from normal queries but preserved in audit logs
- Automatic filtering using `active = true` in views and queries

### Audit Trail
- All tables track `created_at`, `updated_at`, `created_by`, `updated_by`
- Automatically maintained by triggers
- Comprehensive audit logs for all data modifications
- Special audit tables for sensitive operations
- Audit data accessible only to admins

### Data Validation
- Input validation at application and database levels
- Strict type checking and constraints
- Business rule enforcement through triggers
- Automated data quality checks

## API Security

### Role-Specific Endpoints

1. **Dashboard API**
   - Read-only endpoints for analytics and reports
   - Accessible to all authenticated users
   - Rate limited based on role
   - Cached responses for performance

2. **Data Entry API**
   - Write endpoints for data management
   - Limited to editor and admin roles
   - Stricter rate limits and validation
   - Audit logging of all operations

3. **Admin API**
   - System management endpoints
   - Admin role only
   - IP whitelist restrictions
   - Enhanced audit logging

### Security Controls
1. Request validation
   - Input sanitization
   - Schema validation
   - Business rule checking
   - Rate limiting

2. Response security
   - Data filtering by role
   - No sensitive data in responses
   - Proper error handling
   - Response size limits

3. Monitoring
   - Real-time security alerts
   - Access pattern analysis
   - Rate limit monitoring
   - Audit log review

## Monitoring

### Audit Trail
- All changes tracked in `audit` schema
- Captures old and new values
- Records user, timestamp, and action
- Queryable for security review

### Alerts
- Failed login attempts
- Unusual data access patterns
- Mass updates or deletions
- API rate limit violations
