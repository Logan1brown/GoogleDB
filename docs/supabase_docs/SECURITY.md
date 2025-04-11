# Database Security

## Overview

This document outlines the security model for the Google Database, including authentication, authorization, and data access controls.

## Authentication

### Supabase Auth

The database uses Supabase's built-in authentication system. Users must authenticate through one of these methods:
- Email/Password
- Google OAuth
- API Key (for service accounts)

## Authorization

### User Roles

1. **Admin**
   - Full read/write access to all tables
   - Can manage users and permissions
   - Access to audit logs

2. **Editor**
   - Can create and edit show data
   - Can manage team members
   - Cannot delete records (soft delete only)

3. **Viewer**
   - Read-only access to show data
   - Cannot modify any records

### Row Level Security (RLS)

Currently, RLS is not enabled on the tables. This means access is controlled at the role level through Supabase's permission system.

**Recommended Future Policies:**
```sql
-- Example RLS policies to be implemented
ALTER TABLE shows ENABLE ROW LEVEL SECURITY;

-- Viewers can only see active shows
CREATE POLICY "viewers_see_active_shows" ON shows
    FOR SELECT
    TO authenticated
    USING (active = true);

-- Editors can edit but not delete
CREATE POLICY "editors_can_edit" ON shows
    FOR UPDATE
    TO editor
    USING (true)
    WITH CHECK (true);

-- Only admins can delete
CREATE POLICY "admins_full_access" ON shows
    FOR ALL
    TO admin
    USING (true)
    WITH CHECK (true);
```

## Data Protection

### Soft Deletes
- All tables include an `active` boolean field
- Records are never physically deleted
- Deactivated records are hidden from normal queries
- Full history preserved in audit logs

### Timestamps
- All tables track `created_at` and `updated_at`
- Automatically maintained by triggers
- Used for audit trail and synchronization

### Search Fields
- Generated columns for case-insensitive search
- Original text preserved with original formatting
- Search fields automatically updated

## API Security

### Endpoints
- All endpoints require authentication
- Rate limiting applied to prevent abuse
- CORS configured for approved domains only

### Best Practices
1. Always use parameterized queries
2. Validate input data before insertion
3. Use appropriate user roles
4. Monitor audit logs for suspicious activity

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
