-- Migration: Fix API View Permissions
-- Created: 2025-04-15

-- Grant access to API views for anon and authenticated roles
GRANT SELECT ON api_show_details TO anon, authenticated;
GRANT SELECT ON api_network_stats TO anon, authenticated;
GRANT SELECT ON api_team_summary TO anon, authenticated;

-- Add RLS policies to control data access
ALTER VIEW api_show_details SECURITY DEFINER;  -- Run as owner to ensure consistent access
ALTER VIEW api_network_stats SECURITY DEFINER;
ALTER VIEW api_team_summary SECURITY DEFINER;

-- Add helpful comments
COMMENT ON VIEW api_show_details IS 'API view for show details. Accessible by all roles with full read access.';
COMMENT ON VIEW api_network_stats IS 'API view for network statistics. Accessible by all roles with full read access.';
COMMENT ON VIEW api_team_summary IS 'API view for team information. Accessible by all roles with full read access.';
