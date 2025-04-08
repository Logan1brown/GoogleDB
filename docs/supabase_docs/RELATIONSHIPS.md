# Database Relationships

## Entity Relationship Diagram

```mermaid
erDiagram
    Networks ||--o{ Shows : "has many"
    Studios ||--o{ Shows : "has many"
    Shows }|--|| Genres : "primary genre"
    Shows }|--o{ Subgenres : "secondary genres"
    Shows }|--|| StatusTypes : "current status"
    Shows }|--|| OrderTypes : "order type"
    Shows }|--|| SourceTypes : "source type"

    Shows ||--o{ ShowTeam : "has many"
    ShowTeam }|--|| RoleTypes : "has role"

    Shows {
        bigserial id PK
        text title UK "preserve formatting"
        text search_title UK "GENERATED"
        text description
        bigint network_id FK
        bigint studio_id FK "primary studio"
        bigint genre_id FK "primary genre"
        bigint[] subgenres "additional genres"
        bigint status_id FK
        bigint order_type_id FK
        bigint source_type_id FK
        date date "original date"
        integer episode_count
        integer tmdb_id UK
        boolean active
        timestamptz created_at
        timestamptz updated_at
    }

    ShowTeam {
        bigserial id PK
        bigint show_id FK
        text name "preserve formatting"
        text search_name "GENERATED"
        bigint role_type_id FK
        integer team_order
        text notes
        boolean active
        timestamptz created_at
        timestamptz updated_at
    }

    Networks {
        bigserial id PK
        text name UK
        text search_name "GENERATED"
        text type
        text category
        text parent_company
        text parent_division
        text[] business_tags
        text[] aliases
        boolean active
        timestamptz created_at
        timestamp updated_at
    }

    Studios {
        bigserial id PK
        text name UK
        text type
        text category
        text parent_company
        text parent_division
        text[] business_tags
        text[] aliases
        boolean active
        timestamp created_at
        timestamp updated_at
    }

    Genres {
        bigserial id PK
        text name UK
        text category
        text[] aliases
        boolean active
        timestamp created_at
        timestamp updated_at
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

    show_team {
        bigserial id PK
        text show_title FK "references shows.title"
        text member_name
        text search_name "GENERATED"
        bigint role_type_id FK
        integer team_order
        text notes
        boolean active
        timestamp created_at
        timestamp updated_at
    }

    StatusTypes {
        bigserial id PK
        text name UK
        text category
        boolean active
        timestamp created_at
        timestamp updated_at
    }

    OrderTypes {
        bigserial id PK
        text name UK
        text category
        boolean active
        timestamp created_at
        timestamp updated_at
    }

    SourceTypes {
        bigserial id PK
        text name UK
        text category
        boolean active
        timestamp created_at
        timestamp updated_at
    }

    RoleTypes {
        bigserial id PK
        text name UK
        text category
        boolean active
        timestamp created_at
        timestamp updated_at
    }
```

## Key Relationships

### shows table
- Central entity
- Has many team members (through ShowTeam)
- Belongs to one Network
- Belongs to one Studio
- Has one primary Genre
- Has many secondary Genres (through subgenre_ids array)
- Has one StatusType
- Has one OrderType
- Has one SourceType

### show_team table
Matches current implementation:
- One row per creative per show
- Links to show via show_title field
- Captures:
  - Team member's name
  - Their role on the show
  - Team order (for display priority)
  - Additional notes
- Through name matching across shows, we can find:
  - All shows a person worked on
  - Their role history
  - Network/studio connections

### support tables
All support tables (Networks, Studios, Genres, etc.) follow similar patterns:
- Have unique names
- Include category and type fields where relevant
- Support aliases where needed
- Include active flag for soft deletes
- Track creation and update timestamps
