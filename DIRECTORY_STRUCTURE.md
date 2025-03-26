# Directory Structure

```
/GoogleDB
├── README.md                    # Project overview and documentation
├── TASKLIST.md                 # Implementation plan and progress
├── DIRECTORY_STRUCTURE.md      # This file
├── requirements.txt            # Python dependencies
├── setup_env.sh               # Environment setup script
│
├── /apps_script               # Google Apps Script files
│   ├── AddShow.html          # Add show form template
│   ├── AddShowFeature.gs     # Add show functionality
│   ├── MenuManager.gs        # Menu management
│   ├── SearchEditFeature.gs  # Search and edit functionality
│   ├── SearchSidebar.html    # Search sidebar template
│   ├── ShowEditForm.html     # Show edit form template
│   └── /v1_archive          # Archived version 1 files
│
├── /docs                      # Documentation and data files
│   ├── /sheets              # Google Sheets exports/backups (CSV files)
│   └── /user_guides         # Usage documentation
│
├── /logs                     # Application logs
│   └── sheets_api.log       # Google Sheets API interaction logs
│
├── /src
│   ├── /data_processing     # Data processing scripts
│   │   ├── export_shows.py  # Data export functionality
│   │   ├── analyze_shows.py # Data analysis
│   │   └── verify_setup.py  # Setup verification utility
│   │
│   ├── /dashboard          # Streamlit dashboard
│   │   ├── app.py         # Main dashboard application
│   │   ├── /components    # Dashboard components
│   │   │   ├── source_analysis.py
│   │   │   ├── network_analysis.py
│   │   │   └── trend_analysis.py
│   │   └── /utils         # Helper functions
│   │       ├── sheets_connection.py
│   │       └── data_processing.py
│   │
│   └── /tests             # Test files
│       ├── test_analysis.py
│       └── test_dashboard.py
│
└── /config                 # Configuration files
    ├── credentials.json    # Google Sheets API credentials
    ├── sheets_config.json  # Google Sheets configuration
    └── .env.example        # Example environment variables
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
