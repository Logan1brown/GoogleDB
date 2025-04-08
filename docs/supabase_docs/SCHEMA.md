# Database Schema Documentation

## Field Naming Standards

### General Rules
- Use lowercase with underscores (snake_case)
- Be consistent with column names across tables
- Use clear, descriptive names
- Standardize common fields:
  - `id`: Primary key
  - `title`: Show name (standardized from Google Sheets columns):
    - 'shows' sheet: 'shows' column -> 'title'
    - 'show_team' sheet: 'show_name' column -> 'title'
    - 'TMDB_success_metrics': 'Title' column -> 'title'
  - `search_title`: Generated lowercase version of title
  - `name`: Display name for support tables
  - `search_name`: Generated lowercase version of name
  - `created_at`: Creation timestamp
  - `updated_at`: Last update timestamp
  - `active`: Boolean for soft deletes

### Foreign Keys
- Format: `[table_name]_id`
- Examples:
  - `network_id`
  - `studio_id`
  - `show_id`

### TMDB Fields
- Prefix with `tmdb_`
- Examples:
  - `tmdb_id`
  - `tmdb_popularity`
  - `tmdb_vote_average`

## Table Structure

### Support Tables

#### Networks
```sql
- id: BIGSERIAL PRIMARY KEY
- name: TEXT NOT NULL UNIQUE
- search_name: TEXT GENERATED
- type: TEXT
- category: TEXT
- parent_company: TEXT
- parent_division: TEXT
- business_tags: TEXT[]
- aliases: TEXT[]
- active: BOOLEAN
- timestamps
```

#### Studios
```sql
- id: BIGSERIAL PRIMARY KEY
- name: TEXT NOT NULL UNIQUE
- search_name: TEXT GENERATED
- type: TEXT
- category: TEXT
- parent_company: TEXT
- parent_division: TEXT
- business_tags: TEXT[]
- aliases: TEXT[]
- active: BOOLEAN
- timestamps
```

#### Genres
```sql
- id: BIGSERIAL PRIMARY KEY
- name: TEXT NOT NULL UNIQUE
- search_name: TEXT GENERATED
- type: TEXT
- category: TEXT
- parent_company: TEXT
- parent_division: TEXT
- aliases: TEXT[]
- active: BOOLEAN
- timestamps
```

#### Subgenres
```sql
- id: BIGSERIAL PRIMARY KEY
- name: TEXT NOT NULL UNIQUE
- search_name: TEXT GENERATED
- category: TEXT
- aliases: TEXT[]
- active: BOOLEAN
- timestamps
```

### Main Tables

#### Shows
```sql
- id: BIGSERIAL PRIMARY KEY
- title: TEXT NOT NULL UNIQUE  -- Standardized from different source columns:
  - shows sheet: 'shows' column
  - show_team sheet: 'show_name' column
  - TMDB_success_metrics: 'Title' column
- search_title: TEXT GENERATED  -- For case-insensitive search
- description: TEXT
- status_id: BIGINT REFERENCES status_types(id)
- network_id: BIGINT REFERENCES networks(id)
- studio_id: BIGINT REFERENCES studios(id)  -- Primary studio
- genre_id: BIGINT REFERENCES genres(id)  -- Primary genre
- subgenres: BIGINT[]  -- Additional genres
- source_type_id: BIGINT REFERENCES source_types(id)
- order_type_id: BIGINT REFERENCES order_types(id)
- date: DATE  -- Original date from source
- episode_count: INTEGER  -- Number of episodes
- tmdb_id: INTEGER UNIQUE  -- For external reference
- active: BOOLEAN NOT NULL DEFAULT true
- created_at: TIMESTAMPTZ NOT NULL DEFAULT NOW()
- updated_at: TIMESTAMPTZ NOT NULL DEFAULT NOW()
```

Indexes:
- `title`: Exact matches
- `search_title`: Case-insensitive search
- `network_id`, `studio_id`, `genre_id`, `status_id`: Foreign key lookups
- `subgenres`: GIN index for array operations
- `tmdb_id`: External reference lookups

#### Team Members (show_team)
```sql
- id: BIGSERIAL PRIMARY KEY
- title: TEXT REFERENCES shows(title)  -- Standardized show title
- name: TEXT NOT NULL  -- Name as credited, not normalized
- search_name: TEXT GENERATED  -- For case-insensitive search
- role_type_id: BIGINT REFERENCES role_types(id)  -- Normalized role from role_types
- team_order: INTEGER  -- For display priority
- notes: TEXT  -- Additional information
- active: BOOLEAN NOT NULL DEFAULT true
- created_at: TIMESTAMPTZ NOT NULL DEFAULT NOW()
- updated_at: TIMESTAMPTZ NOT NULL DEFAULT NOW()
```

Notes:
- Show titles reference the standardized `shows.title` column
- Names are kept as-is from source data (not normalized)
- Roles are normalized through role_types table
- Each person can have multiple roles on a show
- Unique constraint on (title, name, role_type_id)

## Relationships

### One-to-Many
- Network -> Shows
- Studio -> Shows
- Show -> Team Members
- Genre -> Shows (primary genre)

### Many-to-Many
- Shows -> Subgenres (through subgenre_ids array)

## Indexes

### Shows Table
- title (search)
- network_id (filters)
- studio_id (filters)
- genre_id (filters)
- status_id (filters)
- tmdb_id (unique lookups)
- subgenre_ids (GIN index for array operations)

### Team Members Table
- show_id (joins)
- role_type_id (filters)

## Materialized Views

### show_details
Denormalized view combining show information with related entities:
- Basic show information
- Network and studio details
- Primary and secondary genres
- Status and order types

### team_member_counts
Aggregated view of team members per show:
- Show identification
- Role category counts
- Total member counts
