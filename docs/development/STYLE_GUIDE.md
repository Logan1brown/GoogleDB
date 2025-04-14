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

### Text Styling
- **Professional Tone**: Use clear, concise language
- **No Emojis**: Do not use emojis in UI elements (buttons, headers, etc.) to maintain a professional appearance
- **Sentence Case**: Use sentence case for buttons and headers (e.g., "Add new show" not "Add New Show")
- **Punctuation**: Avoid exclamation marks in UI text unless absolutely necessary

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

### Visualization Architecture

For details on the visualization architecture, including templates, grids, and best practices, see [TEMPLATE_SYSTEM.md](./TEMPLATE_SYSTEM.md).

### Component Example
```python
from src.dashboard.templates.grids import create_chart_grid
from src.dashboard.templates.defaults import create_bar_defaults

# 1. Start with grid layout
fig = create_chart_grid(
    title="Genre Distribution",
    subtitle="Shows by Genre"
)

# 2. Add traces to grid
fig.add_trace(
    go.Bar(
        x=genres,
        y=counts,
        hovertemplate='%{y} shows<br>%{x}'
    ),
    row=1, col=1
)

# 3. Apply style defaults
fig.update_layout(template=create_bar_defaults())
```

## Code Structure

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
