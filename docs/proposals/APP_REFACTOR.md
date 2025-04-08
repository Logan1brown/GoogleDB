# App Refactoring Plan

## Schema Changes

### 1. Column Name Standardization

We've standardized the TV show title column names across all tables to use `title`:

Before:
- Shows sheet: `shows` column
- Show_team sheet: `show_name` column 
- TMDB_success_metrics: `Title` column

After:
- All tables now use: `title` column

This requires updates to:
- [ ] Database queries
- [ ] API endpoints
- [ ] Frontend components that reference these columns
- [ ] Data import/export scripts

### 2. Show Team Multiple Roles

The show_team table now uses a normalized design where each role a person has on a show gets its own row. This requires significant changes to the app's data handling and UI.

### 1. Database Changes
- ✅ One row per (show, person, role) combination
- ✅ Unique constraint on (title, name, role_type_id)
- ✅ Foreign key to role_types table
- ✅ Normalized role names

### 2. API Layer Updates

#### Queries to Update
- [ ] Get person details:
  ```sql
  SELECT 
    st.title,
    st.name,
    array_agg(rt.name) as roles,
    st.team_order,
    st.notes
  FROM show_team st
  JOIN role_types rt ON st.role_type_id = rt.id
  WHERE st.name = $1
  GROUP BY st.title, st.name, st.team_order, st.notes;
  ```

- [ ] Search people:
  ```sql
  SELECT DISTINCT ON (st.name)
    st.name,
    array_agg(rt.name) as roles,
    array_agg(st.title) as shows
  FROM show_team st
  JOIN role_types rt ON st.role_type_id = rt.id
  WHERE st.search_name ILIKE $1
  GROUP BY st.name;
  ```

- [ ] Get show team:
  ```sql
  SELECT 
    st.name,
    array_agg(rt.name) as roles,
    st.team_order,
    st.notes
  FROM show_team st
  JOIN role_types rt ON st.role_type_id = rt.id
  WHERE st.title = $1
  GROUP BY st.name, st.team_order, st.notes
  ORDER BY st.team_order NULLS LAST, st.name;
  ```

#### Mutations to Update
- [ ] Add person to show:
  ```sql
  INSERT INTO show_team (title, name, role_type_id, team_order, notes)
  SELECT $1, $2, rt.id, $4, $5
  FROM unnest($3::text[]) role
  JOIN role_types rt ON rt.name = role;
  ```

- [ ] Update person's roles:
  ```sql
  -- Delete existing roles
  DELETE FROM show_team
  WHERE title = $1 AND name = $2;
  
  -- Insert new roles
  INSERT INTO show_team (title, name, role_type_id, team_order, notes)
  SELECT $1, $2, rt.id, $4, $5
  FROM unnest($3::text[]) role
  JOIN role_types rt ON rt.name = role;
  ```

### 3. Frontend Updates

#### Components to Update
- [ ] PersonDetails
  - Show aggregated roles per show
  - Handle multiple show_team entries
  - Update role editing UI

- [ ] ShowTeam
  - Group team members by name
  - Show all roles for each person
  - Update role filters

- [ ] SearchResults
  - Deduplicate people
  - Show all roles and shows
  - Update sorting/filtering

- [ ] Forms
  - Update role selection to handle multiple roles
  - Validate role combinations
  - Handle batch updates

### 4. Testing Updates
- [ ] Update test fixtures for new schema
- [ ] Add tests for multiple roles
- [ ] Test role aggregation
- [ ] Test search deduplication
- [ ] Test batch operations

### 5. Migration Steps
1. [ ] Deploy schema changes
2. [ ] Update API layer
3. [ ] Test new queries
4. [ ] Update frontend components
5. [ ] Test UI changes
6. [ ] Deploy app updates
7. [ ] Monitor for issues

### 6. Performance Considerations
- Add indexes for common queries
- Monitor query performance with role aggregation
- Cache aggregated results where possible
- Use materialized views for complex queries if needed

### 7. Future Improvements
- Add role categories/types
- Implement role-based permissions
- Add role validation rules
- Improve role suggestion system
