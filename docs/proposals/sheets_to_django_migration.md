# Sheets to Django Migration Proposal

## Overview
Migrate from Google Sheets to a Django+PostgreSQL stack hosted on Railway.app, modernizing the data model while maintaining functionality.

## Proposed Stack
```
Frontend:
- Django Admin (data entry/management)
- Streamlit (analytics dashboards)

Backend:
- Django 4.x
- PostgreSQL 14+
- Railway.app hosting

Auth:
- Django Auth (user management)
- Group-based permissions

## 1. Migration Phases

#### Phase 1: Setup (Week 1)
- [ ] Create Django project with modern schema
- [ ] Setup Railway.app infrastructure
- [ ] Configure PostgreSQL with proper indexes
- [ ] Implement Django Admin customizations
- [ ] Setup authentication and permissions

#### Phase 2: Data Migration (Week 2)
- [ ] Export lookup tables from Google Sheets
  - [ ] Export network_list to CSV
  - [ ] Export studio_list to CSV
  - [ ] Export genre and subgenre lists
  - [ ] Export type mappings (source, order, status, role)
- [ ] Migrate lookup tables to Django
  - [ ] Create canonical entries
  - [ ] Create aliases and mappings
  - [ ] Validate lookup table integrity
- [ ] Export main data from Sheets
  - [ ] Export shows data
  - [ ] Export team data
  - [ ] Validate CSV exports
- [ ] Run main data migration
  - [ ] Create networks and studios
  - [ ] Import shows with relationships
  - [ ] Import team members
  - [ ] Verify data consistency


#### Phase 3: Validation & Cleanup (Week 2)
- [ ] Run data validation scripts
  - [ ] Compare record counts
  - [ ] Verify relationships
  - [ ] Check data integrity
- [ ] Setup automated tests
  - [ ] Unit tests for models
  - [ ] Integration tests for data flow
  - [ ] Migration test cases
- [ ] Add database constraints
  - [ ] Foreign key constraints
  - [ ] Unique constraints
  - [ ] Check constraints
- [ ] Create API endpoints
  - [ ] Shows endpoints
  - [ ] Teams endpoints
  - [ ] Analytics endpoints

#### Phase 4: Dashboard Updates (Week 3)
- [ ] Update Streamlit connection
  - [ ] Switch to Django backend
  - [ ] Update data fetching
  - [ ] Test all visualizations
- [ ] Verify dashboard features
  - [ ] Studio view
  - [ ] Network view
  - [ ] Team analysis
- [ ] Performance testing
  - [ ] Load testing
  - [ ] Query optimization
  - [ ] Caching setup
```

## 2. Database Schema
```python
# shows/models.py

class Network(models.Model):
    name = models.CharField(max_length=100, unique=True)
    active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class Studio(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_indie = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name

class Show(models.Model):
    title = models.CharField(max_length=200)
    network = models.ForeignKey(Network, on_delete=models.PROTECT)
    studio = models.ForeignKey(Studio, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Show'
        verbose_name_plural = 'Shows'
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['network', 'studio']),
        ]
    
    def __str__(self):
        return self.title

class ShowTeam(models.Model):
    ROLE_CHOICES = [
        ('creator', 'Creator'),
        ('writer', 'Writer'),
        ('director', 'Director'),
        ('producer', 'Producer'),
    ]
    
    show = models.ForeignKey(Show, on_delete=models.CASCADE, related_name='team_members')
    role = models.CharField(max_length=100, choices=ROLE_CHOICES)
    person = models.CharField(max_length=200)
    
    class Meta:
        indexes = [
            models.Index(fields=['show', 'role']),
        ]
        unique_together = ['show', 'role', 'person']
```

### Lookup Tables and Aliases
To maintain our existing lookup table functionality while adding database integrity:

```python
# lookup/models.py

class NetworkAlias(models.Model):
    network = models.ForeignKey(Network, on_delete=models.CASCADE)
    alias = models.CharField(max_length=100, unique=True)
    
    class Meta:
        db_table = 'network_aliases'

class StudioAlias(models.Model):
    studio = models.ForeignKey(Studio, on_delete=models.CASCADE)
    alias = models.CharField(max_length=100, unique=True)
    
    class Meta:
        db_table = 'studio_aliases'

class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
class GenreAlias(models.Model):
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    alias = models.CharField(max_length=100, unique=True)

class Subgenre(models.Model):
    name = models.CharField(max_length=100, unique=True)
    parent_genres = models.ManyToManyField(Genre)
    
class SubgenreAlias(models.Model):
    subgenre = models.ForeignKey(Subgenre, on_delete=models.CASCADE)
    alias = models.CharField(max_length=100, unique=True)

class SourceType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
class SourceTypeAlias(models.Model):
    source_type = models.ForeignKey(SourceType, on_delete=models.CASCADE)
    alias = models.CharField(max_length=100, unique=True)

class OrderType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
class OrderTypeAlias(models.Model):
    order_type = models.ForeignKey(OrderType, on_delete=models.CASCADE)
    alias = models.CharField(max_length=100, unique=True)

class Status(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
class StatusAlias(models.Model):
    status = models.ForeignKey(Status, on_delete=models.CASCADE)
    alias = models.CharField(max_length=100, unique=True)

class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
class RoleAlias(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    alias = models.CharField(max_length=100, unique=True)
```

This replaces our current lookup tables with proper database models that:
1. Enforce referential integrity through foreign keys
2. Ensure unique aliases
3. Support efficient querying through indexes
4. Can be managed through Django admin
5. Maintain all existing relationships (like parent_genres for subgenres)

## 3. Implementation Details

#### Data Migration Implementation
```python
# management/commands/migrate_sheets.py
from django.core.management.base import BaseCommand
from django.db import transaction
from shows.models import Show, ShowTeam, Network, Studio

class Command(BaseCommand):
    def handle(self, *args, **options):
        with transaction.atomic():
            # 1. Load lookup tables first
            self.migrate_lookup_tables()
            
            # 2. Export main data
            shows_df = pd.read_csv('shows.csv')
            team_df = pd.read_csv('show_team.csv')
            
            # 3. Create networks and studios with their aliases
            networks = self.create_networks(shows_df['network'].unique())
            studios = self.create_studios(shows_df['studio'].unique())
            
            # 4. Create shows with proper relationships
            show_mapping = {}  # Map old show names to new Show objects
            for _, row in shows_df.iterrows():
                show = Show.objects.create(
                    title=row['shows'],  # Map old 'shows' column to new 'title'
                    network=networks[row['network']],
                    studio=studios[row['studio']]
                )
                show_mapping[row['shows']] = show
            
            # 5. Create team members with validated roles
            for _, row in team_df.iterrows():
                ShowTeam.objects.create(
                    show=show_mapping[row['show_name']],
                    role=self._normalize_role(row['role']),
                    person=row['person']
                )
    
    def migrate_lookup_tables(self):
        """Migrate all lookup tables and their aliases"""
        # Load lookup CSVs
        lookups = {
            'network': pd.read_csv('network_list.csv'),
            'studio': pd.read_csv('studio_list.csv'),
            'genre': pd.read_csv('genre_list.csv'),
            'subgenre': pd.read_csv('subgenre_list.csv'),
            'source': pd.read_csv('source_types.csv'),
            'order': pd.read_csv('order_types.csv'),
            'status': pd.read_csv('status_types.csv'),
            'role': pd.read_csv('role_types.csv')
        }
        
        # Create canonical entries and aliases
        for table_name, df in lookups.items():
            model_class = self._get_model_class(table_name)
            alias_class = self._get_alias_class(table_name)
            
            # Create canonical entries
            entries = {}
            for _, row in df.iterrows():
                canonical_name = row['canonical_name']
                entry = model_class.objects.create(name=canonical_name)
                entries[canonical_name] = entry
                
                # Create aliases if present
                if 'aliases' in row and pd.notna(row['aliases']):
                    aliases = [a.strip() for a in row['aliases'].split(',')]
                    for alias in aliases:
                        alias_class.objects.create(
                            parent=entry,
                            alias=alias
                        )
                        
                # Handle special cases
                if table_name == 'subgenre' and 'parent_genres' in row:
                    genres = [g.strip() for g in row['parent_genres'].split(',')]
                    for genre in genres:
                        if genre in entries:
                            entry.parent_genres.add(entries[genre])
    
    def create_networks(self, network_names):
        """Create networks and map aliases to canonical names"""
        networks = {}
        for name in network_names:
            if pd.isna(name):
                continue
            # Try to find canonical network through alias
            alias = NetworkAlias.objects.filter(alias__iexact=name).first()
            if alias:
                networks[name] = alias.network
            else:
                # Create new network if no alias exists
                network = Network.objects.create(name=name)
                NetworkAlias.objects.create(network=network, alias=name)
                networks[name] = network
        return networks
    
    def create_studios(self, studio_names):
        """Create studios and map aliases to canonical names"""
        studios = {}
        for name in studio_names:
            if pd.isna(name):
                continue
            # Try to find canonical studio through alias
            alias = StudioAlias.objects.filter(alias__iexact=name).first()
            if alias:
                studios[name] = alias.studio
            else:
                # Create new studio if no alias exists
                studio = Studio.objects.create(
                    name=name,
                    is_indie=self._is_indie_studio(name)
                )
                StudioAlias.objects.create(studio=studio, alias=name)
                studios[name] = studio
        return studios
    
    def _get_model_class(self, table_name):
        """Get the model class for a lookup table"""
        return {
            'network': Network,
            'studio': Studio,
            'genre': Genre,
            'subgenre': Subgenre,
            'source': SourceType,
            'order': OrderType,
            'status': Status,
            'role': Role
        }[table_name]
    
    def _get_alias_class(self, table_name):
        """Get the alias model class for a lookup table"""
        return {
            'network': NetworkAlias,
            'studio': StudioAlias,
            'genre': GenreAlias,
            'subgenre': SubgenreAlias,
            'source': SourceTypeAlias,
            'order': OrderTypeAlias,
            'status': StatusAlias,
            'role': RoleAlias
        }[table_name]
    
    def _normalize_role(self, role):
        """Get canonical role through alias lookup"""
        if pd.isna(role):
            return None
        alias = RoleAlias.objects.filter(alias__iexact=role.strip()).first()
        return alias.role if alias else None
    
    def _is_indie_studio(self, name):
        """Determine if studio is indie based on lookup table"""
        if pd.isna(name):
            return False
        alias = StudioAlias.objects.filter(alias__iexact=name.strip()).first()
        return alias.studio.is_indie if alias else True  # Default to indie if unknown
```

## 4. Key Improvements
1. **Better Data Model**:
   - Proper foreign key relationships
   - Indexed fields for performance
   - Enum choices for roles
   - Audit fields (created_at, updated_at)

2. **Data Integrity**:
   - Database-level constraints
   - Transaction safety
   - Unique constraints where needed
   - Protected foreign keys

3. **Performance**:
   - Proper indexes
   - Efficient queries
   - Cached relationships

4. **Maintainability**:
   - Clear model structure
   - Type validation
   - Admin customization
   - API endpoints
                shows=row['shows'],  # Keep original column name
                network=row['network'],
                studio=row['studio']
            )
```

#### Phase 3: API Development (Week 3)
```python
# api/views.py
class ShowViewSet(viewsets.ModelViewSet):
    queryset = Show.objects.all()
    serializer_class = ShowSerializer
    
    def get_queryset(self):
        # Maintain existing query patterns
        if 'network' in self.request.query_params:
            return self.queryset.filter(network=self.request.query_params['network'])
        return self.queryset
```

#### Phase 4: Dashboard Migration (Week 4)
```python
# streamlit/app.py
def load_data():
    # Replace sheets client with Django API
    return requests.get('api/shows').json()

def main():
    shows = load_data()
    st.write("Shows Dashboard")
    # Existing Streamlit code remains largely unchanged
```

### 3. Data Synchronization
During migration:
```
Week 1-2: Sheets (Primary) → Django (Secondary)
Week 3: Django (Primary) ← Sheets (Read-only)
Week 4: Django (Primary) only
```

### 4. User Migration
1. Create Django users for each sheets user
2. Set up appropriate permissions groups
3. Train users on Django admin interface
4. Provide login credentials

## Cost Breakdown
```
Free Tier (0-6 months):
$0 - Railway.app free tier
$0 - PostgreSQL
$0 - Django/Streamlit

Growth Tier (6+ months):
$5/mo - Railway starter
$1/mo - S3 storage
$1/mo - Domain (amortized)
Total: ~$7/month
```

## Risks and Mitigations

### 1. Data Integrity
Risk: Column name mismatches during migration
Mitigation: 
- Strict validation in migration scripts
- Extensive testing with sample data

### 2. User Adoption
Risk: Users resistant to new interface
Mitigation:
- Django Admin is spreadsheet-like
- Provide training sessions
- Keep Sheets read-only during transition

### 3. Performance
Risk: Slower than Sheets for some operations
Mitigation:
- Proper database indexing
- API response caching
- Batch operations for bulk updates

## Success Metrics
- [ ] Zero data loss during migration
- [ ] All existing queries work in new system
- [ ] Response time < 500ms for common operations
- [ ] 100% user activation in new system

## Rollback Plan
- Keep Sheets as backup during first month
- Weekly backups of PostgreSQL data
- Ability to restore from any point

## Timeline
- Week 1: Infrastructure setup
- Week 2: Data migration
- Week 3: API development
- Week 4: Dashboard migration
- Week 5: User training
- Week 6: Go-live

## Next Steps
1. Review and approve proposal
2. Set up development environment
3. Create test migration with sample data
4. Schedule user training sessions
5. Set migration date
