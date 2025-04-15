# Show Entry Form Layout

## Form Organization

The data entry interface supports three main operations:
1. Add Show - Create a new show with all details
2. Edit Show - Modify an existing show's details
3. Remove Show - Mark a show as inactive

## Form Sections

### 1. Operation Selection (Landing Page)
- Three operation buttons: Add Show, Edit Show, Remove Show
- Title search box for Edit/Remove operations
- Real-time fuzzy search with suggestions

### 2. Show Details Form
- Title (editable for new shows)
- Network (dropdown)
- Announcement Date (datepicker)
- Genre (dropdown)
- Subgenres (multi-select)
- Source Type (dropdown)
- Order Type (dropdown)
- Episode Count (number input)
- Status (dropdown)
- Description (text area)

### 3. Studios Section
- Multi-select for existing studios
- "Add New Studio" button
- Text input for new studio names
- Review tab showing selected studios

### 4. Team Members Section
- Name input with suggestions
- Multi-select for roles
- "Add Member" button
- Review tab showing team members with roles

## Form State Management

### ShowFormState
- Tracks all form data
- Handles multi-select for subgenres
- Manages lists of studios and team members
- Preserves state between form sections

### Operation-specific Behavior

#### Add Show
- All fields empty and editable
- Validates show details before saving
- Allows adding new studios and team members

#### Edit Show
- Fields populated with existing data
- All fields editable
- Can add/remove studios and team members
- Validates changes before saving

#### Remove Show
- Fields populated but read-only
- Single "Remove Show" button
- No validation required
- Marks show and related entries as inactive

## Best Practices

1. **Data Validation**:
   - Client-side validation for add/edit operations
   - Skip validation for remove operation
   - Clear error messages for invalid inputs

2. **State Updates**:
   - Use get_data_entry_state/update_data_entry_state
   - Maintain consistent state across operations
   - Handle form resets properly

3. **Error Handling**:
   - Graceful error recovery
   - User-friendly error messages
   - Maintain form state on error

4. **UI/UX**:
   - Consistent button styling
   - Clear operation labels
   - Helpful tooltips and instructions
   - Review tabs for complex data
