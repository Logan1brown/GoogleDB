# Database Views

## Materialized Views

These views pre-compute and cache commonly needed data to improve query performance.

### show_details
```sql
CREATE MATERIALIZED VIEW show_details AS
SELECT 
    s.id,
    s.title,
    s.description,
    nl.network as network_name,
    gl.genre as genre_name,
    array_agg(DISTINCT sgl.genre) as subgenre_names,
    array_agg(DISTINCT stl.studio) as studio_names,
    st.status as status_name,
    ot.type as order_type_name,
    srt.type as source_type_name,
    s.date,
    s.episode_count,
    s.tmdb_id,
    tsm.seasons as tmdb_seasons,
    tsm.total_episodes as tmdb_total_episodes,
    tsm.status as tmdb_status,
    tsm.last_air_date as tmdb_last_air_date
FROM shows s
LEFT JOIN network_list nl ON s.network_id = nl.id
LEFT JOIN genre_list gl ON s.genre_id = gl.id
LEFT JOIN genre_list sgl ON sgl.id = ANY(s.subgenres)
LEFT JOIN studio_list stl ON stl.id = ANY(s.studios)
LEFT JOIN status_types st ON s.status_id = st.id
LEFT JOIN order_types ot ON s.order_type_id = ot.id
LEFT JOIN source_types srt ON s.source_type_id = srt.id
LEFT JOIN tmdb_success_metrics tsm ON s.tmdb_id = tsm.tmdb_id
WHERE s.active = true
GROUP BY 
    s.id, s.title, s.description, nl.network, gl.genre,
    st.status, ot.type, srt.type, s.date, s.episode_count,
    s.tmdb_id, tsm.seasons, tsm.total_episodes, tsm.status,
    tsm.last_air_date;

CREATE UNIQUE INDEX idx_show_details_id ON show_details(id);
```

### team_summary
```sql
CREATE MATERIALIZED VIEW team_summary AS
SELECT 
    st.show_id,
    s.title as show_title,
    array_agg(DISTINCT st.name) FILTER (WHERE rt.role = 'Writer') as writers,
    array_agg(DISTINCT st.name) FILTER (WHERE rt.role = 'Producer') as producers,
    array_agg(DISTINCT st.name) FILTER (WHERE rt.role = 'Director') as directors,
    array_agg(DISTINCT st.name) FILTER (WHERE rt.role = 'Creator') as creators
FROM show_team st
JOIN shows s ON st.show_id = s.id
JOIN role_types rt ON st.role_type_id = rt.id
WHERE st.active = true AND s.active = true
GROUP BY st.show_id, s.title;

CREATE UNIQUE INDEX idx_team_summary_show_id ON team_summary(show_id);
```

### network_stats
```sql
CREATE MATERIALIZED VIEW network_stats AS
SELECT 
    nl.id as network_id,
    nl.network as network_name,
    count(s.id) as total_shows,
    count(s.id) FILTER (WHERE st.status = 'Active') as active_shows,
    count(s.id) FILTER (WHERE st.status = 'Ended') as ended_shows,
    array_agg(DISTINCT gl.genre) as genres,
    array_agg(DISTINCT srt.type) as source_types
FROM network_list nl
LEFT JOIN shows s ON nl.id = s.network_id AND s.active = true
LEFT JOIN status_types st ON s.status_id = st.id
LEFT JOIN genre_list gl ON s.genre_id = gl.id
LEFT JOIN source_types srt ON s.source_type_id = srt.id
WHERE nl.active = true
GROUP BY nl.id, nl.network;

CREATE UNIQUE INDEX idx_network_stats_id ON network_stats(network_id);
```

## Refresh Schedule

### Manual Refresh
Refresh individual views:
```sql
REFRESH MATERIALIZED VIEW CONCURRENTLY show_details;
REFRESH MATERIALIZED VIEW CONCURRENTLY team_summary;
REFRESH MATERIALIZED VIEW CONCURRENTLY network_stats;
```

### Helper Function
Refresh all views at once:
```sql
-- Function definition
CREATE OR REPLACE FUNCTION refresh_materialized_views()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY show_details;
    REFRESH MATERIALIZED VIEW CONCURRENTLY team_summary;
    REFRESH MATERIALIZED VIEW CONCURRENTLY network_stats;
END;
$$ LANGUAGE plpgsql;

-- Usage
SELECT refresh_materialized_views();
```

### Recommended Schedule
- `show_details`: Daily at midnight
- `team_summary`: Daily at midnight
- `network_stats`: Weekly on Sunday

### Cron Job Example
```bash
# /etc/cron.d/refresh_views

# Refresh show_details and team_summary daily at midnight
0 0 * * * postgres psql -c 'SELECT refresh_materialized_views()'

# Refresh network_stats weekly on Sunday at 1 AM
0 1 * * 0 postgres psql -c 'REFRESH MATERIALIZED VIEW CONCURRENTLY network_stats'
```

## Usage Examples

### Show Details with Team
```sql
SELECT 
    sd.*,
    ts.writers,
    ts.producers,
    ts.directors,
    ts.creators
FROM show_details sd
JOIN team_summary ts ON sd.id = ts.show_id
WHERE sd.network_name = $1;
```

### Network Analysis
```sql
SELECT 
    ns.*,
    count(sd.id) as shows_with_tmdb,
    avg(sd.tmdb_total_episodes) as avg_episodes
FROM network_stats ns
LEFT JOIN show_details sd ON ns.network_name = sd.network_name
WHERE sd.tmdb_id IS NOT NULL
GROUP BY ns.network_id, ns.network_name, ns.total_shows, 
         ns.active_shows, ns.ended_shows, ns.genres, ns.source_types;
```

## Performance Benefits

1. **Query Speed**
   - Pre-computed joins reduce runtime
   - Cached results for common queries
   - Efficient array operations

2. **Resource Usage**
   - Reduced database load
   - Minimized complex calculations
   - Better cache utilization

3. **Consistency**
   - Single source of truth
   - Standardized aggregations
   - Reliable reporting data
