# TV Series Database Tasks

## Current Sprint 🔄

### TMDB Work - Success Metrics

1. Create TMDB Success Metrics Sheet
   - [ ] Number of seasons
   - [ ] Episodes per season
   - [ ] Total episode count
   - [ ] Average episodes/season
   - [ ] Status (Returning/Planned/etc)
   - [ ] Last air date
   - [ ] Success score (0-100)

2. Update Shows Sheet
   - [ ] Notes column (TMDB overview)
   - [ ] Order type column (limited vs ongoing)
   - [ ] Status column (Active/Development/Cancelled)
   - [ ] Episode count column (Season 1)
   - [ ] Success score column (0-100)

3. Data Collection Pipeline
   - [ ] Pull raw TMDB data
   - [ ] Calculate success scores
   - [ ] Map TMDB statuses to our statuses
   - [ ] Determine order types
   - [ ] Extract season 1 episode counts

### Implementation & Testing

### Backlog

   - [ ] Create feature branch `feature/tmdb-success-metrics`
   - [ ] Success score calculation (0-100)
   - [ ] Test scoring with known shows
     - [ ] Long-running hits (e.g., Stranger Things)
     - [ ] Quick cancellations
     - [ ] Limited series
     - [ ] Shows with missing data
   - [ ] Validate season/episode counts
   - [ ] Test data pipeline with sample set
   - [ ] Create rollback plan for sheets/db
   - [ ] Success tier assignment
   - [ ] Limited vs ongoing classification
   - [ ] Database schema updates
   - [ ] Sheets column additions

### Components
1. Network Connections Dashboard
   - [ ] Improve layout and spacing
   - [ ] Add tooltips and help text
   - [ ] Optimize performance for large result sets

2. Content Strategy Integration
   - [ ] Combine genre and source views
   - [ ] Add cross-dimensional insights
   - [ ] Market gap identification view
   - [ ] Network preference analysis

3. Role Analysis
   - [ ] Refactor role_analysis.py
   - [ ] Add role distribution charts
   - [ ] Network role preferences
   - [ ] Consider role-based filtering layer

### Improvements

   1. Combined Insights Engine
     - [ ] Network-Genre-Source correlations
     - [ ] Creator specialization tracking
     - [ ] Market gap detection algorithms
     - [ ] Trend prediction models

2. Advanced Visualizations

   - Data Presentation
     - [ ] Progressive loading for large datasets
     - [ ] Smart result summarization
     - [ ] Export and sharing options

## Completed ✅

### TMDB Integration: Show Matching
1. Show Data Enhancement
   - [x] Identify shows without TMDB IDs
   - [x] Search API for potential matches
   - [x] Verify and confirm matches
   - [x] Document unmatched shows

### Must Have 
- Reliable data sync with Google Sheets
- Native Plotly templates for all visualizations
- Clear separation of concerns (templates/components)
- Complete test coverage

### Should Have 
- Fast load times (<2s per view)
- No duplicate code
- Comprehensive documentation

