# Supabase Project Structure

## Directory Structure
```
supabase/
├── migrations/          # SQL migration files
│   └── 00001_*.sql     # Numbered in order of execution
├── config/             # Configuration files
│   └── SUPABASE_CONFIG_SETUP.md  # Supabase project setup and env vars
└── MIGRATIONS.md      # Migration documentation
```

## Migrations
Migration files are numbered and should be run in order. Each file is idempotent (can be run multiple times safely).

### Current Migrations:
1. `00001_create_support_tables.sql` - Creates networks, studios, genres, and other lookup tables
2. `00002_insert_lookup_data.sql` - Inserts initial data for all lookup tables
3. `00003_create_main_tables.sql` - Creates shows and show_team tables with materialized views
4. `00004_setup_auth_policies.sql` - Sets up authentication and RLS policies
5. `00006_add_tmdb_metrics.sql` - Creates TMDB metrics table for storing show metrics from TMDB

### Running TMDB Metrics Migration

1. First, create the table structure:
```bash
# Run the SQL migration to create the table
PGPASSWORD=QTRlgAeCCO1fEumL psql -h db.hlwnwcxylueaoemdqiwo.supabase.co -U postgres -d postgres -f supabase/migrations/00006_add_tmdb_metrics.sql
```

2. Then run the data migration script to populate the table:
```bash
# Make sure you have the following env vars set in .env:
# - GOOGLE_SHEETS_CREDENTIALS_FILE
# - GOOGLE_SHEETS_SPREADSHEET_ID
# - DATABASE_URL
# - METRICS_SHEET_NAME (optional, defaults to 'TMDB_success_metrics')

# Activate virtual environment and run migration
source venv/bin/activate
source .env
python3 supabase/data_migrations/03_migrate_tmdb_metrics.py
```

### Rollback Process
Each migration includes rollback statements at the top. To rollback:

1. Run migrations in reverse order
2. Each file starts with DROP statements
3. CASCADE option ensures dependent objects are removed
4. Verify after each rollback

### Generated Columns
All tables with display names have corresponding search fields:
- `search_title` for shows
- `search_name` for all other tables

### Materialized Views
- `show_details`: Combines show info with lookups
- `show_team_stats`: Team member stats by show

## Running Migrations

### SQL Migrations
To run a SQL migration file:
```bash
# Ensure environment variables are set
source venv/bin/activate

# Run the migration
SUPABASE_URL="https://hlwnwcxylueaoemdqiwo.supabase.co" \
DATABASE_URL="postgresql://postgres:QTRlgAeCCO1fEumL@db.hlwnwcxylueaoemdqiwo.supabase.co:5432/postgres" \
python3 -c "import psycopg2; conn = psycopg2.connect('$DATABASE_URL'); cursor = conn.cursor(); cursor.execute(open('supabase/migrations/YOUR_MIGRATION.sql', 'r').read()); conn.commit(); conn.close();"
```

### Data Migrations
To run a Python data migration script:
```bash
# Ensure environment variables are set
source venv/bin/activate

# Run the migration
SUPABASE_URL="https://hlwnwcxylueaoemdqiwo.supabase.co" \
DATABASE_URL="postgresql://postgres:QTRlgAeCCO1fEumL@db.hlwnwcxylueaoemdqiwo.supabase.co:5432/postgres" \
python3 supabase/data_migrations/YOUR_SCRIPT.py
```

## Schema Overview
- All tables include `created_at` and `updated_at` timestamps
- Automatic `updated_at` maintenance via triggers
- Proper indexes for performance
- Row Level Security enabled
- ENUMs for validated fields
