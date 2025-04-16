-- Migration: Add network_name to api_show_team
-- Created: 2025-04-16

-- Drop existing view
DROP VIEW IF EXISTS api_show_team;

-- Recreate view with network_name
CREATE VIEW api_show_team AS
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

-- Set view permissions (preserving existing security)
ALTER VIEW api_show_team SET (security_invoker = on);

-- Add helpful comment
COMMENT ON VIEW api_show_team IS 'Secure view providing team member data with show and network information. Includes all team members regardless of role.';
