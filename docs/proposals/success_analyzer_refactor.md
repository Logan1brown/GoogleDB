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

## Proposed Changes

### 1. New SuccessAnalyzer Component
Create a dedicated component to handle all success-related logic:
```python
class SuccessAnalyzer:
    """Analyzer for show success metrics using TMDB data."""
    
    # Success thresholds
    HIGH_SUCCESS = 80
    MEDIUM_SUCCESS = 50
    
    def __init__(self, shows_df):
        self.shows_df = shows_df
        
    def calculate_success_score(self, show):
        """Calculate success score using TMDB metrics:
        - Base: 40pts for Season 2
        - Sustained: +20pts each for S3/S4/S5+
        - Status: +10pts planned ending, +5pts in production
        - Penalty: -20pts if cancelled with <11 eps
        """
        pass
        
    def get_success_tier(self, score):
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

### 3. Special Cases
1. Limited Series:
   - Add special handling in calculate_success_score()
   - Consider factors like:
     - Planned episode count
     - Completion status
     - Critical reception

## Benefits
1. Single source of truth for success metrics
2. Consistent success thresholds across components
3. Easier to modify success calculation
4. Better handling of special cases

## Next Steps
1. Create SuccessAnalyzer class
2. Move success calculation from data integration
3. Update MarketAnalyzer to use new component
4. Update other analyzers
5. Add tests for success calculations

## Future Enhancements

### 1. Returning Series Bonus
- Currently unclear if we add 20pts to shows renewed for S2 before S2 actually airs
- Consider adding a "Returning Series" flag in the data
- Could award partial points (e.g. 10pts) for confirmed renewal before S2
- Would help identify shows with strong early performance

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
