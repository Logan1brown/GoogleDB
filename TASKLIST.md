# TV Series Database Tasks

## Current Sprint 

### Phase 1: Basic Auth (1 day)
- [ ] Initial Setup
    - [ ] Set up auth client in Streamlit
    - [ ] Add login form (username/password)
    - [ ] Basic session handling
    - [ ] Simple read-only RLS

### Phase 2: Testing & Fixes (2-4 days)
- [ ] Smoke Testing
    - [ ] Can users log in?
    - [ ] Do charts load with auth?
    - [ ] Is data properly filtered?

- [ ] Fix Issues Found
    - [ ] Auth flow problems
    - [ ] Data access issues
    - [ ] Performance bottlenecks

- [ ] Add Missing Features
    - [ ] Error messages
    - [ ] Session timeout
    - [ ] User feedback

### Phase 3: Initial Deployment (2-3 days)
- [ ] Fresh Environment Test
    - [ ] Create new Python venv
    - [ ] Install only from requirements.txt
    - [ ] Run app with no existing config

- [ ] Performance Testing
    - [ ] Test with network throttling
    - [ ] Simulate Streamlit memory limits
    - [ ] Run multiple sessions in parallel

- [ ] Query Optimization
    - [ ] Time each materialized view
    - [ ] Check cache hit ratios
    - [ ] Identify slow queries (>1s)

- [ ] Load Testing
    - [ ] Test with production-size data
    - [ ] Simulate concurrent users
    - [ ] Monitor memory/CPU usage

- [ ] Configuration Check
    - [ ] Create fresh .env template
    - [ ] Test each config value type
    - [ ] Document resource requirements

### Phase 4: Production Setup (2-3 days)
- [ ] Pre-Deploy Cleanup
    - [ ] Review and clean up /pages/hidden folder
      - [ ] Archive or remove old data entry versions
      - [ ] Move active pages to main directory
      - [ ] Update page numbering if needed

- [ ] First Deploy
    - [ ] Deploy with minimal features first
    - [ ] Watch for memory/CPU spikes
    - [ ] Monitor connection counts

- [ ] Stabilization
    - [ ] Add error logging/monitoring
    - [ ] Set up alerts for failures
    - [ ] Document common errors/fixes

- [ ] Data Management
    - [ ] Test view refresh impact
    - [ ] Monitor query timeouts
    - [ ] Set up basic backup process




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


### Role Analysis
   - [ ] Role distribution charts
   - [ ] Network role preferences
   - [ ] Role-based filtering

### Market Analyzer Cleanup
- [ ] Remove db query studio_list - should be done through market fetch

### Performance Optimizations
- [ ] Implement lazy loading for visualizations
    - [ ] Load charts only when tab is active
    - [ ] Cache chart data per session
    - [ ] Add progress indicators for large charts

- [ ] Rename unified_view.py to content_view.py
    - [ ] Update imports in dependent files
    - [ ] Test all view components after rename
    - [ ] Remove old unified_view.py

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

### Day 4: Database Optimization & View Updates

- [x] Update Analytics Dashboard
    - [x] Connect to Supabase
    - [x] Implement performance optimizations
        - [x] Add st.cache_data for query results
        - [x] Use pagination for large datasets
    - [x] Port existing visualizations
        - [x] Use materialized views for complex charts
       
- [x] Studio Performance Migration
    1. [x] Update studio_analyzer.py to use shows_analyzer
        - [x] Remove success metrics from charts
        - [x] Fix indie studios calculation
        - [x] Use consistent data source for all charts
    2. [x] Update documentation
        - [x] Add data fetching architecture to README
        - [x] Update content analysis migration doc

- [x] Market Analyzer Migration
    1. [x] Update market_analyzer.py to use shows_analyzer
        - [x] Remove direct Supabase calls
        - [x] Update constructor to accept shows_analyzer data
        - [x] Test market snapshot view with new data source
    2. [x] Migrate improvements from market_analyzer_secure.py
        - [x] Port vertically integrated studio detection
        - [x] Port improved network filtering logic
        - [x] Port enhanced team member handling
    3. [x] Clean up
        - [x] Remove market_analyzer_secure.py
        - [x] Remove market_analyzer_old.py
        - [x] Update all imports to use market_analyzer.py

        - [x] Update Data Processing Layer
        - [x] Modify analyze_shows.py to use materialized views
        - [x] Separate data pipelines per component
        - [x] Test data processing changes
    - [ ] Update Components
        - [x] Update studio_view.py
            - [x] Use consistent data source
            - [x] Fix indie studios calculation
            - [x] Remove success metrics
        - [x] Update market_view.py
            - [x] Use shows_analyzer data source
            - [x] Update network filtering logic
            - [x] Test filtering and aggregations

### Must Have 
- Reliable data sync with Google Sheets
- Native Plotly templates for all visualizations
- Clear separation of concerns (templates/components)
- Complete test coverage

### Should Have 
- Fast load times (<2s per view)
- No duplicate code
- Comprehensive documentation

