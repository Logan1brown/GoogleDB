# Studio Performance Migration Audit

## Component Overview

### 1. Data Service Layer (`analyze_shows.py`)
- **Required Data**: Already available in existing views
- **Supabase Views to Use**:
  1. `api_show_details`:
     - studio_names (array)
     - title
     - network_name
     - status_name
     - active
  2. `api_market_analysis`:
     - tmdb_status
     - tmdb_seasons
     - tmdb_total_episodes
     - tmdb_last_air_date

### 2. Analysis Layer (`studio_analyzer.py`)
- **Primary Functions**:
  - `get_all_studios()`: Extract unique studios with counts
  - `get_shows_for_studio()`: Filter shows by studio
  - `analyze_studio_relationships()`: Network/genre analysis
  - `get_studio_insights()`: Detailed studio metrics
- **Required Changes**:
  1. Update column references:
     - 'studio' → 'studio_names' (array)
     - 'network' → 'network_name'
     - 'genre' → 'genre_name'
  2. Add active status filtering
  3. Integrate success metrics from SuccessAnalyzer

### 3. View Layer (`studio_view.py`)
- **Components**:
  - Studio relationship graph
  - Studio metrics
  - Studio filtering interface
  - Success stories
- **Required Changes**:
  1. Update column references to match API views
  2. Add success score coloring to graphs
  3. Filter by active shows only
  4. Update metrics calculations

## Data Flow
1. `ShowsAnalyzer`:
   ```python
   def fetch_studio_data(self):
       # Fetch show details with studio names
       shows_df = self.supabase.table('api_show_details').select(
           'title',
           'network_name',
           'studio_names',
           'status_name',
           'active',
           'tmdb_id'
       ).execute()

       # Get success metrics
       success_df = self.supabase.table('api_market_analysis').select(
           'tmdb_id',
           'tmdb_status',
           'tmdb_seasons',
           'tmdb_total_episodes',
           'tmdb_last_air_date'
       ).execute()

       # Merge success metrics
       shows_df = pd.merge(
           shows_df,
           success_df,
           on='tmdb_id',
           how='left'
       )

       return shows_df
   ```

2. `StudioAnalyzer`:
   ```python
   def analyze_studio_performance(self, shows_df):
       # Filter active shows
       active_shows = shows_df[shows_df['active'] == True]
       
       # Get success metrics
       success_metrics = self.success_analyzer.analyze_market(active_shows)
       
       # Analyze relationships
       studio_metrics = analyze_studio_relationships(active_shows)
       
       return {
           'metrics': studio_metrics,
           'success': success_metrics
       }
   ```

## Migration Steps
1. Update ShowsAnalyzer to preserve studio_names in filtering
2. Modify StudioAnalyzer to use array-based studio_names
3. Update StudioView to handle arrays
4. Add success metrics integration
5. Test with active status filtering

## Success Criteria
- [ ] All studio names correctly extracted from arrays
- [ ] Network relationships accurately mapped
- [ ] Success scores integrated into visualizations
- [ ] Only active shows included in analysis
- [ ] Performance matches or exceeds current version
