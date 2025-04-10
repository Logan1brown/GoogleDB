# TV Series Database Tasks

## Current Sprint 

### Day 1: Setup & Database 
- [x] Setup Supabase Project
    - [x] Configure auth settings
        - [x] Email auth with security settings
        - [x] GitHub OAuth integration
- [ ] Plan Database Schema
    - [x] Document schema design
        - [x] Field naming standards
        - [x] Relationship diagram
        - [x] Validation rules
    - [x] Define table structures
        - [x] Shows table structure
        - [x] Team Members table structure
        - [x] Support tables (Networks, Studios, Genres)
    - [x] Plan constraints and indexes
        - [x] Foreign key relationships
        - [x] Required fields
        - [x] Unique constraints
        - [x] Search and filter indexes

- [x] Prepare Database Schema Scripts
    - [x] Write support tables migrations
        - [x] Networks (name, type, search_name)
        - [x] Studios (name, category, search_name)
        - [x] Genres (name, search_name)
    - [x] Write main tables migrations
        - [x] Shows table
            - [x] Standard fields (title, description, status)
            - [x] Foreign keys (network_id, studio_id)
            - [x] Timestamps (created_at, updated_at)
        - [x] Show Team table (renamed from Team Members)
            - [x] Core fields (member_name, role)
            - [x] Foreign key to shows (show_title)
            - [x] Search fields (search_name)
    - [x] Document constraints and indexes
        - [x] Foreign key constraints
        - [x] Index definitions
            - [x] title and search_title
            - [x] member_name and search_name
            - [x] foreign key lookups
            - [x] network_id, studio_id (for filters)
            - [x] show_title in show_team (for joins)
    - [x] Define materialized views
        - [x] show_details view (with search fields)
        - [x] show_team_stats view (with member lists)

- [x] Execute Database Setup
    - [x] Run support tables migration
    - [x] Run lookup data migration
    - [x] Run main tables migration
    - [x] Run auth policies setup
    - [x] Verify all constraints
    - [x] Test materialized views
    - [x] Configure RLS policies

### Day 2: Data Migration
- [x] Export existing data
    - [x] Export shows data
    - [x] Export team members data
    - [x] Export lookup tables
- [x] Transform data
    - [x] Clean and normalize show titles
        - [x] Generate search_title fields
        - [x] Handle special characters
    - [x] Map network names
        - [x] Generate search_name fields
        - [x] Handle aliases
    - [x] Map studio names
        - [x] Generate search_name fields
        - [x] Handle divisions/platforms
    - [x] Map genres
        - [x] Generate search_name fields
        - [x] Split into primary/secondary
- [x] Import data
    - [x] Import lookup tables first
    - [x] Import shows data
    - [x] Import show_team data
    - [x] Import TMDB metrics data
    - [x] Verify data integrity
        - [x] Check all FKs resolve
        - [x] Validate search fields
        - [x] Test materialized views
    - [x] Setup test helper functions
        - [x] User impersonation helpers
        - [x] Test data generators
        - [x] Cleanup functions
    - [x] Policy Tests
        - [x] Test each RLS policy
        - [x] Verify allowed/denied operations
        - [x] Test different user roles
    - [x] Fuzzy Matching Tests
        - [x] Test similar titles
        - [x] Test special characters
        - [x] Test common prefixes/suffixes
    - [x] Audit Trail Tests
        - [x] Verify operation logging
        - [x] Check user attribution
        - [x] Validate JSON payloads

### Day 3: Streamlit Apps 
- [ ] Create Data Entry App
    - [ ] Setup Supabase client
    - [ ] Create login form
    - [ ] Build data entry forms with validation
    - [ ] Implement fuzzy matching for show entry
    - [ ] Implement merge logic for show updates
    - [ ] Test CRUD operations
    
- [ ] Integration Tests (BLOCKED: DB connection issues)
    - [ ] Complete workflow tests (needs DB access)
    - [ ] Trigger verification (needs DB access)
    - [ ] Constraint validation (needs DB access)

- [ ] Update Analytics Dashboard
    - [ ] Connect to Supabase
    - [ ] Implement performance optimizations
        - [ ] Add st.cache_data for query results
        - [ ] Use pagination for large datasets
        - [ ] Implement lazy loading for visualizations
        - [ ] Add loading states during data fetch
    - [ ] Port existing visualizations
        - [ ] Use materialized views for complex charts
        - [ ] Implement incremental updates
    - [ ] Add user authentication

### Day 4: Testing & Deploy 🚀

- [ ] Application Testing
    - [ ] Form Testing
        - [ ] Input validation
        - [ ] Error handling
        - [ ] Success flows
    - [ ] Authentication Testing
        - [ ] Login flows
        - [ ] Permission checks
        - [ ] Session handling
- [ ] Deploy
    - [ ] Deploy to Streamlit Cloud
    - [ ] Setup monitoring
    - [ ] Document usage




### Backlog

2. Role Analysis
   - [ ] Role distribution charts
   - [ ] Network role preferences
   - [ ] Role-based filtering

## Completed ✅



### Must Have 
- Reliable data sync with Google Sheets
- Native Plotly templates for all visualizations
- Clear separation of concerns (templates/components)
- Complete test coverage

### Should Have 
- Fast load times (<2s per view)
- No duplicate code
- Comprehensive documentation

