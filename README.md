# TV Series Database & Analysis Project

## Project Overview
This project manages and analyzes straight-to-series television orders to inform content development and sales strategies. The database currently contains approximately 400 straight-to-series sales orders.

## Implementation Architecture

### Data Storage
- **Primary Database**: Google Sheets
- **Sheet Structure**:
  - `shows`: Main data table for series information
    - Contains a `key_creatives` display field that mirrors team member data
  - `show_team`: Source of truth for key creative team members
    - Team members are stored here with roles and order
    - Changes here automatically update the `key_creatives` field in `shows`
  - Various lookup tables (networks, studios, genres, etc.)

### Data Model
- `show_team` is the source of truth for team member data
- `key_creatives` in the `shows` sheet is a display-only field
- When team members are added/edited:
  1. Data is saved to `show_team`
  2. `key_creatives` is automatically updated from `show_team`
  3. Never modify `key_creatives` directly, it's derived from `show_team`

### Code Structure

The codebase follows a siloed architecture where each major feature is self-contained to prevent changes in one area from affecting others.

### Setup and Logging
- `setup_env.sh`: Environment setup script for configuring Python environment and dependencies
- `logs/`: Directory containing application logs
  - `sheets_api.log`: Detailed logs of Google Sheets API interactions

#### Feature Modules

##### Add Show Feature
- `AddShow.html`: Client-side form UI
- `AddShowFeature.gs`: Server-side logic for adding new shows

##### Search & Edit Feature
- `SearchSidebar.html`: Search interface
- `ShowEditForm.html`: Edit form UI
- `SearchEditFeature.gs`: Server-side logic for search and edit

##### Core Configuration
- `MenuManager.gs`: Menu configuration and global settings

### Version Control
- `v1_archive/`, `v3_archive/`: Contains backup versions of stable code
- Each feature module is backed up independently with `.backup` suffix
- Changes are isolated to specific features to maintain stability

### Key Features
- ✓ Add new shows with team members
- ✓ Search shows database
- ✓ Edit existing shows
- ✓ Studio name normalization
- ✓ Date field handling
- ✓ Team member management with roles
- ✓ Sheet-specific feature validation

### Design Principles
1. **Feature Isolation**: Each feature is self-contained with its own UI and logic
2. **Backup First**: Stable versions are archived before major changes
3. **Consistent Data Handling**: Normalized field names and data formats across features
4. **Defensive Programming**: Validation and error handling at both client and server side
5. **Context-Aware Features**: Features only activate on appropriate sheets

### Implementation Status
- ✅ Team member management with roles
- ✅ Data validation and error handling
- ✅ Studio name standardization
- ✅ Loading states and user feedback
- ✅ Sheet-specific feature validation
- ✅ Creative network analysis and visualization
- ✅ Structured output organization

## Development Phases

### Phase 1 (Current)
- **Database**: Google Sheets
- **Interface**: Google Apps Script forms
- **Data Entry**: Maintained through current system

### Phase 2 (In Progress)
- **Database**: Remains on Google Sheets
- **Analysis**: Python-based data processing and network analysis
- **Visualization**: Interactive HTML visualizations using Plotly
- **Integration**: Direct Google Sheets connection via gspread

### Analysis Output Process
1. **Data Processing**
   - Raw data fetched from sheets → `src/cache/raw_data/`
   - Processed data → `src/cache/processed/`
   - Analysis results → `src/cache/analysis/`

2. **Analysis Output Structure**
   Each analysis module follows this pattern:
   ```
   /output/network_analysis/
   ├── {analysis_type}/
   │   ├── data/              # JSON data files
   │   │   ├── summary.json   # High-level metrics
   │   │   └── details.json   # Detailed analysis data
   │   ├── figures/           # Static visualizations
   │   │   ├── overview.html  # Main visualization
   │   │   └── details/       # Drill-down visualizations
   │   └── report.html        # Analysis narrative and insights
   ```

3. **Visualization Standards**
   - All interactive plots use Plotly
   - Consistent color scheme from `src/dashboard/utils/style_config.py`
   - Standard layout templates in `src/dashboard/utils/plot_templates.py`
   - All figures include download buttons
   - All tables are sortable and filterable

## Current Development Focus

### Role Analysis Refinement
- Fixing role data normalization to properly handle compound roles
- Enhancing role distribution analysis for single vs multi-role creators
- Improving network role preference visualization
- Removing role progression analysis (not providing value)

### Implementation Details
- Role data stored in `show_team` sheet with compound roles (e.g., "director, writer")
- Role types defined in `STS Sales Database - role_types.csv`
- Role normalization implemented in `src/data_processing/creative_networks/role_analysis.py`
- Core data loading in `src/data_processing/analyze_shows.py`

### Known Issues
- Role normalization needs improvement for compound roles
- Network preferences for multi-role creators not properly represented
- Some role abbreviations may be missed

## Next Steps
1. Complete role analysis improvements:
   - Fix role normalization for compound roles
   - Implement single vs multi-role analysis
   - Update network preference visualizations
2. Clean up codebase organization:
   - Move core analysis into dedicated module
   - Consolidate dashboard utilities
   - Organize analysis modules into proper directories
3. Create comprehensive documentation
4. Train team on analysis tools

See TASKLIST.md for detailed implementation plan.

Last updated: March 26, 2025