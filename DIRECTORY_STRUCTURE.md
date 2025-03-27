# Directory Structure

```
/GoogleDB
├── README.md                    # Project overview and documentation
├── TASKLIST.md                 # Implementation plan and progress
├── DIRECTORY_STRUCTURE.md      # This file
├── requirements.txt            # Python dependencies
├── setup_env.sh               # Environment setup script
├── .env.example               # Example environment variables
│
├── /apps_script               # Google Apps Script files
│   ├── AddShow.html          # Add show form template
│   ├── AddShowFeature.gs     # Add show functionality
│   ├── MenuManager.gs        # Menu management
│   ├── SearchEditFeature.gs  # Search and edit functionality
│   ├── SearchSidebar.html    # Search sidebar template
│   ├── TeamEditSidebar.html  # Team management sidebar
│   ├── /archive             # Old versions archive
│   ├── /v1_archive          # Version 1 archive
│   ├── /v2_archive          # Version 2 archive
│   └── /v3_archive          # Version 3 archive
│
├── /docs                      # Documentation and data files
│   ├── STS Sales Database.pdf # Database documentation
│   ├── google_sheets_setup.md # Setup instructions
│   ├── /sheets              # Google Sheets exports/backups (CSV)
│   └── /user_guides         # User documentation
│       └── USER_GUIDE.md    # Main user guide for database features
│
├── /logs                     # Application logs
│   └── sheets_api.log       # Google Sheets API interaction logs
│
├── /src
│   ├── /cache              # Cache directory
│   ├── /config             # Python configuration
│   │   ├── logging_config.py
│   │   └── sheets_config.py
│   ├── /data_processing         # Data processing and analysis
│   │   ├── analyze_shows.py     # Core data analysis utilities
│   │   ├── export_shows.py      # Data export functionality
│   │   ├── verify_setup.py      # Setup verification utility
│   │   ├── /content_strategy    # Content strategy analysis
│   │   │   ├── genre_analysis.py
│   │   │   └── source_analysis.py
│   │   ├── /creative_networks   # Creative network analysis
│   │   │   ├── relationship_analysis.py
│   │   │   ├── collaboration_patterns.py
│   │   │   └── star_power_analysis.py
│   │   ├── /genre_creative     # Genre-creative correlations
│   │   │   ├── creator_specialization.py
│   │   │   └── success_patterns.py
│   │   └── /studio_analysis    # Studio performance analysis
│   │       ├── independent_performance.py
│   │       └── network_relationships.py
│   ├── /dashboard         # Streamlit dashboard
│   │   ├── app.py        # Main dashboard application
│   │   ├── /components   # Dashboard components
│   │   │   ├── source_analysis.py
│   │   │   ├── network_analysis.py
│   │   │   └── trend_analysis.py
│   │   └── /utils        # Helper functions
│   │       ├── sheets_client.py
│   │       ├── sheets_connection.py
│   │       └── data_processing.py
│   └── /tests            # Test files
│       ├── conftest.py
│       ├── test_config.py
│       ├── test_connection_stability.py
│       ├── test_dashboard_components.py
│       ├── test_data_processing.py
│       ├── test_sheet_import.py
│       ├── test_sheets_auth.py
│       ├── test_sheets_connection.py
│       └── /test_data    # Test data files
│           ├── /csv_samples
│           └── /sheets_responses
│
├── /output                  # Analysis outputs and visualizations
│   └── /network_analysis     # Network analysis results
│       └── /creative_networks # Creative network visualizations
│           └── relationship_analysis.html
│
└── /config                  # Configuration files
    └── sheets_config.json   # Google Sheets configuration
```

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
