# Database Relationships

## Entity Relationship Diagram

```mermaid
erDiagram
    %% One-to-Many Relationships (Foreign Keys)
    network_list ||--o{ shows : "has many"
    genre_list ||--o{ shows : "primary genre"
    status_types ||--o{ shows : "current status"
    order_types ||--o{ shows : "order type"
    source_types ||--o{ shows : "source type"

    %% Array-based Many-to-Many
    shows ||--o{ studios_array : "contains"
    studios_array }o--|| studio_list : "references"
    shows ||--o{ subgenres_array : "contains"
    subgenres_array }o--|| genre_list : "references"

    %% Team and TMDB Relationships
    shows ||--o{ show_team : "has many"
    role_types ||--o{ show_team : "has role"
    shows ||--o| tmdb_success_metrics : "has metrics"

    shows {
        bigint id PK
        text title UK
        text search_title UK "GENERATED"
        text description
        bigint network_id FK
        bigint genre_id FK
        bigint[] subgenres
        bigint[] studios
        bigint status_id FK
        bigint order_type_id FK
        bigint source_type_id FK
        date date
        integer episode_count
        integer tmdb_id UK
        boolean active
        timestamptz created_at
        timestamptz updated_at
    }

    tmdb_success_metrics {
        bigint id PK
        integer tmdb_id FK
        integer seasons
        integer[] episodes_per_season
        integer total_episodes
        float average_episodes
        text status
        date last_air_date
        timestamptz created_at
        timestamptz updated_at
    }

    show_team {
        bigint id PK
        bigint show_id FK
        text name
        bigint role_type_id FK
        boolean active
        timestamptz created_at
        timestamptz updated_at
    }

    network_list {
        bigint id PK
        text network UK
        text search_network UK "GENERATED"
        text type
        text parent_company
        text[] aliases
        boolean active
        timestamptz created_at
        timestamptz updated_at
    }

    studio_list {
        bigint id PK
        text studio UK
        text search_studio UK "GENERATED"
        boolean active
        timestamptz created_at
        timestamptz updated_at
    }

    genre_list {
        bigint id PK
        text genre UK
        text search_genre UK "GENERATED"
        boolean active
        timestamptz created_at
        timestamptz updated_at
    }
    }

    Subgenres {
        bigserial id PK
        text name UK
        text category
        text[] aliases
        boolean active
        timestamp created_at
        timestamp updated_at
    }

    role_types {
        bigint id PK
        text role UK
        boolean active
        timestamptz created_at
        timestamptz updated_at
    }

    source_types {
        bigint id PK
        text type UK
        boolean active
        timestamptz created_at
        timestamptz updated_at
    }

    order_types {
        bigint id PK
        text type UK
        boolean active
        timestamptz created_at
        timestamptz updated_at
    }

    status_types {
        bigint id PK
        text status UK
        boolean active
        timestamptz created_at
        timestamptz updated_at
    }
```

## Key Relationships

### Primary Table Relationships

#### Shows Foreign Keys
- `network_id` → `network_list(id)` (required)
- `genre_id` → `genre_list(id)` (optional)
- `status_id` → `status_types(id)` (optional)
- `order_type_id` → `order_types(id)` (optional)
- `source_type_id` → `source_types(id)` (optional)

#### Shows Array Fields
- `studios`: bigint[] referencing `studio_list(id)`
  - Many-to-many without join table
  - Default: empty array
  - GIN indexed for performance
- `subgenres`: bigint[] referencing `genre_list(id)`
  - Many-to-many without join table
  - GIN indexed for performance

#### Shows Unique Fields
- `title`: text (unique, case-sensitive)
- `search_title`: text (unique, lowercase)
- `tmdb_id`: integer (unique, optional)

### Child Table Relationships

#### Show Team
- Foreign Keys:
  - `show_id` → `shows(id)` (required)
  - `role_type_id` → `role_types(id)` (required)
- Fields:
  - `name`: text (original formatting preserved)
  - Timestamps for creation and updates

#### TMDB Success Metrics
- Foreign Key:
  - `tmdb_id` → `shows(tmdb_id)` (required)
  - Note: Links via `tmdb_id` not `id` to match TMDB API
- Episode Data:
  - `seasons`: integer (total seasons)
  - `episodes_per_season`: integer[] (per-season count)
  - `total_episodes`: integer (total count)
  - `average_episodes`: float (mean per season)
- Status:
  - `status`: text (e.g., 'Ended', 'Running')
  - `last_air_date`: date

### Support Tables

#### Network List
- Primary key: `id`
- Unique network names with generated search version
- Additional metadata:
  - Type (e.g., Broadcast, Streaming)
  - Parent company
  - Aliases array

#### Studio List
- Primary key: `id`
- Unique studio names with generated search version
- Referenced by shows via `studios` array

#### Genre List
- Primary key: `id`
- Unique genre names with generated search version
- Used for both primary genres and subgenres

#### Type Tables
- Role Types: Defines creative team roles
- Source Types: Show source material types
- Order Types: Show order types (Limited, Ongoing, etc.)
- Status Types: Show status values

All support tables include:
- Active status for soft deletes
- Creation and update timestamps
