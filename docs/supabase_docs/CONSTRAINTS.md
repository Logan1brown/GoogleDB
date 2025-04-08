# Database Constraints and Indexes

## Foreign Key Constraints

### shows table
- `network_id` → `networks.id` (broadcast/streaming network)
- `studio_id` → `studios.id` (primary production studio)
- `genre_id` → `genres.id` (primary genre)
- `subgenres` → `genres.id` (array of additional genres)
- `status_id` → `status_types.id` (development status)
- `order_type_id` → `order_types.id` (pilot, series, etc)
- `source_type_id` → `source_types.id` (original, adaptation, etc)

### show_team table
- `show_id` → `shows.id` (foreign key reference)
- `role_type_id` → `role_types.id` (normalized role reference)

## Required Fields (NOT NULL)

### shows table
- `title` (standardized from source columns, preserve formatting)
- `search_title` (generated column: lowercase title)
- `active` (soft delete flag)
- `created_at` (creation timestamp)
- `updated_at` (last modified timestamp)

### show_team table
- `show_id` (reference to shows)
- `name` (credited name, preserve formatting)
- `search_name` (generated column: lowercase name)
- `role_type_id` (normalized role reference)

### support tables
- `name` (unique, preserve exact formatting)
- `search_name` (generated column: lowercase name)
- `id` (auto-generated)

## Unique Constraints

### shows table
- `title` (case-sensitive, preserve formatting)
- `search_title` (unique in lowercase form)
- `tmdb_id` (unique external reference)

### show_team table
- `(show_id, name, role_type_id)` (person can have multiple roles on a show)

## Implementation Notes

### Generated Columns
```sql
-- Automatic normalization on insert/update
search_title text GENERATED ALWAYS AS (LOWER(title)) STORED,
search_name text GENERATED ALWAYS AS (LOWER(member_name)) STORED
```

Benefits:
- Automatic updates when source column changes
- Zero maintenance, no triggers needed
- Guaranteed consistency with source
- Fast searches with materialized values
- Clean separation of display vs search data

### Materialized Views

#### show_details
- Combines show info with support table data
- Includes both display and search fields
- Updates via refresh trigger

#### show_team_stats
- Groups team members by show and role
- Maintains display order via team_order
- Includes search fields for filtering

### Indexes

#### Support Tables
```sql
-- Networks
CREATE INDEX idx_networks_name ON networks(name);
CREATE INDEX idx_networks_search_name ON networks(search_name);
CREATE INDEX idx_networks_type ON networks(type);
CREATE INDEX idx_networks_parent_company ON networks(parent_company);

-- Studios
CREATE INDEX idx_studios_name ON studios(name);
CREATE INDEX idx_studios_search_name ON studios(search_name);
CREATE INDEX idx_studios_parent_company ON studios(parent_company);
CREATE INDEX idx_studios_platform ON studios(platform);

-- Genres
CREATE INDEX idx_genres_name ON genres(name);
CREATE INDEX idx_genres_search_name ON genres(search_name);
CREATE INDEX idx_genres_category ON genres(category);
```

#### shows table
```sql
-- Title lookups
CREATE INDEX idx_shows_title ON shows(title);
CREATE INDEX idx_shows_search_title ON shows(search_title);

-- Foreign key lookups
CREATE INDEX idx_shows_network_id ON shows(network_id);
CREATE INDEX idx_shows_studio_id ON shows(studio_id);
CREATE INDEX idx_shows_genre_id ON shows(genre_id);
CREATE INDEX idx_shows_status_id ON shows(status_id);

-- External IDs
CREATE INDEX idx_shows_tmdb_id ON shows(tmdb_id) WHERE tmdb_id IS NOT NULL;
```

#### show_team table
```sql
-- Show lookups
CREATE INDEX idx_show_team_show_title ON show_team(show_title);
CREATE INDEX idx_show_team_member_name ON show_team(member_name);
CREATE INDEX idx_show_team_search_name ON show_team(search_name);
CREATE INDEX idx_show_team_role_type_id ON show_team(role_type_id);
```

## Data Migration Notes

### Show Titles
- Preserve original formatting, quotes, special characters
- Generate lowercase search version
- Document alternate titles (international, rebranded)

### Member Names
- Store name as credited
- Generate lowercase search version
- Track aliases for cross-referencing
- Handle suffixes (Jr., III, etc.) consistently

### support tables
- `name` in all support tables (case-sensitive unique)

## Indexes

### shows table
```sql
-- Title lookups
CREATE INDEX shows_title_idx ON shows (title);         -- Exact matches
CREATE INDEX shows_search_title_idx ON shows (search_title);  -- Case-insensitive search

-- Foreign key lookups
CREATE INDEX shows_network_id_idx ON shows (network_id);
CREATE INDEX shows_studio_id_idx ON shows (studio_id);
CREATE INDEX shows_genre_id_idx ON shows (genre_id);
CREATE INDEX shows_status_id_idx ON shows (status_id);

-- Array operations
CREATE INDEX shows_subgenres_idx ON shows USING GIN (subgenre_ids);

-- External IDs
CREATE INDEX shows_tmdb_id_idx ON shows (tmdb_id) WHERE tmdb_id IS NOT NULL;
CREATE INDEX shows_tmdb_id_idx ON shows (tmdb_id);
```

### ShowTeam Table
```sql
-- Name search (find person across shows)
CREATE INDEX show_team_person_name_idx ON show_team (person_name);

-- Show lookups
CREATE INDEX show_team_show_title_idx ON show_team (show_title);

-- Role filtering
CREATE INDEX show_team_role_type_idx ON show_team (role_type_id);
```

### Support Tables
```sql
-- Name lookups in all support tables
CREATE INDEX networks_name_idx ON networks (name);
CREATE INDEX studios_name_idx ON studios (name);
CREATE INDEX genres_name_idx ON genres (name);
```

## Soft Deletes
All tables include:
- `active` boolean field (true = active, false = soft deleted)
- `created_at` timestamp
- `updated_at` timestamp

## Validation Rules
1. Names must be non-empty strings
2. Dates must be valid
3. IDs must be positive
4. Arrays (like subgenre_ids) can be empty but not null
5. Boolean fields default to true for active status
