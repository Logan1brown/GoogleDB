# Straight-to-Series Analysis Framework

## Market Snapshot
Provides high-level market overview using Level 1 confidence data.

### Dataset Overview
- **Total Shows**: Total number in database
  - Filter by up to 5 specific shows from dropdown
- **Unique Creatives**: Individual creators across all shows
  - Filter by up to 5 specific creators from dropdown
- **Networks**: Count of unique networks
  - Filter by any number of networks
- **Role Types**: 15 standard roles including:
  - Creative: Creator, Writer, Director, Showrunner
  - Production: Executive Producer, Producer
  - Development: Studio/Network Executives
  - Talent: Actor, Host
  - Filter by any number of roles

### Network Distribution
Visualizes market share through interactive bar chart showing:
- Shows per network (sorted by volume)
- Network-specific tooltips
- Uses Plotly's built-in download options (camera icon)

### Key Metrics
1. **Total Shows**: Current database size
2. **Network Concentration**: Share from top 3 networks
   - Lists the top 3 networks
   - Shows percentage of total orders
3. **Top Genre Network**: Network leadership in genres
   - Identifies leading network
   - Shows count in top genre
   - Names the dominant genre

## Content Strategy
Analyzes content patterns using Level 1 confidence data.

### Genre Analysis
- **Distribution Chart**: Interactive bar chart showing:
  - Shows per genre (sorted by volume)
  - Tooltips with counts and percentages
  - Download options via Plotly toolbar
  - Follows style guide (see `docs/development/STYLE_GUIDE.md`)

- **Network Genre Heatmap**:
  - Genre distribution across networks
  - Percentage-based color intensity (Viridis scale)
  - Detailed tooltips with show counts and shares
  - Networks sorted by genre diversity
  - Dynamic height based on network count
  - Side panel with key insights

- **Genre Insights**:
  - Network genre specializations (>40% share)
  - Genre diversity scoring (genres with >10% share)
  - Unique patterns (15% above market average)
  - Minimum 3 shows per network for analysis
  - Primary/secondary genre identification
  - Network-specific genre preferences

### Source Type Analysis
- **Distribution Chart**: Interactive visualization of:
  - Shows per source type
  - Source-specific tooltips
  - Download options

- **Source Insights**:
  - Most common source type
  - Original content share
  - Network source preferences
  - Minimum 3 shows for network analysis
  - Source diversity scoring (Shannon entropy)
  - Network source specialization

## Creative Networks
Maps talent relationships using Level 2 confidence data.

### Network Connections
- **Talent Pool Analysis**:
  - Exclusive talent identification (single-network creators)
  - Shared talent tracking (multi-network creators)
  - Network overlap measurement
  - Creator show counts
  - Network-specific creator lists

- **Network Graph**:
  - Interactive network visualization
  - Node size by show count
  - Edge weight by shared creators
  - Tooltips with detailed stats
  - Download options

### Network Sharing
- **Cross-Network Activity**: Creators working across networks
- **Network Groups**: Common network combinations
- **Creator Mobility**: Movement between networks
- **Metrics**:
  - Cross-network flow
  - Network overlap analysis
  - Creator network range

### Role Analysis
- **Role Categories**:
  - Creative (Creator, Writer, Director, Showrunner)
  - Production (Executive Producer, Producer, Line Producer)
  - Development (Studio/Network/Development Executive)
  - Talent (Actor, Host)

- **Role Normalization**:
  - Role standardization from role_types.csv
  - Compound role handling
  - Missing data management

- **Analysis Features**:
  - Role distribution charts
  - Network role preferences
  - Role combination patterns
  - Career progression tracking
  - Role diversity metrics

## Future Analysis Areas

### Creative Relationships
- Creator collaboration patterns
- Team composition analysis
- Success rates of different team structures

### Genre-Creative Analysis
- Creator genre specialization
- Genre-specific team structures
- Cross-genre creator activity

### Studio Performance
- Independent studio success rates
- Studio-network relationships
- Genre strengths by studio

## Implementation Notes

### Data Processing Structure
```
src/data_processing/
├── market_analysis/       # High-level market overview
│   ├── __init__.py
│   └── market_analysis.py # Network distribution & metrics
├── content_strategy/      # Content pattern analysis
│   ├── genre_analysis_2.py  # Genre patterns and insights with templates
│   └── source_analysis.py # Source type distribution
├── creative_networks/     # Talent relationship mapping
│   ├── network_connections.py    # Network-creator links
│   ├── network_graph.py          # Network visualizations
│   ├── network_sharing_analysis.py # Cross-network activity
│   └── role_analysis.py          # Role distribution
├── genre_creative/       # Genre specialization
└── studio_analysis/      # Studio performance
```

### Output Structure
```
output/
├── network_analysis/     # Network-focused insights
│   ├── content_strategy/ # Genre and source patterns
│   ├── creative_networks/ # Talent relationships
│   ├── genre_creative/   # Genre specialists
│   └── studio_performance/ # Studio metrics
└── visualizations/      # Generated charts & data
```

### Key Dependencies
- **Data Processing**: pandas, numpy
- **Visualization**: plotly, plotly.express
- **Network Analysis**: networkx
- **Logging**: Python logging module
- **Configuration**: .streamlit/config.toml
