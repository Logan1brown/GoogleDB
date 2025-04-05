# TV Series Dashboard: Unified View Proposal

## Overview
A streamlined dashboard that provides actionable insights for TV series development, focusing on three key areas: Acquisition, Packaging, and Development. The interface emphasizes clean data presentation and consistent styling across all views.

## Design Principles
1. Consistent Formatting
   - Clean markdown text over complex UI elements
   - Uniform spacing with HTML line breaks
   - Clear section headers using H3 (###)
   - No bullet points for cleaner visual hierarchy

2. Data Organization
   - Key metrics displayed in easily scannable format
   - Double line breaks between entities for clear separation
   - Tabbed interface for related but distinct data sets

## View Structure

### 1. Acquisition View

#### Input Panel
- Source Type selector (Original/Book/IP)
- Genre selector (Drama/Comedy/Thriller/Fantasy)

#### Results Panel (Tabbed)

##### Networks Tab
```
HBO
Shows in Genre: 5
Success Score: 85%
Renewal Rate: 90%


Netflix
Shows in Genre: 4
Success Score: 82%
Renewal Rate: 85%
```

##### Creators Tab
```
Craig Mazin
Recent Show: The Last of Us
Success Score: 92%


Mike Flanagan
Recent Show: The Fall of House of Usher
Success Score: 88%
```

##### Pairings Tab
```
HBO + Craig Mazin
(The Last of Us)


Netflix + Mike Flanagan
(Midnight Series)
```

##### Insights Tab
- Format Metrics and Performance displayed in two columns
- Uses Streamlit metrics for emphasis

### 2. Packaging View

#### Input Panel
- Source Type selector (Original/Book/IP)
- Genre selector (Drama/Comedy/Thriller/Fantasy)

#### Results Panel
```
### Package A
Network: HBO Max
Shows: House of the Dragon, His Dark Materials
Team: David E. Kelley, Melissa James Gibson


### Package B
Network: Prime Video
Shows: The Wheel of Time, Good Omens
Team: Rafe Judkins, Neil Gaiman
```

### 3. Development View

#### Input Panel
- Source Type selector (Original/Book/IP)
- Genre selector (Drama/Comedy/Thriller/Fantasy)

#### Results Panel   
- Network Alignment
  - Expandable Dropdown (network name, number of shows)
  - Shows: House of the Dragon, His Dark Materials

#### Metrics
- Market Insights
  - Success Score
  - Renewal Rate

- Format Strategy 
  - Episode Count
  - Best Format 

## Data Sources

### Primary Tables

1. `shows.csv`
   - Show metadata and basic metrics
   - Key fields:
     - shows: Show title
     - network: Broadcasting network
     - genre/subgenre: Show categorization
     - source_type: Original/Book/IP
     - status: Development/Active/Cancelled
     - episode_count: Number of episodes

2. `show_team.csv`
   - Creative team information
   - Key fields:
     - show_name: Show title (join key)
     - name: Team member name
     - roles: Position/responsibility
     - order: Team hierarchy

### Success Analysis

`SuccessAnalyzer` component provides:
1. Show Success Metrics
   - TMDB-based success scores
   - Show status (Returning/Canceled/Ended)
   - Episode metrics (total, per season)

2. Network Performance
   - Aggregated success by network
   - Show count by network/genre
   - Status distribution (returning/canceled/ended)

3. Creator Impact
   - Historical success rates
   - Genre performance patterns
   - Network collaboration history

### Derived Recommendations

1. Package Suggestions
   - Based on SuccessAnalyzer metrics
   - Filtered by genre and source_type
   - Optimized for:
     - Network fit
     - Creator compatibility
     - Format success patterns

## Technical Implementation

### Data Structure
- Shows data from 'shows' column
- Team data from 'show_name' column
- Maintain distinct column names for data pipeline integrity

### Styling Guidelines
1. Text Display
   ```python
   st.markdown('### Section Title')
   st.markdown('''
   Entity Name<br>
   Metric One: Value<br>
   Metric Two: Value<br>
   <br>
   <br>
   Next Entity
   ''', unsafe_allow_html=True)
   ```

2. Metrics Display
   ```python
   col1, col2 = st.columns(2)
   with col1:
       st.metric("Metric Name", "Value")
   ```

### Component Organization
- Separate view logic into distinct functions
- Use consistent parameter names across components
- Maintain clear data transformation pipeline

## Next Steps
1. Implement Development view with consistent styling
2. Add data validation and error handling
3. Integrate real-time data updates
4. Add export functionality for reports
5. Implement user preferences/settings

## Future Enhancements
1. Advanced filtering options
2. Custom package builder
3. Historical trend analysis
4. Recommendation engine
5. Collaboration features
