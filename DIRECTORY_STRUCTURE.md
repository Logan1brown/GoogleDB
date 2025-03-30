# Directory Structure

## File Naming Conventions

1. **Analysis Files** (in src/data_processing/):
   - Named with suffix '_analyzer.py'
   - Focus on data processing and analysis
   - Examples: market_analyzer.py, genre_analyzer.py

2. **View Files** (in src/dashboard/components/):
   - Named with suffix '_view.py'
   - Focus on visualization and UI
   - Examples: market_view.py, genre_view.py

## Directory Layout

GoogleDB/
    # Core Documentation
    README.md                # Project overview
    TASKLIST.md             # Current tasks and roadmap
    STATUS.md               # Project status
    RETROSPECTIVE.md        # Project learnings
    DIRECTORY_STRUCTURE.md  # Directory guide

    # Configuration
    requirements.txt        # Python dependencies
    setup_env.sh           # Environment setup
    .env.example           # Environment template
    .env                   # Active environment
    .gitignore             # Git ignore rules
    test_app.py            # Main test runner

    # Environment & Settings
    .streamlit/            # Streamlit config
        config.toml        # Dashboard settings
    .pytest_cache/         # Test cache
    cache/                 # Data cache
    venv/                  # Virtual env

    # System Configuration
    config/                # App settings
        .env.example       # Config template
        credentials.json   # API credentials
        sheets_config.json # Sheets settings

    # Output & Logs
    output/                # Generated files
        network_analysis/  # Network diagrams
        visualizations/    # Chart outputs
        test_basic_plot.html # Test output
    logs/                  # Log files
        sheets_api.log     # API interaction logs

    # Documentation
    docs/
        analysis/
            DATA_CONFIDENCE.md         # Data quality guide
            STS_ANALYSIS_FRAMEWORK.md  # Analysis methodology
        development/
            STYLE_GUIDE.md            # Visual standards
            TEMPLATE_SYSTEM.md        # Template architecture
        google_sheets_setup.md      # Sheets integration guide
        sheets/                     # Data files
            # Core Data Files (Actively Used)
            STS Sales Database - shows.csv        # Main show data
            STS Sales Database - show_team.csv    # Team member data
            STS Sales Database - role_types.csv   # Role definitions
            
            # Reference Lists
            STS Sales Database - genre_list.csv    # Valid genres
            STS Sales Database - network_list.csv  # Valid networks
            STS Sales Database - source_types.csv  # Valid sources
            STS Sales Database - status_types.csv  # Valid statuses
            STS Sales Database - studio_list.csv   # Valid studios
            STS Sales Database - subgenre_list.csv # Valid subgenres
        user_guides/
            USER_GUIDE.md            # Usage documentation

    # Apps Script Archives
    apps_script/              # Google Apps Script code archives
        archive/             # General archive
        v1_archive/          # Version 1 backup
        v2_archive/          # Version 2 backup
        v3_archive/          # Version 3 backup

    # Scripts
    scripts/                 # Analysis runners and utilities
        analysis/           # Analysis entry points
            analyze_content.py     # Content analysis runner
            analyze_genres.py      # Genre pattern analysis
            analyze_sources.py     # Source type analysis
            analyze_relationships.py # Network analysis
        
        utils/             # Utility scripts
            generate_profile.py    # Profile generation
            restart_streamlit.sh   # Dashboard restart

    # Tests
    tests/
        scripts/          # Script tests
            test_basic_plot.py   # Basic plot tests
            test_sunburst.py    # Sunburst chart tests

    src/
        config/             # Python configuration
            logging_config.py  # Logging settings
            server_config.py   # Server configuration
            sheets_config.py   # Sheets API configuration
            role_config.py     # Shared role definitions

        data_processing/    # Data processing and analysis
            analyze_shows.py  # Core data fetching and processing
            content_analysis.py  # Legacy content analysis (to be refactored)
            
            content_strategy/ # Content strategy analysis
                genre_analyzer.py   # Genre pattern analysis
                source_analyzer.py  # Source type analysis
            
            creative_networks/ # Team and role analysis
                role_analysis.py  # Role patterns and team composition
            
            market_analysis/  # Market performance
                market_analyzer.py  # Market metrics and trends

        dashboard/         # Streamlit dashboard
            app.py        # Main dashboard entry point
            
            components/   # Dashboard views (UI components)
                market_view.py   # Market overview UI
                genre_view.py    # Genre analysis UI
                source_view.py   # Source analysis UI
            
            templates/    # Reusable chart templates
                defaults/  # Chart styling defaults
                    bar.py      # Bar chart styles
                    heatmap.py  # Heatmap styles
                grids/    # Layout templates
                    chart_only.py  # Single chart layout
            
            utils/       # Helper utilities
                data_processing.py   # Data transforms
                sheets_client.py     # Sheets API wrapper
                sheets_connection.py # Connection manager
                style_config.py      # Style constants

        data_processing/         # Data analysis
            analyze_shows.py      # Core analysis
            content_analysis.py   # Content metrics
            export_shows.py       # Data export
            verify_setup.py       # Setup checks
            content_strategy/     # Content analysis
                genre_analysis.py
                genre_analysis_2.py
                source_analysis.py
            creative_networks/    # Network analysis
                network_connections.py
                network_graph.py
                network_sharing_analysis.py
                role_analysis.py
            market_analysis/     # Market metrics
                market_trends.py
                market_share.py
            studio_analysis/     # Studio analysis

        tests/                  # Test suite
            # Core Tests
            conftest.py          # Test configuration
            test_config.py       # Config tests
            test_connection_stability.py  # Connection tests
            test_dashboard_components.py  # UI tests
            test_data_processing.py      # Processing tests
            test_sheet_import.py         # Import tests
            test_sheets_auth.py          # Auth tests
            test_sheets_connection.py    # API tests

            # Test Resources
            dashboard/          # Dashboard tests
                templates/      # Template tests
            test_data/         # Test datasets
                csv_samples/    # Sample CSV files
                sheets_responses/ # Mock API responses
                csv_samples/
                sheets_responses/

    output/                  # Analysis outputs and visualizations
        network_analysis/     # Network analysis results
            content_strategy/  # Content strategy analysis
            creative_networks/ # Creative network analysis
            creative_relationships/ # Creator relationships
            genre_creative/    # Genre correlations
            studio_performance/ # Studio analysis
        visualizations/      # Generated visualizations

    config/                  # Configuration files
        sheets_config.json   # Google Sheets configuration

## Directory Guidelines

1. **Analysis vs. View Separation**:
   - Analysis logic goes in `data_processing/` with '_analyzer.py' suffix
   - UI components go in `dashboard/components/` with '_view.py' suffix
   - Each view file has a corresponding analyzer file

2. **Module Organization**:
   - content_strategy/ - Content-focused analysis (genres, sources)
   - creative_networks/ - Team and role analysis
   - market_analysis/ - Market performance metrics

3. **Template Usage**:
   - Basic chart styles in `templates/defaults/`
   - Layout templates in `templates/grids/`
   - Only keep actively used templates
    - Tests alongside their respective modules

2. **Configuration Management**:
    - All configs in `/config`
    - No hardcoded paths or credentials
    - Use environment variables

3. **Documentation**:
    - User guides in `/docs/user_guides`
    - Sheet backups in `/docs/sheets`
    - Keep README.md updated

4. **Development Rules**:
    - Create new files in appropriate directories
    - No loose files in root directory
    - Follow existing naming conventions
    - Keep paths relative to project root

## Future Organization Notes

1. **Core Analysis Module Restructuring**:
    - Move `analyze_shows.py` into `/src/data_processing/core/`
    - Move `export_shows.py` into `/src/data_processing/core/`
    - This better separates core functionality from analysis modules

2. **Script Consolidation**:
    - Current `/scripts` directory has analysis entry points that partially duplicate module functionality
    - Consider moving script logic into respective modules
    - Keep only minimal entry point code in scripts

3. **Dashboard Utils Cleanup**:
    - Merge `sheets_client.py` and `sheets_connection.py`
    - They have overlapping functionality and should be consolidated

4. **Analysis Module Organization**:
    - Move `content_analysis.py` into `/content_strategy/`
    - Each analysis type should live in its dedicated subdirectory

5. **Test Organization**:
    - Currently all tests are in `/src/tests/`
    - Consider moving tests closer to their respective modules
    - Keep test data in central `/src/tests/test_data/`

Note: These changes should be made carefully and systematically after current analysis tasks are complete to avoid disrupting ongoing work.
