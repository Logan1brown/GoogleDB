# Show Entry Form Layout

## Form Organization

The show entry interface is organized into multiple independent forms on a single page, allowing users to:
1. Enter and save data in logical groups
2. Focus on one section at a time
3. Submit each section independently

## Form Sections

### 1. Title Search (Always Visible)
- Search box for existing titles
- Real-time matching suggestions
- Option to proceed with new title if no match

### 2. Show Details Form
- Title (from search or new)
- Network (dropdown)
- Announcement Date
- Genre
- Subgenre
- Source Type
- Order Type
- Episode Count
- Status
- Description

### 3. Studios & Production Companies Form
- Multiselect for existing studios
- Number input to add new studios (0-5)
- Text fields for each new studio name

### 4. Team Members Form
- Multiselect for existing team members
- Number input to add new members (0-5)
- For each new member:
  - Name
  - Role
  - Company

## Layout Features

- All forms visible on one page (no tabs)
- Expandable/collapsible sections using st.expander
- Independent submit buttons for each form
- Real-time validation where applicable
- Clear visual grouping of related fields

## Best Practices

1. **Form Separation**: Each logical group of fields is in its own form to:
   - Allow independent submission
   - Prevent form callback limitations
   - Enable better error handling

2. **Data Flow**:
   - Title search must be completed first
   - Other forms can be filled in any order
   - Each form saves its data independently

3. **Validation**:
   - Client-side validation in each form
   - Server-side validation on submission
   - Clear error messages for invalid inputs

### 3. Additional Information
- TMDB ID

## Notes
- Single unified form (no separate forms)
- Submit button at bottom
- All dropdowns should have clear default "Select..." option
- Custom studio field only shown if "Add New Studio" selected
