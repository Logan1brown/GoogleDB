# Analyzer Component Architecture

## Overview
This proposal outlines a modular architecture for our analysis system, focusing on specialized component analyzers that work together through a coordinated market analyzer.

## Current State
We have several specialized analyzers:
- NetworkConnectionAnalyzer: Analyzes network relationships and talent flow
- StudioAnalyzer: Handles studio performance and relationships
- GenreAnalyzer: Processes genre distributions and trends
- SourceAnalyzer: Analyzes content sources and adaptations

However, we're currently duplicating some analysis logic in the MarketAnalyzer class, which has grown too large and needs refactoring.

## Proposed Architecture

### 1. Component Analyzers
Each analyzer is responsible for deep analysis in its domain:

#### Existing Analyzers
- **NetworkConnectionAnalyzer**
  - Network-to-network relationships
  - Talent pools and sharing
  - Network success patterns
  
- **StudioAnalyzer**
  - Studio performance metrics
  - Network relationships
  - Genre specialization
  - Vertical integration analysis

- **GenreAnalyzer**
  - Genre distributions
  - Cross-genre patterns
  - Success by genre

#### New Analyzers
- **SuccessAnalyzer**
  ```python
  class SuccessAnalyzer:
      def calculate_success_metrics(self) -> Dict:
          return {
              'avg_success_score': float,
              'high_success_shows': int,
              'success_distribution': Dict,
              'success_by_network': Dict,
              'success_by_genre': Dict
          }
      
      def create_success_visualization(self) -> go.Figure:
          # Success score distribution visualization
  ```

### 2. Data Flow Pattern
1. Base data (shows_df, team_df) loaded once
2. Each analyzer receives data reference
3. Analyzers process and cache results
4. Results combined through MarketAnalyzer

### 3. MarketAnalyzer as Coordinator
```python
class MarketAnalyzer:
    def __init__(self, shows_df, team_df=None):
        self.network_analyzer = NetworkConnectionAnalyzer(shows_df, team_df)
        self.studio_analyzer = StudioAnalyzer(shows_df)
        self.success_analyzer = SuccessAnalyzer(shows_df)
        
    def generate_market_insights(self, shows_df=None):
        # Coordinate between analyzers
        network_data = self.network_analyzer.analyze_talent_pools()
        studio_data = self.studio_analyzer.analyze_studio_relationships()
        success_data = self.success_analyzer.calculate_success_metrics()
        
        return combined_insights
```

### 4. Dashboard Integration
- Each specialized view uses its domain analyzer directly
- Market View uses MarketAnalyzer for coordinated insights
- Filtering handled at component level
- Visualizations created by respective analyzers

## Benefits
1. **Code Reuse**: Analyzers used across components
2. **State Management**: Each analyzer maintains its state
3. **Performance**: Data processed once and cached
4. **Flexibility**: Components can access both deep and broad insights
5. **Maintainability**: Clear separation of concerns

## Implementation Plan

### Phase 1: Success Analyzer
1. Create SuccessAnalyzer class
2. Move success metrics from MarketAnalyzer
3. Add new success visualizations
4. Update market_view.py to use new analyzer

### Phase 2: MarketAnalyzer Refactor
1. Remove duplicate analysis code
2. Update to use component analyzers
3. Add coordinator methods
4. Update dashboard components

### Phase 3: Testing & Documentation
1. Add unit tests for new SuccessAnalyzer
2. Update integration tests
3. Document analyzer interfaces
4. Add usage examples

## Migration Strategy
1. Create new analyzers alongside existing code
2. Gradually move functionality
3. Update components one at a time
4. Run parallel testing
5. Remove deprecated code

## Timeline
- Phase 1: 1-2 days
- Phase 2: 2-3 days
- Phase 3: 1-2 days
- Total: 4-7 days

## Success Criteria
1. Reduced code duplication
2. Improved test coverage
3. Cleaner component interfaces
4. Better performance through caching
5. Easier to add new analysis features
