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

## Genre Analysis
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

## Source Analysis
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

## Network Analysis
Maps talent relationships using network data.

+------------------------+------------------------+
|                       |  [Tabs]                |
|     Heatmap           |  [Search] [Success]    |
|     (500x500)         |                        |
|                       |  Search Tab:           |
|                       |  +-----------------+   |
|                       |  | Networks ▾      |   |
|                       |  +-----------------+   |
|                       |  | Networks ▾      |   |
|                       |  +-----------------+   |
|                       |  | Genre ▾         |   |
|                       |  +-----------------+   |
|                       |  | Source ▾        |   |
|                       |  +-----------------+   |
|                       |  Results:              |
|                       |  [Scrollable list]     |
+------------------------+------------------------+
Two network dropdowns (to compare any two)
Single genre dropdown
Single source dropdown
Each dropdown is optional but must match if selected
Just like our market view's clean dropdown interface

### Network Overview
- **Core Metrics**:
  - Total networks count
  - Total unique creators
  - Cross-network activity percentage

### Network Graph
- **Interactive Visualization**:
  - Node size represents show count
  - Connections show shared talent
  - Network-to-network relationship view

### Network Filter
- **Creator Search**:
  - Filter by network
  - View creator details
  - Show listings
  - Network distribution

### Success Stories
- **Multi-Network Activity**:
  - Success stories
  - Network partnerships
  - Creator metrics

## Studio Performance
Maps studio activity and relationships.

### Studio Overview
- **Core Metrics**:
  - Total studios count
  - Studio show volumes
  - Network partnership rates

### Studio Distribution
- **Interactive Graph**:
  - Top 15 studios by show count
  - Network distribution per studio
  - Studio-network relationships

### Studio Filter
- **Studio Analysis**:
  - Filter by studio
  - Show details
  - Network partners
  - Genre breakdown

### Success Stories
- **Studio Highlights**:
  - Top performing studios
  - Network collaborations
  - Show portfolio

# Future Analysis Areas

## Success Metrics
Integrate into Existing Components
- Add success score averages to genre breakdowns
- Show success rates by source type
- Compare network performance via success metrics
-This gives immediate context to our existing analysis

    Market Snapshot
    - Add "Average Success Score" to Key Metrics
    -      Add "Network Concentration" (e.g., "Top 3: 45%")
    -      Add "Vertical Integration" (e.g., "VI Studios: 45%")
    -      Add "Top Success Network" (e.g., "HBO: 85/100")
    -      Add "Multi-Network Success" (e.g., "4 Networks > 80/100")
    - Add success score distribution chart next to network distribution
    - Add success rate filter option (e.g., "Show only high success (>70)")

    Genre Analysis
    - Add success score column to Network Genre Heatmap
    - Add average success score per genre
    - Color-code genres by success rate
    - Add "Genre Success Leaders" section showing top performing genres

    Source Analysis
    - Add success rate comparison between source types
    - Show which sources tend to lead to higher success
    - Add success metrics to source-specific tooltips

    Network Analysis
    - Add success metrics to network overview stats
    - Color network nodes by average success score
    - Add success stories to network filter view
    - Show success rate distribution per network

New Success-Focused Component
- This could dive deeper into patterns that cross-cut the other categories
- Features could include:
- Success score distribution/histogram
- Top performers analysis
- Risk factors (what correlates with low scores)
- Multi-factor analysis (e.g., genre + source combinations)

## Role Analysis - depends on data refinement
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

## Creative Relationships - depends on data refinement
- Creator collaboration patterns
- Team composition analysis 
- Success rates of different team structures

## Combined Content Strategy - component impovement
- **Layered Analysis Pattern**:
  - Network + Genre + Source combinations
  - Primary/secondary filter hierarchy
  - Cross-dimensional insights

- **Content Strategy Insights**:
  - Network preferences by genre and source
  - Creator adaptability across types
  - Genre-source correlations
  - Market gap identification

# Implementation Notes

## Data Processing Structure
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

## Output Structure
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

USE CASE COMPONENT LAYOUTS

# Use Case 1: Investment/Deal Analysis
def investment_view():
    # Input: IP/Talent to evaluate
    search = st.text_input("Search IP/Talent")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        # Track Record
        st.header("Performance History")
        st.dataframe(show_history)  # Success rates
        st.dataframe(network_deals)  # Who buys from them
        
    with col2:
        # Quick Stats
        st.metric("Success Rate", "72%")
        st.metric("Avg Deal Size", "13 eps")
        st.metric("Network Reach", "4 nets")

# Use Case 2: Show Sales Targeting
def sales_targeting_view():
    # Input: Show characteristics
    genre = st.multiselect("Genres")
    source = st.selectbox("Source Type")
    
    # Who Buys Similar Shows
    st.header("Best Network Matches")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("By Genre Match")
        st.dataframe(network_genre_prefs)
    with col2:
        st.subheader("By Source Match")
        st.dataframe(network_source_prefs)

# Use Case 3: Package Planning
def package_planning_view():
    # Input: Show concept
    show_type = st.selectbox("Show Type")
    target_net = st.multiselect("Target Networks")


    UNIFIED VIEW
    
def market_intel_view():
    # Left Panel: Search & Filters
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        # Show Search
        st.subheader("Search Shows")
        show_query = st.text_input("", key="show_search")
        
        # Creator Search
        st.subheader("Search Creators")
        creator_query = st.text_input("", key="creator_search")
        
        # Filters
        st.divider()
        genre = st.multiselect("Genre")
        source = st.selectbox("Source Type")
       
    with col2:  # Main Results Area
        if show_query or creator_query:
            tabs = st.tabs([
                "Network Matches",  # Who's buying what
                "Package Elements", # What works where
                "Market Position"   # Where's the opportunity
            ])
       
    with col3:  # Persistent Success Panel
        st.subheader("Success Metrics")
           
        # Always show if there's a query
        if show_query or creator_query:
            # Key Metrics
            st.metric("Success Score", "8.2")
            st.metric("Market Demand", "High")
               
            # Quick Stats
            st.info("📈 Trending Genre")
            st.warning("🎯 Niche Market")
               
            # Success Factors
            st.subheader("Success Factors")
            factors = {
                "Genre Fit": "85%",
                "Team Strength": "High",
                "Market Timing": "Good"
            }
            for k, v in factors.items():
            st.text(f"{k}: {v}")
   
        # Comparative Success
        if show_query and creator_query:
            st.divider()
            st.subheader("Package Strength")
            st.progress(0.75)  # Show/Creator combo strength


def market_intel_view():
    # Top: Analysis Type
    analysis_type = st.radio(
        "",
        ["IP Acquisition", "IP Packaging", "IP Development"],
        horizontal=True
    )
    
    if analysis_type == "IP Acquisition":
        col1, col2 = st.columns([1, 3])
        
        with col1:  # Input Panel
            genre = st.multiselect("Genre", ["Drama", "Comedy", "Thriller"])
            
        with col2:  # Results Panel
            tab1, tab2, tab3, tab4 = st.tabs(["Networks", "Creators", "Pairings", "Insights"])
            
            with tab1:  # Network Analysis
                st.markdown("##### Network Performance in Genre")
                # Table: Network | Shows | Success Rate | Renewal Rate | Current Status
                
            with tab2:  # Creator Analysis
                st.markdown("##### Top Creators in Genre")
                # Table: Creator | Role | Shows | Success Rate | Specialties
            
            with tab3:  # Creator / Network Pairings
                st.markdown("##### Creator / Network Pairings")
                # List of successful pairings/teams
              
            with tab4:  # Pattern Analysis
                st.markdown("##### Success Patterns")
                # What makes shows work in this genre
                # - Episode counts
                # - Budget ranges
                # - Source material performance
                # - Timing/scheduling insights
    
    elif analysis_type == "Package Builder":
        col1, col2 = st.columns([1, 3])
        
        with col1:  # Input Panel
            source = st.selectbox("Source Type", ["Original", "Book", "IP"])
            genre = st.multiselect("Genre")
            target = st.multiselect("Target Networks")
            
        with col2:  # Package Recommendations
            st.markdown("##### Recommended Packages")
            # Cards showing:
            # - Network
            # - Successful shows
            # - Successful teams
            
            st.markdown("##### Why These Work")
            # Analysis of why these combinations succeed
            
    else:  # IP Development
        col1, col2 = st.columns([1, 3])
        
        with col1:  # Input Panel
            ip_type = st.selectbox("IP Type", ["Book", "Game", "Film"])
            genre = st.multiselect("Genre")
            tone = st.select_slider("Tone", ["Dark", "Balanced", "Light"])
            
        with col2:  # Strategy Panel
            st.markdown("##### Format Strategy")
            # Analysis of what format works best:
            # - Limited vs Ongoing
            # - Episode count
            
            st.markdown("##### Network Alignment")
            # Which networks succeed with this type
            
            st.markdown("##### Development Insights")
            # Key factors in successful adaptations
            # Common pitfalls to avoid