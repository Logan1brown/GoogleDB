# TV Series Database Tasks

## Current Sprint 

- [ ] Update Analytics Dashboard
    - [x] Connect to Supabase
    - [x] Implement performance optimizations
        - [x] Add st.cache_data for query results
        - [x] Use pagination for large datasets
        - [ ] Implement lazy loading for visualizations
        - [ ] Add loading states during data fetch
    - [ ] Port existing visualizations
        - [x] Use materialized views for complex charts
        - [ ] Implement incremental updates
    - [ ] Add user authentication (moved to deployment phase)

### Day 4: Database Optimization & View Updates

- [ ] Authentication Implementation
    - [ ] Supabase Auth Integration
        - [ ] Set up auth client in Streamlit
        - [ ] Add login/signup forms
        - [ ] Implement session management
        - [ ] Add role-based access control
    - [ ] Auth UI Components
        - [ ] Create login page
        - [ ] Add user profile page
        - [ ] Implement password reset
        - [ ] Add OAuth providers (if needed)
    - [ ] Testing & Security
        - [ ] Test auth flows
        - [ ] Verify RLS policies
        - [ ] Test role permissions
        - [ ] Security review

- [ ] Frontend View Updates
    - [ ] Update Data Processing Layer
        - [ ] Modify analyze_shows.py to use materialized views
        - [ ] Update market_analyzer.py for new column names
        - [ ] Test data processing changes
    - [ ] Update Components
        - [ ] Update market_view.py
            - [ ] Use new column names (network_name, genre_name)
            - [ ] Update team member handling
            - [ ] Test filtering and aggregations
        - [ ] Update other affected components
            - [ ] genre_view.py
            - [ ] studio_view.py
            - [ ] unified_view.py
    - [ ] Test View Integration
        - [ ] Test all filters
        - [ ] Verify data accuracy
        - [ ] Check performance

### Day 5: Testing & Deployment 🚀

- [ ] Application Testing
    - [ ] Form Testing
        - [ ] Input validation
        - [ ] Error handling
        - [ ] Success flows
    - [ ] Integration Testing
        - [ ] Test all database operations
        - [ ] Verify materialized view updates
        - [ ] Load testing with sample data

- [ ] Deployment Preparation
    - [ ] Supabase Backend
        - [ ] Set up materialized view refresh schedule
        - [ ] Configure backup schedule
        - [ ] Review and optimize RLS policies
        - [ ] Document connection strings and API keys

    - [ ] Streamlit Frontend
        - [ ] Create/update requirements.txt
        - [ ] Document environment variables
        - [ ] Create deployment guide
        - [ ] Set up error monitoring

- [ ] Deploy to Production
    - [ ] Deploy to Streamlit Cloud
        - [ ] Connect GitHub repository
        - [ ] Configure environment variables
        - [ ] Set up custom domain (if needed)
    - [ ] Post-Deployment
        - [ ] Verify all features
        - [ ] Monitor performance
        - [ ] Document deployment URLs
        - [ ] Create user guide
    - [ ] Setup monitoring
    - [ ] Document usage




### Backlog

### Database Improvements
- Add soft delete support for show_team table
  - Add `active` column (boolean, default true)
  - Update queries to filter by active=true
  - Update UI to only show active roles
  - Add audit trail for role changes

### Database Optimization
- [ ] Implement automated materialized view refresh strategy
  - [ ] Evaluate pg_cron vs external scheduler
  - [ ] Set up monitoring for refresh performance
  - [ ] Implement retry mechanism for failed refreshes
  - [ ] Document refresh strategy and monitoring


2. Role Analysis
   - [ ] Role distribution charts
   - [ ] Network role preferences
   - [ ] Role-based filtering

## Completed ✅

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
        - [x] Document audit log queries
        - [x] Update AUDIT.md with correct table structure

### Day 3: Streamlit Apps 
- [x] Create Data Entry App
    - [x] Setup Supabase client
    - [x] Create login form
    - [x] Build data entry forms with validation
    - [x] Implement fuzzy matching for show entry
    - [x] Implement merge logic for show updates
    - [x] Test CRUD operations
    
- [x] Integration Tests
    - [x] Complete workflow tests
    - [x] Trigger verification
    - [x] Constraint validation

    - [x] Database Optimization
    - [x] Add foreign key constraints
        - [x] network_id → network_list(id)
        - [x] genre_id → genre_list(id)
        - [x] status_id → status_types(id)
    - [x] Create materialized views
        - [x] show_details view
        - [x] network_stats view
        - [x] team_summary view
    - [x] Update analytics service
        - [x] Use materialized views
        - [x] Update column names
        - [x] Test changes
    - [x] Update documentation
        - [x] Document foreign keys
        - [x] Document materialized views
        - [x] Document refresh process

### Must Have 
- Reliable data sync with Google Sheets
- Native Plotly templates for all visualizations
- Clear separation of concerns (templates/components)
- Complete test coverage

### Should Have 
- Fast load times (<2s per view)
- No duplicate code
- Comprehensive documentation

