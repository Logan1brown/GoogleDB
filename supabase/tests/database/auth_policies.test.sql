-- First, enable pgtap extension if not already enabled
CREATE EXTENSION IF NOT EXISTS pgtap;

begin;

-- Plan the tests
select plan(4); -- We'll test 4 key policies

-- Test 1: Check if RLS is enabled on shows table
select has_table_privilege(
    'anon',
    'shows',
    'SELECT'
) as anon_can_read;

-- Test 2: Check public read access policy exists
select has_policy(
    'shows',
    'Allow public read access',
    'Policy should exist on shows table'
);

-- Test 3: Check authenticated insert policy exists
select has_policy(
    'shows',
    'Allow authenticated insert',
    'Insert policy should exist on shows table'
);

-- Test 4: Check service role delete policy exists
select has_policy(
    'shows',
    'Allow service role delete',
    'Delete policy should exist on shows table'
);

-- Finish the tests
select * from finish();
rollback;
