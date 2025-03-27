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
- **Output Organization**: Structured output directory for analysis results

## Next Steps
1. Enhance network analysis visualizations:
   - Fix role distribution heatmap
   - Add scrollable tables
   - Improve data presentation
2. Develop additional analyses:
   - Genre trends
   - Studio performance
   - Success patterns
3. Create comprehensive documentation
4. Train team on analysis tools

See TASKLIST.md for detailed implementation plan.

Last updated: March 26, 2025