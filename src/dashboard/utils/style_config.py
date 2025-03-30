"""Style configuration for the dashboard."""

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

CHART_DEFAULTS = {
    'margin': {
        'plot': dict(t=30, b=20),
        'section': dict(t=20, b=20)
    },
    'colorscales': {
        'primary': 'Viridis',
        'secondary': 'Plasma'
    }
}

DIMENSIONS = {
    'dashboard': {
        'width': None,  # Use container width
        'height': 400,
        'margin': CHART_DEFAULTS['margin']['plot']
    },
    'standalone': {
        'width': 800,
        'height': 500,
        'margin': CHART_DEFAULTS['margin']['section']
    }
}
