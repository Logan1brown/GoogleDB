# Success Analyzer Component Refactor

## Current State
Success scores are currently scattered across components:
1. MarketAnalyzer:
   - Success filtering in market_view.py (High >80, Medium 50-80, Low <50)
   - Network chart coloring by success in create_network_chart()
2. NetworkAnalyzer:
   - Success patterns analysis
3. StudioAnalyzer:
   - Success rate calculations

## Data Cleanup Plan

### 1. Google Sheets Changes

#### Shows Table
- Remove `success_score` column (will be calculated)
- Add `tmdb_id` column if not exists (for reliable joins)

#### TMDB Metrics Table
- Remove `success_score` column
- Set episode counts to NULL for unreliable statuses:
  ```sql
  UPDATE 'TMDB Metrics'
  SET 
    episodes = NULL,
    total_episodes = NULL,
    avg_episodes = NULL
  WHERE status IN ('Planned', 'In Production');
  ```

### 2. Code Updates (Breaking Changes)
```python
class MarketAnalyzer:
    def create_network_chart(self):
        # Temporarily disable success score coloring
        # Will be re-enabled with SuccessAnalyzer
        return base_chart

class StudioAnalyzer:
    def get_performance_metrics(self):
        # Temporarily return basic counts
        # Will be updated with new success metrics
        return {
            'total_shows': len(shows),
            'in_development': len(planned_shows)
        }
```

### 3. Dashboard Updates
1. Update all components to handle NULL scores
2. Add placeholder UI for in-development shows
3. Show basic metrics until SuccessAnalyzer is ready

## Current Data Quality

TMDB data quality varies by show status:

### Reliable Data (Use for Success Metrics)
- **Returning Series**
  - Accurate season counts
  - Complete episode data per season
  - Example: `Acapulco,3,"10, 10, 10",30,10,Returning Series`

- **Ended**
  - Final season/episode counts
  - Complete air date data
  - Example: `A Small Light,1,8,8,8,Ended`

- **Canceled**
  - Accurate data up to cancellation
  - Example: `Alaska Daily,1,11,11,11,Canceled`

### Unreliable Data (Exclude from Success Metrics)
- **Planned**
  - Often has placeholder data (1 season, 1 episode)
  - Example: `6666,1,1,1,1,Planned`

- **In Production**
  - Incomplete/tentative episode counts
  - Example: `A Knight of the Seven Kingdoms,1,3,3,3,In Production`

## Component Responsibilities

### 1. Core Success Metrics (Studio Profitability Focus)

#### Season Achievement Points (Max: 60)
- Season 2: 40 points (major milestone)
- Season 3+: +20 points each (proven success)

#### Episode Volume Points
- 1 point per episode
- Examples:
  - 8 episode season = 8 points
  - 13 episode season = 13 points
  - 22 episode season = 22 points
- Points accumulate across seasons

#### Status Modifiers (Max: 20)
- Returning Series (pre-S2): +15 points (network confidence)
- Ended (planned): +10 points (completed run)
- Canceled: -20 points (unsuccessful run)

Example Scores:
- Successful Drama: S3 (60pts) + 30 total eps (30pts) + Returning (15pts) = 105pts
- Limited Series: S1 + 8 eps (8pts) + Ended (10pts) = 18pts
- Canceled Show: S1 + 13 eps (13pts) + Canceled (-20pts) = -7pts

### 2. Relative Success Classification

```python
class ShowStatus:
    # Shows with reliable data we can score
    RELIABLE = ['Returning Series', 'Ended', 'Canceled']
    # Shows we can't score yet
    UNRELIABLE = ['Planned', 'In Production']

class SuccessAnalyzer:
    def analyze_market(self, all_shows):
        # Step 1: Split shows into reliable vs unreliable
        reliable_shows = [s for s in all_shows if s['status'] in ShowStatus.RELIABLE]
        unreliable_shows = [s for s in all_shows if s['status'] in ShowStatus.UNRELIABLE]
        
        # Step 2: Calculate scores for reliable shows
        scores = [
            (show, self.calculate_success(show))
            for show in reliable_shows
        ]
        
        # Step 3: Find benchmark (highest achieved score)
        max_score = max(score for _, score in scores)
        
        # Step 4: Define tiers relative to max
        tiers = {
            'high': max_score * 0.8,    # Top 20% of max
            'medium': max_score * 0.5,   # Top 50% of max
            'low': 0                     # Below 50% of max
        }
        
        # Step 5: Classify all shows
        results = {
            # Shows we can score
            'reliable': {
                show['name']: {
                    'score': score,
                    'tier': self._get_tier(score, tiers),
                    'pct_of_max': score / max_score
                }
                for show, score in scores
            },
            # Shows we can't score yet
            'in_development': {
                show['name']: {
                    'status': show['status'],
                    'episodes': show['episodes']
                }
                for show in unreliable_shows
            }
        }
        return results
        
    def _get_tier(self, score, tiers):
        if score >= tiers['high']: return 'high'
        if score >= tiers['medium']: return 'medium'
        return 'low'
```

Benefits:
1. Tiers automatically adjust to the current market
2. Always have shows in each tier
3. Clear what "good performance" means (relative to top shows)
4. Easy to understand (e.g. "performing at 80% of top show")

## Data Flow with Team Filtering

```python
class ShowsAnalyzer:
    def fetch_data(self):
        # 1. Get all data
        shows_df = sheets_client.get_shows_data()
        tmdb_df = sheets_client.get_tmdb_metrics()
        team_df = sheets_client.get_team_data()
        
        # 2. Merge show and TMDB data
        shows_df = shows_df.merge(
            tmdb_df[['show_id', 'status', 'episodes', 'seasons']],
            on='show_id',
            how='left'
        )
        
        # Store raw data for filtering
        self.shows_df = shows_df
        self.team_df = team_df
        self.success_analyzer = SuccessAnalyzer()
        
        # Initial market analysis (unfiltered)
        self._update_market_analysis()
    
    def analyze_team_performance(self, team_member=None, role=None):
        # First get global success tiers from ALL shows
        global_analysis = self.success_analyzer.analyze_market(self.shows_df)
        global_tiers = {
            'high': global_analysis['high_threshold'],
            'medium': global_analysis['medium_threshold']
        }
        
        # Then filter shows if needed
        if team_member or role:
            filtered_team = self.team_df
            if team_member:
                filtered_team = filtered_team[filtered_team['name'] == team_member]
            if role:
                filtered_team = filtered_team[filtered_team['role'] == role]
            
            # Get their shows but keep global tiers
            show_ids = filtered_team['show_id'].unique()
            filtered_df = self.shows_df[self.shows_df['show_id'].isin(show_ids)]
        else:
            filtered_df = self.shows_df
            
        # Score filtered shows using global tiers
        results = {
            'shows': {
                show['name']: {
                    'score': self.success_analyzer.calculate_success(show),
                    'tier': self._get_tier_from_global(show, global_tiers),
                    'pct_of_max': show['score'] / global_analysis['max_score']
                }
                for _, show in filtered_df.iterrows()
                if show['status'] in ShowStatus.RELIABLE
            },
            'summary': {
                'avg_score': np.mean([s['score'] for s in results['shows'].values()]),
                'hit_rate': len([s for s in results['shows'].values() 
                                if s['tier'] == 'high']) / len(results['shows']),
                'total_shows': len(results['shows'])
            }
        }
        return results
    
    def _update_market_analysis(self, shows_df=None):
        # Use provided DataFrame or full dataset
        df = shows_df if shows_df is not None else self.shows_df
        
        # Recalculate success metrics
        market_analysis = self.success_analyzer.analyze_market(df)
        
        # Update all components with new data
        self.market_analyzer = MarketAnalyzer(
            shows_df=df,
            success_data=market_analysis
        )
        self.genre_analyzer = GenreAnalyzer(
            shows_df=df,
            success_data=market_analysis
        )
        # ... etc for other analyzers
```

### Component Usage

```python
# 1. Market View
class MarketAnalyzer:
    def create_network_chart(self):
        network_stats = {}
        for network in self.shows_df['network'].unique():
            network_shows = self.success_data['reliable'].get(
                show for show in self.success_data['reliable']
                if show['network'] == network
            )
            network_stats[network] = {
                'avg_score': np.mean([s['score'] for s in network_shows]),
                'top_show': max(network_shows, key=lambda s: s['score']),
                'in_development': len([s for s in self.success_data['in_development']
                                     if s['network'] == network])
            }

# 2. Genre Analysis
class GenreAnalyzer:
    def analyze_genre_success(self, genre):
        genre_shows = [
            show for show in self.success_data['reliable'].values()
            if genre in show['genres']
        ]
        return {
            'avg_score': np.mean([s['score'] for s in genre_shows]),
            'top_show': max(genre_shows, key=lambda s: s['score']),
            'pct_of_max': np.mean([s['pct_of_max'] for s in genre_shows])
        }

# 3. Source Analysis
class SourceAnalyzer:
    def compare_source_success(self):
        return {
            source: {
                'avg_score': np.mean([s['score'] for s in self.success_data['reliable'].values()
                                    if s['source'] == source]),
                'hit_rate': len([s for s in self.success_data['reliable'].values()
                                if s['source'] == source and s['tier'] == 'high'])
            }
            for source in self.source_types
        }
```
class StudioAnalyzer:
    def analyze_studio_performance(self, studio):
        studio_shows = self.get_shows_by_studio(studio)
        return {
            'success_metrics': {
                'avg_score': self.success_analyzer.get_avg_success(studio_shows),
                'hit_rate': self.success_analyzer.get_hit_rate(studio_shows),
                'total_episodes': self.success_analyzer.get_total_episodes(studio_shows)
            },
            'show_breakdown': {
                'reliable_data': len([s for s in studio_shows if s['status'] in ShowStatus.RELIABLE]),
                'in_development': len([s for s in studio_shows if s['status'] in ShowStatus.UNRELIABLE])
            }
        }
```

## Data Cleanup Required

### 1. Remove Success Score Columns
- Delete `success_score` from shows table
- Delete `success_score` from tmdb_success_metrics
- Success will be calculated dynamically by SuccessAnalyzer

### 2. Clean Episode Data
```sql
-- Set episode counts to NULL for unreliable data
UPDATE tmdb_success_metrics
SET 
    tmdb_eps = NULL,
    tmdb_total_eps = NULL,
    tmdb_avg_eps = NULL
WHERE tmdb_status IN ('Planned', 'In Production');
```

### 3. Update Schema
```sql
-- Allow NULL values for episode counts
ALTER TABLE tmdb_success_metrics
MODIFY COLUMN tmdb_eps VARCHAR(255) NULL,
MODIFY COLUMN tmdb_total_eps INT NULL,
MODIFY COLUMN tmdb_avg_eps FLOAT NULL;
```

## Benefits of Data Cleanup
1. Data accuracy: No more placeholder values
2. Clear intentions: NULL means "no data yet"
3. Single source of truth: Success calculated, not stored
4. Better data quality: Real numbers vs placeholders

## Implementation Plan

1. Create SuccessAnalyzer with data quality controls
2. Update MarketAnalyzer to handle null success scores
3. Add visual indicators for data reliability
4. Document data quality requirements
class SuccessConfig:
    """Central success configuration"""
    def __init__(self):
        self.metrics = {
            'season2_value': 40,
            'additional_season_value': 20,
            'min_episodes': 11
        }

class BaseSuccessStrategy:
    def __init__(self, config: SuccessConfig):
        self.config = config

class SuccessAnalyzer:
    def __init__(self, config: SuccessConfig):
        self.config = config
        self.strategies = {
            'standard': StandardSuccess(config),
            'limited': LimitedSeriesSuccess(config),
            'anthology': AnthologySuccess(config)
        }
    
    def calculate_success(self, show_data):
        strategy = self._select_strategy(show_data)
        return strategy.calculate_success(show_data)
```

This gives us:
1. Configurable metrics when needed
2. Different strategies for show types
3. Central control over success calculation
4. Easy to extend with new strategies

## Proposed Implementation
```python
class SuccessAnalyzer:
    """Analyzer for show success metrics using TMDB data."""
    
    def __init__(self, shows_df):
        self.shows_df = shows_df
        self._validate_data()
        
    def calculate_show_success(self, show_id):
        """Calculate success metrics for a single show"""
        pass
        
    def analyze_network_success(self, network):
        """Analyze success patterns for a network"""
        pass
        
    def get_success_trends(self, timeframe='1Y'):
        """Get success trend analysis"""
        pass
        
    def track_franchise_success(self, parent_show_id):
        """Track success across franchise/spinoffs"""
        pass
```
        """Get success tier (High/Medium/Low) for a score."""
        pass
        
    def filter_by_success(self, df, tier):
        """Filter shows by success tier."""
        pass
        
    def get_success_color(self, score):
        """Get color for visualizations based on success score."""
        pass
```

### 2. Integration Points
1. MarketAnalyzer:
   ```python
   def __init__(self, shows_df):
       self.success_analyzer = SuccessAnalyzer(shows_df)
       
   def create_network_chart(self):
       # Use success_analyzer for coloring
       colors = [self.success_analyzer.get_success_color(score) 
                for score in success_scores]
   ```

2. NetworkAnalyzer:
   ```python
   def analyze_network(self, network):
       success_metrics = self.success_analyzer.get_success_metrics(
           self.shows_df[self.shows_df['network'] == network]
       )
   ```

## Future Enhancements

### 2. Spinoff Tracking
- No current way to track spinoff relationships between shows
- Could add spinoff tracking to boost success scores:
  - Parent show gets bonus for successful spinoffs
  - Spinoff gets partial credit from parent's success
  - Example: Better Call Saul (spinoff) & Breaking Bad (parent)
- Would require:
  - New data field for spinoff relationships
  - Logic to handle multi-generation spinoffs
  - Weighting system for spinoff impact on scores
