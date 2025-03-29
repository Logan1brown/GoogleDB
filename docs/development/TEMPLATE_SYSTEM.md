# Visualization Architecture

## Overview
Our visualization system follows Plotly's best practices with three distinct layers:

### 1. Base Template Layer (`go.layout.Template`)
- Lives in `templates/defaults/`
- Defines visual styling (fonts, colors, etc.)
- Can have multiple traces for cycling styles
- Applied via template parameter in update_layout
- Example: `bar.py`, `scatter.py`

### 2. Grid Layout Layer (`make_subplots`)
- Lives in `templates/grids/`
- Defines structure only (rows, cols, specs)
- Should NOT contain styling
- Just creates the subplot structure
- Example: `market_snapshot.py`, `dual.py`

### 3. Style Config Layer (`style_config.py`)
- Contains constants used by templates
- No direct styling, just values
- Single source of truth for styles
- Example: colors, fonts, margins

This three-layer separation ensures:
- Clear boundaries between styling and structure
- Consistent look and feel across components
- Easy maintenance and updates
- Proper use of Plotly's template system

## 1. Style Configuration
All style constants are defined in `utils/style_config.py`:
```python
COLORS = {
    'background': '#FFFFFF',
    'accent': 'rgb(55, 83, 109)'
}

FONTS = {
    'primary': {
        'family': 'Source Sans Pro',
        'sizes': {'title': 20, 'body': 14}
    }
}
```

## 2. Preview System

Validate grid layouts before use:
```bash
python -m src.tests.dashboard.templates.preview_grid [grid_type]
```

## Preview System

Using the unified preview script:
```bash
python -m src.tests.dashboard.templates.preview_grid [grid_type]
```

The preview system:
- Lives in `tests/dashboard/templates/preview_grid.py`
- Validates grid layouts before use in components
- Provides sample data for visual testing
- Ensures proper subplot configuration

## Templates & Grids

### Style Defaults (`templates/defaults/*.py`)
```python
# defaults/bar.py
from ..utils.style_config import COLORS, FONTS

def create_bar_defaults():
    template = go.layout.Template()
    template.data.bar = [go.Bar(
        marker_color=COLORS['accent'],
        hovertemplate='%{y:,.0f}<br>%{x}'
    )]
    return template
```

### Grid Layouts (`templates/grids/*.py`)
```python
# grids/chart_only.py
from plotly.subplots import make_subplots

def create_chart_grid(title: str, subtitle: str = None):
    fig = make_subplots(
        rows=1, cols=1,
        subplot_titles=[title]
    )
    return fig
```

Grid layouts:
- Use make_subplots for structure
- Handle rows, columns, spacing
- Support subplot titles and types
- No styling, only layout
   - Text can be positioned absolutely or relative to data coordinates

```
```python
# grids/chart_table.py
def create_chart_table_grid(title: str):
    """Create a grid with chart and table side by side."""
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{'type': 'xy'}, {'type': 'table'}]],
        subplot_titles=[title, 'Data Table']
    )
    return fig
```

## Component Examples

### Market Snapshot Component
```python
# components/market_snapshot.py
def create_market_view(data):
    # 1. Start with grid layout
    fig = create_chart_grid(
        title="Market Distribution",
        subtitle="Shows by Network"
    )
    
    # 2. Add traces to grid
    fig.add_trace(
        go.Bar(x=data['networks'], y=data['counts']),
        row=1, col=1
    )
    
    # 3. Add any annotations
    fig.add_annotation(
        text=f"Total Shows: {sum(data['counts'])}",
        xref="paper", yref="paper",
        x=0.5, y=1.1
    )
    
    # 4. Apply style defaults
    fig.update_layout(template=create_bar_defaults())
    return fig
```



## Component Development

### 1. Start with Grid Layout
```python
from ..templates.grids.chart_only import create_chart_grid

# Create base grid structure
fig = create_chart_grid(
    title="Market Overview",
    subtitle="Distribution by Network"
)
```

### 2. Add Traces to Grid
```python
# Add traces to specific grid positions
fig.add_trace(
    go.Bar(x=networks, y=counts),
    row=1, col=1
)

# Add any annotations or text
fig.add_annotation(
    text="Key Insight",
    xref="paper", yref="paper",
    x=0.5, y=1.1
)
```

### 3. Apply Style Defaults
```python
from ..templates.defaults.bar import create_bar_defaults

# Apply style defaults last
fig.update_layout(template=create_bar_defaults())
```

## Best Practices

### Component Structure
1. Components use grid layouts directly - no intermediate templates
2. Grid layouts handle structure (rows, cols, spacing)
3. Style defaults handle appearance (colors, fonts, margins)
4. Preview system validates layouts before use

### Development Flow
1. Start with grid layout from grids/
2. Add traces to specific grid positions
3. Apply style defaults from defaults/
4. Test with preview system:
   ```bash
   python -m src.tests.dashboard.templates.preview_grid [grid_type]
   ```

### Style Guidelines
1. Always use constants from style_config.py
2. Only override template defaults when necessary
3. Keep text positioning consistent across components
4. Use proper subplot types (xy, domain, indicator)
5. Follow conventions in [STYLE_GUIDE.md](./STYLE_GUIDE.md)
