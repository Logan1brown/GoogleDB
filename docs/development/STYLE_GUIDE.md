# Dashboard Style Guide

## Visual Standards

### Typography
- **Primary Font**: Source Sans Pro
- **Font Sizes**:
  - Title: 20px
  - Section Headers: 16px
  - Body Text: 14px
  - Small Text: 12px

### Colors
- **Primary Colors**:
  - Text: rgb(49, 51, 63)
  - Background: #FFFFFF
  - Accent: rgb(55, 83, 109)
- **Chart Colors**:
  - Primary: 'Viridis' colorscale
  - Highlight: rgb(55, 83, 109)

### Layout
- **Margins**:
  - Top: 20px (30px for plots)
  - Bottom: 20px
  - Left/Right: Auto (use container width)
- **Spacing**:
  - Between sections: 30px
  - Between elements: 20px

### Charts & Visualizations
1. **General Rules**:
   - Full width (use_container_width=True)
   - No titles (use section headers instead)
   - Interactive tooltips with detailed data
   - Download buttons for all figures

2. **Specific Chart Types**:
   - **Bar Charts**:
     - Vertical bars
     - Single color (rgb(55, 83, 109))
     - Sorted by value (descending)
     - Hover text with counts and percentages
   
   - **Heatmaps**:
     - Viridis colorscale
     - Right-aligned color bar
     - Hover text with network, genre, counts
     - Dynamic height based on data
   
   - **Tables**:
     - Left-aligned text
     - Source Sans Pro font
     - Header: 14px, bold
     - Cells: 12px, regular

### Templates
All visualizations use Plotly's native template system in `src/dashboard/templates/`:

1. **Base Template**: Common styles from style_config.py
2. **Chart Defaults**: Type-specific styling
   - `bar.py`: Bar chart defaults
   - `heatmap.py`: Heatmap defaults
   - `scatter.py`: Scatter plot defaults
   - `table.py`: Table defaults
3. **Grid Layouts**: Common arrangements
   - `dual.py`: Side-by-side charts
   - `stacked.py`: Vertical stacking
   - `with_table.py`: Chart + data table

## Code Structure

### Template Usage
```python
from src.dashboard.templates.defaults import create_bar_defaults
from src.dashboard.templates.grids import create_with_table_grid

# Create figure with bar defaults
fig = go.Figure(template=create_bar_defaults())

# Add data (styling handled by template)
fig.add_bar(x=genres, y=counts)

# Apply grid layout if needed
fig.update_layout(template=create_with_table_grid())
```

### Style Configuration
Style constants are defined in `src/dashboard/utils/style_config.py`:
```python
COLORS = {
    'text': {
        'primary': 'rgb(49, 51, 63)',
        'secondary': 'rgb(120, 120, 120)'
    },
    'background': '#FFFFFF',
    'accent': 'rgb(55, 83, 109)'
}

FONTS = {
    'primary': {
        'family': 'Source Sans Pro',
        'sizes': {
            'title': 20,
            'header': 16,
            'body': 14,
            'small': 12
        }
    }
}
```
