-- Migration: Simplify Market Analysis View
-- Created: 2025-04-16

-- Drop existing view
DROP VIEW IF EXISTS api_market_analysis;

-- Create secure market analysis view
CREATE VIEW api_market_analysis AS
SELECT 
    s.tmdb_id,
    s.title,
    n.network AS network_name,
    array_agg(DISTINCT st.studio) AS studio_names,
    st2.status AS status_name,
    s.episode_count,
    tm.seasons AS tmdb_seasons,
    tm.total_episodes AS tmdb_total_episodes,
    tm.status AS tmdb_status,
    tm.last_air_date AS tmdb_last_air_date,
    s.date AS announced_date
FROM shows s
LEFT JOIN network_list n ON s.network_id = n.id
LEFT JOIN studio_list st ON st.id = ANY (s.studios)
LEFT JOIN status_types st2 ON s.status_id = st2.id
LEFT JOIN tmdb_success_metrics tm ON s.tmdb_id = tm.tmdb_id
GROUP BY s.tmdb_id, s.title, n.network, st2.status, s.episode_count, tm.seasons, tm.total_episodes, tm.status, tm.last_air_date, s.date;

-- Set view permissions
ALTER VIEW api_market_analysis SET (security_invoker = on);
GRANT SELECT ON api_market_analysis TO authenticated;
GRANT SELECT ON api_market_analysis TO anon;

-- Add helpful comment
COMMENT ON VIEW api_market_analysis IS 'Secure view providing market analysis data. Team data has been moved to api_show_team view.';
