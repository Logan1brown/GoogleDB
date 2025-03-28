# Directory Structure

GoogleDB/
    README.md                    # Project overview and documentation
    TASKLIST.md                 # Implementation plan and progress
    DIRECTORY_STRUCTURE.md      # This file
    requirements.txt            # Python dependencies
    setup_env.sh               # Environment setup script
    .env.example               # Example environment variables

    apps_script/               # Google Apps Script files
        AddShow.html          # Add show form template
        AddShowFeature.gs     # Add show functionality
        MenuManager.gs        # Menu management
        SearchEditFeature.gs  # Search and edit functionality
        SearchSidebar.html    # Search sidebar template
        TeamEditSidebar.html  # Team management sidebar
        archive/             # Old versions archive
        v1_archive/          # Version 1 archive
        v2_archive/          # Version 2 archive
        v3_archive/          # Version 3 archive

    docs/                      # Documentation and data files
        analysis/            # Analysis documentation
            DATA_CONFIDENCE.md    # Data quality assessment
            NETWORK_ANALYSIS.md   # Network analysis guide
            STS_ANALYSIS_FRAMEWORK.md # Analysis methodology
        development/         # Development guides
            STYLE_GUIDE.md       # Visual styling standards
            TEMPLATE_SYSTEM.md   # Template architecture
        sheets/              # Lookup tables and exports
            STS Sales Database - network_list.csv
            STS Sales Database - studio_list.csv
            STS Sales Database - genre_list.csv
            STS Sales Database - role_types.csv
            STS Sales Database - source_types.csv
        user_guides/         # User documentation
            USER_GUIDE.md    # Main user guide for features

    logs/                     # Application logs
        sheets_api.log       # Google Sheets API interaction logs

    scripts/                  # Analysis entry points
        analyze_content.py    # Content analysis script
        analyze_genres.py     # Genre analysis script
        analyze_relationships.py # Network relationship script
        analyze_sources.py    # Source analysis script
        generate_profile.py   # Profile generation script

    src/
        cache/              # Cache directory
        config/             # Python configuration
            logging_config.py
            sheets_config.py
        data_processing/         # Data processing and analysis
            analyze_shows.py     # Core data analysis utilities
            content_analysis.py  # Content analysis module
            export_shows.py      # Data export functionality
            verify_setup.py      # Setup verification utility
            content_strategy/    # Content strategy analysis
                genre_analysis_2.py
                source_analysis.py
            creative_networks/   # Creative network analysis
                network_connections.py # Network connection analysis
                role_analysis.py    # Role distribution analysis
            genre_creative/     # Genre-creative correlations
            studio_analysis/    # Studio performance analysis
        dashboard/         # Streamlit dashboard
            app.py        # Main dashboard application
            templates/    # Plotly native templates
                __init__.py          # Registers templates with Plotly
                base.py             # Single base template with brand styles
                defaults/           # Chart type defaults
                    bar.py         # Bar chart defaults (colors, hovers)
                    heatmap.py     # Heatmap defaults (colorscales)
                    scatter.py     # Scatter defaults (markers, lines)
                    table.py       # Table defaults (header styles)
                    sankey.py      # Network flow defaults
                grids/             # Grid layout templates
                    # Basic Layouts
                    chart_only.py          # Single chart
                    chart_table.py         # Chart + table
                    chart_dual_table.py    # Chart + two tables
                    chart_insights.py      # Chart + key findings
                    chart_insights_table.py # Chart + findings + table
                    
                    # Analysis Layouts
                    market_snapshot.py      # Market analysis dashboard

            components/   # Dashboard components
                snapshot_dashboard.py    # Market snapshot dashboard
                content_analysis.py      # Genre and source analysis
                network_analysis.py      # Creative network analysis
                relationship_analysis.py # Creative relationship analysis
                studio_analysis.py       # Studio performance analysis
            utils/        # Helper functions
                style_config.py          # Style constants (colors, fonts)
                sheets_client.py         # Sheets API client
                sheets_connection.py     # Sheets connection manager
                data_processing.py       # Data processing utilities
                templates/               # OLD: To be removed after migration
                    base.py              # Base template + layouts
                    insight.py           # Insight slide templates
                    network_analysis.py  # Network viz templates
                    market_overview.py   # Market data templates
                    dual_analysis.py     # Multi-chart templates
        tests/            # Test files
            conftest.py
            test_config.py
            test_connection_stability.py
            test_dashboard_components.py
            test_data_processing.py
            test_sheet_import.py
            test_sheets_auth.py
            test_sheets_connection.py
            test_data/    # Test data files
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

1. **Keep Related Files Together**:
    - Dashboard components in `/src/dashboard/components`
    - Analysis utilities in `/src/dashboard/utils`
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
