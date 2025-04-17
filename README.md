# TV Series Database & Analysis Project

## Project Overview
This project manages and analyzes straight-to-series television orders to inform content development and sales strategies. The database currently contains approximately 450+ straight-to-series sales orders.

## Table of Contents

1. [Project Architecture](#project-architecture)
   - [Data Model](#data-model)
   - [Implementation](#implementation)

2. [Documentation](#documentation)
   - [Database](#database)
   - [Data Entry](#data-entry)
   - [Development](#development)

3. [Dashboard](#dashboard)
   - [Components](#components)
   - [Features](#features)

4. [Development Guide](#development-guide)
   - [Prerequisites](#prerequisites)
   - [Local Setup](#local-setup)
   - [Development Workflow](#development-workflow)

## Project Architecture

This project is structured as a modern web application with three main components:

### Data Model
A three-layer system that separates:
1. Storage: Supabase PostgreSQL database with:
   - Normalized schema and proper indexing
   - Comprehensive audit logging in `audit.logs`
   - Full change history for all tables
   - Consistent naming convention for ID->name transformations:
     - Base tables use `_id` suffix for foreign keys (e.g., `network_id`)
     - Views use `_name` suffix to signal ID->name conversion (e.g., `network_name`)
2. Services: Python service layer for data access and business logic
3. Presentation: Streamlit dashboard with modern UI components
   - Components use view column names directly (e.g., `network_name`)
   - No additional ID->name transformations needed in frontend

### External Data Sources
1. **TMDB Integration**
   - Show metadata validation and enrichment
   - Success metrics tracking
   - Automated data synchronization

### Implementation
Code organization follows a clean architecture:

1. **Database Layer** (`docs/supabase_docs/`)
   - `SCHEMA.md`: Complete database schema documentation
   - `RELATIONSHIPS.md`: Entity relationships and constraints
   - `FUNCTIONS.md`: Database functions and triggers
   - `CONSTRAINTS.md`: Data integrity rules
   - `AUDIT.md`: Audit logging system and queries

2. **Service Layer** (`src/dashboard/services/`)
   - `show_service.py`: Core show operations
     - Add/Edit/Remove shows
     - Team member management
     - Studio relationships
   - `tmdb_service.py`: TMDB integration
     - Metadata synchronization
     - Success metrics updates

3. **Dashboard** (`src/dashboard/`)
   - `pages/`: Individual dashboard pages
     - `5_data_entry.py`: Show data management
     - Analysis views (in development)
   - `components/`: Reusable UI components
   - `state/`: Application state management

### Key Features

1. **Data Entry System**
   - Modern form interface
   - Real-time validation
   - Multi-select support
   - Fuzzy search

2. **Data Integrity**
   - Normalized database schema
   - Foreign key constraints
   - Soft delete support
   - Proper indexing

3. **User Experience**
   - Clean, consistent UI
   - Clear error messages
   - Efficient workflows
   - Fast performance
   - `components/`: Reusable UI components
   - `templates/`: Plotly layouts and styles
   - `app.py`: Streamlit entry point (minimal bootstrap)

## Database

The application uses Supabase as its database backend with a layered security architecture:

1. **Base Layer**: Materialized views for high-performance data storage
2. **Security Layer**: SECURITY DEFINER functions for controlled access
3. **Access Layer**: API views for safe public access

See [Database Security](./docs/supabase_docs/DATABASE_SECURITY.md) for detailed documentation.

### Key Features
- Materialized views for performance
- Real-time updates via Supabase's real-time features
- Role-based access control
- Secure API views for frontend access

## Data Layer

### Data Sources
1. **Google Sheets**
   - Primary data entry and storage
   - Live validation using data validation rules
   - Lookup tables for genre and team data

2. **TMDB Integration**
   - Show metadata validation
   - Official genre categorization

## Database Documentation

### Core Tables

1. **Shows** (`shows`)
   - Main series information
   - Network and genre relationships
   - Studio and subgenre arrays
   - TMDB integration fields

2. **Show Team** (`show_team`)
   - Team member data
   - Role relationships
   - Soft delete support
   - One row per role

3. **Support Tables**
   - `network_list`: Networks and platforms
   - `studio_list`: Production companies
   - `genre_list`: Genre classifications
   - `role_types`: Team member roles
   - `status_types`: Project statuses
   - `order_types`: Series order types
   - `source_types`: Content sources

### Data Flow

1. **Data Entry System**
   - Modern form interface with tabs
   - Real-time validation
   - Fuzzy search for existing shows
   - Multi-select for studios and roles

2. **TMDB Integration**
   - Success metrics tracking
   - Episode count updates
   - Status synchronization
   - Metadata enrichment

3. **State Management**
   - Normalized form state
   - Operation-specific flows
   - Consistent error handling
   - Clean state transitions

## Development Guide

### Prerequisites

1. **Database**
   - Supabase account and project
   - PostgreSQL knowledge
   - Database credentials

2. **Python Environment**
   - Python 3.8+
   - Poetry for dependency management
   - Development tools (listed in pyproject.toml)

3. **External Services**
   - TMDB API key
   - Supabase credentials

### Local Setup

1. **Clone and Setup Python Environment**
   ```bash
   git clone <repository-url>
   cd GoogleDB
   python3 -m venv venv
   source venv/bin/activate
   pip install -e .
   ```

2. **Install Development Tools** (Optional)
   ```bash
   xcode-select --install  # For better file watching
   pip install watchdog    # For better file watching
   ```

3. **Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

4. **Configure Environment**
   
   Add the following to your `.env` file:
   ```bash
   SUPABASE_URL=your_supabase_url
   SUPABASE_ANON_KEY=your_anon_key        # For frontend access
   SUPABASE_SERVICE_KEY=your_service_key  # For admin operations
   TMDB_API_KEY=your_tmdb_api_key
   ```

   **Security Note**: The anon key is safe to use in frontend code as it can only access secure API views. The service key should NEVER be exposed in frontend code or public repositories.

5. **Run Development Server**
   ```bash
   # Make sure your virtual environment is activated
   source venv/bin/activate

   # Start the Streamlit dashboard
   streamlit run src/dashboard/app.py
   ```
   The dashboard will be available at http://localhost:8501

### Development Workflow

1. **Code Organization**
   - Follow existing patterns
   - Use type hints
   - Document new functions
   - Update tests

2. **Database Changes**
   - Update schema documentation
   - Follow naming conventions
   - Maintain constraints
   - Add proper indexes

3. **Feature Development**
   - Create feature branch
   - Follow clean architecture
   - Write tests
   - Update documentation

4. **Testing**
   - Run unit tests
   - Test form operations
   - Verify error handling
   - Check performance

## Dashboard

### Components

1. **Pages** (`src/dashboard/pages/`)
   - Data Entry (`5_data_entry.py`)
     - Show management interface
     - Team member handling
     - Studio relationships
   - Analysis views (in development)
     - Market Snapshot
     - Studio Performance
     - Content Analysis

2. **Services** (`src/dashboard/services/`)
   - Show management
   - TMDB integration
   - Data validation
   - Error handling
   - Consistent state management
   - Clear error handling
   - Proper validation

3. **Components** (`src/dashboard/components/`)
   - Form fields
   - Search boxes
   - Multi-select inputs
   - Review tabs

### UI/UX Features

1. **Form Organization**
   - Clear operation selection
   - Logical field grouping
   - Progressive disclosure
   - Helpful instructions

2. **Search & Selection**
   - Fuzzy title matching
   - Real-time suggestions
   - Clear result display
   - Easy navigation

3. **Error Handling**
   - Validation feedback
   - Clear error messages
   - State preservation
   - Recovery options

## Development Guide

### Environment Setup

1. **Dependencies**
   ```bash
   # Install Poetry
   curl -sSL https://install.python-poetry.org | python3 -
   
   # Install project dependencies
   poetry install
   ```

2. **Environment Variables**
   ```bash
   # Copy template
   cp .env.example .env
   ```

3. **Configure Environment**
   
   Add the following to your `.env` file:
   ```bash
   SUPABASE_URL=your_supabase_url
   SUPABASE_ANON_KEY=your_anon_key        # For frontend access
   SUPABASE_SERVICE_KEY=your_service_key  # For admin operations
   TMDB_API_KEY=your_tmdb_api_key
   ```

   **Security Note**: The anon key is safe to use in frontend code as it can only access secure API views. The service key should NEVER be exposed in frontend code or public repositories.

4. **Database Setup**
   - Create Supabase project
   - Run schema migrations
   - Configure indexes
   - Set up row level security

### Best Practices

1. **Code Style**
   - Use type hints
   - Write docstrings
   - Follow PEP 8
   - Keep functions focused

2. **Database Access**
   - Use service layer
   - Handle errors gracefully
   - Validate inputs
   - Maintain constraints

3. **Supabase Client Usage**
   ```python
   # Initialize client
   from supabase import create_client
   supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

   # Basic queries
   result = supabase.table('shows').select('*').execute()
   
   # Filtered queries
   result = supabase.table('shows').select('id,title').eq('active', True).execute()
   
   # Join queries
   result = supabase.table('shows')\
       .select('id,title,show_team(name,role_type_id)')\
       .eq('active', True)\
       .execute()
   ```

4. **Audit Log Queries**
   ```python
   # View recent operations
   logs = supabase.table('audit_log')\
       .select('*')\
       .order('created_at', desc=True)\
       .limit(100)\
       .execute()

   # Search by operation type
   logs = supabase.table('audit_log')\
       .select('*')\
       .eq('operation', 'UPDATE')\
       .execute()

   # View changes by user
   logs = supabase.table('audit_log')\
       .select('*')\
       .eq('user_id', user_id)\
       .execute()

   # View show history
   logs = supabase.table('audit_log')\
       .select('*')\
       .eq('table_name', 'shows')\
       .eq('record_id', show_id)\
       .execute()
   ```

5. **State Management**
   - Use ShowFormState
   - Handle transitions
   - Preserve user input
   - Clear error states

### Documentation

1. **Code Documentation**
   - Clear function signatures
   - Detailed docstrings
   - Usage examples
   - Type annotations

2. **Database Documentation**
   - Schema definitions
   - Relationships
   - Constraints
   - Indexes

3. **User Documentation**
   - Operation guides
   - Form instructions
   - Error solutions
   - Best practices

### Page Development

1. **Structure**
   - Streamlit-based interface
   - Component-driven design
   - Clean state management
   - Consistent error handling

2. **Form Components**
   - Multi-step navigation
   - Real-time validation
   - Clear user feedback
   - State preservation

3. **Best Practices**
   - Follow Streamlit patterns
   - Use type hints
   - Document components
   - Handle errors gracefully

### Testing

1. **Unit Tests**
   ```bash
   poetry run pytest tests/
   ```

2. **Integration Tests**
   ```bash
   poetry run pytest tests/integration/
   ```

3. **Manual Testing**
   - Test form operations
   - Verify error handling
   - Check state management
   - Validate constraints

### Common Issues

1. **Setup Issues**
   - Missing credentials
   - Invalid database URL
   - Poetry installation
   - Python version

2. **Runtime Issues**
   - State persistence
   - Form validation
   - Database constraints
   - API rate limits

### Documentation

1. **User Guide**
   - Form operations
   - Data validation
   - Error recovery
   - Best practices

2. **Developer Guide**
   - Architecture overview
   - Component design
   - State management
   - Error handling

3. **Database Guide**
   - Schema design
   - Relationships
   - Constraints
   - Migrations

## Current Status

### Completed Features

1. **Data Entry System**
   - [x] Form interface
   - [x] Validation rules
   - [x] Error handling
   - [x] State management

2. **Database Integration**
   - [x] Supabase setup
   - [x] Schema migration
   - [x] Data migration
   - [x] Soft deletes

### Upcoming Features

1. **Analysis Views**
   - [ ] Market trends
   - [ ] Network analysis
   - [ ] Success metrics
   - [ ] Team insights

2. **UI Enhancements**
   - [ ] Improved search
   - [ ] Batch operations
   - [ ] Export features
   - [ ] Custom filters

See `docs/ROADMAP.md` for detailed plans.

Last updated: March 2024