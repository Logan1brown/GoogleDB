# TV Series Database Analysis Dashboard

[NOTE TO CASCADE: This file MUST be read completely, but in chunks of 200 lines (maximum allowed by view_file). Start at line 0 and repeatedly call view_file with increasing StartLine until you reach the end of the file. Use IncludeSummaryOfOtherLines=true to maintain context. Never try to read the whole file at once.]


## 🚨 MAJOR REFACTOR IN PROGRESS 🚨

We are transitioning from a custom class-based template system to Plotly's native template system. This is a breaking change that affects multiple components.

### Migration Strategy

1. Visualization System Setup (🟡 In Progress)
   - [x] Style Templates complete
   - [x] Basic Layouts complete
   - [ ] Analysis Layouts in progress
   A. Style Templates (via go.layout.Template)
      - [x] Create base template
          - [x] Brand styles (fonts, colors, margins)
          - [x] Common defaults (legend position, hover)
      - [x] Create chart type defaults:
          - [x] bar.py (colors, hover format)
          - [x] heatmap.py (colorscales, axes)
          - [x] scatter.py (markers, lines)
          - [x] table.py (header styles, sorting)
          - [x] sankey.py (node/link styles)
   
   B. Grid Layouts (via make_subplots)
      - [x] Basic Layouts:
          - [x] chart_only.py (single chart)
          - [x] chart_table.py (chart + data table)
          - [x] chart_dual_table.py (chart + two tables)
          - [x] chart_insights.py (chart + key findings)
          - [x] chart_insights_table.py (chart + findings + table)
      
      - [ ] Analysis Layouts:
          - [-] market_snapshot.py (complex layout)
              Next steps:
              1. Review README specs for Market Snapshot
              2. Create detailed layout plan
              3. Implement one section at a time with visual validation
              4. Focus on proper subplot types and text positioning

2. Component Migration
   a. Move current components to v1/
   b. Create v2 components using Plotly templates:
      - [-] Market Snapshot (attempted but failed)
        - Uses: defaults/bar + grids/with_table
        - Initial attempt failed visual inspection
        - Need to restart with proper layout planning
      - [ ] Content Analysis
        - Uses: defaults/heatmap + grids/stacked
      - [ ] Network Analysis
        - Uses: defaults/sankey + grids/dual
      - [ ] Relationship Analysis
        - Uses: defaults/scatter + grids/with_table
      - [ ] Studio Analysis
        - Uses: defaults/bar + grids/stacked

3. Testing & Validation
   - [ ] Test each template independently
   - [ ] Test template combinations
   - [ ] Verify component visual parity
   - [ ] Update test suite for new structure

4. Documentation
   - [x] Update TEMPLATE_SYSTEM.md
   - [x] Update DIRECTORY_STRUCTURE.md
   - [ ] Document each template's API
   - [ ] Update component migration guide

5. Cleanup
   - [ ] Remove utils/templates/ after migration
   - [ ] Remove v1/ after validation
   - [ ] Remove v2/ prefix from final structure

### File Status Overview

#### Keep (No Changes)
- `src/dashboard/utils/style_config.py` (styling constants)
- `src/data_processing/**/*.py` (data processing)
- `src/dashboard/app.py` (main app)

#### Create New (v2)
- `src/dashboard/templates/`
  - `base.py` → Base Plotly templates
  - `market.py` → Market analysis templates
  - `genre.py` → Genre analysis templates
  - `network.py` → Network analysis templates

#### Update
- `src/dashboard/components/`
  - `market_pulse.py` → `market_dashboard.py`
  - Other components to follow naming convention

#### Remove (After Migration)
- `src/dashboard/utils/templates/`
  - `base.py`
  - `insight.py`
  - `market_overview.py`
  - `network_analysis.py`
  - `dual_analysis.py`

### Documentation Updates Needed
1. `README.md`
  - Update architecture section
  - Add migration notes
  - Update visualization standards
2. `docs/development/`
  - `TEMPLATE_SYSTEM.md` (complete rewrite)
  - `STYLE_GUIDE.md` (update examples)
  - `VISUALIZATION_STANDARDS.md` (new file)
3. API Documentation
  - Update all docstrings
  - Add migration guides
4. Component Documentation
  - Update usage examples
  - Add template examples

## Completed Phases ✅

### Phase 1: Setup and Configuration
- [x] Directory structure and organization
- [x] Dependencies and requirements
- [x] Google Sheets integration
- [x] Authentication and security

### Phase 2: Core Data Processing
- [x] Data fetching and caching
- [x] Data cleaning and validation
- [x] Basic statistical analysis
- [x] Analysis results storage

### Phase 3: Initial Visualizations
- [x] Market snapshot dashboard
  - [x] KPI widgets with trends
  - [x] Mini trend charts
  - [x] Main visualization area
- [x] Basic network analysis
  - [x] Talent pool metrics
  - [x] Network sharing percentages
- [x] Simple genre analysis

## Current Phase: Template System Migration

### 1. Documentation (🟡 In Progress)
- [ ] Create `MIGRATION_GUIDE.md`
  - [ ] Document architectural changes
  - [ ] List affected components
  - [ ] Provide migration examples
- [ ] Update `README.md`
  - [ ] Add migration notice
  - [ ] Update architecture section
  - [ ] Update visualization docs
- [ ] Update `STYLE_GUIDE.md`
  - [ ] Remove class-based examples
  - [ ] Add Plotly template examples
  - [ ] Update naming conventions

### 2. New Template System (✅ Complete)
- [x] Create `src/dashboard/templates/`
  - [x] `base.py`
    - [x] Base Plotly template
    - [x] Grid templates
    - [x] Common annotations
  - [x] `snapshot.py`
    - [x] Dataset overview templates
    - [x] Network distribution templates
    - [x] KPI templates
  - [x] `content.py`
    - [x] Genre analysis templates
    - [x] Source analysis templates
    - [x] Distribution templates
  - [x] `network.py`
    - [x] Connection templates
    - [x] Sharing pattern templates
    - [x] Flow templates
  - [x] `relationship.py`
    - [x] Collaboration templates
    - [x] Team pattern templates
    - [x] Role hierarchy templates
  - [x] `studio.py`
    - [x] Performance templates
    - [x] Comparison templates
    - [x] Metric templates

### 3. Component Migration (🟡 In Progress)
- [ ] Create new components
  - [x] `snapshot_dashboard.py`
    - [x] Dataset overview & KPIs
    - [x] Network distribution
    - [x] Market trends
  - [ ] `content_strategy.py`
    - [ ] Genre analysis
    - [ ] Source analysis
    - [ ] Content patterns
  - [ ] `creative_networks.py`
    - [ ] Network connections
    - [ ] Sharing patterns
    - [ ] Flow diagrams
  - [ ] `creative_relationships.py`
    - [ ] Creator collaborations
    - [ ] Team patterns
    - [ ] Role hierarchies
  - [ ] `studio_performance.py`
    - [ ] Production patterns
    - [ ] Success metrics
    - [ ] Comparative analysis

### 4. Testing & Validation (⭕ Not Started)
- [ ] Create test suite
  - [ ] Template tests
  - [ ] Visual regression tests
  - [ ] Integration tests
- [ ] Manual testing
  - [ ] Visual inspection
  - [ ] Performance testing
  - [ ] Edge cases

### 5. Cleanup (⭕ Not Started)
- [ ] Remove old files
  - [ ] `src/dashboard/utils/templates/`
    - [ ] `base.py`
    - [ ] `insight.py`
    - [ ] `market_overview.py`
    - [ ] `network_analysis.py`
    - [ ] `dual_analysis.py`
  - [ ] Old components
    - [ ] `market_pulse.py`
    - [ ] `trend_analysis.py`
    - [ ] `source_analysis.py`
  - [ ] Move docs/development/MIGRATION_GUIDE.md to docs/archive/2025_template_migration.md
- [ ] Final validation
  - [ ] All features working
  - [ ] No references to old system
  - [ ] Documentation complete
  - [ ] No temporary migration files remain 🚧

### 1. Plotly Native Templates
- [ ] Create base_templates.py:
  - [ ] Common styling template (fonts, colors, margins)
  - [ ] Grid system templates (1x1, 2x1, 3x1, 2x2)
  - [ ] Default trace templates (bar, line, scatter, heatmap)
  - [ ] Annotation templates (titles, insights, KPIs)

### 2. Market Analysis Templates
- [ ] Create market_templates.py:
  - [ ] Market overview template
    - [ ] 3x3 grid layout
    - [ ] KPI widget positions
    - [ ] Mini chart defaults
  - [ ] Chart templates
    - [ ] Trend charts (bar, line)
    - [ ] Distribution charts
    - [ ] Comparison charts

### 3. Network Analysis Templates
- [ ] Create network_templates.py:
  - [ ] Network graph template
    - [ ] Node and edge styling
    - [ ] Force layout defaults
  - [ ] Flow diagram template
  - [ ] Matrix template

### 4. Migration
- [ ] Update market_pulse.py (highest priority)
- [ ] Update genre_analysis.py
- [ ] Update network_analysis.py

## Upcoming Phases

### Phase 5: Enhanced Network Analysis
- [ ] Network sharing visualization:
  - [ ] Force-directed network graph
  - [ ] Detailed sharing metrics
  - [ ] Top creator identification

- [ ] Role analysis improvements:
  - [ ] Compound role handling
  - [ ] Role standardization
  - [ ] Distribution analysis

- [ ] Network pairs deep dive:
  - [ ] Pair-wise analysis
  - [ ] Common patterns
  - [ ] Creator movement

### Phase 6: Additional Analysis Types
- [ ] Source analysis:
  - [ ] Distribution patterns
  - [ ] Network preferences
  - [ ] Success metrics

- [ ] Performance metrics:
  - [ ] Network rankings
  - [ ] Growth patterns
  - [ ] Market share

### Phase 7: Documentation
- [ ] Template system guide
- [ ] Visualization cookbook
- [ ] Analysis methodology
- [ ] Maintenance procedures

### Phase 8: Quality and Performance
- [ ] Error handling
- [ ] Performance optimization
- [ ] Automated testing
- [ ] Backup procedures

## Success Criteria

### Functionality
1. ✅ Analysis scripts run reliably
2. ✅ Data stays synced with Google Sheets
3. ⏳ All visualizations use Plotly native templates
4. ⏳ No references to old template system

### Code Quality
5. ⏳ Consistent naming across codebase
6. ⏳ Clear separation of concerns
7. ⏳ Comprehensive test coverage
8. ⏳ No duplicate code

### Documentation
9. ⏳ Complete migration guide
10. ⏳ Updated architecture docs
11. ⏳ Clear usage examples
12. ⏳ No outdated references

### Performance
13. ⏳ Fast load times (<2s per view)
14. ⏳ Efficient template usage
15. ⏳ No memory leaks

### Functionality
1. ✅ Analysis scripts run reliably
2. ✅ Data stays synced with Google Sheets
3. ⏳ All visualizations use Plotly native templates

### Usability
4. ✅ Clear and interactive visualizations
5. ✅ Organized and accessible output
6. ⏳ Comprehensive documentation

### Performance
7. ⏳ Fast load times (<2s per view)
8. ⏳ Efficient data processing
9. ⏳ Proper error handling
