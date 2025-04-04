# Analyzer System Refactor Proposal

## Current Issues

1. **Monolithic ShowsAnalyzer**
   - ~770 lines handling data loading, cleaning, and analysis
   - Complex dependencies between components
   - Hard to maintain and extend
   - Critical column name differences spread across code

2. **Mixed Responsibilities**
   - Data loading mixed with analysis logic
   - Sheet access spread across components
   - Validation duplicated in multiple places
   - No clear separation of concerns

## Proposed Architecture

### 1. Data Layer

```python
class DataLoader:
    """Single source of truth for data loading"""
    def fetch_data(self, force=False) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Load and clean shows/team data"""
        # Handle sheet access
        # Maintain column differences (shows vs show_name)
        # Cache results
        pass

class DataCleaner:
    """Handle all data normalization"""
    def clean_data(self, shows_df, team_df):
        """Clean and validate data"""
        # Lookup table management
        # Field normalization
        # Data validation
        pass
```

### 2. Analysis Layer

```python
class BaseAnalyzer:
    """Base class for all analyzers"""
    def __init__(self, data_loader: DataLoader):
        self.data_loader = data_loader
        self.shows_df = None
        self.team_df = None
    
    def load_data(self, force=False):
        """Get clean data from loader"""
        self.shows_df, self.team_df = self.data_loader.fetch_data(force)

    def validate_columns(self, required_columns: List[str]):
        """Check analyzer has needed columns"""
        # Common validation logic

class ConnectionsAnalyzer(BaseAnalyzer):
    """Network connections analysis"""
    def analyze_network_connections(self):
        self.load_data()  # Get fresh data
        # Do connections analysis

class GenreAnalyzer(BaseAnalyzer):
    """Genre pattern analysis"""
    def analyze_genre_patterns(self):
        self.load_data()
        # Do genre analysis

class MarketAnalyzer(BaseAnalyzer):
    """Market snapshot analysis"""
    def analyze_market_trends(self):
        self.load_data()
        # Do market analysis
```

## Benefits

1. **Clear Separation of Concerns**
   - Data loading isolated in DataLoader
   - Each analyzer focuses on one type of analysis
   - Common functionality in BaseAnalyzer
   - Clean inheritance hierarchy

2. **Better Data Management**
   - Single source of truth for data loading
   - Centralized column name handling
   - Consistent data cleaning
   - Proper caching strategy

3. **Easier Maintenance**
   - Smaller, focused classes
   - Clear dependencies
   - Easier testing
   - Simpler to extend

## Implementation Strategy

Given the critical nature of the analyzer system, we need a careful migration:

### Phase 1: Preparation
1. Add extensive tests for current functionality
2. Document all analyzer dependencies
3. Create new package structure
4. Add detailed logging

### Phase 2: Data Layer
1. Create DataLoader class
2. Migrate sheet access code
3. Implement caching
4. Add column validation

### Phase 3: Base Classes
1. Create BaseAnalyzer
2. Add common utilities
3. Set up inheritance structure
4. Test with dummy analyzer

### Phase 4: Migration
1. Migrate one analyzer at a time
2. Extensive testing each step
3. Keep old code until verified
4. Update all dependencies

### Phase 5: Cleanup
1. Remove old code
2. Update documentation
3. Final testing
4. Deploy to production

## Risks and Mitigation

1. **Breaking Changes**
   - Keep old code working during migration
   - Extensive testing at each step
   - Clear rollback plan
   - Staged deployment

2. **Column Name Issues**
   - Centralize in DataLoader
   - Add validation
   - Improve logging
   - Document requirements

3. **Performance Impact**
   - Maintain caching
   - Profile new code
   - Optimize critical paths
   - Monitor metrics

## Next Steps

1. Review and approve proposal
2. Set up test infrastructure
3. Create detailed migration plan
4. Begin Phase 1 preparation
