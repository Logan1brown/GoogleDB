-- Migration: Setup Audit System
-- Created: 2025-04-08

-- Rollback
drop trigger if exists shows_audit on shows;
drop function if exists audit.log_changes();
drop table if exists audit.logs;
drop schema if exists audit;

-- Create audit schema and logs table
create schema if not exists audit;

create table if not exists audit.logs (
    id bigserial primary key,
    table_name text not null,
    operation text not null,
    old_data jsonb,
    new_data jsonb,
    changed_by text,
    created_at timestamptz default now()
);

-- Create audit trigger function
create or replace function audit.log_changes()
returns trigger as $$
begin
    insert into audit.logs (
        table_name,
        operation,
        old_data,
        new_data,
        changed_by
    )
    values (
        TG_TABLE_NAME,
        TG_OP,
        case when TG_OP = 'DELETE' then row_to_json(old)::jsonb else null end,
        case when TG_OP in ('INSERT','UPDATE') then row_to_json(new)::jsonb else null end,
        coalesce(auth.email(), current_user)  -- Use Supabase auth email if available
    );
    return null;
end;
$$ language plpgsql security definer;

-- Add trigger to shows table
create trigger shows_audit
after insert or update or delete on shows
for each row execute function audit.log_changes();
