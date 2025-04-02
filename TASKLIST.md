# TV Series Database Tasks

## Current Sprint 🔄

### TMDB Integration: Show Matching
1. Show Data Enhancement
   - [ ] Identify shows without TMDB IDs
   - [ ] Search API for potential matches
   - [ ] Verify and confirm matches
   - [ ] Document unmatched shows

### Backlog

TMDB Work  - Success Metrics
     - [ ] Number of seasons
     - [ ] Episodes per season
     - [ ] Production status (map TMDB status: Returning Series→Active, Planned/In Production→Development)
     - [ ] Last air date
     - [ ] Success score calculation
     - [ ] Success tier assignment
   - Episode Details
     - [ ] Total episode count
     - [ ] Season 1 episode count (maps to Episode Count)
     - [ ] Average episodes/season
   - Show Information
     - [ ] Show overview/summary mapped to Notes
     - [ ] Series type (limited if: single season + not in production, or has limited/miniseries keywords)

2. Implementation & Testing
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




### Must Have 
- Reliable data sync with Google Sheets
- Native Plotly templates for all visualizations
- Clear separation of concerns (templates/components)
- Complete test coverage

### Should Have 
- Fast load times (<2s per view)
- No duplicate code
- Comprehensive documentation

