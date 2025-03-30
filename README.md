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
1. Storage: Google Sheets backend for raw data entry and validation
2. Processing: Python analysis pipeline using pandas and ydata-profiling
3. Presentation: Streamlit dashboard with Plotly visualizations

### Implementation
Code organization follows the three-layer architecture:

1. **Data Storage** (`src/data_processing/`)
   - `sheets/`: Google Sheets integration
   - `validation/`: Data validation rules
   - `cache/`: Local data caching

2. **Analysis Pipeline** (`src/data_processing/`)
   - `content_strategy/`: Content trends analysis
   - `creative_networks/`: Team and role analysis
   - `market_analysis/`: Network and studio metrics

3. **Visualization** (`src/dashboard/`)
   - `components/`: Reusable UI components
   - `templates/`: Plotly layouts and styles
   - `app.py`: Streamlit entry point

## Data Layer

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

2. **Processing Pipeline** (`ShowsAnalyzer`)
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

1. **Market Snapshot**
   - Dataset Overview
     - Total shows, creatives, networks, roles
     - Interactive filters and selections
     - Data scope and limitations
   - Network Distribution
     - Market share visualization
     - Network performance metrics
     - Trend analysis

2. **Genre Analysis**
   - Genre breakdown by network
   - Temporal genre trends
   - Cross-genre patterns
   - Source type correlations

3. **Source Analysis**
   - Original vs adaptation ratios
   - Source material patterns
   - Network preferences
   - Success metrics by source

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

### Prerequisites
- Python 3.8+
- Node.js 14+ (for Apps Script)
- Google Cloud account
- Streamlit account (optional)

### Local Setup
1. **Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configuration**
   ```bash
   cp .env.example .env     # Copy template
   vim .env                 # Add credentials
   ```
   Required credentials:
   - `GOOGLE_SHEETS_ID`: Database sheet
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

Last updated: March 29, 2025