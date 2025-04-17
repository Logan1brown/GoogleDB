# Legacy Code Archive

This directory contains deprecated code that has been archived for reference. This code is no longer actively used in the project but is preserved for historical context and documentation purposes.

## Contents

### Google Sheets Integration (Pre-Supabase)
Previously, the project used Google Sheets as its primary data store before migrating to Supabase. Related code has been moved here from:
- `/docs/sheets/` → `/legacy/sheets/`
- `/src/config/sheets_config.py` → `/legacy/src/config/`
- Sheets-related utilities and tests → `/legacy/src/`
- `/config/sheets_config.json` → `/legacy/config/`

### Google Apps Script
Google Apps Script code from when the project used Google Sheets:

#### Main Features
- `AddShow.html`, `AddShowFeature.gs`: Show addition interface and logic
- `SearchEditFeature.gs`, `SearchSidebar.html`: Search and edit functionality
- `TeamEditSidebar.html`: Team editing interface
- Various utility scripts (MenuManager.gs, AutoUpdateShowNames.gs, etc.)

#### Historical Versions
Older versions of the implementation:
- `/apps_script/v1_archive/` → `/legacy/apps_script/v1/`
- `/apps_script/v2_archive/` → `/legacy/apps_script/v2/`
- `/apps_script/v3_archive/` → `/legacy/apps_script/v3/`

## Important Notes
1. This code is not maintained and may reference outdated APIs or dependencies
2. Credentials and sensitive data have been removed
3. This code should not be used in production
4. For current implementation, refer to the main project directories
