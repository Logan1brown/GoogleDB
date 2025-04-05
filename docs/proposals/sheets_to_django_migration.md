# Sheets to Django Migration Proposal

## Overview
Migrate from Google Sheets to a Django+PostgreSQL stack hosted on Railway.app, while maintaining data integrity and user access.

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
```

## Migration Strategy

### 1. Database Schema
```python
# shows/models.py
class Show(models.Model):
    # Keep original column names for data consistency
    shows = models.CharField(max_length=200)  # Original 'shows' column
    network = models.ForeignKey('Network')
    studio = models.ForeignKey('Studio')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Show'
        verbose_name_plural = 'Shows'
        
class ShowTeam(models.Model):
    # Keep 'show_name' for consistency
    show_name = models.ForeignKey(Show, to_field='shows')  
    role = models.CharField(max_length=100)
    person = models.CharField(max_length=200)
```

### 2. Migration Phases

#### Phase 1: Setup (Week 1)
- [ ] Create Django project
- [ ] Define models preserving original column names
- [ ] Setup Railway.app infrastructure
- [ ] Configure PostgreSQL
- [ ] Setup authentication

#### Phase 2: Data Migration (Week 2)
```python
# management/commands/migrate_sheets.py
class Command(BaseCommand):
    def handle(self, *args, **options):
        # 1. Export sheets to CSV
        shows_df = pd.read_csv('shows.csv')
        team_df = pd.read_csv('show_team.csv')
        
        # 2. Validate data
        validate_column_names(shows_df, ['shows', 'network', 'studio'])
        validate_column_names(team_df, ['show_name', 'role', 'person'])
        
        # 3. Import to Django
        for _, row in shows_df.iterrows():
            Show.objects.create(
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
