# TMDB Data Integration Plan

## Overview
Plan to enrich our TV series database with comprehensive TMDB data, focusing on success metrics, episode details, and show information.

## Data Points to Integrate

### 1. Success Metrics
- Number of seasons
- Episodes per season
- Production status
- Last air date
- Success score (0-100)
- Success tier (Elite/Successful/Moderate/Unsuccessful)

### 2. Episode Information
- Total episode count
- Season 1 episode count
- Average episodes per season

### 3. Show Details
- Show summary/overview

### 4. Order Type Information
- Series type: limited vs ongoing

## Implementation Steps

### Phase 1: Data Collection
```python
def collect_tmdb_data(show_id):
    show = tmdb_client.get_tv_show_details(show_id)
    
    # Get season 1 episode count
    season_1 = tmdb_client.get_season_details(show_id, 1)
    season_1_episodes = len(season_1.episodes) if season_1 else 0
    
    return {
        # Success Metrics
        'number_of_seasons': show.number_of_seasons,
        'number_of_episodes': show.number_of_episodes,
        'status': show.status,
        'in_production': show.in_production,
        'last_air_date': show.last_air_date,
        
        # Show Details
        'overview': show.overview,
        
        # Episode Info
        'season_1_episodes': season_1_episodes,
        
        # Order Type
        'type': 'limited' if show.number_of_seasons == 1 and not show.in_production else 'ongoing'
    }
```

### Phase 2: Database Updates

1. **New Columns Required**
   ```sql
   ALTER TABLE shows ADD COLUMN
       success_score INTEGER,
       success_tier TEXT,
       episode_count INTEGER,
       season_1_episodes INTEGER,
       show_summary TEXT,
       series_type TEXT
   ```

2. **Update Process**
   ```python
   def update_show_data(show_id, tmdb_data):
       # Calculate success metrics
       success_score = calculate_success_score(tmdb_data)
       success_tier = get_success_tier(success_score)
       
       # Update database
       update_query = """
           UPDATE shows SET
               success_score = ?,
               success_tier = ?,
               episode_count = ?,
               season_1_episodes = ?,
               show_summary = ?,
               series_type = ?
           WHERE tmdb_id = ?
       """
       execute_query(update_query, [
           success_score,
           success_tier,
           tmdb_data['number_of_episodes'],
           tmdb_data['season_1_episodes'],
           tmdb_data['overview'],
           tmdb_data['type'],
           show_id
       ])
   ```

### Phase 3: Google Sheets Integration

1. **New Sheet Columns**
   - Success Score
   - Success Tier
   - Episode Count
   - Season 1 Episodes
   - Show Summary
   - Series Type (Limited/Ongoing)

2. **Update Process**
   ```python
   def update_sheets_data(shows_data):
       worksheet = get_worksheet('Shows')
       
       # Add new columns if needed
       add_missing_columns(worksheet, NEW_COLUMNS)
       
       # Batch update rows
       batch_update_rows(worksheet, shows_data)
   ```

## Implementation Schedule

1. **Week 1: Data Collection**
   - Set up TMDB API client
   - Create success scoring pipeline
   - Test with sample shows

2. **Week 2: Database Integration**
   - Add new columns
   - Implement update process
   - Run initial data collection

3. **Week 3: Sheets Integration**
   - Add new columns to sheets
   - Sync database updates
   - Validate data accuracy

## Success Criteria

1. **Data Completeness**
   - Success metrics calculated
   - Episode counts verified
   - Show summaries added
   - Series types classified

2. **Data Quality**
   - Success scores match criteria
   - Episode counts accurate
   - Series types correctly identified

3. **Integration Success**
   - Database updated
   - Sheets synced
   - Documentation complete

## Next Steps

1. Review data schema
2. Test success scoring
3. Run pilot batch
4. Validate results
5. Full implementation
