-- Migration: Add Show Team Audit
-- Created: 2025-04-14

-- Add trigger to show_team table
create trigger show_team_audit
after insert or update or delete on show_team
for each row execute function audit.log_changes();
