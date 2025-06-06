# TV Series Database & Analysis Project

## Project Overview
This project manages and analyzes straight-to-series television orders to inform content development and sales strategies. The database currently contains approximately 450+ straight-to-series sales orders.

## Table of Contents

1. [Project Architecture](#project-architecture)
   - [Data Model](#data-model)
   - [Implementation](#implementation)

2. [Data Layer](#data-layer)
   - [Database Structure](#database-structure)
   - [Data Flow](#data-flow)
   - [Data Processing](#data-processing)

3. [Dashboard](#dashboard)
   - [Components](#components)
   - [Visualization System](#visualization-system)

4. [Development Guide](#development-guide)
   - [Prerequisites](#prerequisites)
   - [Local Setup](#local-setup)
   - [Development Workflow](#development-workflow)

5. [Current Status](#current-status)
   - [Component Development](#component-development)

## Project Architecture

This project is structured as a data pipeline and analysis system with three main components:

### Data Model
A three-layer system that separates:
1. Storage: Google Sheets backend for raw data entry and validation, integrated with TMDB for show metadata
2. Processing: Python analysis pipeline using pandas, with TMDB data enrichment
3. Presentation: Streamlit dashboard with Plotly visualizations

### External Data Sources
1. **TMDB Integration**
   - Show metadata validation and enrichment
   - Genre standardization using TMDB's official genre system
   - Automated ID linking and data synchronization

### Implementation
Code organization follows the three-layer architecture:

1. **Data Storage & Integration**
   - **Python Layer** (`src/data_processing/`)
     - `analyze_shows.py`: Central data loading and preprocessing
       - `fetch_data()`: Single source of truth for data loading
       - Maintains critical column differences ('shows' vs 'show_name')
       - Handles caching, cleaning, and validation
       - Used by all analyzers via `shows_analyzer.fetch_data()`
     - `sheets/`: Google Sheets integration with read/write capabilities
     - `external/tmdb/`: TMDB API client and data synchronization

2. **Analysis Layer**
   - Analyzers receive preprocessed data from `analyze_shows.py`
   - Focus purely on analysis logic, not data loading
   - Examples:
     - `creative_networks/connections_analyzer.py`
     - `content_strategy/genre_analyzer.py`
     - `market_analysis/market_analyzer.py`
     - `validation/`: Data validation rules and lookup tables
     - `cache/`: Local data caching with TTL support
   
   - **Apps Script Layer** (`apps_script/`)
     - Scripts:
       - `SyncTMDBSuccessScore.gs`: Real-time success score sync
       - `AddShowFeature.gs`: Show entry and validation
       - `SearchEditFeature.gs`: Search and edit interface
       - `MenuManager.gs`: Custom menu integration
       - `normalizeStudioNames.gs`: Studio name standardization
       - `AutoUpdateShowNames.gs`: Show name sync
       - `SyncShowNames.gs`: Name consistency checks
       - `MigrateRoles.gs`: Role system updates
     
     - UI Templates:
       - `AddShow.html`: Show entry form
       - `SearchSidebar.html`: Search interface
       - `TeamEditSidebar.html`: Team editing panel
     
     - Triggers:
       - `onOpen`: Initialize custom menu
       - `onEdit`: 
         - Validate data entry
         - Update show names
         - Sync TMDB success scores
       - `onChange`:
         - Studio name normalization
         - Role system updates

2. **Analysis Pipeline** (`src/data_processing/`)
   - `content_strategy/`: Content trends analysis
   - `creative_networks/`: Team and role analysis
   - `market_analysis/`: Network and studio metrics

3. **Visualization** (`src/dashboard/`)
   - `pages/`: Individual dashboard pages
   - `state/`: Page-scoped state management
   - `components/`: Reusable UI components
   - `templates/`: Plotly layouts and styles
   - `app.py`: Streamlit entry point (minimal bootstrap)

## Data Layer

### Data Sources
1. **Google Sheets**
   - Primary data entry and storage
   - Live validation using data validation rules
   - Lookup tables for genre and team data

2. **TMDB Integration**
   - Show metadata validation
   - Official genre categorization
   - Automated data enrichment

### Database Structure
- **Primary Database**: Google Sheets
- **Core Tables**:
  - `shows.csv`: Main series information
  - `show_team.csv`: Team member data (source of truth)
  - `role_types.csv`: Role definitions and hierarchies
  - `network_list.csv`: Network categories and metadata
  - `studio_list.csv`: Studio relationships and data
  - `genre_list.csv`: Primary genre classifications
  - `subgenre_list.csv`: Secondary genre mappings
  - `source_types.csv`: Content source categories
  - `order_types.csv`: Series order classifications
  - `status_types.csv`: Project status tracking

### Data Flow
1. **Data Entry & Validation** (Apps Script)
   - Custom forms for show/team data entry
   - Real-time validation and normalization
   - Automated field updates and cross-references

2. **TMDB Update Pipeline**
   - **Data Pull** (`pull_tmdb_success_metrics_new.py`)
     - Fetch show details from TMDB API
     - Calculate success metrics and scores
     - Map TMDB statuses to internal statuses
     - Generate CSV files:
       - `success_metrics.csv`: TMDB metrics and scores
       - `shows_updates.csv`: Status and metadata updates

   - **Sheet Updates** (`update_tmdb_sheets.py`)
     - Update Success Metrics sheet with TMDB data
     - Batch update Shows sheet with:
       - Notes (show overview)
       - Order type (limited vs ongoing)
       - Status (Active/Development/Cancelled)
       - Episode count (Season 1)
       - Success score (0-100)
     - **Note**: Due to Google Sheets API write quotas (60 requests/minute), large updates should be done through Apps Script instead

   - **Score Sync** (`SyncTMDBSuccessScore.gs`)
     - Apps Script trigger for real-time updates
     - Copy success scores to Shows sheet
     - Maintain data consistency

3. **Processing Pipeline** (`ShowsAnalyzer`)
   - Load from sheets using lookup tables
   - Clean and standardize data:
     - Normalize categorical fields
     - Handle missing values
     - Create derived features
   - Cache results between stages

### Data Processing

#### Pipeline Stages
1. **Data Confidence** (see `docs/analysis/DATA_CONFIDENCE.md`)
   - **Level 1**: Core fields (network, studio, genre, source type, show name)
   - **Level 2**: Team data (roles and associations)
   - **Level 3**: Temporal data (announcement dates)
   - **Level 4**: Secondary classifications (subgenres)
   - **Level 5**: Derived metrics and historical data

2. **Analysis Pipeline** (`src/data_processing/`)
   - `content_strategy/`: Genre and source analysis
   - `creative_networks/`: Team and role analysis
   - `market_analysis/`: Network and studio metrics

3. **Output Types**
   - Processed DataFrames for visualization
   - Cached analysis results
   - Generated insights and metrics

## Dashboard

### Components

1. **Pages** (`src/dashboard/pages/`)
   - Market Snapshot (`1_market_snapshot.py`)
     - Dataset overview and metrics
     - Network distribution analysis
     - Interactive filters and selections
   - Studio Performance (`2_studio_performance.py`)
     - Studio success metrics
     - Performance comparisons
     - Historical trends
   - Unified Dashboard (`3_unified_dashboard.py`)
     - Cross-dimensional analysis
     - Combined metrics view
     - Advanced filtering
   - Market Intel (`4_market_intel.py`)
     - Market trends and patterns
     - Competitive analysis
     - Opportunity identification
   - Network Connections (`5_network_connections.py`)
     - Creator network analysis
     - Multi-network successes
     - Collaboration patterns

2. **State Management** (`src/dashboard/state/`)
   - Page-scoped state via `session.py`
   - Filter persistence per page
   - Shared filter types and utilities

3. **View Components** (`src/dashboard/components/`)
   - Reusable UI elements
   - Chart templates
   - Filter components

### Visualization System
1. **Style Templates** (`templates/defaults/`)
   - Use Plotly's native template system
   - Handle colors, fonts, markers
   - One template per chart type
   - Applied via `update_layout()`

2. **Grid Layouts** (`templates/grids/`)
   - Handle structure via `make_subplots()`
   - Pre-configured row/column layouts
   - Return base figure objects
   - Examples: dual, stacked grids


## Development Guide

### Environment Setup
1. **Source Environment**
   ```bash
   source setup_env.sh
   ```
   This script:
   - Sources environment variables from `.env`
   - Sets up Python aliases
   - Activates virtual environment
   - Adds `src` to PYTHONPATH for proper package imports

2. **Package Structure**
   - Project is set up as a Python package (`setup.py`)
   - All imports should use the package structure
   - Example: `from data_processing.creative_networks import ConnectionsAnalyzer`

3. **Data Access**
   - Raw data: `docs/sheets/STS Sales Database - *.csv`
   - Sheet names configured in `.env`
   - Column names must be preserved (e.g., 'shows' vs 'show_name')

### Best Practices
1. **Data Loading**
   - Always use `analyze_shows.py` for data loading
   - Never normalize column names between sheets
   - Keep data loading separate from analysis logic
   - Document column name expectations

### Development Tools
1. **Code Quality**
   - Type hints and docstrings
   - Unit tests with pytest
   - Code formatting with black

2. **Data Management**
   - Google Sheets API client with rate limiting
   - TMDB API client with caching
   - Data validation and lookup table management
   - Sheet synchronization tools

3. **Documentation**
   - Inline documentation
   - API documentation
   - Usage examples
   - Data flow diagrams

### Page Development
1. **Structure**
   - Each page is a standalone Streamlit app
   - Pages use shared components and state management
   - Follow naming convention: `{number}_{name}.py`

2. **State Management**
   - Use `get_page_state()` for scoped state
   - Define page-specific state classes
   - Maintain filter persistence within pages

3. **Best Practices**
   - Keep page logic separate from view components
   - Use shared filter types where possible
   - Follow error handling patterns
   - Preserve column name differences ('shows' vs 'show_name')

### Prerequisites
- Python 3.8+
- Node.js 14+ (for Apps Script)
- Google Cloud account
- Streamlit account (optional)

### Local Setup
1. **Create Environment**
   ```bash
   python -m venv venv
   pip install -r requirements.txt
   ```

2. **Configuration**
   ```bash
   cp .env.example .env     # Copy template
   vim .env                 # Add credentials
   ```
   Required variables:
   - `GOOGLE_SHEETS_ID`: Database sheet ID
   - `SHOWS_SHEET_NAME`: Shows sheet name
   - `TEAM_SHEET_NAME`: Team sheet name
   - `VENV_PATH`: Path to virtual environment
   - `PYTHON`: Python interpreter
   - `PIP`: Pip executable

3. **Source Environment**
   ```bash
   source setup_env.sh
   ```
   - `GOOGLE_CREDS_PATH`: Service account key
   - `STREAMLIT_*`: Dashboard config

### Development Workflow

#### Chart Development Best Practices

1. **Data Preparation**
   - Convert data to pandas DataFrame early for easier manipulation
   - Sort data before creating charts to control visual hierarchy
   - Use DataFrame operations (sort_values, reindex) instead of manual list building
   - Ensure data is in the right shape before visualization (e.g., wide vs long format)

2. **Chart Configuration**
   - Store common chart settings in `style_config.py`
   - Use consistent color scales across related visualizations
   - Set fixed dimensions based on data size (e.g., cell_size * num_rows)
   - Place axis labels strategically (e.g., x-axis on top for heatmaps)

3. **Interactive Features**
   - Customize hover templates for clear data presentation
   - Use hover_text for rich tooltips with multiple data points
   - Set fixedrange=True to prevent unwanted zoom/pan
   - Adjust margins and spacing for better readability

4. **Layout Management**
   - Use st.columns for responsive multi-chart layouts
   - Wrap charts in containers with fixed heights
   - Match chart heights within the same row
   - Consider aspect ratio for different screen sizes

#### Development Steps

1. **Data Processing**
   ```bash
   python -m src.data_processing.analyze_shows  # Test pipeline
   python -m pytest src/tests/                  # Run tests
   ```

2. **Dashboard Development**
   ```bash
   streamlit run src/dashboard/app.py          # Run dashboard
   ./scripts/restart_streamlit.sh              # Auto-reload
   ```

3. **Apps Script Development**
   ```bash
   npm install -g @google/clasp                # Install tools
   clasp login                                # Auth with Google
   cd apps_script && clasp pull               # Get changes
   clasp push                                 # Deploy changes
   ```

### Running the Project
1. **Dashboard (Production)**
   ```bash
   streamlit run src/dashboard/app.py
   ```
   Available at http://localhost:8501

2. **Dashboard (Development)**
   ```bash
   ./scripts/restart_streamlit.sh  # Auto-reload on changes
   ```
  
### Testing
1. **Unit Tests**
   ```bash
   python -m pytest src/tests/
   ```

2. **Component Testing**
   ```bash
   python -m src.tests.dashboard.templates.preview_grid [grid_type]
   ```

### Common Issues
1. **ModuleNotFoundError**
   - Check virtual environment
   - Verify package installation
   - Check Python path

2. **Process Management**
   ```bash
   ps aux | grep python  # List processes
   kill <PID>           # Clean stop
   ```

### Reference Documentation

#### Analysis Framework
- `docs/analysis/STS_ANALYSIS_FRAMEWORK.md`: Core analysis methodology
- `docs/analysis/DATA_CONFIDENCE.md`: Data quality and confidence levels

#### Development Guides
- `DIRECTORY_STRUCTURE.md`: Complete project layout and organization
- `docs/development/STYLE_GUIDE.md`: Code style and best practices
- `docs/development/TEMPLATE_SYSTEM.md`: Visualization template guide

#### Project Status
- `STATUS.md`: Current development status and roadmap
- `TASKLIST.md`: Upcoming tasks and improvements

## Current Status

### Component Development
1. Genre Analysis
  - [ ] Design grid layout
  - [ ] Implement component
  - [ ] Add tests

2. Network Analysis
  - [ ] Design grid layout
  - [ ] Implement component
  - [ ] Add tests

See `TASKLIST.md` for complete roadmap.

Last updated: March 31, 2025