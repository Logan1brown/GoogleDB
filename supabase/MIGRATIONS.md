# Database Migration Guide

## Project Structure
```
supabase/
├── migrations/          # SQL and Python migration files
│   ├── 00001_*.sql     # SQL schema migrations
│   └── 00001_*.py      # Python data migrations
├── config/             # Configuration files
└── docs/supabase_docs/SUPABASE_CONFIG_SETUP.md  # Project setup and env vars
└── MIGRATIONS.md       # Migration documentation
```

## Complete Database Rebuild Process

### Prerequisites
1. Environment Setup
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your values:
# - SUPABASE_URL
# - SUPABASE_SERVICE_KEY
# - GOOGLE_SHEETS_CREDENTIALS_FILE
# - GOOGLE_SHEETS_SPREADSHEET_ID
source .env
```

2. Verify Google Sheets Access
```bash
# Test Google Sheets connection
python test_sheets_connection.py
```

### Migration Order
Run migrations in this exact order:

1. Initial Schema Setup
```bash
# Create lookup tables
PGPASSWORD=QTRlgAeCCO1fEumL psql -h aws-0-us-west-1.pooler.supabase.com -U postgres.hlwnwcxylueaoemdqiwo -d postgres -f supabase/migrations/00002_create_lookup_tables.sql

# Create show tables
PGPASSWORD=QTRlgAeCCO1fEumL psql -h aws-0-us-west-1.pooler.supabase.com -U postgres.hlwnwcxylueaoemdqiwo -d postgres -f supabase/migrations/00003_create_show_tables.sql

# Set up audit system
PGPASSWORD=QTRlgAeCCO1fEumL psql -h aws-0-us-west-1.pooler.supabase.com -U postgres.hlwnwcxylueaoemdqiwo -d postgres -f supabase/migrations/00010_setup_audit_system.sql
```

2. Schema Updates
```bash
# Add case-insensitive search triggers
PGPASSWORD=QTRlgAeCCO1fEumL psql -h aws-0-us-west-1.pooler.supabase.com -U postgres.hlwnwcxylueaoemdqiwo -d postgres -f supabase/migrations/00005_add_case_triggers.sql

# Add default studio
PGPASSWORD=QTRlgAeCCO1fEumL psql -h aws-0-us-west-1.pooler.supabase.com -U postgres.hlwnwcxylueaoemdqiwo -d postgres -f supabase/migrations/00005_add_default_studio.sql

# Add unknown role type
PGPASSWORD=QTRlgAeCCO1fEumL psql -h aws-0-us-west-1.pooler.supabase.com -U postgres.hlwnwcxylueaoemdqiwo -d postgres -f supabase/migrations/00005_add_unknown_role.sql

# Convert studios to array
PGPASSWORD=QTRlgAeCCO1fEumL psql -h aws-0-us-west-1.pooler.supabase.com -U postgres.hlwnwcxylueaoemdqiwo -d postgres -f supabase/migrations/00007_convert_studios_to_array.sql
```

3. Data Import
```bash
# Import lookup data (networks, genres, studios, etc)
python supabase/migrations/00004_import_lookup_data.py

# Import shows and team members
python supabase/migrations/00005_import_show_data.py

# Import TMDB metrics
python supabase/migrations/00006_add_tmdb_metrics.sql

# Migrate studio data to array format
python supabase/migrations/00008_migrate_studio_data.py
python supabase/migrations/00010_populate_studios_array.py
```

4. Post-Import Schema Updates
```bash
# Update show constraints
PGPASSWORD=QTRlgAeCCO1fEumL psql -h aws-0-us-west-1.pooler.supabase.com -U postgres.hlwnwcxylueaoemdqiwo -d postgres -f supabase/migrations/00009_update_shows_constraints.sql

# Drop old studio_id column
PGPASSWORD=QTRlgAeCCO1fEumL psql -h aws-0-us-west-1.pooler.supabase.com -U postgres.hlwnwcxylueaoemdqiwo -d postgres -f supabase/migrations/00011_drop_studio_id.sql
```

5. Security Setup
```bash
# Set up auth policies
PGPASSWORD=QTRlgAeCCO1fEumL psql -h aws-0-us-west-1.pooler.supabase.com -U postgres.hlwnwcxylueaoemdqiwo -d postgres -f supabase/migrations/00007_setup_auth_policies.sql

# Fix auth policies
PGPASSWORD=QTRlgAeCCO1fEumL psql -h aws-0-us-west-1.pooler.supabase.com -U postgres.hlwnwcxylueaoemdqiwo -d postgres -f supabase/migrations/00008_fix_auth_policies.sql

# Force RLS
PGPASSWORD=QTRlgAeCCO1fEumL psql -h aws-0-us-west-1.pooler.supabase.com -U postgres.hlwnwcxylueaoemdqiwo -d postgres -f supabase/migrations/00009_force_rls.sql
```

### Verification Steps
After rebuilding:

1. Check Data Integrity
```bash
# Verify show counts match Google Sheets
python scripts/utils/verify_import.py

# Check for orphaned records
python find_missing_shows.py
```

2. Test Auth Policies
```bash
# Run policy tests
./test_policies.sh
```

3. Create Backup
```bash
# Create full database backup
pg_dump -h aws-0-us-west-1.pooler.supabase.com -U postgres.hlwnwcxylueaoemdqiwo -d postgres --clean --if-exists --no-owner --no-privileges --disable-triggers -F c -f backups/backup_$(date +%Y%m%d_%H%M%S).dump

# Create SQL-only backup
pg_dump -h aws-0-us-west-1.pooler.supabase.com -U postgres.hlwnwcxylueaoemdqiwo -d postgres --data-only --column-inserts -f backups/data_backup_$(date +%Y%m%d_%H%M%S).sql
```

### Data Dependencies and Mappings

1. Sheet to Database Mappings
```
Shows Sheet:
- 'shows' column -> shows.title
- 'Network' -> network_list.name
- 'Genre' -> genre_list.name
- 'Subgenre' -> subgenre_list.name
- 'Source Type' -> source_types.name
- 'Order Type' -> order_types.name

Show Team Sheet:
- 'show_name' column -> shows.title
- 'Name' -> show_team.name
- 'Role' -> role_types.name
- 'Company' -> studio_list.name

TMDB Metrics Sheet:
- 'Title' column -> shows.title
- 'TMDB ID' -> shows.tmdb_id
- 'Rating' -> tmdb_success_metrics.rating
- 'Vote Count' -> tmdb_success_metrics.vote_count
```

2. Import Order Dependencies
```
Lookup Tables (First):
1. network_list
2. genre_list
3. subgenre_list
4. source_types
5. order_types
6. status_types
7. role_types
8. studio_list

Core Tables (After Lookups):
1. shows (requires network_list, genre_list)
2. show_team (requires shows, role_types, studio_list)
3. tmdb_success_metrics (requires shows)
```

### Troubleshooting

1. Column Name Issues
- Shows sheet: 'shows' column -> shows.title
- Show_team sheet: 'show_name' column -> shows.title
- TMDB_success_metrics: 'Title' column -> shows.title
- All column mappings are case-sensitive

2. Common Problems
- Foreign key violations: Run migrations in correct order (see Dependencies above)
- Duplicate records: Use ON CONFLICT DO NOTHING
- Missing data: Check Google Sheets connection
- Auth errors: Verify RLS policies
- Title mismatches: Check for leading/trailing spaces and case sensitivity

3. Rollback Process
Each migration has rollback statements. To rollback:
1. Run migrations in reverse order
2. Use DROP statements with CASCADE
3. Verify after each rollback

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
