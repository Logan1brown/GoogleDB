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

## Client Configuration

The application uses a centralized Supabase client configuration in `src/config/supabase_client.py`. This ensures:

1. Single source of truth for client initialization
2. Proper separation of concerns:
   - Backend operations use service key (full access)
   - Frontend operations use anon key (limited access)
3. Consistent error handling across the application

### Architecture

1. Data Access Layer:
   - Only `analyze_shows.py` directly interfaces with Supabase
   - Uses service key for full database access
   - Fetches data from secure API views

2. Business Logic Layer:
   - Components like `MarketAnalyzer` get data through `analyze_shows.py`
   - Never directly access Supabase

3. Frontend Layer:
   - Components like `market_snapshot.py` and `market_view.py`
   - Get data through business logic layer
   - Never directly access Supabase

### Local Development

- Uses ports defined in `config.toml`:
  - API: 54321
  - Database: 54322
  - Studio: 54323

### Production

- Uses hosted Supabase instance
- Requires environment variables from Setup section

## Security Notes

- Never commit `.env` files
- Keep service_role key secure - it has admin access!
- Use RLS policies for data access
- Test policies before deployment
- Only use service key in backend operations
- Frontend should always use anon key
