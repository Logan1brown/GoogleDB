# Data Entry App V3 Implementation

## Current State
1. Fully functional Add/Edit/Remove operations with proper state management
2. Improved search using fuzzy matching and streamlit_searchbox
3. Clean UI with consistent styling and clear operation flows
4. Robust error handling and validation

## Key Features

### State Management
```python
@dataclass
class ShowFormState:
    # Core show data
    title: str
    network_id: Optional[int]
    genre_id: Optional[int]
    subgenres: List[int]  # Multi-select support
    source_type_id: Optional[int]
    order_type_id: Optional[int]
    status_id: Optional[int]
    date: Optional[datetime.date]
    episode_count: Optional[int]
    description: Optional[str]
    
    # Related entities
    studios: List[int]  # Multi-select support
    new_studios: List[str]  # New studio names
    team_members: List[TeamMember]  # Name + roles

@dataclass
class DataEntryState:
    operation: str  # "Add Show", "Edit Show", "Remove Show"
    form_started: bool
    show_form: ShowFormState
    lookups: Dict[str, List[LookupItem]]
```

### Operation Flows

#### Add Show
1. Landing page:
   - Title search to check for duplicates
   - "Add New Show" button if no match
2. Form:
   - Empty fields, all editable
   - Multi-select for subgenres/studios
   - Dynamic team member addition
   - Validation before submission

#### Edit Show
1. Landing page:
   - Search existing shows
   - "Edit Selected" button
2. Form:
   - Pre-populated fields
   - All fields editable
   - Can modify all relationships
   - Validation before saving

#### Remove Show
1. Landing page:
   - Search existing shows
   - "Review Selected" button
2. Form:
   - Pre-populated fields (read-only)
   - Review current data
   - Single "Remove Show" button
   - No validation needed

## Implementation Details

### Soft Delete Support
- `active` boolean field on shows and show_team
- Cascading soft delete for team members
- Preserves data history

### Multi-select Handling
- Subgenres stored as integer array
- Studios stored as integer array
- Team members as separate rows

### Validation Rules
1. Add/Edit operations:
   - Required fields: title, network
   - Valid relationships: genre, status, etc.
   - No duplicate team member roles

2. Remove operation:
   - Only validate show exists
   - Skip other validations

### Error Handling
1. User-facing errors:
   - Clear error messages
   - Form state preserved
   - Validation feedback

2. Database errors:
   - Proper error wrapping
   - Meaningful messages
   - Transaction rollback

### UI Improvements
1. Form organization:
   - Logical field grouping
   - Clear section labels
   - Consistent styling

2. User feedback:
   - Operation status
   - Success messages
   - Error indicators

3. Navigation:
   - Clear operation buttons
   - Easy form reset
   - Review before submit
