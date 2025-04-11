# Database Schema Documentation

## Field Naming Standards

### General Rules
- Use lowercase with underscores (snake_case)
- Be consistent with column names across tables
- Use clear, descriptive names
- Standardize common fields:
  - `id`: Primary key (bigint)
  - Primary Name Fields:
    - `title`: For shows table
    - `network`: For network_list
    - `studio`: For studio_list
    - `genre`: For genre_list
  - Search Fields (GENERATED ALWAYS AS STORED):
    - `search_title`: Generated lowercase version of title
    - `search_network`: Generated lowercase version of network
    - `search_studio`: Generated lowercase version of studio
  - Array Fields:
    - `studios`: bigint[] in shows table
    - `subgenres`: bigint[] in shows table
    - `aliases`: text[] in network_list
  - Timestamps:
    - `created_at`: Creation timestamp (with time zone)
    - `updated_at`: Last update timestamp (with time zone)
  - Status:
    - `active`: Boolean for soft deletes (default true)

### Foreign Keys
- Format: `[table_name]_id` (bigint)
- Examples:
  - `network_id`: References network_list(id)
  - `genre_id`: References genre_list(id)
  - `source_type_id`: References source_types(id)
  - `order_type_id`: References order_types(id)
  - `status_id`: References status_types(id)
  - `show_id`: References shows(id)
  - Array References:
    - `studios`: References studio_list(id)[]
    - `subgenres`: References genre_list(id)[]

### TMDB Fields
- In shows table:
  - `tmdb_id`: Integer, unique identifier from TMDB
- In tmdb_success_metrics table:
  - `seasons`: Number of seasons
  - `total_episodes`: Total episode count
  - `status`: Show status from TMDB
  - `last_air_date`: Last aired episode date

## Table Structure

### Primary Tables

#### Shows (shows)
```sql
CREATE TABLE shows (
    id bigint PRIMARY KEY,
    title text NOT NULL,
    search_title text GENERATED ALWAYS AS (lower(title)) STORED,
    description text,
    status_id bigint,
    network_id bigint NOT NULL,
    genre_id bigint,
    subgenres bigint[],
    source_type_id bigint,
    order_type_id bigint,
    date date,
    episode_count integer,
    tmdb_id integer UNIQUE,
    active boolean NOT NULL DEFAULT true,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    studios bigint[] DEFAULT '{}'
);
```

#### Show Team (show_team)
```sql
CREATE TABLE show_team (
    id bigint PRIMARY KEY,
    show_id bigint REFERENCES shows(id),
    name text NOT NULL,
    role_type_id bigint REFERENCES role_types(id),
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);
```

#### TMDB Success Metrics (tmdb_success_metrics)
```sql
CREATE TABLE tmdb_success_metrics (
    id bigint PRIMARY KEY,
    tmdb_id integer REFERENCES shows(tmdb_id),
    seasons integer,
    total_episodes integer,
    status text,
    last_air_date date,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);
```

### Support Tables

#### Network List (network_list)
```sql
CREATE TABLE network_list (
    id bigint PRIMARY KEY,
    network text NOT NULL,
    type text NOT NULL,
    parent_company text,
    aliases text[],
    search_network text GENERATED ALWAYS AS (lower(network)) STORED,
    active boolean NOT NULL DEFAULT true,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);
```

#### Genre List (genre_list)
```sql
CREATE TABLE genre_list (
    id bigint PRIMARY KEY,
    genre text NOT NULL,
    search_genre text GENERATED ALWAYS AS (lower(genre)) STORED,
    active boolean NOT NULL DEFAULT true,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);
```

#### Studio List (studio_list)
```sql
CREATE TABLE studio_list (
    id bigint PRIMARY KEY,
    studio text NOT NULL,
    search_studio text GENERATED ALWAYS AS (lower(studio)) STORED,
    active boolean NOT NULL DEFAULT true,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);
```

#### Role Types (role_types)
```sql
CREATE TABLE role_types (
    id bigint PRIMARY KEY,
    role text NOT NULL,
    active boolean NOT NULL DEFAULT true,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);
```

#### Source Types (source_types)
```sql
CREATE TABLE source_types (
    id bigint PRIMARY KEY,
    type text NOT NULL,
    active boolean NOT NULL DEFAULT true,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);
```

#### Order Types (order_types)
```sql
CREATE TABLE order_types (
    id bigint PRIMARY KEY,
    type text NOT NULL,
    active boolean NOT NULL DEFAULT true,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);
```

#### Status Types (status_types)
```sql
CREATE TABLE status_types (
    id bigint PRIMARY KEY,
    status text NOT NULL,
    active boolean NOT NULL DEFAULT true,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);
```

## Indexes and Constraints

### Primary Tables

#### Shows
- Primary Key: `shows_pkey` on `id`
- Unique Constraints:
  - `shows_title_unique` on `title`
  - `shows_search_title_unique` on `search_title`
  - `shows_tmdb_id_key` on `tmdb_id`
- Foreign Key Indexes:
  - `idx_shows_network_id` on `network_id`
  - `idx_shows_genre_id` on `genre_id`
  - `idx_shows_source_type_id` on `source_type_id`
  - `idx_shows_order_type_id` on `order_type_id`
  - `idx_shows_status_id` on `status_id`
- Array Indexes:
  - `idx_shows_studios` GIN index on `studios`
  - `idx_shows_subgenres` GIN index on `subgenres`
- Search Indexes:
  - `idx_shows_title` on `title`
  - `idx_shows_search_title` on `search_title`
  - `idx_shows_tmdb_id` on `tmdb_id` (partial, WHERE tmdb_id IS NOT NULL)

#### Network List
- Primary Key: `network_list_pkey` on `id`
- Unique Constraints:
  - `network_list_network_unique` on `network`
  - `network_list_search_network_unique` on `search_network`
- Search Indexes:
  - `idx_network_list_network` on `network`
  - `idx_network_list_search_network` on `search_network`
  - `idx_network_list_type` on `type`
  - `idx_network_list_parent_company` on `parent_company`

#### Genre List (genre_list)
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

#### Subgenre List (subgenre_list)
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
- network_id: BIGINT REFERENCES network_list(id)
- studio_id: BIGINT REFERENCES studio_list(id)  -- Primary studio
- genre_id: BIGINT REFERENCES genre_list(id)  -- Primary genre
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

#### TMDB Success Metrics (tmdb_success_metrics)
```sql
- id: BIGSERIAL PRIMARY KEY
- tmdb_id: INTEGER REFERENCES shows(tmdb_id)  -- Link to show
- seasons: INTEGER  -- Number of seasons
- episodes_per_season: INTEGER[]  -- Episodes per season
- total_episodes: INTEGER  -- Total episode count
- average_episodes: FLOAT  -- Average episodes per season
- status: TEXT  -- Raw TMDB status (e.g., 'Returning Series', 'Canceled')
- last_air_date: DATE  -- Last air date

Status Mapping:
- TMDB 'Returning Series' -> status_types 'Active'
- TMDB 'In Production' -> status_types 'Active'
- TMDB 'Ended' -> status_types 'Ended'
- TMDB 'Canceled'/'Cancelled' -> status_types 'Cancelled'
- TMDB 'Planned' -> status_types 'Development'
- created_at: TIMESTAMPTZ NOT NULL DEFAULT NOW()
- updated_at: TIMESTAMPTZ NOT NULL DEFAULT NOW()
```

Notes:
- Links to shows table via tmdb_id
- Stores detailed episode metrics from TMDB
- Status is kept as raw text from TMDB
- Episodes per season stored as array for detailed tracking

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
