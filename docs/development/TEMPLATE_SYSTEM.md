# Plotly Template System

## Overview
We use Plotly's native template system (`go.layout.Template`) to define reusable styles and layouts. Our implementation follows a three-layer approach:

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

## 2. Template Types

### Base Template (`templates/base.py`)
Creates a single base template using style constants:
```python
def create_base_template():
    template = go.layout.Template()
    template.layout = dict(
        font=dict(family=FONTS['primary']['family']),
        paper_bgcolor=COLORS['background'],
        showlegend=True
    )
    return template
```

### Chart Defaults (`templates/defaults/*.py`)
Define default styles for specific chart types:
```python
# defaults/bar.py
def create_bar_defaults():
    template = go.layout.Template()
    template.data.bar = [go.Bar(
        marker_color=COLORS['accent'],
        hovertemplate='%{y:,.0f}<br>%{x}'
    )]
    return template
```

### Grid Layouts (`templates/grids/*.py`)
Define common layout patterns:
```python
# grids/with_table.py
def create_with_table_grid():
    template = go.layout.Template()
    template.layout.grid = dict(
        rows=2, cols=1,
        pattern='independent'
    )
    return template
```

## 3. Usage in Components
Components combine templates as needed:
```python
# components/genre_analysis.py
def create_genre_view():
    # Start with bar defaults
    fig = go.Figure(template=create_bar_defaults())
    
    # Add data (styling handled by template)
    fig.add_bar(x=genres, y=counts)
    
    # Add table grid if needed
    fig.update_layout(template=create_with_table_grid())
    return fig
```

## Best Practices
1. Always use style constants from style_config.py
2. Create templates using go.layout.Template
3. Combine defaults and grids in components
4. Only override template defaults when necessary

## Usage Examples

### Basic Chart
```python
from src.dashboard.utils.templates import create_bar_template

fig = go.Figure(template=create_bar_template())
fig.add_trace(go.Bar(x=categories, y=values))
```

### Chart with Table
```python
from src.dashboard.utils.templates import create_chart_with_table

fig = go.Figure(template=create_chart_with_table())
fig.add_trace(go.Bar(...), row=1, col=1)
fig.add_trace(go.Table(...), row=1, col=2)
```

## Best Practices
1. Always inherit from base template
2. Use template.layout for figure-wide defaults
3. Use template.data for trace-specific defaults
4. Use template.layout.*defaults for annotation/shape defaults
5. Name template elements for later customization
