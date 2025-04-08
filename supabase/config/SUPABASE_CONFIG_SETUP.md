# Supabase Configuration

## Setup

1. Create a new project in Supabase
2. Copy the root `.env.example` to `.env`
3. Find the 'TARGET: Supabase Setup' section
4. Fill in:
   - SUPABASE_URL
   - SUPABASE_ANON_KEY
   - SUPABASE_SERVICE_KEY
   - DATABASE_URL

## Where to Find Values

1. Go to Supabase Dashboard
2. Select your project
3. Go to Project Settings > API
4. Copy the values:
   - Project URL → SUPABASE_URL
   - anon/public key → SUPABASE_ANON_KEY
   - service_role key → SUPABASE_SERVICE_KEY
5. Go to Database > Connection Pooling
6. Copy the connection string → DATABASE_URL

## Security Notes

- Never commit `.env` files
- Keep service_role key secure - it has admin access!
- Use RLS policies for data access
- Test policies before deployment
