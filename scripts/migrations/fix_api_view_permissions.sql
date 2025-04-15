-- Fix API View Permissions
-- Run this in the Supabase SQL Editor

-- Change API views to SECURITY DEFINER
ALTER VIEW api_show_details SECURITY DEFINER;
ALTER VIEW api_network_stats SECURITY DEFINER;
ALTER VIEW api_team_summary SECURITY DEFINER;
ALTER VIEW api_market_analysis SECURITY DEFINER;

-- Grant access to anon role
GRANT SELECT ON api_show_details TO anon;
GRANT SELECT ON api_network_stats TO anon;
GRANT SELECT ON api_team_summary TO anon;
GRANT SELECT ON api_market_analysis TO anon;
