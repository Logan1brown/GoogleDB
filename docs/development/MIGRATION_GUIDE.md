# Template System Migration Guide

## Overview

We are transitioning from our custom class-based template system to Plotly's native template system. This document guides you through the migration process.

## Why We're Migrating

1. **Better Alignment with Plotly**
   - Use Plotly's built-in template features
   - Leverage template inheritance properly
   - Follow Plotly's best practices

2. **Simpler Architecture**
   - Remove unnecessary class abstractions
   - Reduce code duplication
   - Clear separation of concerns

3. **Improved Maintainability**
   - Easier to update styles
   - Better performance
   - More flexible layouts

## What's Changing

### New Structure

The new template system has three main components:

1. **Style Configuration** (`utils/style_config.py`)
   - Brand colors and fonts
   - Chart dimensions
   - Margin settings

2. **Templates** (`templates/`)
   - `base.py`: Common styles from style_config
   - `defaults/`: Chart type defaults
   - `grids/`: Layout patterns

3. **Components** (`components/`)
   - Import and combine templates as needed
   - Focus on data and business logic

### Code Changes

#### Before (Class-based)
```python
from src.dashboard.utils.templates import MarketOverviewTemplate

# Create figure using template class
fig = MarketOverviewTemplate.create_overview()
MarketOverviewTemplate.add_kpi_widgets(fig, kpis)
MarketOverviewTemplate.add_mini_chart(fig, data)
```

#### After (Plotly Native)
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

## Migration Steps

1. **Move to Style Config**
   - Review style_config.py
   - Ensure all brand styles are defined
   - Document style constants

2. **Create Templates**
   - Create base template using style_config
   - Add chart defaults (bar, heatmap, etc.)
   - Add grid layouts (dual, stacked, etc.)
   - Test each template independently

3. **Update Components**
   - Import needed templates
   - Use go.Figure with templates
   - Add data with template styling
   - Apply grid layouts as needed

4. **Testing**
   - Test each chart type
   - Verify template combinations
   - Check style consistency
   - Run performance tests

5. **Cleanup**
   - Remove old template classes
   - Update documentation
   - Archive v1 components

## Testing Your Changes

1. **Template Tests**
   ```python
   # Test base template
   fig = go.Figure(template=create_base_template())
   assert fig.layout.font.family == FONTS['primary']['family']
   
   # Test chart defaults
   fig = go.Figure(template=create_bar_defaults())
   fig.add_bar(x=[1,2], y=[3,4])
   assert fig.data[0].marker.color == COLORS['accent']
   ```

2. **Component Tests**
   - Templates are correctly imported
   - Data is properly styled
   - Grid layouts work as expected
   - Hover text is formatted

## Common Issues

1. **Missing Styles**
   - Import style_config
   - Use base template
   - Check template order

2. **Grid Layout Issues**
   - Apply grid template last
   - Check row/col settings
   - Verify subplot types

3. **Template Conflicts**
   - Base template first
   - Chart defaults second
   - Grid layout last

## Need Help?

- Check TEMPLATE_SYSTEM.md
- Review style_config.py
- Look at example components
- Ask for code review

This guide will be updated as we complete the migration.
