-- Migration: Properly Secure Views
-- Created: 2025-04-16

-- Drop existing views
DROP VIEW IF EXISTS api_show_team CASCADE;
DROP VIEW IF EXISTS api_market_analysis CASCADE;

-- Create secure show team view
CREATE VIEW api_show_team WITH (security_invoker = on) AS
SELECT 
    st.id,
    st.show_id,
    st.name,
    st.search_name,
    st.role_type_id,
    st.team_order,
    st.notes,
    st.active,
    st.created_at,
    st.updated_at,
    s.title,
    n.network AS network_name
FROM show_team st
JOIN shows s ON st.show_id = s.id
LEFT JOIN network_list n ON s.network_id = n.id;

-- Create secure market analysis view
CREATE VIEW api_market_analysis WITH (security_invoker = on) AS
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

-- Revoke public access
REVOKE ALL ON api_show_team FROM public;
REVOKE ALL ON api_market_analysis FROM public;

-- Grant access to authenticated users
GRANT ALL ON api_show_team TO authenticated;
GRANT ALL ON api_market_analysis TO authenticated;

-- Grant SELECT to anon users
GRANT SELECT ON api_show_team TO anon;
GRANT SELECT ON api_market_analysis TO anon;

-- Add helpful comments
COMMENT ON VIEW api_show_team IS 'Secure view providing team member data with show and network information. Includes all team members regardless of role.';
COMMENT ON VIEW api_market_analysis IS 'Secure view providing market analysis data. Team data has been moved to api_show_team view.';
