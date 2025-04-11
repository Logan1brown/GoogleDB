# Data Column Reference

This document serves as the source of truth for column names across different sheets in our data pipeline.

## Shows Sheet
Primary sheet containing show information.

### Columns
- `shows` - Show title
- `key_creatives` - Key creative team members
- `network` - Network name
- `studio` - Studio name
- `date` - Date
- `genre` - Genre
- `subgenre` - Subgenre
- `episode_count` - Number of episodes
- `source_type` - Source type
- `status` - Status
- `order_type` - Order type
- `notes` - Notes
- `TMDB_ID` - TMDB identifier

## Show Team Sheet
Contains team member information.

### Columns
- `show_name` - Show title
- `name` - Team member name
- `roles` - Role(s)
- `order` - Order
- `notes` - Notes

## TMDB Success Metrics Sheet
Contains metrics from TMDB API.

### Columns
- `TMDB_ID` - TMDB identifier
- `Title` - Show title
- `tmdb_seasons` - Number of seasons
- `tmdb_eps` - Episodes per season
- `tmdb_total_eps` - Total episodes
- `tmdb_avg_eps` - Average episodes per season
- `tmdb_status` - Show status
- `tmdb_last_air` - Last air date

## Critical Notes

1. ID Columns
   - `TMDB_ID` is used to join shows with TMDB metrics
   - Convert IDs to string type when joining

2. Best Practices
   - Use exact column names as shown above
   - Add clear comments for column usage
   - Prefix new metrics with source (e.g., tmdb_*, netflix_*)
