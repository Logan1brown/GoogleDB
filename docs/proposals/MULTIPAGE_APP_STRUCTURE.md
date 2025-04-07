# Multipage App Structure Proposal

## Current Issues

1. **State Management**
   - Global state leakage between views due to sidebar navigation
   - Filters inadvertently affect multiple views
   - Session state is shared across all views

2. **Navigation**
   - Using sidebar selectbox for navigation
   - No proper URL routing
   - No deep linking capability
   - Poor user experience when navigating between views

3. **Code Organization**
   - All views loaded at once
   - Mixed concerns in app.py
   - No clear separation between pages and components

## Proposed Solution

### 1. Streamlit Multipage Structure

📁 src/dashboard/
├── app.py           # Main entrypoint (minimal)
├── pages/           # NEW: Each file is a page
│   ├── 1_market_snapshot.py
│   ├── 2_studio_performance.py
│   ├── 3_unified_dashboard.py
│   └── 4_market_intel.py
├── components/      # EXISTING: View components
│   ├── market_view.py
│   ├── studio_view.py
│   └── unified_view.py
├── templates/       # EXISTING: Keep as is
│   ├── defaults/   # Chart configurations
│   └── grids/      # Grid layouts
├── utils/          # EXISTING: Utility functions
└── state/          # NEW: State management
    ├── __init__.py
    └── session.py
```

### 2. Key Improvements

#### a. Page Isolation
- Each page gets its own URL (e.g., `/market-snapshot`, `/studio-performance`)
- Pages load independently
- State is scoped to each page by default
- Clear separation of concerns

#### b. State Management
```python
# state/session.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class FilterState:
    source_type: Optional[str] = None
    genre: Optional[str] = None

def get_page_state(page_name: str) -> FilterState:
    """Get state for a specific page."""
    if f"state_{page_name}" not in st.session_state:
        st.session_state[f"state_{page_name}"] = FilterState()
    return st.session_state[f"state_{page_name}"]
```

#### c. Reusable Components
```python
# components/filters/source_filter.py
def render_source_filter(key_prefix: str) -> str:
    """Render source type filter with page-specific key."""
    return st.selectbox(
        "Source Type",
        options=["Original", "Book", "IP"],
        key=f"{key_prefix}_source_type"
    )
```

#### d. Layout Patterns
```python
# components/layout/two_column.py
@contextmanager
def two_column_layout(left_ratio: int = 1, right_ratio: int = 3):
    """Standard two-column layout pattern."""
    cols = st.columns([left_ratio, right_ratio])
    with cols[0] as left_col, cols[1] as right_col:
        yield left_col, right_col
```

### 3. Implementation Plan

1. **Phase 1: Add New Structure** (No Moving Yet)
   - Create `pages/` directory
   - Create `state/` directory and session management
   - Add minimal `app.py` template

2. **Phase 2: Move Navigation Logic**
   - Create page files for each view:
     ```python
     # pages/1_market_snapshot.py
     import streamlit as st
     from components.market_view import render_market_snapshot
     
     st.title("Market Snapshot")
     shows_df, team_df = shows_analyzer.fetch_data()
     render_market_snapshot(market_analyzer)
     ```
   - Move each view's initialization from `app.py` to its page file
   - Keep view rendering logic in components/

3. **Phase 3: Add State Management**
   - Create state utilities:
     ```python
     # state/session.py
     def get_page_state(page_name: str):
         key = f"state_{page_name}"
         if key not in st.session_state:
             st.session_state[key] = {}
         return st.session_state[key]
     ```
   - Update pages to use scoped state
   - Test state isolation

4. **Phase 4: Clean Up**
   - Remove navigation code from `app.py`
   - Keep only:
     - CSS/styling
     - Data initialization
     - Error handling
   - Verify all pages work independently

5. **Phase 5: Testing & Documentation**
   - Test all pages with new structure
   - Verify no state leakage
   - Update documentation

### 4. Benefits

1. **Developer Experience**
   - Clear file organization
   - Easier to maintain
   - Better code reuse
   - Simpler testing

2. **User Experience**
   - Faster page loads
   - Proper URLs
   - Better navigation
   - State persistence per page

3. **Performance**
   - Lazy loading of pages
   - Reduced memory usage
   - Better caching potential

### 5. Migration Strategy

1. Create new structure alongside existing code
2. Migrate one page at a time
3. Test thoroughly after each migration
4. Remove old code once verified
5. Update documentation

### 6. Risks and Mitigations

1. **Risk**: Session state migration
   - **Mitigation**: Create utility functions to handle state transition

2. **Risk**: Breaking changes
   - **Mitigation**: Maintain old routes temporarily

3. **Risk**: Performance impact
   - **Mitigation**: Monitor and optimize as needed

## Next Steps

1. Review and approve proposal
2. Create project branch
3. Implement directory structure
4. Begin page migration
5. Test and validate
