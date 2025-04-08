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

- [ ] Execute Database Setup
    - [ ] Run support tables migration
    - [ ] Run lookup data migration
    - [ ] Run main tables migration
    - [ ] Run auth policies setup
    - [ ] Verify all constraints
    - [ ] Test materialized views
    - [ ] Configure RLS policies

### Day 2: Data Migration
- [ ] Export existing data
    - [ ] Export shows data
    - [ ] Export team members data
    - [ ] Export lookup tables
- [ ] Transform data
    - [ ] Clean and normalize show titles
        - [ ] Generate search_title fields
        - [ ] Handle special characters
    - [ ] Map network names
        - [ ] Generate search_name fields
        - [ ] Handle aliases
    - [ ] Map studio names
        - [ ] Generate search_name fields
        - [ ] Handle divisions/platforms
    - [ ] Map genres
        - [ ] Generate search_name fields
        - [ ] Split into primary/secondary
- [ ] Import data
    - [ ] Import lookup tables first
    - [ ] Import shows data
    - [ ] Import show_team data
    - [ ] Verify data integrity
        - [ ] Check all FKs resolve
        - [ ] Validate search fields
        - [ ] Test materialized views

### Day 3: Streamlit Apps 
- [ ] Create Data Entry App
    - [ ] Setup Supabase client
    - [ ] Create login form
    - [ ] Build data entry forms with validation
    - [ ] Test CRUD operations
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
- [ ] Testing
    - [ ] Test all forms
    - [ ] Verify permissions
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

