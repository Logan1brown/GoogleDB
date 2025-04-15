-- Migration: Fix Function Search Paths
-- Created: 2025-04-15

-- Fix 1: refresh_materialized_views
-- Drop existing function if it exists
DROP FUNCTION IF EXISTS public.refresh_materialized_views();

-- Create function with explicit search path
CREATE OR REPLACE FUNCTION public.refresh_materialized_views()
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
    -- Refresh materialized views in dependency order
    REFRESH MATERIALIZED VIEW public.show_details;
    REFRESH MATERIALIZED VIEW public.network_stats;
    REFRESH MATERIALIZED VIEW public.team_summary;
END;
$$;

-- Grant execute permission to authenticated users
GRANT EXECUTE ON FUNCTION public.refresh_materialized_views() TO authenticated;
GRANT EXECUTE ON FUNCTION public.refresh_materialized_views() TO service_role;

-- Revoke execute from public
REVOKE EXECUTE ON FUNCTION public.refresh_materialized_views() FROM public;

-- Fix 2: trigger_set_timestamp
-- Drop trigger first
DROP TRIGGER IF EXISTS set_timestamp ON tmdb_success_metrics;
-- Then drop function
DROP FUNCTION IF EXISTS public.trigger_set_timestamp();

-- Create function with explicit search path
CREATE OR REPLACE FUNCTION public.trigger_set_timestamp()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;

-- Grant execute permission to authenticated users
GRANT EXECUTE ON FUNCTION public.trigger_set_timestamp() TO authenticated;
GRANT EXECUTE ON FUNCTION public.trigger_set_timestamp() TO service_role;

-- Revoke execute from public
REVOKE EXECUTE ON FUNCTION public.trigger_set_timestamp() FROM public;

-- Recreate the trigger
CREATE TRIGGER set_timestamp
    BEFORE UPDATE ON tmdb_success_metrics
    FOR EACH ROW
    EXECUTE FUNCTION public.trigger_set_timestamp();

-- Fix 3: update_updated_at
-- Drop all triggers that use this function
DROP TRIGGER IF EXISTS update_status_types_updated_at ON status_types;
DROP TRIGGER IF EXISTS update_network_list_updated_at ON network_list;
DROP TRIGGER IF EXISTS update_studio_list_updated_at ON studio_list;
DROP TRIGGER IF EXISTS update_genre_list_updated_at ON genre_list;
DROP TRIGGER IF EXISTS update_subgenre_list_updated_at ON subgenre_list;
DROP TRIGGER IF EXISTS update_shows_updated_at ON shows;
DROP TRIGGER IF EXISTS update_show_team_updated_at ON show_team;
DROP TRIGGER IF EXISTS update_user_metadata_updated_at ON auth.user_metadata;
DROP TRIGGER IF EXISTS update_source_types_updated_at ON source_types;
DROP TRIGGER IF EXISTS update_role_types_updated_at ON role_types;
DROP TRIGGER IF EXISTS update_order_types_updated_at ON order_types;

-- Drop the function
DROP FUNCTION IF EXISTS public.update_updated_at() CASCADE;

-- Create function with explicit search path
CREATE OR REPLACE FUNCTION public.update_updated_at()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;

-- Grant execute permission to authenticated users
GRANT EXECUTE ON FUNCTION public.update_updated_at() TO authenticated;
GRANT EXECUTE ON FUNCTION public.update_updated_at() TO service_role;

-- Revoke execute from public
REVOKE EXECUTE ON FUNCTION public.update_updated_at() FROM public;

-- Recreate all triggers
CREATE TRIGGER update_status_types_updated_at
    BEFORE UPDATE ON status_types
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at();

CREATE TRIGGER update_network_list_updated_at
    BEFORE UPDATE ON network_list
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at();

CREATE TRIGGER update_studio_list_updated_at
    BEFORE UPDATE ON studio_list
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at();

CREATE TRIGGER update_genre_list_updated_at
    BEFORE UPDATE ON genre_list
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at();

CREATE TRIGGER update_subgenre_list_updated_at
    BEFORE UPDATE ON subgenre_list
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at();

CREATE TRIGGER update_shows_updated_at
    BEFORE UPDATE ON shows
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at();

CREATE TRIGGER update_show_team_updated_at
    BEFORE UPDATE ON show_team
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at();

CREATE TRIGGER update_user_metadata_updated_at
    BEFORE UPDATE ON auth.user_metadata
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at();

CREATE TRIGGER update_source_types_updated_at
    BEFORE UPDATE ON source_types
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at();

CREATE TRIGGER update_role_types_updated_at
    BEFORE UPDATE ON role_types
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at();

CREATE TRIGGER update_order_types_updated_at
    BEFORE UPDATE ON order_types
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at();

-- Fix 4: standardize_name
-- Drop all triggers that use this function
DROP TRIGGER IF EXISTS standardize_network_name ON network_list;
DROP TRIGGER IF EXISTS standardize_studio_name ON studio_list;
DROP TRIGGER IF EXISTS standardize_genre_name ON genre_list;
DROP TRIGGER IF EXISTS standardize_status_name ON status_types;
DROP TRIGGER IF EXISTS standardize_order_type_name ON order_types;
DROP TRIGGER IF EXISTS standardize_source_type_name ON source_types;

-- Drop the function
DROP FUNCTION IF EXISTS public.standardize_name() CASCADE;

-- Create function with explicit search path
CREATE OR REPLACE FUNCTION public.standardize_name()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
    -- Convert first letter of each word to uppercase, rest to lowercase
    NEW.name = regexp_replace(
        initcap(NEW.name),
        '\s+(\w)',
        ' \1',
        'g'
    );
    RETURN NEW;
END;
$$;

-- Grant execute permission to authenticated users
GRANT EXECUTE ON FUNCTION public.standardize_name() TO authenticated;
GRANT EXECUTE ON FUNCTION public.standardize_name() TO service_role;

-- Revoke execute from public
REVOKE EXECUTE ON FUNCTION public.standardize_name() FROM public;

-- Recreate all triggers
CREATE TRIGGER standardize_network_name
    BEFORE INSERT OR UPDATE ON network_list
    FOR EACH ROW
    EXECUTE FUNCTION public.standardize_name();

CREATE TRIGGER standardize_studio_name
    BEFORE INSERT OR UPDATE ON studio_list
    FOR EACH ROW
    EXECUTE FUNCTION public.standardize_name();

CREATE TRIGGER standardize_genre_name
    BEFORE INSERT OR UPDATE ON genre_list
    FOR EACH ROW
    EXECUTE FUNCTION public.standardize_name();

CREATE TRIGGER standardize_status_name
    BEFORE INSERT OR UPDATE ON status_types
    FOR EACH ROW
    EXECUTE FUNCTION public.standardize_name();

CREATE TRIGGER standardize_order_type_name
    BEFORE INSERT OR UPDATE ON order_types
    FOR EACH ROW
    EXECUTE FUNCTION public.standardize_name();

CREATE TRIGGER standardize_source_type_name
    BEFORE INSERT OR UPDATE ON source_types
    FOR EACH ROW
    EXECUTE FUNCTION public.standardize_name();

-- Fix 5: audit.log_changes
-- Drop all triggers that use this function
DROP TRIGGER IF EXISTS shows_audit ON shows;
DROP TRIGGER IF EXISTS show_team_audit ON show_team;

-- Drop the function
DROP FUNCTION IF EXISTS audit.log_changes() CASCADE;

-- Create function with explicit search path
CREATE OR REPLACE FUNCTION audit.log_changes()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = audit, public
AS $$
BEGIN
    INSERT INTO logs (
        table_name,
        operation,
        old_data,
        new_data,
        changed_by
    )
    VALUES (
        TG_TABLE_NAME,
        TG_OP,
        CASE WHEN TG_OP = 'DELETE' THEN row_to_json(old)::jsonb ELSE null END,
        CASE WHEN TG_OP in ('INSERT','UPDATE') THEN row_to_json(new)::jsonb ELSE null END,
        coalesce(auth.email(), current_user)  -- Use Supabase auth email if available
    );
    RETURN null;
END;
$$;

-- Grant execute permission to authenticated users
GRANT EXECUTE ON FUNCTION audit.log_changes() TO authenticated;
GRANT EXECUTE ON FUNCTION audit.log_changes() TO service_role;

-- Revoke execute from public
REVOKE EXECUTE ON FUNCTION audit.log_changes() FROM public;

-- Recreate all triggers
CREATE TRIGGER shows_audit
    AFTER INSERT OR UPDATE OR DELETE ON shows
    FOR EACH ROW
    EXECUTE FUNCTION audit.log_changes();

CREATE TRIGGER show_team_audit
    AFTER INSERT OR UPDATE OR DELETE ON show_team
    FOR EACH ROW
    EXECUTE FUNCTION audit.log_changes();
