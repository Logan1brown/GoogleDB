# Multipage Dashboard Structure

## Overview
The dashboard now uses a multipage architecture for better organization and state management.

## Directory Structure
```
src/dashboard/
├── app.py              # Main entry point
├── pages/             # Individual page files
│   ├── __init__.py
│   ├── 1_market_snapshot.py
│   ├── 2_studio_performance.py
│   ├── 3_unified_dashboard.py
│   ├── 4_market_intel.py
│   └── 5_network_connections.py
├── state/             # State management
│   ├── __init__.py
│   └── session.py
├── components/        # Reusable view components
└── templates/         # Chart templates
```

## State Management
Each page has its own scoped state namespace to prevent interference:
```python
# Example: Getting page-specific state
state = get_page_state("market_snapshot")
if "market" not in state:
    state["market"] = asdict(MarketState())
```

## Page Structure
Each page follows this template:
1. Import required components and state utilities
2. Define page-specific state dataclass
3. Initialize data and analyzers
4. Update state with current filter values
5. Render view components

## Important Notes
- Column names are preserved as per data standards:
  - shows sheet: uses 'shows' column
  - show_team sheet: uses 'show_name' column
- Each page maintains its own filter state
- Components are reused across pages
- Error handling is consistent across all views
